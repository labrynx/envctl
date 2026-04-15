"""Inspect command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import OutputFormat, present
from envctl.cli.presenters.common import merge_outputs
from envctl.cli.presenters.models import CommandOutput
from envctl.cli.presenters.outputs.inspect import (
    build_contract_group_output,
    build_contract_groups_summary_output,
    build_contract_set_output,
    build_contract_sets_summary_output,
    build_contracts_output,
    build_inspect_key_output,
    build_inspect_output,
)
from envctl.cli.presenters.outputs.warnings import (
    build_command_warnings_output,
    build_contract_deprecation_warnings_output,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning, InspectResult
from envctl.domain.selection import ContractSelection
from envctl.errors import ExecutionError


def _normalize_view_flags(
    contracts: bool,
    sets: bool,
    groups: bool,
) -> tuple[bool, bool, bool]:
    """Normalize inspect auxiliary view flags."""
    return (
        contracts if isinstance(contracts, bool) else False,
        sets if isinstance(sets, bool) else False,
        groups if isinstance(groups, bool) else False,
    )


def _get_auxiliary_views(
    contracts: bool,
    sets: bool,
    groups: bool,
) -> list[str]:
    """Return the enabled auxiliary inspect views."""
    return [
        name
        for name, enabled in (
            ("contracts", contracts),
            ("sets", sets),
            ("groups", groups),
        )
        if enabled
    ]


def _validate_inspect_arguments(
    key: str | None,
    selection: ContractSelection,
    auxiliary_views: list[str],
) -> None:
    """Validate mutually exclusive inspect arguments."""
    if key is not None and (selection.mode != "full" or auxiliary_views):
        raise ExecutionError(
            "Cannot combine `inspect KEY` with --group, --set, --var, "
            "--contracts, --sets, or --groups. "
            "Use either a positional key or one inspect scope/view option."
        )

    if len(auxiliary_views) > 1:
        raise ExecutionError(
            "Inspect view selectors are mutually exclusive: "
            "--contracts, --sets, and --groups cannot be used together."
        )


def _build_warning_output(
    *,
    contract_warnings: tuple[ContractDeprecationWarning, ...],
    command_warnings: tuple[CommandWarning, ...],
) -> CommandOutput | None:
    """Build one merged warnings output when needed."""
    outputs: list[CommandOutput] = []

    if contract_warnings:
        outputs.append(
            build_contract_deprecation_warnings_output(contract_warnings),
        )

    if command_warnings:
        outputs.append(
            build_command_warnings_output(command_warnings),
        )

    if not outputs:
        return None

    return merge_outputs(*outputs)


def _present_output(output: CommandOutput) -> None:
    """Render one command output using the active CLI format."""
    output_format: OutputFormat = "json" if is_json_output() else "text"
    present(output, output_format=output_format)


def _build_overview_output(
    inspect_result: InspectResult,
    *,
    contracts: bool,
    sets: bool,
    groups: bool,
    selection: ContractSelection,
) -> CommandOutput:
    """Build the selected inspect overview output."""
    if contracts:
        return build_contracts_output(inspect_result)

    if sets:
        return build_contract_sets_summary_output(inspect_result)

    if groups:
        return build_contract_groups_summary_output(inspect_result)

    if selection.mode == "set" and selection.set_name is not None:
        from envctl.services.inspect_service import ensure_known_contract_set

        ensure_known_contract_set(inspect_result, selection.set_name)
        return build_contract_set_output(inspect_result, selection.set_name)

    if selection.mode == "group" and selection.group is not None:
        from envctl.services.inspect_service import ensure_known_contract_group

        ensure_known_contract_group(inspect_result, selection.group)
        return build_contract_group_output(inspect_result, selection.group)

    return build_inspect_output(inspect_result)


def _handle_inspect_key(key: str) -> None:
    """Handle `inspect KEY`."""
    from envctl.services.inspect_service import run_inspect_key

    _context, key_result, contract_warnings = run_inspect_key(key, get_active_profile())

    main_output = build_inspect_key_output(key_result)
    warning_output = _build_warning_output(
        contract_warnings=tuple(contract_warnings),
        command_warnings=tuple(key_result.warnings),
    )

    output = (
        merge_outputs(warning_output, main_output) if warning_output is not None else main_output
    )
    _present_output(output)


def _handle_inspect_overview(
    *,
    contracts: bool,
    sets: bool,
    groups: bool,
    selection: ContractSelection,
) -> None:
    """Handle overview inspect views."""
    from envctl.services.inspect_service import run_inspect

    _context, inspect_result, contract_warnings = run_inspect(
        get_active_profile(),
        selection=selection,
    )

    main_output = _build_overview_output(
        inspect_result,
        contracts=contracts,
        sets=sets,
        groups=groups,
        selection=selection,
    )
    warning_output = _build_warning_output(
        contract_warnings=tuple(contract_warnings),
        command_warnings=tuple(inspect_result.warnings),
    )

    output = (
        merge_outputs(warning_output, main_output) if warning_output is not None else main_output
    )
    _present_output(output)


@handle_errors
def inspect_command(
    key: str | None = typer.Argument(None),
    contracts: bool = typer.Option(False, "--contracts", help="Show resolved contracts only."),
    sets: bool = typer.Option(False, "--sets", help="Show all resolved contract sets."),
    groups: bool = typer.Option(False, "--groups", help="Show all resolved contract groups."),
) -> None:
    """Inspect the resolved environment or one key in detail."""
    contracts, sets, groups = _normalize_view_flags(contracts, sets, groups)

    selection = get_contract_selection()
    auxiliary_views = _get_auxiliary_views(contracts, sets, groups)
    _validate_inspect_arguments(key, selection, auxiliary_views)

    if key is not None:
        _handle_inspect_key(key)
        return

    _handle_inspect_overview(
        contracts=contracts,
        sets=sets,
        groups=groups,
        selection=selection,
    )
