from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
import typer

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.domain.runtime import RuntimeMode
from envctl.domain.selection import ContractSelection, group_selection
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
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)
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

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)
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

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
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
        "error": {"type": "EnvctlError", "message": "boom"},
    }


def test_handle_errors_renders_projection_validation_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, tuple[ProjectionValidationDiagnostics, str]] = {}
    diagnostics = ProjectionValidationDiagnostics(
        operation="sync",
        active_profile="staging",
        selection=group_selection("Application"),
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
                selection=ContractSelection(),
                report=make_resolution_report(missing_required=("DATABASE_URL",)),
                suggested_actions=("envctl fill",),
            ),
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl sync",
    )
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
        "selection": {"mode": "full", "group": None, "set": None, "var": None},
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
        path=Path("/tmp/demo/.envctl.yaml"),
        suggested_actions=("envctl check",),
    )

    @handle_errors
    def sample() -> None:
        raise ContractError(
            "Contract file not found: /tmp/demo/.envctl.yaml",
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
        "Contract file not found: /tmp/demo/.envctl.yaml",
    )


def test_handle_errors_emits_contract_details_in_json_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    @handle_errors
    def sample() -> None:
        raise ContractError(
            "Invalid YAML contract: /tmp/demo/.envctl.yaml",
            diagnostics=ContractDiagnostics(
                category="invalid_yaml",
                path=Path("/tmp/demo/.envctl.yaml"),
                suggested_actions=("envctl check", "fix .envctl.yaml"),
            ),
        )

    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)
    monkeypatch.setattr(
        "envctl.cli.decorators.get_command_path",
        lambda: "envctl check",
    )
    monkeypatch.setattr(
        "envctl.cli.decorators.emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit):
        sample()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["error"]["details"] == {
        "category": "invalid_yaml",
        "path": "/tmp/demo/.envctl.yaml",
        "key": None,
        "field": None,
        "issues": [],
        "suggested_actions": ["envctl check", "fix .envctl.yaml"],
    }


def test_emit_handled_error_renders_other_structured_families(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: False)

    @handle_errors
    def sample_config() -> None:
        raise ConfigError(
            "bad config",
            diagnostics=ConfigDiagnostics(category="invalid_json"),
        )

    @handle_errors
    def sample_state() -> None:
        raise StateError(
            "bad state",
            diagnostics=StateDiagnostics(
                category="corrupted_state",
                path=Path("/tmp/state.json"),
            ),
        )

    @handle_errors
    def sample_repo() -> None:
        raise ProjectDetectionError(
            "bad repo",
            diagnostics=RepositoryDiscoveryDiagnostics(
                category="not_a_git_repository",
            ),
        )

    @handle_errors
    def sample_binding() -> None:
        raise ProjectDetectionError(
            "bad binding",
            diagnostics=ProjectBindingDiagnostics(
                category="ambiguous_vault_identity",
            ),
        )

    for func in (sample_config, sample_state, sample_repo, sample_binding):
        with pytest.raises(typer.Exit):
            func()

    captured = capsys.readouterr()
    assert "Error: bad config" in captured.err
    assert "Error: bad state" in captured.err
    assert "Error: bad repo" in captured.err
    assert "Error: bad binding" in captured.err


def test_requires_writable_runtime_blocks_ci_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.cli.decorators.load_config",
        lambda: SimpleNamespace(runtime_mode=RuntimeMode.CI),
    )

    @requires_writable_runtime("sync")
    def sample() -> None:
        raise AssertionError("Should not be called")

    with pytest.raises(
        ExecutionError,
        match="Command 'sync' is not available in CI read-only mode.",
    ):
        sample()


def test_text_output_only_rejects_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("envctl.cli.decorators.is_json_output", lambda: True)

    @text_output_only("run")
    def sample() -> None:
        raise AssertionError("Should not be called")

    with pytest.raises(ExecutionError, match="JSON output is not supported"):
        sample()
