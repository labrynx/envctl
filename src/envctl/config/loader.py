"""Config file loader helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from envctl.config.defaults import (
    get_default_config_path,
    get_default_contract_filename,
    get_default_env_filename,
    get_default_vault_dir,
)
from envctl.config.profile_resolution import resolve_active_profile, validate_profile_name
from envctl.constants import (
    DEFAULT_PROFILE,
    ENVCTL_RUNTIME_MODE_ENVVAR,
)
from envctl.domain.app_config import AppConfig
from envctl.domain.error_diagnostics import ConfigDiagnostics
from envctl.domain.runtime import RuntimeMode
from envctl.errors import ConfigError
from envctl.utils.logging import get_logger

logger = get_logger(__name__)

SUPPORTED_KEYS = {
    "vault_dir",
    "env_filename",
    "contract_filename",
    "runtime_mode",
    "default_profile",
    "encryption",
}


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON mapping from disk."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"Invalid JSON config: {path}",
            diagnostics=ConfigDiagnostics(
                category="invalid_json",
                path=path,
                suggested_actions=("fix config.json",),
            ),
        ) from exc
    except OSError as exc:
        raise ConfigError(
            f"Unable to read config file: {path}",
            diagnostics=ConfigDiagnostics(
                category="unreadable_config",
                path=path,
                suggested_actions=("check config file permissions",),
            ),
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError(
            f"Config file must contain a JSON object: {path}",
            diagnostics=ConfigDiagnostics(
                category="invalid_config_shape",
                path=path,
                field="root",
                suggested_actions=("fix config.json",),
            ),
        )

    return data


def _validate_filename(
    name: str,
    label: str,
    *,
    path: Path | None = None,
    source_label: str | None = None,
) -> str:
    """Validate a configured file name."""
    value = str(name).strip()
    if not value:
        raise ConfigError(
            f"{label} cannot be empty",
            diagnostics=ConfigDiagnostics(
                category="invalid_filename",
                path=path,
                key=label,
                source_label=source_label,
                value=str(name),
                suggested_actions=("fix config.json",),
            ),
        )
    if "/" in value:
        raise ConfigError(
            f"{label} must be a file name, not a path",
            diagnostics=ConfigDiagnostics(
                category="invalid_filename",
                path=path,
                key=label,
                source_label=source_label,
                value=value,
                suggested_actions=("fix config.json",),
            ),
        )
    return value


def _validate_runtime_mode(
    value: object,
    source_label: str,
    *,
    path: Path | None = None,
) -> RuntimeMode:
    """Validate and normalize one runtime mode value."""
    normalized = str(value).strip().lower()
    try:
        return RuntimeMode(normalized)
    except ValueError as exc:
        allowed = ", ".join(mode.value for mode in RuntimeMode)
        raise ConfigError(
            f"Invalid runtime mode in {source_label}: {value!r}. Expected one of: {allowed}",
            diagnostics=ConfigDiagnostics(
                category="invalid_runtime_mode",
                path=path,
                source_label=source_label,
                value=repr(value),
                suggested_actions=("set runtime_mode to local or ci",),
            ),
        ) from exc


def _parse_encryption_config(
    raw_encryption: object,
    *,
    path: Path | None = None,
) -> tuple[bool, bool]:
    """Parse and validate the ``encryption`` configuration block.

    Returns ``(enabled, strict)``.
    Missing or ``null`` block defaults to ``(False, False)``.
    """
    if raw_encryption is None:
        return False, False

    if not isinstance(raw_encryption, dict):
        raise ConfigError(
            "encryption must be a JSON object with 'enabled' and optional 'strict' keys",
            diagnostics=ConfigDiagnostics(
                category="invalid_config_shape",
                path=path,
                field="encryption",
                suggested_actions=('use {"encryption": {"enabled": true, "strict": false}}',),
            ),
        )

    unknown = set(raw_encryption.keys()) - {"enabled", "strict"}
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ConfigError(
            f"Unsupported encryption config key(s): {keys}",
            diagnostics=ConfigDiagnostics(
                category="unsupported_keys",
                path=path,
                key=keys,
                suggested_actions=("remove unsupported encryption config keys",),
            ),
        )

    enabled = raw_encryption.get("enabled", False)
    strict = raw_encryption.get("strict", False)

    if not isinstance(enabled, bool):
        raise ConfigError(
            f"encryption.enabled must be a boolean, got {enabled!r}",
            diagnostics=ConfigDiagnostics(
                category="invalid_config_shape",
                path=path,
                field="encryption.enabled",
                value=repr(enabled),
                suggested_actions=("set encryption.enabled to true or false",),
            ),
        )

    if not isinstance(strict, bool):
        raise ConfigError(
            f"encryption.strict must be a boolean, got {strict!r}",
            diagnostics=ConfigDiagnostics(
                category="invalid_config_shape",
                path=path,
                field="encryption.strict",
                value=repr(strict),
                suggested_actions=("set encryption.strict to true or false",),
            ),
        )

    if strict and not enabled:
        raise ConfigError(
            "encryption.strict cannot be true when encryption.enabled is false",
            diagnostics=ConfigDiagnostics(
                category="invalid_config_shape",
                path=path,
                field="encryption.strict",
                suggested_actions=("enable encryption or disable strict mode",),
            ),
        )

    return enabled, strict


def load_config() -> AppConfig:
    """Resolve the application configuration."""
    config_path = get_default_config_path()
    raw: dict[str, Any] = {}
    logger.debug("Loading application config", extra={"config_path": config_path})

    if config_path.exists():
        raw = _read_json(config_path)
        logger.debug(
            "Loaded config file", extra={"config_path": config_path, "configured_keys": sorted(raw)}
        )
        unknown = set(raw.keys()) - SUPPORTED_KEYS
        if unknown:
            keys = ", ".join(sorted(unknown))
            raise ConfigError(
                f"Unsupported config key(s): {keys}",
                diagnostics=ConfigDiagnostics(
                    category="unsupported_keys",
                    path=config_path,
                    key=keys,
                    suggested_actions=("remove unsupported config keys",),
                ),
            )

    vault_dir = Path(raw.get("vault_dir", get_default_vault_dir())).expanduser().resolve()

    env_filename = _validate_filename(
        raw.get("env_filename", get_default_env_filename()),
        "env_filename",
        path=config_path if config_path.exists() else None,
        source_label="config file",
    )
    contract_filename = _validate_filename(
        raw.get("contract_filename", get_default_contract_filename()),
        "contract_filename",
        path=config_path if config_path.exists() else None,
        source_label="config file",
    )

    config_runtime_mode = _validate_runtime_mode(
        raw.get("runtime_mode", RuntimeMode.LOCAL.value),
        "config file",
        path=config_path if config_path.exists() else None,
    )

    env_runtime_mode_raw = os.environ.get(ENVCTL_RUNTIME_MODE_ENVVAR)
    runtime_mode = (
        _validate_runtime_mode(env_runtime_mode_raw, ENVCTL_RUNTIME_MODE_ENVVAR)
        if env_runtime_mode_raw is not None
        else config_runtime_mode
    )

    try:
        config_default_profile = validate_profile_name(
            raw.get("default_profile", DEFAULT_PROFILE),
            "config file",
        )
    except ConfigError as exc:
        if exc.diagnostics is None:
            raise ConfigError(
                str(exc),
                diagnostics=ConfigDiagnostics(
                    category="invalid_default_profile",
                    path=config_path if config_path.exists() else None,
                    key="default_profile",
                    source_label="config file",
                    value=repr(raw.get("default_profile", DEFAULT_PROFILE)),
                    suggested_actions=("fix config.json",),
                ),
            ) from exc
        raise

    encryption_enabled, encryption_strict = _parse_encryption_config(
        raw.get("encryption"),
        path=config_path if config_path.exists() else None,
    )

    logger.debug(
        "Resolved application config",
        extra={
            "config_path": config_path,
            "vault_dir": vault_dir,
            "runtime_mode": runtime_mode.value,
            "default_profile": config_default_profile,
            "encryption_enabled": encryption_enabled,
            "encryption_strict": encryption_strict,
        },
    )

    return AppConfig(
        config_path=config_path,
        vault_dir=vault_dir,
        env_filename=env_filename,
        contract_filename=contract_filename,
        runtime_mode=runtime_mode,
        default_profile=config_default_profile,
        encryption_enabled=encryption_enabled,
        encryption_strict=encryption_strict,
    )


def resolve_default_profile() -> str:
    """Resolve the active profile from environment and config defaults.

    Precedence:
    1. ENVCTL_PROFILE
    2. config.default_profile
    3. DEFAULT_PROFILE
    """
    config = load_config()
    return resolve_active_profile(config_default_profile=config.default_profile)
