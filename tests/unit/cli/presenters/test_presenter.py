from __future__ import annotations

from envctl.cli.presenters.models import CommandOutput
from envctl.cli.presenters.presenter import present


def test_present_uses_json_renderer(monkeypatch) -> None:
    called = {"json": False, "text": False}

    def fake_json(output: CommandOutput) -> None:
        called["json"] = True

    def fake_text(output: CommandOutput) -> None:
        called["text"] = True

    monkeypatch.setattr("envctl.cli.presenters.presenter.emit_json", fake_json)
    monkeypatch.setattr("envctl.cli.presenters.presenter.emit_text", fake_text)

    present(CommandOutput(), output_format="json")

    assert called == {"json": True, "text": False}


def test_present_uses_text_renderer(monkeypatch) -> None:
    called = {"json": False, "text": False}

    def fake_json(output: CommandOutput) -> None:
        called["json"] = True

    def fake_text(output: CommandOutput) -> None:
        called["text"] = True

    monkeypatch.setattr("envctl.cli.presenters.presenter.emit_json", fake_json)
    monkeypatch.setattr("envctl.cli.presenters.presenter.emit_text", fake_text)

    present(CommandOutput(), output_format="text")

    assert called == {"json": False, "text": True}
