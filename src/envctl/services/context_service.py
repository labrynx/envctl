"""Shared context helpers."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.repository.project_context import build_project_context


def load_project_context(project_name: str | None = None) -> tuple[AppConfig, ProjectContext]:
    """Load config and build the current project context."""
    config = load_config()
    context = build_project_context(config, project_name=project_name)
    return config, context
