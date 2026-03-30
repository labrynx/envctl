"""Config file loader helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from envctl.config.defaults import (
    get_default_config_path,
    get_default_env_filename,
    get_default_schema_filename,
    get_default_vault_dir,
)
from envctl.constants import (
    DEFAULT_PROFILE,
    ENVCTL_PROFILE_ENVVAR,
    ENVCTL_RUNTIME_MODE_ENVVAR,
)
from envctl.domain.app_config import AppConfig
from envctl.domain.runtime import RuntimeMode
from envctl.errors import ConfigError

SUPPORTED_KEYS = {
    "vault_dir",
    "env_filename",
    "schema_filename",
    "runtime_mode",
    "default_profile",
}


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


def _validate_runtime_mode(value: object, source_label: str) -> RuntimeMode:
    """Validate and normalize one runtime mode value."""
    normalized = str(value).strip().lower()
    try:
        return RuntimeMode(normalized)
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in RuntimeMode)
        raise ConfigError(
            f"Invalid runtime mode in {source_label}: {value!r}. Expected one of: {allowed}"
        ) from exc


def _validate_profile(value: object, source_label: str) -> str:
    """Validate and normalize one profile name."""
    normalized = str(value).strip().lower()
    if not normalized:
        raise ConfigError(
            f"Invalid profile in {source_label}: {value!r}. Expected a non-empty string."
        )

    if "/" in normalized or "\\" in normalized:
        raise ConfigError(
            f"Invalid profile in {source_label}: {value!r}. "
            "Profile names must not contain path separators."
        )

    return normalized


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
        raw.get("env_filename", get_default_env_filename()),
        "env_filename",
    )
    schema_filename = _validate_filename(
        raw.get("schema_filename", get_default_schema_filename()),
        "schema_filename",
    )

    config_runtime_mode = _validate_runtime_mode(
        raw.get("runtime_mode", RuntimeMode.LOCAL.value),
        "config file",
    )

    env_runtime_mode_raw = os.environ.get(ENVCTL_RUNTIME_MODE_ENVVAR)
    runtime_mode = (
        _validate_runtime_mode(env_runtime_mode_raw, ENVCTL_RUNTIME_MODE_ENVVAR)
        if env_runtime_mode_raw is not None
        else config_runtime_mode
    )

    config_default_profile = _validate_profile(
        raw.get("default_profile", DEFAULT_PROFILE),
        "config file",
    )

    return AppConfig(
        config_path=config_path,
        vault_dir=vault_dir,
        env_filename=env_filename,
        schema_filename=schema_filename,
        runtime_mode=runtime_mode,
        default_profile=config_default_profile,
    )


def resolve_default_profile() -> str:
    """Resolve the active profile from environment and config defaults.

    Precedence:
    1. ENVCTL_PROFILE
    2. config.default_profile
    3. DEFAULT_PROFILE
    """
    env_profile_raw = os.environ.get(ENVCTL_PROFILE_ENVVAR)
    if env_profile_raw is not None:
        return _validate_profile(env_profile_raw, ENVCTL_PROFILE_ENVVAR)

    config = load_config()
    return _validate_profile(config.default_profile, "config file")
