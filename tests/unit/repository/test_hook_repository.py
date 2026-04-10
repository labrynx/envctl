from __future__ import annotations

from pathlib import Path

import pytest

from envctl.repository.hook_repository import HookRepository


def test_ensure_executable_is_noop_on_windows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "hook"
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    repository = HookRepository()

    monkeypatch.setattr(repository, "_is_windows", lambda: True)

    repository.ensure_executable(path)

    assert path.exists()
