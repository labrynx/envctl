"""Presenters for action-style commands."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from envctl.domain.hooks import HooksReason
from envctl.utils.masking import mask_value
from envctl.utils.output import (
    print_kv,
    print_result_summary,
    print_section,
    print_success,
    print_warning,
)

if TYPE_CHECKING:
    from envctl.domain.operations import InitResult


def render_config_init_result(config_path: Path) -> None:
    """Render config init output."""
    print_result_summary(
        title="Created envctl config file",
        success=True,
        metadata={
            "config": str(config_path),
        },
    )


def render_add_result(
    *,
    key: str,
    profile: str,
    profile_path: Path,
    contract_path: Path,
    contract_created: bool,
    contract_updated: bool,
    contract_entry_created: bool,
) -> None:
    """Render add command output."""
    print_success(f"Added '{key}' to contract and profile '{profile}'")
    print_kv("profile", profile)
    print_kv("vault_values", str(profile_path))
    print_kv("contract", str(contract_path))

    if contract_created:
        print_kv("contract_created", "yes")
    if contract_updated:
        print_kv("contract_updated", "yes")
    if contract_entry_created:
        print_kv("contract_entry_created", "yes")


def render_inferred_spec(inferred_spec: dict[str, object] | None) -> None:
    """Render inferred metadata details when present."""
    if inferred_spec is None:
        return

    print_section("Inferred metadata")

    if "type" in inferred_spec:
        print_kv("inferred_type", str(inferred_spec["type"]))
    if "required" in inferred_spec:
        print_kv("required", "yes" if inferred_spec["required"] else "no")
    if "sensitive" in inferred_spec:
        print_kv("sensitive", "yes" if inferred_spec["sensitive"] else "no")
    if "description" in inferred_spec:
        print_kv("description", str(inferred_spec["description"]))

    print_warning("Review .envctl.yaml to confirm the inferred metadata.")


def render_inspect_value(
    *,
    profile: str,
    key: str,
    source: str,
    raw_value: str | None,
    value: str,
    masked: bool,
    expansion_status: str,
    expansion_refs: tuple[str, ...],
    expansion_error: str | None,
    valid: bool,
    detail: str | None,
) -> None:
    """Render inspected variable output."""
    shown_value = mask_value(value) if masked else value

    print_kv("profile", profile)
    print_kv("key", key)
    print_kv("source", source)
    if raw_value is not None:
        print_kv("raw_value", raw_value)
    print_kv("value", shown_value)
    print_kv("expansion_status", expansion_status)
    if expansion_refs:
        print_kv("expansion_refs", ", ".join(expansion_refs))
    if expansion_error is not None:
        print_kv("expansion_error", expansion_error)
    print_kv("valid", "yes" if valid else "no")

    if detail:
        print_kv("detail", detail)


def render_export_output(*, profile: str, rendered: str) -> None:
    """Render export command output."""
    print_kv("profile", profile)
    if rendered:
        print(rendered, end="")


def render_fill_no_changes(
    *,
    profile: str,
    profile_path: Path | None = None,
) -> None:
    """Render fill output when nothing changes."""
    print_warning("No keys were changed")
    print_kv("profile", profile)
    if profile_path is not None:
        print_kv("vault_values", str(profile_path))


def render_fill_result(
    *,
    project_name: str,
    profile: str,
    profile_path: Path,
    changed_keys: list[str],
) -> None:
    """Render fill command output."""
    if not changed_keys:
        render_fill_no_changes(
            profile=profile,
            profile_path=profile_path,
        )
        return

    print_success(f"Filled {len(changed_keys)} key(s) for {project_name}")
    print_kv("profile", profile)
    print_kv("vault_values", str(profile_path))
    print_kv("keys", ", ".join(changed_keys))


def render_init_result(
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
) -> None:
    """Render init command output."""
    print_success(f"Initialized {display_name}")
    print_kv("project_key", project_key)
    print_kv("binding_source", binding_source)
    print_kv("repo_root", str(repo_root))
    print_kv("contract", str(contract_path))
    print_kv("vault_dir", str(vault_dir))
    print_kv("vault_values", str(vault_values_path))
    print_kv("vault_state", str(vault_state_path))

    if init_result.contract_created:
        print_kv("contract_created", "yes")
        print_kv("contract_template", init_result.contract_template or "custom")
    elif init_result.contract_skipped:
        print_warning("No contract file was created")

    print_kv("hooks_installed", "yes" if init_result.hooks_installed else "no")
    if init_result.hooks_reason is not None:
        print_kv("hooks_reason", init_result.hooks_reason.value)
    if init_result.hooks_reason is not None and init_result.hooks_reason not in {
        HooksReason.INSTALLED,
        HooksReason.ALREADY_HEALTHY,
    }:
        print_warning(_render_hooks_reason(init_result.hooks_reason))
    for warning in init_result.runtime_warnings:
        print_warning(warning)


def _render_hooks_reason(reason: HooksReason) -> str:
    if reason == HooksReason.PARTIAL_CONFLICT:
        return "Managed hooks were partially installed, but conflicts remain."
    if reason == HooksReason.UNSUPPORTED_HOOKS_PATH:
        return "Managed hooks were not installed because the effective hooks path is unsupported."
    if reason == HooksReason.FOREIGN_HOOK_PRESENT:
        return "Managed hooks were not installed because a foreign hook is already present."
    if reason == HooksReason.INSTALL_FAILED:
        return "Managed hooks could not be installed due to an unexpected error."
    return reason.value


def render_remove_result(
    *,
    key: str,
    contract_path: Path,
    removed_from_contract: bool,
    inspected_profiles: tuple[str, ...],
    removed_from_profiles: tuple[str, ...],
    missing_from_profiles: tuple[str, ...],
    affected_paths: tuple[Path, ...],
    repo_root: Path,
) -> None:
    """Render remove command output."""
    print_success(f"Removed '{key}' from contract and persisted profiles")
    print_kv("contract", str(contract_path))
    print_kv("removed_from_contract", "yes" if removed_from_contract else "no")
    print_kv(
        "removed_from_profiles",
        ", ".join(removed_from_profiles) if removed_from_profiles else "none",
    )
    print_kv(
        "inspected_profiles",
        ", ".join(inspected_profiles) if inspected_profiles else "none",
    )
    print_kv(
        "missing_from_profiles",
        ", ".join(missing_from_profiles) if missing_from_profiles else "none",
    )

    if affected_paths:
        print_kv("affected_paths", ", ".join(str(path) for path in affected_paths))

    print_kv("repo_root", str(repo_root))


def render_set_result(
    *,
    key: str,
    profile: str,
    profile_path: Path,
) -> None:
    """Render set command output."""
    print_success(f"Set '{key}' in profile '{profile}'")
    print_kv("profile", profile)
    print_kv("vault_values", str(profile_path))


def render_unset_result(
    *,
    key: str,
    profile: str,
    profile_path: Path,
    removed: bool,
) -> None:
    """Render unset command output."""
    if removed:
        print_success(f"Unset '{key}' in profile '{profile}'")
    else:
        print_warning(f"'{key}' was not set in profile '{profile}'")

    print_kv("profile", profile)
    print_kv("vault_values", str(profile_path))


def render_sync_result(*, profile: str, target_path: Path) -> None:
    """Render sync command output."""
    print_success("Synced generated environment")
    print_kv("profile", profile)
    print_kv("target", str(target_path))
