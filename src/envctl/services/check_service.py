"""Check service."""

from __future__ import annotations

from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.services.context_service import load_project_context
from envctl.services.group_selection_service import filter_resolution_report
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def run_check(
    active_profile: str | None = None,
    *,
    group: str | None = None,
) -> tuple[ProjectContext, str, ResolutionReport]:
    """Validate the current project environment against the contract."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=resolved_profile)
    return context, resolved_profile, filter_resolution_report(report, contract, group=group)
