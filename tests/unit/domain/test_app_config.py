# tests/unit/domain/test_app_config.py
"""Unit tests for AppConfig."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.app_config import AppConfig
from envctl.domain.runtime import RuntimeMode


def _make_config(
    *,
    vault_dir: str = "/home/user/.envctl/vault",
    encryption_enabled: bool = False,
    encryption_strict: bool = False,
) -> AppConfig:
    return AppConfig(
        config_path=Path("/home/user/.config/envctl/config.json"),
        vault_dir=Path(vault_dir),
        env_filename=".env.local",
        schema_filename=".envctl.schema.yaml",
        runtime_mode=RuntimeMode.LOCAL,
        default_profile="local",
        encryption_enabled=encryption_enabled,
        encryption_strict=encryption_strict,
    )


def test_encryption_enabled_defaults_to_false() -> None:
    config = _make_config()
    assert config.encryption_enabled is False


def test_encryption_enabled_can_be_true() -> None:
    config = _make_config(encryption_enabled=True)
    assert config.encryption_enabled is True


def test_encryption_strict_defaults_to_false() -> None:
    config = _make_config()
    assert config.encryption_strict is False


def test_encryption_strict_can_be_true() -> None:
    config = _make_config(encryption_enabled=True, encryption_strict=True)
    assert config.encryption_strict is True


def test_app_config_has_no_global_vault_key_path() -> None:
    config = _make_config(vault_dir="/home/user/.envctl/vault")
    assert not hasattr(config, "vault_key_path")


def test_projects_dir_unchanged() -> None:
    config = _make_config(vault_dir="/home/user/.envctl/vault")
    assert config.projects_dir == Path("/home/user/.envctl/vault/projects")
