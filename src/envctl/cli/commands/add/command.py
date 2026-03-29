"""Add command."""

from __future__ import annotations

import typer

from envctl.cli.callbacks import typer_confirm, typer_prompt
from envctl.cli.decorators import handle_errors
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
    override_required = _resolve_required(required, optional)
    override_sensitive = _resolve_sensitive(sensitive, non_sensitive)
    override_choices = tuple(choice) if choice else None

    context, result = run_add(
        key=key,
        value=value,
        interactive=interactive,
        prompt=typer_prompt,
        confirm=typer_confirm,
        override_type=type_,
        override_required=override_required,
        override_sensitive=override_sensitive,
        override_description=description,
        override_default=default,
        override_example=example,
        override_pattern=pattern,
        override_choices=override_choices,
    )

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
        if "description" in result.inferred_spec and result.inferred_spec["description"]:
            print_kv("description", str(result.inferred_spec["description"]))

    print_warning("Review .envctl.schema.yaml to confirm the inferred metadata.")
