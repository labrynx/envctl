"""Contract loading, validation and writing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, NoReturn, cast

import yaml
from pydantic import ValidationError as PydanticValidationError

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract import Contract
from envctl.domain.deprecations import (
    ContractDeprecationWarning,
    make_group_deprecation_warning,
    make_required_deprecation_warning,
)
from envctl.domain.error_diagnostics import (
    ContractDiagnosticCategory,
    ContractDiagnosticIssue,
    ContractDiagnostics,
)
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
        actions.append("fix .envctl.yaml")

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
    """Load a contract from disk without surfacing deprecation warnings."""
    contract, _warnings = load_contract_with_warnings(path)
    return contract


def load_contract_with_warnings(
    path: Path,
) -> tuple[Contract, tuple[ContractDeprecationWarning, ...]]:
    """Load a contract from disk and collect normalized deprecation warnings."""
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

    normalized, warnings = _normalize_contract_payload_with_path(raw, path)

    try:
        return Contract.model_validate(normalized), warnings
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
) -> tuple[dict[str, object], tuple[ContractDeprecationWarning, ...]]:
    raw_mapping = _normalize_contract_root(raw, path)

    version = raw_mapping.get("version", CONTRACT_VERSION)
    meta_raw = _normalize_meta_payload(raw_mapping.get("meta"), path)
    imports = _normalize_imports_payload(raw_mapping.get("imports", ()), path=path)
    variables_raw = _require_mapping(
        raw_mapping.get("variables", {}),
        path=path,
        field="variables",
    )
    sets_raw = _require_mapping(
        raw_mapping.get("sets", {}),
        path=path,
        field="sets",
    )

    warnings: list[ContractDeprecationWarning] = []
    variables = _normalize_variables_payload(variables_raw, path=path, warnings=warnings)
    sets = _normalize_sets_payload(sets_raw, path=path)

    warnings = sorted(
        _dedupe_warnings(warnings),
        key=lambda item: (item.key, item.deprecated_field),
    )

    return {
        "version": version,
        "meta": meta_raw,
        "imports": imports,
        "variables": variables,
        "sets": sets,
    }, tuple(warnings)


def _normalize_imports_payload(
    value: object,
    *,
    path: Path,
) -> tuple[str, ...]:
    if value is None:
        return ()

    if not isinstance(value, list | tuple):
        _raise_contract_error(
            "'imports' must be a list of strings",
            category="invalid_top_level_shape",
            path=path,
            field="imports",
        )

    imports: list[str] = []
    for item in value:
        if not isinstance(item, str):
            _raise_contract_error(
                "'imports' must contain only strings",
                category="invalid_top_level_shape",
                path=path,
                field="imports",
            )
        normalized = item.strip()
        if not normalized:
            _raise_contract_error(
                "'imports' cannot contain empty values",
                category="invalid_top_level_shape",
                path=path,
                field="imports",
            )
        imports.append(normalized)

    return tuple(imports)


def _normalize_contract_root(raw: object, path: Path) -> dict[str, Any]:
    if raw is None:
        raw = {}

    if not isinstance(raw, dict):
        _raise_contract_error(
            "Contract must be a YAML mapping",
            category="invalid_top_level_shape",
            path=path,
            field="root",
        )

    return cast(dict[str, Any], raw)


def _normalize_meta_payload(meta_raw: object, path: Path) -> dict[str, Any] | None:
    if meta_raw is None:
        return None
    if not isinstance(meta_raw, dict):
        _raise_contract_error(
            "'meta' must be a mapping",
            category="invalid_top_level_shape",
            path=path,
            field="meta",
        )
    return cast(dict[str, Any], meta_raw)


def _require_mapping(
    value: object,
    *,
    path: Path,
    field: str,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _raise_contract_error(
            f"'{field}' must be a mapping",
            category="invalid_top_level_shape",
            path=path,
            field=field,
        )
    return cast(dict[str, Any], value)


def _normalize_variables_payload(
    variables_raw: dict[str, Any],
    *,
    path: Path,
    warnings: list[ContractDeprecationWarning],
) -> dict[str, object]:
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

        variable_key = str(key)
        variable_payload = dict(value)
        _validate_deprecated_group_usage(
            variable_key,
            variable_payload=variable_payload,
            path=path,
        )
        _apply_variable_deprecations(
            variable_key,
            variable_payload=variable_payload,
            warnings=warnings,
        )
        variables[variable_key] = {"name": variable_key, **variable_payload}

    return variables


def _validate_deprecated_group_usage(
    variable_key: str,
    *,
    variable_payload: dict[str, Any],
    path: Path,
) -> None:
    if "group" not in variable_payload or "groups" not in variable_payload:
        return

    _raise_contract_error(
        f"Variable '{variable_key}' cannot define both 'group' and 'groups'",
        category="validation_failed",
        path=path,
        key=variable_key,
        field="variables",
        issues=(
            ContractDiagnosticIssue(
                field=f"variables.{variable_key}",
                detail="'group' and 'groups' cannot be used together",
            ),
        ),
    )


def _apply_variable_deprecations(
    variable_key: str,
    *,
    variable_payload: dict[str, Any],
    warnings: list[ContractDeprecationWarning],
) -> None:
    if "group" in variable_payload:
        group_value = str(variable_payload["group"]).strip()
        warnings.append(make_group_deprecation_warning(variable_key, group_value))
        variable_payload["groups"] = [group_value]
        variable_payload.pop("group", None)

    if "required" in variable_payload:
        warnings.append(make_required_deprecation_warning(variable_key))
        variable_payload.pop("required", None)


def _normalize_sets_payload(
    sets_raw: dict[str, Any],
    *,
    path: Path,
) -> dict[str, object]:
    sets: dict[str, object] = {}
    for key, value in sets_raw.items():
        if not isinstance(value, dict):
            _raise_contract_error(
                f"Set '{key}' must be a mapping",
                category="invalid_variable_shape",
                path=path,
                key=str(key),
                field="sets",
            )
        sets[str(key)] = {"name": str(key), **value}
    return sets


def _dedupe_warnings(
    warnings: list[ContractDeprecationWarning],
) -> list[ContractDeprecationWarning]:
    seen: set[tuple[str, str]] = set()
    unique: list[ContractDeprecationWarning] = []
    for warning in warnings:
        key = (warning.key, warning.deprecated_field)
        if key in seen:
            continue
        seen.add(key)
        unique.append(warning)
    return unique


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
