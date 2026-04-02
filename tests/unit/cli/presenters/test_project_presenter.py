"""Tests for project presenters."""

from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.project_presenter import (
    render_project_bind_result,
    render_project_rebind_result,
    render_project_repair_result,
    render_project_unbind_result,
)


def test_render_project_bind_result_changed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render successful bind output."""
    render_project_bind_result(
        changed=True,
        display_name="demo-app",
        project_key="demo-app",
        project_id="prj_1234567890ab",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        vault_dir=Path("/tmp/vault/demo-app--prj_1234567890ab"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_1234567890ab/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Bound repository to demo-app" in captured
    assert "project_key: demo-app" in captured
    assert "project_id: prj_1234567890ab" in captured
    assert "binding_source: local" in captured


def test_render_project_bind_result_unchanged(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render already-bound warning output."""
    render_project_bind_result(
        changed=False,
        display_name="demo-app",
        project_key="demo-app",
        project_id="prj_1234567890ab",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        vault_dir=Path("/tmp/vault/demo-app--prj_1234567890ab"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_1234567890ab/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[WARN] Repository already bound to demo-app" in captured


def test_render_project_rebind_result_with_previous_id(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render rebind output including the previous id."""
    render_project_rebind_result(
        display_name="demo-app",
        previous_project_id="prj_old12345678",
        new_project_id="prj_new12345678",
        copied_values=True,
        repo_root=Path("/workspace/demo-app"),
        vault_dir=Path("/tmp/vault/demo-app--prj_new12345678"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_new12345678/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Rebound repository to demo-app" in captured
    assert "previous_project_id: prj_old12345678" in captured
    assert "new_project_id: prj_new12345678" in captured
    assert "copied_values: yes" in captured


def test_render_project_rebind_result_without_previous_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """It should omit the previous id when absent."""
    render_project_rebind_result(
        display_name="demo-app",
        previous_project_id=None,
        new_project_id="prj_new12345678",
        copied_values=False,
        repo_root=Path("/workspace/demo-app"),
        vault_dir=Path("/tmp/vault/demo-app--prj_new12345678"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_new12345678/values.env"),
    )
    captured = capsys.readouterr().out

    assert "previous_project_id:" not in captured
    assert "copied_values: no" in captured


def test_render_project_repair_result_successful(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render successful repair output."""
    render_project_repair_result(
        status="repaired",
        detail="Recovered a matching vault and persisted the local git binding.",
        project_id="prj_1234567890ab",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        vault_dir=Path("/tmp/vault/demo-app--prj_1234567890ab"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_1234567890ab/values.env"),
    )
    captured = capsys.readouterr().out

    assert "[OK] Recovered a matching vault and persisted the local git binding." in captured
    assert "project_id: prj_1234567890ab" in captured
    assert "binding_source: local" in captured


def test_render_project_repair_result_needs_action(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render warning repair output."""
    render_project_repair_result(
        status="needs_action",
        detail="No persisted binding exists yet.",
        project_id="prj_1234567890ab",
        binding_source=None,
        repo_root=None,
        vault_dir=None,
        vault_values_path=None,
    )
    captured = capsys.readouterr().out

    assert "[WARN] No persisted binding exists yet." in captured
    assert "project_id: prj_1234567890ab" in captured
    assert "binding_source:" not in captured


def test_render_project_unbind_result_removed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render removed unbind output."""
    render_project_unbind_result(
        removed=True,
        repo_root=Path("/workspace/demo-app"),
        previous_project_id="prj_1234567890ab",
    )
    captured = capsys.readouterr().out

    assert "[OK] Removed local repository binding" in captured
    assert "repo_root: /workspace/demo-app" in captured
    assert "previous_project_id: prj_1234567890ab" in captured


def test_render_project_unbind_result_not_present(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render warning when there was no binding."""
    render_project_unbind_result(
        removed=False,
        repo_root=Path("/workspace/demo-app"),
        previous_project_id=None,
    )
    captured = capsys.readouterr().out

    assert "[WARN] No local repository binding was present" in captured
    assert "previous_project_id:" not in captured
