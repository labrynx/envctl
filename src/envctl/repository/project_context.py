"""Project context builders."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

from envctl.adapters.git import (
    get_local_git_config,
    get_repo_remote,
    resolve_repo_root,
    set_local_git_config,
)
from envctl.constants import (
    DEFAULT_STATE_FILENAME,
    DEFAULT_VALUES_FILENAME,
    GIT_CONFIG_PROJECT_ID_KEY,
    PROVISIONAL_PROJECT_ID_LENGTH,
)
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError, StateError
from envctl.repository.contract_repository import load_contract_optional
from envctl.repository.state_repository import read_state, upsert_state
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_ids import is_valid_project_id
from envctl.utils.project_names import resolve_project_name
from envctl.utils.project_paths import build_vault_project_dir


def _build_provisional_project_id(repo_root: Path, repo_remote: str | None) -> str:
    """Build a provisional identifier before a binding is persisted."""
    basis = repo_remote or str(repo_root.resolve())
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return f"tmp_{digest[:PROVISIONAL_PROJECT_ID_LENGTH]}"


def find_vault_dir_by_project_id(projects_dir: Path, project_id: str) -> Path | None:
    """Return the vault directory for one persisted project id."""
    if not projects_dir.exists():
        return None

    matches = [path for path in projects_dir.iterdir() if path.is_dir() and path.name.endswith(f"--{project_id}")]
    if not matches:
        return None
    if len(matches) > 1:
        options = ", ".join(sorted(path.name for path in matches))
        raise ProjectDetectionError(
            f"Multiple vault directories found for project id '{project_id}': {options}"
        )
    return matches[0]


def _iter_state_records(projects_dir: Path) -> list[tuple[Path, dict[str, object]]]:
    """Read every valid state file under the projects directory."""
    records: list[tuple[Path, dict[str, object]]] = []

    if not projects_dir.exists():
        return records

    for child in projects_dir.iterdir():
        if not child.is_dir():
            continue

        state_path = child / DEFAULT_STATE_FILENAME
        if not state_path.exists():
            continue

        state = read_state(state_path)
        if state is None:
            continue

        records.append((child, state))

    return records


def _resolve_project_key(repo_root: Path, repo_contract_path: Path, project_slug: str) -> str:
    """Resolve the logical project key from contract metadata or fallback slug."""
    contract = load_contract_optional(repo_contract_path)
    if contract is None or contract.meta is None:
        return project_slug
    return contract.meta.project_key or project_slug


def _build_context(
    *,
    config: AppConfig,
    repo_root: Path,
    repo_remote: str | None,
    repo_contract_path: Path,
    project_slug: str,
    project_key: str,
    project_id: str,
    binding_source: str,
    vault_project_dir: Path | None = None,
) -> ProjectContext:
    """Build a complete project context."""
    resolved_vault_project_dir = (
        vault_project_dir
        if vault_project_dir is not None
        else build_vault_project_dir(project_slug, project_id, config.projects_dir)
    )

    return ProjectContext(
        project_slug=project_slug,
        project_key=project_key,
        project_id=project_id,
        repo_root=repo_root,
        repo_remote=repo_remote,
        binding_source=binding_source,  # type: ignore[arg-type]
        repo_env_path=repo_root / config.env_filename,
        repo_contract_path=repo_contract_path,
        vault_project_dir=resolved_vault_project_dir,
        vault_values_path=resolved_vault_project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=resolved_vault_project_dir / DEFAULT_STATE_FILENAME,
    )


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
    project_key = _resolve_project_key(repo_root, repo_contract_path, project_slug)

    vault_dir = find_vault_dir_by_project_id(config.projects_dir, project_id)
    if vault_dir is not None:
        state = read_state(vault_dir / DEFAULT_STATE_FILENAME)
        if state is not None:
            project_slug = str(state.get("project_slug") or project_slug)
            project_key = str(state.get("project_key") or project_key)

    return _build_context(
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


def _recover_context(
    *,
    config: AppConfig,
    repo_root: Path,
    repo_remote: str | None,
    repo_contract_path: Path,
    project_slug: str,
    project_key: str,
) -> ProjectContext | None:
    """Attempt to recover a context from persisted vault state."""
    candidates: list[tuple[Path, dict[str, object]]] = []

    for vault_dir, state in _iter_state_records(config.projects_dir):
        state_remote = state.get("git_remote")
        state_project_key = state.get("project_key")
        state_known_paths = state.get("known_paths", [])

        if repo_remote and isinstance(state_remote, str) and state_remote == repo_remote:
            candidates.append((vault_dir, state))
            continue

        if not repo_remote:
            if isinstance(state_project_key, str) and state_project_key == project_key:
                candidates.append((vault_dir, state))
                continue

            if (
                isinstance(state_known_paths, list)
                and str(repo_root.resolve()) in state_known_paths
            ):
                candidates.append((vault_dir, state))
                continue

    if not candidates:
        return None

    unique_by_id: dict[str, tuple[Path, dict[str, object]]] = {}
    for vault_dir, state in candidates:
        project_id = str(state["project_id"])
        unique_by_id[project_id] = (vault_dir, state)

    if len(unique_by_id) > 1:
        options = ", ".join(sorted(unique_by_id))
        raise ProjectDetectionError(
            f"Ambiguous vault identity for this repository. Matching project ids: {options}. "
            f"Bind one explicitly by writing '{GIT_CONFIG_PROJECT_ID_KEY}'."
        )

    vault_dir, state = next(iter(unique_by_id.values()))
    project_id = str(state["project_id"])
    resolved_slug = str(state.get("project_slug") or project_slug)
    resolved_key = str(state.get("project_key") or project_key)

    return _build_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=resolved_slug,
        project_key=resolved_key,
        project_id=project_id,
        binding_source="recovered",
        vault_project_dir=vault_dir,
    )


def build_project_context(config: AppConfig, project_name: str | None = None) -> ProjectContext:
    """Build the project context for the current repository."""
    repo_root = resolve_repo_root()
    project_slug = resolve_project_name(repo_root, project_name)
    repo_contract_path = repo_root / config.schema_filename
    project_key = _resolve_project_key(repo_root, repo_contract_path, project_slug)
    repo_remote = get_repo_remote(repo_root)

    bound_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)
    if bound_project_id:
        if not is_valid_project_id(bound_project_id):
            raise ProjectDetectionError(
                f"Invalid project binding in local git config: {bound_project_id!r}"
            )

        vault_dir = find_vault_dir_by_project_id(config.projects_dir, bound_project_id)
        if vault_dir is None:
            raise ProjectDetectionError(
                f"Bound project id '{bound_project_id}' was found in local git config, "
                "but no matching vault exists. Run 'envctl repair --recreate-bound-vault' "
                "or rebind the repository."
            )

        state = read_state(vault_dir / DEFAULT_STATE_FILENAME)
        resolved_slug = project_slug
        resolved_key = project_key
        if state is not None:
            resolved_slug = str(state.get("project_slug") or project_slug)
            resolved_key = str(state.get("project_key") or project_key)

        return _build_context(
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

    recovered = _recover_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=project_slug,
        project_key=project_key,
    )
    if recovered is not None:
        return recovered

    provisional_project_id = _build_provisional_project_id(repo_root, repo_remote)
    return _build_context(
        config=config,
        repo_root=repo_root,
        repo_remote=repo_remote,
        repo_contract_path=repo_contract_path,
        project_slug=project_slug,
        project_key=project_key,
        project_id=provisional_project_id,
        binding_source="derived",
    )


def persist_project_binding(config: AppConfig, context: ProjectContext) -> ProjectContext:
    """Persist the current repo ↔ vault binding and refresh vault state metadata."""
    if not is_valid_project_id(context.project_id):
        raise StateError(
            f"Cannot persist a non-canonical project id: {context.project_id!r}"
        )

    ensure_dir(config.projects_dir)

    vault_project_dir = build_vault_project_dir(
        context.project_slug,
        context.project_id,
        config.projects_dir,
    )
    ensure_dir(vault_project_dir)

    set_local_git_config(
        context.repo_root,
        GIT_CONFIG_PROJECT_ID_KEY,
        context.project_id,
    )

    state_path = vault_project_dir / DEFAULT_STATE_FILENAME
    upsert_state(
        state_path,
        project_slug=context.project_slug,
        project_key=context.project_key,
        project_id=context.project_id,
        repo_root=str(context.repo_root),
        git_remote=context.repo_remote,
    )

    return replace(
        context,
        binding_source="local",
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=state_path,
    )