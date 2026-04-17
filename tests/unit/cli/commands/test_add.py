from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.add.command as add_command_module
from envctl.cli.presenters.outputs.actions import build_add_output
from envctl.cli.presenters.renderers.json import build_json_payload
from envctl.domain.operations import AddVariableRequest
from envctl.domain.runtime import RuntimeMode


def test_resolve_required_returns_true_when_required() -> None:
    assert add_command_module._resolve_required(True, False) is True


def test_resolve_required_returns_false_when_optional() -> None:
    assert add_command_module._resolve_required(False, True) is False


def test_resolve_required_returns_none_when_no_flags() -> None:
    assert add_command_module._resolve_required(False, False) is None


def test_resolve_required_raises_when_both_flags_are_set() -> None:
    with pytest.raises(ValueError, match=r"--required or --optional"):
        add_command_module._resolve_required(True, True)


def test_resolve_sensitive_returns_true_when_sensitive() -> None:
    assert add_command_module._resolve_sensitive(True, False) is True


def test_resolve_sensitive_returns_false_when_non_sensitive() -> None:
    assert add_command_module._resolve_sensitive(False, True) is False


def test_resolve_sensitive_returns_none_when_no_flags() -> None:
    assert add_command_module._resolve_sensitive(False, False) is None


def test_resolve_sensitive_raises_when_both_flags_are_set() -> None:
    with pytest.raises(ValueError, match=r"--sensitive or --non-sensitive"):
        add_command_module._resolve_sensitive(True, True)


def test_add_command_calls_service_and_prints_full_inference(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.yaml",
    )
    result = SimpleNamespace(
        active_profile="local",
        profile_path="/tmp/vault/values.env",
        contract_created=True,
        contract_updated=True,
        contract_entry_created=True,
        inferred_spec={
            "type": "url",
            "required": True,
            "sensitive": True,
            "description": "Primary database connection URL",
        },
        inferred_fields_used=["type", "required", "sensitive", "description"],
    )

    prompts = iter(
        [
            "url",
            "Primary database connection URL",
            "",
            "postgres://user:pass@localhost:5432/app",
            "",
            "^postgres://",
            "a, b",
        ]
    )
    confirms = iter([True, True])

    monkeypatch.setattr(
        add_command_module,
        "prompt_string",
        lambda _message, default="": next(prompts),
    )
    monkeypatch.setattr(
        add_command_module,
        "confirm",
        lambda _message, default=False: next(confirms),
    )

    captured: dict[str, Any] = {}

    def fake_run_add(
        request: AddVariableRequest,
        active_profile: str | None = None,
    ) -> tuple[object, object]:
        captured["request"] = request
        captured["active_profile"] = active_profile
        return context, result

    monkeypatch.setattr("envctl.services.add_service.run_add", fake_run_add)
    monkeypatch.setattr(add_command_module, "get_active_profile", lambda: "local")

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
        format_=None,
        pattern="^postgres://",
        choice=["a", "b"],
    )

    output = capsys.readouterr().out
    request = cast(AddVariableRequest, captured["request"])

    assert captured["active_profile"] == "local"
    assert request.key == "DATABASE_URL"
    assert request.value == "postgres://user:pass@localhost:5432/app"
    assert request.override_type == "url"
    assert request.override_required is True
    assert request.override_sensitive is True
    assert request.override_description == "Primary database connection URL"
    assert request.override_default is None
    assert request.override_example == "postgres://user:pass@localhost:5432/app"
    assert request.override_format is None
    assert request.override_pattern == "^postgres://"
    assert request.override_choices == ("a", "b")

    assert "[OK] Added 'DATABASE_URL' to contract and profile 'local'" in output
    assert "profile: local" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "contract: /tmp/repo/.envctl.yaml" in output
    assert "contract_created: yes" in output
    assert "contract_updated: yes" in output
    assert "contract_entry_created: yes" in output
    assert "inferred_type: url" in output
    assert "required: yes" in output
    assert "sensitive: yes" in output
    assert "description: Primary database connection URL" in output
    assert "[WARN] Review .envctl.yaml to confirm the inferred metadata." in output


def test_add_command_prints_minimal_output_when_inference_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.yaml",
    )
    result = SimpleNamespace(
        active_profile="local",
        profile_path="/tmp/vault/values.env",
        contract_created=False,
        contract_updated=False,
        contract_entry_created=False,
        inferred_spec=None,
        inferred_fields_used=[],
    )

    captured: dict[str, Any] = {}

    def fake_run_add(
        request: AddVariableRequest,
        active_profile: str | None = None,
    ) -> tuple[object, object]:
        captured["request"] = request
        captured["active_profile"] = active_profile
        return context, result

    monkeypatch.setattr("envctl.services.add_service.run_add", fake_run_add)
    monkeypatch.setattr(add_command_module, "get_active_profile", lambda: "local")

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
        format_=None,
        pattern=None,
        choice=None,
    )

    output = capsys.readouterr().out
    request = cast(AddVariableRequest, captured["request"])

    assert captured["active_profile"] == "local"
    assert request.key == "APP_NAME"
    assert request.value == "demo"

    assert "[OK] Added 'APP_NAME' to contract and profile 'local'" in output
    assert "profile: local" in output
    assert "vault_values: /tmp/vault/values.env" in output
    assert "contract: /tmp/repo/.envctl.yaml" in output
    assert "contract_created: yes" not in output
    assert "contract_updated: yes" not in output
    assert "contract_entry_created: yes" not in output
    assert "inferred_type:" not in output
    assert "required:" not in output
    assert "sensitive:" not in output
    assert "description:" not in output
    assert "[WARN] Review .envctl.yaml to confirm the inferred metadata." not in output


def test_add_command_omits_optional_inferred_fields_when_not_present(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.yaml",
    )
    result = SimpleNamespace(
        active_profile="local",
        profile_path="/tmp/vault/values.env",
        contract_created=False,
        contract_updated=True,
        contract_entry_created=True,
        inferred_spec={"type": "string"},
        inferred_fields_used=["type"],
    )

    monkeypatch.setattr(
        "envctl.services.add_service.run_add",
        lambda request, active_profile=None: (context, result),
    )
    monkeypatch.setattr(add_command_module, "get_active_profile", lambda: "local")

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
        format_=None,
        pattern=None,
        choice=None,
    )


def test_add_command_passes_format_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = SimpleNamespace(
        vault_values_path="/tmp/vault/values.env",
        repo_contract_path="/tmp/repo/.envctl.yaml",
    )
    result = SimpleNamespace(
        active_profile="local",
        profile_path="/tmp/vault/values.env",
        contract_created=False,
        contract_updated=True,
        contract_entry_created=True,
        inferred_spec=None,
        inferred_fields_used=[],
    )
    captured: dict[str, Any] = {}

    def fake_run_add(
        request: AddVariableRequest,
        active_profile: str | None = None,
    ) -> tuple[object, object]:
        captured["request"] = request
        captured["active_profile"] = active_profile
        return context, result

    monkeypatch.setattr("envctl.services.add_service.run_add", fake_run_add)
    monkeypatch.setattr(add_command_module, "get_active_profile", lambda: "local")

    add_command_module.add_command(
        key="TEST_JSON",
        value='{"ok": true}',
        required=False,
        optional=False,
        sensitive=False,
        non_sensitive=False,
        interactive=False,
        description=None,
        default=None,
        example=None,
        format_="json",
        pattern=None,
        choice=None,
    )

    request = cast(AddVariableRequest, captured["request"])
    assert request.override_format == "json"


def test_add_command_rejects_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "envctl.config.loader.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )
    monkeypatch.setattr(
        "envctl.cli.runtime.is_json_output",
        lambda: False,
    )

    with pytest.raises(typer.Exit) as exc_info:
        add_command_module.add_command(
            key="APP_NAME",
            value="demo",
        )

    assert exc_info.value.exit_code == 1
    captured = capsys.readouterr()
    assert "CI read-only mode" in captured.err


def test_add_command_emits_json_output() -> None:
    payload = build_json_payload(
        build_add_output(
            key="APP_NAME",
            profile="local",
            profile_path=Path("/tmp/vault/values.env"),
            contract_path=Path("/tmp/repo/.envctl.yaml"),
            contract_created=False,
            contract_updated=False,
            contract_entry_created=True,
        )
    )

    assert payload["metadata"]["key"] == "APP_NAME"
    assert payload["metadata"]["profile"] == "local"
    assert payload["metadata"]["vault_values"] == "/tmp/vault/values.env"
    assert payload["metadata"]["contract"] == "/tmp/repo/.envctl.yaml"
