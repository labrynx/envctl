"""Unlink command domain models."""

from __future__ import annotations

from dataclasses import dataclass

from envctl.domain.project import ProjectContext


@dataclass(frozen=True)
class UnlinkResult:
    """Result of an unlink operation."""

    context: ProjectContext
    removed: bool
    message: str
