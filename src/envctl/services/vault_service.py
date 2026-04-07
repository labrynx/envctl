"""Vault-oriented services."""

from __future__ import annotations

import os
import tempfile
from contextlib import suppress
from pathlib import Path

import envctl.adapters.editor as editor_adapter
from envctl.constants import DEFAULT_KEY_FILENAME, DEFAULT_STATE_FILENAME, DEFAULT_VALUES_FILENAME
from envctl.domain.app_config import AppConfig
from envctl.domain.operations import (
    VaultAuditFileResult,
    VaultAuditProjectResult,
    VaultCheckResult,
    VaultDecryptResult,
    VaultEditResult,
    VaultEncryptResult,
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
from envctl.repository.state_repository import read_state
from envctl.services.context_service import load_configured_vault_crypto, load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import is_world_writable
from envctl.utils.project_paths import build_profiles_dir
from envctl.vault_crypto import VaultCrypto, VaultFileState


def _resolve_selected_profile(
    context: ProjectContext,
    active_profile: str | None,
) -> tuple[str, Path]:
    """Resolve the active profile name and file path."""
    if active_profile in (None, "local"):
        return resolve_profile_vault_path(context, active_profile)

    return require_persisted_profile(context, active_profile)


def _collect_vault_profile_paths(context: ProjectContext) -> list[Path]:
    """Return all existing vault profile file paths for the current project."""
    paths: list[Path] = []
    if context.vault_values_path.exists():
        paths.append(context.vault_values_path)

    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if profiles_dir.exists():
        paths.extend(sorted(profiles_dir.glob("*.env")))

    return paths


def _classify_vault_file(
    context: ProjectContext,
    profile_path: Path,
) -> tuple[VaultFileState, str]:
    """Return the inspection state for one vault path."""
    if not profile_path.exists():
        return "missing", "Vault file does not exist."

    raw = profile_path.read_bytes()
    if context.vault_crypto is not None:
        inspection = context.vault_crypto.inspect_bytes(raw)
        return inspection.state, inspection.detail

    if VaultCrypto.looks_encrypted(raw):
        return (
            "encrypted",
            "Vault file is encrypted, but encryption is disabled in config.",
        )

    return "plaintext", "Vault file is plaintext."


def _resolve_sensitive_keys_for_values(
    context: ProjectContext,
    values: dict[str, str],
) -> dict[str, bool]:
    """Resolve whether each vault key should be treated as sensitive."""
    contract = load_contract_optional(context.repo_contract_path)
    contract_variables = contract.variables if contract is not None else {}

    sensitive_keys: dict[str, bool] = {}
    for key in values:
        spec = contract_variables.get(key)
        sensitive_keys[key] = True if spec is None else spec.sensitive

    return sensitive_keys


def _run_vault_edit_encrypted(profile_path: Path, *, context: ProjectContext) -> None:
    """Open a vault file through a decrypted temporary file and re-encrypt it."""
    crypto = context.vault_crypto
    if crypto is None:  # pragma: no cover
        raise ExecutionError("Vault edit requested encrypted mode without an active key.")

    content = crypto.read_file(profile_path, allow_plaintext=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=".edit-",
        suffix=".tmp",
        dir=str(profile_path.parent),
    )
    tmp_path = Path(tmp_name)

    try:
        with suppress(AttributeError):
            os.fchmod(fd, 0o600)

        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)

        editor_adapter.open_file(str(tmp_path))

        edited_content = tmp_path.read_text(encoding="utf-8")
        crypto.write_encrypted_file(profile_path, edited_content)
    finally:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)


def _require_no_plaintext_in_strict_mode(
    context: ProjectContext,
    *,
    strict: bool,
) -> None:
    """Reject any plaintext vault files when strict mode is enabled."""
    if not strict:
        return

    for path in _collect_vault_profile_paths(context):
        state, detail = _classify_vault_file(context, path)
        if state == "plaintext":
            raise ExecutionError(
                f"Plaintext vault file detected in strict encryption mode: {path}. {detail}"
            )


def _iter_project_dirs(projects_dir: Path) -> tuple[Path, ...]:
    """Return every persisted project vault directory."""
    if not projects_dir.exists():
        return ()

    return tuple(sorted(path for path in projects_dir.iterdir() if path.is_dir()))


def _project_metadata_from_dir(project_dir: Path) -> tuple[str, str]:
    """Resolve project slug and id from state or directory name."""
    state = read_state(project_dir / DEFAULT_STATE_FILENAME)
    if state is not None:
        project_slug = str(state.get("project_slug") or project_dir.name)
        project_id = str(state.get("project_id") or project_dir.name)
        return project_slug, project_id

    slug, _, project_id = project_dir.name.rpartition("--")
    return slug or project_dir.name, project_id or project_dir.name


def _build_project_audit_context(
    config: AppConfig,
    project_dir: Path,
) -> ProjectContext:
    """Build a lightweight context for one persisted project vault."""
    project_slug, project_id = _project_metadata_from_dir(project_dir)

    return ProjectContext(
        project_slug=project_slug,
        project_key=project_slug,
        project_id=project_id,
        repo_root=project_dir,
        repo_remote=None,
        binding_source="local",
        repo_env_path=project_dir / ".env.local",
        repo_contract_path=project_dir / ".envctl.yaml",
        vault_project_dir=project_dir,
        vault_values_path=project_dir / DEFAULT_VALUES_FILENAME,
        vault_state_path=project_dir / DEFAULT_STATE_FILENAME,
        vault_key_path=project_dir / DEFAULT_KEY_FILENAME,
        vault_crypto=load_configured_vault_crypto(
            config,
            ProjectContext(
                project_slug=project_slug,
                project_key=project_slug,
                project_id=project_id,
                repo_root=project_dir,
                repo_remote=None,
                binding_source="local",
                repo_env_path=project_dir / ".env.local",
                repo_contract_path=project_dir / ".envctl.yaml",
                vault_project_dir=project_dir,
                vault_values_path=project_dir / DEFAULT_VALUES_FILENAME,
                vault_state_path=project_dir / DEFAULT_STATE_FILENAME,
                vault_key_path=project_dir / DEFAULT_KEY_FILENAME,
                vault_crypto=None,
            ),
        )
        if config.encryption_enabled
        else None,
    )


def _audit_project(
    config: AppConfig,
    project_dir: Path,
) -> VaultAuditProjectResult:
    """Audit one persisted project vault."""
    context = _build_project_audit_context(config, project_dir)

    files: list[VaultAuditFileResult] = []
    candidate_paths = [context.vault_values_path]

    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if profiles_dir.exists():
        candidate_paths.extend(sorted(profiles_dir.glob("*.env")))

    for path in candidate_paths:
        state, detail = _classify_vault_file(context, path)
        if state == "missing":
            continue

        files.append(
            VaultAuditFileResult(
                path=path,
                state=state,
                detail=detail,
                private_permissions=not is_world_writable(path),
            )
        )

    return VaultAuditProjectResult(
        project_slug=context.project_slug,
        project_id=context.project_id,
        key_path=context.vault_key_path,
        key_exists=context.vault_key_path.exists(),
        files=tuple(files),
    )


def _run_encrypt_for_context(context: ProjectContext) -> VaultEncryptResult:
    """Encrypt all plaintext vault profile files for one prepared context."""
    crypto = context.vault_crypto
    if crypto is None:
        raise ExecutionError(
            "Encryption is not enabled. "
            "Set 'encryption.enabled = true' in your config first, "
            "then re-run 'envctl vault encrypt'."
        )

    profile_paths = _collect_vault_profile_paths(context)
    encrypted: list[Path] = []
    skipped: list[Path] = []

    for path in profile_paths:
        inspection = crypto.inspect_file(path)
        if inspection.state == "missing":
            continue
        if inspection.state == "encrypted":
            skipped.append(path)
            continue
        if inspection.state == "wrong_key":
            raise ExecutionError(f"Cannot encrypt '{path}': {inspection.detail}")
        if inspection.state == "corrupt":
            raise ExecutionError(f"Cannot encrypt '{path}': {inspection.detail}")

        raw_text = path.read_text(encoding="utf-8")
        crypto.write_encrypted_file(path, raw_text)
        encrypted.append(path)

    return VaultEncryptResult(
        encrypted_files=tuple(encrypted),
        skipped_files=tuple(skipped),
    )


def _run_decrypt_for_context(context: ProjectContext) -> VaultDecryptResult:
    """Decrypt all encrypted vault profile files for one prepared context."""
    crypto = context.vault_crypto
    if crypto is None:
        raise ExecutionError(
            "Encryption is not enabled. "
            "Enable encryption and run 'envctl vault encrypt' to encrypt first."
        )

    profile_paths = _collect_vault_profile_paths(context)
    decrypted: list[Path] = []
    skipped: list[Path] = []

    for path in profile_paths:
        inspection = crypto.inspect_file(path)
        if inspection.state == "missing":
            continue
        if inspection.state == "plaintext":
            skipped.append(path)
            continue
        if inspection.state == "wrong_key":
            raise ExecutionError(f"Cannot decrypt '{path}': {inspection.detail}")
        if inspection.state == "corrupt":
            raise ExecutionError(f"Cannot decrypt '{path}': {inspection.detail}")

        plaintext = crypto.decrypt(path.read_bytes())
        write_text_atomic(path, plaintext)
        decrypted.append(path)

    return VaultDecryptResult(
        decrypted_files=tuple(decrypted),
        skipped_files=tuple(skipped),
    )


def run_vault_check(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultCheckResult]:
    """Check the current physical vault file for the active profile."""
    config, context = load_project_context()
    _require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    state, detail = _classify_vault_file(context, profile_path)
    if state == "missing":
        result = VaultCheckResult(
            path=profile_path,
            exists=False,
            parseable=False,
            private_permissions=False,
            key_count=0,
            state="missing",
            detail=detail,
        )
        return context, resolved_profile, result

    try:
        _resolved_profile, _path, values = load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
            allow_plaintext=not config.encryption_strict,
        )
        parseable = True
        key_count = len(values)
    except (ExecutionError, OSError, ValueError):
        parseable = False
        key_count = 0

    result = VaultCheckResult(
        path=profile_path,
        exists=True,
        parseable=parseable,
        private_permissions=not is_world_writable(profile_path),
        key_count=key_count,
        state=state,
        detail=detail,
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
    config, context = load_project_context()
    _require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)
    state, detail = _classify_vault_file(context, profile_path)

    exists = profile_path.exists()
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
    )
    sensitive_keys = _resolve_sensitive_keys_for_values(context, values)

    return (
        context,
        resolved_profile,
        VaultShowResult(
            path=profile_path,
            exists=exists,
            values=values,
            sensitive_keys=sensitive_keys,
            state=state,
            detail=detail,
        ),
    )


def run_vault_edit(
    active_profile: str | None = None,
) -> tuple[ProjectContext, VaultEditResult]:
    """Open the current physical vault file for the selected profile."""
    config, context = load_project_context()
    _require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    created = False
    if not profile_path.exists():
        write_profile_values(context, resolved_profile, {})
        created = True

    if context.vault_crypto is not None:
        _run_vault_edit_encrypted(profile_path, context=context)
    else:
        editor_adapter.open_file(str(profile_path))

    try:
        load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
            allow_plaintext=not config.encryption_strict,
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
    config, context = load_project_context()
    _require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
    )

    if contract is None:
        return context, resolved_profile, profile_path, tuple(sorted(values))

    unknown_keys = tuple(sorted(set(values) - set(contract.variables)))
    return context, resolved_profile, profile_path, unknown_keys


def run_vault_prune(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, VaultPruneResult]:
    """Remove unknown keys from the active profile vault."""
    config, context = load_project_context()
    _require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = _resolve_selected_profile(context, active_profile)

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
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


def run_vault_encrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultEncryptResult]:
    """Encrypt plaintext vault profile files for the current project or all projects."""
    config, context = load_project_context()

    if include_all_projects:
        encrypted: list[Path] = []
        skipped: list[Path] = []

        for project_dir in _iter_project_dirs(config.projects_dir):
            audit_context = _build_project_audit_context(config, project_dir)
            result = _run_encrypt_for_context(audit_context)
            encrypted.extend(result.encrypted_files)
            skipped.extend(result.skipped_files)

        return context, VaultEncryptResult(
            encrypted_files=tuple(encrypted),
            skipped_files=tuple(skipped),
        )

    result = _run_encrypt_for_context(context)
    return context, result


def run_vault_decrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultDecryptResult]:
    """Decrypt encrypted vault profile files for the current project or all projects."""
    config, context = load_project_context()

    if include_all_projects:
        decrypted: list[Path] = []
        skipped: list[Path] = []

        for project_dir in _iter_project_dirs(config.projects_dir):
            audit_context = _build_project_audit_context(config, project_dir)
            result = _run_decrypt_for_context(audit_context)
            decrypted.extend(result.decrypted_files)
            skipped.extend(result.skipped_files)

        return context, VaultDecryptResult(
            decrypted_files=tuple(decrypted),
            skipped_files=tuple(skipped),
        )

    result = _run_decrypt_for_context(context)
    return context, result


def run_vault_audit() -> tuple[ProjectContext, tuple[VaultAuditProjectResult, ...]]:
    """Audit all project vaults and report plaintext or inconsistent files."""
    config, context = load_project_context()
    projects = tuple(
        _audit_project(config, project_dir)
        for project_dir in _iter_project_dirs(config.projects_dir)
    )
    return context, projects
