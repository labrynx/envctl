"""Check service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CheckResult
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.domain.selection import ContractSelection
from envctl.observability import get_active_observability_context
from envctl.observability.events import (
    CONTRACT_COMPOSE_ERROR,
    CONTRACT_COMPOSE_FINISH,
    CONTRACT_COMPOSE_START,
)
from envctl.observability.error_mapping import map_exception_to_error_event
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow
from envctl.repository.contract_composition import load_resolved_contract_bundle
from envctl.services.context_service import load_project_context
from envctl.services.resolution_diagnostics import (
    build_diagnostic_problems,
    build_diagnostic_summary,
)
from envctl.services.resolution_service import resolve_environment
from envctl.services.selection_filtering import filter_resolution_report
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def _build_check_result(
    active_profile: str,
    selection: ContractSelection,
    filtered_report: ResolutionReport,
) -> CheckResult:
    return CheckResult(
        active_profile=active_profile,
        selection=selection,
        summary=build_diagnostic_summary(filtered_report),
        problems=build_diagnostic_problems(filtered_report),
        values=tuple(filtered_report.values[key] for key in sorted(filtered_report.values)),
    )


def run_check(
    active_profile: str | None = None,
    *,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, CheckResult, tuple[ContractDeprecationWarning, ...]]:
    """Validate the current project environment against the contract."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTRACT_COMPOSE_START,
            status="start",
            module=__name__,
            operation="run_check",
            fields={
                "has_selection": selection is not None,
                "has_profile": active_profile is not None,
            },
        )
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    active_selection = selection or ContractSelection()
    logger.debug(
        "Running check",
        extra={
            "active_profile": resolved_profile,
            "selection": active_selection.describe(),
            "repo_root": context.repo_root,
        },
    )
    try:
        bundle = load_resolved_contract_bundle(context.repo_root)
    except Exception as exc:
        if obs_context is not None:
            mapping = map_exception_to_error_event(exc)
            record_event(
                obs_context,
                event=CONTRACT_COMPOSE_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="run_check",
                fields={
                    "has_selection": selection is not None,
                    "has_profile": active_profile is not None,
                    "message_safe": mapping.message_safe,
                    "phase": "contract_compose",
                    "recoverable": mapping.recoverable,
                },
            )
            record_event(
                obs_context,
                event=mapping.event,
                status="error",
                module=__name__,
                operation="run_check",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "contract_compose",
                    "recoverable": mapping.recoverable,
                },
            )
        raise
    contract = bundle.contract
    report = resolve_environment(context, contract, active_profile=resolved_profile)
    filtered_report = filter_resolution_report(report, contract, selection=active_selection)
    logger.debug(
        "Built filtered check report",
        extra={
            "active_profile": resolved_profile,
            "selection": active_selection.describe(),
            "visible_value_count": len(filtered_report.values),
            "missing_required_count": len(filtered_report.missing_required),
            "invalid_key_count": len(filtered_report.invalid_keys),
            "unknown_key_count": len(filtered_report.unknown_keys),
        },
    )
    result = _build_check_result(resolved_profile, active_selection, filtered_report)
    if context.runtime_warnings:
        logger.debug(
            "Appending runtime warnings to check result",
            extra={
                "active_profile": resolved_profile,
                "runtime_warning_count": len(context.runtime_warnings),
            },
        )
        result = CheckResult(
            active_profile=result.active_profile,
            selection=result.selection,
            summary=result.summary,
            problems=result.problems,
            values=result.values,
            warnings=result.warnings + context.runtime_warnings,
        )
    logger.debug(
        "Check result ready",
        extra={
            "active_profile": resolved_profile,
            "selection": active_selection.describe(),
            "problem_count": len(result.problems),
            "warning_count": len(result.warnings),
        },
    )
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTRACT_COMPOSE_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="run_check",
            fields={
                "contract_variable_count": len(contract.variables),
                "problem_count": len(result.problems),
                "warning_count": len(result.warnings),
            },
        )
    return (context, result, bundle.warnings)
