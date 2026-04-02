"""Resolution service."""

from __future__ import annotations

import csv
import json
import os
import re
from io import StringIO
from urllib.parse import urlparse

from envctl.adapters.dotenv import load_env_file
from envctl.domain.contract import Contract, VariableSpec
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.repository.contract_repository import load_contract
from envctl.utils.project_paths import (
    build_profile_env_path,
    is_local_profile,
    normalize_profile_name,
)


def _validate_choices(spec: VariableSpec, value: str) -> tuple[bool, str | None]:
    """Validate choice constraints."""
    if spec.choices and value not in spec.choices:
        return False, f"Expected one of: {', '.join(spec.choices)}"
    return True, None


def _validate_pattern(spec: VariableSpec, value: str) -> tuple[bool, str | None]:
    """Validate regex pattern constraints."""
    if spec.pattern and re.fullmatch(spec.pattern, value) is None:
        return False, f"Value does not match pattern: {spec.pattern}"
    return True, None


def _validate_int(value: str) -> tuple[bool, str | None]:
    """Validate integer values."""
    try:
        int(value)
    except ValueError:
        return False, "Expected an integer"
    return True, None


def _validate_bool(value: str) -> tuple[bool, str | None]:
    """Validate boolean values."""
    normalized = value.lower()
    if normalized not in {"true", "false", "1", "0", "yes", "no"}:
        return False, "Expected a boolean"
    return True, None


def _validate_url(value: str) -> tuple[bool, str | None]:
    """Validate URL values."""
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return False, "Expected a valid URL"
    return True, None


def _validate_json(value: str) -> tuple[bool, str | None]:
    """Validate JSON string payloads."""
    try:
        json.loads(value)
    except json.JSONDecodeError:
        return False, "Expected a valid JSON string"
    return True, None


def _validate_csv(value: str) -> tuple[bool, str | None]:
    """Validate CSV string payloads."""
    if not value.strip():
        return False, "Expected a non-empty CSV string"

    try:
        parsed_rows = list(csv.reader(StringIO(value)))
    except csv.Error:
        return False, "Expected a valid CSV string"

    if not parsed_rows:
        return False, "Expected a valid CSV string"

    if not any(cell.strip() for cell in parsed_rows[0]):
        return False, "Expected a non-empty CSV string"

    return True, None


def _validate_string_format(spec: VariableSpec, value: str) -> tuple[bool, str | None]:
    """Validate semantic format hints for string-typed variables."""
    if spec.format is None:
        return True, None

    if spec.format == "json":
        return _validate_json(value)
    if spec.format == "url":
        return _validate_url(value)
    return _validate_csv(value)


def _is_valid_type(spec: VariableSpec, value: str) -> tuple[bool, str | None]:
    """Validate one value against its declared type."""
    valid, detail = _validate_choices(spec, value)
    if not valid:
        return valid, detail

    valid, detail = _validate_pattern(spec, value)
    if not valid:
        return valid, detail

    if spec.type == "string":
        return _validate_string_format(spec, value)
    if spec.type == "int":
        return _validate_int(value)
    if spec.type == "bool":
        return _validate_bool(value)
    return _validate_url(value)


def load_contract_for_context(context: ProjectContext) -> Contract:
    """Load the contract for the current project."""
    return load_contract(context.repo_contract_path)


def resolve_environment(
    context: ProjectContext,
    contract: Contract,
    *,
    active_profile: str | None = None,
) -> ResolutionReport:
    """Resolve environment values from the selected profile and system env."""
    resolved_profile = normalize_profile_name(active_profile)

    if is_local_profile(resolved_profile):
        profile_env_path = context.vault_values_path
        profile_source = "vault"
    else:
        profile_env_path = build_profile_env_path(context.vault_project_dir, resolved_profile)
        profile_source = "profile"

    profile_values = load_env_file(profile_env_path)

    values: dict[str, ResolvedValue] = {}
    missing_required: list[str] = []
    invalid_keys: list[str] = []

    for key, spec in contract.variables.items():
        raw_value: str | None = None
        source: str | None = None

        system_value = os.environ.get(key)
        if system_value is not None and system_value != "":
            raw_value = system_value
            source = "system"
        elif key in profile_values:
            raw_value = profile_values[key]
            source = profile_source
        elif spec.default is not None:
            raw_value = str(spec.default)
            source = "default"

        if raw_value is None:
            if spec.required:
                missing_required.append(key)
            continue

        valid, detail = _is_valid_type(spec, raw_value)
        if not valid:
            invalid_keys.append(key)

        values[key] = ResolvedValue(
            key=key,
            value=raw_value,
            source=source or "unknown",
            masked=spec.sensitive,
            valid=valid,
            detail=detail,
        )

    unknown_keys = sorted(set(profile_values) - set(contract.variables))

    return ResolutionReport.from_parts(
        values=values,
        missing_required=sorted(missing_required),
        unknown_keys=unknown_keys,
        invalid_keys=sorted(invalid_keys),
    )
