"""Inspect command."""

from __future__ import annotations

from collections.abc import Sequence

import typer

from envctl.cli.decorators import handle_errors
from envctl.cli.presenters import (
    render_contract_deprecation_warnings,
    render_contract_group_result,
    render_contract_groups_summary,
    render_contract_set_result,
    render_contract_sets_summary,
    render_contracts_result,
    render_inspect_key_result,
    render_inspect_result,
)
from envctl.cli.runtime import get_active_profile, get_contract_selection, is_json_output
from envctl.cli.serializers import (
    emit_json,
    serialize_command_warnings,
    serialize_contract_deprecation_warnings,
    serialize_inspect_key_result,
    serialize_inspect_result,
)
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import InspectKeyResult, InspectResult
from envctl.domain.selection import ContractSelection
from envctl.errors import ExecutionError
from envctl.services.inspect_service import (
    ensure_known_contract_group,
    ensure_known_contract_set,
    run_inspect,
    run_inspect_key,
)


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


def _emit_inspect_key_json(
    key_result: InspectKeyResult,
    warnings: Sequence[ContractDeprecationWarning],
) -> None:
    """Emit JSON output for `inspect KEY`."""
    emit_json(
        {
            "ok": True,
            "command": "inspect",
            "data": {
                **serialize_inspect_key_result(key_result),
                "warnings": serialize_contract_deprecation_warnings(warnings)
                + serialize_command_warnings(key_result.warnings),
            },
        }
    )


def _emit_inspect_json(
    inspect_result: InspectResult,
    warnings: Sequence[ContractDeprecationWarning],
) -> None:
    """Emit JSON output for `inspect`."""
    emit_json(
        {
            "ok": True,
            "command": "inspect",
            "data": {
                **serialize_inspect_result(inspect_result),
                "warnings": serialize_contract_deprecation_warnings(warnings)
                + serialize_command_warnings(inspect_result.warnings),
            },
        }
    )


def _render_inspect_terminal_view(
    inspect_result: InspectResult,
    *,
    contracts: bool,
    sets: bool,
    groups: bool,
    selection: ContractSelection,
) -> None:
    """Render the selected terminal inspect view."""
    if contracts:
        render_contracts_result(inspect_result)
        return

    if sets:
        render_contract_sets_summary(inspect_result)
        return

    if groups:
        render_contract_groups_summary(inspect_result)
        return

    if selection.mode == "set" and selection.set_name is not None:
        ensure_known_contract_set(inspect_result, selection.set_name)
        render_contract_set_result(inspect_result, selection.set_name)
        return

    if selection.mode == "group" and selection.group is not None:
        ensure_known_contract_group(inspect_result, selection.group)
        render_contract_group_result(inspect_result, selection.group)
        return

    render_inspect_result(inspect_result)


def _handle_inspect_key(key: str) -> None:
    """Handle `inspect KEY`."""
    _context, key_result, warnings = run_inspect_key(key, get_active_profile())

    if is_json_output():
        _emit_inspect_key_json(key_result, warnings)
        return

    if warnings:
        render_contract_deprecation_warnings(warnings)

    render_inspect_key_result(key_result)


def _handle_inspect_overview(
    *,
    contracts: bool,
    sets: bool,
    groups: bool,
    selection: ContractSelection,
) -> None:
    """Handle overview inspect views."""
    _context, inspect_result, warnings = run_inspect(
        get_active_profile(),
        selection=selection,
    )

    if is_json_output():
        _emit_inspect_json(inspect_result, warnings)
        return

    if warnings:
        render_contract_deprecation_warnings(warnings)

    _render_inspect_terminal_view(
        inspect_result,
        contracts=contracts,
        sets=sets,
        groups=groups,
        selection=selection,
    )


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
