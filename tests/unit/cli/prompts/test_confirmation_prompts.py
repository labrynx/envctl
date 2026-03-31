"""Tests for CLI confirmation prompt builders."""

from __future__ import annotations

from types import SimpleNamespace

from envctl.cli.prompts.confirmation_prompts import (
    build_profile_remove_confirmation_message,
    build_project_rebind_confirmation_message,
    build_remove_confirmation_message,
    build_vault_prune_confirmation_message,
    build_vault_show_raw_confirmation_message,
)


def test_build_profile_remove_confirmation_message() -> None:
    """It should build the expected profile removal prompt."""
    result = build_profile_remove_confirmation_message("prod")
    assert result == "Remove profile 'prod'?"


def test_build_project_rebind_confirmation_message() -> None:
    """It should build the expected project rebind prompt."""
    result = build_project_rebind_confirmation_message()
    assert result == "This will generate a new project identity for the current checkout. Continue?"


def test_build_remove_confirmation_message_with_active_and_other_profiles() -> None:
    """It should include active and other profile details when present."""
    plan = SimpleNamespace(
        present_in_active_profile=True,
        present_in_other_profiles=("prod", "staging"),
    )

    result = build_remove_confirmation_message("DATABASE_URL", plan)

    assert "Remove 'DATABASE_URL' from the contract and all profiles?" in result
    assert "- present in the active profile" in result
    assert "- also present in: prod, staging" in result


def test_build_remove_confirmation_message_without_extra_profile_details() -> None:
    """It should keep the message compact when no extra profile details exist."""
    plan = SimpleNamespace(
        present_in_active_profile=False,
        present_in_other_profiles=(),
    )

    result = build_remove_confirmation_message("DEBUG", plan)

    assert result == "Remove 'DEBUG' from the contract and all profiles?"


def test_build_vault_prune_confirmation_message() -> None:
    """It should build the expected vault prune prompt."""
    result = build_vault_prune_confirmation_message(
        profile="prod",
        unknown_key_count=3,
    )
    assert result == "Remove 3 unknown key(s) from profile 'prod'?"


def test_build_vault_show_raw_confirmation_message() -> None:
    """It should build the expected raw vault display prompt."""
    result = build_vault_show_raw_confirmation_message()
    assert result == "This will display unmasked secret values. Continue?"
