"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture()
def runner() -> CliRunner:
    """Return a CLI runner."""
    return CliRunner()


@pytest.fixture()
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create an isolated workspace with envctl defaults redirected."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))

    repo = tmp_path / "repo"
    repo.mkdir()

    git_dir = repo / ".git"
    git_dir.mkdir()

    def fake_run_git(args, cwd=None):
        if args == ["rev-parse", "--show-toplevel"]:
            return str(repo)
        if args == ["remote", "get-url", "origin"]:
            return "git@github.com:alessbarb/envctl.git"
        raise RuntimeError(f"Unexpected git args: {args}")

    monkeypatch.setattr("envctl.utils.git._run_git", fake_run_git)

    schema = {
        "version": 1,
        "variables": {
            "APP_NAME": {
                "type": "string",
                "required": True,
                "sensitive": False,
            },
            "PORT": {
                "type": "int",
                "required": True,
                "default": 3000,
                "sensitive": False,
            },
            "DATABASE_URL": {
                "type": "url",
                "required": True,
                "sensitive": True,
            },
        },
    }
    import yaml

    (repo / ".envctl.schema.yaml").write_text(
        yaml.safe_dump(schema, sort_keys=False), encoding="utf-8"
    )
    return repo
