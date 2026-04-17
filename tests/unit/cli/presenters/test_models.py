from __future__ import annotations

from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputMessage, OutputSection


def test_output_message_defaults() -> None:
    message = OutputMessage(level="info", text="hello")
    assert message.level == "info"
    assert message.text == "hello"
    assert message.err is False


def test_output_item_defaults() -> None:
    item = OutputItem(kind="raw", text="hello")
    assert item.kind == "raw"
    assert item.text == "hello"
    assert item.value is None
    assert item.err is False


def test_output_section_defaults() -> None:
    section = OutputSection(title="Section")
    assert section.title == "Section"
    assert section.items == []
    assert section.err is False


def test_command_output_defaults() -> None:
    output = CommandOutput()
    assert output.title is None
    assert output.messages == []
    assert output.sections == []
    assert output.metadata == {}
