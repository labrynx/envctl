from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import click
import pytest
import typer

import envctl.cli.commands.hook.commands.run as hook_run_command_module
import envctl.cli.commands.hooks.commands.install as hooks_install_module
import envctl.cli.commands.hooks.commands.remove as hooks_remove_module
import envctl.cli.commands.hooks.commands.repair as hooks_repair_module
import envctl.cli.commands.hooks.commands.status as hooks_status_module
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

hooks_install_command = hooks_install_module.hooks_install_command
hooks_remove_command = hooks_remove_module.hooks_remove_command
hooks_repair_command = hooks_repair_module.hooks_repair_command
hooks_status_command = hooks_status_module.hooks_status_command


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


def test_hooks_status_command_renders_output_and_exits_non_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        hooks_status_module,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hooks_status_module,
        "HookService",
        lambda repo_root: SimpleNamespace(
            get_status=lambda: _make_status_report(HookStatus.MISSING)
        ),
    )
    monkeypatch.setattr(hooks_status_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        hooks_status_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        hooks_status_command()

    assert exc_info.value.exit_code == 1
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["kind"] == "hooks_status"
    assert captured["output"].metadata["overall_status"] == "degraded"
    assert captured["output"].metadata["ok"] is False


def test_hooks_status_command_emits_presenter_json_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        hooks_status_module,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hooks_status_module,
        "HookService",
        lambda repo_root: SimpleNamespace(
            get_status=lambda: _make_status_report(HookStatus.HEALTHY)
        ),
    )
    monkeypatch.setattr(hooks_status_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        hooks_status_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        hooks_status_command()

    assert exc_info.value.exit_code == 0
    assert captured["output_format"] == "json"
    assert captured["output"].metadata["kind"] == "hooks_status"
    assert captured["output"].metadata["overall_status"] == "healthy"
    assert captured["output"].metadata["ok"] is True


@pytest.mark.parametrize(
    (
        "module",
        "command",
        "method_name",
        "operation_name",
        "json_mode",
        "final_status",
        "force",
    ),
    [
        (
            hooks_install_module,
            hooks_install_command,
            "install",
            "install",
            True,
            HooksStatusLevel.HEALTHY,
            True,
        ),
        (
            hooks_repair_module,
            hooks_repair_command,
            "repair",
            "repair",
            True,
            HooksStatusLevel.CONFLICT,
            False,
        ),
        (
            hooks_repair_module,
            hooks_repair_command,
            "repair",
            "repair",
            False,
            HooksStatusLevel.CONFLICT,
            False,
        ),
        (
            hooks_remove_module,
            hooks_remove_command,
            "remove",
            "remove",
            True,
            HooksStatusLevel.HEALTHY,
            None,
        ),
        (
            hooks_remove_module,
            hooks_remove_command,
            "remove",
            "remove",
            False,
            HooksStatusLevel.HEALTHY,
            None,
        ),
    ],
)
def test_hooks_mutation_commands_cover_json_and_text_paths(
    monkeypatch: pytest.MonkeyPatch,
    module: Any,
    command: Any,
    method_name: str,
    operation_name: str,
    json_mode: bool,
    final_status: HooksStatusLevel,
    force: bool | None,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        module,
        "load_project_context",
        lambda: (SimpleNamespace(runtime_warnings=("warn",)), context),
    )
    monkeypatch.setattr(
        "envctl.services.context_service.load_project_context",
        lambda: (SimpleNamespace(runtime_warnings=("warn",)), context),
    )
    monkeypatch.setattr(
        "envctl.config.loader.load_config",
        lambda: SimpleNamespace(runtime_mode="local"),
    )

    def _build_service(_repo_root: Path) -> SimpleNamespace:
        report = _make_operation_report(final_status)
        return SimpleNamespace(**{method_name: lambda **_kwargs: report})

    monkeypatch.setattr(module, "HookService", _build_service)
    monkeypatch.setattr("envctl.services.hook_service.HookService", _build_service)
    monkeypatch.setattr(module, "is_json_output", lambda: json_mode)
    monkeypatch.setattr(
        module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    action = (lambda: command()) if force is None else (lambda: command(force=force))

    with pytest.raises(typer.Exit) as exc_info:
        action()

    expected_exit = 0 if final_status == HooksStatusLevel.HEALTHY else 1
    assert exc_info.value.exit_code == expected_exit
    assert captured["output_format"] == ("json" if json_mode else "text")
    assert captured["output"].metadata["kind"] == "hooks_operation"
    assert captured["output"].metadata["operation_name"] == operation_name
    assert captured["output"].metadata["overall_status"] == final_status.value
    assert captured["output"].metadata["ok"] is (final_status != HooksStatusLevel.CONFLICT)


def test_hook_run_command_success_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.services.hook_service.HookExecutionService",
        lambda: SimpleNamespace(
            run_guarded_hook=lambda hook_name, argv: SimpleNamespace(
                exit_code=0,
                guard_result=SimpleNamespace(ok=True, scanned_paths=(Path("a"),), findings=()),
            )
        ),
    )
    monkeypatch.setattr(
        hook_run_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    ctx = typer.Context(click.Command("hook run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command_module.hook_run_command(ctx, "pre-commit")

    assert exc_info.value.exit_code == 0
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["kind"] == "hook_run"
    assert captured["output"].metadata["hook_name"] == "pre-commit"
    assert captured["output"].metadata["exit_code"] == 0


def test_hook_run_command_failure_path_captures_findings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    finding = SimpleNamespace(
        path=".env", kind="secret", message="secret detected", actions=("remove secret",)
    )

    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.services.hook_service.HookExecutionService",
        lambda: SimpleNamespace(
            run_guarded_hook=lambda hook_name, argv: SimpleNamespace(
                exit_code=1,
                guard_result=SimpleNamespace(ok=False, scanned_paths=(), findings=(finding,)),
            )
        ),
    )
    monkeypatch.setattr(
        hook_run_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    ctx = typer.Context(click.Command("hook run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command_module.hook_run_command(ctx, "pre-commit")

    assert exc_info.value.exit_code == 1
    assert captured["output_format"] == "text"
    assert captured["output"].metadata["kind"] == "hook_run"
    assert captured["output"].metadata["exit_code"] == 1
    assert captured["output"].metadata["findings"][0]["message"] == "secret detected"


def test_hook_run_command_rejects_unsupported_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.cli.runtime.get_command_path",
        lambda: "hook run",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_handled_error",
        lambda exc, *, output_format, command: captured.update(
            {
                "message": str(exc),
                "output_format": output_format,
                "command": command,
            }
        ),
    )

    ctx = typer.Context(click.Command("hook run"))
    ctx.args = []

    with pytest.raises(typer.Exit) as exc_info:
        hook_run_command_module.hook_run_command(ctx, "post-merge")

    assert exc_info.value.exit_code == 1
    assert captured["message"] == "Unsupported hook: post-merge"
    assert captured["command"] == "hook run"
