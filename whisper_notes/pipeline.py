from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from whisper_notes.collect import FileEntry, resolve_date
from whisper_notes.config import add_vault, save_config
from whisper_notes.format import (
    build_prompt,
    compose_output,
    format_with_claude,
    parse_response,
)
from whisper_notes.output import write_archival, write_processed
from whisper_notes.readers import read_document


@dataclass
class ProcessResult:
    processed_path: Path
    title: str
    vault: str
    source: str
    date: str
    medium: str


def transcribe(audio_path: Path, model) -> str:
    """Transcribe audio using a preloaded Whisper model."""
    print(f"Transcribing: {audio_path.name}")
    result = model.transcribe(str(audio_path), fp16=False)
    return result["text"].strip()


def process_file(
    entry: FileEntry,
    config: dict,
    output_dir: Path,
    whisper_model: str,
    claude_model_id: str,
    config_path: Path | None = None,
    _whisper_model=None,
) -> ProcessResult:
    """Process a single file through the full pipeline."""
    date = resolve_date(entry.path)
    processed = datetime.now().isoformat(timespec="seconds")

    # Get raw text
    if entry.medium == "audio":
        raw_text = transcribe(entry.path, _whisper_model)
    else:
        raw_text = read_document(entry.path)

    # Format with Claude
    prompt = build_prompt(date, processed, entry.medium, config["vaults"])
    response = format_with_claude(raw_text, prompt, claude_model_id)
    parsed = parse_response(response)

    # Handle new vault suggestion
    if parsed.vault not in config["vaults"]:
        confirm = input(
            f"\nClaude suggested new vault '{parsed.vault}'. Add it? [Y/n] "
        )
        if confirm.strip().lower() in ("", "y"):
            add_vault(config, parsed.vault)
            if config_path:
                save_config(config, config_path)

    # Compose output (audio includes raw transcription, documents don't)
    include_raw = raw_text if entry.medium == "audio" else None
    content = compose_output(parsed, raw_text=include_raw)

    # Write to processed/
    processed_path = write_processed(parsed.title, content, output_dir)
    print(f"Saved: {processed_path}")

    # Archival copy (audio only — documents left untouched)
    if entry.medium == "audio":
        write_archival(entry.path, parsed.title, content)

    return ProcessResult(
        processed_path=processed_path,
        title=parsed.title,
        vault=parsed.vault,
        source=str(entry.path),
        date=parsed.date,
        medium=parsed.medium,
    )


def process_batch(
    files: list[FileEntry],
    config: dict,
    output_dir: Path,
    whisper_model: str,
    claude_model_id: str,
    config_path: Path | None = None,
) -> list[ProcessResult]:
    """Process a batch of files. Loads Whisper model once for all audio."""
    _whisper_model = None
    if any(f.medium == "audio" for f in files):
        import whisper

        print(f"Loading Whisper model '{whisper_model}'...")
        _whisper_model = whisper.load_model(whisper_model)

    results = []
    for entry in files:
        result = process_file(
            entry=entry,
            config=config,
            output_dir=output_dir,
            whisper_model=whisper_model,
            claude_model_id=claude_model_id,
            config_path=config_path,
            _whisper_model=_whisper_model,
        )
        results.append(result)
    return results


def show_preview(files: list[FileEntry], skip_count: int = 0) -> None:
    """Print a preview summary of files to process."""
    audio_count = sum(1 for f in files if f.medium == "audio")
    doc_count = sum(1 for f in files if f.medium == "document")

    print(f"\nFiles to process: {len(files)}")
    if audio_count:
        print(f"  Audio: {audio_count}")
    if doc_count:
        print(f"  Documents: {doc_count}")
    if skip_count:
        print(f"  Skipped (already processed): {skip_count}")
    print(f"  Estimated API calls: {len(files)} (Claude)")
    if audio_count:
        print(f"  Whisper transcriptions: {audio_count}")
    print()
