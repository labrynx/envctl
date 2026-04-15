"""Output builders for warnings."""

from __future__ import annotations

from collections.abc import Sequence

from envctl.cli.presenters.common import bullet_item, section, warning_message
from envctl.cli.presenters.models import CommandOutput
from envctl.cli.presenters.payloads import (
    serialize_command_warnings,
    serialize_contract_deprecation_warnings,
)
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning


def build_contract_deprecation_warnings_output(
    warnings: Sequence[ContractDeprecationWarning],
    *,
    stderr: bool = False,
) -> CommandOutput:
    """Build unified output for contract deprecation warnings."""
    if not warnings:
        return CommandOutput(
            metadata={
                "kind": "contract_deprecation_warnings",
                "warnings": [],
            }
        )

    payload = serialize_contract_deprecation_warnings(warnings)

    return CommandOutput(
        messages=[warning_message(warning.message, err=stderr) for warning in warnings],
        sections=[
            section(
                "Deprecation warnings",
                *(bullet_item(warning.message, err=stderr) for warning in warnings),
                err=stderr,
            )
        ],
        metadata={
            "kind": "contract_deprecation_warnings",
            "warnings": payload,
        },
    )


def build_command_warnings_output(
    warnings: Sequence[CommandWarning],
) -> CommandOutput:
    """Build unified output for command warnings."""
    if not warnings:
        return CommandOutput(
            metadata={
                "kind": "command_warnings",
                "warnings": [],
            }
        )

    payload = serialize_command_warnings(warnings)

    return CommandOutput(
        messages=[warning_message(warning.message) for warning in warnings],
        sections=[
            section(
                "Warnings",
                *(bullet_item(warning.message) for warning in warnings),
            )
        ],
        metadata={
            "kind": "command_warnings",
            "warnings": payload,
        },
    )
