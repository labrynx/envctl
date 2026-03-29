from __future__ import annotations

import subprocess

import pytest

from envctl.adapters.editor import open_file, resolve_editor
from envctl.errors import ExecutionError


def test_resolve_editor_prefers_visual(monkeypatch) -> None:
    monkeypatch.setenv("VISUAL", "code --wait")
    monkeypatch.setenv("EDITOR", "nano")

    assert resolve_editor() == ["code", "--wait"]


def test_resolve_editor_uses_editor_when_visual_is_missing(monkeypatch) -> None:
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.setenv("EDITOR", "vim")

    assert resolve_editor() == ["vim"]


def test_resolve_editor_falls_back_to_available_binary(monkeypatch) -> None:
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/nano" if name == "nano" else None)

    assert resolve_editor() == ["/usr/bin/nano"]


def test_resolve_editor_raises_when_no_editor_found(monkeypatch) -> None:
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    monkeypatch.setattr("shutil.which", lambda name: None)

    with pytest.raises(ExecutionError, match="No editor found"):
        resolve_editor()


def test_open_file_runs_editor(monkeypatch) -> None:
    calls: dict[str, object] = {}

    monkeypatch.setattr("envctl.adapters.editor.resolve_editor", lambda: ["nano"])

    def fake_run(command: list[str], check: bool = False):
        calls["command"] = command
        calls["check"] = check
        return type("Completed", (), {"returncode": 0})()

    monkeypatch.setattr(subprocess, "run", fake_run)

    open_file("/tmp/demo.env")

    assert calls["command"] == ["nano", "/tmp/demo.env"]
    assert calls["check"] is False


def test_open_file_wraps_oserror(monkeypatch) -> None:
    monkeypatch.setattr("envctl.adapters.editor.resolve_editor", lambda: ["nano"])

    def fake_run(command: list[str], check: bool = False):
        raise OSError("boom")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ExecutionError, match="Failed to launch editor: nano"):
        open_file("/tmp/demo.env")


def test_open_file_raises_on_non_zero_exit(monkeypatch) -> None:
    monkeypatch.setattr("envctl.adapters.editor.resolve_editor", lambda: ["nano"])

    def fake_run(command: list[str], check: bool = False):
        return type("Completed", (), {"returncode": 2})()

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ExecutionError, match="Editor exited with code 2"):
        open_file("/tmp/demo.env")
