"""Repository unlink service."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.domain.unlink import UnlinkResult
from envctl.repository.project_context import require_project_context


def run_unlink() -> UnlinkResult:
    """Remove the repository symlink only when present."""
    config = load_config()
    context = require_project_context(config=config)

    if context.repo_env_path.is_symlink():
        context.repo_env_path.unlink()
        return UnlinkResult(
            context=context,
            removed=True,
            message="Managed repository symlink removed",
        )

    return UnlinkResult(
        context=context,
        removed=False,
        message="No managed repository symlink found; no changes made",
    )
