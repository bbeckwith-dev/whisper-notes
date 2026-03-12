# whisper-notes

Transcribe audio recordings from [Just Press Record](https://www.openplanetsoftware.com/just-press-record/) (or any audio app) into markdown files using [OpenAI Whisper](https://github.com/openai/whisper).

## Requirements

- macOS with Apple Silicon
- [Homebrew](https://brew.sh)
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [ffmpeg](https://ffmpeg.org)

## Setup

```bash
# Install uv and ffmpeg (if not already installed)
brew install uv ffmpeg

# Install Python dependencies
uv sync
```

## Usage

```bash
# Transcribe a single file
uv run main.py recording.m4a

# Transcribe all audio files in a folder
uv run main.py recordings/

# Use a more accurate model
uv run main.py recording.m4a --model medium
```

The transcript is saved as a `.md` file next to the original audio file.

**Example:** `morning-notes.m4a` → `morning-notes.md`

```markdown
# morning-notes

Pick up groceries on the way home. Also need to call the dentist about that
appointment next week...
```

## Models

| Model | Speed | Accuracy | Best for |
|-------|-------|----------|---------|
| `tiny` | Fastest | Low | Quick drafts |
| `base` | Fast | Good | Clear speech (default) |
| `small` | Moderate | Better | Accents, noisy audio |
| `medium` | Slow | Great | High accuracy needed |
| `large` | Slowest | Best | Maximum accuracy |

The model is downloaded automatically on first use and cached locally.

## Supported audio formats

`.m4a` `.mp3` `.wav` `.mp4` `.mov` `.m4v`
