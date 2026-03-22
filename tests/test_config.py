from whisper_notes.config import load_config, save_config, add_vault, DEFAULT_VAULTS


def test_load_creates_default_when_missing(tmp_path):
    config = load_config(tmp_path / "config.json")
    assert config["vaults"] == DEFAULT_VAULTS


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "config.json"
    config = {"vaults": ["test-vault"]}
    save_config(config, path)
    loaded = load_config(path)
    assert loaded == config


def test_add_vault():
    config = {"vaults": ["a", "b"]}
    add_vault(config, "c")
    assert config["vaults"] == ["a", "b", "c"]


def test_add_duplicate_vault_is_noop():
    config = {"vaults": ["a", "b"]}
    add_vault(config, "a")
    assert config["vaults"] == ["a", "b"]
