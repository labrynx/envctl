from __future__ import annotations

from pathlib import Path

import pytest

import envctl.repository.contract_repository as contract_repository
from envctl.errors import ContractError
from envctl.repository.contract_repository import load_contract


def write_contract(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_load_contract_reads_valid_contract(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
version: 1
variables:
  APP_NAME:
    type: string
    required: true
    sensitive: false
    description: Application name
    default: demo
    provider: local
    example: my-app
    pattern: "^[a-z0-9-]+$"
    choices:
      - demo
      - my-app
""".strip(),
    )

    contract = load_contract(contract_path)
    spec = contract.variables["APP_NAME"]

    assert contract.version == 1
    assert set(contract.variables) == {"APP_NAME"}
    assert spec.name == "APP_NAME"
    assert spec.type == "string"
    assert spec.required is True
    assert spec.sensitive is False
    assert spec.description == "Application name"
    assert spec.default == "demo"
    assert spec.provider == "local"
    assert spec.example == "my-app"
    assert spec.pattern == "^[a-z0-9-]+$"
    assert spec.choices == ("demo", "my-app")


def test_load_contract_uses_defaults_for_optional_fields(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  PORT: {}
""".strip(),
    )

    contract = load_contract(contract_path)
    spec = contract.variables["PORT"]

    assert contract.version == 1
    assert spec.type == "string"
    assert spec.required is True
    assert spec.sensitive is True
    assert spec.description == ""
    assert spec.default is None
    assert spec.provider is None
    assert spec.example is None
    assert spec.pattern is None
    assert spec.choices == ()


def test_load_contract_fails_when_file_is_missing(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"

    with pytest.raises(ContractError, match="Contract file not found"):
        load_contract(contract_path)


def test_load_contract_fails_on_invalid_yaml(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(contract_path, "variables: [unclosed")

    with pytest.raises(ContractError, match="Invalid YAML contract"):
        load_contract(contract_path)


def test_load_contract_fails_when_root_is_not_mapping(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(contract_path, "- just\n- a\n- list\n")

    with pytest.raises(ContractError, match="Contract must be a YAML mapping"):
        load_contract(contract_path)


def test_load_contract_fails_on_unsupported_version(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
version: 999
variables:
  APP_NAME: {}
""".strip(),
    )

    with pytest.raises(ContractError, match="Unsupported contract version"):
        load_contract(contract_path)


def test_load_contract_allows_missing_variables_mapping(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(contract_path, "version: 1\n")

    contract = load_contract(contract_path)

    assert contract.version == 1
    assert contract.variables == {}


def test_load_contract_fails_on_invalid_variable_name(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  app_name: {}
""".strip(),
    )

    with pytest.raises(ContractError, match="Invalid variable name"):
        load_contract(contract_path)


def test_load_contract_fails_when_variable_spec_is_not_mapping(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  APP_NAME: hello
""".strip(),
    )

    with pytest.raises(ContractError, match="must be a mapping"):
        load_contract(contract_path)


def test_load_contract_fails_on_unsupported_type(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  APP_NAME:
    type: float
""".strip(),
    )

    with pytest.raises(ContractError, match="Invalid contract"):
        load_contract(contract_path)


def test_load_contract_fails_when_boolean_fields_are_not_boolean(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  APP_NAME:
    required: "yes"
""".strip(),
    )

    contract = load_contract(contract_path)

    assert contract.variables["APP_NAME"].required is True


def test_load_contract_fails_when_choices_is_not_list_of_strings(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    write_contract(
        contract_path,
        """
variables:
  APP_NAME:
    choices:
      - ok
      - 123
""".strip(),
    )

    with pytest.raises(ContractError, match="Invalid contract"):
        load_contract(contract_path)


def test_load_contract_raises_when_file_cannot_be_read(monkeypatch, tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    contract_path.write_text("variables:\n  APP_NAME: {}\n", encoding="utf-8")

    def broken_read_text(self, encoding: str = "utf-8") -> str:
        raise OSError("boom")

    monkeypatch.setattr(contract_repository.Path, "read_text", broken_read_text)

    with pytest.raises(ContractError, match="Unable to read contract"):
        load_contract(contract_path)


def test_load_contract_rejects_non_mapping_variable_spec(tmp_path: Path) -> None:
    contract_path = tmp_path / ".envctl.schema.yaml"
    contract_path.write_text(
        """
variables:
  APP_NAME: hello
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ContractError, match="Variable 'APP_NAME' must be a mapping"):
        load_contract(contract_path)
