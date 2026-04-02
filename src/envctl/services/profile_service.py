"""Profile services."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
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
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import (
    build_profile_env_path,
    build_profiles_dir,
    normalize_profile_name,
)


def _validate_explicit_profile_name(profile: str) -> str:
    """Validate a profile name that must not be the implicit local profile."""
    normalized = normalize_profile_name(profile)

    if normalized == DEFAULT_PROFILE:
        raise ValidationError(
            f"'{DEFAULT_PROFILE}' is the implicit local profile and cannot be managed "
            "with 'envctl profile create/remove'."
        )

    return normalized


def _write_profile_values(path: Path, values: dict[str, str]) -> None:
    """Persist one profile values file."""
    ensure_dir(path.parent)
    write_text_atomic(path, dump_env(values))


def _list_explicit_profiles(vault_project_dir: Path) -> list[str]:
    """Return explicit profiles discovered from the filesystem."""
    profiles_dir = build_profiles_dir(vault_project_dir)
    if not profiles_dir.exists():
        return []

    profiles: list[str] = []
    for item in sorted(profiles_dir.glob("*.env")):
        if item.is_file():
            profiles.append(item.stem)

    return profiles


def run_profile_list(
    active_profile: str | None = None,
) -> tuple[ProjectContext, ProfileListResult]:
    """List available profiles for the current project."""
    _config, context = load_project_context()
    resolved_active = normalize_profile_name(active_profile)

    discovered = [DEFAULT_PROFILE, *_list_explicit_profiles(context.vault_project_dir)]
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
    path = build_profile_env_path(context.vault_project_dir, normalized)

    already_exists = path.exists()
    if not already_exists:
        _write_profile_values(path, {})

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

    source_path = build_profile_env_path(context.vault_project_dir, source)
    target_path = build_profile_env_path(context.vault_project_dir, target)

    source_values = load_env_file(source_path)
    if not source_values and not source_path.exists():
        raise ExecutionError(f"Source profile does not exist: {source}")

    _write_profile_values(target_path, source_values)

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
    path = build_profile_env_path(context.vault_project_dir, normalized)

    removed = False
    if path.exists():
        path.unlink()
        removed = True

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
    path = build_profile_env_path(context.vault_project_dir, selected)

    return context, ProfilePathResult(
        profile=selected,
        path=path,
    )
