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
from whisper_notes.pipeline import (
    process_batch,
    show_preview,
    transcribe_raw_only,
)

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
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("processed"),
        help="Directory for generated notes and the index (default: processed). "
        "The input tree is never modified.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: '{input_path}' does not exist.")
        sys.exit(1)

    output_dir = args.output_dir
    # Mirror the input layout under output_dir; a single file maps to the root.
    input_root = input_path if input_path.is_dir() else input_path.parent

    config_path = Path("config.json")
    config = load_config(config_path)

    # Skip the output dir so a run pointed at a parent won't re-ingest its notes.
    collected = collect_files(input_path, skip_dir_names={output_dir.name})
    if not collected.supported and not collected.unsupported:
        print("No files found.")
        sys.exit(1)

    # Filter already-processed unless --force
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
        # Raw-only mode: transcribe into the mirrored output dir (never the source).
        written = transcribe_raw_only(
            files=audio_only,
            input_root=input_root,
            output_dir=output_dir,
            whisper_model=args.model,
        )
        print(f"\nDone. {len(written)} file(s) transcribed (raw only).")
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
        input_root=input_root,
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
