from __future__ import annotations

from envctl.cli.commands.inspect import inspect_command
from envctl.domain.resolution import ResolutionReport


def test_inspect_command_renders_resolution(monkeypatch) -> None:
    report = ResolutionReport(
        values={},
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )
    called: dict[str, object] = {}

    monkeypatch.setattr(
        "envctl.cli.commands.inspect.command.run_inspect",
        lambda: ("context", report),
    )
    monkeypatch.setattr(
        "envctl.cli.commands.inspect.command.render_resolution",
        lambda value: called.update({"report": value}),
    )

    inspect_command()

    assert called["report"] is report
