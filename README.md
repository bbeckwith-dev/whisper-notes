# whisper-notes

Transcribe audio recordings from [Just Press Record](https://www.openplanetsoftware.com/just-press-record/) (or any audio app) into markdown files using [OpenAI Whisper](https://github.com/openai/whisper), then reformat them into clean, structured markdown using the [Anthropic API](https://www.anthropic.com).

## Requirements

- macOS with Apple Silicon
- [Homebrew](https://brew.sh)
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
# Transcribe and format a single file (defaults: small Whisper model, Haiku)
uv run main.py recording.m4a

# Transcribe all audio files in a folder
uv run main.py recordings/

# Use a more accurate Whisper model
uv run main.py recording.m4a --model medium

# Use a different Claude model for formatting
uv run main.py recording.m4a --claude-model sonnet
uv run main.py recording.m4a --claude-model opus

# Skip Claude formatting entirely (raw transcription only)
uv run main.py recording.m4a --no-format
```

The transcript is saved as a `.md` file next to the original audio file.

**Example:** `morning-notes.m4a` → `morning-notes.md`

```markdown
## Morning Notes

- Pick up groceries on the way home
- Call the dentist about the appointment next week

---

## Raw Transcription

Pick up groceries on the way home also need to call the dentist about that
appointment next week...
```

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
| `haiku` | Fastest | Lowest | Everyday use (default) |
| `sonnet` | Moderate | Mid | Better structure and phrasing |
| `opus` | Slowest | Highest | Best quality formatting |

## Supported audio formats

`.m4a` `.mp3` `.wav` `.mp4` `.mov` `.m4v`
