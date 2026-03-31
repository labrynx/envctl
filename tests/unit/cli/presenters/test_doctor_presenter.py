"""Tests for doctor presenters."""

from __future__ import annotations

from types import SimpleNamespace

from envctl.cli.presenters.doctor_presenter import render_doctor_checks


def test_render_doctor_checks_only_healthy(capsys: object) -> None:
    """It should render a healthy doctor summary and no failures."""
    checks = [
        SimpleNamespace(name="runtime_mode", status="ok", detail="Runtime mode: local"),
        SimpleNamespace(name="project", status="ok", detail="Resolved project: demo"),
    ]

    has_failures = render_doctor_checks(checks)
    captured = capsys.readouterr().out

    assert has_failures is False
    assert "Doctor summary" in captured
    assert "failures: 0" in captured
    assert "warnings: 0" in captured
    assert "healthy: 2" in captured
    assert "Healthy checks" in captured
    assert "[OK] runtime_mode: Runtime mode: local" in captured
    assert "[OK] project: Resolved project: demo" in captured


def test_render_doctor_checks_with_warning(capsys: object) -> None:
    """It should render warnings in the warnings section."""
    checks = [
        SimpleNamespace(
            name="vault_permissions",
            status="warn",
            detail="Vault directory does not exist yet",
        ),
        SimpleNamespace(
            name="binding_source",
            status="ok",
            detail="Binding source: local",
        ),
    ]

    has_failures = render_doctor_checks(checks)
    captured = capsys.readouterr().out

    assert has_failures is False
    assert "warnings: 1" in captured
    assert "healthy: 1" in captured
    assert "Warnings" in captured
    assert "[WARN] vault_permissions: Vault directory does not exist yet" in captured
    assert "Healthy checks" in captured


def test_render_doctor_checks_with_failure(capsys: object) -> None:
    """It should report failures and return True."""
    checks = [
        SimpleNamespace(
            name="project",
            status="fail",
            detail="Project binding is invalid",
        ),
        SimpleNamespace(
            name="vault_profile",
            status="warn",
            detail="Profile vault file does not exist yet",
        ),
    ]

    has_failures = render_doctor_checks(checks)
    captured = capsys.readouterr().out

    assert has_failures is True
    assert "failures: 1" in captured
    assert "warnings: 1" in captured
    assert "healthy: 0" in captured
    assert "Failures" in captured
    assert "[FAIL] project: Project binding is invalid" in captured
    assert "Warnings" in captured
    assert "[WARN] vault_profile: Profile vault file does not exist yet" in captured
