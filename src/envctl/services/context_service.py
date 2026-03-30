"""Shared context helpers."""

from __future__ import annotations

from dataclasses import replace

from envctl.config.loader import load_config
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.repository.project_context import build_project_context, persist_project_binding
from envctl.utils.project_ids import new_project_id


def load_project_context(
    project_name: str | None = None,
    *,
    persist_binding: bool = False,
) -> tuple[AppConfig, ProjectContext]:
    """Load config and build the current project context."""
    config = load_config()
    context = build_project_context(config, project_name=project_name)

    if persist_binding:
        if context.binding_source == "derived":
            context = replace(context, project_id=new_project_id())

        context = persist_project_binding(config, context)

    return config, context
