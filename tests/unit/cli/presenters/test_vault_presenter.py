"""Tests for vault presenters."""

from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.vault_presenter import (
    render_vault_check_result,
    render_vault_edit_result,
    render_vault_path_result,
    render_vault_prune_cancelled,
    render_vault_prune_no_changes,
    render_vault_prune_result,
    render_vault_show_cancelled,
    render_vault_show_empty,
    render_vault_show_missing,
    render_vault_show_values,
)


def test_render_vault_check_result_when_file_is_missing(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the missing vault file case."""
    render_vault_check_result(
        profile="local",
        path=Path("/tmp/demo/values.env"),
        exists=False,
        parseable=False,
        private_permissions=False,
        key_count=0,
    )
    captured = capsys.readouterr().out

    assert "[WARN] Vault file does not exist" in captured
    assert "profile: local" in captured
    assert "vault_values: /tmp/demo/values.env" in captured


def test_render_vault_check_result_when_permissions_are_not_private(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """It should render the non-private permissions case."""
    render_vault_check_result(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
        exists=True,
        parseable=True,
        private_permissions=False,
        key_count=3,
    )
    captured = capsys.readouterr().out

    assert "[WARN] Vault file is parseable but permissions are not private enough" in captured
    assert "profile: prod" in captured
    assert "parseable: yes" in captured
    assert "private_permissions: no" in captured
    assert "keys: 3" in captured


def test_render_vault_check_result_when_file_is_valid(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the valid vault file case."""
    render_vault_check_result(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
        exists=True,
        parseable=True,
        private_permissions=True,
        key_count=2,
    )
    captured = capsys.readouterr().out

    assert "[OK] Vault file looks valid" in captured
    assert "private_permissions: yes" in captured


def test_render_vault_edit_result_created(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the created-and-opened vault case."""
    render_vault_edit_result(
        profile="staging",
        path=Path("/tmp/demo/staging.env"),
        created=True,
    )
    captured = capsys.readouterr().out

    assert "[OK] Created and opened profile 'staging' vault file" in captured
    assert "profile: staging" in captured


def test_render_vault_edit_result_open_existing(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the opened existing vault case."""
    render_vault_edit_result(
        profile="staging",
        path=Path("/tmp/demo/staging.env"),
        created=False,
    )
    captured = capsys.readouterr().out

    assert "[OK] Opened profile 'staging' vault file" in captured


def test_render_vault_path_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the vault path output."""
    render_vault_path_result(
        profile="local",
        path=Path("/tmp/demo/values.env"),
    )
    captured = capsys.readouterr().out

    assert "profile: local" in captured
    assert "vault_values: /tmp/demo/values.env" in captured


def test_render_vault_prune_no_changes(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the no-changes prune case."""
    render_vault_prune_no_changes(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "[WARN] No unknown keys were removed" in captured


def test_render_vault_prune_cancelled(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the cancelled prune case."""
    render_vault_prune_cancelled(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
    )
    captured = capsys.readouterr().out

    assert "[WARN] No unknown keys were removed" in captured
    assert "kept_keys: unchanged" in captured


def test_render_vault_prune_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render removed and kept key information."""
    render_vault_prune_result(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
        removed_keys=("OLD_KEY", "LEGACY_FLAG"),
        kept_keys=4,
    )
    captured = capsys.readouterr().out

    assert "[OK] Removed 2 unknown key(s) from profile 'prod'" in captured
    assert "removed_keys: OLD_KEY, LEGACY_FLAG" in captured
    assert "kept_keys: 4" in captured


def test_render_vault_show_missing(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the missing vault show case."""
    render_vault_show_missing(
        profile="local",
        path=Path("/tmp/demo/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[WARN] Vault file does not exist" in captured
    assert "profile: local" in captured


def test_render_vault_show_empty(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the empty vault show case."""
    render_vault_show_empty(
        profile="local",
        path=Path("/tmp/demo/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[WARN] Vault file is empty" in captured


def test_render_vault_show_cancelled(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the cancelled raw vault display case."""
    render_vault_show_cancelled(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
    )
    captured = capsys.readouterr().out

    assert "[WARN] Nothing was shown." in captured


def test_render_vault_show_values(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render the values section in sorted order."""
    render_vault_show_values(
        profile="prod",
        path=Path("/tmp/demo/prod.env"),
        values={
            "Z_KEY": "zzz",
            "A_KEY": "aaa",
        },
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "vault_values: /tmp/demo/prod.env" in captured
    assert "Values:" in captured

    a_index = captured.index("  A_KEY=aaa")
    z_index = captured.index("  Z_KEY=zzz")
    assert a_index < z_index
