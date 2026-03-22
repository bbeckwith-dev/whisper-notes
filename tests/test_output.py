from whisper_notes.output import write_processed, write_archival


def test_write_processed_creates_dir(tmp_path):
    output_dir = tmp_path / "processed"
    path = write_processed("my-note", "content\n", output_dir)
    assert path == output_dir / "my-note.md"
    assert path.read_text() == "content\n"


def test_write_processed_collision_suffix(tmp_path):
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    (output_dir / "my-note.md").write_text("existing")
    path = write_processed("my-note", "new\n", output_dir)
    assert path == output_dir / "my-note-2.md"


def test_write_processed_multiple_collisions(tmp_path):
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    (output_dir / "my-note.md").write_text("1")
    (output_dir / "my-note-2.md").write_text("2")
    path = write_processed("my-note", "3\n", output_dir)
    assert path == output_dir / "my-note-3.md"


def test_write_archival_audio(tmp_path):
    source = tmp_path / "voice001.m4a"
    source.write_bytes(b"fake audio")
    md_path, new_source = write_archival(source, "my-note", "content\n")
    assert md_path == tmp_path / "my-note.md"
    assert md_path.read_text() == "content\n"
    assert new_source == tmp_path / "my-note.m4a"
    assert new_source.exists()
    assert not source.exists()


def test_write_archival_same_name_no_rename(tmp_path):
    source = tmp_path / "my-note.m4a"
    source.write_bytes(b"fake audio")
    md_path, new_source = write_archival(source, "my-note", "content\n")
    assert md_path == tmp_path / "my-note.md"
    assert new_source == tmp_path / "my-note.m4a"
    assert new_source.exists()
