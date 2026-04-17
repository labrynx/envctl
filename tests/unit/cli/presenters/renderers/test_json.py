from __future__ import annotations

import json

from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputMessage, OutputSection
from envctl.cli.presenters.renderers.json import build_json_payload, emit_json


def test_build_json_payload() -> None:
    output = CommandOutput(
        title="Demo",
        messages=[OutputMessage(level="success", text="done")],
        sections=[
            OutputSection(
                title="Details",
                items=[OutputItem(kind="field", text="profile", value="local")],
            )
        ],
        metadata={"kind": "demo"},
    )

    payload = build_json_payload(output)

    assert payload["title"] == "Demo"
    assert payload["messages"][0]["text"] == "done"
    assert payload["sections"][0]["title"] == "Details"
    assert payload["metadata"]["kind"] == "demo"


def test_emit_json(monkeypatch) -> None:
    captured: list[str] = []

    def fake_echo(value: str) -> None:
        captured.append(value)

    monkeypatch.setattr("envctl.cli.presenters.renderers.json.typer.echo", fake_echo)

    emit_json(CommandOutput(metadata={"kind": "demo"}))

    assert len(captured) == 1
    assert json.loads(captured[0])["metadata"]["kind"] == "demo"
