from __future__ import annotations

from pathlib import Path

import pytest

import envctl.config.writer as writer_module
from envctl.errors import ConfigError
from envctl.utils.tilde import to_tilde_path


def test_write_default_config_file_creates_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config" / "config.json"
    vault_dir = tmp_path / "vault"

    monkeypatch.setattr(writer_module, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(writer_module, "get_default_vault_dir", lambda: vault_dir)
    monkeypatch.setattr(writer_module, "get_default_env_filename", lambda: ".env.local")
    monkeypatch.setattr(writer_module, "get_default_schema_filename", lambda: ".envctl.schema.yaml")

    path = writer_module.write_default_config_file()

    assert path == config_path
    assert config_path.exists()

    content = config_path.read_text(encoding="utf-8")
    assert to_tilde_path(vault_dir) in content
    assert '".env.local"' in content
    assert '".envctl.schema.yaml"' in content


def test_write_default_config_file_rejects_existing_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "config" / "config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(writer_module, "get_default_config_path", lambda: config_path)

    with pytest.raises(ConfigError, match="Config file already exists"):
        writer_module.write_default_config_file()
