"""
whisper-notes: Transcribe audio files to markdown using OpenAI Whisper,
then reformat with Claude for clean, structured output.

Usage:
    uv run main.py recording.m4a
    uv run main.py recording.m4a --model large
    uv run main.py recording.m4a --no-format     # skip Claude, raw only
    uv run main.py recordings/                   # transcribe a whole folder
"""

import argparse
import os
import sys
from pathlib import Path

import anthropic
import whisper
from dotenv import load_dotenv

load_dotenv()

AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".mov", ".m4v"}

FORMAT_PROMPT = """\
You are a transcription editor. I will give you a raw voice transcription from a \
speech-to-text tool. Your job is to reformat it into clean, well-structured markdown.

Guidelines:
- Add appropriate headings (##, ###) to organize topics
- Use bullet points or numbered lists where they improve clarity
- Use **bold** for key terms and *italic* for emphasis where it fits naturally
- Remove filler words (um, uh, like, you know) and false starts
- Fix run-on sentences and awkward phrasing
- DO NOT add any information that was not in the original
- DO NOT change the meaning or omit any ideas

Return only the formatted markdown. No preamble, no explanation.\
"""


def transcribe(audio_path: Path, model_name: str) -> str:
    """Load the Whisper model and transcribe a single audio file."""
    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {audio_path.name}")
    result = model.transcribe(str(audio_path), fp16=False)
    return result["text"].strip()


CLAUDE_MODELS = {
    "opus":   "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5",
}


def format_with_claude(raw_text: str, claude_model: str) -> str:
    """Send the raw transcription to Claude and return formatted markdown."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "Error: ANTHROPIC_API_KEY is not set.\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your key from https://console.anthropic.com\n"
            "  3. Or run with --no-format to skip Claude."
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    model_id = CLAUDE_MODELS[claude_model]
    print(f"Formatting with Claude {claude_model.capitalize()} ({model_id})...")

    formatted_chunks = []
    with client.messages.stream(
        model=model_id,
        max_tokens=4096,
        system=FORMAT_PROMPT,
        messages=[{"role": "user", "content": raw_text}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            formatted_chunks.append(text)

    print("\n")  # newline after streamed output
    return "".join(formatted_chunks).strip()


def write_markdown(audio_path: Path, formatted: str, raw: str, skip_format: bool) -> Path:
    """Write the final .md file next to the audio file."""
    md_path = audio_path.with_suffix(".md")

    if skip_format:
        content = f"# {audio_path.stem}\n\n{raw}\n"
    else:
        content = (
            f"{formatted}\n\n"
            f"---\n\n"
            f"## Raw Transcription\n\n"
            f"{raw}\n"
        )

    md_path.write_text(content, encoding="utf-8")
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
        description="Transcribe audio files to markdown using Whisper + Claude."
    )
    parser.add_argument(
        "input",
        help="Path to an audio file or a folder of audio files.",
    )
    parser.add_argument(
        "--model",
        default="small",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size. Larger = more accurate but slower. (default: small)",
    )
    parser.add_argument(
        "--claude-model",
        default="haiku",
        choices=["opus", "sonnet", "haiku"],
        help="Claude model for formatting. opus=best, sonnet=balanced, haiku=fastest/cheapest. (default: haiku)",
    )
    parser.add_argument(
        "--no-format",
        action="store_true",
        help="Skip Claude formatting and save the raw Whisper transcription only.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    audio_files = collect_audio_files(input_path)

    for audio_file in audio_files:
        raw = transcribe(audio_file, args.model)

        if args.no_format:
            formatted = None
        else:
            formatted = format_with_claude(raw, args.claude_model)

        md_path = write_markdown(audio_file, formatted, raw, skip_format=args.no_format)
        print(f"Saved: {md_path}\n")

    print(f"Done. {len(audio_files)} file(s) transcribed.")


if __name__ == "__main__":
    main()
