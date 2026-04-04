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
                source="vault",
            ),
        },
    )

    render_resolution_view(profile="prod", group="Application", report=report)
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "group: Application" in captured
    assert "Missing required keys" in captured
    assert "DATABASE_URL" in captured
    assert "Invalid keys" in captured
    assert "PORT: Expected an integer" in captured
    assert "Unknown keys in vault" in captured
    assert "LEGACY_KEY" in captured
    assert "Resolved values" in captured
    assert "TOKEN = su*********" in captured
    assert "(vault)" in captured


def test_render_resolution_view_marks_expanded_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = make_resolution_report(
        values={
            "AUTH": make_resolved_value(
                key="AUTH",
                value="neo4j/secret",
                masked=False,
                source="vault",
                expansion_status="expanded",
                expansion_refs=("USER", "PASSWORD"),
            ),
        }
    )

    render_resolution_view(profile="local", group=None, report=report)
    captured = capsys.readouterr().out

    assert "AUTH = neo4j/secret (vault) [expanded: USER, PASSWORD]" in captured


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
