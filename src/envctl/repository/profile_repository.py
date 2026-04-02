"""Profile vault persistence helpers."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.constants import DEFAULT_PROFILE, DEFAULT_VALUES_FILENAME
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import (
    build_profile_env_path,
    build_profiles_dir,
    is_local_profile,
    normalize_profile_name,
)


def resolve_profile_path(
    context: ProjectContext,
    profile: str | None,
) -> tuple[str, Path]:
    """Resolve the normalized profile name and its backing vault file path."""
    resolved_profile = normalize_profile_name(profile)

    if is_local_profile(resolved_profile):
        return resolved_profile, context.vault_values_path

    return resolved_profile, build_profile_env_path(context.vault_project_dir, resolved_profile)


def require_persisted_profile(
    context: ProjectContext,
    profile: str | None,
) -> tuple[str, Path]:
    """Require the selected profile to exist when it is explicit.

    The implicit ``local`` profile stays virtual until first write.
    """
    resolved_profile, path = resolve_profile_path(context, profile)
    if is_local_profile(resolved_profile):
        return resolved_profile, path

    if not path.exists():
        raise ExecutionError(
            f"Profile does not exist: {resolved_profile}. "
            f"Create it with 'envctl profile create {resolved_profile}'."
        )

    return resolved_profile, path


def list_explicit_profiles(context: ProjectContext) -> tuple[str, ...]:
    """Return explicit profiles persisted in the vault."""
    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if not profiles_dir.exists():
        return ()

    profiles: list[str] = []
    for item in sorted(profiles_dir.glob("*.env")):
        if item.is_file():
            profiles.append(item.stem)

    return tuple(profiles)


def list_persisted_profiles(context: ProjectContext) -> tuple[str, ...]:
    """Return every currently persisted profile."""
    profiles: list[str] = []
    if context.vault_values_path.exists():
        profiles.append(DEFAULT_PROFILE)

    profiles.extend(list_explicit_profiles(context))
    return tuple(profiles)


def load_local_profile_values_from_vault_dir(vault_project_dir: Path) -> dict[str, str]:
    """Load the implicit local profile directly from one vault directory."""
    return load_env_file(vault_project_dir / DEFAULT_VALUES_FILENAME)


def load_profile_values(
    context: ProjectContext,
    profile: str | None,
    *,
    require_existing_explicit: bool = False,
) -> tuple[str, Path, dict[str, str]]:
    """Load values for one profile."""
    if require_existing_explicit:
        resolved_profile, path = require_persisted_profile(context, profile)
    else:
        resolved_profile, path = resolve_profile_path(context, profile)

    return resolved_profile, path, load_env_file(path)


def write_profile_values(
    context: ProjectContext,
    profile: str | None,
    values: dict[str, str],
    *,
    require_existing_explicit: bool = False,
) -> tuple[str, Path]:
    """Persist values for one profile."""
    if require_existing_explicit:
        resolved_profile, path = require_persisted_profile(context, profile)
    else:
        resolved_profile, path = resolve_profile_path(context, profile)

    ensure_dir(path.parent)
    write_text_atomic(path, dump_env(values))
    return resolved_profile, path


def remove_key_from_profile(
    context: ProjectContext,
    profile: str | None,
    key: str,
    *,
    require_existing_explicit: bool = False,
) -> tuple[str, Path, bool]:
    """Remove one key from one profile when present."""
    resolved_profile, path, values = load_profile_values(
        context,
        profile,
        require_existing_explicit=require_existing_explicit,
    )
    if key not in values:
        return resolved_profile, path, False

    values.pop(key, None)
    write_profile_values(
        context,
        resolved_profile,
        values,
        require_existing_explicit=require_existing_explicit,
    )
    return resolved_profile, path, True
