# tests/unit/cli/commands/vault/test_vault_encrypt.py
"""Unit tests for vault encrypt and decrypt CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import typer

import envctl.cli.commands.vault.commands.decrypt as decrypt_module
import envctl.cli.commands.vault.commands.encrypt as encrypt_module
from envctl.domain.operations import VaultDecryptResult, VaultEncryptResult
from envctl.errors import ExecutionError


def _make_encrypt_result(
    *,
    encrypted: tuple[Path, ...] = (),
    skipped: tuple[Path, ...] = (),
) -> VaultEncryptResult:
    return VaultEncryptResult(encrypted_files=encrypted, skipped_files=skipped)


def _make_decrypt_result(
    *,
    decrypted: tuple[Path, ...] = (),
    skipped: tuple[Path, ...] = (),
) -> VaultDecryptResult:
    return VaultDecryptResult(decrypted_files=decrypted, skipped_files=skipped)


# ---------------------------------------------------------------------------
# vault encrypt
# ---------------------------------------------------------------------------


def test_vault_encrypt_command_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    encrypted_path = Path("/tmp/vault/values.env")
    result = _make_encrypt_result(encrypted=(encrypted_path,))

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_encrypt_project",
        lambda include_all_projects=False: (object(), result),
    )
    encrypt_module.vault_encrypt_command(all_projects=False)

    out = capsys.readouterr().out
    assert "Encrypted 1 file(s)" in out


def test_vault_encrypt_command_shows_skipped(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    skipped_path = Path("/tmp/vault/values.env")
    result = _make_encrypt_result(skipped=(skipped_path,))

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_encrypt_project",
        lambda include_all_projects=False: (object(), result),
    )
    encrypt_module.vault_encrypt_command(all_projects=False)

    out = capsys.readouterr().out
    assert "No plaintext vault files found to encrypt" in out
    assert "skipped" in out


def test_vault_encrypt_command_emits_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(encrypt_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_encrypt_project",
        lambda include_all_projects=False: (
            object(),
            _make_encrypt_result(encrypted=(Path("/tmp/vault/values.env"),)),
        ),
    )
    monkeypatch.setattr(
        encrypt_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    encrypt_module.vault_encrypt_command(all_projects=False)
    assert captured["output_format"] == "json"
    assert captured["output"].metadata["kind"] == "vault_encrypt"
    assert captured["output"].metadata["encrypted_files"] == ["/tmp/vault/values.env"]


def test_vault_encrypt_command_propagates_execution_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_encrypt_project",
        lambda include_all_projects=False: (_ for _ in ()).throw(
            ExecutionError("Encryption is not enabled")
        ),
    )

    with pytest.raises(typer.Exit):
        encrypt_module.vault_encrypt_command(all_projects=False)


# ---------------------------------------------------------------------------
# vault decrypt
# ---------------------------------------------------------------------------


def test_vault_decrypt_command_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    decrypted_path = Path("/tmp/vault/values.env")
    result = _make_decrypt_result(decrypted=(decrypted_path,))

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_decrypt_project",
        lambda include_all_projects=False: (object(), result),
    )
    decrypt_module.vault_decrypt_command(all_projects=False)

    out = capsys.readouterr().out
    assert "Decrypted 1 file(s)" in out


def test_vault_decrypt_command_shows_no_encrypted_files(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    skipped_path = Path("/tmp/vault/values.env")
    result = _make_decrypt_result(skipped=(skipped_path,))

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_decrypt_project",
        lambda include_all_projects=False: (object(), result),
    )
    decrypt_module.vault_decrypt_command(all_projects=False)

    out = capsys.readouterr().out
    assert "No encrypted vault files found to decrypt" in out


def test_vault_decrypt_command_emits_json_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(decrypt_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_decrypt_project",
        lambda include_all_projects=False: (
            object(),
            _make_decrypt_result(decrypted=(Path("/tmp/vault/values.env"),)),
        ),
    )
    monkeypatch.setattr(
        decrypt_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    decrypt_module.vault_decrypt_command(all_projects=False)
    assert captured["output_format"] == "json"
    assert captured["output"].metadata["kind"] == "vault_decrypt"
    assert captured["output"].metadata["decrypted_files"] == ["/tmp/vault/values.env"]
