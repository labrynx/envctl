from __future__ import annotations

from types import SimpleNamespace

import pytest
import typer

import envctl.cli.commands.add.command as add_command_module
from envctl.domain.operations import AddVariableRequest


def test_resolve_required_returns_true_when_required() -> None:
    assert add_command_module._resolve_required(True, False) is True


def test_resolve_required_returns_false_when_optional() -> None:
    assert add_command_module._resolve_required(False, True) is False


def test_resolve_required_returns_none_when_no_flags() -> None:
    assert add_command_module._resolve_required(False, False) is None


def test_resolve_required_raises_when_both_flags_are_set() -> None:
    with pytest.raises(typer.BadParameter, match="--required or --optional"):
        add_command_module._resolve_required(True, True)


def test_resolve_sensitive_returns_true_when_sensitive() -> None:
    assert add_command_module._resolve_sensitive(True, False) is True


def test_resolve_sensitive_returns_false_when_non_sensitive() -> None:
    assert add_command_module._resolve_sensitive(False, True) is False


def test_resolve_sensitive_returns_none_when_no_flags() -> None:
    assert add_command_module._resolve_sensitive(False, False) is None


def test_resolve_sensitive_raises_when_both_flags_are_set() -> None:
    with pytest.raises(typer.BadParameter, match="--sensitive or --non-sensitive"):
        add_command_module._resolve_sensitive(True, True)


def test_add_command_calls_service_and_prints_full_inference(monkeypatch, capsys) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.schema.yaml",
    )
    result = SimpleNamespace(
        contract_created=True,
        contract_updated=True,
        contract_entry_created=True,
        inferred_spec={
            "type": "url",
            "required": True,
            "sensitive": True,
            "description": "Primary database connection URL",
        },
    )

    prompts = iter(
        [
            "url",
            "Primary database connection URL",
            "",
            "postgres://user:pass@localhost:5432/app",
            "^postgres://",
            "a, b",
        ]
    )
    confirms = iter([True, True])

    monkeypatch.setattr(
        add_command_module,
        "typer_prompt",
        lambda _message, _secret, _default: next(prompts),
    )
    monkeypatch.setattr(
        add_command_module,
        "typer_confirm",
        lambda _message, default=False: next(confirms),
    )

    captured: dict[str, object] = {}

    def fake_run_add(request: AddVariableRequest):
        captured["request"] = request
        return context, result

    monkeypatch.setattr(add_command_module, "run_add", fake_run_add)

    add_command_module.add_command(
        key="DATABASE_URL",
        value="postgres://user:pass@localhost:5432/app",
        type_="url",
        required=True,
        optional=False,
        sensitive=True,
        non_sensitive=False,
        interactive=True,
        description="Primary database connection URL",
        default=None,
        example="postgres://user:pass@localhost:5432/app",
        pattern="^postgres://",
        choice=["a", "b"],
    )

    output = capsys.readouterr().out
    request = captured["request"]

    assert isinstance(request, AddVariableRequest)
    assert request.key == "DATABASE_URL"
    assert request.value == "postgres://user:pass@localhost:5432/app"
    assert request.override_type == "url"
    assert request.override_required is True
    assert request.override_sensitive is True
    assert request.override_description == "Primary database connection URL"
    assert request.override_default is None
    assert request.override_example == "postgres://user:pass@localhost:5432/app"
    assert request.override_pattern == "^postgres://"
    assert request.override_choices == ("a", "b")

    assert "[OK] Added 'DATABASE_URL' to contract and local vault" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "contract: /tmp/repo/.envctl.schema.yaml" in output
    assert "contract_created: yes" in output
    assert "contract_updated: yes" in output
    assert "contract_entry_created: yes" in output
    assert "inferred_type: url" in output
    assert "required: yes" in output
    assert "sensitive: yes" in output
    assert "description: Primary database connection URL" in output
    assert "[WARN] Review .envctl.schema.yaml to confirm the inferred metadata." in output


def test_add_command_prints_minimal_output_when_inference_is_missing(monkeypatch, capsys) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.schema.yaml",
    )
    result = SimpleNamespace(
        contract_created=False,
        contract_updated=False,
        contract_entry_created=False,
        inferred_spec=None,
    )

    captured: dict[str, object] = {}

    def fake_run_add(request: AddVariableRequest):
        captured["request"] = request
        return context, result

    monkeypatch.setattr(add_command_module, "run_add", fake_run_add)

    add_command_module.add_command(
        key="APP_NAME",
        value="demo",
        type_=None,
        required=False,
        optional=False,
        sensitive=False,
        non_sensitive=False,
        interactive=False,
        description=None,
        default=None,
        example=None,
        pattern=None,
        choice=None,
    )

    output = capsys.readouterr().out
    request = captured["request"]

    assert isinstance(request, AddVariableRequest)
    assert request.key == "APP_NAME"
    assert request.value == "demo"

    assert "[OK] Added 'APP_NAME' to contract and local vault" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "contract: /tmp/repo/.envctl.schema.yaml" in output
    assert "contract_created: yes" not in output
    assert "contract_updated: yes" not in output
    assert "contract_entry_created: yes" not in output
    assert "inferred_type:" not in output
    assert "required:" not in output
    assert "sensitive:" not in output
    assert "description:" not in output
    assert "[WARN] Review .envctl.schema.yaml to confirm the inferred metadata." in output


def test_add_command_omits_optional_inferred_fields_when_not_present(monkeypatch, capsys) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.schema.yaml",
    )
    result = SimpleNamespace(
        contract_created=False,
        contract_updated=True,
        contract_entry_created=True,
        inferred_spec={"type": "string"},
    )

    monkeypatch.setattr(
        add_command_module,
        "run_add",
        lambda request: (context, result),
    )

    add_command_module.add_command(
        key="APP_NAME",
        value="demo",
        type_=None,
        required=False,
        optional=False,
        sensitive=False,
        non_sensitive=False,
        interactive=False,
        description=None,
        default=None,
        example=None,
        pattern=None,
        choice=None,
    )

    output = capsys.readouterr().out

    assert "inferred_type: string" in output
    assert "required:" not in output
    assert "sensitive:" not in output
    assert "description:" not in output
