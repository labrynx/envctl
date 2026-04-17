from __future__ import annotations

from envctl.cli.presenters.common import (
    action_list_section,
    append_message,
    append_section,
    blank_item,
    bullet_item,
    bullet_items,
    cancelled_message,
    cancelled_output,
    error_message,
    failure_message,
    field_item,
    field_items,
    help_hint_section,
    info_message,
    merge_outputs,
    raw_item,
    result_summary_messages,
    result_summary_section,
    section,
    success_message,
    title_item,
    warning_message,
    warnings_section,
)
from envctl.cli.presenters.models import CommandOutput, OutputMessage, OutputSection


def test_merge_outputs_merges_messages_sections_and_metadata() -> None:
    left = CommandOutput(
        title="Primary",
        messages=[OutputMessage(level="info", text="left")],
        sections=[OutputSection(title="Left")],
        metadata={"kind": "left", "warnings": ["w1"], "command": "envctl check"},
    )
    right = CommandOutput(
        title="Secondary",
        messages=[OutputMessage(level="warning", text="right")],
        sections=[OutputSection(title="Right")],
        metadata={"kind": "right", "warnings": ["w2"], "command": "envctl status"},
    )

    merged = merge_outputs(left, right)

    assert merged.title == "Primary"
    assert [m.text for m in merged.messages] == ["left", "right"]
    assert [s.title for s in merged.sections] == ["Left", "Right"]
    assert merged.metadata["kind"] == "right"
    assert merged.metadata["warnings"] == ["w1", "w2"]
    assert merged.metadata["command"] == "envctl check"


def test_append_message_appends_only_when_present() -> None:
    messages: list[OutputMessage] = []
    append_message(messages, None)
    append_message(messages, info_message("hello"))
    assert [m.text for m in messages] == ["hello"]


def test_append_section_appends_only_when_present() -> None:
    sections: list[OutputSection] = []
    append_section(sections, None)
    append_section(sections, section("Demo"))
    assert [s.title for s in sections] == ["Demo"]


def test_item_builders() -> None:
    assert blank_item().text == ""
    assert title_item("Title").text == "Title"
    assert field_item("key", "value").value == "value"
    assert bullet_item("hello").kind == "bullet"
    assert raw_item("hello").kind == "raw"


def test_collection_item_builders() -> None:
    bullets = bullet_items(["a", "b"])
    fields = field_items([("a", "1"), ("b", "2")])

    assert [item.text for item in bullets] == ["a", "b"]
    assert [(item.text, item.value) for item in fields] == [("a", "1"), ("b", "2")]


def test_message_builders() -> None:
    assert info_message("i").level == "info"
    assert success_message("s").level == "success"
    assert warning_message("w").level == "warning"
    assert failure_message("f").level == "failure"
    assert error_message("e").level == "error"
    assert error_message("e").err is True


def test_action_list_section_returns_none_when_empty() -> None:
    assert action_list_section([]) is None


def test_action_list_section_builds_section() -> None:
    built = action_list_section(["envctl check", "envctl status"])
    assert built is not None
    assert built.title == "Next steps"
    assert [item.text for item in built.items] == [
        "Run `envctl check`",
        "Run `envctl status`",
    ]


def test_help_hint_section_uses_default_command() -> None:
    built = help_hint_section(None)
    assert built.title == "Next steps"
    assert built.items[0].text == "Run `envctl --help`"


def test_help_hint_section_uses_specific_command() -> None:
    built = help_hint_section("envctl inspect")
    assert built.items[0].text == "Run `envctl inspect --help`"


def test_result_summary_messages_success_and_warning() -> None:
    assert result_summary_messages("Done", success=True)[0].level == "success"
    assert result_summary_messages("Done", success=False)[0].level == "warning"


def test_result_summary_section_returns_none_when_empty() -> None:
    assert result_summary_section({}) is None


def test_result_summary_section_builds_fields() -> None:
    built = result_summary_section({"profile": "local"})
    assert built is not None
    assert built.title == "Details"
    assert built.items[0].text == "profile"
    assert built.items[0].value == "local"


def test_warnings_section_returns_none_when_empty() -> None:
    assert warnings_section([]) is None


def test_warnings_section_builds_items() -> None:
    built = warnings_section(["one", "two"])
    assert built is not None
    assert [item.text for item in built.items] == ["one", "two"]


def test_cancelled_message_and_output() -> None:
    message = cancelled_message()
    output = cancelled_output(kind="demo", reason="user")

    assert message.text == "Nothing was changed."
    assert output.messages[0].text == "Nothing was changed."
    assert output.metadata["kind"] == "demo"
    assert output.metadata["cancelled"] is True
    assert output.metadata["reason"] == "user"
