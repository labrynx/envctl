from __future__ import annotations

from pathlib import Path

import pytest

import envctl.config.writer as writer_module
from envctl.errors import ConfigError
from envctl.utils.tilde import to_tilde_path
from tests.support.assertions import require_config_diagnostics


def test_write_default_config_file_creates_expected_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"

    monkeypatch.setattr(writer_module, "get_default_config_path", lambda: config_path)
    monkeypatch.setattr(writer_module, "get_default_vault_dir", lambda: tmp_path / "vault")
    monkeypatch.setattr(writer_module, "get_default_env_filename", lambda: ".env.local")
    monkeypatch.setattr(
        writer_module,
        "get_default_schema_filename",
        lambda: ".envctl.schema.yaml",
    )

    written: dict[str, object] = {}

    monkeypatch.setattr(writer_module, "ensure_dir", lambda path: None)

    def fake_write_json_atomic(path: Path, payload: dict[str, object]) -> None:
        written["path"] = path
        written["payload"] = payload

    monkeypatch.setattr(writer_module, "write_json_atomic", fake_write_json_atomic)

    result = writer_module.write_default_config_file()

    assert result == config_path
    assert written["path"] == config_path
    assert written["payload"] == {
        "vault_dir": to_tilde_path(tmp_path / "vault"),
        "env_filename": ".env.local",
        "schema_filename": ".envctl.schema.yaml",
        "runtime_mode": "local",
        "default_profile": "local",
    }


def test_write_default_config_file_rejects_existing_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(writer_module, "get_default_config_path", lambda: config_path)

    with pytest.raises(ConfigError, match=r"Config file already exists") as exc_info:
        writer_module.write_default_config_file()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "config_file_exists"
    assert diagnostics.path == config_path
