"""Repair service."""

from __future__ import annotations

from dataclasses import replace

from envctl.adapters.git import get_local_git_config, resolve_repo_root
from envctl.config.loader import load_config
from envctl.constants import GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.operations import RepairResult
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError, ProjectDetectionError
from envctl.repository.project_context import (
    build_context_for_project_id,
    build_project_context,
    find_vault_dir_by_project_id,
    persist_project_binding,
)
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.project_ids import is_valid_project_id, new_project_id


def run_repair(
    *,
    create_if_missing: bool = False,
    recreate_bound_vault: bool = False,
) -> tuple[ProjectContext | None, RepairResult]:
    """Repair a recovered, missing, or incomplete local project binding."""
    config = load_config()
    repo_root = resolve_repo_root()
    bound_project_id = get_local_git_config(repo_root, GIT_CONFIG_PROJECT_ID_KEY)

    if bound_project_id is not None:
        if not is_valid_project_id(bound_project_id):
            raise ExecutionError(
                f"Invalid project binding in local git config '{GIT_CONFIG_PROJECT_ID_KEY}': "
                f"{bound_project_id!r}"
            )

        existing_vault_dir = find_vault_dir_by_project_id(config.projects_dir, bound_project_id)
        if existing_vault_dir is not None:
            context = build_context_for_project_id(
                config,
                repo_root=repo_root,
                project_id=bound_project_id,
                binding_source="local",
            )
            context = persist_project_binding(config, context)
            return context, RepairResult(
                status="healthy",
                detail="Local binding is already healthy.",
                project_id=context.project_id,
            )

        if recreate_bound_vault:
            context = build_context_for_project_id(
                config,
                repo_root=repo_root,
                project_id=bound_project_id,
                binding_source="local",
            )
            context = persist_project_binding(config, context)
            ensure_dir(context.vault_project_dir)
            ensure_file(context.vault_values_path, "")
            return context, RepairResult(
                status="recreated",
                detail="Recreated the missing vault for the current bound project id.",
                project_id=context.project_id,
            )

        return None, RepairResult(
            status="needs_action",
            detail=(
                "A local git binding exists, but its vault is missing. "
                "Run 'envctl repair --recreate-bound-vault' to recreate it, "
                "or use 'envctl rebind --new-project' to separate this checkout."
            ),
            project_id=bound_project_id,
        )

    try:
        context = build_project_context(config)
    except ProjectDetectionError as exc:
        return None, RepairResult(
            status="needs_action",
            detail=str(exc),
            project_id=None,
        )

    if context.binding_source == "local":
        return context, RepairResult(
            status="healthy",
            detail="Local binding is already healthy.",
            project_id=context.project_id,
        )

    if context.binding_source == "recovered":
        repaired = persist_project_binding(config, context)
        return repaired, RepairResult(
            status="repaired",
            detail="Recovered a matching vault and persisted the local git binding.",
            project_id=repaired.project_id,
        )

    if create_if_missing:
        created = replace(context, project_id=new_project_id())
        created = persist_project_binding(config, created)
        ensure_dir(created.vault_project_dir)
        ensure_file(created.vault_values_path, "")
        return created, RepairResult(
            status="created",
            detail="Created and persisted a new project binding for this checkout.",
            project_id=created.project_id,
        )

    return context, RepairResult(
        status="needs_action",
        detail=(
            "No persisted binding exists yet. Run 'envctl repair --create-if-missing' "
            "or 'envctl init' to create one."
        ),
        project_id=context.project_id,
    )
