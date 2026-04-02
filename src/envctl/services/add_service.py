"""Add service."""

from __future__ import annotations

from envctl.domain.contract import Contract, VariableFormat, VariableSpec, VariableType
from envctl.domain.contract_inference import infer_spec
from envctl.domain.operations import AddVariableRequest, AddVariableResult
from envctl.domain.project import ProjectContext
from envctl.errors import ValidationError
from envctl.repository.contract_repository import (
    create_empty_contract,
    ensure_contract_metadata,
    load_contract_optional,
    write_contract,
)
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.utils.project_paths import normalize_profile_name

_ALLOWED_VARIABLE_TYPES: tuple[VariableType, ...] = ("string", "int", "bool", "url")
_ALLOWED_VARIABLE_FORMATS: tuple[VariableFormat, ...] = ("json", "url", "csv")


def _resolve_variable_type(raw_type: str | None, inferred_type: VariableType) -> VariableType:
    """Resolve one final variable type."""
    if raw_type is None:
        return inferred_type

    normalized = raw_type.strip().lower()
    if normalized not in _ALLOWED_VARIABLE_TYPES:
        allowed = ", ".join(_ALLOWED_VARIABLE_TYPES)
        raise ValidationError(f"Invalid variable type: {raw_type!r}. Expected one of: {allowed}")

    return normalized  # type: ignore[return-value]


def _resolve_variable_format(raw_format: str | None) -> VariableFormat | None:
    """Resolve one optional string-format hint."""
    if raw_format is None:
        return None

    normalized = raw_format.strip().lower()
    if not normalized:
        return None

    if normalized not in _ALLOWED_VARIABLE_FORMATS:
        allowed = ", ".join(_ALLOWED_VARIABLE_FORMATS)
        raise ValidationError(
            f"Invalid variable format: {raw_format!r}. Expected one of: {allowed}"
        )

    return normalized  # type: ignore[return-value]


def _apply_request_to_spec(
    inferred: VariableSpec,
    request: AddVariableRequest,
) -> tuple[VariableSpec, dict[str, object] | None, tuple[str, ...]]:
    """Apply request overrides on top of the inferred spec."""
    inferred_fields_used: list[str] = []

    type_ = _resolve_variable_type(request.override_type, inferred.type)
    if request.override_type is None:
        inferred_fields_used.append("type")

    format_ = _resolve_variable_format(request.override_format)
    if format_ is not None and type_ != "string":
        raise ValidationError("Variable format can only be used with type 'string'")

    required = (
        request.override_required if request.override_required is not None else inferred.required
    )
    if request.override_required is None:
        inferred_fields_used.append("required")

    sensitive = (
        request.override_sensitive if request.override_sensitive is not None else inferred.sensitive
    )
    if request.override_sensitive is None:
        inferred_fields_used.append("sensitive")

    description = (
        request.override_description
        if request.override_description is not None
        else inferred.description
    )
    if request.override_description is None and inferred.description:
        inferred_fields_used.append("description")

    spec = VariableSpec(
        name=request.key,
        type=type_,
        required=required,
        sensitive=sensitive,
        description=description or "",
        default=request.override_default,
        example=request.override_example,
        format=format_,
        pattern=request.override_pattern,
        choices=request.override_choices or (),
    )

    inferred_spec: dict[str, object] | None = None
    if inferred_fields_used:
        inferred_spec = {
            "type": inferred.type,
            "required": inferred.required,
            "sensitive": inferred.sensitive,
        }
        if inferred.description:
            inferred_spec["description"] = inferred.description

    return spec, inferred_spec, tuple(inferred_fields_used)


def _load_or_create_contract(
    context: ProjectContext,
) -> tuple[Contract, bool]:
    """Load the repository contract or create an empty one."""
    contract = load_contract_optional(context.repo_contract_path)
    contract_created = contract is None

    if contract is None:
        contract = create_empty_contract(
            project_key=context.project_key,
            project_name=context.display_name,
        )
    else:
        contract = ensure_contract_metadata(
            contract,
            project_key=context.project_key,
            project_name=context.display_name,
        )

    return contract, contract_created


def run_add(
    request: AddVariableRequest,
    active_profile: str | None = None,
) -> tuple[ProjectContext, AddVariableResult]:
    """Add one variable to the contract and store its initial value in the active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract, contract_created = _load_or_create_contract(context)

    inferred = infer_spec(request.key, request.value)
    spec, inferred_spec, inferred_fields_used = _apply_request_to_spec(inferred, request)

    contract_entry_created = request.key not in contract.variables
    updated_contract = contract.with_variable(spec)
    write_contract(context.repo_contract_path, updated_contract)

    _resolved_profile, profile_path, profile_values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )
    profile_values[request.key] = request.value
    write_profile_values(
        context,
        resolved_profile,
        profile_values,
        require_existing_explicit=True,
    )

    result = AddVariableResult(
        key=request.key,
        active_profile=resolved_profile,
        profile_path=profile_path,
        value_written=True,
        contract_created=contract_created,
        contract_updated=True,
        contract_entry_created=contract_entry_created,
        inferred_spec=inferred_spec,
        inferred_fields_used=inferred_fields_used,
    )
    return context, result
