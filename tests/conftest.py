"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner


def write_sample_contract(repo: Path) -> None:
    """Write a standard CLI integration contract into the repository."""
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

    (repo / ".envctl.schema.yaml").write_text(
        yaml.safe_dump(schema, sort_keys=False),
        encoding="utf-8",
    )


def patch_git_for_repo(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:
    """Patch git helpers so tests operate inside an isolated repository."""

    def fake_run_git(args: list[str], cwd: Path | None = None) -> str:
        if args == ["rev-parse", "--show-toplevel"]:
            return str(repo)
        if args == ["remote", "get-url", "origin"]:
            return "git@github.com:alessbarb/envctl.git"
        raise RuntimeError(f"Unexpected git args: {args}")

    monkeypatch.setattr("envctl.utils.git._run_git", fake_run_git)


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
    (repo / ".git").mkdir()

    patch_git_for_repo(monkeypatch, repo)
    write_sample_contract(repo)

    return repo
