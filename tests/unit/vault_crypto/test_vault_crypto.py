# tests/unit/vault_crypto/test_vault_crypto.py
from __future__ import annotations

from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from envctl.constants import MASTER_KEY_FORMAT_VERSION
from envctl.errors import ExecutionError
from envctl.vault_crypto import (
    VaultCrypto,
    VaultDecryptionError,
    derive_master_key_id,
    parse_master_key_material,
    serialize_master_key_v1,
)


def test_load_or_create_generates_key_on_first_call(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"

    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    assert isinstance(crypto, VaultCrypto)
    assert key_path.exists()


def test_load_or_create_key_has_restrictive_permissions(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"

    VaultCrypto.load_or_create(key_path, protected_paths=())

    mode = key_path.stat().st_mode & 0o777
    assert mode == 0o400


def test_load_or_create_refuses_to_replace_missing_key_when_encrypted_data_exists(
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "master.key"
    encrypted_file = tmp_path / "values.env"

    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())
    crypto.write_encrypted_file(encrypted_file, "APP_NAME=demo\n")

    key_path.unlink()

    with pytest.raises(ExecutionError, match=r"encrypted vault data already exists"):
        VaultCrypto.load_or_create(key_path, protected_paths=(encrypted_file,))


def test_load_or_create_returns_same_key_on_second_call(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"

    crypto1 = VaultCrypto.load_or_create(key_path, protected_paths=())
    crypto2 = VaultCrypto.load_or_create(key_path, protected_paths=())

    plaintext = "APP_NAME=demo\n"
    token = crypto1.encrypt(plaintext)
    assert crypto2.decrypt(token) == plaintext


def test_encrypt_decrypt_round_trip(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    plaintext = "APP_NAME=demo\nDEBUG=true\n"
    token = crypto.encrypt(plaintext)

    assert crypto.decrypt(token) == plaintext


def test_encrypt_produces_bytes_with_envelope(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    token = crypto.encrypt("APP_NAME=demo\n")

    assert isinstance(token, bytes)
    assert token.startswith(b"ENVCTL-VAULT-V1:")


def test_decrypt_raises_on_invalid_payload(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    with pytest.raises(VaultDecryptionError):
        crypto.decrypt(b"not-a-valid-payload")


def test_decrypt_raises_on_wrong_key(tmp_path: Path) -> None:
    key_path1 = tmp_path / "master-1.key"
    key_path2 = tmp_path / "master-2.key"

    crypto1 = VaultCrypto.load_or_create(key_path1, protected_paths=())
    crypto2 = VaultCrypto.load_or_create(key_path2, protected_paths=())

    token = crypto1.encrypt("APP_NAME=demo\n")

    with pytest.raises(VaultDecryptionError, match=r"different project key"):
        crypto2.decrypt(token)


def test_inspect_bytes_distinguishes_wrong_key_from_corruption(tmp_path: Path) -> None:
    key_path1 = tmp_path / "master-1.key"
    key_path2 = tmp_path / "master-2.key"

    crypto1 = VaultCrypto.load_or_create(key_path1, protected_paths=())
    crypto2 = VaultCrypto.load_or_create(key_path2, protected_paths=())

    token = crypto1.encrypt("APP_NAME=demo\n")

    wrong_key_inspection = crypto2.inspect_bytes(token)
    assert wrong_key_inspection.state == "wrong_key"

    corrupt_token = token[:-8] + b"corrupted"
    corrupt_inspection = crypto1.inspect_bytes(corrupt_token)
    assert corrupt_inspection.state == "corrupt"


def test_read_file_accepts_plaintext_during_migration(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "values.env"
    values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    assert crypto.read_file(values_path, allow_plaintext=True) == "APP_NAME=demo\n"


def test_write_encrypted_file_and_read_file_round_trip(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "values.env"
    crypto.write_encrypted_file(values_path, "APP_NAME=demo\nDEBUG=true\n")

    assert values_path.read_bytes().startswith(b"ENVCTL-VAULT-V1:")
    assert crypto.read_file(values_path) == "APP_NAME=demo\nDEBUG=true\n"


def test_write_encrypted_file_permissions(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    values_path = tmp_path / "values.env"
    crypto.write_encrypted_file(values_path, "APP_NAME=demo\n")

    mode = values_path.stat().st_mode & 0o777
    assert mode == 0o600


def test_encrypt_different_tokens_for_same_plaintext(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    plaintext = "APP_NAME=demo\n"

    token1 = crypto.encrypt(plaintext)
    token2 = crypto.encrypt(plaintext)

    assert token1 != token2
    assert crypto.decrypt(token1) == plaintext
    assert crypto.decrypt(token2) == plaintext


def test_parse_master_key_material_accepts_canonical_format(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    material = parse_master_key_material(key_path.read_bytes())

    assert material.format == "v1"
    assert material.key_id == crypto.key_id
    assert material.key_bytes == serialize_master_key_v1(material.key_bytes).split(b":", 2)[2]


def test_parse_master_key_material_accepts_legacy_format(tmp_path: Path) -> None:
    legacy_key = Fernet.generate_key()

    material = parse_master_key_material(legacy_key)

    assert material.format == "legacy"
    assert material.key_id == derive_master_key_id(legacy_key)
    assert material.key_bytes == legacy_key


def test_parse_master_key_material_rejects_invalid_content() -> None:
    with pytest.raises(ExecutionError, match="Invalid master key material"):
        parse_master_key_material(b"not-a-key")


def test_serialize_master_key_v1_is_canonical() -> None:
    key_bytes = Fernet.generate_key()

    serialized = serialize_master_key_v1(key_bytes)

    assert serialized.startswith(f"{MASTER_KEY_FORMAT_VERSION}:".encode())
    assert serialized.endswith(key_bytes)


def test_load_or_create_migrates_legacy_key_file(tmp_path: Path) -> None:
    key_path = tmp_path / "master.key"
    legacy_key = Fernet.generate_key()
    key_path.write_bytes(legacy_key)

    crypto = VaultCrypto.load_or_create(key_path, protected_paths=())

    assert crypto.key_id == derive_master_key_id(legacy_key)
    assert key_path.read_bytes().startswith(f"{MASTER_KEY_FORMAT_VERSION}:".encode())
    assert any(w.kind == "legacy_master_key_migrated" for w in crypto.runtime_warnings)
