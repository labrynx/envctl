from __future__ import annotations

from types import SimpleNamespace

import envctl.cli.commands.init.command as init_command_module
from envctl.cli.commands.init import init_command
from envctl.services.init_service import InitResult


def test_typer_confirm_bridges_to_typer(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_confirm(message: str, default: bool) -> bool:
        captured["message"] = message
        captured["default"] = default
        return True

    monkeypatch.setattr(init_command_module.typer, "confirm", fake_confirm)

    result = init_command_module.typer_confirm("Proceed?", True)

    assert result is True
    assert captured == {
        "message": "Proceed?",
        "default": True,
    }


def test_init_command_prints_contract_creation_details(monkeypatch, capsys) -> None:
    context = SimpleNamespace(
        display_name="demo (prj_aaaaaaaaaaaaaaaa)",
        project_key="demo",
        binding_source="local",
        repo_root="/tmp/demo",
        repo_contract_path="/tmp/demo/.envctl.schema.yaml",
        vault_project_dir="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa",
        vault_values_path="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/values.env",
        vault_state_path="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/state.json",
    )
    init_result = InitResult(
        contract_created=True,
        contract_template="starter",
        contract_skipped=False,
    )

    monkeypatch.setattr(
        init_command_module,
        "run_init",
        lambda project_name=None, contract_mode="ask", confirm=None: (context, init_result),
    )

    init_command()

    output = capsys.readouterr().out
    assert "Initialized demo (prj_aaaaaaaaaaaaaaaa)" in output
    assert "project_key: demo" in output
    assert "binding_source: local" in output
    assert "repo_root: /tmp/demo" in output
    assert "contract: /tmp/demo/.envctl.schema.yaml" in output
    assert "vault_dir: /tmp/vault/demo--prj_aaaaaaaaaaaaaaaa" in output
    assert "vault_values: /tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/values.env" in output
    assert "vault_state: /tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/state.json" in output
    assert "contract_created: yes" in output
    assert "contract_template: starter" in output


def test_init_command_warns_when_contract_is_skipped(monkeypatch, capsys) -> None:
    context = SimpleNamespace(
        display_name="demo (prj_aaaaaaaaaaaaaaaa)",
        project_key="demo",
        binding_source="local",
        repo_root="/tmp/demo",
        repo_contract_path="/tmp/demo/.envctl.schema.yaml",
        vault_project_dir="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa",
        vault_values_path="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/values.env",
        vault_state_path="/tmp/vault/demo--prj_aaaaaaaaaaaaaaaa/state.json",
    )
    init_result = InitResult(
        contract_created=False,
        contract_template=None,
        contract_skipped=True,
    )

    monkeypatch.setattr(
        init_command_module,
        "run_init",
        lambda project_name=None, contract_mode="ask", confirm=None: (context, init_result),
    )

    init_command()

    output = capsys.readouterr().out
    assert "Initialized demo (prj_aaaaaaaaaaaaaaaa)" in output
    assert "project_key: demo" in output
    assert "binding_source: local" in output
    assert "No contract file was created" in output