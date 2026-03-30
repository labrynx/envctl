"""Unset service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.project import ProjectContext
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import build_profile_env_path, normalize_profile_name


def _write_profile_values(path: Path, values: dict[str, str]) -> None:
    """Persist one profile values file."""
    ensure_dir(path.parent)
    write_text_atomic(path, dump_env(values))


def run_unset(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, bool]:
    """Remove one key from the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    profile_path = build_profile_env_path(context.vault_project_dir, resolved_profile)

    values = load_env_file(profile_path)
    removed = key in values
    values.pop(key, None)

    _write_profile_values(profile_path, values)
    return context, resolved_profile, profile_path, removed
