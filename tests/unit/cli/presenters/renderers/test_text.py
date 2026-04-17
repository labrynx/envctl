from __future__ import annotations

from typing import Any

from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputMessage, OutputSection
from envctl.cli.presenters.renderers.text import emit_text


def test_emit_text_renders_title_messages_and_sections(monkeypatch) -> None:
    calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def fake_echo(*args, **kwargs):
        calls.append(("echo", args, kwargs))

    def fake_secho(*args, **kwargs):
        calls.append(("secho", args, kwargs))

    monkeypatch.setattr("envctl.cli.presenters.renderers.text.typer.echo", fake_echo)
    monkeypatch.setattr("envctl.cli.presenters.renderers.text.typer.secho", fake_secho)

    output = CommandOutput(
        title="Demo",
        messages=[OutputMessage(level="success", text="done")],
        sections=[
            OutputSection(
                title="Details",
                items=[
                    OutputItem(kind="field", text="profile", value="local"),
                    OutputItem(kind="bullet", text="next"),
                    OutputItem(kind="raw", text="raw line"),
                ],
            )
        ],
    )

    emit_text(output)

    assert calls
    assert any(call[0] == "secho" and call[1][0] == "Demo" for call in calls)
    assert any(call[0] == "secho" and "[OK] done" in call[1][0] for call in calls)
    assert any(call[0] == "secho" and call[1][0] == "Details" for call in calls)
    assert any(call[0] == "echo" and call[1] and "  - next" in call[1][0] for call in calls)
    assert any(call[0] == "echo" and call[1] and "raw line" in call[1][0] for call in calls)
