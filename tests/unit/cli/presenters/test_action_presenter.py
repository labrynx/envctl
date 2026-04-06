"""Tests for action presenters."""

from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.action_presenter import (
    render_add_result,
    render_config_init_result,
    render_export_output,
    render_fill_no_changes,
    render_fill_result,
    render_inferred_spec,
    render_init_result,
    render_inspect_value,
    render_remove_result,
    render_set_result,
    render_sync_result,
    render_unset_result,
)
from envctl.services.init_service import InitResult


def test_render_config_init_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render config init output."""
    render_config_init_result(Path("/tmp/envctl/config.json"))
    captured = capsys.readouterr().out

    assert "[OK] Created envctl config file" in captured
    assert "config: /tmp/envctl/config.json" in captured


def test_render_add_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render add command output."""
    render_add_result(
        key="DATABASE_URL",
        profile="prod",
        profile_path=Path("/tmp/vault/prod.env"),
        contract_path=Path("/workspace/.envctl.yaml"),
        contract_created=True,
        contract_updated=True,
        contract_entry_created=True,
    )
    captured = capsys.readouterr().out

    assert "[OK] Added 'DATABASE_URL' to contract and profile 'prod'" in captured
    assert "profile: prod" in captured
    assert "vault_values: /tmp/vault/prod.env" in captured
    assert "contract: /workspace/.envctl.yaml" in captured
    assert "contract_created: yes" in captured
    assert "contract_updated: yes" in captured
    assert "contract_entry_created: yes" in captured


def test_render_inferred_spec_when_present(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render inferred metadata details."""
    render_inferred_spec(
        {
            "type": "url",
            "required": True,
            "sensitive": True,
            "description": "Primary database connection URL",
        }
    )
    captured = capsys.readouterr().out

    assert "Inferred metadata" in captured
    assert "inferred_type: url" in captured
    assert "required: yes" in captured
    assert "sensitive: yes" in captured
    assert "description: Primary database connection URL" in captured
    assert "[WARN] Review .envctl.yaml to confirm the inferred metadata." in captured


def test_render_inferred_spec_when_none(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render nothing when there is no inferred spec."""
    render_inferred_spec(None)
    captured = capsys.readouterr().out

    assert captured == ""


def test_render_inspect_value_masks_when_needed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should mask sensitive values in explain output."""
    render_inspect_value(
        profile="prod",
        key="TOKEN",
        source="vault",
        raw_value=None,
        value="supersecret",
        masked=True,
        expansion_status="none",
        expansion_refs=(),
        expansion_error=None,
        valid=True,
        detail=None,
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "key: TOKEN" in captured
    assert "source: vault" in captured
    assert "value: su*********" in captured
    assert "valid: yes" in captured


def test_render_inspect_value_with_detail(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render validation detail when present."""
    render_inspect_value(
        profile="local",
        key="PORT",
        source="vault",
        raw_value="abc",
        value="abc",
        masked=False,
        expansion_status="none",
        expansion_refs=(),
        expansion_error=None,
        valid=False,
        detail="Expected an integer",
    )
    captured = capsys.readouterr().out

    assert "value: abc" in captured
    assert "raw_value: abc" in captured
    assert "valid: no" in captured
    assert "detail: Expected an integer" in captured


def test_render_export_output_with_rendered_content(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render profile and export lines."""
    render_export_output(
        profile="prod",
        rendered="export A='1'\nexport B='2'\n",
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "export A='1'" in captured
    assert "export B='2'" in captured


def test_render_export_output_without_rendered_content(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render only the profile when there is no export body."""
    render_export_output(profile="prod", rendered="")
    captured = capsys.readouterr().out

    assert captured == "profile: prod\n"


def test_render_fill_no_changes_without_profile_path(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render fill no-changes without vault path."""
    render_fill_no_changes(profile="local")
    captured = capsys.readouterr().out

    assert "[WARN] No keys were changed" in captured
    assert "profile: local" in captured
    assert "vault_values:" not in captured


def test_render_fill_no_changes_with_profile_path(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render fill no-changes with vault path."""
    render_fill_no_changes(
        profile="prod",
        profile_path=Path("/tmp/vault/prod.env"),
    )
    captured = capsys.readouterr().out

    assert "profile: prod" in captured
    assert "vault_values: /tmp/vault/prod.env" in captured


def test_render_fill_result_with_changes(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render successful fill output."""
    render_fill_result(
        project_name="demo-app",
        profile="prod",
        profile_path=Path("/tmp/vault/prod.env"),
        changed_keys=["DATABASE_URL", "TOKEN"],
    )
    captured = capsys.readouterr().out

    assert "[OK] Filled 2 key(s) for demo-app" in captured
    assert "profile: prod" in captured
    assert "vault_values: /tmp/vault/prod.env" in captured
    assert "keys: DATABASE_URL, TOKEN" in captured


def test_render_fill_result_without_changes_delegates_to_no_changes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """It should render the no-change path when changed_keys is empty."""
    render_fill_result(
        project_name="demo-app",
        profile="prod",
        profile_path=Path("/tmp/vault/prod.env"),
        changed_keys=[],
    )
    captured = capsys.readouterr().out

    assert "[WARN] No keys were changed" in captured
    assert "vault_values: /tmp/vault/prod.env" in captured


def test_render_init_result_with_created_contract(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render init output with contract creation details."""
    init_result = InitResult(
        contract_created=True,
        contract_template="starter",
        contract_skipped=False,
    )

    render_init_result(
        project_key="demo-app",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        contract_path=Path("/workspace/demo-app/.envctl.yaml"),
        vault_dir=Path("/tmp/vault/demo-app--prj_x"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_x/values.env"),
        vault_state_path=Path("/tmp/vault/demo-app--prj_x/state.json"),
        init_result=init_result,
        display_name="demo-app",
    )
    captured = capsys.readouterr().out

    assert "[OK] Initialized demo-app" in captured
    assert "project_key: demo-app" in captured
    assert "binding_source: local" in captured
    assert "contract_created: yes" in captured
    assert "contract_template: starter" in captured


def test_render_init_result_with_skipped_contract(capsys: pytest.CaptureFixture[str]) -> None:
    """It should warn when init skipped contract creation."""
    init_result = InitResult(
        contract_created=False,
        contract_template=None,
        contract_skipped=True,
    )

    render_init_result(
        project_key="demo-app",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        contract_path=Path("/workspace/demo-app/.envctl.yaml"),
        vault_dir=Path("/tmp/vault/demo-app--prj_x"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_x/values.env"),
        vault_state_path=Path("/tmp/vault/demo-app--prj_x/state.json"),
        init_result=init_result,
        display_name="demo-app",
    )
    captured = capsys.readouterr().out

    assert "[WARN] No contract file was created" in captured


def test_render_remove_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render remove output."""
    render_remove_result(
        key="TOKEN",
        contract_path=Path("/workspace/.envctl.yaml"),
        removed_from_contract=True,
        inspected_profiles=("local", "prod", "staging"),
        removed_from_profiles=("local", "prod"),
        missing_from_profiles=("staging",),
        affected_paths=(
            Path("/tmp/vault/values.env"),
            Path("/tmp/vault/profiles/prod.env"),
        ),
        repo_root=Path("/workspace"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Removed 'TOKEN' from contract and persisted profiles" in captured
    assert "removed_from_contract: yes" in captured
    assert "inspected_profiles: local, prod, staging" in captured
    assert "removed_from_profiles: local, prod" in captured
    assert "missing_from_profiles: staging" in captured
    assert "affected_paths: /tmp/vault/values.env, /tmp/vault/profiles/prod.env" in captured
    assert "repo_root: /workspace" in captured


def test_render_set_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render set output."""
    render_set_result(
        key="DEBUG",
        profile="local",
        profile_path=Path("/tmp/vault/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Set 'DEBUG' in profile 'local'" in captured
    assert "profile: local" in captured
    assert "vault_values: /tmp/vault/values.env" in captured


def test_render_unset_result_removed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render removed unset output."""
    render_unset_result(
        key="DEBUG",
        profile="local",
        profile_path=Path("/tmp/vault/values.env"),
        removed=True,
    )
    captured = capsys.readouterr().out

    assert "[OK] Unset 'DEBUG' in profile 'local'" in captured


def test_render_unset_result_not_removed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render warning unset output."""
    render_unset_result(
        key="DEBUG",
        profile="local",
        profile_path=Path("/tmp/vault/values.env"),
        removed=False,
    )
    captured = capsys.readouterr().out

    assert "[WARN] 'DEBUG' was not set in profile 'local'" in captured


def test_render_sync_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render sync output."""
    render_sync_result(
        profile="prod",
        target_path=Path("/workspace/.env"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Synced generated environment" in captured
    assert "profile: prod" in captured
    assert "target: /workspace/.env" in captured
