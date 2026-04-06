from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import envctl.repository.contract_repository as contract_repository
from envctl.errors import ContractError
from envctl.repository.contract_repository import (
    create_empty_contract,
    ensure_contract_metadata,
    load_contract,
    load_contract_optional,
    write_contract,
)
from tests.support.assertions import require_contract_diagnostics
from tests.support.contracts import make_contract, make_variable_spec


def test_create_empty_contract_returns_valid_contract() -> None:
    contract = create_empty_contract()

    assert contract.version == 1
    assert contract.variables == {}


def test_create_empty_contract_includes_metadata_when_provided() -> None:
    contract = create_empty_contract(project_key="demo", project_name="Demo")

    assert contract.meta is not None
    assert contract.meta.project_key == "demo"
    assert contract.meta.project_name == "Demo"


def test_ensure_contract_metadata_returns_same_contract_when_metadata_matches() -> None:
    contract = create_empty_contract(project_key="demo", project_name="Demo")

    updated = ensure_contract_metadata(
        contract,
        project_key="demo",
        project_name="Demo",
    )

    assert updated == contract


def test_ensure_contract_metadata_updates_contract_when_metadata_differs() -> None:
    contract = create_empty_contract()

    updated = ensure_contract_metadata(
        contract,
        project_key="demo",
        project_name="Demo",
    )

    assert updated.meta is not None
    assert updated.meta.project_key == "demo"
    assert updated.meta.project_name == "Demo"


def test_load_contract_reads_valid_yaml_contract(tmp_path: Path) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    payload = {
        "version": 1,
        "variables": {
            "APP_NAME": {
                "type": "string",
                "group": "Application",
                "format": "json",
                "required": True,
                "sensitive": False,
            }
        },
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    contract = load_contract(path)

    assert contract.version == 1
    assert "APP_NAME" in contract.variables

    spec = contract.variables["APP_NAME"]

    assert spec.group is None
    assert spec.groups == ("Application",)
    assert spec.normalized_groups == ("Application",)
    assert spec.format == "json"


def test_load_contract_optional_returns_none_when_missing(tmp_path: Path) -> None:
    path = tmp_path / ".envctl.schema.yaml"

    assert load_contract_optional(path) is None


def test_write_contract_serializes_contract(tmp_path: Path) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(
                name="APP_NAME",
                type="string",
                group="Application",
                format="csv",
                required=True,
                sensitive=False,
            )
        }
    )

    write_contract(path, contract)

    written = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert written["version"] == 1
    assert "APP_NAME" in written["variables"]
    assert written["variables"]["APP_NAME"]["groups"] == ["Application"]
    assert "group" not in written["variables"]["APP_NAME"]
    assert written["variables"]["APP_NAME"]["format"] == "csv"


def test_load_contract_raises_when_file_is_missing(tmp_path: Path) -> None:
    path = tmp_path / ".envctl.schema.yaml"

    with pytest.raises(ContractError, match=r"Contract file not found") as exc_info:
        load_contract(path)

    diagnostics = require_contract_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "missing_contract_file"
    assert diagnostics.path == path
    assert diagnostics.suggested_actions == (
        "envctl check",
        "fix .envctl.schema.yaml",
        "envctl init --contract starter",
    )


def test_load_contract_raises_when_yaml_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    path.write_text(":\n- bad", encoding="utf-8")

    with pytest.raises(ContractError, match=r"Invalid YAML contract") as exc_info:
        load_contract(path)

    diagnostics = require_contract_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_yaml"
    assert diagnostics.path == path


def test_load_contract_raises_when_file_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    path.write_text("version: 1\nvariables: {}\n", encoding="utf-8")

    def broken_read_text(self: Path, encoding: str = "utf-8") -> str:
        raise OSError("boom")

    monkeypatch.setattr(contract_repository.Path, "read_text", broken_read_text)

    with pytest.raises(ContractError, match=r"Unable to read contract") as exc_info:
        load_contract(path)

    diagnostics = require_contract_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "unreadable_contract"
    assert diagnostics.path == path


def test_load_contract_raises_for_invalid_variable_shape_with_structured_diagnostics(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    path.write_text("version: 1\nvariables:\n  PORT: nope\n", encoding="utf-8")

    with pytest.raises(ContractError, match=r"Variable 'PORT' must be a mapping") as exc_info:
        load_contract(path)

    diagnostics = require_contract_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_variable_shape"
    assert diagnostics.path == path
    assert diagnostics.key == "PORT"
    assert diagnostics.field == "variables"


def test_load_contract_raises_for_pydantic_validation_with_structured_issues(
    tmp_path: Path,
) -> None:
    path = tmp_path / ".envctl.schema.yaml"
    path.write_text(
        (
            "version: 1\n"
            "variables:\n"
            "  PORT:\n"
            "    type: nope\n"
            "    required: true\n"
            "    sensitive: false\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match=r"Invalid contract:") as exc_info:
        load_contract(path)

    diagnostics = require_contract_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "validation_failed"
    assert diagnostics.path == path
    assert diagnostics.issues
    assert any(issue.field.startswith("variables.PORT.type") for issue in diagnostics.issues)
