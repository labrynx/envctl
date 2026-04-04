from __future__ import annotations

import csv
import json
import re
from io import StringIO
from urllib.parse import urlparse

from envctl.domain.contract import VariableSpec


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


def _validate_string_format(
    spec: VariableSpec,
    value: str,
) -> tuple[bool, str | None]:
    """Validate semantic format hints for string-typed variables."""
    if spec.format is None:
        return True, None

    if spec.format == "json":
        return _validate_json(value)
    if spec.format == "url":
        return _validate_url(value)
    return _validate_csv(value)


def validate_value_against_spec(
    spec: VariableSpec,
    value: str,
) -> tuple[bool, str | None]:
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
