"""Contract loading, validation and writing helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract import Contract, VariableSpec
from envctl.errors import ContractError
from envctl.utils.atomic import write_text_atomic

_ALLOWED_TYPES = {"string", "int", "bool", "url"}
_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _to_bool(value: Any, *, default: bool) -> bool:
    """Coerce a YAML value into bool with a default."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    raise ContractError("Boolean fields must be true or false")


def _coerce_choices(value: Any) -> tuple[str, ...]:
    """Coerce choices into a tuple of strings."""
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ContractError("'choices' must be a list of strings")
    return tuple(value)


def _validate_key(key: str) -> None:
    """Validate one contract variable name."""
    if not isinstance(key, str) or not _KEY_RE.match(key):
        raise ContractError(f"Invalid variable name: {key!r}")


def _validate_type(var_type: str, key: str) -> str:
    """Validate one declared variable type."""
    value = str(var_type).strip()
    if value not in _ALLOWED_TYPES:
        raise ContractError(f"Unsupported type '{value}' for variable '{key}'")
    return value


def _spec_to_payload(spec: VariableSpec) -> dict[str, Any]:
    """Convert one VariableSpec into a YAML payload mapping."""
    payload: dict[str, Any] = {
        "type": spec.type,
        "required": spec.required,
        "sensitive": spec.sensitive,
        "description": spec.description,
    }

    if spec.default is not None:
        payload["default"] = spec.default

    if spec.provider is not None:
        payload["provider"] = spec.provider

    if spec.example is not None:
        payload["example"] = spec.example

    if spec.pattern is not None:
        payload["pattern"] = spec.pattern

    if spec.choices:
        payload["choices"] = list(spec.choices)

    return payload


def create_empty_contract() -> Contract:
    """Create an empty valid contract."""
    return Contract(version=CONTRACT_VERSION, variables={})


def load_contract(path: Path) -> Contract:
    """Load a contract from disk."""
    if not path.exists():
        raise ContractError(f"Contract file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ContractError(f"Invalid YAML contract: {path}") from exc
    except OSError as exc:
        raise ContractError(f"Unable to read contract: {path}") from exc

    if raw is None:
        raw = {}

    if not isinstance(raw, dict):
        raise ContractError("Contract must be a YAML mapping")

    version = raw.get("version", CONTRACT_VERSION)
    if version != CONTRACT_VERSION:
        raise ContractError(f"Unsupported contract version: {version}")

    variables_raw = raw.get("variables", {})
    if not isinstance(variables_raw, dict):
        raise ContractError("'variables' must be a mapping")

    variables: dict[str, VariableSpec] = {}

    for key, value in variables_raw.items():
        _validate_key(key)

        if not isinstance(value, dict):
            raise ContractError(f"Variable '{key}' must be a mapping")

        spec = VariableSpec(
            name=key,
            type=_validate_type(value.get("type", "string"), key),
            required=_to_bool(value.get("required"), default=True),
            description=str(value.get("description", "")).strip(),
            sensitive=_to_bool(value.get("sensitive"), default=True),
            default=value.get("default"),
            provider=str(value["provider"]).strip()
            if "provider" in value and value["provider"] is not None
            else None,
            example=str(value["example"]).strip()
            if "example" in value and value["example"] is not None
            else None,
            pattern=str(value["pattern"]).strip()
            if "pattern" in value and value["pattern"] is not None
            else None,
            choices=_coerce_choices(value.get("choices")),
        )
        variables[key] = spec

    return Contract(version=CONTRACT_VERSION, variables=variables)


def load_contract_optional(path: Path) -> Contract | None:
    """Load a contract when present, otherwise return None."""
    if not path.exists():
        return None
    return load_contract(path)


def write_contract(path: Path, contract: Contract) -> None:
    """Write a contract to disk."""
    payload = {
        "version": contract.version,
        "variables": {
            key: _spec_to_payload(contract.variables[key]) for key in sorted(contract.variables)
        },
    }
    content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    write_text_atomic(path, content)


def upsert_variable(contract: Contract, spec: VariableSpec) -> Contract:
    """Insert or replace one variable spec in a contract."""
    _validate_key(spec.name)
    _validate_type(spec.type, spec.name)

    variables = dict(contract.variables)
    variables[spec.name] = spec
    return Contract(version=contract.version, variables=variables)


def remove_variable(contract: Contract, key: str) -> Contract:
    """Remove one variable spec from a contract."""
    variables = dict(contract.variables)
    variables.pop(key, None)
    return Contract(version=contract.version, variables=variables)
