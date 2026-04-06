from __future__ import annotations

import pytest

from envctl.cli.presenters.projection_error_presenter import render_projection_validation_failure
from envctl.domain.selection import group_selection
from envctl.services.error_diagnostics import ProjectionValidationDiagnostics
from tests.support.builders import make_resolution_report, make_resolved_value


def test_render_projection_validation_failure_renders_summary_problems_and_next_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    diagnostics = ProjectionValidationDiagnostics(
        operation="export",
        active_profile="staging",
        selection=group_selection("Application"),
        report=make_resolution_report(
            missing_required=("DATABASE_URL",),
            invalid_keys=("PORT",),
            unknown_keys=("OLD_KEY",),
            values={
                "PORT": make_resolved_value(
                    key="PORT",
                    value="abc",
                    valid=False,
                    detail="Expected an integer",
                )
            },
        ),
        suggested_actions=("envctl fill", "envctl check"),
    )

    render_projection_validation_failure(
        diagnostics,
        message="Cannot export because the environment contract is not satisfied.",
    )
    captured = capsys.readouterr().err

    assert "Error: Cannot export because the environment contract is not satisfied." in captured
    assert "profile: staging" in captured
    assert "scope: group=Application" in captured
    assert "Missing required keys" in captured
    assert "Invalid keys" in captured
    assert "Unknown keys in vault for the current contract" in captured
    assert "Run `envctl fill`" in captured
