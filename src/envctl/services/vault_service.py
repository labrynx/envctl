"""Vault-oriented services."""

from __future__ import annotations

from pathlib import Path

import envctl.adapters.editor as editor_adapter
from envctl.domain.operations import (
    VaultCheckResult,
    VaultEditResult,
    VaultPruneResult,
    VaultShowResult,
)
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.repository.contract_repository import load_contract_optional
from envctl.repository.profile_repository import (
    load_profile_values,
    require_persisted_profile,
    write_profile_values,
)
from envctl.repository.profile_repository import (
    resolve_profile_path as resolve_profile_vault_path,
)
from envctl.services.context_service import load_project_context
from envctl.utils.filesystem import is_world_writable


def _resolve_selected_profile(
    context: ProjectContext,
    active_profile: str | None,
) -> tuple[str, Path]:
    """Resolve the active profile name and file path."""
    if active_profile in (None, "local"):
        return resolve_profile_vault_path(context, active_profile)

    return require_persisted_profile(context, active_profile)


def run_vault_check(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultCheckResult]:
    """Check the current physical vault file for the active profile."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    if not profile_path.exists():
        result = VaultCheckResult(
            path=profile_path,
            exists=False,
            parseable=False,
            private_permissions=False,
            key_count=0,
        )
        return context, resolved_profile, result

    try:
        _resolved_profile, _path, values = load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
        )
        parseable = True
        key_count = len(values)
    except (OSError, ValueError):
        parseable = False
        key_count = 0

    result = VaultCheckResult(
        path=profile_path,
        exists=True,
        parseable=parseable,
        private_permissions=not is_world_writable(profile_path),
        key_count=key_count,
    )
    return context, resolved_profile, result


def run_vault_path(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path]:
    """Return the current physical vault path for the active profile."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)
    return context, resolved_profile, profile_path


def run_vault_show(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultShowResult]:
    """Return the current physical vault content for the active profile."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    exists = profile_path.exists()
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )

    return (
        context,
        resolved_profile,
        VaultShowResult(
            path=profile_path,
            exists=exists,
            values=values,
        ),
    )


def run_vault_edit(
    active_profile: str | None = None,
) -> tuple[ProjectContext, VaultEditResult]:
    """Open the current physical vault file for the selected profile."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    created = False
    if not profile_path.exists():
        write_profile_values(context, resolved_profile, {})
        created = True

    editor_adapter.open_file(str(profile_path))

    try:
        load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
        )
    except Exception as exc:  # pragma: no cover
        raise ExecutionError(f"Edited vault file is no longer parseable: {profile_path}") from exc

    return context, VaultEditResult(
        path=profile_path,
        profile=resolved_profile,
        created=created,
    )


def get_unknown_vault_keys(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, tuple[str, ...]]:
    """Return unknown keys stored in the active profile vault."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )

    if contract is None:
        return context, resolved_profile, profile_path, tuple(sorted(values))

    unknown_keys = tuple(sorted(set(values) - set(contract.variables)))
    return context, resolved_profile, profile_path, unknown_keys


def run_vault_prune(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, VaultPruneResult]:
    """Remove unknown keys from the active profile vault."""
    _config, context = load_project_context()
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
    )

    if contract is None:
        removed_keys = tuple(sorted(values))
        kept: dict[str, str] = {}
    else:
        removed_keys = tuple(sorted(set(values) - set(contract.variables)))
        kept = {key: value for key, value in values.items() if key in contract.variables}

    write_profile_values(
        context,
        resolved_profile,
        kept,
        require_existing_explicit=True,
    )

    return (
        context,
        resolved_profile,
        profile_path,
        VaultPruneResult(
            path=profile_path,
            removed_keys=removed_keys,
            kept_keys=len(kept),
        ),
    )
