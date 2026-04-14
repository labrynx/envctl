from __future__ import annotations

import json
from typing import Any

import typer

from envctl.cli.presenters.models import (
    CommandOutput,
    OutputItem,
    OutputMessage,
    OutputSection,
)


def _serialize_message(message: OutputMessage) -> dict[str, Any]:
    """Serialize one output message."""
    return {
        "level": message.level,
        "text": message.text,
        "err": message.err,
    }


def _serialize_item(item: OutputItem) -> dict[str, Any]:
    """Serialize one section item."""
    return {
        "kind": item.kind,
        "text": item.text,
        "value": item.value,
        "err": item.err,
    }


def _serialize_section(section: OutputSection) -> dict[str, Any]:
    """Serialize one output section."""
    return {
        "title": section.title,
        "err": section.err,
        "items": [_serialize_item(item) for item in section.items],
    }


def build_json_payload(output: CommandOutput) -> dict[str, Any]:
    """Build one JSON-serializable command payload."""
    return {
        "title": output.title,
        "messages": [_serialize_message(message) for message in output.messages],
        "sections": [_serialize_section(section) for section in output.sections],
        "metadata": output.metadata,
    }


def emit_json(output: CommandOutput) -> None:
    """Emit one command output as structured JSON."""
    typer.echo(json.dumps(build_json_payload(output), indent=2, sort_keys=True))
