from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

import envctl.services.hook_service as hook_service
from envctl.domain.hooks import (
    HookAction,
    HookName,
    HooksReason,
    HooksStatusLevel,
    HookStatus,
)
from envctl.errors import ExecutionError
from envctl.services.git_secret_guard_service import GitSecretGuardResult
from tests.support.contexts import make_project_context


def _set_hooks_env(
    monkeypatch: pytest.MonkeyPatch,
    repo_root: Path,
    *,
    hooks_path: Path,
    hooks_path_config: str | None = None,
) -> None:
    monkeypatch.setattr(hook_service, "resolve_hooks_path", lambda _repo_root: hooks_path)
    monkeypatch.setattr(
        hook_service,
        "get_local_git_config",
        lambda _repo_root, key: hooks_path_config if key == "core.hooksPath" else None,
    )


def test_render_managed_hook_uses_minimal_wrapper() -> None:
    spec = hook_service._MANAGED_HOOK_SPECS[0]

    rendered = hook_service.render_managed_hook(spec)

    assert rendered.startswith("#!/bin/sh\n")
    assert "# managed-by: envctl\n" in rendered
    assert f"# hook: {spec.name.value}\n" in rendered
    assert "command -v envctl >/dev/null 2>&1" in rendered
    assert f'envctl hook-run {spec.name.value} "$@"' in rendered
    assert "\r" not in rendered


def test_status_detects_healthy_hook_after_normalizing_crlf(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)

    rendered = hook_service.render_managed_hook(hook_service._MANAGED_HOOK_SPECS[0]).replace(
        "\n",
        "\r\n",
    )
    hook_path = hooks_path / HookName.PRE_COMMIT.value
    hook_path.write_text(rendered, encoding="utf-8", newline="")
    hook_path.chmod(0o755)

    report = hook_service.HookService(repo_root).get_status()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert pre_commit.status == HookStatus.HEALTHY


def test_status_reports_null_is_executable_on_windows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    monkeypatch.setattr(hook_service.HookRepository, "_is_windows", lambda self: True)

    hook_path = hooks_path / HookName.PRE_COMMIT.value
    hook_path.write_text(
        hook_service.render_managed_hook(hook_service._MANAGED_HOOK_SPECS[0]),
        encoding="utf-8",
    )

    report = hook_service.HookService(repo_root).get_status()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert pre_commit.is_executable is None


def test_install_creates_missing_hooks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)

    report = hook_service.HookService(repo_root).install()

    assert report.final_status == HooksStatusLevel.HEALTHY
    assert report.changed is True
    assert {result.action for result in report.results} == {HookAction.CREATED}
    assert (hooks_path / HookName.PRE_COMMIT.value).exists()
    assert (hooks_path / HookName.PRE_PUSH.value).exists()


def test_repair_creates_missing_hooks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)

    report = hook_service.HookService(repo_root).repair()

    assert report.final_status == HooksStatusLevel.HEALTHY
    assert all(result.after_status == HookStatus.HEALTHY for result in report.results)


def test_install_skips_foreign_without_force(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    (hooks_path / HookName.PRE_COMMIT.value).write_text(
        "#!/bin/sh\necho custom\n",
        encoding="utf-8",
    )

    report = hook_service.HookService(repo_root).install()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert report.final_status == HooksStatusLevel.CONFLICT
    assert pre_commit.action == HookAction.SKIPPED_FOREIGN
    assert pre_commit.after_status == HookStatus.FOREIGN


def test_install_force_overwrites_foreign(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    hook_path = hooks_path / HookName.PRE_COMMIT.value
    hook_path.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")

    report = hook_service.HookService(repo_root).install(force=True)
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert report.final_status == HooksStatusLevel.HEALTHY
    assert pre_commit.action == HookAction.REWRITTEN
    assert "envctl hook-run pre-commit" in hook_path.read_text(encoding="utf-8")


def test_status_marks_external_hooks_path_as_unsupported(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    external_hooks = tmp_path / "shared-hooks"
    _set_hooks_env(
        monkeypatch,
        repo_root,
        hooks_path=external_hooks,
        hooks_path_config="../shared-hooks",
    )

    report = hook_service.HookService(repo_root).get_status()

    assert report.overall_status == HooksStatusLevel.CONFLICT
    assert all(result.status == HookStatus.UNSUPPORTED for result in report.results)


def test_remove_cleans_supported_legacy_githooks_config(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    legacy_hooks_path = repo_root / ".githooks"
    legacy_hooks_path.mkdir(parents=True)
    config_store = {"core.hooksPath": ".githooks"}

    def fake_resolve_hooks_path(_repo_root: Path) -> Path:
        hooks_path_config = config_store.get("core.hooksPath")
        if hooks_path_config == ".githooks":
            return legacy_hooks_path
        return repo_root / ".git" / "hooks"

    monkeypatch.setattr(hook_service, "resolve_hooks_path", fake_resolve_hooks_path)
    monkeypatch.setattr(
        hook_service,
        "get_local_git_config",
        lambda _repo_root, key: config_store.get(key),
    )
    monkeypatch.setattr(
        hook_service,
        "unset_local_git_config",
        lambda _repo_root, key: config_store.pop(key, None),
    )

    (legacy_hooks_path / HookName.PRE_COMMIT.value).write_text(
        hook_service._LEGACY_PRE_COMMIT,
        encoding="utf-8",
    )
    (legacy_hooks_path / HookName.PRE_PUSH.value).write_text(
        hook_service._LEGACY_PRE_PUSH,
        encoding="utf-8",
    )

    report = hook_service.HookService(repo_root).remove()

    assert report.final_status == HooksStatusLevel.HEALTHY
    assert config_store.get("core.hooksPath") is None
    assert any("core.hooksPath=.githooks" in detail for detail in report.details)


def test_derive_init_hooks_outcome_maps_conflict_without_changes_to_foreign_reason() -> None:
    report = hook_service.HookOperationReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        final_status=HooksStatusLevel.CONFLICT,
        changed=False,
        results=(
            hook_service.HookOperationResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                before_status=HookStatus.FOREIGN,
                after_status=HookStatus.FOREIGN,
                action=HookAction.SKIPPED_FOREIGN,
                changed=False,
                managed=False,
            ),
        ),
    )

    installed, reason = hook_service.derive_init_hooks_outcome(report)

    assert installed is False
    assert reason == HooksReason.FOREIGN_HOOK_PRESENT


def test_hook_execution_service_dispatches_guard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        repo_contract_path=repo_root / ".envctl.yaml",
        repo_env_path=repo_root / ".env.local",
        vault_project_dir=tmp_path / "vault" / "projects" / "demo--prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        hook_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hook_service,
        "run_git_secret_guard",
        lambda _context: GitSecretGuardResult(scanned_paths=(), findings=()),
    )

    result = hook_service.HookExecutionService().run_guarded_hook(HookName.PRE_COMMIT, ())

    assert result.exit_code == 0
    assert result.guard_result.ok is True


def test_hook_execution_service_rejects_unsupported_hooks() -> None:
    with pytest.raises(ExecutionError, match="Unsupported hook"):
        hook_service.HookExecutionService().run_guarded_hook(cast(HookName, "post-merge"), ())


def test_status_detects_drifted_hook(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    hook_path = hooks_path / HookName.PRE_COMMIT.value
    hook_path.write_text(
        hook_service.render_managed_hook(hook_service._MANAGED_HOOK_SPECS[0]).replace(
            "exit $?\n",
            "echo drift\nexit $?\n",
        ),
        encoding="utf-8",
    )
    hook_path.chmod(0o755)

    report = hook_service.HookService(repo_root).get_status()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert pre_commit.status == HookStatus.DRIFTED
    assert pre_commit.managed is True


@pytest.mark.skipif(__import__("os").name == "nt", reason="POSIX executable bits required")
def test_repair_fixes_not_executable_hook(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    hook_path = hooks_path / HookName.PRE_COMMIT.value
    hook_path.write_text(
        hook_service.render_managed_hook(hook_service._MANAGED_HOOK_SPECS[0]),
        encoding="utf-8",
    )
    hook_path.chmod(0o644)

    report = hook_service.HookService(repo_root).repair()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert pre_commit.action == HookAction.FIXED_PERMISSIONS
    assert pre_commit.after_status == HookStatus.HEALTHY


def test_install_noops_when_hooks_are_already_healthy(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)

    for spec in hook_service._MANAGED_HOOK_SPECS:
        hook_path = hooks_path / spec.name.value
        hook_path.write_text(hook_service.render_managed_hook(spec), encoding="utf-8")
        hook_path.chmod(0o755)

    report = hook_service.HookService(repo_root).install()

    assert report.changed is False
    assert {result.action for result in report.results} == {HookAction.NOOP}


def test_remove_keeps_foreign_hook_and_reports_inconsistent_path_warning(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    hooks_path = repo_root / ".git" / "hooks"
    hooks_path.mkdir(parents=True)
    _set_hooks_env(monkeypatch, repo_root, hooks_path=hooks_path)
    (hooks_path / HookName.PRE_COMMIT.value).write_text(
        "#!/bin/sh\necho foreign\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        hook_service.HookService,
        "_has_inconsistent_hooks_path",
        lambda self: True,
    )

    report = hook_service.HookService(repo_root).remove()
    pre_commit = next(result for result in report.results if result.name == HookName.PRE_COMMIT)

    assert report.final_status == HooksStatusLevel.CONFLICT
    assert pre_commit.action == HookAction.SKIPPED_FOREIGN
    assert any("core.hooksPath still points" in detail for detail in report.details)


@pytest.mark.parametrize(
    ("report", "expected"),
    [
        (
            hook_service.HookOperationReport(
                hooks_path=Path("/tmp/demo/.git/hooks"),
                final_status=HooksStatusLevel.HEALTHY,
                changed=True,
                results=(),
            ),
            (True, HooksReason.INSTALLED),
        ),
        (
            hook_service.HookOperationReport(
                hooks_path=Path("/tmp/demo/.git/hooks"),
                final_status=HooksStatusLevel.HEALTHY,
                changed=False,
                results=(),
            ),
            (True, HooksReason.ALREADY_HEALTHY),
        ),
        (
            hook_service.HookOperationReport(
                hooks_path=Path("/tmp/demo/.git/hooks"),
                final_status=HooksStatusLevel.CONFLICT,
                changed=False,
                results=(
                    hook_service.HookOperationResult(
                        name=HookName.PRE_COMMIT,
                        path=Path("/tmp/demo/.git/hooks/pre-commit"),
                        before_status=HookStatus.UNSUPPORTED,
                        after_status=HookStatus.UNSUPPORTED,
                        action=HookAction.SKIPPED_UNSUPPORTED,
                        changed=False,
                        managed=False,
                    ),
                ),
            ),
            (False, HooksReason.UNSUPPORTED_HOOKS_PATH),
        ),
        (
            hook_service.HookOperationReport(
                hooks_path=Path("/tmp/demo/.git/hooks"),
                final_status=HooksStatusLevel.CONFLICT,
                changed=True,
                results=(),
            ),
            (False, HooksReason.PARTIAL_CONFLICT),
        ),
        (
            hook_service.HookOperationReport(
                hooks_path=Path("/tmp/demo/.git/hooks"),
                final_status=HooksStatusLevel.DEGRADED,
                changed=False,
                results=(
                    hook_service.HookOperationResult(
                        name=HookName.PRE_COMMIT,
                        path=Path("/tmp/demo/.git/hooks/pre-commit"),
                        before_status=HookStatus.MISSING,
                        after_status=HookStatus.MISSING,
                        action=HookAction.NOOP,
                        changed=False,
                        managed=False,
                    ),
                ),
            ),
            (False, HooksReason.INSTALL_FAILED),
        ),
    ],
)
def test_derive_init_hooks_outcome_maps_all_remaining_paths(report: Any, expected: Any) -> None:
    assert hook_service.derive_init_hooks_outcome(report) == expected


def test_hook_execution_service_run_returns_non_zero_for_failed_guard(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        repo_contract_path=repo_root / ".envctl.yaml",
        repo_env_path=repo_root / ".env.local",
        vault_project_dir=tmp_path / "vault" / "projects" / "demo--prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        hook_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        hook_service,
        "run_git_secret_guard",
        lambda _context: GitSecretGuardResult(
            scanned_paths=(Path("a"),),
            findings=(SimpleNamespace(),),
        ),
    )

    result = hook_service.HookExecutionService().run(HookName.PRE_PUSH, ())

    assert result == 1


def test_remove_skips_unsupported_hooks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    external_hooks = tmp_path / "shared-hooks"
    _set_hooks_env(
        monkeypatch,
        repo_root,
        hooks_path=external_hooks,
        hooks_path_config="../shared-hooks",
    )

    report = hook_service.HookService(repo_root).remove()

    assert all(result.action == HookAction.SKIPPED_UNSUPPORTED for result in report.results)


def test_install_skips_unsupported_hooks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    external_hooks = tmp_path / "shared-hooks"
    _set_hooks_env(
        monkeypatch,
        repo_root,
        hooks_path=external_hooks,
        hooks_path_config="../shared-hooks",
    )

    report = hook_service.HookService(repo_root).install()

    assert all(result.action == HookAction.SKIPPED_UNSUPPORTED for result in report.results)


def test_apply_single_operation_rejects_unknown_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    service = hook_service.HookService(repo_root)
    env = hook_service._HooksEnvironment(
        repo_root=repo_root,
        hooks_path=repo_root / ".git" / "hooks",
        hooks_path_config=None,
        supported=True,
        details=(),
    )
    fake_status = cast(HookStatus, type("FakeStatus", (), {"value": "weird"})())
    before = hook_service.HookInspectionResult(
        name=HookName.PRE_COMMIT,
        path=env.hooks_path / "pre-commit",
        status=fake_status,
        managed=False,
        is_executable=None,
    )

    with pytest.raises(ExecutionError, match="Unsupported hook state for install: weird"):
        service._apply_single_operation(
            operation="install",
            spec=hook_service._MANAGED_HOOK_SPECS[0],
            env=env,
            before=before,
            force=False,
        )


def test_record_inspection_emits_event_when_observability_is_active(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    service = hook_service.HookService(tmp_path / "repo")
    captured: dict[str, Any] = {}
    result = hook_service.HookInspectionResult(
        name=HookName.PRE_COMMIT,
        path=Path("/tmp/demo/.git/hooks/pre-commit"),
        status=HookStatus.HEALTHY,
        managed=True,
        is_executable=True,
    )

    monkeypatch.setattr(hook_service, "get_active_observability_context", lambda: object())
    monkeypatch.setattr(
        hook_service,
        "record_event",
        lambda context, **kwargs: captured.update(kwargs),
    )

    service._record_inspection(result)

    assert captured["event"] == "hook.inspect.finish"
    assert captured["fields"]["managed"] is True


def test_should_cleanup_legacy_hooks_path_rejects_external_or_foreign_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    external = tmp_path / "external"
    external.mkdir()
    service = hook_service.HookService(repo_root)

    unsupported_env = hook_service._HooksEnvironment(
        repo_root=repo_root,
        hooks_path=external,
        hooks_path_config=".githooks",
        supported=False,
        details=(),
    )
    assert service._should_cleanup_legacy_hooks_path(unsupported_env, {}) is False

    legacy_path = repo_root / ".githooks"
    legacy_path.mkdir()
    (legacy_path / HookName.PRE_COMMIT.value).write_text(
        "#!/bin/sh\necho foreign\n",
        encoding="utf-8",
    )
    managed_env = hook_service._HooksEnvironment(
        repo_root=repo_root,
        hooks_path=legacy_path,
        hooks_path_config=".githooks",
        supported=True,
        details=(),
    )
    assert service._should_cleanup_legacy_hooks_path(managed_env, {}) is False


def test_has_inconsistent_hooks_path_detects_missing_and_empty_dirs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    service = hook_service.HookService(repo_root)

    monkeypatch.setattr(hook_service, "get_local_git_config", lambda _repo_root, key: ".hooks")
    monkeypatch.setattr(hook_service, "resolve_hooks_path", lambda _repo_root: repo_root / ".hooks")
    assert service._has_inconsistent_hooks_path() is True

    empty_hooks = repo_root / ".hooks"
    empty_hooks.mkdir()
    assert service._has_inconsistent_hooks_path() is True


def test_classify_operation_status_covers_degraded_paths() -> None:
    assert (
        hook_service._classify_operation_status("remove", [HookStatus.HEALTHY])
        == HooksStatusLevel.DEGRADED
    )
    assert (
        hook_service._classify_operation_status("install", [HookStatus.MISSING])
        == HooksStatusLevel.DEGRADED
    )
