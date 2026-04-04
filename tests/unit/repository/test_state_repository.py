from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import envctl.repository.state_repository as state_repository
from envctl.errors import StateError
from envctl.repository.state_repository import read_state, upsert_state, write_state
from tests.support.assertions import require_state_diagnostics


def test_read_state_returns_none_when_file_is_missing(tmp_path: Path) -> None:
    path = tmp_path / "state.json"

    assert read_state(path) is None


def test_write_state_creates_valid_minimal_state(tmp_path: Path) -> None:
    path = tmp_path / "state.json"

    write_state(
        path,
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root="/tmp/demo",
    )

    payload = read_state(path)
    assert payload is not None
    assert payload["project_slug"] == "demo"
    assert payload["project_key"] == "demo"
    assert payload["project_id"] == "prj_aaaaaaaaaaaaaaaa"
    assert payload["repo_root"] == "/tmp/demo"
    assert payload["known_paths"] == ["/tmp/demo"]


def test_upsert_state_preserves_created_at_and_updates_last_seen(tmp_path: Path) -> None:
    path = tmp_path / "state.json"

    write_state(
        path,
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root="/tmp/demo",
    )
    previous = read_state(path)
    assert previous is not None

    upsert_state(
        path,
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root="/tmp/demo",
        git_remote="git@github.com:labrynx/envctl.git",
    )

    updated = read_state(path)
    assert updated is not None
    assert updated["created_at"] == previous["created_at"]
    assert updated["git_remote"] == "git@github.com:labrynx/envctl.git"
    assert "/tmp/demo" in updated["known_paths"]


def test_read_state_raises_on_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(StateError, match=r"State file is corrupted") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "corrupted_state"
    assert diagnostics.path == path


def test_read_state_raises_on_invalid_shape(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(StateError, match=r"State file must contain a JSON object") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_state_shape"
    assert diagnostics.field == "root"


def test_read_state_raises_when_file_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "state.json"
    path.write_text("{}", encoding="utf-8")

    def broken_read_text(*args: Any, **kwargs: Any) -> str:
        raise OSError("boom")

    monkeypatch.setattr(state_repository.Path, "read_text", broken_read_text)

    with pytest.raises(StateError, match=r"Unable to read state file") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "unreadable_state"


def test_read_state_raises_on_unsupported_state_version_with_structured_diagnostics(
    tmp_path: Path,
) -> None:
    path = tmp_path / "state.json"
    path.write_text('{"version": 999}', encoding="utf-8")

    with pytest.raises(StateError, match=r"Unsupported state version") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "unsupported_state_version"
    assert diagnostics.field == "version"


def test_read_state_raises_when_required_field_is_missing(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text(
        '{"version": 2, "project_slug": "demo", "project_key": "demo", "repo_root": "/tmp/demo"}',
        encoding="utf-8",
    )

    with pytest.raises(StateError, match=r"missing a valid project_id") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "missing_required_field"
    assert diagnostics.field == "project_id"


def test_read_state_raises_on_invalid_known_paths(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    path.write_text(
        (
            '{"version": 2, "project_slug": "demo", "project_key": "demo", '
            '"project_id": "prj_aaaaaaaaaaaaaaaa", "repo_root": "/tmp/demo", '
            '"known_paths": "not-a-list"}'
        ),
        encoding="utf-8",
    )

    with pytest.raises(StateError, match=r"invalid known_paths") as exc_info:
        read_state(path)

    diagnostics = require_state_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_known_paths"
    assert diagnostics.field == "known_paths"
