from pathlib import Path
from unittest.mock import MagicMock, patch

from whisper_notes.pipeline import (
    mirror_subpath,
    process_file,
    show_preview,
    transcribe_raw_only,
    ProcessResult,
)
from whisper_notes.collect import FileEntry


def test_mirror_subpath_nested(tmp_path):
    root = tmp_path / "input"
    f = root / "2026-01" / "a.m4a"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"x")
    assert mirror_subpath(root, f) == Path("2026-01")


def test_mirror_subpath_root_level(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    f = root / "a.m4a"
    f.write_bytes(b"x")
    assert mirror_subpath(root, f) == Path(".")


def test_process_file_audio(tmp_path, sample_config, sample_claude_response):
    input_root = tmp_path / "input"
    source = input_root / "recordings" / "voice001.m4a"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"fake audio")
    output_dir = tmp_path / "processed"

    with patch("whisper_notes.pipeline.transcribe") as mock_transcribe, \
         patch("whisper_notes.pipeline.format_with_claude") as mock_format:
        mock_transcribe.return_value = "raw whisper text"
        mock_format.return_value = sample_claude_response

        result = process_file(
            entry=FileEntry(path=source, medium="audio"),
            config=sample_config,
            output_dir=output_dir,
            input_root=input_root,
            whisper_model="small",
            claude_model_id="claude-sonnet-4-6",
        )

    assert result.processed_path.exists()
    # Output mirrors the input subdirectory under output_dir
    assert result.processed_path.parent == output_dir / "recordings"
    assert "weightlifting-goals" in result.processed_path.name
    content = result.processed_path.read_text()
    assert "## Raw Transcription" in content
    assert "raw whisper text" in content
    # source frontmatter points at the original absolute path
    assert f"source: {source.resolve()}" in content
    # Invariant: source untouched, no stray .md next to it
    assert source.exists()
    assert source.read_bytes() == b"fake audio"
    assert not (source.parent / "weightlifting-goals.md").exists()


def test_process_file_document(tmp_path, sample_config):
    input_root = tmp_path / "input"
    input_root.mkdir()
    source = input_root / "notes.txt"
    source.write_text("My document content")
    output_dir = tmp_path / "processed"

    response = (
        "---\n"
        "title: my-doc-notes\n"
        "date: 2026-03-21\n"
        "processed: 2026-03-21T14:00:00\n"
        "status: raw\n"
        "medium: document\n"
        "vault: software-engineering\n"
        "---\n\n"
        "## Summary\nSummary here\n\n"
        "## Cleaned Transcription\nCleaned content"
    )

    with patch("whisper_notes.pipeline.format_with_claude") as mock_format:
        mock_format.return_value = response

        result = process_file(
            entry=FileEntry(path=source, medium="document"),
            config=sample_config,
            output_dir=output_dir,
            input_root=input_root,
            whisper_model="small",
            claude_model_id="claude-sonnet-4-6",
        )

    assert result.processed_path.exists()
    # Root-level source mirrors to output_dir root
    assert result.processed_path.parent == output_dir
    content = result.processed_path.read_text()
    assert "## Raw Transcription" not in content
    assert source.exists()  # document source left untouched


def test_transcribe_raw_only_writes_to_output(tmp_path):
    input_root = tmp_path / "input"
    source = input_root / "sub" / "voice001.m4a"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"fake audio")
    output_dir = tmp_path / "processed"

    with patch("whisper_notes.pipeline.transcribe", return_value="raw text"), \
         patch("whisper.load_model", return_value=MagicMock()):
        written = transcribe_raw_only(
            files=[FileEntry(path=source, medium="audio")],
            input_root=input_root,
            output_dir=output_dir,
            whisper_model="small",
        )

    assert written[0].parent == output_dir / "sub"
    assert written[0].read_text() == "# voice001\n\nraw text\n"
    # Invariant: source untouched, nothing written into the input tree
    assert source.exists()
    assert not (source.parent / "voice001.md").exists()


def test_show_preview(capsys):
    files = [
        FileEntry(Path("a.m4a"), "audio"),
        FileEntry(Path("b.txt"), "document"),
    ]
    show_preview(files, skip_count=1)
    output = capsys.readouterr().out
    assert "2" in output
    assert "1" in output
