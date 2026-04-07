"""Shared projection validation helpers."""

from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.error_diagnostics import (
    ProjectionOperation,
    ProjectionValidationDiagnostics,
)
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.domain.selection import ContractSelection
from envctl.domain.selection_resolution import filter_resolution_report
from envctl.errors import ValidationError
from envctl.repository.contract_composition import load_resolved_contract_bundle
from envctl.services.resolution_service import resolve_environment
from envctl.utils.logging import get_logger, summarize_keys

logger = get_logger(__name__)


def resolve_projectable_environment(
    context: ProjectContext,
    *,
    active_profile: str,
    selection: ContractSelection | None,
    operation: ProjectionOperation,
) -> tuple[Contract, ResolutionReport, tuple[ContractDeprecationWarning, ...]]:
    """Resolve and validate one projectable environment."""
    logger.debug(
        "Resolving projectable environment",
        extra={
            "operation": operation,
            "active_profile": active_profile,
            "selection": selection.describe() if selection is not None else "full contract",
            "repo_root": context.repo_root,
        },
    )

    bundle = load_resolved_contract_bundle(context.repo_root)
    contract = bundle.contract
    report = resolve_environment(context, contract, active_profile=active_profile)
    filtered_report = filter_resolution_report(report, contract, selection=selection)

    if filtered_report.is_valid and not filtered_report.unknown_keys:
        logger.debug(
            "Projection validation passed",
            extra={
                "operation": operation,
                "active_profile": active_profile,
                "resolved_key_count": len(report.values),
            },
        )
        return contract, report, bundle.warnings

    logger.error(
        "Projection validation failed",
        extra={
            "operation": operation,
            "active_profile": active_profile,
            "missing_required": summarize_keys(filtered_report.missing_required),
            "invalid_keys": summarize_keys(filtered_report.invalid_keys),
            "unknown_keys": summarize_keys(filtered_report.unknown_keys),
        },
    )

    raise ValidationError(
        _build_projection_blocked_message(operation),
        diagnostics=ProjectionValidationDiagnostics(
            operation=operation,
            active_profile=active_profile,
            selection=selection or ContractSelection(),
            report=filtered_report,
            suggested_actions=_build_suggested_actions(filtered_report),
        ),
    )


def _build_projection_blocked_message(operation: ProjectionOperation) -> str:
    """Build a stable user-facing summary for one blocked projection."""
    return f"Cannot {operation} because the environment contract is not satisfied."


def _build_suggested_actions(report: ResolutionReport) -> tuple[str, ...]:
    """Build stable next-step suggestions for one invalid projection report."""
    actions: list[str] = []

    if report.missing_required:
        actions.extend(("envctl fill", "envctl set KEY VALUE"))

    if report.invalid_keys:
        actions.extend(("envctl check", "envctl inspect KEY"))

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
