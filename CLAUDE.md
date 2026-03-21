# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run on a single file
uv run main.py recording.m4a

# Run on a directory of audio files
uv run main.py recordings/

# Common flags
uv run main.py recording.m4a --model medium          # larger Whisper model
uv run main.py recording.m4a --claude-model sonnet   # better Claude model
uv run main.py recording.m4a --no-format             # skip Claude, raw transcription only
```

No lint or test commands exist yet — this is a single-script tool with no test suite.

## Architecture

Everything lives in `main.py`. The pipeline is:

1. **`collect_audio_files`** — resolves a file or directory path into a list of audio files
2. **`transcribe`** — loads the requested Whisper model and runs speech-to-text; returns raw text
3. **`format_with_claude`** — streams the raw text through Claude using `FORMAT_PROMPT`; prints streamed output to stdout in real time
4. **`write_markdown`** — writes a `.md` file next to the audio source; includes both Claude-formatted content and a `## Raw Transcription` section (or just the raw text with `--no-format`)

**Model mappings** (`CLAUDE_MODELS` dict) map shorthand names (`haiku`, `sonnet`, `opus`) to full Anthropic model IDs. Update these when newer Claude models are released.

**Output format** (with formatting): Claude-formatted markdown on top, a `---` divider, then `## Raw Transcription` at the bottom.

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
