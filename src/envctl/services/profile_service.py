"""Profile services."""

from __future__ import annotations

from envctl.constants import DEFAULT_PROFILE
from envctl.domain.operations import (
    ProfileCopyResult,
    ProfileCreateResult,
    ProfileListResult,
    ProfilePathResult,
    ProfileRemoveResult,
)
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError, ValidationError
from envctl.repository.profile_repository import (
    list_explicit_profiles,
    load_profile_values,
    resolve_profile_path,
    write_profile_values,
)
from envctl.services.context_service import load_project_context
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def _validate_explicit_profile_name(profile: str) -> str:
    """Validate a profile name that must not be the implicit local profile."""
    normalized = normalize_profile_name(profile)

    if normalized == DEFAULT_PROFILE:
        raise ValidationError(
            f"'{DEFAULT_PROFILE}' is the implicit local profile and cannot be managed "
            "with 'envctl profile create/remove'."
        )

    return normalized


def run_profile_list(
    active_profile: str | None = None,
) -> tuple[ProjectContext, ProfileListResult]:
    """List available profiles for the current project."""
    _config, context = load_project_context()
    resolved_active = normalize_profile_name(active_profile)
    logger.debug(
        "Listing profiles",
        extra={
            "active_profile": resolved_active,
            "repo_root": context.repo_root,
        },
    )

    discovered = [DEFAULT_PROFILE, *list_explicit_profiles(context)]
    unique_profiles = sorted(
        set(discovered),
        key=lambda name: (name != DEFAULT_PROFILE, name),
    )

    return context, ProfileListResult(
        active_profile=resolved_active,
        profiles=tuple(unique_profiles),
    )


def run_profile_create(
    profile: str,
) -> tuple[ProjectContext, ProfileCreateResult]:
    """Create one explicit empty profile if missing."""
    _config, context = load_project_context()
    normalized = _validate_explicit_profile_name(profile)
    logger.debug(
        "Creating profile",
        extra={
            "profile": normalized,
            "repo_root": context.repo_root,
        },
    )
    _resolved_profile, path = resolve_profile_path(context, normalized)

    already_exists = path.exists()
    if not already_exists:
        write_profile_values(context, normalized, {})
    logger.debug(
        "Profile create result ready",
        extra={
            "profile": normalized,
            "profile_created": not already_exists,
            "path": path,
        },
    )
    logger.info(
        "Profile create completed",
        extra={
            "profile": normalized,
            "profile_created": not already_exists,
            "path": path,
        },
    )

    return context, ProfileCreateResult(
        profile=normalized,
        path=path,
        created=not already_exists,
    )


def run_profile_copy(
    source_profile: str,
    target_profile: str,
) -> tuple[ProjectContext, ProfileCopyResult]:
    """Copy one profile into another."""
    _config, context = load_project_context()

    source = normalize_profile_name(source_profile)
    target = _validate_explicit_profile_name(target_profile)

    if source == target:
        raise ValidationError("Source and target profiles must be different")
    logger.debug(
        "Copying profile",
        extra={
            "source_profile": source,
            "target_profile": target,
            "repo_root": context.repo_root,
        },
    )

    _resolved_source, source_path, source_values = load_profile_values(context, source)
    if not source_values and not source_path.exists():
        raise ExecutionError(f"Source profile does not exist: {source}")

    _resolved_target, target_path = write_profile_values(context, target, source_values)
    logger.debug(
        "Profile copy result ready",
        extra={
            "source_profile": source,
            "target_profile": target,
            "copied_key_count": len(source_values),
            "target_path": target_path,
        },
    )
    logger.info(
        "Profile copy completed",
        extra={
            "source_profile": source,
            "target_profile": target,
            "copied_key_count": len(source_values),
            "target_path": target_path,
        },
    )

    return context, ProfileCopyResult(
        source_profile=source,
        target_profile=target,
        source_path=source_path,
        target_path=target_path,
        copied_keys=len(source_values),
    )


def run_profile_remove(
    profile: str,
) -> tuple[ProjectContext, ProfileRemoveResult]:
    """Remove one explicit profile file."""
    _config, context = load_project_context()
    normalized = _validate_explicit_profile_name(profile)
    logger.debug(
        "Removing profile",
        extra={
            "profile": normalized,
            "repo_root": context.repo_root,
        },
    )
    _resolved_profile, path = resolve_profile_path(context, normalized)

    removed = False
    if path.exists():
        path.unlink()
        removed = True
    logger.debug(
        "Profile remove result ready",
        extra={
            "profile": normalized,
            "removed": removed,
            "path": path,
        },
    )
    logger.info(
        "Profile remove completed",
        extra={
            "profile": normalized,
            "removed": removed,
            "path": path,
        },
    )

    return context, ProfileRemoveResult(
        profile=normalized,
        path=path,
        removed=removed,
    )


def run_profile_path(
    profile: str | None = None,
    active_profile: str | None = None,
) -> tuple[ProjectContext, ProfilePathResult]:
    """Resolve the filesystem path for one profile."""
    _config, context = load_project_context()
    selected = normalize_profile_name(profile or active_profile)
    _resolved_profile, path = resolve_profile_path(context, selected)

    return context, ProfilePathResult(
        profile=selected,
        path=path,
    )
