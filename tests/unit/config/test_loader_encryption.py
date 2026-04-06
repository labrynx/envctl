# tests/unit/config/test_loader_encryption.py
"""Unit tests for the encryption config block in config/loader.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envctl.config.loader import _parse_encryption_config, load_config
from envctl.errors import ConfigError


def test_parse_none_returns_disabled_non_strict() -> None:
    assert _parse_encryption_config(None) == (False, False)


def test_parse_empty_dict_returns_disabled_non_strict() -> None:
    assert _parse_encryption_config({}) == (False, False)


def test_parse_enabled_true_returns_enabled_non_strict() -> None:
    assert _parse_encryption_config({"enabled": True}) == (True, False)


def test_parse_enabled_false_returns_disabled_non_strict() -> None:
    assert _parse_encryption_config({"enabled": False}) == (False, False)


def test_parse_enabled_and_strict_true_returns_both_true() -> None:
    assert _parse_encryption_config({"enabled": True, "strict": True}) == (True, True)


def test_parse_non_dict_raises() -> None:
    with pytest.raises(ConfigError, match=r"encryption must be a JSON object"):
        _parse_encryption_config("yes")


def test_parse_non_bool_enabled_raises() -> None:
    with pytest.raises(ConfigError, match=r"encryption.enabled must be a boolean"):
        _parse_encryption_config({"enabled": "true"})


def test_parse_non_bool_strict_raises() -> None:
    with pytest.raises(ConfigError, match=r"encryption.strict must be a boolean"):
        _parse_encryption_config({"enabled": True, "strict": "true"})


def test_parse_unknown_key_raises() -> None:
    with pytest.raises(ConfigError, match=r"Unsupported encryption config key"):
        _parse_encryption_config({"enabled": True, "algorithm": "AES"})


def test_load_config_encryption_disabled_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    config = load_config()

    assert config.encryption_enabled is False
    assert config.encryption_strict is False


def test_load_config_encryption_enabled_from_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir = tmp_path / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text(
        json.dumps({"encryption": {"enabled": True}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    config = load_config()

    assert config.encryption_enabled is True
    assert config.encryption_strict is False


def test_load_config_encryption_strict_from_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir = tmp_path / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text(
        json.dumps({"encryption": {"enabled": True, "strict": True}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    config = load_config()

    assert config.encryption_enabled is True
    assert config.encryption_strict is True


def test_load_config_encryption_false_from_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir = tmp_path / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text(
        json.dumps({"encryption": {"enabled": False}}),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    config = load_config()

    assert config.encryption_enabled is False
    assert config.encryption_strict is False


def test_load_config_encryption_invalid_block_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_dir = tmp_path / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    (config_dir / "config.json").write_text(
        json.dumps({"encryption": "yes"}),
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))

    with pytest.raises(ConfigError, match=r"encryption must be a JSON object"):
        load_config()
