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

    (repo / ".envctl.yaml").write_text(
        yaml.safe_dump(schema, sort_keys=False),
        encoding="utf-8",
    )


def patch_git_for_repo(monkeypatch: pytest.MonkeyPatch, repo: Path) -> None:  # noqa: C901
    """Patch git helpers so tests operate inside an isolated repository."""

    git_config_store: dict[str, str] = {}

    def fake_run_git(
        args: list[str],
        cwd: Path | None = None,
        check: bool = True,
        text: bool = True,
    ) -> str | bytes:
        del cwd, check

        if args == ["rev-parse", "--show-toplevel"]:
            return str(repo)

        if args == ["rev-parse", "--absolute-git-dir"]:
            return str(repo / ".git")

        if args == ["rev-parse", "--git-path", "hooks"]:
            return git_config_store.get("core.hooksPath", ".git/hooks")

        if args == ["rev-parse", "--is-inside-work-tree"]:
            return "true"

        if args == ["remote", "get-url", "origin"]:
            return "git@github.com:labrynx/envctl.git"

        if args == ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]:
            return b"" if not text else ""

        if args == ["config", "--local", "--get", "envctl.projectId"]:
            return git_config_store.get("envctl.projectId", "")

        if args == ["config", "--local", "--get", "core.hooksPath"]:
            return git_config_store.get("core.hooksPath", "")

        if len(args) == 4 and args[:2] == ["config", "--local"]:
            key = args[2]
            value = args[3]
            git_config_store[key] = value
            return ""

        raise RuntimeError(f"Unexpected git args: {args}")

    monkeypatch.setattr(git_adapters, "_run_git", fake_run_git)


@pytest.fixture(autouse=True)
def reset_vault_crypto_runtime_state() -> None:
    """Reset VaultCrypto module-level runtime flags between tests."""
    from envctl.vault_crypto import VaultCrypto

    VaultCrypto._legacy_warning_emitted = False


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
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    monkeypatch.setattr(Path, "home", lambda: home)

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()

    patch_git_for_repo(monkeypatch, repo)
    write_sample_contract(repo)

    monkeypatch.chdir(repo)

    return repo
