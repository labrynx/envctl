"""Fill service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.contract import VariableSpec
from envctl.domain.operations import FillPlanItem
from envctl.domain.project import ProjectContext
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import build_profile_env_path, normalize_profile_name


def _write_profile_values(path: Path, values: dict[str, str]) -> None:
    """Persist one profile values file."""
    ensure_dir(path.parent)
    write_text_atomic(path, dump_env(values))


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
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    plan: list[FillPlanItem] = []
    for key in report.missing_required:
        spec = contract.variables[key]
        plan.append(_build_fill_item(key, spec))

    return context, resolved_profile, tuple(plan)


def apply_fill(
    values_to_apply: dict[str, str],
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, list[str]]:
    """Apply user-provided fill values to the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    profile_path = build_profile_env_path(context.vault_project_dir, resolved_profile)

    stored = load_env_file(profile_path)
    changed_keys: list[str] = []

    for key, value in values_to_apply.items():
        cleaned = value.strip()
        if not cleaned:
            continue
        stored[key] = cleaned
        changed_keys.append(key)

    _write_profile_values(profile_path, stored)
    return context, resolved_profile, profile_path, changed_keys
