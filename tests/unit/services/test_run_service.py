from __future__ import annotations

import logging
from subprocess import CompletedProcess
from typing import Any

import pytest

import envctl.services.run_service as run_service
from envctl.domain.selection import group_selection
from envctl.errors import ExecutionError, ValidationError
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

    monkeypatch.setattr("envctl.services.run_service.subprocess.run", fake_run)

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
        "envctl.services.run_service.subprocess.run",
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

    monkeypatch.setattr("envctl.services.run_service.subprocess.run", fake_run)

    run_service.run_command(
        ["python3", "-V"],
        "staging",
        selection=group_selection("Application"),
    )

    env = captured["env"]
    assert isinstance(env, dict)
    assert env["APP_NAME"] == "demo"
    assert "DATABASE_URL" not in env or env["DATABASE_URL"] != "https://db.example.com"


def _patch_valid_run_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Any, Any]:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="profile",
            )
        }
    )

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

    return context, contract


def test_run_command_rejects_empty_command() -> None:
    with pytest.raises(ExecutionError, match="No command provided"):
        run_service.run_command([])


def test_run_command_wraps_os_error_from_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    def fake_run(
        command: list[str],
        check: bool = False,
        env: dict[str, str] | None = None,
    ) -> CompletedProcess[str]:
        raise OSError("boom")

    monkeypatch.setattr("envctl.services.run_service.subprocess.run", fake_run)

    with pytest.raises(ExecutionError, match=r"Failed to launch child process: python3"):
        run_service.run_command(["python3", "-V"], "dev")


@pytest.mark.parametrize(
    ("command", "expected_fragment"),
    [
        (
            ["docker", "run", "-e", "APP_NAME=demo", "aria-eventd:dev"],
            "Docker only injects variables into the container when they are forwarded explicitly",
        ),
        (
            ["docker", "run", "--env", "APP_NAME=demo", "aria-eventd:dev"],
            "Docker only injects variables into the container when they are forwarded explicitly",
        ),
        (
            ["docker", "run", "--env=APP_NAME=demo", "aria-eventd:dev"],
            "Docker only injects variables into the container when they are forwarded explicitly",
        ),
        (
            ["docker", "compose", "run", "app"],
            "envctl injected the resolved environment into the host-side docker process",
        ),
        (
            ["docker", "container", "run", "app"],
            "envctl injected the resolved environment into the host-side docker process",
        ),
    ],
)
def test_run_command_emits_expected_docker_warning_shapes(
    monkeypatch: pytest.MonkeyPatch,
    command: list[str],
    expected_fragment: str,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    monkeypatch.setattr(
        "envctl.services.run_service.subprocess.run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=0,
        ),
    )

    _context, result, _warnings = run_service.run_command(command, "dev")

    assert result.warnings
    assert expected_fragment in result.warnings[0]


@pytest.mark.parametrize(
    "command",
    [
        ["docker", "run", "--env-file", ".env", "aria-eventd:dev"],
        ["docker", "run", "--env-file=.env", "aria-eventd:dev"],
    ],
)
def test_run_command_skips_warning_for_explicit_env_file_handoff(
    monkeypatch: pytest.MonkeyPatch,
    command: list[str],
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    monkeypatch.setattr(
        "envctl.services.run_service.subprocess.run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=0,
        ),
    )

    _context, result, _warnings = run_service.run_command(command, "dev")

    assert result.warnings == ()


def test_run_command_logs_warning_for_docker_handoff(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    monkeypatch.setattr(
        "envctl.services.run_service.subprocess.run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=0,
        ),
    )

    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    caplog.set_level("WARNING")

    try:
        run_service.run_command(["docker", "run", "aria-eventd:dev"], "dev")
    finally:
        logger.removeHandler(caplog.handler)

    assert any(
        record.name == "envctl.services.run_service"
        and record.levelname == "WARNING"
        and record.message == "Run command produced docker environment handoff warning"
        and getattr(record, "warning_count", None) == 1
        for record in caplog.records
    )


def test_run_command_logs_info_lifecycle_with_sanitized_command(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    monkeypatch.setattr(
        "envctl.services.run_service.subprocess.run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=7,
        ),
    )

    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    logger.setLevel(logging.INFO)
    caplog.set_level("INFO")

    try:
        run_service.run_command(
            ["docker", "run", "API_KEY=supersecret", "aria-eventd:dev"],
            "dev",
        )
    finally:
        logger.removeHandler(caplog.handler)

    start = next(
        record
        for record in caplog.records
        if record.name == "envctl.services.run_service"
        and record.levelname == "INFO"
        and record.message == "Executing child process"
    )
    finish = next(
        record
        for record in caplog.records
        if record.name == "envctl.services.run_service"
        and record.levelname == "INFO"
        and record.message == "Child process completed"
    )
    assert getattr(start, "command", ()) == (
        "docker",
        "run",
        "API_KEY=su*********",
        "aria-eventd:dev",
    )
    assert getattr(finish, "exit_code", None) == 7


def test_run_command_logs_sanitized_error_context(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    def fake_run(
        command: list[str],
        check: bool = False,
        env: dict[str, str] | None = None,
    ) -> CompletedProcess[str]:
        raise OSError("boom")

    monkeypatch.setattr("envctl.services.run_service.subprocess.run", fake_run)
    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    caplog.set_level("ERROR")

    try:
        with pytest.raises(ExecutionError, match=r"Failed to launch child process: docker"):
            run_service.run_command(
                ["docker", "run", "API_KEY=supersecret", "aria-eventd:dev"],
                "dev",
            )
    finally:
        logger.removeHandler(caplog.handler)

    matching = [
        record
        for record in caplog.records
        if record.name == "envctl.services.run_service"
        and record.levelname == "ERROR"
        and record.message == "Failed to launch child process"
    ]
    assert matching
    logged_command = getattr(matching[0], "command", ())
    assert logged_command == (
        "docker",
        "run",
        "API_KEY=su*********",
        "aria-eventd:dev",
    )


def test_run_command_does_not_emit_warning_for_non_docker_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_valid_run_dependencies(monkeypatch)

    monkeypatch.setattr(
        "envctl.services.run_service.subprocess.run",
        lambda command, check=False, env=None: CompletedProcess(
            args=command,
            returncode=0,
        ),
    )

    _context, result, _warnings = run_service.run_command(["python3", "-V"], "dev")

    assert result.warnings == ()
