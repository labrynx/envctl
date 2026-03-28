from __future__ import annotations

import json
from pathlib import Path

import pytest

import envctl.config.writer as writer
from envctl.errors import ConfigError


def test_write_default_config_file_creates_config(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "config.json"
    vault_dir = tmp_path / "vault"

    monkeypatch.setattr(writer, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(writer, "get_default_vault_dir", lambda: vault_dir)
    monkeypatch.setattr(writer, "get_default_env_filename", lambda: ".env.local")
    monkeypatch.setattr(writer, "get_default_schema_filename", lambda: ".envctl.schema.yaml")
    monkeypatch.setattr(writer, "to_tilde_path", lambda path: "~/vault")

    result = writer.write_default_config_file()

    assert result == config_path
    assert config_path.exists()

    data = json.loads(config_path.read_text(encoding="utf-8"))
    assert data == {
        "vault_dir": "~/vault",
        "env_filename": ".env.local",
        "schema_filename": ".envctl.schema.yaml",
    }


def test_write_default_config_file_rejects_existing_file(monkeypatch, tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(writer, "get_default_config_path", lambda: config_path)

    with pytest.raises(ConfigError, match="Config file already exists"):
        writer.write_default_config_file()
