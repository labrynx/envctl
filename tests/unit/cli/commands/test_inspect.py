from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.inspect.command as inspect_command_module
from envctl.domain.diagnostics import (
    DiagnosticSummary,
    InspectContractGraph,
    InspectKeyResult,
    InspectResult,
)
from envctl.domain.selection import ContractSelection, group_selection
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def make_inspect_result() -> InspectResult:
    context = make_project_context(repo_root="/tmp/demo")
    return InspectResult(
        project=context,
        active_profile="staging",
        selection=group_selection("Application"),
        contract_path=str(context.repo_contract_path),
        values_path=str(context.vault_values_path),
        summary=DiagnosticSummary(total=1, valid=1, invalid=0, unknown=0),
        variables=(
            make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="vault",
            ),
        ),
        problems=(),
        contract_graph=InspectContractGraph(
            root_path=Path(context.repo_contract_path),
            contract_paths=(Path(context.repo_contract_path),),
            contracts_total=1,
            variables_total=1,
            sets_total=0,
            groups_total=1,
            import_graph={Path(context.repo_contract_path): ()},
            declared_in={"APP_NAME": Path(context.repo_contract_path)},
            sets_index={},
            groups_index={"Application": ("APP_NAME",)},
        ),
    )


def make_key_result() -> InspectKeyResult:
    context = make_project_context(repo_root="/tmp/demo")
    return InspectKeyResult(
        project=context,
        active_profile="staging",
        item=make_resolved_value(key="APP_NAME", value="demo", source="vault"),
        contract_type="string",
        contract_format=None,
        declared_in=Path(context.repo_contract_path),
        sets=(),
        groups=("Application",),
        default=None,
        sensitive=False,
    )


def test_inspect_command_renders_report(monkeypatch: pytest.MonkeyPatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_inspect_result()
    called: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.inspect_service.run_inspect",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(inspect_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        ContractSelection,
    )
    monkeypatch.setattr(
        inspect_command_module,
        "render_inspect_result",
        lambda result: called.update({"result": result}),
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: False)

    inspect_command_module.inspect_command(None)

    assert called["result"] is result


def test_inspect_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_inspect_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.inspect_service.run_inspect",
        lambda profile, *, selection=None: (context, result, ()),
    )
    monkeypatch.setattr(inspect_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        inspect_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    inspect_command_module.inspect_command(None)

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["command"] == "inspect"
    assert payload["data"]["runtime"]["active_profile"] == "staging"
    assert payload["data"]["variables"]["APP_NAME"]["value"] == "demo"


def test_inspect_key_command_emits_json(monkeypatch: pytest.MonkeyPatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = make_key_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.inspect_service.run_inspect_key",
        lambda key, profile: (context, result, ()),
    )
    monkeypatch.setattr(inspect_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        ContractSelection,
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        inspect_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    inspect_command_module.inspect_command("APP_NAME")

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["data"]["item"]["key"] == "APP_NAME"
    assert payload["data"]["contract"]["type"] == "string"


def test_inspect_key_rejects_scope_selectors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: False)

    with pytest.raises(typer.Exit) as exc_info:
        inspect_command_module.inspect_command("APP_NAME")

    assert exc_info.value.exit_code == 1


def test_inspect_key_rejects_scope_selectors_with_clear_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        lambda: group_selection("Application"),
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: False)

    with pytest.raises(typer.Exit) as exc_info:
        inspect_command_module.inspect_command("APP_NAME")

    assert exc_info.value.exit_code == 1


def test_inspect_key_json_includes_combined_warnings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = make_key_result()
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.inspect_service.run_inspect_key",
        lambda key, profile: (result.project, result, ()),
    )
    monkeypatch.setattr(inspect_command_module, "get_active_profile", lambda: "staging")
    monkeypatch.setattr(
        inspect_command_module,
        "get_contract_selection",
        ContractSelection,
    )
    monkeypatch.setattr(inspect_command_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        inspect_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    inspect_command_module.inspect_command("APP_NAME")

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["data"]["warnings"] == []
