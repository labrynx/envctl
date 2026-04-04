from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.config_error_presenter import render_config_error
from envctl.cli.presenters.repository_error_presenter import (
    render_project_binding_error,
    render_repository_discovery_error,
)
from envctl.cli.presenters.state_error_presenter import render_state_error
from envctl.services.error_diagnostics import (
    ConfigDiagnostics,
    ProjectBindingDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)


def test_render_config_error_renders_path_source_and_actions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_config_error(
        ConfigDiagnostics(
            category="invalid_runtime_mode",
            path=Path("/tmp/config.json"),
            source_label="config file",
            value="'banana'",
            suggested_actions=("set runtime_mode to local or ci",),
        ),
        message="Invalid runtime mode in config file: 'banana'",
    )
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Error: Invalid runtime mode in config file: 'banana'" in captured.err
    assert "path: /tmp/config.json" in captured.err
    assert "source: config file" in captured.err
    assert "value: 'banana'" in captured.err


def test_render_state_error_renders_path_and_actions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_state_error(
        StateDiagnostics(
            category="corrupted_state",
            path=Path("/tmp/state.json"),
            field="root",
            suggested_actions=("repair the project binding",),
        ),
        message="State file is corrupted: /tmp/state.json",
    )
    captured = capsys.readouterr()

    assert "path: /tmp/state.json" in captured.err
    assert "field: root" in captured.err


def test_render_repository_error_presenters_render_facts(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_repository_discovery_error(
        RepositoryDiscoveryDiagnostics(
            category="not_a_git_repository",
            repo_root=Path("/tmp/repo"),
            git_stderr="fatal: not a git repository",
            suggested_actions=("run envctl inside a git repository",),
        ),
        message="fatal: not a git repository",
    )
    render_project_binding_error(
        ProjectBindingDiagnostics(
            category="ambiguous_vault_identity",
            repo_root=Path("/tmp/repo"),
            matching_ids=("prj_a", "prj_b"),
            matching_directories=(Path("/tmp/a"), Path("/tmp/b")),
            suggested_actions=("envctl project bind",),
        ),
        message="Ambiguous vault identity for this repository.",
    )
    captured = capsys.readouterr()

    assert "repo_root: /tmp/repo" in captured.err
    assert "git_stderr: fatal: not a git repository" in captured.err
    assert "matching_ids: prj_a, prj_b" in captured.err
    assert "matching_directories:" in captured.err
