from __future__ import annotations

from envctl.cli.formatters import render_doctor_checks, render_resolution, render_status
from envctl.domain.doctor import DoctorCheck
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.domain.status import StatusReport
from envctl.utils.masking import mask_value


def test_render_doctor_checks_outputs_known_prefixes_and_detects_failures(capsys) -> None:
    checks = [
        DoctorCheck("config", "ok", "config ok"),
        DoctorCheck("vault", "warn", "vault warn"),
        DoctorCheck("git", "fail", "git fail"),
        DoctorCheck("misc", "other", "misc info"),
    ]

    has_failures = render_doctor_checks(checks)

    captured = capsys.readouterr()
    output = captured.out

    assert has_failures is True
    assert "[OK] config: config ok" in output
    assert "[WARN] vault: vault warn" in output
    assert "[FAIL] git: git fail" in output
    assert "[INFO] misc: misc info" in output


def test_render_resolution_outputs_full_report(capsys) -> None:
    report = ResolutionReport(
        values={
            "API_KEY": ResolvedValue(
                key="API_KEY",
                value="super-secret",
                source="vault",
                masked=True,
                valid=True,
                detail=None,
            ),
            "PORT": ResolvedValue(
                key="PORT",
                value="abc",
                source="default",
                masked=False,
                valid=False,
                detail="Expected an integer",
            ),
        },
        missing_required=["DATABASE_URL"],
        unknown_keys=["LEGACY_KEY"],
        invalid_keys=["PORT"],
    )

    render_resolution(report)

    captured = capsys.readouterr()
    output = captured.out

    assert "Resolved values:" in output
    assert f"API_KEY = {mask_value('super-secret')} (vault)" in output
    assert "PORT = abc (default) [invalid: Expected an integer]" in output
    assert "Missing required keys:" in output
    assert "  - DATABASE_URL" in output
    assert "Invalid keys:" in output
    assert "  - PORT" in output
    assert "Unknown keys in vault:" in output
    assert "  - LEGACY_KEY" in output


def test_render_resolution_outputs_empty_state(capsys) -> None:
    report = ResolutionReport(
        values={},
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )

    render_resolution(report)

    captured = capsys.readouterr()
    assert captured.out.strip() == "No resolved values."


def test_render_status_outputs_summary_issues_and_action(capsys) -> None:
    report = StatusReport(
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root="/tmp/demo",
        contract_exists=True,
        vault_exists=False,
        resolved_valid=False,
        summary="The project contract is not satisfied yet.",
        issues=["Missing required keys: API_KEY", "Unknown keys in vault: OLD_KEY"],
        suggested_action="Run 'envctl fill'",
    )

    render_status(report)

    captured = capsys.readouterr()
    output = captured.out

    assert "Project: demo (prj_aaaaaaaaaaaaaaaa)" in output
    assert "Repository: /tmp/demo" in output
    assert "The project contract is not satisfied yet." in output
    assert "Contract present: yes" in output
    assert "Vault values present: no" in output
    assert "Resolved valid: no" in output
    assert "Issues:" in output
    assert "  - Missing required keys: API_KEY" in output
    assert "  - Unknown keys in vault: OLD_KEY" in output
    assert "Suggested action: Run 'envctl fill'" in output
