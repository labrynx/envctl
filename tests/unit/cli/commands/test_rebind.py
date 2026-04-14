from __future__ import annotations

from types import SimpleNamespace

import pytest
import typer

import envctl.cli.commands.project.commands.rebind as rebind_command_module
from envctl.domain.operations import RebindResult
from envctl.domain.runtime import RuntimeMode


def test_rebind_command_aborts_when_confirmation_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    confirm_calls: list[tuple[str, bool]] = []
    run_calls: list[bool] = []

    def fake_confirm(message: str, default: bool) -> bool:
        confirm_calls.append((message, default))
        return False

    def fake_run_rebind(*, copy_values: bool = True) -> tuple[object, object]:
        run_calls.append(copy_values)
        raise AssertionError("run_rebind should not be called when confirmation is rejected")

    monkeypatch.setattr(rebind_command_module, "confirm", fake_confirm)
    monkeypatch.setattr("envctl.services.rebind_service.run_rebind", fake_run_rebind)

    rebind_command_module.project_rebind_command(yes=False)

    output = capsys.readouterr().out
    assert "Nothing was changed." in output
    assert len(confirm_calls) == 1
    assert "generate a new project identity" in confirm_calls[0][0]
    assert confirm_calls[0][1] is False
    assert run_calls == []


def test_rebind_command_skips_confirmation_when_yes_is_true(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    confirm_calls: list[tuple[str, bool]] = []

    context = SimpleNamespace(
        display_name="demo (prj_bbbbbbbbbbbbbbbb)",
        repo_root="/tmp/demo",
        vault_project_dir="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb",
        vault_values_path="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb/values.env",
    )
    result = RebindResult(
        previous_project_id="prj_aaaaaaaaaaaaaaaa",
        new_project_id="prj_bbbbbbbbbbbbbbbb",
        copied_values=True,
    )

    def fake_confirm(message: str, default: bool) -> bool:
        confirm_calls.append((message, default))
        return True

    monkeypatch.setattr(rebind_command_module, "confirm", fake_confirm)
    monkeypatch.setattr(
        "envctl.services.rebind_service.run_rebind",
        lambda *, copy_values=True: (context, result),
    )

    rebind_command_module.project_rebind_command(yes=True)

    output = capsys.readouterr().out
    assert "Rebound repository to demo (prj_bbbbbbbbbbbbbbbb)" in output
    assert confirm_calls == []


def test_rebind_command_prints_rebind_details_with_previous_project_id(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(
        display_name="demo (prj_bbbbbbbbbbbbbbbb)",
        repo_root="/tmp/demo",
        vault_project_dir="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb",
        vault_values_path="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb/values.env",
    )
    result = RebindResult(
        previous_project_id="prj_aaaaaaaaaaaaaaaa",
        new_project_id="prj_bbbbbbbbbbbbbbbb",
        copied_values=True,
    )

    monkeypatch.setattr(
        rebind_command_module,
        "confirm",
        lambda message, default: True,
    )
    monkeypatch.setattr(
        "envctl.services.rebind_service.run_rebind",
        lambda *, copy_values=True: (context, result),
    )

    rebind_command_module.project_rebind_command(copy_values=True, yes=False)

    output = capsys.readouterr().out
    assert "Rebound repository to demo (prj_bbbbbbbbbbbbbbbb)" in output
    assert "previous_project_id: prj_aaaaaaaaaaaaaaaa" in output
    assert "new_project_id: prj_bbbbbbbbbbbbbbbb" in output
    assert "copied_values: yes" in output
    assert "repo_root: /tmp/demo" in output
    assert "vault_dir: /tmp/vault/demo--prj_bbbbbbbbbbbbbbbb" in output
    assert "vault_values: /tmp/vault/demo--prj_bbbbbbbbbbbbbbbb/values.env" in output


def test_rebind_command_prints_no_copy_when_values_are_not_copied(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(
        display_name="demo (prj_bbbbbbbbbbbbbbbb)",
        repo_root="/tmp/demo",
        vault_project_dir="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb",
        vault_values_path="/tmp/vault/demo--prj_bbbbbbbbbbbbbbbb/values.env",
    )
    result = RebindResult(
        previous_project_id=None,
        new_project_id="prj_bbbbbbbbbbbbbbbb",
        copied_values=False,
    )

    monkeypatch.setattr(
        "envctl.services.rebind_service.run_rebind",
        lambda *, copy_values=True: (context, result),
    )

    rebind_command_module.project_rebind_command(copy_values=False, yes=True)

    output = capsys.readouterr().out
    assert "new_project_id: prj_bbbbbbbbbbbbbbbb" in output
    assert "copied_values: no" in output
    assert "previous_project_id:" not in output


def test_rebind_command_rejects_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.config.loader.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )
    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.print_error",
        lambda message: captured.update({"message": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        rebind_command_module.project_rebind_command(yes=True)

    assert exc_info.value.exit_code == 1
    assert "CI read-only mode" in captured["message"]
