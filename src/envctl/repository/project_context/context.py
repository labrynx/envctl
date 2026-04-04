"""Project context builders."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.git import get_local_git_config, get_repo_remote, resolve_repo_root
from envctl.constants import DEFAULT_STATE_FILENAME, GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError
from envctl.repository.contract_repository import load_contract_optional
from envctl.repository.project_context.builders import build_context
from envctl.repository.project_context.discovery import find_vault_dir_by_project_id
from envctl.repository.project_context.identity import build_provisional_project_id
from envctl.repository.project_context.recovery import recover_context
from envctl.repository.state_repository import read_state
from envctl.services.error_diagnostics import ProjectBindingDiagnostics
from envctl.utils.project_ids import is_valid_project_id
from envctl.utils.project_names import resolve_project_name


def _resolve_project_key(repo_contract_path: Path, project_slug: str) -> str:
    """Resolve the logical project key from contract metadata or fallback slug."""
    contract = load_contract_optional(repo_contract_path)
    if contract is None or contract.meta is None:
        return project_slug
    return contract.meta.project_key or project_slug


def build_context_for_project_id(
    config: AppConfig,
    *,
    repo_root: Path,
    project_id: str,
    project_name: str | None = None,
    binding_source: str = "local",
) -> ProjectContext:
    """Build a context for one explicit project id."""
    repo_remote = get_repo_remote(repo_root)
    project_slug = resolve_project_name(repo_root, project_name)
    repo_contract_path = repo_root / config.schema_filename
    project_key = _resolve_project_key(repo_contract_path, project_slug)

    vault_dir = find_vault_dir_by_project_id(config.projects_dir, project_id)
    if vault_dir is not None:
        state = read_state(vault_dir / DEFAULT_STATE_FILENAME)
        if state is not None:
            project_slug = str(state.get("project_slug") or project_slug)
            project_key = str(state.get("project_key") or project_key)

    return build_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=project_slug,
        project_key=project_key,
        project_id=project_id,
        binding_source=binding_source,
        vault_project_dir=vault_dir,
    )


def build_project_context(
    config: AppConfig,
    project_name: str | None = None,
) -> ProjectContext:
    """Build the project context for the current repository."""
    repo_root = resolve_repo_root()
    project_slug = resolve_project_name(repo_root, project_name)
    repo_contract_path = repo_root / config.schema_filename
    project_key = _resolve_project_key(repo_contract_path, project_slug)
    repo_remote = get_repo_remote(repo_root)

    bound_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)
    if bound_project_id:
        if not is_valid_project_id(bound_project_id):
            raise ProjectDetectionError(
                f"Invalid project binding in local git config: {bound_project_id!r}",
                diagnostics=ProjectBindingDiagnostics(
                    category="invalid_bound_project_id",
                    repo_root=repo_root,
                    project_id=bound_project_id,
                    suggested_actions=("envctl project rebind",),
                ),
            )

        vault_dir = find_vault_dir_by_project_id(config.projects_dir, bound_project_id)
        if vault_dir is None:
            raise ProjectDetectionError(
                f"Bound project id '{bound_project_id}' was found in local git config, "
                "but no matching vault exists. Run 'envctl repair --recreate-bound-vault' "
                "or rebind the repository.",
                diagnostics=ProjectBindingDiagnostics(
                    category="bound_project_missing_vault",
                    repo_root=repo_root,
                    project_id=bound_project_id,
                    suggested_actions=(
                        "envctl repair --recreate-bound-vault",
                        "envctl project rebind",
                    ),
                ),
            )

        state = read_state(vault_dir / DEFAULT_STATE_FILENAME)
        resolved_slug = project_slug
        resolved_key = project_key
        if state is not None:
            resolved_slug = str(state.get("project_slug") or project_slug)
            resolved_key = str(state.get("project_key") or project_key)

        return build_context(
            config=config,
            repo_root=repo_root,
            repo_remote=repo_remote,
            repo_contract_path=repo_contract_path,
            project_slug=resolved_slug,
            project_key=resolved_key,
            project_id=bound_project_id,
            binding_source="local",
            vault_project_dir=vault_dir,
        )

    recovered = recover_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=project_slug,
        project_key=project_key,
    )
    if recovered is not None:
        return recovered

    provisional_project_id = build_provisional_project_id(repo_root, repo_remote)
    return build_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=project_slug,
        project_key=project_key,
        project_id=provisional_project_id,
        binding_source="derived",
    )
