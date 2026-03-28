"""Default path resolution for envctl."""

from __future__ import annotations

import os
from pathlib import Path

from envctl.constants import (
    DEFAULT_CONFIG_DIRNAME,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_ENV_FILENAME,
    DEFAULT_METADATA_FILENAME,
)


def get_home_dir() -> Path:
    """Return the current user's home directory."""
    return Path.home()


def get_xdg_config_home() -> Path:
    """Return the XDG config home directory."""
    raw = os.environ.get("XDG_CONFIG_HOME")
    if raw:
        return Path(raw).expanduser().resolve()
    return (get_home_dir() / ".config").resolve()


def get_default_config_path() -> Path:
    """Return the default config path."""
    return get_xdg_config_home() / DEFAULT_CONFIG_DIRNAME / DEFAULT_CONFIG_FILENAME


def get_default_vault_dir() -> Path:
    """Return the default vault root directory.

    envctl keeps its managed vault in a user-visible home directory location
    instead of under XDG data to improve discoverability.
    """
    return (get_home_dir() / ".envctl" / "vault").resolve()


def get_default_env_filename() -> str:
    """Return the default environment filename."""
    return DEFAULT_ENV_FILENAME


def get_default_metadata_filename() -> str:
    """Return the default repository metadata filename."""
    return DEFAULT_METADATA_FILENAME
