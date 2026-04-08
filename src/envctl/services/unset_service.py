"""Unset service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.project import ProjectContext
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def run_unset(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, bool]:
    """Remove one key from the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Running unset",
        extra={
            "key": key,
            "active_profile": resolved_profile,
            "repo_root": context.repo_root,
        },
    )

    _resolved_profile, _profile_path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )
    removed = key in values
    values.pop(key, None)

    _resolved_profile, profile_path = write_profile_values(
        context,
        resolved_profile,
        values,
        require_existing_explicit=True,
    )
    logger.debug(
        "Persisted unset result",
        extra={
            "key": key,
            "active_profile": resolved_profile,
            "profile_path": profile_path,
            "removed": removed,
        },
    )
    logger.info(
        "Unset key in active profile",
        extra={
            "key": key,
            "active_profile": resolved_profile,
            "profile_path": profile_path,
            "removed": removed,
        },
    )
    return context, resolved_profile, profile_path, removed
