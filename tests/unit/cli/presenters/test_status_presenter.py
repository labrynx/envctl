"""Tests for status presenters."""

from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.status_presenter import (
    render_status,
    render_status_view,
)
from envctl.domain.status import StatusReport


def test_render_status_view_with_issues_and_next_step(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render profile, issues, and next step when present."""
    report = StatusReport(
        project_slug="demo-app",
        project_id="prj_1234567890ab",
        repo_root=Path("/workspace/demo-app"),
        contract_exists=False,
        vault_exists=True,
        resolved_valid=False,
        summary="The project contract is not satisfied yet.",
        issues=["Contract file is missing", "Missing required keys: DATABASE_URL"],
        suggested_action="Run 'envctl init' or create .envctl.yaml",
    )

    render_status_view(profile="local", report=report)
    captured = capsys.readouterr().out

    assert "profile: local" in captured
    assert "Status" in captured
    assert "state: action needed" in captured
    assert "name: demo-app" in captured
    assert "id: prj_1234567890ab" in captured
    assert "contract: missing" in captured
    assert "vault values: present" in captured
    assert "resolution: invalid" in captured
    assert "Issues" in captured
    assert "Contract file is missing" in captured
    assert "Next step" in captured
    assert "Run 'envctl init' or create .envctl.yaml" in captured


def test_render_status_without_issues(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render a healthy status without issues or next step sections."""
    report = StatusReport(
        project_slug="demo-app",
        project_id="prj_1234567890ab",
        repo_root=Path("/workspace/demo-app"),
        contract_exists=True,
        vault_exists=True,
        resolved_valid=True,
        summary="The project contract is satisfied and the environment can be projected safely.",
        issues=[],
        suggested_action=None,
    )

    render_status(report)
    captured = capsys.readouterr().out

    assert "state: healthy" in captured
    assert "Issues" not in captured
    assert "Next step" not in captured
