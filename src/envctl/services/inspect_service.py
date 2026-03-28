"""Inspect service."""

from __future__ import annotations

from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment


def run_inspect() -> tuple[ProjectContext, ResolutionReport]:
    """Inspect the resolved environment."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)
    return context, report
