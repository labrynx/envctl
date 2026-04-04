"""Shared projection validation helpers."""

from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.errors import ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.error_diagnostics import (
    ProjectionOperation,
    ProjectionValidationDiagnostics,
)
from envctl.services.group_selection_service import filter_resolution_report
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def resolve_projectable_environment(
    context: ProjectContext,
    *,
    active_profile: str,
    group: str | None,
    operation: ProjectionOperation,
) -> tuple[Contract, ResolutionReport]:
    """Resolve and validate one projectable environment."""
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=active_profile)
    filtered_report = filter_resolution_report(report, contract, group=group)

    # Validation is evaluated against the selected projection view, but callers
    # still receive the full report so later projection steps can reuse the
    # complete resolved environment before group-level filtering.
    if filtered_report.is_valid and not filtered_report.unknown_keys:
        return contract, report

    raise ValidationError(
        _build_projection_blocked_message(operation),
        diagnostics=ProjectionValidationDiagnostics(
            operation=operation,
            active_profile=active_profile,
            selected_group=group,
            report=filtered_report,
            suggested_actions=_build_suggested_actions(filtered_report),
        ),
    )


def validate_projection_request(
    active_profile: str | None = None,
    *,
    group: str | None,
    operation: ProjectionOperation,
) -> tuple[ProjectContext, str]:
    """Validate one projection command request without performing the projection."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    resolve_projectable_environment(
        context,
        active_profile=resolved_profile,
        group=group,
        operation=operation,
    )
    return context, resolved_profile


def _build_projection_blocked_message(operation: ProjectionOperation) -> str:
    """Build a stable user-facing summary for one blocked projection."""
    return f"Cannot {operation} because the environment contract is not satisfied."


def _build_suggested_actions(report: ResolutionReport) -> tuple[str, ...]:
    """Build stable next-step suggestions for one invalid projection report."""
    actions: list[str] = []

    if report.missing_required:
        actions.extend(("envctl fill", "envctl set KEY VALUE"))

    if report.invalid_keys:
        actions.extend(("envctl check", "envctl explain KEY"))

    if report.unknown_keys:
        actions.extend(("envctl check", "envctl inspect"))

    seen: set[str] = set()
    ordered_actions: list[str] = []
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        ordered_actions.append(action)

    return tuple(ordered_actions)
