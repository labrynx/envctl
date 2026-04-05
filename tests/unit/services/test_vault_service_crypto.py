# tests/unit/services/test_vault_service_crypto.py
from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.vault_service as vault_service_module
from envctl.errors import ExecutionError
from envctl.vault_crypto import VaultCrypto
from tests.support.contexts import make_project_context


def test_encrypt_raises_when_crypto_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(vault_crypto=None)

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    with pytest.raises(ExecutionError, match="Encryption is not enabled"):
        vault_service_module.run_vault_encrypt_project()


def test_encrypt_encrypts_plaintext_vault_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "vault" / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=key_path,
        vault_crypto=crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    _context, result = vault_service_module.run_vault_encrypt_project()

    assert result.encrypted_files == (values_path,)
    assert result.skipped_files == ()
    assert values_path.read_text(encoding="utf-8").startswith("ENVCTL-VAULT-V1:")


def test_encrypt_skips_already_encrypted_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "vault" / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    crypto.write_encrypted_file(values_path, "APP_NAME=demo\n")

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=key_path,
        vault_crypto=crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    _context, result = vault_service_module.run_vault_encrypt_project()

    assert result.encrypted_files == ()
    assert result.skipped_files == (values_path,)


def test_encrypt_raises_on_wrong_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    original_key_path = tmp_path / "original" / "master.key"
    original_key_path.parent.mkdir(parents=True, exist_ok=True)
    original_crypto = VaultCrypto.load_or_create(original_key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    original_crypto.write_encrypted_file(values_path, "APP_NAME=demo\n")

    wrong_key_path = tmp_path / "vault" / "master.key"
    wrong_crypto = VaultCrypto.load_or_create(wrong_key_path, protected_paths=())

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=wrong_key_path,
        vault_crypto=wrong_crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    with pytest.raises(ExecutionError, match="different project key"):
        vault_service_module.run_vault_encrypt_project()


def test_decrypt_raises_when_crypto_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(vault_crypto=None)

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    with pytest.raises(ExecutionError, match="Enable encryption"):
        vault_service_module.run_vault_decrypt_project()


def test_decrypt_restores_plaintext_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "vault" / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    crypto.write_encrypted_file(values_path, "APP_NAME=demo\n")

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=key_path,
        vault_crypto=crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    _context, result = vault_service_module.run_vault_decrypt_project()

    assert result.decrypted_files == (values_path,)
    assert result.skipped_files == ()
    assert values_path.read_text(encoding="utf-8") == "APP_NAME=demo\n"


def test_decrypt_skips_already_plaintext_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "vault" / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=key_path,
        vault_crypto=crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    _context, result = vault_service_module.run_vault_decrypt_project()

    assert result.decrypted_files == ()
    assert result.skipped_files == (values_path,)


def test_encrypt_then_decrypt_full_roundtrip(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "vault" / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "vault" / "values.env"
    values_path.parent.mkdir(parents=True, exist_ok=True)
    values_path.write_text("APP_NAME=demo\nDEBUG=true\n", encoding="utf-8")

    context = make_project_context(
        vault_project_dir=values_path.parent,
        vault_values_path=values_path,
        vault_key_path=key_path,
        vault_crypto=crypto,
    )

    monkeypatch.setattr(
        vault_service_module,
        "load_project_context",
        lambda: (object(), context),
    )

    vault_service_module.run_vault_encrypt_project()
    encrypted_text = values_path.read_text(encoding="utf-8")
    assert encrypted_text.startswith("ENVCTL-VAULT-V1:")

    vault_service_module.run_vault_decrypt_project()
    assert values_path.read_text(encoding="utf-8") == "APP_NAME=demo\nDEBUG=true\n"
