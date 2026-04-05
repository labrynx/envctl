"""Rebind service."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from envctl.adapters.git import get_local_git_config, resolve_repo_root
from envctl.config.loader import load_config
from envctl.constants import DEFAULT_KEY_FILENAME, GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.app_config import AppConfig
from envctl.domain.operations import RebindResult
from envctl.domain.project import ProjectContext
from envctl.repository.profile_repository import (
    load_local_profile_values_from_vault_dir,
    write_profile_values,
)
from envctl.repository.project_context import (
    build_context_for_project_id,
    find_vault_dir_by_project_id,
    persist_project_binding,
)
from envctl.services.context_service import load_configured_vault_crypto
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.project_ids import new_project_id
from envctl.vault_crypto import VaultCrypto


def _load_previous_values(
    projects_dir: Path,
    previous_project_id: str | None,
    *,
    crypto: VaultCrypto | None = None,
) -> dict[str, str]:
    """Load previous vault values when available."""
    if previous_project_id is None:
        return {}

    previous_vault_dir = find_vault_dir_by_project_id(projects_dir, previous_project_id)
    if previous_vault_dir is None:
        return {}

    return load_local_profile_values_from_vault_dir(previous_vault_dir, crypto=crypto)


def _load_previous_project_crypto(
    *,
    config: AppConfig,
    previous_project_id: str | None,
) -> VaultCrypto | None:
    """Load crypto for the previous project when encryption is enabled."""
    if not config.encryption_enabled or previous_project_id is None:
        return None

    previous_vault_dir = find_vault_dir_by_project_id(config.projects_dir, previous_project_id)
    if previous_vault_dir is None:
        return None

    key_path = previous_vault_dir / DEFAULT_KEY_FILENAME
    return VaultCrypto.load_or_create(
        key_path,
        protected_paths=previous_vault_dir.rglob("*.env"),
    )


def run_rebind(*, copy_values: bool = True) -> tuple[ProjectContext, RebindResult]:
    """Generate a new canonical project id and bind the current checkout to it."""
    config = load_config()
    repo_root = resolve_repo_root()
    previous_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)

    previous_crypto = _load_previous_project_crypto(
        config=config,
        previous_project_id=previous_project_id,
    )
    previous_values = _load_previous_values(
        config.projects_dir,
        previous_project_id,
        crypto=previous_crypto,
    )

    new_project_id_value = new_project_id()
    context = build_context_for_project_id(
        config,
        repo_root=repo_root,
        project_id=new_project_id_value,
        binding_source="local",
    )
    context = replace(context, vault_crypto=load_configured_vault_crypto(config, context))
    context = persist_project_binding(config, context)

    ensure_dir(context.vault_project_dir)
    ensure_file(context.vault_values_path, "")

    copied = False
    if copy_values and previous_values:
        write_profile_values(context, "local", previous_values)
        copied = True

    return context, RebindResult(
        previous_project_id=previous_project_id,
        new_project_id=new_project_id_value,
        copied_values=copied,
    )
