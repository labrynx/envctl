from __future__ import annotations

from envctl.cli.compat.deprecated_commands import build_deprecated_command_warning


def test_build_deprecated_command_warning_uses_stable_message() -> None:
    warning = build_deprecated_command_warning(
        command_name="envctl doctor",
        replacement="envctl inspect",
        removal_version="v2.6.0",
    )

    assert warning.kind == "deprecated_command"
    assert "envctl doctor" in warning.message
    assert "envctl inspect" in warning.message
    assert "v2.6.0" in warning.message
