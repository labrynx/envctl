"""Confirmation prompt builders."""

from __future__ import annotations

from collections.abc import Sequence


def build_profile_remove_confirmation_message(profile: str) -> str:
    """Build the confirmation message for profile removal."""
    return f"Remove profile '{profile}'?"


def build_project_rebind_confirmation_message() -> str:
    """Build the confirmation message for project rebind."""
    return "This will generate a new project identity for the current checkout. Continue?"


def build_remove_confirmation_message(
    key: str,
    *,
    present_in_active_profile: bool,
    present_in_other_profiles: Sequence[str],
    absent_in_other_profiles: Sequence[str],
) -> str:
    """Build the confirmation message for removing a declared key."""
    lines = [f"Remove '{key}' from the contract and all profiles?"]

    if present_in_active_profile:
        lines.append("- present in the active profile")

    if present_in_other_profiles:
        lines.append(f"- also present in: {', '.join(present_in_other_profiles)}")

    if absent_in_other_profiles:
        lines.append(f"- not present in: {', '.join(absent_in_other_profiles)}")

    return "\n".join(lines)


def build_vault_prune_confirmation_message(
    *,
    profile: str,
    unknown_key_count: int,
) -> str:
    """Build the confirmation message for vault prune."""
    return f"Remove {unknown_key_count} unknown key(s) from profile '{profile}'?"


def build_vault_show_raw_confirmation_message() -> str:
    """Build the confirmation message for raw vault display."""
    return "This will display unmasked secret values. Continue?"
