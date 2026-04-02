from __future__ import annotations

import pytest

from envctl.config.profile_resolution import resolve_active_profile, validate_profile_name
from envctl.constants import DEFAULT_PROFILE
from envctl.errors import ConfigError


def test_resolve_active_profile_prefers_cli_over_env_and_config() -> None:
    result = resolve_active_profile(
        "staging",
        environ={"ENVCTL_PROFILE": "dev"},
        config_default_profile="prod",
    )

    assert result == "staging"


def test_resolve_active_profile_prefers_env_over_config() -> None:
    result = resolve_active_profile(
        environ={"ENVCTL_PROFILE": "dev"},
        config_default_profile="prod",
    )

    assert result == "dev"


def test_resolve_active_profile_prefers_config_over_fallback() -> None:
    result = resolve_active_profile(config_default_profile="prod")

    assert result == "prod"


def test_resolve_active_profile_falls_back_to_local() -> None:
    assert resolve_active_profile(environ={}) == DEFAULT_PROFILE


def test_validate_profile_name_rejects_path_separators() -> None:
    with pytest.raises(ConfigError, match="Profile names must not contain path separators"):
        validate_profile_name("bad/name", "--profile")
