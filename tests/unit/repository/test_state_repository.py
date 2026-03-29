from __future__ import annotations

from pathlib import Path

import pytest

from envctl.errors import StateError
from envctl.repository.state_repository import read_state, write_state


def test_write_state_persists_minimal_project_state(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"

    write_state(
        state_path,
        project_slug="demo-app",
        project_id="abc123",
        repo_root="/tmp/demo-app",
    )

    data = read_state(state_path)

    assert data == {
        "version": 1,
        "project_slug": "demo-app",
        "project_id": "abc123",
        "repo_root": "/tmp/demo-app",
    }


def test_read_state_returns_none_when_file_is_missing(tmp_path: Path) -> None:
    state_path = tmp_path / "missing.json"

    assert read_state(state_path) is None


def test_read_state_raises_when_json_is_invalid(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    state_path.write_text("{not-valid-json", encoding="utf-8")

    with pytest.raises(StateError, match="State file is corrupted"):
        read_state(state_path)


def test_read_state_raises_when_file_cannot_be_read(monkeypatch, tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    state_path.write_text("{}", encoding="utf-8")

    def broken_read_text(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(Path, "read_text", broken_read_text)

    with pytest.raises(StateError, match="Unable to read state file"):
        read_state(state_path)
