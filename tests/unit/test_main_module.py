from __future__ import annotations

import runpy

import pytest


def test_main_module_invokes_app(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"count": 0}

    def fake_app() -> None:
        called["count"] += 1

    monkeypatch.setattr("envctl.cli.app.app", fake_app)

    runpy.run_module("envctl.__main__", run_name="__main__")

    assert called["count"] == 1
