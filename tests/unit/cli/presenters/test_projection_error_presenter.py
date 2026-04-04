from __future__ import annotations

import pytest

from envctl.cli.presenters.projection_error_presenter import (
    render_projection_validation_failure,
)
from envctl.services.projection_validation import ProjectionValidationDiagnostics
from tests.support.builders import make_resolution_report, make_resolved_value


def test_render_projection_validation_failure_renders_summary_problems_and_next_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    diagnostics = ProjectionValidationDiagnostics(
        operation="export",
        active_profile="staging",
        selected_group="Application",
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
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Error: Cannot export because the environment contract is not satisfied." in captured.err
    assert "profile: staging" in captured.err
    assert "group: Application" in captured.err
    assert "Missing required keys" in captured.err
    assert "DATABASE_URL" in captured.err
    assert "Invalid keys" in captured.err
    assert "PORT: Expected an integer" in captured.err
    assert "Unknown keys in vault for the current contract" in captured.err
    assert "OLD_KEY" in captured.err
    assert "Next steps" in captured.err
    assert "Run `envctl fill`" in captured.err
    assert "Run `envctl check`" in captured.err
