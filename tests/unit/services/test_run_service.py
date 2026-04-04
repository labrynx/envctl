from __future__ import annotations

from subprocess import CompletedProcess
from typing import Any

import pytest

import envctl.services.run_service as run_service
from envctl.errors import ExecutionError, ValidationError
from envctl.services.projection_validation import ProjectionValidationDiagnostics
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec
from tests.support.projection_validation import raise_projection_error


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
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
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

    _context, result = run_service.run_command(["python3", "-V"], "staging")

    assert result.active_profile == "staging"
    assert result.exit_code == 0
    assert result.warnings == ()
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
    filtered_report = make_resolution_report(missing_required=("DATABASE_URL",))

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (
            raise_projection_error(
                operation=operation,
                profile=active_profile,
                group=group,
                report=filtered_report,
                suggested_actions=("envctl fill", "envctl set KEY VALUE"),
            )
        ),
    )

    with pytest.raises(ValidationError, match="Cannot run because") as exc_info:
        run_service.run_command(["python3", "-V"], "dev")

    assert exc_info.value.diagnostics == ProjectionValidationDiagnostics(
        operation="run",
        active_profile="dev",
        selected_group=None,
        report=filtered_report,
        suggested_actions=("envctl fill", "envctl set KEY VALUE"),
    )


def test_run_command_warns_for_docker_run_without_env_forwarding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(args=command, returncode=0),
    )

    _context, result = run_service.run_command(["docker", "run", "aria-eventd:dev"], "dev")

    assert result.warnings == (
        "envctl injected the resolved environment into the host-side docker process, not "
        "the container. Forward required container variables explicitly with -e, --env, "
        "or --env-file. For container workflows, prefer an explicit env-file handoff "
        "such as 'docker run --env-file <(envctl export --format dotenv) my-image'.",
    )


def test_run_command_warns_for_docker_container_run_without_env_forwarding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(args=command, returncode=0),
    )

    _context, result = run_service.run_command(
        ["docker", "container", "run", "aria-eventd:dev"],
        "dev",
    )

    assert result.warnings == (
        "envctl injected the resolved environment into the host-side docker process, not "
        "the container. Forward required container variables explicitly with -e, --env, "
        "or --env-file. For container workflows, prefer an explicit env-file handoff "
        "such as 'docker run --env-file <(envctl export --format dotenv) my-image'.",
    )


def test_run_command_warns_for_docker_compose_run_without_env_forwarding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(args=command, returncode=0),
    )

    _context, result = run_service.run_command(["docker", "compose", "run", "app"], "dev")

    assert result.warnings == (
        "envctl injected the resolved environment into the host-side docker process, not "
        "the container. Forward required container variables explicitly with -e, --env, "
        "or --env-file. For container workflows, prefer an explicit env-file handoff "
        "such as 'docker run --env-file <(envctl export --format dotenv) my-image'.",
    )


@pytest.mark.parametrize(
    "command",
    [
        ["docker", "run", "-e", "APP_NAME", "aria-eventd:dev"],
        ["docker", "run", "-e", "APP_NAME=demo", "aria-eventd:dev"],
        ["docker", "run", "--env", "APP_NAME", "aria-eventd:dev"],
        ["docker", "run", "--env", "APP_NAME=demo", "aria-eventd:dev"],
        ["docker", "run", "--env=APP_NAME", "aria-eventd:dev"],
    ],
)
def test_run_command_warns_when_docker_env_forwarding_is_partial(
    monkeypatch: pytest.MonkeyPatch,
    command: list[str],
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(args=command, returncode=0),
    )

    _context, result = run_service.run_command(command, "dev")

    assert result.warnings == (
        "Docker only injects variables into the container when they are forwarded "
        "explicitly with -e, --env, or --env-file. Other envctl-resolved values stay "
        "in the host-side docker client process unless you forward them too. "
        "For container workflows, prefer an explicit env-file handoff such as "
        "'docker run --env-file <(envctl export --format dotenv) my-image'.",
    )


@pytest.mark.parametrize(
    "command",
    [
        ["docker", "run", "--env-file", ".env.local", "aria-eventd:dev"],
        ["docker", "run", "--env-file=.env.local", "aria-eventd:dev"],
    ],
)
def test_run_command_skips_warning_when_docker_env_file_is_used(
    monkeypatch: pytest.MonkeyPatch,
    command: list[str],
) -> None:
    context = make_project_context()
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (object(), report),
    )
    monkeypatch.setattr(
        run_service.subprocess,
        "run",
        lambda command, check=False, env=None: CompletedProcess(args=command, returncode=0),
    )

    _context, result = run_service.run_command(command, "dev")

    assert result.warnings == ()


def test_run_command_injects_only_selected_group_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME", group="Application"),
            "DATABASE_URL": make_variable_spec(name="DATABASE_URL", group="Secrets"),
        }
    )
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
        missing_required=("DATABASE_URL",),
        unknown_keys=("OLD_KEY",),
        invalid_keys=("DATABASE_URL",),
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(run_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        run_service,
        "resolve_projectable_environment",
        lambda _context, *, active_profile, group, operation: (contract, report),
    )

    def fake_run(
        command: list[str],
        check: bool = False,
        env: dict[str, str] | None = None,
    ) -> CompletedProcess[str]:
        captured["env"] = env
        return CompletedProcess(args=command, returncode=0)

    monkeypatch.setattr(run_service.subprocess, "run", fake_run)

    run_service.run_command(["python3", "-V"], "staging", group="Application")

    env = captured["env"]
    assert isinstance(env, dict)
    assert env["APP_NAME"] == "demo"
    assert "DATABASE_URL" not in env
