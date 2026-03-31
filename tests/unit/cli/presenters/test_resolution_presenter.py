"""Tests for resolution presenters."""

from __future__ import annotations

from types import SimpleNamespace

from envctl.cli.presenters.resolution_presenter import (
    render_resolution,
    render_resolution_view,
)


def test_render_resolution_view_includes_profile_and_sections(
    capsys: object,
) -> None:
    """It should render the profile header and resolution sections."""
    report = SimpleNamespace(
        missing_required=["DATABASE_URL"],
        invalid_keys=["PORT"],
        unknown_keys=["LEGACY_KEY"],
        values={
            "PORT": SimpleNamespace(
                value="abc",
                masked=False,
                source="vault",
                valid=False,
                detail="Expected an integer",
            ),
            "TOKEN": SimpleNamespace(
                value="supersecret",
                masked=True,
                source="system",
                valid=True,
                detail=None,
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


def test_render_resolution_handles_empty_values(capsys: object) -> None:
    """It should render an empty resolved values block cleanly."""
    report = SimpleNamespace(
        missing_required=[],
        invalid_keys=[],
        unknown_keys=[],
        values={},
    )

    render_resolution(report)
    captured = capsys.readouterr().out

    assert "Resolved values" in captured
    assert "  None" in captured
    assert "Missing required keys" not in captured
    assert "Invalid keys" not in captured
    assert "Unknown keys in vault" not in captured
