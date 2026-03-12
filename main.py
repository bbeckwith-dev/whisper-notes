"""
whisper-notes: Transcribe audio files to markdown using OpenAI Whisper.

Usage:
    uv run main.py recording.m4a
    uv run main.py recording.m4a --model medium
    uv run main.py recordings/  # transcribe a whole folder
"""

import argparse
import sys
from pathlib import Path

import whisper

AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".mov", ".m4v"}


def transcribe(audio_path: Path, model_name: str) -> str:
    """Load the Whisper model and transcribe a single audio file."""
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {audio_path.name}")
    result = model.transcribe(str(audio_path))
    return result["text"].strip()


def write_markdown(audio_path: Path, text: str) -> Path:
    """Write transcription text to a .md file next to the audio file."""
    md_path = audio_path.with_suffix(".md")
    md_path.write_text(f"# {audio_path.stem}\n\n{text}\n", encoding="utf-8")
    return md_path


def collect_audio_files(input_path: Path) -> list[Path]:
    """Return a list of audio files from a file or directory path."""
    if input_path.is_file():
        if input_path.suffix.lower() not in AUDIO_EXTENSIONS:
            print(f"Error: '{input_path}' is not a supported audio file.")
            print(f"Supported formats: {', '.join(sorted(AUDIO_EXTENSIONS))}")
            sys.exit(1)
        return [input_path]

    if input_path.is_dir():
        files = [
            f for f in input_path.iterdir()
            if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
        ]
        if not files:
            print(f"No audio files found in '{input_path}'.")
            sys.exit(1)
        return sorted(files)

    print(f"Error: '{input_path}' does not exist.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files to markdown using Whisper."
    )
    parser.add_argument(
        "input",
        help="Path to an audio file or a folder of audio files.",
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size. Larger = more accurate but slower. (default: base)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    audio_files = collect_audio_files(input_path)

    for audio_file in audio_files:
        text = transcribe(audio_file, args.model)
        md_path = write_markdown(audio_file, text)
        print(f"Saved: {md_path}\n")

    print(f"Done. {len(audio_files)} file(s) transcribed.")


if __name__ == "__main__":
    main()
