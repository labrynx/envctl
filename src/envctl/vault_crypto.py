"""Vault encryption helpers using explicit, inspectable envelopes.

Vault payloads are versioned and self-identifying::

    ENVCTL-VAULT-V1:<key-id>:<fernet-token>

Master keys are also versioned and self-identifying::

    ENVCTL-MASTER-KEY-V1:<key-id>:<base64-key>

Legacy master keys remain supported until v2.6.0. When a legacy key is loaded
from disk and the file is writable, envctl rewrites it automatically to the new
canonical format without changing the real secret.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import ClassVar, Literal

from cryptography.fernet import Fernet, InvalidToken

from envctl.constants import (
    ENVCTL_VAULT_KEY_ENVVAR,
    MASTER_KEY_FORMAT_VERSION,
    MASTER_KEY_ID_LENGTH,
    VAULT_ENCRYPTION_FORMAT_VERSION,
)
from envctl.domain.diagnostics import CommandWarning
from envctl.errors import ExecutionError
from envctl.observability.timing import observe_span
from envctl.utils.atomic import write_bytes_atomic

VaultFileState = Literal["missing", "plaintext", "encrypted", "wrong_key", "corrupt"]
MasterKeyFormat = Literal["legacy", "v1"]

_ENVELOPE_PREFIX = f"{VAULT_ENCRYPTION_FORMAT_VERSION}:".encode()
_MASTER_KEY_PREFIX = f"{MASTER_KEY_FORMAT_VERSION}:".encode()


@dataclass(frozen=True)
class VaultInspection:
    """Inspection result for one vault artifact."""

    state: VaultFileState
    detail: str


@dataclass(frozen=True)
class MasterKeyMaterial:
    """Parsed master-key material."""

    format: MasterKeyFormat
    key_id: str
    key_bytes: bytes

    @property
    def is_legacy(self) -> bool:
        """Return whether the parsed material came from the legacy raw format."""
        return self.format == "legacy"


class VaultDecryptionError(ExecutionError):
    """Raised when vault content cannot be decrypted safely."""


VaultMaterialSource = Literal["env", "file", "generated"]


class VaultCrypto:
    """Symmetric vault encryption backed by versioned Fernet envelopes."""

    _legacy_warning_emitted: ClassVar[bool] = False

    def __init__(
        self,
        key_bytes: bytes,
        *,
        runtime_warnings: tuple[CommandWarning, ...] = (),
        material_source: VaultMaterialSource | None = None,
        material_format: MasterKeyFormat | None = None,
    ) -> None:
        self._key_bytes = key_bytes
        self._fernet = Fernet(key_bytes)
        self._key_id = derive_master_key_id(key_bytes)
        self.runtime_warnings = runtime_warnings
        self._material_source: VaultMaterialSource | None = material_source
        self._material_format: MasterKeyFormat | None = material_format

    @property
    def material_source(self) -> VaultMaterialSource | None:
        """Return the logical source of the active key material."""
        return self._material_source

    @property
    def material_format(self) -> MasterKeyFormat | None:
        """Return the normalized format of the active key material."""
        return self._material_format

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
        protected_paths = tuple(protected_paths)
        raw_env = os.environ.get(ENVCTL_VAULT_KEY_ENVVAR)
        if raw_env is not None:
            material = parse_master_key_material(raw_env.strip().encode("utf-8"))
            warnings = cls._warnings_for_loaded_material(material, source="env")
            return cls(
                material.key_bytes,
                runtime_warnings=warnings,
                material_source="env",
                material_format=material.format,
            )

        return cls.load_or_create(key_path, protected_paths=protected_paths)

    @classmethod
    def load_or_create(
        cls,
        key_path: Path,
        *,
        protected_paths: Iterable[Path] = (),
    ) -> VaultCrypto:
        """Load the existing vault key or create it when safe."""
        protected_paths = tuple(protected_paths)
        with observe_span(
            "vault",
            module=__name__,
            operation="load_or_create",
            fields={
                "path_kind": "vault_master_key",
                "protected_path_count": len(protected_paths),
            },
        ) as span_fields:
            if key_path.exists():
                raw = key_path.read_bytes()
                material = parse_master_key_material(raw)
                warnings = list(cls._warnings_for_loaded_material(material, source="file"))
                span_fields["state"] = "loaded_from_file"
                span_fields["material_source"] = "file"
                span_fields["material_format"] = material.format
                span_fields["material_id"] = material.key_id
                span_fields["exists"] = True
                if material.is_legacy:
                    migrated_warning = cls._migrate_legacy_key_file(key_path, material)
                    if migrated_warning is not None:
                        warnings.append(migrated_warning)
                span_fields["warning_count"] = len(warnings)
                return cls(
                    material.key_bytes,
                    runtime_warnings=tuple(warnings),
                    material_source="file",
                    material_format=material.format,
                )

            encrypted_path = cls._find_encrypted_path(protected_paths)
            if encrypted_path is not None:
                span_fields["state"] = "missing"
                raise ExecutionError(
                    "Vault encryption key is missing, but encrypted vault data already exists. "
                    f"Restore '{key_path}' before continuing. First encrypted file found: "
                    f"{encrypted_path}"
                )

            key_bytes = Fernet.generate_key()
            key_path.parent.mkdir(parents=True, exist_ok=True)
            write_bytes_atomic(key_path, serialize_master_key_v1(key_bytes), mode=0o400)
            span_fields["state"] = "created"
            span_fields["created"] = True
            span_fields["exists"] = True
            span_fields["material_format"] = "v1"
            span_fields["material_id"] = derive_master_key_id(key_bytes)
            return cls(
                key_bytes,
                material_source="generated",
                material_format="v1",
            )

    @classmethod
    def _warnings_for_loaded_material(
        cls,
        material: MasterKeyMaterial,
        *,
        source: Literal["env", "file"],
    ) -> tuple[CommandWarning, ...]:
        if not material.is_legacy or cls._legacy_warning_emitted:
            return ()

        cls._legacy_warning_emitted = True
        if source == "env":
            message = (
                f"Warning: {ENVCTL_VAULT_KEY_ENVVAR} uses a legacy raw master-key format and "
                "will stop being supported in v2.6.0. Use the canonical format "
                f"'{MASTER_KEY_FORMAT_VERSION}:<key-id>:<base64-key>' instead."
            )
        else:
            message = (
                "Warning: the project master key file uses a legacy raw format and will stop "
                "being supported in v2.6.0. envctl will migrate it automatically when it can "
                f"rewrite '{(source == 'file' and 'master.key') or 'the key file'}'."
            )
        return (CommandWarning(kind="legacy_master_key", message=message),)

    @classmethod
    def _migrate_legacy_key_file(
        cls,
        key_path: Path,
        material: MasterKeyMaterial,
    ) -> CommandWarning | None:
        with observe_span(
            "vault",
            module=__name__,
            operation="_migrate_legacy_key_file",
            fields={
                "path_kind": "vault_master_key",
                "material_format": material.format,
                "material_id": material.key_id,
            },
        ) as span_fields:
            try:
                write_bytes_atomic(
                    key_path,
                    serialize_master_key_v1(material.key_bytes),
                    mode=0o400,
                )
            except OSError as exc:
                span_fields["updated"] = False
                span_fields["message_safe"] = (
                    "Could not rewrite the legacy master key to canonical format."
                )
                return CommandWarning(
                    kind="legacy_master_key_migration_failed",
                    message=(
                        "Warning: envctl could not rewrite the legacy master key to the canonical "
                        f"format at '{key_path}': {exc.strerror or exc}. "
                        "The key is still usable for "
                        "now, but you should fix file permissions before v2.6.0."
                    ),
                )
            span_fields["state"] = "migrated_legacy"
            span_fields["updated"] = True
            return CommandWarning(
                kind="legacy_master_key_migrated",
                message=(
                    f"Warning: envctl migrated the legacy master key at '{key_path}' to the "
                    f"canonical {MASTER_KEY_FORMAT_VERSION} format."
                ),
            )

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
        with observe_span(
            "vault",
            module=__name__,
            operation="encrypt",
            fields={"material_id": self._key_id},
        ) as span_fields:
            token = self._fernet.encrypt(content.encode("utf-8"))
            span_fields["state"] = "encrypted"
            return _ENVELOPE_PREFIX + self._key_id.encode("utf-8") + b":" + token

    @staticmethod
    def _split_envelope(data: bytes) -> tuple[str | None, bytes | None, str | None]:
        """Return parsed payload material id and token when the envelope is readable."""
        if not VaultCrypto.looks_encrypted(data):
            return None, None, None

        envelope = data[len(_ENVELOPE_PREFIX) :]
        key_part, separator, token = envelope.partition(b":")
        if not separator or not key_part or not token:
            return None, None, "Vault file has a malformed encryption envelope."

        try:
            payload_material_id = key_part.decode("utf-8")
        except UnicodeDecodeError:
            return None, None, "Vault file has an unreadable encryption header."
        return payload_material_id, token, None

    def payload_material_id(self, data: bytes) -> str | None:
        """Return the payload material id when one encrypted envelope is readable."""
        payload_material_id, _token, _error = self._split_envelope(data)
        return payload_material_id

    def inspect_bytes(self, data: bytes) -> VaultInspection:
        """Classify one vault payload using the current key when available."""
        if not data:
            return VaultInspection("plaintext", "Vault file is empty plaintext.")

        if not self.looks_encrypted(data):
            return VaultInspection(
                "plaintext",
                "Vault file is plaintext. Run 'envctl vault encrypt' to migrate it.",
            )

        payload_key_id, token, envelope_error = self._split_envelope(data)
        if envelope_error is not None or payload_key_id is None or token is None:
            return VaultInspection("corrupt", envelope_error or "Vault file is corrupted.")

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
        content, _fields = self.read_file_with_metadata(path, allow_plaintext=allow_plaintext)
        return content

    def read_file_with_metadata(
        self,
        path: Path,
        *,
        allow_plaintext: bool = True,
    ) -> tuple[str, dict[str, str]]:
        """Read one vault file and return compact observability metadata."""
        if not path.exists():
            return "", {"state": "missing"}

        raw = path.read_bytes()
        inspection = self.inspect_bytes(raw)
        metadata: dict[str, str] = {"state": inspection.state}
        payload_material_id = self.payload_material_id(raw)
        if payload_material_id is not None:
            metadata["payload_material_id"] = payload_material_id
        if inspection.state == "plaintext":
            if not allow_plaintext:
                raise VaultDecryptionError(inspection.detail)
            try:
                return raw.decode("utf-8"), metadata
            except UnicodeDecodeError as exc:
                raise VaultDecryptionError(
                    "Vault file is plaintext but not valid UTF-8. Repair or replace it before "
                    "continuing."
                ) from exc

        if inspection.state in {"wrong_key", "corrupt"}:
            raise VaultDecryptionError(inspection.detail)

        _payload_material_id, token, error = self._split_envelope(raw)

        if token is None:
            raise VaultDecryptionError(error or "Vault file has an invalid encryption envelope.")

        return self._fernet.decrypt(token).decode("utf-8"), metadata

    def write_encrypted_file(self, path: Path, content: str) -> None:
        """Encrypt ``content`` and write it atomically to ``path``."""
        encrypted = self.encrypt(content)
        write_bytes_atomic(path, encrypted, mode=0o600)


def derive_master_key_id(key_bytes: bytes) -> str:
    """Return the stable public id for one master key."""
    return sha256(key_bytes).hexdigest()[:MASTER_KEY_ID_LENGTH]


def serialize_master_key_v1(key_bytes: bytes) -> bytes:
    """Serialize one Fernet key to the canonical versioned format."""
    key_id = derive_master_key_id(key_bytes)
    return _MASTER_KEY_PREFIX + key_id.encode("utf-8") + b":" + key_bytes


def parse_master_key_material(raw: bytes) -> MasterKeyMaterial:
    """Parse raw key material in legacy or canonical format."""
    stripped = raw.strip()
    if not stripped:
        raise ExecutionError("Master key file is empty. Restore it or create a new vault key.")

    if stripped.startswith(_MASTER_KEY_PREFIX):
        body = stripped[len(_MASTER_KEY_PREFIX) :]
        key_id_bytes, sep, key_bytes = body.partition(b":")
        if not sep or not key_id_bytes or not key_bytes:
            raise ExecutionError(
                f"Malformed master key. Expected '{MASTER_KEY_FORMAT_VERSION}:"
                f"<key-id>:<base64-key>'."
            )
        try:
            key_id = key_id_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExecutionError("Malformed master key. The key id is not valid UTF-8.") from exc
        _validate_fernet_key(key_bytes)
        expected_key_id = derive_master_key_id(key_bytes)
        if key_id != expected_key_id:
            raise ExecutionError(
                "Malformed master key. The embedded key id does not match the actual key material."
            )
        return MasterKeyMaterial(format="v1", key_id=key_id, key_bytes=key_bytes)

    _validate_fernet_key(stripped)
    return MasterKeyMaterial(
        format="legacy",
        key_id=derive_master_key_id(stripped),
        key_bytes=stripped,
    )


def _validate_fernet_key(key_bytes: bytes) -> None:
    try:
        Fernet(key_bytes)
    except Exception as exc:
        raise ExecutionError(
            "Invalid master key material. Expected either a Fernet-compatible legacy key or "
            f"'{MASTER_KEY_FORMAT_VERSION}:<key-id>:<base64-key>'."
        ) from exc
