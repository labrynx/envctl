from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import click
import pytest
import typer

import envctl.cli.commands.hook_run.command as hook_run_command_module
import envctl.cli.commands.hooks.command as hooks_command_module
from envctl.cli.commands.hook_run import hook_run_command
from envctl.domain.hooks import (
    HookAction,
    HookInspectionResult,
    HookName,
    HookOperationReport,
    HookOperationResult,
    HooksStatusLevel,
    HooksStatusReport,
    HookStatus,
)
from tests.support.contexts import make_project_context

hooks_install_command = hooks_command_module.hooks_install_command
hooks_remove_command = hooks_command_module.hooks_remove_command
hooks_repair_command = hooks_command_module.hooks_repair_command
hooks_status_command = hooks_command_module.hooks_status_command


def _make_status_report(status: HookStatus) -> HooksStatusReport:
    overall = (
        HooksStatusLevel.HEALTHY
        if status == HookStatus.HEALTHY
        else HooksStatusLevel.CONFLICT
        if status in {HookStatus.FOREIGN, HookStatus.UNSUPPORTED}
        else HooksStatusLevel.DEGRADED
    )
    return HooksStatusReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        overall_status=overall,
        results=(
            HookInspectionResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                status=status,
                managed=status != HookStatus.FOREIGN,
                is_executable=True,
            ),
        ),
    )


def _make_operation_report(final_status: HooksStatusLevel) -> HookOperationReport:
    return HookOperationReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        final_status=final_status,
        changed=final_status != HooksStatusLevel.CONFLICT,
        results=(
            HookOperationResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                before_status=HookStatus.MISSING,
                after_status=(
                    HookStatus.HEALTHY
                    if final_status == HooksStatusLevel.HEALTHY
                    else HookStatus.FOREIGN
                ),
                action=(
                    HookAction.CREATED
                    if final_status == HooksStatusLevel.HEALTHY
                    else HookAction.SKIPPED_FOREIGN
                ),
                changed=final_status == HooksStatusLevel.HEALTHY,
                managed=final_status == HooksStatusLevel.HEALTHY,
            ),
        ),
    )


def test_hooks_status_command_renders_text_and_exits_non_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    called: dict[str, Any] = {}

    monkeypatch.setattr(
        hooks_command_module,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hooks_command_module,
        "HookService",
        lambda repo_root: SimpleNamespace(
            get_status=lambda: _make_status_report(HookStatus.MISSING)
        ),
    )
    monkeypatch.setattr(hooks_command_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        hooks_command_module,
        "render_hooks_status",
        lambda report, *, repo_root: called.update({"report": report, "repo_root": repo_root}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        hooks_status_command()

    assert exc_info.value.exit_code == 1
    assert called["repo_root"] == context.repo_root
    assert cast(HooksStatusReport, called["report"]).overall_status == HooksStatusLevel.DEGRADED


def test_hooks_status_command_emits_json_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        hooks_command_module,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hooks_command_module,
        "HookService",
        lambda repo_root: SimpleNamespace(
            get_status=lambda: _make_status_report(HookStatus.HEALTHY)
        ),
    )
    monkeypatch.setattr(hooks_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(hooks_command_module, "emit_json", lambda payload: captured.update(payload))

    with pytest.raises(typer.Exit) as exc_info:
        hooks_status_command()

    assert exc_info.value.exit_code == 0
    assert captured["ok"] is True
    assert captured["command"] == "hooks status"
    assert captured["schema_version"] == 1
    assert captured["data"]["overall_status"] == "healthy"


@pytest.mark.parametrize(
    ("command", "method_name", "operation_name", "json_mode", "final_status", "force"),
    [
        (hooks_install_command, "install", "install", True, HooksStatusLevel.HEALTHY, True),
        (hooks_repair_command, "repair", "repair", True, HooksStatusLevel.CONFLICT, False),
        (hooks_repair_command, "repair", "repair", False, HooksStatusLevel.CONFLICT, False),
        (hooks_remove_command, "remove", "remove", True, HooksStatusLevel.HEALTHY, None),
        (hooks_remove_command, "remove", "remove", False, HooksStatusLevel.HEALTHY, None),
    ],
)
def test_hooks_mutation_commands_cover_json_and_text_paths(
    monkeypatch: pytest.MonkeyPatch,
    command: Any,
    method_name: str,
    operation_name: str,
    json_mode: bool,
    final_status: HooksStatusLevel,
    force: bool | None,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    captured: dict[str, Any] = {}
    rendered: dict[str, Any] = {}

    monkeypatch.setattr(
        hooks_command_module,
        "load_project_context",
        lambda: (SimpleNamespace(runtime_warnings=("warn",)), context),
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode="local"),
    )

    def _build_service(_repo_root: Path) -> SimpleNamespace:
        report = _make_operation_report(final_status)
        return SimpleNamespace(**{method_name: lambda **_kwargs: report})

    monkeypatch.setattr(hooks_command_module, "HookService", _build_service)
    monkeypatch.setattr(hooks_command_module, "is_json_output", lambda: json_mode)
    monkeypatch.setattr(hooks_command_module, "emit_json", lambda payload: captured.update(payload))
    monkeypatch.setattr(
        hooks_command_module,
        "render_hook_operation",
        lambda report, *, repo_root, operation_name: rendered.update(
            {"report": report, "repo_root": repo_root, "operation_name": operation_name}
        ),
    )

    action = (lambda: command()) if force is None else (lambda: command(force=force))

    with pytest.raises(typer.Exit) as exc_info:
        action()

    expected_exit = 0 if final_status == HooksStatusLevel.HEALTHY else 1
    assert exc_info.value.exit_code == expected_exit
    if json_mode:
        assert captured["command"] == f"hooks {operation_name}"
        assert captured["schema_version"] == 1
        assert captured["ok"] is (expected_exit == 0)
    else:
        assert rendered["operation_name"] == operation_name
        assert rendered["repo_root"] == context.repo_root


def test_hook_run_command_success_path(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
    monkeypatch.setattr(
        hook_run_command_module,
        "HookExecutionService",
        lambda: SimpleNamespace(
            run_guarded_hook=lambda hook_name, argv: SimpleNamespace(
                exit_code=0,
                guard_result=SimpleNamespace(ok=True, scanned_paths=(Path("a"),), findings=()),
            )
        ),
    )
    ctx = typer.Context(click.Command("hook-run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command(ctx, "pre-commit")

    assert exc_info.value.exit_code == 0
    output = capsys.readouterr().out
    assert "No staged envctl secrets detected" in output
    assert "scanned_paths: 1" in output


def test_hook_run_command_failure_path_prints_findings(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
    finding = SimpleNamespace(path=".env", message="secret detected", actions=("remove secret",))
    monkeypatch.setattr(
        hook_run_command_module,
        "HookExecutionService",
        lambda: SimpleNamespace(
            run_guarded_hook=lambda hook_name, argv: SimpleNamespace(
                exit_code=1,
                guard_result=SimpleNamespace(ok=False, scanned_paths=(), findings=(finding,)),
            )
        ),
    )
    ctx = typer.Context(click.Command("hook-run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command(ctx, "pre-push")

    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert ".env: secret detected" in captured.err
    assert "action: remove secret" in captured.out


def test_hook_run_command_rejects_unsupported_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_handled_error",
        lambda exc, *, json_output, command: captured.update(
            {"message": str(exc), "json_output": json_output, "command": command}
        ),
    )
    monkeypatch.setattr("envctl.cli.decorators.get_command_path", lambda: "hook-run")
    ctx = typer.Context(click.Command("hook-run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command(ctx, "post-merge")

    assert exc_info.value.exit_code == 1
    assert captured["message"] == "Unsupported hook: post-merge"
