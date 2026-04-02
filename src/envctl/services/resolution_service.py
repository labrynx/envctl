"""Resolution service."""

from __future__ import annotations

import csv
import json
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from io import StringIO
from urllib.parse import urlparse

from envctl.adapters.dotenv import load_env_file
from envctl.adapters.process_environment import ProcessEnvironmentProvider
from envctl.domain.contract import Contract, VariableSpec
from envctl.domain.expansion import (
    MAX_EXPANSION_DEPTH,
    ExpansionErrorInfo,
    ExpansionErrorType,
    ExpansionResult,
    LiteralSegment,
    Segment,
    parse_placeholder_segments,
)
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.repository.contract_repository import load_contract
from envctl.utils.project_paths import (
    build_profile_env_path,
    is_local_profile,
    normalize_profile_name,
)


@dataclass(frozen=True)
class _SelectedValue:
    """One raw selected value before expansion."""

    key: str
    raw_value: str
    source: str
    masked: bool


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


def _format_expansion_error(error: ExpansionErrorInfo) -> str:
    """Render one expansion error for user-facing output."""
    labels = {
        "syntax_error": "Expansion syntax error",
        "reference_resolution_error": "Expansion reference error",
        "cycle_error": "Expansion cycle error",
        "depth_exceeded_error": "Expansion depth error",
    }
    return f"{labels[error.kind]}: {error.detail}"


def _make_expansion_error_result(
    *,
    value: str,
    kind: ExpansionErrorType,
    detail: str,
    refs: tuple[str, ...] = (),
) -> ExpansionResult:
    """Build one failed expansion result."""
    return ExpansionResult(
        value=value,
        status="error",
        refs=refs,
        error=ExpansionErrorInfo(kind=kind, detail=detail),
    )


def _build_selected_values(
    contract: Contract,
    *,
    profile_values: dict[str, str],
    profile_source: str,
) -> tuple[dict[str, _SelectedValue], list[str]]:
    """Select raw values before expansion."""
    selected_values: dict[str, _SelectedValue] = {}
    missing_required: list[str] = []

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

        selected_values[key] = _SelectedValue(
            key=key,
            raw_value=raw_value,
            source=source or "unknown",
            masked=spec.sensitive,
        )

    return selected_values, missing_required


def _resolve_placeholder_value(
    *,
    contract: Contract,
    selected_values: dict[str, _SelectedValue],
    expanded: dict[str, ExpansionResult],
    derived_sensitive: dict[str, bool],
    external_provider: ProcessEnvironmentProvider,
    resolve_key: Callable[[str, int], ExpansionResult],
    current_key: str,
    placeholder_name: str,
    refs: list[str],
    depth: int,
) -> tuple[str | None, ExpansionResult | None, bool]:
    """Resolve one placeholder to a string or an error result."""
    if placeholder_name in contract.variables:
        referenced = selected_values.get(placeholder_name)
        if referenced is None:
            return (
                None,
                _make_expansion_error_result(
                    value=selected_values[current_key].raw_value,
                    kind="reference_resolution_error",
                    detail=f"Missing value for referenced key '{placeholder_name}'",
                    refs=tuple(refs),
                ),
                False,
            )

        nested = resolve_key(placeholder_name, depth + 1)
        if nested.error is not None:
            return (
                None,
                ExpansionResult(
                    value=selected_values[current_key].raw_value,
                    status="error",
                    refs=tuple(refs + list(nested.refs)),
                    error=nested.error,
                ),
                False,
            )

        inherited_sensitive = referenced.masked or derived_sensitive.get(placeholder_name, False)
        return nested.value, None, inherited_sensitive

    external_value = external_provider.get(placeholder_name)
    if external_value is None:
        return (
            None,
            _make_expansion_error_result(
                value=selected_values[current_key].raw_value,
                kind="reference_resolution_error",
                detail=f"Unknown placeholder '{placeholder_name}'",
                refs=tuple(refs),
            ),
            False,
        )

    return external_value, None, False


def _get_cached_or_guarded_result(
    *,
    key: str,
    depth: int,
    selected_values: dict[str, _SelectedValue],
    states: dict[str, str],
    expanded: dict[str, ExpansionResult],
) -> ExpansionResult | None:
    """Return one cached or immediate guard error before expanding."""
    if key in expanded:
        return expanded[key]

    if depth > MAX_EXPANSION_DEPTH:
        result = _make_expansion_error_result(
            value=selected_values[key].raw_value,
            kind="depth_exceeded_error",
            detail=f"Expansion depth exceeded for '{key}'",
        )
        expanded[key] = result
        return result

    state = states[key]
    if state == "visiting":
        result = _make_expansion_error_result(
            value=selected_values[key].raw_value,
            kind="cycle_error",
            detail=f"Cycle detected while expanding '{key}'",
            refs=(key,),
        )
        expanded[key] = result
        return result
    if state == "resolved":
        return expanded[key]

    return None


def _expand_segments(
    *,
    contract: Contract,
    current_key: str,
    segments: tuple[Segment, ...],
    selected_values: dict[str, _SelectedValue],
    expanded: dict[str, ExpansionResult],
    derived_sensitive: dict[str, bool],
    external_provider: ProcessEnvironmentProvider,
    resolve_key: Callable[[str, int], ExpansionResult],
    depth: int,
) -> tuple[ExpansionResult, bool]:
    """Expand one parsed segment sequence."""
    parts: list[str] = []
    refs: list[str] = []
    inherited_sensitive = False

    for segment in segments:
        if isinstance(segment, LiteralSegment):
            parts.append(segment.value)
            continue

        refs.append(segment.name)
        resolved_value, error_result, is_sensitive = _resolve_placeholder_value(
            contract=contract,
            selected_values=selected_values,
            expanded=expanded,
            derived_sensitive=derived_sensitive,
            external_provider=external_provider,
            resolve_key=resolve_key,
            current_key=current_key,
            placeholder_name=segment.name,
            refs=refs,
            depth=depth,
        )
        if error_result is not None:
            return error_result, inherited_sensitive

        inherited_sensitive = inherited_sensitive or is_sensitive
        parts.append(resolved_value or "")

    return (
        ExpansionResult(value="".join(parts), status="expanded", refs=tuple(refs)),
        inherited_sensitive,
    )


def _expand_selected_values(
    contract: Contract,
    selected_values: dict[str, _SelectedValue],
    *,
    external_provider: ProcessEnvironmentProvider,
) -> tuple[dict[str, ExpansionResult], dict[str, bool]]:
    """Expand all selected values using contract-aware references."""
    states: dict[str, str] = {key: "unvisited" for key in selected_values}
    expanded: dict[str, ExpansionResult] = {}
    derived_sensitive: dict[str, bool] = {key: False for key in selected_values}

    def resolve_key(key: str, depth: int) -> ExpansionResult:
        cached = _get_cached_or_guarded_result(
            key=key,
            depth=depth,
            selected_values=selected_values,
            states=states,
            expanded=expanded,
        )
        if cached is not None:
            return cached

        states[key] = "visiting"
        current = selected_values[key]
        segments, parse_error = parse_placeholder_segments(current.raw_value)
        if parse_error is not None:
            result = ExpansionResult(
                value=current.raw_value,
                status="error",
                refs=(),
                error=parse_error,
            )
            expanded[key] = result
            states[key] = "resolved"
            return result

        if all(isinstance(segment, LiteralSegment) for segment in segments):
            result = ExpansionResult(value=current.raw_value, status="none", refs=())
            expanded[key] = result
            states[key] = "resolved"
            return result

        result, inherited_sensitive = _expand_segments(
            contract=contract,
            current_key=key,
            segments=segments,
            selected_values=selected_values,
            expanded=expanded,
            derived_sensitive=derived_sensitive,
            external_provider=external_provider,
            resolve_key=resolve_key,
            depth=depth,
        )
        derived_sensitive[key] = inherited_sensitive
        expanded[key] = result
        states[key] = "resolved"
        return result

    for key in sorted(selected_values):
        resolve_key(key, 0)

    return expanded, derived_sensitive


def _build_resolved_value(
    *,
    key: str,
    spec: VariableSpec,
    selected: _SelectedValue,
    expanded: ExpansionResult,
    derived_sensitive: bool,
) -> tuple[ResolvedValue, bool]:
    """Build one final resolved value and report whether it is invalid."""
    valid = expanded.error is None
    detail: str | None = None

    if expanded.error is not None:
        detail = _format_expansion_error(expanded.error)
    else:
        valid, detail = _is_valid_type(spec, expanded.value)

    raw_value = None if spec.sensitive or derived_sensitive else selected.raw_value
    resolved_value = ResolvedValue(
        key=key,
        raw_value=raw_value,
        value=expanded.value,
        source=selected.source,
        masked=selected.masked or derived_sensitive,
        expansion_status=expanded.status,
        expansion_refs=expanded.refs,
        expansion_error=expanded.error,
        valid=valid,
        detail=detail,
    )
    return resolved_value, not valid


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
    selected_values, missing_required = _build_selected_values(
        contract,
        profile_values=profile_values,
        profile_source=profile_source,
    )

    expansion_results, derived_sensitive = _expand_selected_values(
        contract,
        selected_values,
        external_provider=ProcessEnvironmentProvider(),
    )

    values: dict[str, ResolvedValue] = {}
    invalid_keys: list[str] = []

    for key, selected in selected_values.items():
        spec = contract.variables[key]
        value, invalid = _build_resolved_value(
            key=key,
            spec=spec,
            selected=selected,
            expanded=expansion_results[key],
            derived_sensitive=derived_sensitive.get(key, False),
        )
        values[key] = value
        if invalid:
            invalid_keys.append(key)

    unknown_keys = sorted(set(profile_values) - set(contract.variables))

    return ResolutionReport.from_parts(
        values=values,
        missing_required=sorted(missing_required),
        unknown_keys=unknown_keys,
        invalid_keys=sorted(invalid_keys),
    )
