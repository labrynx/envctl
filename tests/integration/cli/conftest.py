from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_cli_home(
    monkeypatch: pytest.MonkeyPatch,
    workspace: Path,
) -> None:
    """Force CLI integration tests to use an isolated fake home directory."""
    fake_home = workspace.parent / "home"
    fake_config_home = fake_home / ".config"

    fake_home.mkdir(parents=True, exist_ok=True)
    fake_config_home.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(fake_config_home))

    monkeypatch.setattr(Path, "home", lambda: fake_home)