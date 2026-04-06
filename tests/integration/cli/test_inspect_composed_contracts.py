from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from envctl.cli.app import app
from tests.support.profile_values import patch_loaded_profile_values


def _write_contract(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_inspect_json_outputs_contract_graph_for_composed_contracts(
    runner: CliRunner,
    workspace: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = workspace / ".envctl.yaml"
    legacy = workspace / ".envctl.schema.yaml"
    legacy.unlink(missing_ok=True)
    _write_contract(
        root,
        {
            "version": 1,
            "imports": ["./contracts/shared.yaml", "./contracts/backend.yaml"],
            "variables": {"APP_NAME": {"sensitive": False}},
            "sets": {"runtime": {"variables": ["APP_NAME"]}},
        },
    )
    _write_contract(
        workspace / "contracts" / "shared.yaml",
        {"version": 1, "variables": {"API_URL": {"sensitive": False, "groups": ["runtime"]}}},
    )
    _write_contract(
        workspace / "contracts" / "backend.yaml",
        {"version": 1, "variables": {"DATABASE_URL": {"sensitive": True, "groups": ["infra"]}}},
    )

    patch_loaded_profile_values(
        monkeypatch,
        values={
            "APP_NAME": "demo-app",
            "API_URL": "https://api.example.com",
            "DATABASE_URL": "postgres://user:pass@localhost:5432/app",
        },
    )

    result = runner.invoke(app, ["--json", "inspect"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    graph = payload["data"]["contract_graph"]
    assert graph["contracts_total"] == 3
    assert sorted(graph["declared_in"]) == ["API_URL", "APP_NAME", "DATABASE_URL"]
    assert "runtime" in graph["groups_index"] or "infra" in graph["groups_index"]
