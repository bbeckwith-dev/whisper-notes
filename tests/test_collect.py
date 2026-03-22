from datetime import date
from whisper_notes.collect import collect_files, resolve_date


def test_collect_audio_files(tmp_path):
    (tmp_path / "a.m4a").touch()
    (tmp_path / "b.mp3").touch()
    result = collect_files(tmp_path)
    audio = [f for f in result.supported if f.medium == "audio"]
    assert len(audio) == 2


def test_collect_text_files(tmp_path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.md").touch()
    result = collect_files(tmp_path)
    docs = [f for f in result.supported if f.medium == "document"]
    assert len(docs) == 2


def test_collect_unsupported_files(tmp_path):
    (tmp_path / "doc.pages").touch()
    result = collect_files(tmp_path)
    assert len(result.unsupported) == 1
    assert result.unsupported[0].reason == "Unsupported format"


def test_collect_recursive(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "a.m4a").touch()
    (tmp_path / "b.m4a").touch()
    result = collect_files(tmp_path)
    assert len(result.supported) == 2


def test_collect_ignores_symlinks(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    (real / "a.m4a").touch()
    link = tmp_path / "link"
    link.symlink_to(real)
    result = collect_files(tmp_path)
    assert len(result.supported) == 1


def test_collect_single_file(tmp_path):
    f = tmp_path / "test.m4a"
    f.touch()
    result = collect_files(f)
    assert len(result.supported) == 1


def test_collect_skips_processed_dir(tmp_path):
    (tmp_path / "a.m4a").touch()
    processed = tmp_path / "processed"
    processed.mkdir()
    (processed / "note.md").write_text("already processed")
    result = collect_files(tmp_path)
    assert len(result.supported) == 1
    assert result.supported[0].path.name == "a.m4a"


def test_date_from_folder_name(tmp_path):
    folder = tmp_path / "2026-03-21"
    folder.mkdir()
    f = folder / "test.m4a"
    f.touch()
    assert resolve_date(f) == "2026-03-21"


def test_date_from_mtime(tmp_path):
    f = tmp_path / "test.m4a"
    f.touch()
    assert resolve_date(f) == date.today().isoformat()


def test_date_folder_priority_over_mtime(tmp_path):
    folder = tmp_path / "2025-01-15"
    folder.mkdir()
    f = folder / "test.m4a"
    f.touch()
    assert resolve_date(f) == "2025-01-15"
