from __future__ import annotations

from pathlib import Path

from envctl.cli.presenters.outputs.vault import (
    build_vault_check_output,
    build_vault_edit_output,
    build_vault_path_output,
    build_vault_prune_cancelled_output,
    build_vault_prune_no_changes_output,
    build_vault_prune_output,
    build_vault_show_cancelled_output,
    build_vault_show_empty_output,
    build_vault_show_missing_output,
    build_vault_show_values_output,
)


def test_build_vault_check_output_missing() -> None:
    output = build_vault_check_output(
        profile="local",
        path=Path("/tmp/values.env"),
        exists=False,
        parseable=False,
        private_permissions=False,
        key_count=0,
        state="missing",
    )
    assert output.metadata["kind"] == "vault_check"
    assert output.metadata["ok"] is False


def test_build_vault_check_output_encrypted() -> None:
    output = build_vault_check_output(
        profile="local",
        path=Path("/tmp/values.env"),
        exists=True,
        parseable=True,
        private_permissions=True,
        key_count=2,
        state="encrypted",
    )
    assert output.metadata["ok"] is True
    assert output.messages[0].level == "success"


def test_build_vault_edit_output() -> None:
    output = build_vault_edit_output(profile="local", path=Path("/tmp/values.env"), created=True)
    assert output.metadata["kind"] == "vault_edit"
    assert output.metadata["created"] is True


def test_build_vault_path_output() -> None:
    output = build_vault_path_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["kind"] == "vault_path"


def test_build_vault_prune_no_changes_output() -> None:
    output = build_vault_prune_no_changes_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["changed"] is False
    assert output.metadata["cancelled"] is False


def test_build_vault_prune_cancelled_output() -> None:
    output = build_vault_prune_cancelled_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["changed"] is False
    assert output.metadata["cancelled"] is True


def test_build_vault_prune_output() -> None:
    output = build_vault_prune_output(
        profile="local",
        path=Path("/tmp/values.env"),
        removed_keys=("A", "B"),
        kept_keys=3,
    )
    assert output.metadata["changed"] is True
    assert output.metadata["removed_keys"] == ["A", "B"]


def test_build_vault_show_missing_output() -> None:
    output = build_vault_show_missing_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["state"] == "missing"
    assert output.metadata["ok"] is False


def test_build_vault_show_empty_output() -> None:
    output = build_vault_show_empty_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["state"] == "empty"
    assert output.metadata["ok"] is True


def test_build_vault_show_cancelled_output() -> None:
    output = build_vault_show_cancelled_output(profile="local", path=Path("/tmp/values.env"))
    assert output.metadata["cancelled"] is True
    assert output.metadata["ok"] is True


def test_build_vault_show_values_output() -> None:
    output = build_vault_show_values_output(
        profile="local",
        path=Path("/tmp/values.env"),
        values={"A": "1", "B": "2"},
        state="plaintext",
        detail="demo",
    )
    assert output.metadata["kind"] == "vault_show"
    assert output.metadata["values"] == {"A": "1", "B": "2"}
