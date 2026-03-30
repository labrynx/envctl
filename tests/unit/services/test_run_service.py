from __future__ import annotations

from subprocess import CompletedProcess
from typing import Any

import pytest

import envctl.services.run_service as run_service
from envctl.errors import ExecutionError, ValidationError
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_run_command_executes_child_with_resolved_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile"),
            "DATABASE_URL": make_resolved_value(
                key="DATABASE_URL",
                value="https://db.example.com",
                source="profile",
                masked=True,
            ),
        },
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(run_service, "load_contract_for_context", lambda _context: object())
    monkeypatch.setattr(
        run_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    def fake_run(
        command: list[str],
        check: bool = False,
        env: dict[str, str] | None = None,
    ) -> CompletedProcess[str]:
        captured["command"] = command
        captured["env"] = env
        return CompletedProcess(args=command, returncode=0)

    monkeypatch.setattr(run_service.subprocess, "run", fake_run)

    _context, active_profile, exit_code = run_service.run_command(
        ["python3", "-V"],
        "staging",
    )

    assert active_profile == "staging"
    assert exit_code == 0
    assert captured["command"] == ["python3", "-V"]

    env = captured["env"]
    assert isinstance(env, dict)
    assert env["APP_NAME"] == "demo"
    assert env["DATABASE_URL"] == "https://db.example.com"


def test_run_command_rejects_missing_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ExecutionError, match="No command provided"):
        run_service.run_command([], "local")


def test_run_command_rejects_invalid_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(missing_required=("DATABASE_URL",))

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(run_service, "load_contract_for_context", lambda _context: object())
    monkeypatch.setattr(
        run_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    with pytest.raises(ValidationError, match="Environment contract is not satisfied"):
        run_service.run_command(["python3", "-V"], "dev")
