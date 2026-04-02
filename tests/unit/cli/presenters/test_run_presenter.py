"""Tests for run presenter."""

from __future__ import annotations

import pytest

from envctl.cli.presenters.run_presenter import render_run_warnings


def test_render_run_warnings_uses_warning_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_run_warnings(("docker forwarding required",))
    captured = capsys.readouterr().out

    assert captured == "[WARN] docker forwarding required\n"


def test_render_run_warnings_skips_empty_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_run_warnings(())
    captured = capsys.readouterr().out

    assert captured == ""
