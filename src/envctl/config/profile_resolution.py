"""Active profile resolution helpers."""

from __future__ import annotations

import os
from collections.abc import Mapping

from envctl.constants import DEFAULT_PROFILE, ENVCTL_PROFILE_ENVVAR
from envctl.errors import ConfigError
from envctl.utils.logging import get_logger

logger = get_logger(__name__)


def validate_profile_name(value: object, source_label: str) -> str:
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


def resolve_active_profile(
    cli_profile: str | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    config_default_profile: str | None = None,
) -> str:
    """Resolve the active profile from CLI, environment, config, and fallback.

    Precedence:
    1. CLI ``--profile``
    2. ``ENVCTL_PROFILE``
    3. config ``default_profile``
    4. ``local``
    """
    if cli_profile is not None:
        logger.debug("Resolved active profile from CLI option", extra={"source": "--profile"})
        return validate_profile_name(cli_profile, "--profile")

    resolved_environ = os.environ if environ is None else environ
    env_profile_raw = resolved_environ.get(ENVCTL_PROFILE_ENVVAR)
    if env_profile_raw is not None:
        logger.debug(
            "Resolved active profile from environment",
            extra={"source": ENVCTL_PROFILE_ENVVAR},
        )
        return validate_profile_name(env_profile_raw, ENVCTL_PROFILE_ENVVAR)

    if config_default_profile is not None:
        logger.debug(
            "Resolved active profile from config default",
            extra={"source": "config.default_profile"},
        )
        return validate_profile_name(config_default_profile, "config.default_profile")

    logger.debug("Resolved active profile from fallback", extra={"source": DEFAULT_PROFILE})
    return DEFAULT_PROFILE
