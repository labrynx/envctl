"""JSON serializers for CLI output."""

from envctl.cli.serializers.check import serialize_check_result
from envctl.cli.serializers.common import emit_json
from envctl.cli.serializers.deprecations import serialize_contract_deprecation_warnings
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
from envctl.cli.serializers.inspect import serialize_inspect_key_result, serialize_inspect_result
from envctl.cli.serializers.status import serialize_status_report
from envctl.cli.serializers.warnings import serialize_command_warnings

__all__ = [
    "emit_json",
    "serialize_check_result",
    "serialize_command_warnings",
    "serialize_config_diagnostics",
    "serialize_contract_deprecation_warnings",
    "serialize_contract_diagnostics",
    "serialize_doctor_checks",
    "serialize_error",
    "serialize_error_diagnostics",
    "serialize_inspect_key_result",
    "serialize_inspect_result",
    "serialize_project_binding_diagnostics",
    "serialize_projection_validation_diagnostics",
    "serialize_repository_discovery_diagnostics",
    "serialize_state_diagnostics",
    "serialize_status_report",
]
