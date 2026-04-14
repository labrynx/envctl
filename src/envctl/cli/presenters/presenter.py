from __future__ import annotations

from typing import Literal

from envctl.cli.presenters.models import CommandOutput
from envctl.cli.presenters.renderers.json import emit_json
from envctl.cli.presenters.renderers.text import emit_text

OutputFormat = Literal["text", "json"]


def present(
    output: CommandOutput,
    *,
    output_format: OutputFormat = "text",
) -> None:
    """Render one command output using the selected output format."""
    if output_format == "json":
        emit_json(output)
        return

    emit_text(output)