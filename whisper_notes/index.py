import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IndexEntry:
    file: str
    title: str
    date: str
    medium: str
    vault: str
    source: str


@dataclass
class UnprocessedEntry:
    file: str
    reason: str


def generate_index(
    entries: list[IndexEntry], unprocessed: list[UnprocessedEntry]
) -> str:
    """Generate _index.md content."""
    lines = ["# Processed Notes Index", ""]
    lines.append("## Processed Files")
    lines.append("| File | Title | Date | Medium | Vault | Source Path |")
    lines.append("|------|-------|------|--------|-------|-------------|")
    for e in entries:
        lines.append(
            f"| {e.file} | {e.title} | {e.date} | {e.medium} | {e.vault} | {e.source} |"
        )
    lines.append("")

    if unprocessed:
        lines.append("## Unprocessed Files")
        lines.append("| File | Reason |")
        lines.append("|------|--------|")
        for u in unprocessed:
            lines.append(f"| {u.file} | {u.reason} |")
        lines.append("")

    return "\n".join(lines)


def write_index(
    entries: list[IndexEntry],
    unprocessed: list[UnprocessedEntry],
    output_dir: Path,
) -> Path:
    """Write _index.md to output directory."""
    content = generate_index(entries, unprocessed)
    path = output_dir / "_index.md"
    output_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def load_processed_sources(output_dir: Path) -> set[str]:
    """Load set of already-processed source paths from _index.md."""
    return {e.source for e in load_existing_entries(output_dir)}


def load_existing_entries(output_dir: Path) -> list[IndexEntry]:
    """Load existing IndexEntry list from _index.md for merging."""
    index_path = output_dir / "_index.md"
    if not index_path.exists():
        return []

    entries = []
    content = index_path.read_text(encoding="utf-8")
    for match in re.finditer(
        r"^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|$",
        content,
        re.MULTILINE,
    ):
        file, title, date, medium, vault, source = (
            g.strip() for g in match.groups()
        )
        if file == "File" or file.startswith("-"):
            continue
        entries.append(IndexEntry(
            file=file, title=title, date=date,
            medium=medium, vault=vault, source=source,
        ))
    return entries
