from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.domain.runtime import RuntimeMode
from envctl.errors import (
    ConfigError,
    ContractError,
    EnvctlError,
    ExecutionError,
    ProjectDetectionError,
    StateError,
    ValidationError,
)
from envctl.services.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ProjectBindingDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)
from envctl.services.projection_validation import ProjectionValidationDiagnostics
from tests.support.builders import make_resolution_report


def test_handle_errors_returns_wrapped_result() -> None:
    @handle_errors
    def sample(value: int) -> int:
        return value + 1

    assert sample(4) == 5


def test_handle_errors_converts_envctl_error_to_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    @handle_errors
    def sample() -> None:
        raise EnvctlError("boom")

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: False,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.print_error",
        lambda message: captured.update({"message": message}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["message"] == "Error: boom"


def test_handle_errors_emits_structured_json_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    @handle_errors
    def sample() -> None:
        raise EnvctlError("boom")

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl check",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload == {
        "ok": False,
        "command": "envctl check",
        "error": {
            "type": "EnvctlError",
            "message": "boom",
        },
    }


def test_handle_errors_renders_projection_validation_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, tuple[ProjectionValidationDiagnostics, str]] = {}
    diagnostics = ProjectionValidationDiagnostics(
        operation="sync",
        active_profile="staging",
        selected_group="Application",
        report=make_resolution_report(missing_required=("DATABASE_URL",)),
        suggested_actions=("envctl fill",),
    )

    @handle_errors
    def sample() -> None:
        raise ValidationError(
            "Cannot sync because the environment contract is not satisfied.",
            diagnostics=diagnostics,
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
    monkeypatch.setattr(
        "envctl.cli.decorators.render_projection_validation_failure",
        lambda received_diagnostics, *, message: captured.update(
            {"value": (received_diagnostics, message)}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["value"] == (
        diagnostics,
        "Cannot sync because the environment contract is not satisfied.",
    )


def test_handle_errors_emits_validation_details_in_json_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    @handle_errors
    def sample() -> None:
        raise ValidationError(
            "Cannot sync because the environment contract is not satisfied.",
            diagnostics=ProjectionValidationDiagnostics(
                operation="sync",
                active_profile="staging",
                selected_group=None,
                report=make_resolution_report(missing_required=("DATABASE_URL",)),
                suggested_actions=("envctl fill",),
            ),
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
    monkeypatch.setattr("envctl.cli.decorators.get_command_path", lambda: "envctl sync")
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit):
        sample()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["error"]["details"] == {
        "operation": "sync",
        "active_profile": "staging",
        "selected_group": None,
        "report": {
            "is_valid": False,
            "values": {},
            "missing_required": ["DATABASE_URL"],
            "unknown_keys": [],
            "invalid_keys": [],
        },
        "suggested_actions": ["envctl fill"],
    }


def test_handle_errors_renders_contract_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, tuple[ContractDiagnostics, str]] = {}
    diagnostics = ContractDiagnostics(
        category="missing_contract_file",
        path=Path("/tmp/demo/.envctl.schema.yaml"),
        suggested_actions=("envctl check",),
    )

    @handle_errors
    def sample() -> None:
        raise ContractError(
            "Contract file not found: /tmp/demo/.envctl.schema.yaml",
            diagnostics=diagnostics,
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
    monkeypatch.setattr(
        "envctl.cli.decorators.render_contract_error",
        lambda received_diagnostics, *, message: captured.update(
            {"value": (received_diagnostics, message)}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        sample()

    assert exc_info.value.exit_code == 1
    assert captured["value"] == (
        diagnostics,
        "Contract file not found: /tmp/demo/.envctl.schema.yaml",
    )


def test_handle_errors_emits_contract_details_in_json_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    @handle_errors
    def sample() -> None:
        raise ContractError(
            "Invalid YAML contract: /tmp/demo/.envctl.schema.yaml",
            diagnostics=ContractDiagnostics(
                category="invalid_yaml",
                path=Path("/tmp/demo/.envctl.schema.yaml"),
                suggested_actions=("envctl check", "fix .envctl.schema.yaml"),
            ),
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
    monkeypatch.setattr("envctl.cli.decorators.get_command_path", lambda: "envctl check")
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit):
        sample()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["error"]["details"] == {
        "category": "invalid_yaml",
        "path": "/tmp/demo/.envctl.schema.yaml",
        "key": None,
        "field": None,
        "issues": [],
        "suggested_actions": ["envctl check", "fix .envctl.schema.yaml"],
    }


def test_emit_handled_error_renders_other_structured_families(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.cli.decorators.render_config_error",
        lambda diagnostics, *, message: captured.update({"config": message}),
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.render_state_error",
        lambda diagnostics, *, message: captured.update({"state": message}),
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.render_repository_discovery_error",
        lambda diagnostics, *, message: captured.update({"repo": message}),
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.render_project_binding_error",
        lambda diagnostics, *, message: captured.update({"binding": message}),
    )

    from envctl.cli.decorators import emit_handled_error

    emit_handled_error(
        ConfigError("bad config", diagnostics=ConfigDiagnostics(category="invalid_json")),
        json_output=False,
        command="envctl",
    )
    emit_handled_error(
        StateError(
            "bad state",
            diagnostics=StateDiagnostics(category="corrupted_state", path=Path("/tmp/state.json")),
        ),
        json_output=False,
        command="envctl status",
    )
    emit_handled_error(
        ProjectDetectionError(
            "git failed",
            diagnostics=RepositoryDiscoveryDiagnostics(category="git_command_failed"),
        ),
        json_output=False,
        command="envctl status",
    )
    emit_handled_error(
        ProjectDetectionError(
            "binding failed",
            diagnostics=ProjectBindingDiagnostics(category="ambiguous_vault_identity"),
        ),
        json_output=False,
        command="envctl status",
    )

    assert captured == {
        "config": "bad config",
        "state": "bad state",
        "repo": "git failed",
        "binding": "binding failed",
    }


def test_text_output_only_allows_text_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @text_output_only("export")
    def sample() -> str:
        return "ok"

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: False,
    )

    assert sample() == "ok"


def test_text_output_only_rejects_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @text_output_only("export")
    def sample() -> None:
        return None

    monkeypatch.setattr(
        "envctl.cli.decorators.is_json_output",
        lambda: True,
    )

    with pytest.raises(ExecutionError, match="JSON output is not supported"):
        sample()


def test_requires_writable_runtime_allows_local_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @requires_writable_runtime("add")
    def sample() -> str:
        return "ok"

    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.LOCAL),
    )

    assert sample() == "ok"


def test_requires_writable_runtime_rejects_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    @requires_writable_runtime("add")
    def sample() -> None:
        return None

    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )

    with pytest.raises(ExecutionError, match="CI read-only mode"):
        sample()
