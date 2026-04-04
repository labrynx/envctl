"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

import envctl.adapters.git as git_adapters


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

    git_config_store: dict[str, str] = {}

    def fake_run_git(args: list[str], cwd: Path | None = None, check: bool = True) -> str:
        del cwd, check

        if args == ["rev-parse", "--show-toplevel"]:
            return str(repo)

        if args == ["remote", "get-url", "origin"]:
            return "git@github.com:labrynx/envctl.git"

        if args == ["config", "--local", "--get", "envctl.projectId"]:
            return git_config_store.get("envctl.projectId", "")

        if len(args) == 4 and args[:2] == ["config", "--local"]:
            key = args[2]
            value = args[3]
            git_config_store[key] = value
            return ""

        raise RuntimeError(f"Unexpected git args: {args}")

    monkeypatch.setattr(git_adapters, "_run_git", fake_run_git)


@pytest.fixture
def runner() -> CliRunner:
    """Return a CLI runner."""
    return CliRunner()


@pytest.fixture
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

    monkeypatch.chdir(repo)

    return repo
