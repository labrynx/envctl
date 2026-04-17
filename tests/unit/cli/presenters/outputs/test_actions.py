from __future__ import annotations

from pathlib import Path

from envctl.cli.presenters.outputs.actions import (
    build_add_output,
    build_config_init_output,
    build_fill_no_changes_output,
    build_set_output,
    build_sync_output,
    build_unset_output,
)


def test_build_config_init_output() -> None:
    output = build_config_init_output(Path("/tmp/.envctl.toml"))
    assert output.messages[0].text == "Created envctl config file"
    assert output.metadata["kind"] == "config_init"


def test_build_add_output() -> None:
    output = build_add_output(
        key="API_KEY",
        profile="local",
        profile_path=Path("/tmp/values.env"),
        contract_path=Path("/tmp/.envctl.yaml"),
        contract_created=True,
        contract_updated=True,
        contract_entry_created=True,
    )
    assert output.metadata["kind"] == "add"
    assert output.metadata["key"] == "API_KEY"
    assert output.metadata["contract_created"] is True


def test_build_fill_no_changes_output() -> None:
    output = build_fill_no_changes_output(
        profile="local",
        profile_path=Path("/tmp/values.env"),
    )
    assert output.metadata["kind"] == "fill"
    assert output.metadata["changed"] is False


def test_build_set_output() -> None:
    output = build_set_output(
        key="API_KEY",
        profile="local",
        profile_path=Path("/tmp/values.env"),
    )
    assert output.metadata["kind"] == "set"
    assert output.messages[0].level == "success"


def test_build_unset_output_removed() -> None:
    output = build_unset_output(
        key="API_KEY",
        profile="local",
        profile_path=Path("/tmp/values.env"),
        removed=True,
    )
    assert output.metadata["removed"] is True
    assert output.messages[0].level == "success"


def test_build_unset_output_not_removed() -> None:
    output = build_unset_output(
        key="API_KEY",
        profile="local",
        profile_path=Path("/tmp/values.env"),
        removed=False,
    )
    assert output.metadata["removed"] is False
    assert output.messages[0].level == "warning"


def test_build_sync_output() -> None:
    output = build_sync_output(profile="local", target_path=Path("/tmp/.env"))
    assert output.metadata["kind"] == "sync"
    assert output.metadata["profile"] == "local"
