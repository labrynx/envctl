from __future__ import annotations

from typing import Any, cast

import pytest

import envctl.cli.commands.inspect.command as inspect_command_module
from envctl.cli.commands.inspect import inspect_command
from tests.support.builders import make_resolution_report
from tests.support.contexts import make_project_context


def test_inspect_command_renders_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=(),
        unknown_keys=(),
        invalid_keys=(),
    )
    called: dict[str, Any] = {}

    monkeypatch.setattr(
        inspect_command_module,
        "run_inspect",
        lambda profile: (context, "staging", report),
    )
    monkeypatch.setattr(
        inspect_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        inspect_command_module,
        "render_resolution_view",
        lambda *, profile, report: called.update({"profile": profile, "report": report}),
    )
    monkeypatch.setattr(
        inspect_command_module,
        "is_json_output",
        lambda: False,
    )

    inspect_command()

    assert called["profile"] == "staging"
    assert called["report"] is report


def test_inspect_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    report = make_resolution_report(
        values={},
        missing_required=("DATABASE_URL",),
        unknown_keys=("OLD_KEY",),
        invalid_keys=("PORT",),
    )
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        inspect_command_module,
        "run_inspect",
        lambda profile: (context, "staging", report),
    )
    monkeypatch.setattr(
        inspect_command_module,
        "get_active_profile",
        lambda: "staging",
    )
    monkeypatch.setattr(
        inspect_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        inspect_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    inspect_command()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is True
    assert payload["command"] == "inspect"
    assert payload["data"]["active_profile"] == "staging"
    assert payload["data"]["context"]["project_slug"] == "demo"
    assert payload["data"]["report"]["missing_required"] == ["DATABASE_URL"]
    assert payload["data"]["report"]["unknown_keys"] == ["OLD_KEY"]
    assert payload["data"]["report"]["invalid_keys"] == ["PORT"]
