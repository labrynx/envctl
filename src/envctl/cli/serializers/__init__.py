"""JSON serializers for CLI output."""

from envctl.cli.serializers.common import emit_json
from envctl.cli.serializers.context import serialize_project_context
from envctl.cli.serializers.diagnostics import (
    serialize_config_diagnostics,
    serialize_contract_diagnostics,
    serialize_error_diagnostics,
    serialize_project_binding_diagnostics,
    serialize_projection_validation_diagnostics,
    serialize_repository_discovery_diagnostics,
    serialize_state_diagnostics,
)
from envctl.cli.serializers.doctor import serialize_doctor_checks
from envctl.cli.serializers.errors import serialize_error
from envctl.cli.serializers.resolution import (
    serialize_resolution_report,
    serialize_resolved_value,
)
from envctl.cli.serializers.status import serialize_status_report

__all__ = [
    "emit_json",
    "serialize_config_diagnostics",
    "serialize_contract_diagnostics",
    "serialize_doctor_checks",
    "serialize_error",
    "serialize_error_diagnostics",
    "serialize_project_binding_diagnostics",
    "serialize_project_context",
    "serialize_projection_validation_diagnostics",
    "serialize_repository_discovery_diagnostics",
    "serialize_resolution_report",
    "serialize_resolved_value",
    "serialize_state_diagnostics",
    "serialize_status_report",
]
