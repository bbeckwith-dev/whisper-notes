import pytest
from whisper_notes.format import (
    build_prompt,
    parse_response,
    compose_output,
    ParsedResponse,
)


def test_build_prompt_includes_all_fields():
    prompt = build_prompt(
        date="2026-03-21",
        processed="2026-03-21T14:32:00",
        medium="audio",
        vaults=["self-observations", "software-engineering"],
    )
    assert "2026-03-21" in prompt
    assert "audio" in prompt
    assert "self-observations" in prompt
    assert "software-engineering" in prompt


def test_parse_response_extracts_fields(sample_claude_response):
    parsed = parse_response(sample_claude_response)
    assert parsed.title == "weightlifting-goals"
    assert parsed.vault == "self-observations"
    assert parsed.date == "2026-03-21"
    assert parsed.processed == "2026-03-21T14:32:00"
    assert parsed.medium == "audio"
    assert "## Summary" in parsed.body
    assert "## Cleaned Transcription" in parsed.body


def test_parse_response_missing_frontmatter():
    with pytest.raises(ValueError, match="frontmatter"):
        parse_response("No frontmatter here")


def test_compose_output_audio_includes_raw():
    parsed = ParsedResponse(
        title="test-note",
        vault="self-observations",
        date="2026-03-21",
        processed="2026-03-21T14:00:00",
        medium="audio",
        body="## Summary\nTest summary\n\n## Cleaned Transcription\nCleaned content",
    )
    output = compose_output(parsed, raw_text="raw whisper output")
    assert output.startswith("---\n")
    assert "title: test-note" in output
    # vault stripped from frontmatter
    fm_section = output.split("---")[1]
    assert "vault" not in fm_section
    assert "## Raw Transcription" in output
    assert "raw whisper output" in output


def test_compose_output_document_no_raw():
    parsed = ParsedResponse(
        title="test-doc",
        vault="software-engineering",
        date="2026-03-21",
        processed="2026-03-21T14:00:00",
        medium="document",
        body="## Summary\nTest\n\n## Cleaned Transcription\nContent",
    )
    output = compose_output(parsed, raw_text=None)
    assert "## Raw Transcription" not in output


from unittest.mock import MagicMock, patch
from whisper_notes.format import format_with_claude


def test_format_with_claude_returns_response(sample_claude_response):
    mock_stream = MagicMock()
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.text_stream = iter([sample_claude_response])

    mock_client = MagicMock()
    mock_client.messages.stream.return_value = mock_stream

    with patch("whisper_notes.format.anthropic.Anthropic", return_value=mock_client):
        result = format_with_claude(
            raw_text="test input",
            system_prompt="test prompt",
            model_id="claude-sonnet-4-6",
        )

    assert "weightlifting-goals" in result
    mock_client.messages.stream.assert_called_once()
