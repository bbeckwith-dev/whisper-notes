import tempfile
from pathlib import Path


def _atomic_write(path: Path, content: str) -> None:
    """Write content to a temp file then rename for atomicity."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)
        Path(tmp).rename(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_processed(title: str, content: str, output_dir: Path) -> Path:
    """Write content to processed/ with collision handling. Returns final path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{title}.md"
    if not path.exists():
        _atomic_write(path, content)
        return path

    n = 2
    while True:
        path = output_dir / f"{title}-{n}.md"
        if not path.exists():
            _atomic_write(path, content)
            return path
        n += 1
