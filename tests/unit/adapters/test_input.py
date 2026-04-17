"""Tests for input adapter behavior."""

from __future__ import annotations

import typer

from envctl.cli.decorators import (
    handle_errors,
    requires_writable_runtime,
    text_output_only,
)
from envctl.cli.presenters.outputs.actions import build_add_output, build_inferred_spec_output
from envctl.cli.prompts.input import confirm, prompt_string
from envctl.cli.runtime import get_active_profile
from envctl.domain.operations import AddVariableRequest
from envctl.services.add_service import run_add

KEY_ARGUMENT = typer.Argument(...)
VALUE_ARGUMENT = typer.Argument(...)
TYPE_OPTION = typer.Option(None, "--type")
REQUIRED_OPTION = typer.Option(False, "--required")
OPTIONAL_OPTION = typer.Option(False, "--optional")
SENSITIVE_OPTION = typer.Option(False, "--sensitive")
NON_SENSITIVE_OPTION = typer.Option(False, "--non-sensitive")
INTERACTIVE_OPTION = typer.Option(False, "--interactive")
DESCRIPTION_OPTION = typer.Option(None, "--description")
DEFAULT_OPTION = typer.Option(None, "--default")
EXAMPLE_OPTION = typer.Option(None, "--example")
PATTERN_OPTION = typer.Option(None, "--pattern")
CHOICE_OPTION = typer.Option(None, "--choice")


def _resolve_required(required: bool, optional: bool) -> bool | None:
    """Resolve required/optional flags."""
    if required and optional:
        raise typer.BadParameter("Use either --required or --optional, not both.")
    if required:
        return True
    if optional:
        return False
    return None


def _resolve_sensitive(sensitive: bool, non_sensitive: bool) -> bool | None:
    """Resolve sensitive/non-sensitive flags."""
    if sensitive and non_sensitive:
        raise typer.BadParameter("Use either --sensitive or --non-sensitive, not both.")
    if sensitive:
        return True
    if non_sensitive:
        return False
    return None


def _collect_interactive_overrides(
    *,
    type_: str | None,
    description: str | None,
    override_required: bool | None,
    override_sensitive: bool | None,
    default: str | None,
    example: str | None,
    pattern: str | None,
    choice: list[str] | None,
) -> tuple[
    str | None,
    str | None,
    bool | None,
    bool | None,
    str | None,
    str | None,
    str | None,
    list[str],
]:
    """Collect interactive metadata overrides."""
    resolved_type = prompt_string("Variable type", default=type_ or "string")
    resolved_description = prompt_string("Description", default=description or "")

    resolved_required = override_required
    if resolved_required is None:
        resolved_required = confirm("Required?", default=True)

    resolved_sensitive = override_sensitive
    if resolved_sensitive is None:
        resolved_sensitive = confirm("Sensitive?", default=False)

    resolved_default = prompt_string("Default value", default=default or "")
    resolved_example = prompt_string("Example", default=example or "")
    resolved_pattern = prompt_string("Pattern", default=pattern or "")
    choices_text = prompt_string(
        "Choices (comma-separated)",
        default=", ".join(choice or []),
    )
    resolved_choices = [item.strip() for item in choices_text.split(",") if item.strip()]

    return (
        resolved_type,
        resolved_description,
        resolved_required,
        resolved_sensitive,
        resolved_default,
        resolved_example,
        resolved_pattern,
        resolved_choices,
    )


def _build_add_request(
    *,
    key: str,
    value: str,
    type_: str | None,
    required: bool,
    optional: bool,
    sensitive: bool,
    non_sensitive: bool,
    interactive: bool,
    description: str | None,
    default: str | None,
    example: str | None,
    pattern: str | None,
    choice: list[str] | None,
) -> AddVariableRequest:
    """Build the add request payload."""
    override_required = _resolve_required(required, optional)
    override_sensitive = _resolve_sensitive(sensitive, non_sensitive)

    resolved_type = type_
    resolved_description = description
    resolved_default = default
    resolved_example = example
    resolved_pattern = pattern
    resolved_choice = choice or []

    if interactive:
        (
            resolved_type,
            resolved_description,
            override_required,
            override_sensitive,
            resolved_default,
            resolved_example,
            resolved_pattern,
            resolved_choice,
        ) = _collect_interactive_overrides(
            type_=type_,
            description=description,
            override_required=override_required,
            override_sensitive=override_sensitive,
            default=default,
            example=example,
            pattern=pattern,
            choice=choice,
        )

    return AddVariableRequest(
        key=key,
        value=value,
        override_type=resolved_type,
        override_required=override_required,
        override_sensitive=override_sensitive,
        override_description=resolved_description,
        override_default=resolved_default or None,
        override_example=resolved_example or None,
        override_pattern=resolved_pattern or None,
        override_choices=tuple(resolved_choice),
    )


@handle_errors
@requires_writable_runtime("add")
@text_output_only("add")
def add_command(
    key: str = KEY_ARGUMENT,
    value: str = VALUE_ARGUMENT,
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
    """Add one variable to the contract and store its initial value in the active profile."""
    request = _build_add_request(
        key=key,
        value=value,
        type_=type_,
        required=required,
        optional=optional,
        sensitive=sensitive,
        non_sensitive=non_sensitive,
        interactive=interactive,
        description=description,
        default=default,
        example=example,
        pattern=pattern,
        choice=choice,
    )

    context, result = run_add(request, get_active_profile())

    build_add_output(
        key=key,
        profile=result.active_profile,
        profile_path=result.profile_path,
        contract_path=context.repo_contract_path,
        contract_created=result.contract_created,
        contract_updated=result.contract_updated,
        contract_entry_created=result.contract_entry_created,
    )
    build_inferred_spec_output(result.inferred_spec)
