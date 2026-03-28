from __future__ import annotations

from pathlib import Path

import pytest

import envctl.config.loader as loader
from envctl.errors import ConfigError


def configure_defaults(monkeypatch, tmp_path: Path, config_path: Path) -> None:
    monkeypatch.setattr(loader, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(loader, "get_default_vault_dir", lambda: tmp_path / "vault-default")
    monkeypatch.setattr(loader, "get_default_env_filename", lambda: ".env.local")
    monkeypatch.setattr(loader, "get_default_schema_filename", lambda: ".envctl.schema.yaml")


def test_load_config_uses_defaults_when_config_file_is_missing(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)

    config = loader.load_config()

    assert config.config_path == config_path
    assert config.vault_dir == (tmp_path / "vault-default").resolve()
    assert config.env_filename == ".env.local"
    assert config.schema_filename == ".envctl.schema.yaml"


def test_load_config_reads_valid_json_config(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)

    config_path.write_text(
        """
{
  "vault_dir": "./custom-vault",
  "env_filename": ".env.dev",
  "schema_filename": ".contract.yaml"
}
""".strip(),
        encoding="utf-8",
    )

    config = loader.load_config()

    assert config.config_path == config_path
    assert config.vault_dir == Path("./custom-vault").resolve()
    assert config.env_filename == ".env.dev"
    assert config.schema_filename == ".contract.yaml"


def test_load_config_rejects_invalid_json(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ConfigError, match="Invalid JSON config"):
        loader.load_config()


def test_load_config_rejects_unreadable_config(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text("{}", encoding="utf-8")

    def broken_read_text(self, encoding: str = "utf-8") -> str:
        raise OSError("boom")

    monkeypatch.setattr(loader.Path, "read_text", broken_read_text)

    with pytest.raises(ConfigError, match="Unable to read config file"):
        loader.load_config()


def test_load_config_rejects_non_object_json(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text('["not", "an", "object"]', encoding="utf-8")

    with pytest.raises(ConfigError, match="Config file must contain a JSON object"):
        loader.load_config()


def test_load_config_rejects_unknown_keys(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text('{"extra_key": "value"}', encoding="utf-8")

    with pytest.raises(ConfigError, match="Unsupported config key\\(s\\): extra_key"):
        loader.load_config()


def test_load_config_rejects_empty_env_filename(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text('{"env_filename": "   "}', encoding="utf-8")

    with pytest.raises(ConfigError, match="env_filename cannot be empty"):
        loader.load_config()


def test_load_config_rejects_env_filename_paths(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text('{"env_filename": "nested/.env.local"}', encoding="utf-8")

    with pytest.raises(ConfigError, match="env_filename must be a file name, not a path"):
        loader.load_config()


def test_load_config_rejects_invalid_schema_filename(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    configure_defaults(monkeypatch, tmp_path, config_path)
    config_path.write_text('{"schema_filename": "contracts/schema.yaml"}', encoding="utf-8")

    with pytest.raises(ConfigError, match="schema_filename must be a file name, not a path"):
        loader.load_config()