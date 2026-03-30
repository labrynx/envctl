from __future__ import annotations

from typing import Any, cast

import click

from envctl.cli.runtime import (
    CliState,
    get_active_profile,
    get_cli_state,
    get_output_format,
    is_json_output,
    set_cli_state,
)
from envctl.domain.runtime import OutputFormat


def test_get_cli_state_returns_default_when_no_context_exists() -> None:
    state = get_cli_state()

    assert state == CliState()
    assert state.output_format == OutputFormat.TEXT
    assert state.profile == "local"


def test_set_cli_state_persists_profile_and_output_format() -> None:
    ctx = click.Context(click.Command("envctl"))

    with ctx:
        set_cli_state(
            cast(Any, ctx),
            output_format=OutputFormat.JSON,
            profile="staging",
        )

        state = get_cli_state()

        assert state.output_format == OutputFormat.JSON
        assert state.profile == "staging"
        assert get_output_format() == OutputFormat.JSON
        assert is_json_output() is True
        assert get_active_profile() == "staging"


def test_get_cli_state_ignores_non_clistate_context_obj() -> None:
    ctx = click.Context(click.Command("envctl"))
    ctx.obj = {"not": "a CliState"}

    with ctx:
        state = get_cli_state()

    assert state == CliState()
    assert state.profile == "local"
