"""Add service."""

from __future__ import annotations

from dataclasses import asdict, replace

from envctl.domain.contract import VariableSpec
from envctl.domain.contract_inference import infer_spec
from envctl.domain.operations import AddResult
from envctl.domain.project import ConfirmFn, ProjectContext, PromptFn
from envctl.repository.contract_repository import (
    create_empty_contract,
    load_contract_optional,
    upsert_variable,
    write_contract,
)
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.dotenv import dump_env, load_env_file
from envctl.utils.filesystem import ensure_dir
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions

AllowedType = str


def _stringify(value: str | int | bool | None) -> str | None:
    """Convert an optional scalar value into a prompt-friendly string."""
    if value is None:
        return None
    return str(value)


def _prompt_optional(
    prompt: PromptFn,
    message: str,
    *,
    default: str | None,
) -> str | None:
    """Prompt for a non-secret optional string value."""
    answer = prompt(message, False, default)
    normalized = answer.strip()
    if not normalized:
        return default
    return normalized


def _prompt_choices(
    prompt: PromptFn,
    *,
    default: tuple[str, ...],
) -> tuple[str, ...]:
    """Prompt for a comma-separated list of choices."""
    default_text = ", ".join(default) if default else None
    answer = prompt("Choices (comma-separated)", False, default_text).strip()
    if not answer:
        return default
    return tuple(part.strip() for part in answer.split(",") if part.strip())


def _edit_spec_interactively(
    spec: VariableSpec,
    *,
    prompt: PromptFn,
    confirm: ConfirmFn,
) -> VariableSpec:
    """Interactively review and edit one variable spec."""
    updated = spec

    updated = replace(
        updated,
        type=prompt("Type", False, updated.type).strip() or updated.type,
    )

    updated = replace(
        updated,
        required=confirm("Required?", updated.required),
    )

    updated = replace(
        updated,
        sensitive=confirm("Sensitive?", updated.sensitive),
    )

    description = _prompt_optional(
        prompt,
        "Description",
        default=updated.description or None,
    )
    updated = replace(updated, description=description or "")

    default_value = _prompt_optional(
        prompt,
        "Default value",
        default=_stringify(updated.default),
    )
    updated = replace(updated, default=default_value)

    example_value = _prompt_optional(
        prompt,
        "Example value",
        default=updated.example,
    )
    updated = replace(updated, example=example_value)

    pattern_value = _prompt_optional(
        prompt,
        "Validation pattern",
        default=updated.pattern,
    )
    updated = replace(updated, pattern=pattern_value)

    updated = replace(
        updated,
        choices=_prompt_choices(prompt, default=updated.choices),
    )

    return updated


def _apply_overrides(
    spec: VariableSpec,
    *,
    override_type: AllowedType | None,
    override_required: bool | None,
    override_sensitive: bool | None,
    override_description: str | None,
    override_default: str | int | bool | None,
    override_example: str | None,
    override_pattern: str | None,
    override_choices: tuple[str, ...] | None,
) -> VariableSpec:
    """Apply explicit CLI overrides to a variable spec."""
    updated = spec

    if override_type is not None:
        updated = replace(updated, type=override_type)

    if override_required is not None:
        updated = replace(updated, required=override_required)

    if override_sensitive is not None:
        updated = replace(updated, sensitive=override_sensitive)

    if override_description is not None:
        updated = replace(updated, description=override_description)

    if override_default is not None:
        updated = replace(updated, default=override_default)

    if override_example is not None:
        updated = replace(updated, example=override_example)

    if override_pattern is not None:
        updated = replace(updated, pattern=override_pattern)

    if override_choices is not None:
        updated = replace(updated, choices=override_choices)

    return updated


def run_add(
    key: str,
    value: str,
    *,
    interactive: bool = False,
    prompt: PromptFn | None = None,
    confirm: ConfirmFn | None = None,
    override_type: AllowedType | None = None,
    override_required: bool | None = None,
    override_sensitive: bool | None = None,
    override_description: str | None = None,
    override_default: str | int | bool | None = None,
    override_example: str | None = None,
    override_pattern: str | None = None,
    override_choices: tuple[str, ...] | None = None,
) -> tuple[ProjectContext, AddResult]:
    """Add or update a key in vault and contract."""
    _config, context = load_project_context()

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    data = load_env_file(context.vault_values_path)
    data[key] = value
    write_text_atomic(context.vault_values_path, dump_env(data))
    ensure_private_file_permissions(context.vault_values_path)

    contract = load_contract_optional(context.repo_contract_path)
    contract_created = False
    contract_updated = False
    contract_entry_created = False
    inferred_spec: dict[str, object] | None = None

    if contract is None:
        contract = create_empty_contract()
        contract_created = True

    existing = contract.variables.get(key)

    if existing is None:
        base_spec = infer_spec(key, value)
        inferred_spec = asdict(base_spec)
        contract_entry_created = True
    else:
        base_spec = existing

    if interactive:
        if prompt is None or confirm is None:
            raise ValueError("Interactive add requires prompt and confirm callbacks")
        base_spec = _edit_spec_interactively(
            base_spec,
            prompt=prompt,
            confirm=confirm,
        )

    final_spec = _apply_overrides(
        base_spec,
        override_type=override_type,
        override_required=override_required,
        override_sensitive=override_sensitive,
        override_description=override_description,
        override_default=override_default,
        override_example=override_example,
        override_pattern=override_pattern,
        override_choices=override_choices,
    )

    if existing is None or final_spec != existing:
        contract = upsert_variable(contract, final_spec)
        contract_updated = True
        write_contract(context.repo_contract_path, contract)

    return context, AddResult(
        key=key,
        value_written=True,
        contract_created=contract_created,
        contract_updated=contract_updated,
        contract_entry_created=contract_entry_created,
        declared_in_contract=True,
        inferred_spec=inferred_spec,
    )
