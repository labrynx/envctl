"""Vault artifact services."""

from __future__ import annotations

import os
import stat

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.adapters.editor import open_file
from envctl.domain.operations import EditResult, VaultCheckResult, VaultPruneResult, VaultShowResult
from envctl.domain.project import ConfirmFn, ProjectContext
from envctl.errors import ContractError, ExecutionError
from envctl.repository.contract_repository import load_contract
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions


def _load_vault_context() -> ProjectContext:
    """Resolve the current project context for vault operations."""
    _config, context = load_project_context()
    return context


def _ensure_vault_file(context: ProjectContext) -> bool:
    """Ensure the vault directory and values file exist."""
    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    created = not context.vault_values_path.exists()
    ensure_file(context.vault_values_path, "")
    ensure_private_file_permissions(context.vault_values_path)
    return created


def _has_private_file_permissions(path: str | os.PathLike[str]) -> bool:
    """Return whether the file permissions look private on POSIX systems."""
    try:
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except OSError:
        return False
    return mode == 0o600


def run_vault_edit() -> tuple[ProjectContext, EditResult]:
    """Open the local vault file in the user's editor."""
    context = _load_vault_context()
    created = _ensure_vault_file(context)

    open_file(str(context.vault_values_path))

    try:
        load_env_file(context.vault_values_path)
    except OSError as exc:
        raise ExecutionError(
            f"Unable to read edited vault file: {context.vault_values_path}"
        ) from exc

    ensure_private_file_permissions(context.vault_values_path)

    return context, EditResult(
        path=context.vault_values_path,
        created=created,
    )


def run_vault_check() -> tuple[ProjectContext, VaultCheckResult]:
    """Check the current vault artifact."""
    context = _load_vault_context()
    path = context.vault_values_path

    exists = path.exists()
    if not exists:
        return context, VaultCheckResult(
            path=path,
            exists=False,
            parseable=False,
            private_permissions=False,
            key_count=0,
        )

    try:
        values = load_env_file(path)
        parseable = True
        key_count = len(values)
    except OSError as exc:
        raise ExecutionError(f"Unable to read vault file: {path}") from exc

    return context, VaultCheckResult(
        path=path,
        exists=True,
        parseable=parseable,
        private_permissions=_has_private_file_permissions(path),
        key_count=key_count,
    )


def run_vault_path() -> tuple[ProjectContext, str]:
    """Return the current vault file path."""
    context = _load_vault_context()
    return context, str(context.vault_values_path)


def run_vault_show() -> tuple[ProjectContext, VaultShowResult]:
    """Show the current vault file contents."""
    context = _load_vault_context()
    path = context.vault_values_path

    if not path.exists():
        return context, VaultShowResult(
            path=path,
            exists=False,
            values={},
        )

    try:
        values = load_env_file(path)
    except OSError as exc:
        raise ExecutionError(f"Unable to read vault file: {path}") from exc

    return context, VaultShowResult(
        path=path,
        exists=True,
        values=values,
    )


def run_vault_prune(
    *,
    yes: bool = False,
    confirm: ConfirmFn | None = None,
) -> tuple[ProjectContext, VaultPruneResult]:
    """Remove keys from the vault that are not declared in the contract."""
    context = _load_vault_context()
    _ensure_vault_file(context)

    try:
        contract = load_contract(context.repo_contract_path)
    except ContractError as exc:
        raise ExecutionError(f"Cannot prune vault without a valid contract: {exc}") from exc

    values = load_env_file(context.vault_values_path)
    declared_keys = set(contract.variables)
    unknown_keys = tuple(sorted(key for key in values if key not in declared_keys))

    if not unknown_keys:
        return context, VaultPruneResult(
            path=context.vault_values_path,
            removed_keys=(),
            kept_keys=len(values),
        )

    if not yes and confirm is not None:
        approved = confirm(
            f"Remove {len(unknown_keys)} unknown key(s) from the local vault?",
            False,
        )
        if not approved:
            return context, VaultPruneResult(
                path=context.vault_values_path,
                removed_keys=(),
                kept_keys=len(values),
            )

    pruned_values = {key: values[key] for key in values if key in declared_keys}
    write_text_atomic(context.vault_values_path, dump_env(pruned_values))
    ensure_private_file_permissions(context.vault_values_path)

    return context, VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=unknown_keys,
        kept_keys=len(pruned_values),
    )


def run_edit() -> tuple[ProjectContext, EditResult]:
    """Backward-compatible wrapper for legacy edit command."""
    return run_vault_edit()
