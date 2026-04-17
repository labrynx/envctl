from __future__ import annotations

from envctl.cli.presenters.outputs.errors import build_error_output


def test_build_error_output() -> None:
    output = build_error_output(
        error_type="demo_error",
        message="Something failed",
        command="envctl demo",
        details={"reason": "boom"},
    )

    assert output.messages[0].level == "error"
    assert output.messages[0].err is True
    assert output.metadata["ok"] is False
    assert output.metadata["error"]["type"] == "demo_error"
    assert output.metadata["error"]["message"] == "Something failed"
    assert output.metadata["command"] == "envctl demo"
