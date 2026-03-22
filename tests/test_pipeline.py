from pathlib import Path
from unittest.mock import patch
from whisper_notes.pipeline import process_file, show_preview, ProcessResult
from whisper_notes.collect import FileEntry


def test_process_file_audio(tmp_path, sample_config, sample_claude_response):
    source = tmp_path / "recordings" / "voice001.m4a"
    source.parent.mkdir()
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
            whisper_model="small",
            claude_model_id="claude-sonnet-4-6",
        )

    assert result.processed_path.exists()
    assert "weightlifting-goals" in result.processed_path.name
    content = result.processed_path.read_text()
    assert "## Raw Transcription" in content
    assert "raw whisper text" in content


def test_process_file_document(tmp_path, sample_config):
    source = tmp_path / "notes.txt"
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
            whisper_model="small",
            claude_model_id="claude-sonnet-4-6",
        )

    assert result.processed_path.exists()
    content = result.processed_path.read_text()
    assert "## Raw Transcription" not in content
    assert source.exists()  # document source left untouched


def test_show_preview(capsys):
    files = [
        FileEntry(Path("a.m4a"), "audio"),
        FileEntry(Path("b.txt"), "document"),
    ]
    show_preview(files, skip_count=1)
    output = capsys.readouterr().out
    assert "2" in output
    assert "1" in output
