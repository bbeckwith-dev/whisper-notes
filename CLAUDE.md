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

**Environment**: Requires `ANTHROPIC_API_KEY` in `.env` (copy from `.env.example`). The key is loaded via `python-dotenv` at startup.

## Working Principles

### 1. Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing:
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

Define success criteria. Loop until verified.

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
