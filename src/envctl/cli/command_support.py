"""Shared helpers for canonical CLI command orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from envctl.cli.presenters.outputs.warnings import build_contract_deprecation_warnings_output
from envctl.cli.presenters.payloads import build_command_warnings_payload
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning


def normalize_bool_flags(*values: bool) -> tuple[bool, ...]:
    """Normalize Typer boolean options into plain booleans."""
    return tuple(value if isinstance(value, bool) else False for value in values)


def build_json_command_payload(
    *,
    command: str,
    data: Mapping[str, Any],
    ok: bool = True,
    schema_version: int | None = None,
    contract_warnings: Sequence[ContractDeprecationWarning] = (),
    command_warnings: Sequence[CommandWarning] = (),
    extra_warnings: Sequence[CommandWarning] = (),
) -> dict[str, Any]:
    """Build one canonical JSON command payload."""
    payload_data = dict(data)
    payload_data["warnings"] = build_command_warnings_payload(
        contract_warnings=contract_warnings,
        command_warnings=command_warnings,
        extra_warnings=extra_warnings,
    )
    payload: dict[str, Any] = {
        "ok": ok,
        "command": command,
        "data": payload_data,
    }
    if schema_version is not None:
        payload["schema_version"] = schema_version
    return payload


def render_contract_warnings_if_any(
    warnings: Sequence[ContractDeprecationWarning],
    *,
    stderr: bool = False,
) -> None:
    """Render contract deprecation warnings when present."""
    if warnings:
        build_contract_deprecation_warnings_output(warnings, stderr=stderr)
