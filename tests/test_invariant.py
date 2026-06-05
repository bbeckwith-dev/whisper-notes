"""The prime directive: a run must leave the input tree byte-for-byte identical.

This test snapshots the input directory (relative path -> size, mtime, content
hash) before and after a full batch run and asserts equality. It exists so a
future change cannot quietly reintroduce writing into the source tree (e.g. the
old archival rename).
"""

import hashlib
from pathlib import Path
from unittest.mock import patch

from whisper_notes.collect import FileEntry
from whisper_notes.pipeline import process_batch


def _snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    """Map each file under root to (size, mtime_ns, sha256)."""
    snap: dict[str, tuple[int, int, str]] = {}
    for f in sorted(root.rglob("*")):
        if not f.is_file():
            continue
        data = f.read_bytes()
        st = f.stat()
        rel = str(f.relative_to(root))
        snap[rel] = (st.st_size, st.st_mtime_ns, hashlib.sha256(data).hexdigest())
    return snap


def test_input_tree_unchanged_after_run(
    tmp_path, sample_config, sample_claude_response
):
    input_root = tmp_path / "input"
    (input_root / "2026-01").mkdir(parents=True)
    audio = input_root / "2026-01" / "voice001.m4a"
    audio.write_bytes(b"fake audio bytes")
    doc = input_root / "notes.txt"
    doc.write_text("some document text")
    output_dir = tmp_path / "out"

    before = _snapshot(input_root)

    with patch(
        "whisper_notes.pipeline.transcribe", return_value="raw whisper text"
    ), patch(
        "whisper_notes.pipeline.format_with_claude",
        return_value=sample_claude_response,
    ):
        process_batch(
            files=[
                FileEntry(path=audio, medium="audio"),
                FileEntry(path=doc, medium="document"),
            ],
            config=sample_config,
            output_dir=output_dir,
            input_root=input_root,
            whisper_model="small",
            claude_model_id="claude-sonnet-4-6",
        )

    after = _snapshot(input_root)
    assert after == before
    # And the artifacts really were produced under output_dir only.
    assert list(output_dir.rglob("*.md"))
