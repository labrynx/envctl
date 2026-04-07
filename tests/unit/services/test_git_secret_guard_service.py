from __future__ import annotations

import subprocess
from pathlib import Path

from cryptography.fernet import Fernet

from envctl.services.git_secret_guard_service import run_git_secret_guard
from envctl.vault_crypto import VaultCrypto
from tests.support.contexts import make_project_context


def _git(repo_root: Path, *args: str) -> None:
    # Intentional in tests: use git from PATH against a temporary local repository.
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def _init_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    _git(repo_root, "init")
    _git(repo_root, "config", "user.email", "test@example.com")
    _git(repo_root, "config", "user.name", "Test User")


def test_guard_detects_renamed_vault_payload(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    key_path = vault_dir / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    leaked_path = repo_root / "notes.txt"
    leaked_path.write_bytes(crypto.encrypt("APP_NAME=demo\n"))
    _git(repo_root, "add", "notes.txt")

    context = make_project_context(
        repo_root=repo_root, vault_project_dir=vault_dir, vault_key_path=key_path
    )
    result = run_git_secret_guard(context)

    assert not result.ok
    assert result.findings[0].kind == "vault_payload"
    assert result.findings[0].path == Path("notes.txt")


def test_guard_detects_canonical_master_key_even_when_renamed(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    key_path = vault_dir / "master.key"
    VaultCrypto.load_or_create(key_path, protected_paths=())
    canonical_key = key_path.read_bytes()

    leaked_path = repo_root / "rename.me"
    leaked_path.write_bytes(canonical_key)
    _git(repo_root, "add", "rename.me")

    context = make_project_context(
        repo_root=repo_root, vault_project_dir=vault_dir, vault_key_path=key_path
    )
    result = run_git_secret_guard(context)

    assert not result.ok
    assert result.findings[0].kind == "master_key"


def test_guard_detects_staged_legacy_master_key(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    _init_repo(repo_root)
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    key_path = vault_dir / "master.key"
    legacy_key = Fernet.generate_key()
    key_path.write_bytes(legacy_key)

    leaked_path = repo_root / "secret.bin"
    leaked_path.write_bytes(legacy_key)
    _git(repo_root, "add", "secret.bin")

    context = make_project_context(
        repo_root=repo_root, vault_project_dir=vault_dir, vault_key_path=key_path
    )
    result = run_git_secret_guard(context)

    assert not result.ok
    assert result.findings[0].kind == "legacy_master_key"
