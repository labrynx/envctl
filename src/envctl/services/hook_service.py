"""Managed Git hooks services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from envctl.adapters.git import (
    get_local_git_config,
    resolve_hooks_path,
    unset_local_git_config,
)
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
    ManagedHookSpec,
)
from envctl.errors import ExecutionError
from envctl.observability import get_active_observability_context
from envctl.observability.recorder import record_event
from envctl.observability.timing import observe_span
from envctl.repository.hook_repository import HookRepository
from envctl.services.context_service import load_project_context
from envctl.services.git_secret_guard_service import GitSecretGuardResult, run_git_secret_guard

_HOOKS_PATH_CONFIG = "core.hooksPath"
_MANAGED_MARKER = "# managed-by: envctl"
_LEGACY_HOOKS_DIRNAME = ".githooks"
_LEGACY_PRE_COMMIT = (
    "#!/bin/sh\n"
    "set -eu\n\n"
    "# managed-by: envctl\n"
    "if command -v uv >/dev/null 2>&1; then\n"
    "  uv run envctl guard secrets\n"
    "else\n"
    "  envctl guard secrets\n"
    "fi\n\n"
    "# your additional checks here\n"
)
_LEGACY_PRE_PUSH = '#!/bin/sh\nHOOK_NAME=pre-push exec .githooks/_shared_hook.sh "$@"\n'

_MANAGED_HOOK_SPECS = (
    ManagedHookSpec(
        name=HookName.PRE_COMMIT,
        version=1,
        command=("envctl", "hook-run", HookName.PRE_COMMIT.value),
    ),
    ManagedHookSpec(
        name=HookName.PRE_PUSH,
        version=1,
        command=("envctl", "hook-run", HookName.PRE_PUSH.value),
    ),
)


@dataclass(frozen=True)
class HookExecutionResult:
    """Result of executing one managed hook policy."""

    hook_name: HookName
    exit_code: int
    guard_result: GitSecretGuardResult


@dataclass(frozen=True)
class _HooksEnvironment:
    repo_root: Path
    hooks_path: Path
    hooks_path_config: str | None
    supported: bool
    details: tuple[str, ...]


def render_managed_hook(spec: ManagedHookSpec) -> str:
    """Render one canonical envctl-managed hook wrapper."""
    command = " ".join(spec.command)
    return (
        "#!/bin/sh\n"
        f"{_MANAGED_MARKER}\n"
        f"# hook: {spec.name.value}\n"
        f"# version: {spec.version}\n\n"
        "if ! command -v envctl >/dev/null 2>&1; then\n"
        '  echo >&2 "envctl is not available in PATH in this environment."\n'
        "  exit 1\n"
        "fi\n\n"
        f'{command} "$@"\n'
        "exit $?\n"
    )


def derive_init_hooks_outcome(report: HookOperationReport) -> tuple[bool, HooksReason]:
    """Map one install report into the stable init outcome contract."""
    if report.final_status == HooksStatusLevel.HEALTHY:
        if report.changed:
            return True, HooksReason.INSTALLED
        return True, HooksReason.ALREADY_HEALTHY

    statuses = {result.before_status for result in report.results}
    if HookStatus.UNSUPPORTED in statuses:
        return False, HooksReason.UNSUPPORTED_HOOKS_PATH
    if report.changed:
        return False, HooksReason.PARTIAL_CONFLICT
    if HookStatus.FOREIGN in statuses:
        return False, HooksReason.FOREIGN_HOOK_PRESENT
    return False, HooksReason.INSTALL_FAILED


class HookService:
    """Manage envctl-owned Git hooks for one repository."""

    def __init__(
        self,
        repo_root: Path,
        *,
        hook_repository: HookRepository | None = None,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self._hook_repository = hook_repository or HookRepository()

    def get_status(self) -> HooksStatusReport:
        """Inspect the supported managed hooks."""
        with observe_span(
            "hooks.status",
            module=__name__,
            operation="get_status",
            fields={},
        ) as span_fields:
            env = self._resolve_environment()
            results = tuple(self._inspect_all(env))
            overall_status = _classify_status_level(result.status for result in results)
            span_fields["hooks_path"] = str(env.hooks_path)
            span_fields["overall_status"] = overall_status.value
            return HooksStatusReport(
                hooks_path=env.hooks_path,
                overall_status=overall_status,
                results=results,
                details=env.details,
            )

    def install(self, *, force: bool = False) -> HookOperationReport:
        """Install or rewrite managed hooks to the canonical state."""
        return self._apply_operation("install", force=force)

    def repair(self, *, force: bool = False) -> HookOperationReport:
        """Repair managed hooks to the canonical state."""
        return self._apply_operation("repair", force=force)

    def remove(self) -> HookOperationReport:
        """Remove managed hooks and clean the supported legacy layout when safe."""
        with observe_span(
            "hooks.remove",
            module=__name__,
            operation="remove",
            fields={},
        ) as span_fields:
            before_report = self.get_status()
            before_results = {result.name: result for result in before_report.results}
            env = self._resolve_environment()
            operation_results: list[HookOperationResult] = []

            for spec in _MANAGED_HOOK_SPECS:
                path = env.hooks_path / spec.name.value
                before = before_results[spec.name]
                if before.status == HookStatus.UNSUPPORTED:
                    operation_results.append(
                        HookOperationResult(
                            name=spec.name,
                            path=path,
                            before_status=before.status,
                            after_status=before.status,
                            action=HookAction.SKIPPED_UNSUPPORTED,
                            changed=False,
                            managed=before.managed,
                            details=before.details,
                        )
                    )
                    continue

                if before.status in {
                    HookStatus.HEALTHY,
                    HookStatus.DRIFTED,
                    HookStatus.NOT_EXECUTABLE,
                }:
                    self._hook_repository.remove(path)
                    after_status = HookStatus.MISSING
                    action = HookAction.REMOVED
                    changed = True
                elif before.status == HookStatus.FOREIGN:
                    after_status = HookStatus.FOREIGN
                    action = HookAction.SKIPPED_FOREIGN
                    changed = False
                else:
                    after_status = HookStatus.MISSING
                    action = HookAction.NOOP
                    changed = False

                operation_results.append(
                    HookOperationResult(
                        name=spec.name,
                        path=path,
                        before_status=before.status,
                        after_status=after_status,
                        action=action,
                        changed=changed,
                        managed=before.managed,
                        details=before.details,
                    )
                )

            details: list[str] = []
            changed = any(result.changed for result in operation_results)
            if self._should_cleanup_legacy_hooks_path(env, before_results):
                unset_local_git_config(self.repo_root, _HOOKS_PATH_CONFIG)
                changed = True
                details.append("Removed legacy core.hooksPath=.githooks managed by envctl.")

            final_status_report = self.get_status()
            if self._has_inconsistent_hooks_path():
                details.append(
                    "core.hooksPath still points to an empty, missing, or inconsistent "
                    "hooks directory."
                )

            final_status = _classify_operation_status(
                "remove",
                (result.status for result in final_status_report.results),
            )
            span_fields["hooks_path"] = str(final_status_report.hooks_path)
            span_fields["final_status"] = final_status.value
            span_fields["changed"] = changed
            return HookOperationReport(
                hooks_path=final_status_report.hooks_path,
                final_status=final_status,
                changed=changed,
                results=tuple(
                    self._refresh_operation_result(
                        result,
                        final_status_report.results,
                    )
                    for result in operation_results
                ),
                details=tuple(details),
            )

    def _apply_operation(self, operation: str, *, force: bool) -> HookOperationReport:
        event_prefix = f"hooks.{operation}"
        with observe_span(
            event_prefix,
            module=__name__,
            operation=operation,
            fields={"force": force},
        ) as span_fields:
            before_report = self.get_status()
            before_results = {result.name: result for result in before_report.results}
            env = self._resolve_environment()

            if env.supported:
                env.hooks_path.mkdir(parents=True, exist_ok=True)

            operation_results: list[HookOperationResult] = []
            for spec in _MANAGED_HOOK_SPECS:
                before = before_results[spec.name]
                operation_results.append(
                    self._apply_single_operation(
                        operation=operation,
                        spec=spec,
                        env=env,
                        before=before,
                        force=force,
                    )
                )

            after_report = self.get_status()
            final_status = _classify_operation_status(
                operation,
                (result.status for result in after_report.results),
            )
            changed = any(result.changed for result in operation_results)
            span_fields["hooks_path"] = str(after_report.hooks_path)
            span_fields["final_status"] = final_status.value
            span_fields["changed"] = changed
            span_fields["force"] = force
            return HookOperationReport(
                hooks_path=after_report.hooks_path,
                final_status=final_status,
                changed=changed,
                results=tuple(
                    self._refresh_operation_result(result, after_report.results)
                    for result in operation_results
                ),
                details=after_report.details,
            )

    def _apply_single_operation(
        self,
        *,
        operation: str,
        spec: ManagedHookSpec,
        env: _HooksEnvironment,
        before: HookInspectionResult,
        force: bool,
    ) -> HookOperationResult:
        path = env.hooks_path / spec.name.value
        rendered = render_managed_hook(spec)

        if before.status == HookStatus.UNSUPPORTED:
            return HookOperationResult(
                name=spec.name,
                path=path,
                before_status=before.status,
                after_status=before.status,
                action=HookAction.SKIPPED_UNSUPPORTED,
                changed=False,
                managed=before.managed,
                details=before.details,
            )

        if before.status == HookStatus.HEALTHY:
            return HookOperationResult(
                name=spec.name,
                path=path,
                before_status=before.status,
                after_status=before.status,
                action=HookAction.NOOP,
                changed=False,
                managed=True,
                details=before.details,
            )

        if before.status == HookStatus.FOREIGN and not force:
            return HookOperationResult(
                name=spec.name,
                path=path,
                before_status=before.status,
                after_status=before.status,
                action=HookAction.SKIPPED_FOREIGN,
                changed=False,
                managed=False,
                details=before.details,
            )

        if before.status in {HookStatus.MISSING, HookStatus.DRIFTED, HookStatus.FOREIGN}:
            self._hook_repository.write(path, rendered)
            self._hook_repository.ensure_executable(path)
            action = (
                HookAction.CREATED if before.status == HookStatus.MISSING else HookAction.REWRITTEN
            )
            return HookOperationResult(
                name=spec.name,
                path=path,
                before_status=before.status,
                after_status=HookStatus.HEALTHY,
                action=action,
                changed=True,
                managed=True,
                details=before.details,
            )

        if before.status == HookStatus.NOT_EXECUTABLE:
            self._hook_repository.ensure_executable(path)
            return HookOperationResult(
                name=spec.name,
                path=path,
                before_status=before.status,
                after_status=HookStatus.HEALTHY,
                action=HookAction.FIXED_PERMISSIONS,
                changed=True,
                managed=True,
                details=before.details,
            )

        raise ExecutionError(f"Unsupported hook state for {operation}: {before.status.value}")

    def _resolve_environment(self) -> _HooksEnvironment:
        hooks_path = resolve_hooks_path(self.repo_root)
        hooks_path_config = get_local_git_config(self.repo_root, _HOOKS_PATH_CONFIG)
        supported = _path_is_within(self.repo_root, hooks_path)
        details: tuple[str, ...] = ()
        if not supported:
            details = (
                "The effective hooks path is outside the repository perimeter and is unsupported.",
            )
        return _HooksEnvironment(
            repo_root=self.repo_root,
            hooks_path=hooks_path,
            hooks_path_config=hooks_path_config,
            supported=supported,
            details=details,
        )

    def _inspect_all(self, env: _HooksEnvironment) -> list[HookInspectionResult]:
        results: list[HookInspectionResult] = []
        for spec in _MANAGED_HOOK_SPECS:
            result = self._inspect_one(spec, env)
            results.append(result)
            self._record_inspection(result)
        return results

    def _inspect_one(self, spec: ManagedHookSpec, env: _HooksEnvironment) -> HookInspectionResult:
        path = env.hooks_path / spec.name.value
        if not env.supported:
            return HookInspectionResult(
                name=spec.name,
                path=path,
                status=HookStatus.UNSUPPORTED,
                managed=False,
                is_executable=None,
                details=env.details,
            )

        if not self._hook_repository.exists(path):
            return HookInspectionResult(
                name=spec.name,
                path=path,
                status=HookStatus.MISSING,
                managed=False,
                is_executable=None,
            )

        content = self._hook_repository.read(path)
        managed = _MANAGED_MARKER in content
        rendered = render_managed_hook(spec)
        is_executable = self._hook_repository.is_executable(path)

        if managed and content == rendered:
            if is_executable is False:
                return HookInspectionResult(
                    name=spec.name,
                    path=path,
                    status=HookStatus.NOT_EXECUTABLE,
                    managed=True,
                    is_executable=is_executable,
                )
            return HookInspectionResult(
                name=spec.name,
                path=path,
                status=HookStatus.HEALTHY,
                managed=True,
                is_executable=is_executable,
            )

        if managed:
            return HookInspectionResult(
                name=spec.name,
                path=path,
                status=HookStatus.DRIFTED,
                managed=True,
                is_executable=is_executable,
            )

        return HookInspectionResult(
            name=spec.name,
            path=path,
            status=HookStatus.FOREIGN,
            managed=False,
            is_executable=is_executable,
        )

    def _record_inspection(self, result: HookInspectionResult) -> None:
        context = get_active_observability_context()
        if context is None:
            return
        record_event(
            context,
            event="hook.inspect.finish",
            status="finish",
            module=__name__,
            operation="inspect",
            fields={
                "hook_name": result.name.value,
                "status": result.status.value,
                "path": str(result.path),
                "managed": result.managed,
            },
        )

    def _refresh_operation_result(
        self,
        result: HookOperationResult,
        inspection_results: tuple[HookInspectionResult, ...],
    ) -> HookOperationResult:
        after_by_name = {item.name: item for item in inspection_results}
        after = after_by_name[result.name]
        return HookOperationResult(
            name=result.name,
            path=after.path,
            before_status=result.before_status,
            after_status=after.status,
            action=result.action,
            changed=result.changed,
            managed=after.managed,
            details=after.details,
        )

    def _should_cleanup_legacy_hooks_path(
        self,
        env: _HooksEnvironment,
        before_results: dict[HookName, HookInspectionResult],
    ) -> bool:
        if env.hooks_path_config != _LEGACY_HOOKS_DIRNAME:
            return False
        if not _path_is_within(self.repo_root, env.hooks_path):
            return False

        legacy_expected = {
            HookName.PRE_COMMIT: _LEGACY_PRE_COMMIT,
            HookName.PRE_PUSH: _LEGACY_PRE_PUSH,
        }
        for hook_name, expected in legacy_expected.items():
            path = env.hooks_path / hook_name.value
            if not path.exists():
                continue
            content = self._hook_repository.read(path)
            if _MANAGED_MARKER not in content and content != expected:
                return False
        return True

    def _has_inconsistent_hooks_path(self) -> bool:
        hooks_path_config = get_local_git_config(self.repo_root, _HOOKS_PATH_CONFIG)
        if hooks_path_config is None:
            return False
        hooks_path = resolve_hooks_path(self.repo_root)
        if not hooks_path.exists() or not hooks_path.is_dir():
            return True
        return not any(hooks_path.iterdir())


class HookExecutionService:
    """Dispatch supported managed hook policies."""

    def run(self, hook_name: HookName, argv: list[str] | tuple[str, ...]) -> int:
        """Execute one supported hook and return its exit code."""
        return self.run_guarded_hook(hook_name, argv).exit_code

    def run_guarded_hook(
        self,
        hook_name: HookName,
        argv: list[str] | tuple[str, ...],
    ) -> HookExecutionResult:
        """Execute one supported hook policy and return the structured result."""
        del argv
        hook_name_value = hook_name.value if isinstance(hook_name, HookName) else str(hook_name)
        with observe_span(
            "hook.run",
            module=__name__,
            operation="run_guarded_hook",
            fields={"hook_name": hook_name_value},
        ) as span_fields:
            if hook_name not in {HookName.PRE_COMMIT, HookName.PRE_PUSH}:
                raise ExecutionError(f"Unsupported hook: {hook_name_value}")

            _config, context = load_project_context()
            guard_result = run_git_secret_guard(context)
            exit_code = 0 if guard_result.ok else 1
            span_fields["exit_code"] = exit_code
            span_fields["hook_name"] = hook_name_value
            return HookExecutionResult(
                hook_name=HookName(hook_name),
                exit_code=exit_code,
                guard_result=guard_result,
            )


def _path_is_within(repo_root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def _classify_status_level(statuses: Any) -> HooksStatusLevel:
    status_set = set(statuses)
    if HookStatus.UNSUPPORTED in status_set or HookStatus.FOREIGN in status_set:
        return HooksStatusLevel.CONFLICT
    if status_set == {HookStatus.HEALTHY}:
        return HooksStatusLevel.HEALTHY
    return HooksStatusLevel.DEGRADED


def _classify_operation_status(
    operation: str,
    statuses: Any,
) -> HooksStatusLevel:
    status_set = set(statuses)
    if HookStatus.UNSUPPORTED in status_set or HookStatus.FOREIGN in status_set:
        return HooksStatusLevel.CONFLICT
    if operation == "remove":
        if status_set <= {HookStatus.MISSING}:
            return HooksStatusLevel.HEALTHY
        return HooksStatusLevel.DEGRADED
    if status_set == {HookStatus.HEALTHY}:
        return HooksStatusLevel.HEALTHY
    return HooksStatusLevel.DEGRADED
