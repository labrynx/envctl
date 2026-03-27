"""Repository status service."""

from __future__ import annotations

from pathlib import Path

from envctl.config.loader import load_config
from envctl.models import StatusReport
from envctl.utils.filesystem import read_project_metadata_record
from envctl.utils.paths import build_context_from_metadata_record, resolve_repo_root


def _resolve_symlink_match(repo_env_path: Path, vault_env_path: Path | None) -> bool:
    """Return whether the repository symlink points to the expected vault path."""
    if not repo_env_path.is_symlink() or vault_env_path is None:
        return False

    try:
        return repo_env_path.resolve() == vault_env_path.resolve()
    except OSError:
        return False


def run_status() -> StatusReport:
    """Build a human-oriented repository status report."""
    config = load_config()
    repo_root = resolve_repo_root()
    repo_metadata_path = repo_root / config.metadata_filename
    metadata = read_project_metadata_record(repo_metadata_path)

    context = build_context_from_metadata_record(
        config=config,
        repo_root=repo_root,
        metadata=metadata,
    )

    if context is None:
        return StatusReport(
            state="not initialized",
            project_slug=None,
            project_id=None,
            repo_root=repo_root,
            repo_metadata_path=repo_metadata_path,
            repo_env_path=repo_root / config.env_filename,
            vault_env_path=None,
            summary="Repository not initialized with envctl",
            repo_env_status="unmanaged",
            vault_env_status="unknown",
            issues=[],
            suggested_action="envctl init",
        )

    repo_env_path = context.repo_env_path
    vault_env_path = context.vault_env_path
    symlink_matches = _resolve_symlink_match(repo_env_path, vault_env_path)

    if symlink_matches and vault_env_path.exists():
        return StatusReport(
            state="healthy",
            project_slug=context.project_slug,
            project_id=context.project_id,
            repo_root=repo_root,
            repo_metadata_path=repo_metadata_path,
            repo_env_path=repo_env_path,
            vault_env_path=vault_env_path,
            summary="Repository is correctly linked to the managed vault env file",
            repo_env_status="linked",
            vault_env_status="present",
            issues=[],
            suggested_action=None,
        )

    issues: list[str] = []

    if not vault_env_path.exists():
        issues.append("managed vault env file does not exist")
        return StatusReport(
            state="missing vault",
            project_slug=context.project_slug,
            project_id=context.project_id,
            repo_root=repo_root,
            repo_metadata_path=repo_metadata_path,
            repo_env_path=repo_env_path,
            vault_env_path=vault_env_path,
            summary="Managed vault env file is missing",
            repo_env_status="linked" if symlink_matches else "not linked",
            vault_env_status="missing",
            issues=issues,
            suggested_action="envctl init",
        )

    if repo_env_path.is_symlink():
        issues.append(".env.local is not linked to the managed vault file")
        repo_env_status = "symlink mismatch"
    elif repo_env_path.exists():
        issues.append(".env.local is a regular file, not a managed symlink")
        repo_env_status = "regular file"
    else:
        issues.append(".env.local is missing")
        repo_env_status = "missing"

    return StatusReport(
        state="broken",
        project_slug=context.project_slug,
        project_id=context.project_id,
        repo_root=repo_root,
        repo_metadata_path=repo_metadata_path,
        repo_env_path=repo_env_path,
        vault_env_path=vault_env_path,
        summary="Repository link is broken or missing",
        repo_env_status=repo_env_status,
        vault_env_status="present",
        issues=issues,
        suggested_action="envctl repair",
    )