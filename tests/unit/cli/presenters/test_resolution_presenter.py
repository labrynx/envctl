"""Tests for resolution presenters."""

from __future__ import annotations

import pytest

from envctl.cli.presenters.resolution_presenter import (
    render_resolution,
    render_resolution_view,
)
from tests.support.builders import make_resolution_report, make_resolved_value


def test_render_resolution_view_includes_profile_and_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """It should render the profile header and resolution sections."""
    report = make_resolution_report(
        missing_required=("DATABASE_URL",),
        invalid_keys=("PORT",),
        unknown_keys=("LEGACY_KEY",),
        values={
            "PORT": make_resolved_value(
                key="PORT",
                value="abc",
                masked=False,
                source="vault",
                valid=False,
                detail="Expected an integer",
            ),
            "TOKEN": make_resolved_value(
                key="TOKEN",
                value="supersecret",
                masked=True,
                source="system",
            ),
        },
    )

    render_resolution_view(profile="prod", report=report)
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "Missing required keys" in captured
    assert "DATABASE_URL" in captured
    assert "Invalid keys" in captured
    assert "PORT: Expected an integer" in captured
    assert "Unknown keys in vault" in captured
    assert "LEGACY_KEY" in captured
    assert "Resolved values" in captured
    assert "TOKEN = su*********" in captured
    assert "(system)" in captured


def test_render_resolution_handles_empty_values(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render an empty resolved values block cleanly."""
    report = make_resolution_report()

    render_resolution(report)
    captured = capsys.readouterr().out

    assert "Resolved values" in captured
    assert "  None" in captured
    assert "Missing required keys" not in captured
    assert "Invalid keys" not in captured
    assert "Unknown keys in vault" not in captured
