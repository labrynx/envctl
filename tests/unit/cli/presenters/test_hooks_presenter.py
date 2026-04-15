from __future__ import annotations

from pathlib import Path

import pytest
from envctl.cli.presenters.action_presenter import _render_hooks_reason, render_init_result
from envctl.cli.presenters.hooks_presenter import render_hook_operation, render_hooks_status

from envctl.domain.hooks import (
    HookAction,
    HookInspectionResult,
    HookName,
    HookOperationReport,
    HookOperationResult,
    HooksReason,
    HooksStatusLevel,
    HooksStatusReport,
    HookStatus,
)
from envctl.domain.operations import InitResult
from tests.support.paths import normalize_path_str


def test_render_hooks_status_shows_relative_and_absolute_paths(
    capsys: pytest.CaptureFixture[str],
) -> None:
    report = HooksStatusReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        overall_status=HooksStatusLevel.DEGRADED,
        details=("warn",),
        results=(
            HookInspectionResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                status=HookStatus.MISSING,
                managed=False,
                is_executable=None,
            ),
            HookInspectionResult(
                name=HookName.PRE_PUSH,
                path=Path("/outside/hooks/pre-push"),
                status=HookStatus.UNSUPPORTED,
                managed=False,
                is_executable=None,
                details=("unsupported",),
            ),
        ),
    )

    render_hooks_status(report, repo_root=Path("/tmp/demo"))
    output = normalize_path_str(capsys.readouterr().out)

    assert "Managed hooks need attention" in output
    assert "hooks_path: /tmp/demo/.git/hooks" in output
    assert "pre-commit: missing" in output
    assert "path: .git/hooks/pre-commit" in output
    assert "path: /outside/hooks/pre-push" in output
    assert "[WARN] warn" in output
    assert "[WARN] unsupported" in output


@pytest.mark.parametrize(
    ("final_status", "changed", "expected"),
    [
        (HooksStatusLevel.CONFLICT, False, "finished with conflicts"),
        (HooksStatusLevel.HEALTHY, True, "completed"),
        (HooksStatusLevel.DEGRADED, False, "made no changes"),
    ],
)
def test_render_hook_operation_covers_all_summary_paths(
    capsys: pytest.CaptureFixture[str],
    final_status: HooksStatusLevel,
    changed: bool,
    expected: str,
) -> None:
    report = HookOperationReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        final_status=final_status,
        changed=changed,
        details=("detail",),
        results=(
            HookOperationResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                before_status=HookStatus.MISSING,
                after_status=HookStatus.HEALTHY,
                action=HookAction.CREATED,
                changed=True,
                managed=True,
            ),
            HookOperationResult(
                name=HookName.PRE_PUSH,
                path=Path("/tmp/demo/.git/hooks/pre-push"),
                before_status=HookStatus.UNSUPPORTED,
                after_status=HookStatus.UNSUPPORTED,
                action=HookAction.SKIPPED_UNSUPPORTED,
                changed=False,
                managed=False,
                details=("unsupported",),
            ),
        ),
    )

    render_hook_operation(report, repo_root=Path("/tmp/demo"), operation_name="install")
    output = normalize_path_str(capsys.readouterr().out)

    assert expected in output
    assert "action: created" in output
    assert "changed: yes" in output
    assert "pre-push: unsupported" in output
    assert "action: skipped_unsupported" in output
    assert "[WARN] detail" in output
    assert "[WARN] unsupported" in output


def test_render_init_result_shows_hooks_warning_and_runtime_warning(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_init_result(
        project_key="demo-app",
        binding_source="local",
        repo_root=Path("/workspace/demo-app"),
        contract_path=Path("/workspace/demo-app/.envctl.yaml"),
        vault_dir=Path("/tmp/vault/demo-app--prj_x"),
        vault_values_path=Path("/tmp/vault/demo-app--prj_x/values.env"),
        vault_state_path=Path("/tmp/vault/demo-app--prj_x/state.json"),
        init_result=InitResult(
            contract_created=False,
            hooks_installed=False,
            hooks_reason=HooksReason.PARTIAL_CONFLICT,
            runtime_warnings=("runtime warning",),
        ),
        display_name="demo-app",
    )
    output = normalize_path_str(capsys.readouterr().out)

    assert "hooks_installed: no" in output
    assert "hooks_reason: partial_conflict" in output
    assert "Managed hooks were partially installed, but conflicts remain." in output
    assert "runtime warning" in output


def test_render_inspect_value_includes_expansion_fields(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from envctl.cli.presenters.action_presenter import render_inspect_value

    render_inspect_value(
        profile="local",
        key="API_URL",
        source="vault",
        raw_value=None,
        value="${HOST}:${PORT}",
        masked=False,
        expansion_status="expanded",
        expansion_refs=("HOST", "PORT"),
        expansion_error="missing PORT",
        valid=False,
        detail=None,
    )

    output = capsys.readouterr().out
    assert "expansion_refs: HOST, PORT" in output
    assert "expansion_error: missing PORT" in output


@pytest.mark.parametrize(
    ("reason", "expected"),
    [
        (HooksReason.UNSUPPORTED_HOOKS_PATH, "effective hooks path is unsupported"),
        (HooksReason.FOREIGN_HOOK_PRESENT, "a foreign hook is already present"),
        (HooksReason.INSTALL_FAILED, "unexpected error"),
        (HooksReason.INSTALLED, "installed"),
    ],
)
def test_render_hooks_reason_messages(reason: HooksReason, expected: str) -> None:
    assert expected in _render_hooks_reason(reason)
