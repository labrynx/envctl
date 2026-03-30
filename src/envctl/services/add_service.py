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


def _field_uses_inference(
    *,
    override_used: bool,
    final_value: object,
    base_value: object,
    require_non_empty: bool = False,
) -> bool:
    """Return whether a final field value still comes from inference."""
    if override_used or final_value != base_value:
        return False

    if not require_non_empty:
        return True

    if final_value is None:
        return False

    if isinstance(final_value, tuple):
        return len(final_value) > 0

    if isinstance(final_value, str):
        return final_value != ""

    return True


def _collect_inferred_fields_used(
    *,
    base_spec: VariableSpec,
    final_spec: VariableSpec,
    request: AddVariableRequest,
) -> tuple[str, ...]:
    """Return the inferred fields that survived explicit overrides."""
    checks = (
        ("type", request.override_type is not None, final_spec.type, base_spec.type, False),
        (
            "required",
            request.override_required is not None,
            final_spec.required,
            base_spec.required,
            False,
        ),
        (
            "sensitive",
            request.override_sensitive is not None,
            final_spec.sensitive,
            base_spec.sensitive,
            False,
        ),
        (
            "description",
            request.override_description is not None,
            final_spec.description,
            base_spec.description,
            True,
        ),
        (
            "default",
            request.override_default is not None,
            final_spec.default,
            base_spec.default,
            True,
        ),
        (
            "example",
            request.override_example is not None,
            final_spec.example,
            base_spec.example,
            True,
        ),
        (
            "pattern",
            request.override_pattern is not None,
            final_spec.pattern,
            base_spec.pattern,
            True,
        ),
        (
            "choices",
            request.override_choices is not None,
            final_spec.choices,
            base_spec.choices,
            True,
        ),
    )

    fields: list[str] = []
    for name, override_used, final_value, base_value, require_non_empty in checks:
        if _field_uses_inference(
            override_used=override_used,
            final_value=final_value,
            base_value=base_value,
            require_non_empty=require_non_empty,
        ):
            fields.append(name)

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
