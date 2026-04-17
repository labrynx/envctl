from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import envctl.cli.commands.project.commands.bind as bind_command_module
import envctl.cli.commands.project.commands.repair as repair_command_module
import envctl.cli.commands.project.commands.unbind as unbind_command_module
from envctl.domain.operations import BindResult, RepairResult, UnbindResult
from envctl.domain.runtime import RuntimeMode
from tests.support.contexts import make_project_context


def _enable_writable_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "envctl.config.loader.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.LOCAL),
    )


def test_project_bind_command_builds_success_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    context = make_project_context(
        project_slug="demo-app",
        project_key="demo-app",
        project_id="prj_bbbbbbbbbbbbbbbb",
        binding_source="local",
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.bind_service.run_bind",
        lambda project_id: (
            context,
            BindResult(project_id=project_id, changed=True),
        ),
    )
    monkeypatch.setattr(bind_command_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        bind_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    bind_command_module.project_bind_command("prj_bbbbbbbbbbbbbbbb")

    output = captured["output"]
    assert captured["output_format"] == "text"
    assert output.metadata["kind"] == "project_bind"
    assert output.metadata["changed"] is True
    assert output.metadata["project_key"] == "demo-app"
    assert output.metadata["project_id"] == "prj_bbbbbbbbbbbbbbbb"
    assert output.metadata["binding_source"] == "local"
    assert output.messages[0].level == "success"
    assert "Bound repository to demo-app" in output.messages[0].text


def test_project_bind_command_builds_warning_when_binding_is_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    context = make_project_context(
        project_slug="demo-app",
        project_key="demo-app",
        project_id="prj_bbbbbbbbbbbbbbbb",
        binding_source="local",
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.bind_service.run_bind",
        lambda project_id: (
            context,
            BindResult(project_id=project_id, changed=False),
        ),
    )
    monkeypatch.setattr(bind_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        bind_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    bind_command_module.project_bind_command("prj_bbbbbbbbbbbbbbbb")

    output = captured["output"]
    assert captured["output_format"] == "json"
    assert output.metadata["changed"] is False
    assert output.messages[0].level == "warning"
    assert "already bound" in output.messages[0].text


def test_project_repair_command_builds_success_output_with_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    context = make_project_context(
        project_slug="demo-app",
        project_id="prj_cccccccccccccccc",
        binding_source="local",
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.repair_service.run_repair",
        lambda *, create_if_missing=False, recreate_bound_vault=False: (
            context,
            RepairResult(
                status="recreated",
                detail="Recreated bound vault for demo-app.",
                project_id="prj_cccccccccccccccc",
            ),
        ),
    )
    monkeypatch.setattr(repair_command_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        repair_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    repair_command_module.project_repair_command(
        create_if_missing=True,
        recreate_bound_vault=True,
    )

    output = captured["output"]
    assert captured["output_format"] == "text"
    assert output.metadata["kind"] == "project_repair"
    assert output.metadata["status"] == "recreated"
    assert output.metadata["project_id"] == "prj_cccccccccccccccc"
    assert output.metadata["binding_source"] == "local"
    assert output.messages[0].level == "success"
    assert "Recreated bound vault" in output.messages[0].text
    assert output.sections


def test_project_repair_command_builds_warning_output_without_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.repair_service.run_repair",
        lambda *, create_if_missing=False, recreate_bound_vault=False: (
            None,
            RepairResult(
                status="needs_action",
                detail="Run envctl project rebind to recover the repository identity.",
                project_id="prj_dddddddddddddddd",
            ),
        ),
    )
    monkeypatch.setattr(repair_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        repair_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    repair_command_module.project_repair_command()

    output = captured["output"]
    assert captured["output_format"] == "json"
    assert output.metadata["status"] == "needs_action"
    assert output.metadata["project_id"] == "prj_dddddddddddddddd"
    assert output.metadata["binding_source"] is None
    assert output.messages[0].level == "warning"
    assert "rebind" in output.messages[0].text
    assert len(output.sections) == 1
    assert output.sections[0].items[0].text == "project_id"


def test_project_unbind_command_builds_success_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    context = make_project_context(repo_root="/tmp/demo-unbind")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.unbind_service.run_unbind",
        lambda: (
            context.repo_root,
            UnbindResult(removed=True, previous_project_id="prj_aaaaaaaaaaaaaaaa"),
        ),
    )
    monkeypatch.setattr(unbind_command_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        unbind_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    unbind_command_module.project_unbind_command()

    output = captured["output"]
    assert captured["output_format"] == "text"
    assert output.metadata["kind"] == "project_unbind"
    assert output.metadata["removed"] is True
    assert output.metadata["previous_project_id"] == "prj_aaaaaaaaaaaaaaaa"
    assert output.messages[0].level == "success"
    assert "Removed local repository binding" in output.messages[0].text


def test_project_unbind_command_builds_warning_output_when_binding_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_writable_runtime(monkeypatch)
    context = make_project_context(repo_root="/tmp/demo-unbind")
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.unbind_service.run_unbind",
        lambda: (
            context.repo_root,
            UnbindResult(removed=False, previous_project_id=None),
        ),
    )
    monkeypatch.setattr(unbind_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        unbind_command_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    unbind_command_module.project_unbind_command()

    output = captured["output"]
    assert captured["output_format"] == "json"
    assert output.metadata["removed"] is False
    assert output.metadata["previous_project_id"] is None
    assert output.messages[0].level == "warning"
    assert "No local repository binding was present" in output.messages[0].text
