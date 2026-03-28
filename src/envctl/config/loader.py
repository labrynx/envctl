"""Load and validate configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from envctl.config.defaults import (
    get_default_config_path,
    get_default_env_filename,
    get_default_schema_filename,
    get_default_vault_dir,
)
from envctl.domain.app_config import AppConfig
from envctl.errors import ConfigError

SUPPORTED_KEYS = {"vault_dir", "env_filename", "schema_filename"}


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON mapping from disk."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON config: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"Unable to read config file: {path}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"Config file must contain a JSON object: {path}")

    return data


def _validate_filename(name: str, label: str) -> str:
    """Validate a configured file name."""
    value = str(name).strip()
    if not value:
        raise ConfigError(f"{label} cannot be empty")
    if "/" in value:
        raise ConfigError(f"{label} must be a file name, not a path")
    return value


def load_config() -> AppConfig:
    """Resolve the application configuration."""
    config_path = get_default_config_path()
    raw: dict[str, Any] = {}

    if config_path.exists():
        raw = _read_json(config_path)
        unknown = set(raw.keys()) - SUPPORTED_KEYS
        if unknown:
            keys = ", ".join(sorted(unknown))
            raise ConfigError(f"Unsupported config key(s): {keys}")

    vault_dir = Path(raw.get("vault_dir", get_default_vault_dir())).expanduser().resolve()
    env_filename = _validate_filename(
        raw.get("env_filename", get_default_env_filename()), "env_filename"
    )
    schema_filename = _validate_filename(
        raw.get("schema_filename", get_default_schema_filename()),
        "schema_filename",
    )

    return AppConfig(
        config_path=config_path,
        vault_dir=vault_dir,
        env_filename=env_filename,
        schema_filename=schema_filename,
    )
