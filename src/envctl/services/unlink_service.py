"""Repository unlink service."""

from __future__ import annotations

from dataclasses import dataclass

from envctl.config.loader import load_config
from envctl.models import ProjectContext
from envctl.utils.paths import require_project_context


@dataclass(frozen=True)
class UnlinkResult:
    """Result of an unlink operation."""

    context: ProjectContext
    removed: bool
    message: str


def run_unlink() -> UnlinkResult:
    """Remove the repository symlink only when present.

    Behavior:
    - requires valid repository metadata
    - removes the repository env symlink if present
    - if no symlink exists, performs no action
    - does not modify a regular file
    - does not remove repository metadata
    - does not remove the managed vault file

    TODO(v1.1):
    - add a dedicated `detach` or `remove` command for explicit local materialization
    - support richer unlink diagnostics for scripting
    """
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
