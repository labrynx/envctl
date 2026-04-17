from __future__ import annotations

import pytest

from envctl.cli.presenters.formatters import (
    render_action_state,
    render_present_missing,
    render_valid_invalid,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "action needed"),
        (False, "healthy"),
    ],
)
def test_render_action_state(value: bool, expected: str) -> None:
    assert render_action_state(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "present"),
        (False, "missing"),
    ],
)
def test_render_present_missing(value: bool, expected: str) -> None:
    assert render_present_missing(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "valid"),
        (False, "invalid"),
    ],
)
def test_render_valid_invalid(value: bool, expected: str) -> None:
    assert render_valid_invalid(value) == expected
