"""Set service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.project import ProjectContext
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def run_set(
    key: str,
    value: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path]:
    """Store one value in the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Running set",
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
    values[key] = value

    _resolved_profile, profile_path = write_profile_values(
        context,
        resolved_profile,
        values,
        require_existing_explicit=True,
    )
    logger.debug(
        "Persisted set value",
        extra={
            "key": key,
            "active_profile": resolved_profile,
            "profile_path": profile_path,
        },
    )
    logger.info(
        "Stored key in active profile",
        extra={
            "key": key,
            "active_profile": resolved_profile,
            "profile_path": profile_path,
        },
    )
    return context, resolved_profile, profile_path
