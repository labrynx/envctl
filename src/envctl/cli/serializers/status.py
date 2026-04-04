"""Status serializers."""

from __future__ import annotations

from typing import Any

from envctl.cli.serializers.common import path_to_str
from envctl.domain.status import StatusReport


def serialize_status_report(report: StatusReport) -> dict[str, Any]:
    """Serialize one status report."""
    return {
        "project_slug": report.project_slug,
        "project_id": report.project_id,
        "repo_root": path_to_str(report.repo_root),
        "contract_exists": report.contract_exists,
        "vault_exists": report.vault_exists,
        "resolved_valid": report.resolved_valid,
        "summary": report.summary,
        "issues": list(report.issues),
        "suggested_action": report.suggested_action,
    }
