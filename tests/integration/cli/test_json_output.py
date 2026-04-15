from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from typer.testing import CliRunner

from envctl.cli.app import app
from tests.support.profile_values import patch_loaded_profile_values


def parse_json_output(output: str) -> dict[str, Any]:
    """Parse one CLI JSON payload."""
    return cast(dict[str, Any], json.loads(output))


def get_fake_home(workspace: Path) -> Path:
    """Return the fake home directory used by CLI integration tests."""
    return workspace.parent / "home"


def get_vault_projects_dir(workspace: Path) -> Path:
    """Return the test vault projects directory."""
    return get_fake_home(workspace) / ".envctl" / "vault" / "projects"


def get_config_path(workspace: Path) -> Path:
    """Return the config file path inside the fake home directory."""
    return get_fake_home(workspace) / ".config" / "envctl" / "config.json"


def find_single_state_path(workspace: Path) -> Path:
    """Locate the single generated state.json file for the test workspace."""
    vault_projects_dir = get_vault_projects_dir(workspace)
    candidates = sorted(vault_projects_dir.glob("*/state.json"))

    matching = []
    for candidate in candidates:
        try:
            contents = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            matching.append(candidate)
            continue

        if contents.get("repo_root") == str(workspace):
            matching.append(candidate)

    assert matching, f"No state.json found for workspace {workspace} under {vault_projects_dir}"
    assert len(matching) == 1, (
        f"Expected exactly one state.json for workspace {workspace}, "
        f"found {len(matching)}: {matching}"
    )
    return matching[0]


def test_check_json_outputs_structured_payload_for_invalid_environment(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
        },
    )

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["ok"] is False
    assert payload["command"] == "check"

    data = cast(dict[str, Any], payload["data"])
    assert data["context"]["project_slug"] == "repo"
    assert data["report"]["is_valid"] is False
    assert data["report"]["missing_required"] == ["DATABASE_URL"]
    assert data["report"]["unknown_keys"] == []
    assert data["report"]["invalid_keys"] == []


def test_sync_json_outputs_structured_projection_validation_error(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
        },
    )

    result = runner.invoke(app, ["--json", "sync"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["ok"] is False
    assert payload["command"] == "envctl sync"
    assert payload["error"]["type"] == "ValidationError"
    assert payload["error"]["message"] == (
        "Cannot sync because the environment contract is not satisfied."
    )
    details = cast(dict[str, Any], payload["error"]["details"])
    assert details["operation"] == "sync"
    assert details["active_profile"] == "local"
    assert details["selection"] == {
        "mode": "full",
        "group": None,
        "set": None,
        "var": None,
    }
    assert details["suggested_actions"] == ["envctl fill", "envctl set KEY VALUE"]
    report = cast(dict[str, Any], details["report"])
    assert report["is_valid"] is False
    assert report["missing_required"] == ["DATABASE_URL"]
    assert report["unknown_keys"] == []
    assert report["invalid_keys"] == []
    app_name = cast(dict[str, Any], report["values"]["APP_NAME"])
    assert app_name["key"] == "APP_NAME"
    assert app_name["value"] == "demo-app"
    assert app_name["source"] == "vault"
    assert app_name["valid"] is True


def test_check_json_outputs_success_payload_when_environment_is_valid(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
            "DATABASE_URL": "postgres://user:pass@localhost:5432/app",
        },
    )

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "check"

    data = cast(dict[str, Any], payload["data"])
    assert data["report"]["is_valid"] is True
    assert data["report"]["missing_required"] == []
    assert sorted(data["report"]["values"]) == ["APP_NAME", "DATABASE_URL", "PORT"]


def test_check_json_outputs_structured_contract_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    contract_path = workspace / ".envctl.yaml"
    contract_path.write_text(":\n- bad", encoding="utf-8")

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload["ok"] is False
    assert payload["command"] == "envctl check"
    assert payload["error"]["type"] == "ContractError"
    assert payload["error"]["message"] == f"Invalid YAML contract: {contract_path}"
    assert payload["error"]["details"] == {
        "category": "invalid_yaml",
        "path": str(contract_path),
        "key": None,
        "field": None,
        "issues": [],
        "suggested_actions": ["envctl check", "fix .envctl.yaml"],
    }


def test_callback_json_outputs_structured_config_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    config_path = get_config_path(workspace)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text('{"runtime_mode":"banana"}', encoding="utf-8")

    result = runner.invoke(app, ["--json", "check"])

    assert result.exit_code == 1
    payload = parse_json_output(result.output)
    assert payload["error"]["type"] == "ConfigError"
    assert payload["error"]["details"]["category"] == "invalid_runtime_mode"
    assert payload["error"]["details"]["path"] == str(config_path)
    assert payload["error"]["details"]["source_label"] == "config file"


def test_status_json_outputs_structured_state_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    state_path = find_single_state_path(workspace)
    state_path.write_text("{not-json", encoding="utf-8")

    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 1
    payload = parse_json_output(result.output)
    assert payload["error"]["type"] == "StateError"
    assert payload["error"]["details"]["category"] == "corrupted_state"


def test_status_json_outputs_structured_project_binding_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)

    vault_projects_dir = get_vault_projects_dir(workspace)
    first = vault_projects_dir / "demo-a--prj_1111111111111111"
    second = vault_projects_dir / "demo-b--prj_2222222222222222"
    first.mkdir(parents=True, exist_ok=True)
    second.mkdir(parents=True, exist_ok=True)
    first_payload = {
        "version": 2,
        "project_slug": "demo",
        "project_key": "demo",
        "project_id": "prj_1111111111111111",
        "repo_root": str(workspace),
        "git_remote": "git@github.com:labrynx/envctl.git",
        "known_paths": [],
        "created_at": "2026-03-30T00:00:00Z",
        "last_seen_at": "2026-03-30T00:00:00Z",
    }
    second_payload = {
        "version": 2,
        "project_slug": "demo",
        "project_key": "demo",
        "project_id": "prj_2222222222222222",
        "repo_root": str(workspace),
        "git_remote": "git@github.com:labrynx/envctl.git",
        "known_paths": [],
        "created_at": "2026-03-30T00:00:00Z",
        "last_seen_at": "2026-03-30T00:00:00Z",
    }

    (first / "state.json").write_text(
        json.dumps(first_payload),
        encoding="utf-8",
    )
    (second / "state.json").write_text(
        json.dumps(second_payload),
        encoding="utf-8",
    )

    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 1
    payload_json = parse_json_output(result.output)
    assert payload_json["error"]["type"] == "ProjectDetectionError"
    assert payload_json["error"]["details"]["category"] == "ambiguous_vault_identity"
    assert payload_json["error"]["details"]["repo_root"] == str(workspace)


def test_inspect_json_outputs_structured_resolution_report(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
        },
    )

    result = runner.invoke(app, ["--json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "inspect"

    data = cast(dict[str, Any], payload["data"])
    assert data["context"]["project_slug"] == "repo"
    assert data["report"]["missing_required"] == ["DATABASE_URL"]
    assert "APP_NAME" in data["report"]["values"]
    assert data["report"]["values"]["APP_NAME"]["value"] == "demo-app"
    assert data["report"]["values"]["APP_NAME"]["source"] == "vault"


def test_inspect_json_outputs_one_resolved_item(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
            "DATABASE_URL": "postgres://user:pass@localhost:5432/app",
        },
    )

    result = runner.invoke(app, ["--json", "inspect", "DATABASE_URL"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "inspect"

    data = cast(dict[str, Any], payload["data"])
    item = cast(dict[str, Any], data["item"])
    assert item["key"] == "DATABASE_URL"
    assert item["source"] == "vault"
    assert item["masked"] is True
    assert item["valid"] is True
    assert str(item["value"]).startswith("po")


def test_inspect_json_outputs_structured_error_for_unresolved_key(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
        },
    )

    result = runner.invoke(app, ["--json", "inspect", "MISSING_KEY"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl inspect",
        "error": {
            "type": "ValidationError",
            "message": "Key is not resolved: MISSING_KEY",
        },
    }


def test_status_json_outputs_structured_status_payload(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "status"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["ok"] is True
    assert payload["command"] == "status"

    data = cast(dict[str, Any], payload["data"])
    assert data["project_slug"] == "repo"
    assert data["contract_exists"] is True
    assert data["vault_exists"] is False
    assert data["resolved_valid"] is False
    assert isinstance(data["issues"], list)


def test_doctor_json_outputs_structured_checks(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    assert payload["command"] == "inspect"
    assert payload["ok"] is True

    data = payload["data"]
    assert "context" in data
    assert "project" in data
    assert "problems" in data


def test_json_is_rejected_for_unsupported_text_only_command(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--json", "vault", "show"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    assert payload == {
        "ok": False,
        "command": "envctl vault show",
        "error": {
            "type": "ExecutionError",
            "message": "JSON output is not supported for 'vault show' yet.",
        },
    }
