from whisper_notes.output import write_processed


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
