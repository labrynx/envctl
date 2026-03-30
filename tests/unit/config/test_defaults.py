from __future__ import annotations

from pathlib import Path

import pytest

import envctl.config.defaults as defaults
from envctl.constants import (
    DEFAULT_CONFIG_DIRNAME,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_ENV_FILENAME,
    DEFAULT_SCHEMA_FILENAME,
)


def test_get_home_dir_returns_path_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setattr(defaults.Path, "home", lambda: home)

    assert defaults.get_home_dir() == home


def test_get_xdg_config_home_uses_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    xdg_home = tmp_path / "xdg-config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_home))

    result = defaults.get_xdg_config_home()

    assert result == xdg_home.resolve()


def test_get_xdg_config_home_falls_back_to_home_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(defaults.Path, "home", lambda: home)

    result = defaults.get_xdg_config_home()

    assert result == (home / ".config").resolve()


def test_default_path_and_filenames_are_resolved_correctly(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setattr(defaults.Path, "home", lambda: home)

    assert defaults.get_default_config_path() == (
        home / ".config" / DEFAULT_CONFIG_DIRNAME / DEFAULT_CONFIG_FILENAME
    )
    assert defaults.get_default_vault_dir() == (home / ".envctl" / "vault").resolve()
    assert defaults.get_default_env_filename() == DEFAULT_ENV_FILENAME
    assert defaults.get_default_schema_filename() == DEFAULT_SCHEMA_FILENAME
