"""Fill service."""

from __future__ import annotations

from collections.abc import Mapping

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.operations import FillPlanItem
from envctl.domain.project import ProjectContext
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.atomic import write_text_atomic


def build_fill_plan() -> tuple[ProjectContext, tuple[FillPlanItem, ...]]:
    """Return the missing required values that should be collected by the CLI."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)

    items: list[FillPlanItem] = []
    for key in report.missing_required:
        spec = contract.variables[key]
        items.append(
            FillPlanItem(
                key=key,
                description=spec.description or f"Provide a value for {key}",
                sensitive=spec.sensitive,
                default_value=None if spec.default is None else str(spec.default),
            )
        )

    return context, tuple(items)


def apply_fill(values: Mapping[str, str]) -> tuple[ProjectContext, list[str]]:
    """Persist collected values into the local vault."""
    _config, context = load_project_context(persist_binding=True)
    data = load_env_file(context.vault_values_path)
    changed: list[str] = []

    for key, value in values.items():
        normalized = value.strip()
        if not normalized:
            continue
        data[key] = normalized
        changed.append(key)

    if changed:
        write_text_atomic(context.vault_values_path, dump_env(data))

    return context, changed