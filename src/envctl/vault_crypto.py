"""Vault encryption helpers using an explicit, inspectable file envelope.

The encrypted file format is versioned and self-identifying:

    ENVCTL-VAULT-V1:<key-id>:<fernet-token>

This avoids heuristic detection, makes migration states explicit, and lets
``envctl`` distinguish plaintext, wrong-key, and corrupted vault files.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from contextlib import suppress
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

from cryptography.fernet import Fernet, InvalidToken

from envctl.constants import ENVCTL_VAULT_KEY_ENVVAR, VAULT_ENCRYPTION_FORMAT_VERSION
from envctl.errors import ExecutionError

VaultFileState = Literal["missing", "plaintext", "encrypted", "wrong_key", "corrupt"]

_ENVELOPE_PREFIX = f"{VAULT_ENCRYPTION_FORMAT_VERSION}:".encode()


@dataclass(frozen=True)
class VaultInspection:
    """Inspection result for one vault artifact."""

    state: VaultFileState
    detail: str


class VaultDecryptionError(ExecutionError):
    """Raised when vault content cannot be decrypted safely."""


class VaultCrypto:
    """Symmetric vault encryption backed by a versioned Fernet envelope."""

    def __init__(self, key_bytes: bytes) -> None:
        self._key_bytes = key_bytes
        self._fernet = Fernet(key_bytes)
        self._key_id = sha256(key_bytes).hexdigest()[:16]

    @property
    def key_id(self) -> str:
        """Return a stable public identifier for the active key."""
        return self._key_id

    @classmethod
    def from_env_or_file(
        cls,
        key_path: Path,
        *,
        protected_paths: Iterable[Path] = (),
    ) -> VaultCrypto:
        """Load key material from env when present, otherwise from disk."""
        raw_env = os.environ.get(ENVCTL_VAULT_KEY_ENVVAR)
        if raw_env is not None:
            key_bytes = raw_env.strip().encode("utf-8")
            try:
                return cls(key_bytes)
            except Exception as exc:
                raise ExecutionError(
                    f"Invalid key material in {ENVCTL_VAULT_KEY_ENVVAR}. "
                    "Expected a Fernet-compatible base64 key."
                ) from exc

        return cls.load_or_create(key_path, protected_paths=protected_paths)

    @classmethod
    def load_or_create(
        cls,
        key_path: Path,
        *,
        protected_paths: Iterable[Path] = (),
    ) -> VaultCrypto:
        """Load the existing vault key or create it when safe."""
        if key_path.exists():
            return cls(key_path.read_bytes())

        encrypted_path = cls._find_encrypted_path(protected_paths)
        if encrypted_path is not None:
            raise ExecutionError(
                "Vault encryption key is missing, but encrypted vault data already exists. "
                f"Restore '{key_path}' before continuing. First encrypted file found: "
                f"{encrypted_path}"
            )

        key_bytes = Fernet.generate_key()
        key_path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{key_path.name}.",
            suffix=".tmp",
            dir=str(key_path.parent),
        )
        tmp_path = Path(tmp_name)
        try:
            with suppress(AttributeError):
                os.fchmod(fd, 0o400)
            with os.fdopen(fd, "wb") as handle:
                handle.write(key_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, key_path)
            with suppress(OSError):
                key_path.chmod(0o400)
        except Exception:
            with suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            raise

        return cls(key_bytes)

    @staticmethod
    def _find_encrypted_path(paths: Iterable[Path]) -> Path | None:
        for path in paths:
            if path.exists() and VaultCrypto.looks_encrypted(path.read_bytes()):
                return path
        return None

    @staticmethod
    def looks_encrypted(data: bytes) -> bool:
        """Return whether raw bytes use envctl's encrypted envelope."""
        return data.startswith(_ENVELOPE_PREFIX)

    def encrypt(self, content: str) -> bytes:
        """Encrypt plaintext and return the full envctl payload."""
        token = self._fernet.encrypt(content.encode("utf-8"))
        return _ENVELOPE_PREFIX + self._key_id.encode("utf-8") + b":" + token

    def inspect_bytes(self, data: bytes) -> VaultInspection:
        """Classify one vault payload using the current key when available."""
        if not data:
            return VaultInspection("plaintext", "Vault file is empty plaintext.")

        if not self.looks_encrypted(data):
            return VaultInspection(
                "plaintext",
                "Vault file is plaintext. Run 'envctl vault encrypt' to migrate it.",
            )

        envelope = data[len(_ENVELOPE_PREFIX) :]
        key_part, separator, token = envelope.partition(b":")
        if not separator or not key_part or not token:
            return VaultInspection("corrupt", "Vault file has a malformed encryption envelope.")

        try:
            payload_key_id = key_part.decode("utf-8")
        except UnicodeDecodeError:
            return VaultInspection("corrupt", "Vault file has an unreadable encryption header.")

        if payload_key_id != self._key_id:
            return VaultInspection(
                "wrong_key",
                "Vault file is encrypted with a different project key. Restore the correct "
                "master.key for this project or supply ENVCTL_VAULT_KEY.",
            )

        try:
            self._fernet.decrypt(token)
        except InvalidToken:
            return VaultInspection(
                "corrupt",
                "Vault file is encrypted with the current key id but its payload is corrupted.",
            )

        return VaultInspection("encrypted", "Vault file is encrypted and readable.")

    def decrypt(self, data: bytes) -> str:
        """Decrypt a full envctl payload and return plaintext content."""
        inspection = self.inspect_bytes(data)
        if inspection.state in {"plaintext", "wrong_key", "corrupt"}:
            raise VaultDecryptionError(inspection.detail)

        envelope = data[len(_ENVELOPE_PREFIX) :]
        _key_id, _separator, token = envelope.partition(b":")
        return self._fernet.decrypt(token).decode("utf-8")

    def inspect_file(self, path: Path) -> VaultInspection:
        """Inspect one vault file on disk."""
        if not path.exists():
            return VaultInspection("missing", "Vault file does not exist.")
        return self.inspect_bytes(path.read_bytes())

    def read_file(self, path: Path, *, allow_plaintext: bool = True) -> str:
        """Read one vault file, optionally accepting plaintext during migration."""
        if not path.exists():
            return ""

        raw = path.read_bytes()
        inspection = self.inspect_bytes(raw)
        if inspection.state == "plaintext":
            if not allow_plaintext:
                raise VaultDecryptionError(inspection.detail)
            try:
                return raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise VaultDecryptionError(
                    "Vault file is plaintext but not valid UTF-8. Repair or replace it before "
                    "continuing."
                ) from exc

        if inspection.state in {"wrong_key", "corrupt"}:
            raise VaultDecryptionError(inspection.detail)

        return self.decrypt(raw)

    def write_encrypted_file(self, path: Path, content: str) -> None:
        """Encrypt ``content`` and write it atomically to ``path``."""
        encrypted = self.encrypt(content)
        path.parent.mkdir(parents=True, exist_ok=True)

        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(path.parent),
        )
        tmp_path = Path(tmp_name)
        try:
            with suppress(AttributeError):
                os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(encrypted)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, path)
            with suppress(OSError):
                path.chmod(0o600)
        except Exception:
            with suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            raise
