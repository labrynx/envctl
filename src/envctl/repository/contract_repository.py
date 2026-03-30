"""Contract loading, validation and writing helpers."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError as PydanticValidationError

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract import Contract
from envctl.errors import ContractError
from envctl.utils.atomic import write_text_atomic


def create_empty_contract(
    *,
    project_key: str | None = None,
    project_name: str | None = None,
) -> Contract:
    """Create an empty valid contract."""
    contract = Contract(version=CONTRACT_VERSION, variables={})
    if project_key is not None:
        contract = contract.with_meta(
            project_key=project_key,
            project_name=project_name,
        )
    return contract


def ensure_contract_metadata(
    contract: Contract,
    *,
    project_key: str,
    project_name: str | None = None,
) -> Contract:
    """Ensure the contract carries logical metadata."""
    if (
        contract.meta is not None
        and contract.meta.project_key == project_key
        and contract.meta.project_name == project_name
    ):
        return contract

    return contract.with_meta(
        project_key=project_key,
        project_name=project_name,
    )


def _normalize_contract_payload(raw: object) -> dict[str, object]:
    """Normalize raw YAML into the shape expected by the Pydantic models."""
    if raw is None:
        raw = {}

    if not isinstance(raw, dict):
        raise ContractError("Contract must be a YAML mapping")

    version = raw.get("version", CONTRACT_VERSION)
    meta_raw = raw.get("meta")
    variables_raw = raw.get("variables", {})

    if meta_raw is not None and not isinstance(meta_raw, dict):
        raise ContractError("'meta' must be a mapping")

    if not isinstance(variables_raw, dict):
        raise ContractError("'variables' must be a mapping")

    variables: dict[str, object] = {}

    for key, value in variables_raw.items():
        if not isinstance(value, dict):
            raise ContractError(f"Variable '{key}' must be a mapping")
        variables[str(key)] = {
            "name": str(key),
            **value,
        }

    return {
        "version": version,
        "meta": meta_raw,
        "variables": variables,
    }


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

    normalized = _normalize_contract_payload(raw)

    try:
        return Contract.model_validate(normalized)
    except PydanticValidationError as exc:
        raise ContractError(f"Invalid contract: {exc}") from exc


def load_contract_optional(path: Path) -> Contract | None:
    """Load a contract when present, otherwise return None."""
    if not path.exists():
        return None
    return load_contract(path)


def write_contract(path: Path, contract: Contract) -> None:
    """Write a contract to disk."""
    content = yaml.safe_dump(
        contract.to_contract_payload(),
        sort_keys=False,
        allow_unicode=True,
    )
    write_text_atomic(path, content)