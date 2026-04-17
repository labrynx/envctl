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

    result = runner.invoke(app, ["--output", "json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["ok"] is False
    assert metadata["kind"] == "check"
    assert metadata["context"]["project_slug"] == "repo"
    assert metadata["summary"]["invalid"] == 1
    assert metadata["problems"][0]["key"] == "DATABASE_URL"
    assert metadata["problems"][0]["kind"] == "missing_required"


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

    result = runner.invoke(app, ["--output", "json", "sync"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["ok"] is False
    assert metadata["command"] == "envctl sync"
    assert metadata["error"]["type"] == "ValidationError"
    assert metadata["error"]["message"] == (
        "Cannot sync because the environment contract is not satisfied."
    )
    details = cast(dict[str, Any], metadata["error"]["details"])
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

    result = runner.invoke(app, ["--output", "json", "check"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["ok"] is True
    assert metadata["kind"] == "check"
    assert metadata["summary"]["invalid"] == 0
    assert sorted(metadata["values"]) == ["APP_NAME", "DATABASE_URL", "PORT"]


def test_check_json_outputs_structured_contract_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    contract_path = workspace / ".envctl.yaml"
    contract_path.write_text(":\n- bad", encoding="utf-8")

    result = runner.invoke(app, ["--output", "json", "check"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["ok"] is False
    assert metadata["command"] == "envctl check"
    assert metadata["error"]["type"] == "ContractError"
    assert metadata["error"]["message"] == f"Invalid YAML contract: {contract_path}"
    assert metadata["error"]["details"] == {
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

    result = runner.invoke(app, ["--output", "json", "check"])

    assert result.exit_code == 1
    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["error"]["type"] == "ConfigError"
    assert metadata["error"]["details"]["category"] == "invalid_runtime_mode"
    assert metadata["error"]["details"]["path"] == str(config_path)
    assert metadata["error"]["details"]["source_label"] == "config file"


def test_status_json_outputs_structured_state_error(
    runner: CliRunner,
    workspace: Path,
) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)

    state_path = find_single_state_path(workspace)
    state_path.write_text("{not-json", encoding="utf-8")

    result = runner.invoke(app, ["--output", "json", "status"])

    assert result.exit_code == 1
    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["error"]["type"] == "StateError"
    assert metadata["error"]["details"]["category"] == "corrupted_state"


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

    result = runner.invoke(app, ["--output", "json", "status"])

    assert result.exit_code == 1
    payload_json = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload_json["metadata"])
    assert metadata["error"]["type"] == "ProjectDetectionError"
    assert metadata["error"]["details"]["category"] == "ambiguous_vault_identity"
    assert metadata["error"]["details"]["repo_root"] == str(workspace)


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

    result = runner.invoke(app, ["--output", "json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["kind"] == "inspect"
    assert metadata["context"]["project_slug"] == "repo"
    assert metadata["problems"][0]["key"] == "DATABASE_URL"
    assert "APP_NAME" in metadata["variables"]
    assert metadata["variables"]["APP_NAME"]["value"] == "demo-app"
    assert metadata["variables"]["APP_NAME"]["source"] == "vault"


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

    result = runner.invoke(app, ["--output", "json", "inspect", "DATABASE_URL"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["kind"] == "inspect_key"
    item = cast(dict[str, Any], metadata["item"])
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

    result = runner.invoke(app, ["--output", "json", "inspect", "MISSING_KEY"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["ok"] is False
    assert metadata["command"] == "envctl inspect"
    assert metadata["error"]["type"] == "ValidationError"
    assert metadata["error"]["message"] == "Key is not resolved: MISSING_KEY"


def test_status_json_outputs_structured_status_payload(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--output", "json", "status"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["kind"] == "status"
    assert metadata["ok"] is False
    assert metadata["project_slug"] == "repo"
    assert metadata["contract_exists"] is True
    assert metadata["vault_exists"] is False
    assert metadata["resolved_valid"] is False
    assert isinstance(metadata["issues"], list)


def test_doctor_json_outputs_structured_checks(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--output", "json", "inspect"])

    assert result.exit_code == 0

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["kind"] == "inspect"
    assert "context" in metadata
    assert "project" in metadata
    assert "problems" in metadata


def test_vault_show_json_outputs_structured_missing_payload(
    runner: CliRunner,
    workspace: Path,
) -> None:
    result = runner.invoke(app, ["--output", "json", "vault", "show"])

    assert result.exit_code == 1

    payload = parse_json_output(result.output)
    metadata = cast(dict[str, Any], payload["metadata"])
    assert metadata["kind"] == "vault_show"
    assert metadata["state"] == "missing"
    assert metadata["ok"] is False
