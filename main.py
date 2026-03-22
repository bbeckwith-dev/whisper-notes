# main.py
"""
whisper-notes: Transcribe audio and text files to structured markdown
using OpenAI Whisper and Claude.

Usage:
    uv run main.py recording.m4a
    uv run main.py recordings/                   # process a whole folder
    uv run main.py recording.m4a --no-format     # skip Claude, raw only
    uv run main.py recordings/ --force            # reprocess all files
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from whisper_notes.collect import collect_files
from whisper_notes.config import load_config
from whisper_notes.format import CLAUDE_MODELS
from whisper_notes.index import (
    IndexEntry,
    UnprocessedEntry,
    load_existing_entries,
    load_processed_sources,
    write_index,
)
from whisper_notes.pipeline import process_batch, show_preview

load_dotenv()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe audio and text files to structured markdown."
    )
    parser.add_argument(
        "input",
        help="Path to a file or folder to process.",
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: small)",
    )
    parser.add_argument(
        "--claude-model",
        default="sonnet",
        choices=list(CLAUDE_MODELS.keys()),
        help="Claude model for formatting (default: sonnet)",
    )
    parser.add_argument(
        "--no-format",
        action="store_true",
        help="Skip Claude formatting (raw transcription only, audio files only)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocess files even if already in processed/",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: '{input_path}' does not exist.")
        sys.exit(1)

    config_path = Path("config.json")
    config = load_config(config_path)

    collected = collect_files(input_path)
    if not collected.supported and not collected.unsupported:
        print("No files found.")
        sys.exit(1)

    # Filter already-processed unless --force
    output_dir = Path("processed")
    to_process = collected.supported
    skip_count = 0

    if not args.force:
        already = load_processed_sources(output_dir)
        filtered = []
        for entry in collected.supported:
            if str(entry.path) in already:
                skip_count += 1
            else:
                filtered.append(entry)
        to_process = filtered

    if not to_process:
        print("All files already processed. Use --force to reprocess.")
        sys.exit(0)

    # --no-format: only process audio files, skip Claude
    if args.no_format:
        audio_only = [f for f in to_process if f.medium == "audio"]
        if not audio_only:
            print("--no-format only works with audio files.")
            sys.exit(1)
        # Raw-only mode: transcribe and write next to source (v1 behavior)
        import whisper as whisper_lib
        print(f"Loading Whisper model '{args.model}'...")
        model = whisper_lib.load_model(args.model)
        for entry in audio_only:
            print(f"Transcribing: {entry.path.name}")
            result = model.transcribe(str(entry.path), fp16=False)
            raw = result["text"].strip()
            md_path = entry.path.with_suffix(".md")
            md_path.write_text(
                f"# {entry.path.stem}\n\n{raw}\n", encoding="utf-8"
            )
            print(f"Saved: {md_path}")
        print(f"\nDone. {len(audio_only)} file(s) transcribed (raw only).")
        sys.exit(0)

    # Preview and confirm
    show_preview(to_process, skip_count=skip_count)
    confirm = input("Proceed? [Y/n] ").strip().lower()
    if confirm and confirm != "y":
        print("Cancelled.")
        sys.exit(0)

    claude_model_id = CLAUDE_MODELS[args.claude_model]

    results = process_batch(
        files=to_process,
        config=config,
        output_dir=output_dir,
        whisper_model=args.model,
        claude_model_id=claude_model_id,
        config_path=config_path,
    )

    # Build and write index (merge with existing entries)
    existing_entries = load_existing_entries(output_dir)
    new_entries = [
        IndexEntry(
            file=r.processed_path.name,
            title=r.title,
            date=r.date,
            medium=r.medium,
            vault=r.vault,
            source=r.source,
        )
        for r in results
    ]
    # Merge: keep existing entries whose source wasn't reprocessed
    reprocessed_sources = {r.source for r in results}
    merged = [e for e in existing_entries if e.source not in reprocessed_sources]
    merged.extend(new_entries)

    unprocessed_entries = [
        UnprocessedEntry(file=e.path.name, reason=e.reason)
        for e in collected.unsupported
    ]
    write_index(merged, unprocessed_entries, output_dir)

    print(f"\nDone. {len(results)} file(s) processed.")


if __name__ == "__main__":
    main()
