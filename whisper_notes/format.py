import re
from dataclasses import dataclass


@dataclass
class ParsedResponse:
    title: str
    vault: str
    date: str
    processed: str
    medium: str
    body: str


FORMAT_PROMPT_TEMPLATE = """\
You are a note processor. I will give you raw content from a {medium} source.

Generate structured markdown with YAML frontmatter using these exact field values:
- date: {date}
- processed: {processed}
- status: raw
- medium: {medium}

You must also generate:
- title: a short, descriptive kebab-case name (max 20 characters)
- vault: choose the most appropriate category from: {vaults}

Then write two sections:

1. **## Summary** — A comprehensive markdown summary of the content. Capture all \
key points, ideas, and themes. Use headings, bullet points, and structure as needed \
to make it a useful reference. No length limit — be as thorough as the content warrants.

2. **## Cleaned Transcription** — The original content, cleaned up for readability. \
Fix grammar, punctuation, and sentence structure. Remove filler words (um, uh, \
like, you know) and false starts if present. Do NOT rewrite or rephrase — preserve \
the original words and meaning. The goal is a grammatically correct version of the \
source content, not a reinterpretation.

Output exactly this format and nothing else:
---
title: <kebab-case-name>
date: {date}
processed: {processed}
status: raw
medium: {medium}
vault: <your-choice>
---

## Summary
<comprehensive summary>

## Cleaned Transcription
<grammatically cleaned transcription>\
"""

CLAUDE_MODELS = {
    "opus": "claude-opus-4-6",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
}


def build_prompt(date: str, processed: str, medium: str, vaults: list[str]) -> str:
    """Build the system prompt with interpolated values."""
    return FORMAT_PROMPT_TEMPLATE.format(
        date=date,
        processed=processed,
        medium=medium,
        vaults=", ".join(vaults),
    )


def parse_response(response: str) -> ParsedResponse:
    """Parse Claude's structured response into components."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", response.strip(), re.DOTALL)
    if not match:
        raise ValueError("Response missing YAML frontmatter delimiters (---)")

    fm_text = match.group(1)
    body = match.group(2).strip()

    def extract(field: str) -> str:
        m = re.search(rf"^{field}:\s*(.+)$", fm_text, re.MULTILINE)
        if not m:
            raise ValueError(f"Missing frontmatter field: {field}")
        return m.group(1).strip()

    return ParsedResponse(
        title=extract("title"),
        vault=extract("vault"),
        date=extract("date"),
        processed=extract("processed"),
        medium=extract("medium"),
        body=body,
    )


def compose_output(parsed: ParsedResponse, raw_text: str | None) -> str:
    """Compose final markdown output (frontmatter without vault + body + optional raw)."""
    frontmatter = (
        f"---\n"
        f"title: {parsed.title}\n"
        f"date: {parsed.date}\n"
        f"processed: {parsed.processed}\n"
        f"status: raw\n"
        f"medium: {parsed.medium}\n"
        f"---"
    )
    parts = [frontmatter, "", parsed.body]
    if raw_text is not None:
        parts.extend(["", "---", "", "## Raw Transcription", "", raw_text])
    return "\n".join(parts) + "\n"
