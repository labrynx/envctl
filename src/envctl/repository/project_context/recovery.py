from __future__ import annotations

from pathlib import Path

from envctl.constants import DEFAULT_STATE_FILENAME, GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.app_config import AppConfig
from envctl.domain.error_diagnostics import ProjectBindingDiagnostics
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError
from envctl.repository.project_context.builders import build_context
from envctl.repository.state_repository import read_state


def iter_state_records(projects_dir: Path) -> list[tuple[Path, dict[str, object]]]:
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


def recover_context(
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

    for vault_dir, state in iter_state_records(config.projects_dir):
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
            f"Bind one explicitly by writing '{GIT_CONFIG_PROJECT_ID_KEY}'.",
            diagnostics=ProjectBindingDiagnostics(
                category="ambiguous_vault_identity",
                repo_root=repo_root,
                matching_ids=tuple(sorted(unique_by_id)),
                suggested_actions=("envctl project bind",),
            ),
        )

    vault_dir, state = next(iter(unique_by_id.values()))
    project_id = str(state["project_id"])
    resolved_slug = str(state.get("project_slug") or project_slug)
    resolved_key = str(state.get("project_key") or project_key)

    return build_context(
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
