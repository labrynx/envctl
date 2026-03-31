"""Project path helpers."""

from __future__ import annotations

from pathlib import Path

from envctl.constants import (
    DEFAULT_PROFILE,
    DEFAULT_PROFILES_DIRNAME,
    DEFAULT_VALUES_FILENAME,
)


def build_vault_project_dir(project_slug: str, project_id: str, projects_dir: Path) -> Path:
    """Return the vault directory for a project."""
    return projects_dir / f"{project_slug}--{project_id}"


def normalize_profile_name(profile: str | None) -> str:
    """Normalize one profile name, falling back to the local profile."""
    normalized = (profile or DEFAULT_PROFILE).strip().lower()
    return normalized or DEFAULT_PROFILE


def is_local_profile(profile: str | None) -> bool:
    """Return whether the given profile is the implicit local profile."""
    return normalize_profile_name(profile) == DEFAULT_PROFILE


def build_profiles_dir(vault_project_dir: Path) -> Path:
    """Return the directory that stores explicit profile files."""
    return vault_project_dir / DEFAULT_PROFILES_DIRNAME


def build_profile_env_path(vault_project_dir: Path, profile: str | None) -> Path:
    """Return the env file path for the selected profile.

    The implicit ``local`` profile keeps using the legacy ``values.env`` path
    so existing projects continue to work without migration.
    """
    normalized = normalize_profile_name(profile)

    if normalized == DEFAULT_PROFILE:
        return vault_project_dir / DEFAULT_VALUES_FILENAME

    return build_profiles_dir(vault_project_dir) / f"{normalized}.env"

def build_repo_sync_env_path(repo_root: Path, profile: str | None) -> Path:
    """Return the repository sync target for the selected profile.

    The implicit local profile is materialized as ``.env.local``.
    Explicit profiles are materialized as ``.env.<profile>``.
    """
    normalized = normalize_profile_name(profile)
    return repo_root / f".env.{normalized}"
