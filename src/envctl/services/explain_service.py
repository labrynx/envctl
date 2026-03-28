"""Explain service."""

from __future__ import annotations

from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolvedValue
from envctl.errors import ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment


def run_explain(key: str) -> tuple[ProjectContext, ResolvedValue]:
    """Explain one resolved key."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)

    try:
        value = report.values[key]
    except KeyError as exc:
        raise ValidationError(f"Key is not resolved: {key}") from exc

    return context, value
