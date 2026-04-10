"""Common normalized field helpers for observability."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from envctl.observability.sanitization import sanitize_command

if TYPE_CHECKING:
    from envctl.domain.selection import ContractSelection


def selection_scope(selection: ContractSelection | None) -> str:
    """Return one normalized selection scope description."""
    if selection is None:
        return "full contract"
    return selection.describe()


def command_preview(command: Sequence[str]) -> tuple[str, ...]:
    """Return one sanitized command preview for observability fields."""
    return sanitize_command(command, policy="masked")


def repo_relative_path(path: Path, *, repo_root: Path | None = None) -> str:
    """Return a stable repo-relative path when possible."""
    if repo_root is not None:
        with_repo_root = repo_root.resolve()
        try:
            return str(path.resolve().relative_to(with_repo_root))
        except ValueError:
            pass
    return path.name
