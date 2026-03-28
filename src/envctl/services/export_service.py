"""Export service."""

from __future__ import annotations

from envctl.errors import ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.shells import to_export_lines


def run_export() -> str:
    """Return shell export lines for the resolved environment."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)

    if not report.is_valid:
        raise ValidationError("Cannot export because the resolved environment is invalid")

    plain = {key: value.value for key, value in report.values.items()}
    return to_export_lines(plain)
