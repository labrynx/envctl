"""Environment resolution helpers."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse

from envctl.domain.contract import Contract, VariableSpec
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.repository.contract_repository import load_contract
from envctl.utils.dotenv import load_env_file


def _is_valid_type(spec: VariableSpec, value: str) -> tuple[bool, str | None]:
    """Validate one value against its declared type."""
    if spec.choices and value not in spec.choices:
        return False, f"Expected one of: {', '.join(spec.choices)}"

    if spec.pattern:
        if re.fullmatch(spec.pattern, value) is None:
            return False, f"Value does not match pattern: {spec.pattern}"

    if spec.type == "string":
        return True, None

    if spec.type == "int":
        try:
            int(value)
        except ValueError:
            return False, "Expected an integer"
        return True, None

    if spec.type == "bool":
        normalized = value.lower()
        if normalized not in {"true", "false", "1", "0", "yes", "no"}:
            return False, "Expected a boolean"
        return True, None

    if spec.type == "url":
        parsed = urlparse(value)
        if not parsed.scheme or not parsed.netloc:
            return False, "Expected a valid URL"
        return True, None

    return False, f"Unsupported type: {spec.type}"


def load_contract_for_context(context: ProjectContext) -> Contract:
    """Load the contract for the current project."""
    return load_contract(context.repo_contract_path)


def resolve_environment(context: ProjectContext, contract: Contract) -> ResolutionReport:
    """Resolve environment values from the current sources."""
    vault_values = load_env_file(context.vault_values_path)
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
        elif key in vault_values:
            raw_value = vault_values[key]
            source = "vault"
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

    unknown_keys = sorted(set(vault_values) - set(contract.variables))

    return ResolutionReport(
        values=values,
        missing_required=sorted(missing_required),
        unknown_keys=unknown_keys,
        invalid_keys=sorted(invalid_keys),
    )
