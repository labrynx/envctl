"""Unified output builders for action-style commands."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from envctl.cli.presenters.common import (
    field_item,
    raw_item,
    section,
    success_message,
    warning_message,
)
from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputSection
from envctl.cli.presenters.payloads import path_to_str
from envctl.domain.hooks import HooksReason

if TYPE_CHECKING:
    from envctl.domain.operations import InitResult


def _yes_no(value: bool) -> str:
    """Render one boolean as yes/no."""
    return "yes" if value else "no"


def _details_section(*items: OutputItem) -> OutputSection:
    """Build one standard details section."""
    return section("Details", *items)


def _optional_path(path: Path | None) -> str | None:
    """Serialize one optional path."""
    return path_to_str(path) if path is not None else None


def _build_hooks_reason_message(reason: HooksReason) -> str:
    """Build one human-facing hooks reason message."""
    if reason == HooksReason.PARTIAL_CONFLICT:
        return "Managed hooks were partially installed, but conflicts remain."
    if reason == HooksReason.UNSUPPORTED_HOOKS_PATH:
        return "Managed hooks were not installed because the effective hooks path is unsupported."
    if reason == HooksReason.FOREIGN_HOOK_PRESENT:
        return "Managed hooks were not installed because a foreign hook is already present."
    if reason == HooksReason.INSTALL_FAILED:
        return "Managed hooks could not be installed due to an unexpected error."
    return reason.value


def build_config_init_output(config_path: Path) -> CommandOutput:
    """Build one unified output model for ``config init``."""
    return CommandOutput(
        messages=[success_message("Created envctl config file")],
        sections=[
            _details_section(
                field_item("config", path_to_str(config_path)),
            )
        ],
        metadata={
            "kind": "config_init",
            "config": path_to_str(config_path),
        },
    )


def build_add_output(
    *,
    key: str,
    profile: str,
    profile_path: Path,
    contract_path: Path,
    contract_created: bool,
    contract_updated: bool,
    contract_entry_created: bool,
) -> CommandOutput:
    """Build one unified output model for ``add``."""
    items = [
        field_item("profile", profile),
        field_item("vault_values", path_to_str(profile_path)),
        field_item("contract", path_to_str(contract_path)),
    ]
    if contract_created:
        items.append(field_item("contract_created", "yes"))
    if contract_updated:
        items.append(field_item("contract_updated", "yes"))
    if contract_entry_created:
        items.append(field_item("contract_entry_created", "yes"))

    return CommandOutput(
        messages=[success_message(f"Added '{key}' to contract and profile '{profile}'")],
        sections=[_details_section(*items)],
        metadata={
            "kind": "add",
            "key": key,
            "profile": profile,
            "vault_values": path_to_str(profile_path),
            "contract": path_to_str(contract_path),
            "contract_created": contract_created,
            "contract_updated": contract_updated,
            "contract_entry_created": contract_entry_created,
        },
    )


def build_inferred_spec_output(inferred_spec: dict[str, object] | None) -> CommandOutput:
    """Build one unified output model for inferred metadata details."""
    if inferred_spec is None:
        return CommandOutput(
            metadata={
                "kind": "inferred_spec",
                "inferred_spec": None,
            }
        )

    items: list[OutputItem] = []
    if "type" in inferred_spec:
        items.append(field_item("inferred_type", str(inferred_spec["type"])))
    if "required" in inferred_spec:
        items.append(field_item("required", _yes_no(bool(inferred_spec["required"]))))
    if "sensitive" in inferred_spec:
        items.append(field_item("sensitive", _yes_no(bool(inferred_spec["sensitive"]))))
    if "description" in inferred_spec:
        items.append(field_item("description", str(inferred_spec["description"])))

    return CommandOutput(
        messages=[warning_message("Review .envctl.yaml to confirm the inferred metadata.")],
        sections=[section("Inferred metadata", *items)],
        metadata={
            "kind": "inferred_spec",
            "inferred_spec": dict(inferred_spec),
        },
    )


def build_export_output(
    *,
    active_profile: str,
    format: Literal["shell", "dotenv"],
    values: dict[str, str],
    rendered: str,
) -> CommandOutput:
    """Build one unified output model for ``export``."""
    sections = [
        section(
            "Context",
            field_item("profile", active_profile),
        )
    ]
    if rendered:
        sections.append(section("Rendered", raw_item(rendered)))

    return CommandOutput(
        sections=sections,
        metadata={
            "kind": "export",
            "active_profile": active_profile,
            "format": format,
            "values": dict(values),
            "rendered": rendered,
        },
    )


def build_fill_no_changes_output(
    *,
    profile: str,
    profile_path: Path | None = None,
) -> CommandOutput:
    """Build one unified output model for ``fill`` with no changes."""
    items = [field_item("profile", profile)]
    if profile_path is not None:
        items.append(field_item("vault_values", path_to_str(profile_path)))

    return CommandOutput(
        messages=[warning_message("No keys were changed")],
        sections=[_details_section(*items)],
        metadata={
            "kind": "fill",
            "profile": profile,
            "vault_values": _optional_path(profile_path),
            "changed": False,
            "changed_keys": [],
        },
    )


def build_fill_output(
    *,
    project_name: str,
    profile: str,
    profile_path: Path,
    changed_keys: list[str],
) -> CommandOutput:
    """Build one unified output model for ``fill``."""
    if not changed_keys:
        return build_fill_no_changes_output(
            profile=profile,
            profile_path=profile_path,
        )

    return CommandOutput(
        messages=[success_message(f"Filled {len(changed_keys)} key(s) for {project_name}")],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("vault_values", path_to_str(profile_path)),
                field_item("keys", ", ".join(changed_keys)),
            )
        ],
        metadata={
            "kind": "fill",
            "project_name": project_name,
            "profile": profile,
            "vault_values": path_to_str(profile_path),
            "changed": True,
            "changed_keys": list(changed_keys),
        },
    )


def build_init_output(
    *,
    project_key: str,
    binding_source: str,
    repo_root: Path,
    contract_path: Path,
    vault_dir: Path,
    vault_values_path: Path,
    vault_state_path: Path,
    init_result: InitResult,
    display_name: str,
) -> CommandOutput:
    """Build one unified output model for ``init``."""
    items = [
        field_item("project_key", project_key),
        field_item("binding_source", binding_source),
        field_item("repo_root", path_to_str(repo_root)),
        field_item("contract", path_to_str(contract_path)),
        field_item("vault_dir", path_to_str(vault_dir)),
        field_item("vault_values", path_to_str(vault_values_path)),
        field_item("vault_state", path_to_str(vault_state_path)),
    ]

    if init_result.contract_created:
        items.append(field_item("contract_created", "yes"))
        items.append(field_item("contract_template", init_result.contract_template or "custom"))

    items.append(field_item("hooks_installed", _yes_no(init_result.hooks_installed)))
    if init_result.hooks_reason is not None:
        items.append(field_item("hooks_reason", init_result.hooks_reason.value))

    messages = [success_message(f"Initialized {display_name}")]
    if init_result.contract_skipped:
        messages.append(warning_message("No contract file was created"))
    if init_result.hooks_reason is not None and init_result.hooks_reason not in {
        HooksReason.INSTALLED,
        HooksReason.ALREADY_HEALTHY,
    }:
        messages.append(warning_message(_build_hooks_reason_message(init_result.hooks_reason)))
    messages.extend(warning_message(warning) for warning in init_result.runtime_warnings)

    return CommandOutput(
        messages=messages,
        sections=[_details_section(*items)],
        metadata={
            "kind": "init",
            "display_name": display_name,
            "project_key": project_key,
            "binding_source": binding_source,
            "repo_root": path_to_str(repo_root),
            "contract": path_to_str(contract_path),
            "vault_dir": path_to_str(vault_dir),
            "vault_values": path_to_str(vault_values_path),
            "vault_state": path_to_str(vault_state_path),
            "contract_created": init_result.contract_created,
            "contract_template": init_result.contract_template,
            "contract_skipped": init_result.contract_skipped,
            "hooks_installed": init_result.hooks_installed,
            "hooks_reason": init_result.hooks_reason.value if init_result.hooks_reason else None,
            "runtime_warnings": list(init_result.runtime_warnings),
        },
    )


def build_remove_output(
    *,
    key: str,
    contract_path: Path,
    removed_from_contract: bool,
    inspected_profiles: tuple[str, ...],
    removed_from_profiles: tuple[str, ...],
    missing_from_profiles: tuple[str, ...],
    affected_paths: tuple[Path, ...],
    repo_root: Path,
) -> CommandOutput:
    """Build one unified output model for ``remove``."""
    items = [
        field_item("contract", path_to_str(contract_path)),
        field_item("removed_from_contract", _yes_no(removed_from_contract)),
        field_item(
            "removed_from_profiles",
            ", ".join(removed_from_profiles) if removed_from_profiles else "none",
        ),
        field_item(
            "inspected_profiles",
            ", ".join(inspected_profiles) if inspected_profiles else "none",
        ),
        field_item(
            "missing_from_profiles",
            ", ".join(missing_from_profiles) if missing_from_profiles else "none",
        ),
    ]
    if affected_paths:
        items.append(
            field_item("affected_paths", ", ".join(path_to_str(path) for path in affected_paths))
        )
    items.append(field_item("repo_root", path_to_str(repo_root)))

    return CommandOutput(
        messages=[success_message(f"Removed '{key}' from contract and persisted profiles")],
        sections=[_details_section(*items)],
        metadata={
            "kind": "remove",
            "key": key,
            "contract": path_to_str(contract_path),
            "removed_from_contract": removed_from_contract,
            "inspected_profiles": list(inspected_profiles),
            "removed_from_profiles": list(removed_from_profiles),
            "missing_from_profiles": list(missing_from_profiles),
            "affected_paths": [path_to_str(path) for path in affected_paths],
            "repo_root": path_to_str(repo_root),
        },
    )


def build_set_output(
    *,
    key: str,
    profile: str,
    profile_path: Path,
) -> CommandOutput:
    """Build one unified output model for ``set``."""
    return CommandOutput(
        messages=[success_message(f"Set '{key}' in profile '{profile}'")],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("vault_values", path_to_str(profile_path)),
            )
        ],
        metadata={
            "kind": "set",
            "key": key,
            "profile": profile,
            "vault_values": path_to_str(profile_path),
        },
    )


def build_unset_output(
    *,
    key: str,
    profile: str,
    profile_path: Path,
    removed: bool,
) -> CommandOutput:
    """Build one unified output model for ``unset``."""
    message = (
        success_message(f"Unset '{key}' in profile '{profile}'")
        if removed
        else warning_message(f"'{key}' was not set in profile '{profile}'")
    )

    return CommandOutput(
        messages=[message],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("vault_values", path_to_str(profile_path)),
            )
        ],
        metadata={
            "kind": "unset",
            "key": key,
            "profile": profile,
            "vault_values": path_to_str(profile_path),
            "removed": removed,
        },
    )


def build_sync_output(*, profile: str, target_path: Path) -> CommandOutput:
    """Build one unified output model for ``sync``."""
    return CommandOutput(
        messages=[success_message("Synced generated environment")],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("target", path_to_str(target_path)),
            )
        ],
        metadata={
            "kind": "sync",
            "profile": profile,
            "target": path_to_str(target_path),
        },
    )


def build_profile_list_output(*, active_profile: str, profiles: tuple[str, ...]) -> CommandOutput:
    """Build one unified output model for ``profile list``."""
    return CommandOutput(
        sections=[
            section(
                "Profiles",
                field_item("active_profile", active_profile),
                field_item("profiles", ", ".join(profiles)),
            )
        ],
        metadata={
            "kind": "profile_list",
            "active_profile": active_profile,
            "profiles": list(profiles),
        },
    )


def build_profile_create_output(*, profile: str, path: Path, created: bool) -> CommandOutput:
    """Build one unified output model for ``profile create``."""
    message = (
        success_message(f"Created profile '{profile}'")
        if created
        else warning_message(f"Profile '{profile}' already exists")
    )

    return CommandOutput(
        messages=[message],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("path", path_to_str(path)),
            )
        ],
        metadata={
            "kind": "profile_create",
            "profile": profile,
            "path": path_to_str(path),
            "created": created,
        },
    )


def build_profile_copy_output(
    *,
    source_profile: str,
    target_profile: str,
    source_path: Path,
    target_path: Path,
    copied_keys: int,
) -> CommandOutput:
    """Build one unified output model for ``profile copy``."""
    return CommandOutput(
        messages=[success_message(f"Copied profile '{source_profile}' into '{target_profile}'")],
        sections=[
            _details_section(
                field_item("source_profile", source_profile),
                field_item("target_profile", target_profile),
                field_item("source_path", path_to_str(source_path)),
                field_item("target_path", path_to_str(target_path)),
                field_item("copied_keys", str(copied_keys)),
            )
        ],
        metadata={
            "kind": "profile_copy",
            "source_profile": source_profile,
            "target_profile": target_profile,
            "source_path": path_to_str(source_path),
            "target_path": path_to_str(target_path),
            "copied_keys": copied_keys,
        },
    )


def build_profile_remove_output(*, profile: str, path: Path, removed: bool) -> CommandOutput:
    """Build one unified output model for ``profile remove``."""
    message = (
        success_message(f"Removed profile '{profile}'")
        if removed
        else warning_message(f"Profile '{profile}' does not exist")
    )

    return CommandOutput(
        messages=[message],
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("path", path_to_str(path)),
            )
        ],
        metadata={
            "kind": "profile_remove",
            "profile": profile,
            "path": path_to_str(path),
            "removed": removed,
        },
    )


def build_profile_path_output(*, profile: str, path: Path) -> CommandOutput:
    """Build one unified output model for ``profile path``."""
    return CommandOutput(
        sections=[
            _details_section(
                field_item("profile", profile),
                field_item("path", path_to_str(path)),
            )
        ],
        metadata={
            "kind": "profile_path",
            "profile": profile,
            "path": path_to_str(path),
        },
    )


def build_project_bind_output(
    *,
    changed: bool,
    display_name: str,
    project_key: str,
    project_id: str,
    binding_source: str,
    repo_root: Path,
    vault_dir: Path,
    vault_values_path: Path,
) -> CommandOutput:
    """Build one unified output model for ``project bind``."""
    message = (
        success_message(f"Bound repository to {display_name}")
        if changed
        else warning_message(f"Repository already bound to {display_name}")
    )

    return CommandOutput(
        messages=[message],
        sections=[
            _details_section(
                field_item("project_key", project_key),
                field_item("project_id", project_id),
                field_item("binding_source", binding_source),
                field_item("repo_root", path_to_str(repo_root)),
                field_item("vault_dir", path_to_str(vault_dir)),
                field_item("vault_values", path_to_str(vault_values_path)),
            )
        ],
        metadata={
            "kind": "project_bind",
            "changed": changed,
            "display_name": display_name,
            "project_key": project_key,
            "project_id": project_id,
            "binding_source": binding_source,
            "repo_root": path_to_str(repo_root),
            "vault_dir": path_to_str(vault_dir),
            "vault_values": path_to_str(vault_values_path),
        },
    )


def build_project_rebind_output(
    *,
    display_name: str,
    previous_project_id: str | None,
    new_project_id: str,
    copied_values: bool,
    repo_root: Path,
    vault_dir: Path,
    vault_values_path: Path,
) -> CommandOutput:
    """Build one unified output model for ``project rebind``."""
    items = [
        field_item("new_project_id", new_project_id),
        field_item("copied_values", _yes_no(copied_values)),
        field_item("repo_root", path_to_str(repo_root)),
        field_item("vault_dir", path_to_str(vault_dir)),
        field_item("vault_values", path_to_str(vault_values_path)),
    ]
    if previous_project_id is not None:
        items.insert(0, field_item("previous_project_id", previous_project_id))

    return CommandOutput(
        messages=[success_message(f"Rebound repository to {display_name}")],
        sections=[_details_section(*items)],
        metadata={
            "kind": "project_rebind",
            "display_name": display_name,
            "previous_project_id": previous_project_id,
            "new_project_id": new_project_id,
            "copied_values": copied_values,
            "repo_root": path_to_str(repo_root),
            "vault_dir": path_to_str(vault_dir),
            "vault_values": path_to_str(vault_values_path),
        },
    )


def build_project_repair_output(
    *,
    status: str,
    detail: str,
    project_id: str | None,
    binding_source: str | None,
    repo_root: Path | None,
    vault_dir: Path | None,
    vault_values_path: Path | None,
) -> CommandOutput:
    """Build one unified output model for ``project repair``."""
    message = (
        success_message(detail)
        if status in {"healthy", "repaired", "created", "recreated"}
        else warning_message(detail)
    )

    items: list[OutputItem] = []
    if project_id is not None:
        items.append(field_item("project_id", project_id))
    if binding_source is not None:
        items.append(field_item("binding_source", binding_source))
    if repo_root is not None:
        items.append(field_item("repo_root", path_to_str(repo_root)))
    if vault_dir is not None:
        items.append(field_item("vault_dir", path_to_str(vault_dir)))
    if vault_values_path is not None:
        items.append(field_item("vault_values", path_to_str(vault_values_path)))

    sections = [_details_section(*items)] if items else []

    return CommandOutput(
        messages=[message],
        sections=sections,
        metadata={
            "kind": "project_repair",
            "status": status,
            "detail": detail,
            "project_id": project_id,
            "binding_source": binding_source,
            "repo_root": _optional_path(repo_root),
            "vault_dir": _optional_path(vault_dir),
            "vault_values": _optional_path(vault_values_path),
        },
    )


def build_project_unbind_output(
    *,
    removed: bool,
    repo_root: Path,
    previous_project_id: str | None,
) -> CommandOutput:
    """Build one unified output model for ``project unbind``."""
    items = [field_item("repo_root", path_to_str(repo_root))]
    if previous_project_id is not None:
        items.append(field_item("previous_project_id", previous_project_id))

    message = (
        success_message("Removed local repository binding")
        if removed
        else warning_message("No local repository binding was present")
    )

    return CommandOutput(
        messages=[message],
        sections=[_details_section(*items)],
        metadata={
            "kind": "project_unbind",
            "removed": removed,
            "repo_root": path_to_str(repo_root),
            "previous_project_id": previous_project_id,
        },
    )


def build_run_warnings_output(warnings: tuple[str, ...]) -> CommandOutput:
    """Build one unified output model for run warnings."""
    return CommandOutput(
        messages=[warning_message(warning) for warning in warnings],
        sections=[section("Warnings", *(raw_item(warning) for warning in warnings))]
        if warnings
        else [],
        metadata={
            "kind": "run_warnings",
            "warnings": list(warnings),
        },
    )
