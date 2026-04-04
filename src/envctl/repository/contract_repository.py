"""Contract loading, validation and writing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, NoReturn, cast

import yaml
from pydantic import ValidationError as PydanticValidationError

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract import Contract
from envctl.errors import ContractError
from envctl.services.error_diagnostics import (
    ContractDiagnosticCategory,
    ContractDiagnosticIssue,
    ContractDiagnostics,
)
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


def _raise_contract_error(
    message: str,
    *,
    category: ContractDiagnosticCategory,
    path: Path,
    key: str | None = None,
    field: str | None = None,
    issues: tuple[ContractDiagnosticIssue, ...] = (),
) -> NoReturn:
    """Raise one structured contract error."""
    raise ContractError(
        message,
        diagnostics=ContractDiagnostics(
            category=category,
            path=path,
            key=key,
            field=field,
            issues=issues,
            suggested_actions=_build_contract_suggested_actions(category=category, key=key),
        ),
    )


def _build_contract_suggested_actions(
    *,
    category: ContractDiagnosticCategory,
    key: str | None,
) -> tuple[str, ...]:
    """Build compact next-step suggestions for one contract failure."""
    actions = ["envctl check"]

    if category in {
        "missing_contract_file",
        "invalid_yaml",
        "validation_failed",
        "invalid_top_level_shape",
        "invalid_variable_shape",
    }:
        actions.append("fix .envctl.schema.yaml")

    if category == "missing_contract_file":
        actions.append("envctl init --contract starter")

    if category == "invalid_variable_shape" and key is not None:
        actions.append(f"inspect contract key {key}")

    seen: set[str] = set()
    ordered: list[str] = []
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        ordered.append(action)
    return tuple(ordered)


def load_contract(path: Path) -> Contract:
    """Load a contract from disk."""
    if not path.exists():
        _raise_contract_error(
            f"Contract file not found: {path}",
            category="missing_contract_file",
            path=path,
        )

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        _raise_contract_error(
            f"Invalid YAML contract: {path}",
            category="invalid_yaml",
            path=path,
        )
    except OSError:
        _raise_contract_error(
            f"Unable to read contract: {path}",
            category="unreadable_contract",
            path=path,
        )

    normalized = _normalize_contract_payload_with_path(raw, path)

    try:
        return Contract.model_validate(normalized)
    except PydanticValidationError as exc:
        _raise_contract_error(
            f"Invalid contract: {exc}",
            category="validation_failed",
            path=path,
            issues=tuple(
                ContractDiagnosticIssue(
                    field=".".join(str(part) for part in error["loc"]),
                    detail=str(error["msg"]),
                )
                for error in exc.errors()
            ),
        )


def _normalize_contract_payload_with_path(
    raw: object,
    path: Path,
) -> dict[str, object]:
    """Normalize raw YAML into the shape expected by the Pydantic models."""
    if raw is None:
        raw = {}

    if not isinstance(raw, dict):
        _raise_contract_error(
            "Contract must be a YAML mapping",
            category="invalid_top_level_shape",
            path=path,
            field="root",
        )

    raw_mapping = cast(dict[str, Any], raw)

    version = raw_mapping.get("version", CONTRACT_VERSION)
    meta_raw = raw_mapping.get("meta")
    variables_raw = raw_mapping.get("variables", {})

    if meta_raw is not None and not isinstance(meta_raw, dict):
        _raise_contract_error(
            "'meta' must be a mapping",
            category="invalid_top_level_shape",
            path=path,
            field="meta",
        )

    if not isinstance(variables_raw, dict):
        _raise_contract_error(
            "'variables' must be a mapping",
            category="invalid_top_level_shape",
            path=path,
            field="variables",
        )

    variables: dict[str, object] = {}

    for key, value in variables_raw.items():
        if not isinstance(value, dict):
            _raise_contract_error(
                f"Variable '{key}' must be a mapping",
                category="invalid_variable_shape",
                path=path,
                key=str(key),
                field="variables",
            )
        variables[str(key)] = {
            "name": str(key),
            **value,
        }

    return {
        "version": version,
        "meta": meta_raw,
        "variables": variables,
    }


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
