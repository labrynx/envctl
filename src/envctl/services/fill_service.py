"""Fill service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.contract import VariableSpec
from envctl.domain.operations import FillPlanItem
from envctl.domain.project import ProjectContext
from envctl.observability.timing import observe_span
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.project_paths import normalize_profile_name


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
    with observe_span(
        "variables.mutate",
        module=__name__,
        operation="build_fill_plan",
        fields={},
    ) as span_fields:
        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)
        contract = load_contract_for_context(context)
        report = resolve_environment(context, contract, active_profile=resolved_profile)

        plan: list[FillPlanItem] = []
        for key in report.missing_required:
            spec = contract.variables[key]
            plan.append(_build_fill_item(key, spec))
        span_fields["selected_profile"] = resolved_profile
        span_fields["missing_required_count"] = len(report.missing_required)
        return context, resolved_profile, tuple(plan)


def apply_fill(
    values_to_apply: dict[str, str],
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, list[str]]:
    """Apply user-provided fill values to the active profile."""
    with observe_span(
        "variables.mutate",
        module=__name__,
        operation="apply_fill",
        fields={"updated": True},
    ) as span_fields:
        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)

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
        span_fields["selected_profile"] = resolved_profile
        span_fields["changed_key_count"] = len(changed_keys)
        return context, resolved_profile, profile_path, changed_keys
