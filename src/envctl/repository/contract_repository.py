"""Contract loading helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract import Contract, VariableSpec
from envctl.errors import ContractError

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

    if not isinstance(raw, dict):
        raise ContractError("Contract must be a YAML mapping")

    version = raw.get("version", CONTRACT_VERSION)
    if version != CONTRACT_VERSION:
        raise ContractError(f"Unsupported contract version: {version}")

    variables_raw = raw.get("variables")
    if not isinstance(variables_raw, dict) or not variables_raw:
        raise ContractError("Contract must define a non-empty 'variables' mapping")

    variables: dict[str, VariableSpec] = {}

    for key, value in variables_raw.items():
        if not isinstance(key, str) or not _KEY_RE.match(key):
            raise ContractError(f"Invalid variable name: {key!r}")
        if not isinstance(value, dict):
            raise ContractError(f"Variable '{key}' must be a mapping")

        var_type = str(value.get("type", "string")).strip()
        if var_type not in _ALLOWED_TYPES:
            raise ContractError(f"Unsupported type '{var_type}' for variable '{key}'")

        spec = VariableSpec(
            name=key,
            type=var_type,
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
