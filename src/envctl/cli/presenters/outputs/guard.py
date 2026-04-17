"""Output builders for guard commands."""

from __future__ import annotations

from typing import Any

from envctl.cli.presenters.common import (
    bullet_item,
    failure_message,
    field_item,
    section,
    success_message,
)
from envctl.cli.presenters.models import CommandOutput


def build_guard_secrets_output(result: Any) -> CommandOutput:
    """Build one unified output model for ``guard secrets``."""
    findings_payload = [
        {
            "path": str(finding.path),
            "kind": finding.kind,
            "message": finding.message,
            "actions": list(finding.actions),
        }
        for finding in result.findings
    ]

    if result.ok:
        return CommandOutput(
            messages=[success_message("No staged envctl secrets detected")],
            sections=[
                section(
                    "Guard",
                    field_item("scanned_paths", str(len(result.scanned_paths))),
                )
            ],
            metadata={
                "kind": "guard_secrets",
                "ok": True,
                "scanned_paths": [str(path) for path in result.scanned_paths],
                "findings": findings_payload,
            },
        )

    sections = [
        section(
            "Guard",
            field_item("scanned_paths", str(len(result.scanned_paths))),
        ),
        section(
            "Findings",
            *(
                item
                for finding in result.findings
                for item in (
                    bullet_item(f"{finding.path}: {finding.message}"),
                    *(bullet_item(f"action: {action}") for action in finding.actions),
                )
            ),
        ),
    ]

    return CommandOutput(
        messages=[failure_message("Staged envctl secrets detected")],
        sections=sections,
        metadata={
            "kind": "guard_secrets",
            "ok": False,
            "scanned_paths": [str(path) for path in result.scanned_paths],
            "findings": findings_payload,
        },
    )
