from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from envctl.cli.presenters.outputs.guard import build_guard_secrets_output


def test_build_guard_secrets_output_ok() -> None:
    result = SimpleNamespace(
        ok=True,
        scanned_paths=[Path("/tmp/a"), Path("/tmp/b")],
        findings=[],
    )

    output = build_guard_secrets_output(result)

    assert output.messages[0].level == "success"
    assert output.metadata["ok"] is True
    assert output.metadata["kind"] == "guard_secrets"


def test_build_guard_secrets_output_fail() -> None:
    finding = SimpleNamespace(
        path=Path("/tmp/a"),
        kind="vault_key",
        message="secret detected",
        actions=["remove it", "rotate key"],
    )
    result = SimpleNamespace(
        ok=False,
        scanned_paths=[Path("/tmp/a")],
        findings=[finding],
    )

    output = build_guard_secrets_output(result)

    assert output.messages[0].level == "failure"
    assert output.metadata["ok"] is False
    assert output.sections[1].title == "Findings"
