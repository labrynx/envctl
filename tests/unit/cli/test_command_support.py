from __future__ import annotations

from envctl.cli.command_support import (
    build_command_warnings_payload,
    build_json_command_payload,
    normalize_bool_flags,
)
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import CommandWarning


def test_normalize_bool_flags_coerces_values_to_plain_bools() -> None:
    assert normalize_bool_flags(True, False) == (True, False)


def test_build_command_warnings_payload_preserves_warning_order() -> None:
    contract_warning = ContractDeprecationWarning(
        key="APP_NAME",
        deprecated_field="group",
        message="Use groups instead.",
    )
    command_warning = CommandWarning(kind="deprecated_command", message="Deprecated command.")
    extra_warning = CommandWarning(kind="advisory", message="Extra warning.")

    payload = build_command_warnings_payload(
        contract_warnings=(contract_warning,),
        command_warnings=(command_warning,),
        extra_warnings=(extra_warning,),
    )

    assert [item["message"] for item in payload] == [
        "Use groups instead.",
        "Deprecated command.",
        "Extra warning.",
    ]


def test_build_json_command_payload_injects_warnings_field() -> None:
    payload = build_json_command_payload(
        command="status",
        data={"summary": "ok"},
    )

    assert payload == {
        "ok": True,
        "command": "status",
        "data": {
            "summary": "ok",
            "warnings": [],
        },
    }


def test_build_json_command_payload_includes_schema_version_when_requested() -> None:
    payload = build_json_command_payload(
        command="hooks status",
        schema_version=1,
        data={"overall_status": "healthy"},
    )

    assert payload["schema_version"] == 1
