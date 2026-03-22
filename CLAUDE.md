# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run on a single file (audio or text document)
uv run main.py recording.m4a
uv run main.py notes.txt

# Run on a directory (recursive, with preview)
uv run main.py recordings/

# Common flags
uv run main.py recording.m4a --model medium          # larger Whisper model
uv run main.py recording.m4a --claude-model opus     # better Claude model (default: sonnet)
uv run main.py recording.m4a --no-format             # skip Claude, raw transcription only
uv run main.py recordings/ --force                   # reprocess already-processed files

# Run tests
uv run pytest tests/ -v
```

## Architecture

`main.py` is a slim CLI entry point. The processing logic lives in the `whisper_notes/` package:

| Module | Responsibility |
|--------|---------------|
| `config.py` | Load/save `config.json`, vault management |
| `collect.py` | File discovery (recursive), date resolution, format detection |
| `format.py` | Prompt template, Claude API streaming, response parsing |
| `output.py` | Write to `processed/`, naming, collision handling, archival |
| `index.py` | Generate/update `_index.md` in `processed/` |
| `readers.py` | Extract text from `.md`, `.txt`, `.docx`, `.rtf` files |
| `pipeline.py` | Orchestrate processing: transcribe/read → format → write → preview |

**Pipeline flow:**
1. **`collect_files`** — recursively discovers audio + text files, skips `processed/`
2. **Skip logic** — checks `_index.md` for already-processed sources (unless `--force`)
3. **`transcribe`** (audio) or **`read_document`** (text) — gets raw content
4. **`format_with_claude`** — streams through Claude with structured prompt; produces YAML frontmatter + Summary + Cleaned Transcription
5. **`write_processed`** — writes to `processed/<title>.md` with collision handling
6. **`write_archival`** — writes `.md` copy next to source audio + renames audio to match title
7. **`write_index`** — updates `processed/_index.md` with all entries

**Supported formats:** Audio (`.m4a`, `.mp3`, `.wav`, `.mp4`, `.mov`, `.m4v`), Documents (`.md`, `.txt`, `.docx`, `.rtf`)

**Model mappings** (`CLAUDE_MODELS` dict in `format.py`) map shorthand names (`haiku`, `sonnet`, `opus`) to full Anthropic model IDs. Update these when newer Claude models are released.

**Environment**: Requires `ANTHROPIC_API_KEY` in `.env` (copy from `.env.example`). The key is loaded via `python-dotenv` at startup. Also copy `config.example.json` to `config.json` and add your vault names.
