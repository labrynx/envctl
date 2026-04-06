from __future__ import annotations

from subprocess import CompletedProcess
from typing import Any

import pytest

import envctl.services.run_service as run_service
from envctl.domain.selection import group_selection
from envctl.errors import ValidationError
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec
from tests.support.projection_validation import raise_projection_error


def test_run_command_executes_child_with_resolved_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME"),
            "DATABASE_URL": make_variable_spec(name="DATABASE_URL"),
        }
    )
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="profile",
            ),
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
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, selection, operation: (
            contract,
            report,
            (),
        ),
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

    _context, result, warnings = run_service.run_command(["python3", "-V"], "staging")

    assert result.exit_code == 0
    assert warnings == ()
    assert captured["command"] == ["python3", "-V"]
    env = captured["env"]
    assert isinstance(env, dict)
    assert env["APP_NAME"] == "demo"
    assert env["DATABASE_URL"] == "https://db.example.com"


def test_run_command_rejects_invalid_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    filtered_report = make_resolution_report(missing_required=("DATABASE_URL",))

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, selection, operation: raise_projection_error(
            operation=operation,
            profile=active_profile,
            selection=selection,
            report=filtered_report,
            suggested_actions=("envctl fill", "envctl set KEY VALUE"),
        ),
    )

    with pytest.raises(ValidationError, match=r"Cannot run because"):
        run_service.run_command(["python3", "-V"], "dev")


def test_run_command_emits_docker_forwarding_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="profile",
            )
        }
    )
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, selection, operation: (
            contract,
            report,
            (),
        ),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=0,
        ),
    )

    _context, result, _warnings = run_service.run_command(
        ["docker", "run", "aria-eventd:dev"],
        "dev",
    )

    assert result.warnings
    assert "envctl injected the resolved environment" in result.warnings[0]


def test_run_command_injects_only_selected_group_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME", groups=("Application",)),
            "DATABASE_URL": make_variable_spec(
                name="DATABASE_URL",
                groups=("Secrets",),
            ),
        }
    )
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="profile",
            ),
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
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, selection, operation: (
            contract,
            report,
            (),
        ),
    )

    def fake_run(
        command: list[str],
        check: bool = False,
        env: dict[str, str] | None = None,
    ) -> CompletedProcess[str]:
        captured["env"] = env
        return CompletedProcess(args=command, returncode=0)

    monkeypatch.setattr(run_service.subprocess, "run", fake_run)

    run_service.run_command(
        ["python3", "-V"],
        "staging",
        selection=group_selection("Application"),
    )

    env = captured["env"]
    assert isinstance(env, dict)
    assert env["APP_NAME"] == "demo"
    assert "DATABASE_URL" not in env or env["DATABASE_URL"] != "https://db.example.com"
