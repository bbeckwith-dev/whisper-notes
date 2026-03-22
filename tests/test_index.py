from whisper_notes.index import (
    generate_index,
    write_index,
    load_processed_sources,
    load_existing_entries,
    IndexEntry,
    UnprocessedEntry,
)


def test_generate_index_with_entries():
    entries = [
        IndexEntry(
            file="weightlifting-goals.md",
            title="weightlifting-goals",
            date="2026-03-21",
            medium="audio",
            vault="self-observations",
            source="recordings/voice001.m4a",
        )
    ]
    content = generate_index(entries, [])
    assert "## Processed Files" in content
    assert "weightlifting-goals.md" in content
    assert "voice001.m4a" in content


def test_generate_index_with_unprocessed():
    unprocessed = [
        UnprocessedEntry(file="doc.pages", reason="Unsupported format")
    ]
    content = generate_index([], unprocessed)
    assert "## Unprocessed Files" in content
    assert "doc.pages" in content
    assert "Unsupported format" in content


def test_write_and_load_index(tmp_path):
    entries = [
        IndexEntry(
            file="note.md",
            title="note",
            date="2026-03-21",
            medium="audio",
            vault="self-observations",
            source="recordings/voice001.m4a",
        )
    ]
    write_index(entries, [], tmp_path)
    assert (tmp_path / "_index.md").exists()
    sources = load_processed_sources(tmp_path)
    assert "recordings/voice001.m4a" in sources


def test_load_processed_sources_empty(tmp_path):
    sources = load_processed_sources(tmp_path)
    assert sources == set()


def test_load_existing_entries(tmp_path):
    entries = [
        IndexEntry(
            file="note.md",
            title="note",
            date="2026-03-21",
            medium="audio",
            vault="self-observations",
            source="recordings/voice001.m4a",
        )
    ]
    write_index(entries, [], tmp_path)
    loaded = load_existing_entries(tmp_path)
    assert len(loaded) == 1
    assert loaded[0].source == "recordings/voice001.m4a"
