"""Unit tests for the crypto-aware I/O in profile_repository."""

from __future__ import annotations

from pathlib import Path

import pytest

import envctl.repository.profile_repository as repo
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.vault_crypto import VaultCrypto
from tests.support.contexts import make_project_context


def _make_context(
    tmp_path: Path,
    *,
    crypto: VaultCrypto | None = None,
) -> ProjectContext:
    return make_project_context(
        vault_project_dir=tmp_path / "vault",
        vault_values_path=tmp_path / "vault" / "values.env",
        vault_crypto=crypto,
    )


def test_write_profile_values_encrypts_content(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    context = _make_context(tmp_path, crypto=crypto)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)

    repo.write_profile_values(context, "local", {"SECRET": "topsecret"})

    raw_bytes = context.vault_values_path.read_bytes()
    assert b"topsecret" not in raw_bytes
    assert VaultCrypto.looks_encrypted(raw_bytes) is True


def test_load_profile_values_decrypts_content(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    context = _make_context(tmp_path, crypto=crypto)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)

    repo.write_profile_values(context, "local", {"SECRET": "topsecret", "PORT": "8080"})
    _profile, _path, values = repo.load_profile_values(context, "local")

    assert values == {"SECRET": "topsecret", "PORT": "8080"}


def test_write_and_load_explicit_profile_with_encryption(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    context = _make_context(tmp_path, crypto=crypto)
    profiles_dir = tmp_path / "vault" / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "staging.env").write_bytes(b"")

    repo.write_profile_values(context, "staging", {"STAGE": "production"})
    _profile, _path, values = repo.load_profile_values(context, "staging")

    assert values == {"STAGE": "production"}


def test_write_without_crypto_writes_plaintext(tmp_path: Path) -> None:
    context = _make_context(tmp_path, crypto=None)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)

    repo.write_profile_values(context, "local", {"KEY": "plainval"})

    raw = context.vault_values_path.read_text(encoding="utf-8")
    assert "plainval" in raw


def test_load_plaintext_file_when_encryption_enabled_supports_migration(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    context = _make_context(tmp_path, crypto=crypto)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("KEY=plain\n", encoding="utf-8")

    _profile, _path, values = repo.load_profile_values(context, "local")

    assert values == {"KEY": "plain"}


def test_load_encrypted_file_when_encryption_disabled_raises(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    encrypted_context = _make_context(tmp_path, crypto=crypto)
    encrypted_context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    repo.write_profile_values(encrypted_context, "local", {"KEY": "secret"})

    plain_context = _make_context(tmp_path, crypto=None)

    with pytest.raises(ExecutionError, match="Vault file is encrypted"):
        repo.load_profile_values(plain_context, "local")


def test_remove_key_from_profile_with_encryption(tmp_path: Path) -> None:
    crypto = VaultCrypto.load_or_create(tmp_path / "master.key")
    context = _make_context(tmp_path, crypto=crypto)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)

    repo.write_profile_values(context, "local", {"A": "1", "B": "2"})
    _profile, _path, removed = repo.remove_key_from_profile(context, "local", "A")

    assert removed is True
    _profile, _path, values = repo.load_profile_values(context, "local")
    assert "A" not in values
    assert values["B"] == "2"
