"""Add command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm, typer_prompt
from envctl.cli.decorators import handle_errors
from envctl.domain.contract_inference import infer_spec
from envctl.domain.operations import AddVariableRequest
from envctl.services.add_service import run_add
from envctl.utils.output import print_kv, print_success, print_warning

TYPE_OPTION = typer.Option(None, "--type", help="Override the inferred variable type.")
REQUIRED_OPTION = typer.Option(False, "--required", help="Mark the variable as required.")
OPTIONAL_OPTION = typer.Option(False, "--optional", help="Mark the variable as optional.")
SENSITIVE_OPTION = typer.Option(False, "--sensitive", help="Mark the variable as sensitive.")
NON_SENSITIVE_OPTION = typer.Option(
    False,
    "--non-sensitive",
    help="Mark the variable as non-sensitive.",
)
INTERACTIVE_OPTION = typer.Option(
    False,
    "--interactive",
    help="Interactively review metadata before writing the contract.",
)
DESCRIPTION_OPTION = typer.Option(None, "--description", help="Override the description.")
DEFAULT_OPTION = typer.Option(None, "--default", help="Set a contract default value.")
EXAMPLE_OPTION = typer.Option(None, "--example", help="Set a contract example value.")
PATTERN_OPTION = typer.Option(None, "--pattern", help="Set a contract validation pattern.")
CHOICE_OPTION = typer.Option(
    None,
    "--choice",
    help="Add a choice value. Repeat the flag to provide multiple choices.",
)


def _resolve_required(required: bool, optional: bool) -> bool | None:
    """Resolve required/optional flags into one value."""
    if required and optional:
        raise typer.BadParameter("Use either --required or --optional, not both.")
    if required:
        return True
    if optional:
        return False
    return None


def _resolve_sensitive(sensitive: bool, non_sensitive: bool) -> bool | None:
    """Resolve sensitive/non-sensitive flags into one value."""
    if sensitive and non_sensitive:
        raise typer.BadParameter("Use either --sensitive or --non-sensitive, not both.")
    if sensitive:
        return True
    if non_sensitive:
        return False
    return None


def _parse_bool_scalar(value: str) -> bool:
    """Parse a string into a strict boolean scalar."""
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise typer.BadParameter("Boolean defaults must be one of: true, false, 1, 0, yes, no.")


def _coerce_default(value: str | None, variable_type: str) -> str | int | bool | None:
    """Coerce a CLI default string into the declared contract scalar."""
    if value is None:
        return None

    if variable_type == "int":
        try:
            return int(value)
        except ValueError as exc:
            raise typer.BadParameter("Default value must be a valid integer.") from exc

    if variable_type == "bool":
        return _parse_bool_scalar(value)

    return value


def _prompt_optional_field(label: str, default: str | None) -> str | None:
    """Prompt for an optional string field."""
    answer = typer_prompt(label, False, default).strip()
    return answer or None


def _prompt_choices(default: tuple[str, ...]) -> tuple[str, ...]:
    """Prompt for comma-separated choices."""
    default_text = ", ".join(default) if default else None
    answer = typer_prompt("Choices (comma-separated)", False, default_text).strip()
    if not answer:
        return default
    return tuple(part.strip() for part in answer.split(",") if part.strip())


def _build_request(
    *,
    key: str,
    value: str,
    interactive: bool,
    type_: str | None,
    required: bool,
    optional: bool,
    sensitive: bool,
    non_sensitive: bool,
    description: str | None,
    default: str | None,
    example: str | None,
    pattern: str | None,
    choice: list[str] | None,
) -> AddVariableRequest:
    """Build the final add request in the CLI layer."""
    override_required = _resolve_required(required, optional)
    override_sensitive = _resolve_sensitive(sensitive, non_sensitive)

    inferred = infer_spec(key, value)

    effective_type = type_ or inferred.type
    effective_required = inferred.required if override_required is None else override_required
    effective_sensitive = inferred.sensitive if override_sensitive is None else override_sensitive
    effective_description = inferred.description if description is None else description
    effective_default_raw = inferred.default if default is None else default
    effective_example = inferred.example if example is None else example
    effective_pattern = inferred.pattern if pattern is None else pattern
    effective_choices = inferred.choices if choice is None else tuple(choice)

    if interactive:
        effective_type = typer_prompt("Type", False, effective_type).strip() or effective_type
        effective_required = typer_confirm("Required?", default=effective_required)
        effective_sensitive = typer_confirm("Sensitive?", default=effective_sensitive)
        effective_description = _prompt_optional_field("Description", effective_description) or ""

        default_text = None if effective_default_raw is None else str(effective_default_raw)
        prompted_default = _prompt_optional_field("Default value", default_text)
        effective_default_raw = prompted_default

        effective_example = _prompt_optional_field("Example value", effective_example)
        effective_pattern = _prompt_optional_field("Validation pattern", effective_pattern)
        effective_choices = _prompt_choices(effective_choices)

    effective_default = (
        effective_default_raw
        if default is None and not interactive and not isinstance(effective_default_raw, str)
        else _coerce_default(
            None if effective_default_raw is None else str(effective_default_raw),
            effective_type,
        )
    )

    return AddVariableRequest(
        key=key,
        value=value,
        override_type=effective_type,
        override_required=effective_required,
        override_sensitive=effective_sensitive,
        override_description=effective_description,
        override_default=effective_default,
        override_example=effective_example,
        override_pattern=effective_pattern,
        override_choices=effective_choices,
    )


@handle_errors
def add_command(
    key: str = typer.Argument(...),
    value: str = typer.Argument(...),
    type_: str | None = TYPE_OPTION,
    required: bool = REQUIRED_OPTION,
    optional: bool = OPTIONAL_OPTION,
    sensitive: bool = SENSITIVE_OPTION,
    non_sensitive: bool = NON_SENSITIVE_OPTION,
    interactive: bool = INTERACTIVE_OPTION,
    description: str | None = DESCRIPTION_OPTION,
    default: str | None = DEFAULT_OPTION,
    example: str | None = EXAMPLE_OPTION,
    pattern: str | None = PATTERN_OPTION,
    choice: list[str] | None = CHOICE_OPTION,
) -> None:
    """Add or update one key in the local vault and contract."""
    request = _build_request(
        key=key,
        value=value,
        interactive=interactive,
        type_=type_,
        required=required,
        optional=optional,
        sensitive=sensitive,
        non_sensitive=non_sensitive,
        description=description,
        default=default,
        example=example,
        pattern=pattern,
        choice=choice,
    )

    context, result = run_add(request)

    print_success(f"Added '{key}' to contract and local vault")
    print_kv("vault_values", str(context.vault_values_path))
    print_kv("contract", str(context.repo_contract_path))

    if result.contract_created:
        print_kv("contract_created", "yes")

    if result.contract_updated:
        print_kv("contract_updated", "yes")

    if result.contract_entry_created:
        print_kv("contract_entry_created", "yes")

    if result.inferred_spec:
        if "type" in result.inferred_spec:
            print_kv("inferred_type", str(result.inferred_spec["type"]))
        if "required" in result.inferred_spec:
            print_kv("required", "yes" if result.inferred_spec["required"] else "no")
        if "sensitive" in result.inferred_spec:
            print_kv("sensitive", "yes" if result.inferred_spec["sensitive"] else "no")
        if result.inferred_spec.get("description"):
            print_kv("description", str(result.inferred_spec["description"]))

    if result.inferred_fields_used:
        print_kv("inferred_fields", ", ".join(result.inferred_fields_used))
        print_warning("Review .envctl.schema.yaml to confirm the inferred metadata.")