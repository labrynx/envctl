from __future__ import annotations

from typing import Any, cast

import click

from envctl.cli.runtime import (
    CliState,
    get_active_profile,
    get_cli_state,
    get_contract_selection,
    get_output_format,
    get_profile_observability,
    get_selected_group,
    get_selected_set,
    get_selected_var,
    get_trace_enabled,
    get_trace_file,
    get_trace_format,
    get_trace_output,
    is_error_debug_enabled,
    is_json_output,
    set_cli_state,
)
from envctl.domain.runtime import OutputFormat


def test_get_cli_state_returns_default_when_no_context_exists() -> None:
    state = get_cli_state()

    assert state == CliState()
    assert state.output_format == OutputFormat.TEXT
    assert state.requested_profile is None


def test_set_cli_state_persists_profile_output_and_selection() -> None:
    ctx = click.Context(click.Command("envctl"))

    with ctx:
        set_cli_state(
            cast(Any, ctx),
            output_format=OutputFormat.JSON,
            requested_profile="staging",
            requested_group="Application",
            requested_set_name=None,
            requested_variable=None,
            trace_enabled=True,
            trace_format="human",
            trace_output="both",
            trace_file=None,
            profile_observability=True,
            debug_errors=True,
        )

        state = get_cli_state()

        assert state.output_format == OutputFormat.JSON
        assert state.requested_profile == "staging"
        assert state.requested_group == "Application"
        assert get_output_format() == OutputFormat.JSON
        assert is_json_output() is True
        assert get_active_profile() == "staging"
        assert get_selected_group() == "Application"
        assert get_selected_set() is None
        assert get_selected_var() is None
        assert get_trace_enabled() is True
        assert get_trace_format() == "human"
        assert get_trace_output() == "both"
        assert get_trace_file() is None
        assert get_profile_observability() is True
        assert is_error_debug_enabled() is True
        assert get_contract_selection().describe() == "group=Application"


def test_get_cli_state_ignores_non_clistate_context_obj() -> None:
    ctx = click.Context(click.Command("envctl"))
    ctx.obj = {"not": "a CliState"}

    with ctx:
        state = get_cli_state()

    assert state == CliState()
    assert state.requested_profile is None
