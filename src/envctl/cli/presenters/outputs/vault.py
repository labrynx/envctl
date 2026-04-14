"""Output builders for vault commands."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from envctl.cli.presenters.common import (
    bullet_item,
    field_item,
    raw_item,
    section,
    success_message,
    warning_message,
)
from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputSection
from envctl.cli.presenters.payloads import path_to_str

if TYPE_CHECKING:
    from envctl.domain.operations import VaultAuditProjectResult


def _vault_context_items(*, profile: str, path: Path) -> list[OutputItem]:
    """Build common vault context items."""
    return [
        field_item("profile", profile),
        field_item("vault_values", path_to_str(path)),
    ]


def _vault_context_section(
    *,
    profile: str,
    path: Path,
    title: str = "Vault",
) -> OutputSection:
    """Build one common vault context section."""
    return section(title, *_vault_context_items(profile=profile, path=path))


def _build_vault_process_items(
    *,
    processed_label: str,
    processed_paths: list[str],
    skipped_paths: list[str],
) -> list[OutputItem]:
    """Build one common item list for encrypt/decrypt style outputs."""
    items = [field_item(processed_label, path) for path in processed_paths]
    items.extend(field_item("skipped", path) for path in skipped_paths)
    return items


def build_vault_check_output(
    *,
    profile: str,
    path: Path,
    exists: bool,
    parseable: bool,
    private_permissions: bool,
    key_count: int,
    state: str,
    detail: str | None = None,
) -> CommandOutput:
    """Build one unified output model for ``vault check``."""
    metadata: dict[str, Any] = {
        "kind": "vault_check",
        "profile": profile,
        "vault_values": path_to_str(path),
        "exists": exists,
        "state": state,
        "parseable": parseable,
        "private_permissions": private_permissions,
        "keys": key_count,
        "detail": detail,
    }

    if not exists:
        return CommandOutput(
            messages=[warning_message("Vault file does not exist")],
            sections=[_vault_context_section(profile=profile, path=path, title="Context")],
            metadata={
                **metadata,
                "ok": False,
            },
        )

    if state == "encrypted":
        messages = [success_message("Vault file is encrypted and readable")]
        ok = True
    elif state == "plaintext":
        messages = [warning_message("Vault file is plaintext")]
        ok = False
    elif state == "wrong_key":
        messages = [warning_message("Vault file is encrypted with a different key")]
        ok = False
    elif state == "corrupt":
        messages = [warning_message("Vault file is corrupted")]
        ok = False
    else:
        messages = []
        ok = parseable and private_permissions

    items = [
        *_vault_context_items(profile=profile, path=path),
        field_item("state", state),
        field_item("parseable", "yes" if parseable else "no"),
        field_item("private_permissions", "yes" if private_permissions else "no"),
        field_item("keys", str(key_count)),
    ]
    if detail:
        items.append(field_item("detail", detail))

    return CommandOutput(
        messages=messages,
        sections=[section("Vault", *items)],
        metadata={
            **metadata,
            "ok": ok,
        },
    )


def build_vault_edit_output(*, profile: str, path: Path, created: bool) -> CommandOutput:
    """Build one unified output model for ``vault edit``."""
    message = (
        success_message(f"Created and opened profile '{profile}' vault file")
        if created
        else success_message(f"Opened profile '{profile}' vault file")
    )

    return CommandOutput(
        messages=[message],
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_edit",
            "profile": profile,
            "vault_values": path_to_str(path),
            "created": created,
            "ok": True,
        },
    )


def build_vault_path_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for ``vault path``."""
    return CommandOutput(
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_path",
            "profile": profile,
            "vault_values": path_to_str(path),
        },
    )


def build_vault_prune_no_changes_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for ``vault prune`` when nothing changes."""
    return CommandOutput(
        messages=[warning_message("No unknown keys were removed")],
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_prune",
            "profile": profile,
            "vault_values": path_to_str(path),
            "removed_keys": [],
            "changed": False,
            "cancelled": False,
            "ok": True,
        },
    )


def build_vault_prune_cancelled_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for cancelled ``vault prune``."""
    return CommandOutput(
        messages=[warning_message("No unknown keys were removed")],
        sections=[
            section(
                "Vault",
                *_vault_context_items(profile=profile, path=path),
                field_item("kept_keys", "unchanged"),
            )
        ],
        metadata={
            "kind": "vault_prune",
            "profile": profile,
            "vault_values": path_to_str(path),
            "removed_keys": [],
            "changed": False,
            "cancelled": True,
            "kept_keys": "unchanged",
            "ok": True,
        },
    )


def build_vault_prune_output(
    *,
    profile: str,
    path: Path,
    removed_keys: tuple[str, ...],
    kept_keys: int,
) -> CommandOutput:
    """Build one unified output model for successful ``vault prune``."""
    return CommandOutput(
        messages=[
            success_message(f"Removed {len(removed_keys)} unknown key(s) from profile '{profile}'")
        ],
        sections=[
            section(
                "Vault",
                *_vault_context_items(profile=profile, path=path),
                field_item("removed_keys", ", ".join(removed_keys)),
                field_item("kept_keys", str(kept_keys)),
            )
        ],
        metadata={
            "kind": "vault_prune",
            "profile": profile,
            "vault_values": path_to_str(path),
            "removed_keys": list(removed_keys),
            "kept_keys": kept_keys,
            "changed": True,
            "cancelled": False,
            "ok": True,
        },
    )


def build_vault_show_missing_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for missing ``vault show``."""
    return CommandOutput(
        messages=[warning_message("Vault file does not exist")],
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_show",
            "profile": profile,
            "vault_values": path_to_str(path),
            "state": "missing",
            "ok": False,
        },
    )


def build_vault_show_empty_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for empty ``vault show``."""
    return CommandOutput(
        messages=[warning_message("Vault file is empty")],
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_show",
            "profile": profile,
            "vault_values": path_to_str(path),
            "state": "empty",
            "ok": True,
        },
    )


def build_vault_show_cancelled_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for cancelled raw ``vault show``."""
    return CommandOutput(
        messages=[warning_message("Nothing was shown.")],
        sections=[_vault_context_section(profile=profile, path=path)],
        metadata={
            "kind": "vault_show",
            "profile": profile,
            "vault_values": path_to_str(path),
            "cancelled": True,
            "ok": True,
        },
    )


def build_vault_show_values_output(
    *,
    profile: str,
    path: Path,
    values: dict[str, str],
    state: str,
    detail: str | None = None,
) -> CommandOutput:
    """Build one unified output model for ``vault show`` values."""
    sections = [
        section(
            "Vault",
            *_vault_context_items(profile=profile, path=path),
            field_item("state", state),
            *([field_item("detail", detail)] if detail else []),
        ),
        section(
            "Values",
            *(bullet_item(f"{key}={values[key]}") for key in sorted(values))
            if values
            else (raw_item("None"),),
        ),
    ]

    return CommandOutput(
        sections=sections,
        metadata={
            "kind": "vault_show",
            "profile": profile,
            "vault_values": path_to_str(path),
            "state": state,
            "detail": detail,
            "values": dict(values),
            "ok": True,
        },
    )


def build_vault_encrypt_output(result: object) -> CommandOutput:
    """Build one unified output model for ``vault encrypt``."""
    from envctl.domain.operations import VaultEncryptResult

    if not isinstance(result, VaultEncryptResult):  # pragma: no cover
        return CommandOutput(
            metadata={
                "kind": "vault_encrypt",
                "unsupported_result_type": type(result).__name__,
            }
        )

    encrypted_files = [path_to_str(path) for path in result.encrypted_files]
    skipped_files = [path_to_str(path) for path in result.skipped_files]

    message = (
        success_message(f"Encrypted {len(result.encrypted_files)} file(s)")
        if result.encrypted_files
        else warning_message("No plaintext vault files found to encrypt")
    )

    items = _build_vault_process_items(
        processed_label="encrypted",
        processed_paths=encrypted_files,
        skipped_paths=skipped_files,
    )

    return CommandOutput(
        messages=[message],
        sections=[section("Vault encryption", *items)] if items else [],
        metadata={
            "kind": "vault_encrypt",
            "encrypted_files": encrypted_files,
            "skipped_files": skipped_files,
            "ok": True,
        },
    )


def build_vault_decrypt_output(result: object) -> CommandOutput:
    """Build one unified output model for ``vault decrypt``."""
    from envctl.domain.operations import VaultDecryptResult

    if not isinstance(result, VaultDecryptResult):  # pragma: no cover
        return CommandOutput(
            metadata={
                "kind": "vault_decrypt",
                "unsupported_result_type": type(result).__name__,
            }
        )

    decrypted_files = [path_to_str(path) for path in result.decrypted_files]
    skipped_files = [path_to_str(path) for path in result.skipped_files]

    message = (
        success_message(f"Decrypted {len(result.decrypted_files)} file(s)")
        if result.decrypted_files
        else warning_message("No encrypted vault files found to decrypt")
    )

    items = _build_vault_process_items(
        processed_label="decrypted",
        processed_paths=decrypted_files,
        skipped_paths=skipped_files,
    )

    return CommandOutput(
        messages=[message],
        sections=[section("Vault decryption", *items)] if items else [],
        metadata={
            "kind": "vault_decrypt",
            "decrypted_files": decrypted_files,
            "skipped_files": skipped_files,
            "ok": True,
        },
    )


def build_vault_audit_output(projects: tuple[VaultAuditProjectResult, ...]) -> CommandOutput:
    """Build one unified output model for ``vault audit``."""
    if not projects:
        return CommandOutput(
            messages=[warning_message("No persisted vault projects were found")],
            metadata={
                "kind": "vault_audit",
                "projects": [],
                "ok": True,
            },
        )

    sections = []
    projects_payload: list[dict[str, Any]] = []

    for project in projects:
        project_payload: dict[str, Any] = {
            "project_slug": project.project_slug,
            "project_id": project.project_id,
            "key_path": path_to_str(project.key_path),
            "key_exists": project.key_exists,
            "files": [],
        }

        items: list[OutputItem] = [
            field_item("project", f"{project.project_slug} ({project.project_id})"),
            field_item("key_path", path_to_str(project.key_path)),
            field_item("key_exists", "yes" if project.key_exists else "no"),
        ]

        if not project.files:
            items.append(raw_item("No vault files found"))
            sections.append(section("Project", *items))
            projects_payload.append(project_payload)
            continue

        for file_item in project.files:
            items.extend(
                [
                    field_item("file", path_to_str(file_item.path)),
                    field_item("state", file_item.state),
                    field_item(
                        "private_permissions",
                        "yes" if file_item.private_permissions else "no",
                    ),
                    field_item("detail", file_item.detail),
                ]
            )
            project_payload["files"].append(
                {
                    "path": path_to_str(file_item.path),
                    "state": file_item.state,
                    "private_permissions": file_item.private_permissions,
                    "detail": file_item.detail,
                }
            )

        sections.append(section("Project", *items))
        projects_payload.append(project_payload)

    return CommandOutput(
        sections=sections,
        metadata={
            "kind": "vault_audit",
            "projects": projects_payload,
            "ok": True,
        },
    )
