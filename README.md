# whisper-notes

Transcribe audio recordings and process text documents into structured, categorized markdown using [OpenAI Whisper](https://github.com/openai/whisper) and the [Anthropic API](https://www.anthropic.com). Designed as an intake pipeline for [Obsidian](https://obsidian.md) vaults.

## Requirements

- macOS with Apple Silicon (or any platform that supports Whisper)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [ffmpeg](https://ffmpeg.org)
- An [Anthropic API key](https://console.anthropic.com)

## Setup

```bash
# Install uv and ffmpeg (if not already installed)
brew install uv ffmpeg

# Install Python dependencies
uv sync

# Add your Anthropic API key
cp .env.example .env
# Then open .env and replace the placeholder with your key
```

## Usage

```bash
# Process a single audio file
uv run main.py recording.m4a

# Process a text document
uv run main.py notes.txt

# Process all supported files in a folder (recursive)
uv run main.py recordings/

# Use a more accurate Whisper model
uv run main.py recording.m4a --model medium

# Use a different Claude model for formatting
uv run main.py recording.m4a --claude-model opus

# Skip Claude formatting entirely (raw transcription only, audio files only)
uv run main.py recording.m4a --no-format

# Reprocess files that were already processed
uv run main.py recordings/ --force

# Write notes to a directory other than ./processed
uv run main.py recordings/ --output-dir ~/obsidian-intake
```

When processing a directory, you'll see a preview of what will be processed before confirming:

```
Files to process: 3
  Audio: 2
  Documents: 1
  Estimated API calls: 3 (Claude)
  Whisper transcriptions: 2

Proceed? [Y/n]
```

Files that have already been processed are automatically skipped on subsequent runs (use `--force` to override).

## Output

Processed files are written to the output directory (default `processed/`, set with `--output-dir`), mirroring the input's subfolder layout so each note lines up with its original. **The input tree is never modified** — nothing is written beside your sources and originals are never renamed. Each note carries a `source:` field in its frontmatter pointing back to the exact original file:

```markdown
---
title: weightlifting-goals
date: 2026-03-21
processed: 2026-03-21T14:32:00
status: raw
medium: audio
source: /Users/you/recordings/2026-01/voice001.m4a
---

## Summary

This recording covers a discussion about weightlifting goals for the
upcoming quarter, including specific targets for squat and deadlift
numbers and thoughts on training split adjustments.

## Cleaned Transcription

I want to increase my squat to 300 lbs by the end of the quarter.
For deadlifts, I'm going to focus on form over weight for now.

---

## Raw Transcription

i want to increase my squat to like 300 lbs by the end of the quarter
um for deadlifts im going to focus on form over weight for now...
```

Originals are the source of truth, so a run never touches them: no markdown is written beside a source, and no file is renamed — for audio and documents alike. Traceability is provided three redundant ways instead: the `source:` frontmatter field (a precise pointer), the mirrored output subfolders (locations line up), and the `_index.md` row.

### Index

Each run updates `_index.md` at the root of the output directory — a table tracking all processed files, their source paths, dates, and vault assignments. Unsupported files found during collection are listed separately.

## Vault categorization

Claude assigns each processed file to a vault category from `config.json`. Default vaults:

- `fantasy-writing`
- `game-development`
- `self-observations`
- `software-engineering`

If Claude suggests a vault that doesn't exist, you'll be prompted to add it. Edit `config.json` directly to add or remove vaults.

## Supported formats

**Audio:** `.m4a` `.mp3` `.wav` `.mp4` `.mov` `.m4v`

**Documents:** `.txt` `.md` `.docx` `.rtf`

## Whisper models

| Model | Speed | Accuracy | Best for |
|-------|-------|----------|---------|
| `tiny` | Fastest | Low | Quick drafts |
| `base` | Fast | Good | Clear speech |
| `small` | Moderate | Better | Accents, noisy audio (default) |
| `medium` | Slow | Great | High accuracy needed |
| `large` | Slowest | Best | Maximum accuracy |

The model is downloaded automatically on first use and cached locally.

## Claude models

| Model | Speed | Cost | Best for |
|-------|-------|------|---------|
| `haiku` | Fastest | Lowest | Quick processing |
| `sonnet` | Moderate | Mid | Good balance (default) |
| `opus` | Slowest | Highest | Best quality formatting |

## Development

```bash
# Run tests
uv run pytest tests/ -v
```
