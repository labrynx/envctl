from __future__ import annotations

from types import SimpleNamespace

import pytest

import envctl.services.run_service as run_service
from envctl.errors import ExecutionError, ValidationError
from envctl.services.run_service import run_command
from tests.support.builders import make_resolution_report, make_resolved_value


def test_run_command_fails_when_command_is_empty() -> None:
    with pytest.raises(ExecutionError, match="A command is required after '--'"):
        run_command([])


def test_run_command_fails_when_resolved_environment_is_invalid(monkeypatch) -> None:
    context = SimpleNamespace()
    contract = object()
    report = make_resolution_report(missing_required=["API_KEY"])

    monkeypatch.setattr(run_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(run_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(run_service, "resolve_environment", lambda _context, _contract: report)

    with pytest.raises(ValidationError, match="resolved environment is invalid"):
        run_command(["python", "-V"])


def test_run_command_executes_subprocess_with_injected_environment(monkeypatch) -> None:
    context = SimpleNamespace()
    contract = object()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="vault",
                valid=True,
            ),
            "DATABASE_URL": make_resolved_value(
                key="DATABASE_URL",
                value="https://db.example.com",
                source="system",
                masked=True,
                valid=True,
            ),
        }
    )

    captured: dict[str, object] = {}

    def fake_run(command, env, check):
        captured["command"] = command
        captured["env"] = env
        captured["check"] = check
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(run_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(run_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(run_service, "resolve_environment", lambda _context, _contract: report)
    monkeypatch.setattr(run_service.subprocess, "run", fake_run)
    monkeypatch.setenv("EXISTING_VAR", "keep-me")

    returncode = run_command(["python", "-V"])

    assert returncode == 7
    assert captured["command"] == ["python", "-V"]
    assert captured["check"] is False

    env = captured["env"]
    assert env["EXISTING_VAR"] == "keep-me"
    assert env["APP_NAME"] == "demo"
    assert env["DATABASE_URL"] == "https://db.example.com"
