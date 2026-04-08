"""Fill service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.contract import VariableSpec
from envctl.domain.operations import FillPlanItem
from envctl.domain.project import ProjectContext
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def _build_fill_item(key: str, spec: VariableSpec) -> FillPlanItem:
    """Build one fill plan item from the contract."""
    default_value = None if spec.default is None else str(spec.default)
    return FillPlanItem(
        key=key,
        description=spec.description,
        sensitive=spec.sensitive,
        default_value=default_value,
    )


def build_fill_plan(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, tuple[FillPlanItem, ...]]:
    """Build the interactive fill plan for the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Building fill plan",
        extra={
            "active_profile": resolved_profile,
            "repo_root": context.repo_root,
        },
    )
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    plan: list[FillPlanItem] = []
    for key in report.missing_required:
        spec = contract.variables[key]
        plan.append(_build_fill_item(key, spec))
    logger.debug(
        "Built fill plan",
        extra={
            "active_profile": resolved_profile,
            "missing_required_count": len(report.missing_required),
            "planned_item_count": len(plan),
        },
    )

    return context, resolved_profile, tuple(plan)


def apply_fill(
    values_to_apply: dict[str, str],
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, list[str]]:
    """Apply user-provided fill values to the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Applying fill values",
        extra={
            "active_profile": resolved_profile,
            "requested_key_count": len(values_to_apply),
        },
    )

    _resolved_profile, _profile_path, stored = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )
    changed_keys: list[str] = []
    skipped_blank_keys: list[str] = []

    for key, value in values_to_apply.items():
        cleaned = value.strip()
        if not cleaned:
            skipped_blank_keys.append(key)
            continue
        stored[key] = cleaned
        changed_keys.append(key)

    _resolved_profile, profile_path = write_profile_values(
        context,
        resolved_profile,
        stored,
        require_existing_explicit=True,
    )
    logger.debug(
        "Applied fill values",
        extra={
            "active_profile": resolved_profile,
            "changed_key_count": len(changed_keys),
            "skipped_blank_key_count": len(skipped_blank_keys),
            "profile_path": profile_path,
        },
    )
    return context, resolved_profile, profile_path, changed_keys
