from __future__ import annotations

from envctl.cli.presenters.outputs.warnings import (
    build_command_warnings_output,
    build_contract_deprecation_warnings_output,
)
from tests.unit.cli.presenters.support.factories import (
    make_command_warning,
    make_contract_deprecation_warning,
)


def test_build_contract_deprecation_warnings_output_empty() -> None:
    output = build_contract_deprecation_warnings_output([])
    assert output.metadata["kind"] == "contract_deprecation_warnings"
    assert output.metadata["warnings"] == []


def test_build_contract_deprecation_warnings_output_with_values() -> None:
    warnings = [make_contract_deprecation_warning()]
    output = build_contract_deprecation_warnings_output(warnings, stderr=True)

    assert output.messages[0].level == "warning"
    assert output.messages[0].err is True
    assert output.sections[0].title == "Deprecation warnings"


def test_build_command_warnings_output_empty() -> None:
    output = build_command_warnings_output([])
    assert output.metadata["kind"] == "command_warnings"
    assert output.metadata["warnings"] == []


def test_build_command_warnings_output_with_values() -> None:
    warnings = [make_command_warning()]
    output = build_command_warnings_output(warnings)

    assert output.messages[0].level == "warning"
    assert output.sections[0].title == "Warnings"
