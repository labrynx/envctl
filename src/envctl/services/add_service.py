"""Add service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.contract import VariableSpec
from envctl.domain.contract_inference import infer_spec
from envctl.domain.operations import AddResult, AddVariableRequest
from envctl.domain.project import ProjectContext
from envctl.repository.contract_repository import (
    create_empty_contract,
    ensure_contract_metadata,
    load_contract_optional,
    write_contract,
)
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir


def _apply_request_to_spec(
    base_spec: VariableSpec,
    request: AddVariableRequest,
) -> VariableSpec:
    """Apply explicit request overrides to a base spec."""
    updates: dict[str, object] = {}

    if request.override_type is not None:
        updates["type"] = request.override_type

    if request.override_required is not None:
        updates["required"] = request.override_required

    if request.override_sensitive is not None:
        updates["sensitive"] = request.override_sensitive

    if request.override_description is not None:
        updates["description"] = request.override_description

    if request.override_default is not None:
        updates["default"] = request.override_default

    if request.override_example is not None:
        updates["example"] = request.override_example

    if request.override_pattern is not None:
        updates["pattern"] = request.override_pattern

    if request.override_choices is not None:
        updates["choices"] = request.override_choices

    if not updates:
        return base_spec

    return base_spec.model_copy(update=updates)


def _collect_inferred_fields_used(
    *,
    base_spec: VariableSpec,
    final_spec: VariableSpec,
    request: AddVariableRequest,
) -> tuple[str, ...]:
    """Return the inferred fields that survived explicit overrides."""
    fields: list[str] = []

    if request.override_type is None and final_spec.type == base_spec.type:
        fields.append("type")

    if request.override_required is None and final_spec.required == base_spec.required:
        fields.append("required")

    if request.override_sensitive is None and final_spec.sensitive == base_spec.sensitive:
        fields.append("sensitive")

    if request.override_description is None and final_spec.description == base_spec.description:
        if final_spec.description:
            fields.append("description")

    if request.override_default is None and final_spec.default == base_spec.default:
        if final_spec.default is not None:
            fields.append("default")

    if request.override_example is None and final_spec.example == base_spec.example:
        if final_spec.example is not None:
            fields.append("example")

    if request.override_pattern is None and final_spec.pattern == base_spec.pattern:
        if final_spec.pattern is not None:
            fields.append("pattern")

    if request.override_choices is None and final_spec.choices == base_spec.choices:
        if final_spec.choices:
            fields.append("choices")

    return tuple(fields)


def run_add(request: AddVariableRequest) -> tuple[ProjectContext, AddResult]:
    """Add or update a key in vault and contract."""
    _config, context = load_project_context(persist_binding=True)

    ensure_dir(context.vault_project_dir)

    data = load_env_file(context.vault_values_path)
    data[request.key] = request.value
    write_text_atomic(context.vault_values_path, dump_env(data))

    contract = load_contract_optional(context.repo_contract_path)
    contract_created = False
    contract_updated = False
    contract_entry_created = False
    inferred_spec: dict[str, object] | None = None
    inferred_fields_used: tuple[str, ...] = ()

    if contract is None:
        contract = create_empty_contract(
            project_key=context.project_key,
            project_name=context.project_slug,
        )
        contract_created = True
    else:
        contract = ensure_contract_metadata(
            contract,
            project_key=context.project_key,
            project_name=context.project_slug,
        )

    existing = contract.variables.get(request.key)

    if existing is None:
        base_spec = infer_spec(request.key, request.value)
        inferred_spec = base_spec.model_dump(mode="python")
        contract_entry_created = True
    else:
        base_spec = existing

    final_spec = _apply_request_to_spec(base_spec, request)

    if existing is None:
        inferred_fields_used = _collect_inferred_fields_used(
            base_spec=base_spec,
            final_spec=final_spec,
            request=request,
        )

    if existing is None or final_spec != existing or contract_created:
        contract = contract.with_variable(final_spec)
        write_contract(context.repo_contract_path, contract)
        contract_updated = True

    return context, AddResult(
        key=request.key,
        value_written=True,
        contract_created=contract_created,
        contract_updated=contract_updated,
        contract_entry_created=contract_entry_created,
        declared_in_contract=True,
        inferred_spec=inferred_spec,
        inferred_fields_used=inferred_fields_used,
    )