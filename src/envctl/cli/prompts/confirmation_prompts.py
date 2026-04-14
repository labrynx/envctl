"""Confirmation prompt builders."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envctl.domain.operations import RemovePlan


def build_profile_remove_confirmation_message(profile: str) -> str:
    """Build the confirmation message for profile removal."""
    return f"Remove profile '{profile}'?"


def build_project_rebind_confirmation_message() -> str:
    """Build the confirmation message for project rebind."""
    return "This will generate a new project identity for the current checkout. Continue?"


def build_remove_confirmation_message(
    key: str,
    plan: RemovePlan | None = None,
    *,
    present_in_active_profile: bool | None = None,
    present_in_other_profiles: Sequence[str] | None = None,
    absent_in_other_profiles: Sequence[str] | None = None,
) -> str:
    """Build the confirmation message for removing a declared key.

    Supports both the legacy `plan` argument and the newer explicit keyword form.
    """
    if plan is not None:
        present_in_active_profile = plan.present_in_active_profile
        present_in_other_profiles = plan.present_in_other_profiles
        absent_in_other_profiles = plan.absent_in_other_profiles

    active = bool(present_in_active_profile)
    present_elsewhere = tuple(present_in_other_profiles or ())
    absent_elsewhere = tuple(absent_in_other_profiles or ())

    lines = [f"Remove '{key}' from the contract and all profiles?"]

    if active:
        lines.append("- present in the active profile")

    if present_elsewhere:
        lines.append(f"- also present in: {', '.join(present_elsewhere)}")

    if absent_elsewhere:
        lines.append(f"- not present in: {', '.join(absent_elsewhere)}")

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
