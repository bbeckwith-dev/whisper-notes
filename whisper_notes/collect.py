import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav", ".mp4", ".mov", ".m4v"}
TEXT_EXTENSIONS = {".md", ".txt", ".docx", ".rtf"}
DATE_FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class FileEntry:
    path: Path
    medium: str  # "audio" or "document"


@dataclass
class SkippedEntry:
    path: Path
    reason: str


@dataclass
class CollectedFiles:
    supported: list[FileEntry]
    unsupported: list[SkippedEntry]


SKIP_DIRS = {"processed"}


def collect_files(input_path: Path) -> CollectedFiles:
    """Collect supported and unsupported files from a path."""
    if input_path.is_file():
        entry = _classify_file(input_path)
        if isinstance(entry, FileEntry):
            return CollectedFiles(supported=[entry], unsupported=[])
        return CollectedFiles(supported=[], unsupported=[entry])

    supported = []
    unsupported = []
    for f in sorted(input_path.rglob("*")):
        if f.is_symlink() or not f.is_file():
            continue
        # Skip files inside output directories
        if SKIP_DIRS & {p.name for p in f.relative_to(input_path).parents}:
            continue
        entry = _classify_file(f)
        if isinstance(entry, FileEntry):
            supported.append(entry)
        else:
            unsupported.append(entry)
    return CollectedFiles(supported=supported, unsupported=unsupported)


def _classify_file(path: Path) -> FileEntry | SkippedEntry:
    suffix = path.suffix.lower()
    if suffix in AUDIO_EXTENSIONS:
        return FileEntry(path=path, medium="audio")
    if suffix in TEXT_EXTENSIONS:
        return FileEntry(path=path, medium="document")
    return SkippedEntry(path=path, reason="Unsupported format")


def resolve_date(file_path: Path) -> str:
    """Resolve date: folder name YYYY-MM-DD > mtime > today."""
    parent_name = file_path.parent.name
    if DATE_FOLDER_RE.match(parent_name):
        return parent_name
    mtime = file_path.stat().st_mtime
    return datetime.fromtimestamp(mtime).date().isoformat()
