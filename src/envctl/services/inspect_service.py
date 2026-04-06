"""Inspect service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.domain.selection import ContractSelection
from envctl.repository.contract_repository import load_contract_with_warnings
from envctl.services.context_service import load_project_context
from envctl.services.contract_selection_service import filter_resolution_report
from envctl.services.resolution_service import resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def run_inspect(
    active_profile: str | None = None,
    *,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, str, ResolutionReport, tuple[ContractDeprecationWarning, ...]]:
    """Inspect the resolved environment."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    contract, warnings = load_contract_with_warnings(context.repo_contract_path)
    report = resolve_environment(context, contract, active_profile=resolved_profile)
    return (
        context,
        resolved_profile,
        filter_resolution_report(report, contract, selection=selection),
        warnings,
    )
