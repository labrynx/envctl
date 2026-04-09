"""Resolution service implementation."""

from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.observability import get_active_observability_context
from envctl.observability.events import (
    CONTRACT_COMPOSE_ERROR,
    CONTRACT_COMPOSE_FINISH,
    CONTRACT_COMPOSE_START,
    RESOLUTION_ERROR,
    RESOLUTION_FINISH,
    RESOLUTION_START,
)
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow
from envctl.repository.contract_composition import load_resolved_contract_bundle
from envctl.repository.profile_repository import load_profile_values
from envctl.services.resolution_service.builders import build_resolved_value
from envctl.services.resolution_service.expansion import expand_selected_values
from envctl.services.resolution_service.selection import select_contract_values
from envctl.utils.logging import get_logger, summarize_key_count, summarize_keys
from envctl.utils.project_paths import is_local_profile, normalize_profile_name

logger = get_logger(__name__)


def load_contract_for_context(context: ProjectContext) -> Contract:
    """Load the contract for the current project."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTRACT_COMPOSE_START,
            status="start",
            module=__name__,
            operation="load_contract_for_context",
            fields={},
        )
    try:
        contract = load_resolved_contract_bundle(context.repo_root).contract
    except Exception:
        if obs_context is not None:
            record_event(
                obs_context,
                event=CONTRACT_COMPOSE_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="load_contract_for_context",
                fields={},
            )
        raise
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTRACT_COMPOSE_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="load_contract_for_context",
            fields={"contract_variable_count": len(contract.variables)},
        )
    return contract


def resolve_environment(
    context: ProjectContext,
    contract: Contract,
    *,
    active_profile: str | None = None,
) -> ResolutionReport:
    """Resolve environment values from the selected profile and contract defaults."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=RESOLUTION_START,
            status="start",
            module=__name__,
            operation="resolve_environment",
            fields={"has_profile": active_profile is not None},
        )
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Resolving environment",
        extra={
            "project_id": context.project_id,
            "active_profile": resolved_profile,
        },
    )

    try:
        _loaded_profile, _profile_env_path, profile_values = load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
        )
    except Exception:
        if obs_context is not None:
            record_event(
                obs_context,
                event=RESOLUTION_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="resolve_environment",
                fields={"active_profile": resolved_profile},
            )
        raise

    logger.debug(
        "Loaded profile values",
        extra={
            "active_profile": resolved_profile,
            "profile_key_count": len(profile_values),
            "profile_key_summary": summarize_key_count(profile_values),
        },
    )

    profile_source = (
        "vault" if is_local_profile(resolved_profile) else f"profile:{resolved_profile}"
    )

    selected_values, missing_required = select_contract_values(
        contract,
        profile_values=profile_values,
        profile_source=profile_source,
    )

    logger.debug(
        "Selected contract values",
        extra={
            "selected_key_count": len(selected_values),
            "missing_required_count": len(missing_required),
            "missing_required": summarize_keys(sorted(missing_required)),
        },
    )

    expansion_results, derived_sensitive = expand_selected_values(
        contract,
        selected_values,
    )

    values: dict[str, ResolvedValue] = {}
    invalid_keys: list[str] = []

    for key, selected in selected_values.items():
        spec = contract.variables[key]
        value, invalid = build_resolved_value(
            key=key,
            spec=spec,
            selected=selected,
            expanded=expansion_results[key],
            derived_sensitive=derived_sensitive.get(key, False),
        )
        values[key] = value
        if invalid:
            invalid_keys.append(key)

    unknown_keys = sorted(set(profile_values) - set(contract.variables))

    logger.debug(
        "Resolved environment report",
        extra={
            "resolved_key_count": len(values),
            "invalid_key_count": len(invalid_keys),
            "unknown_key_count": len(unknown_keys),
            "invalid_keys": summarize_keys(sorted(invalid_keys)),
            "unknown_keys": summarize_keys(unknown_keys),
        },
    )

    report = ResolutionReport.from_parts(
        values=values,
        missing_required=sorted(missing_required),
        unknown_keys=unknown_keys,
        invalid_keys=sorted(invalid_keys),
    )
    if obs_context is not None:
        record_event(
            obs_context,
            event=RESOLUTION_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="resolve_environment",
            fields={
                "active_profile": resolved_profile,
                "resolved_key_count": len(values),
                "invalid_key_count": len(invalid_keys),
                "unknown_key_count": len(unknown_keys),
                "missing_required_count": len(missing_required),
            },
        )
    return report
