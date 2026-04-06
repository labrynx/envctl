"""Tests for resolution presenters."""

from __future__ import annotations

import pytest

from envctl.cli.presenters.resolution_presenter import (
    render_resolution,
    render_resolution_view,
)
from envctl.domain.selection import ContractSelection, group_selection
from tests.support.builders import make_resolution_report, make_resolved_value


def test_render_resolution_view_includes_profile_scope_and_sections(
    capsys: pytest.CaptureFixture[str],
) -> None:
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

    render_resolution_view(
        profile="prod",
        selection=group_selection("Application"),
        report=report,
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "scope: group=Application" in captured
    assert "Missing required keys" in captured
    assert "Invalid keys" in captured
    assert "Unknown keys in vault" in captured


def test_render_resolution_view_uses_full_contract_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_resolution_view(
        profile="local",
        selection=ContractSelection(),
        report=make_resolution_report(),
    )
    captured = capsys.readouterr().out
    assert "scope: full contract" in captured


def test_render_resolution_renders_expansion_details(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = make_resolution_report(
        values={
            "AUTH": make_resolved_value(
                key="AUTH",
                value="user:password",
                source="vault",
                masked=True,
                expansion_status="expanded",
                expansion_refs=("USER", "PASSWORD"),
            )
        }
    )

    render_resolution(report)
    captured = capsys.readouterr().out
    assert "expanded: USER, PASSWORD" in captured
