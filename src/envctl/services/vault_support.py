"""Internal support helpers for vault-oriented services."""

from __future__ import annotations

from pathlib import Path

from envctl.constants import DEFAULT_KEY_FILENAME, DEFAULT_STATE_FILENAME, DEFAULT_VALUES_FILENAME
from envctl.domain.app_config import AppConfig
from envctl.domain.operations import (
    VaultAuditFileResult,
    VaultAuditProjectResult,
    VaultDecryptResult,
    VaultEncryptResult,
)
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.repository.profile_repository import require_persisted_profile
from envctl.repository.profile_repository import (
    resolve_profile_path as resolve_profile_vault_path,
)
from envctl.repository.state_repository import read_state
from envctl.services.context_service import load_configured_vault_crypto
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import is_world_writable
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import build_profiles_dir
from envctl.vault_crypto import VaultCrypto, VaultFileState

logger = get_logger(__name__)


def resolve_selected_profile(
    context: ProjectContext,
    active_profile: str | None,
) -> tuple[str, Path]:
    """Resolve the active profile name and file path."""
    if active_profile in (None, "local"):
        return resolve_profile_vault_path(context, active_profile)

    return require_persisted_profile(context, active_profile)


def collect_vault_profile_paths(context: ProjectContext) -> list[Path]:
    """Return all existing vault profile file paths for the current project."""
    paths: list[Path] = []
    if context.vault_values_path.exists():
        paths.append(context.vault_values_path)

    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if profiles_dir.exists():
        paths.extend(sorted(profiles_dir.glob("*.env")))

    return paths


def classify_vault_file(
    context: ProjectContext,
    profile_path: Path,
) -> tuple[VaultFileState, str]:
    """Return the inspection state for one vault path."""
    if not profile_path.exists():
        logger.debug("Vault file is missing during classification", extra={"path": profile_path})
        return "missing", "Vault file does not exist."

    raw = profile_path.read_bytes()
    if context.vault_crypto is not None:
        inspection = context.vault_crypto.inspect_bytes(raw)
        logger.debug(
            "Classified vault file with crypto",
            extra={"path": profile_path, "state": inspection.state},
        )
        return inspection.state, inspection.detail

    if VaultCrypto.looks_encrypted(raw):
        logger.debug(
            "Vault file looks encrypted without active crypto",
            extra={"path": profile_path},
        )
        return (
            "encrypted",
            "Vault file is encrypted, but encryption is disabled in config.",
        )

    logger.debug("Vault file classified as plaintext", extra={"path": profile_path})
    return "plaintext", "Vault file is plaintext."


def require_no_plaintext_in_strict_mode(
    context: ProjectContext,
    *,
    strict: bool,
) -> None:
    """Reject any plaintext vault files when strict mode is enabled."""
    if not strict:
        return

    logger.debug(
        "Checking strict vault plaintext policy",
        extra={"project_id": context.project_id, "strict": strict},
    )
    for path in collect_vault_profile_paths(context):
        state, detail = classify_vault_file(context, path)
        if state == "plaintext":
            raise ExecutionError(
                f"Plaintext vault file detected in strict encryption mode: {path}. {detail}"
            )


def iter_project_dirs(projects_dir: Path) -> tuple[Path, ...]:
    """Return every persisted project vault directory."""
    if not projects_dir.exists():
        return ()

    return tuple(sorted(path for path in projects_dir.iterdir() if path.is_dir()))


def project_metadata_from_dir(project_dir: Path) -> tuple[str, str]:
    """Resolve project slug and id from state or directory name."""
    state = read_state(project_dir / DEFAULT_STATE_FILENAME)
    if state is not None:
        project_slug = str(state.get("project_slug") or project_dir.name)
        project_id = str(state.get("project_id") or project_dir.name)
        return project_slug, project_id

    slug, _, project_id = project_dir.name.rpartition("--")
    return slug or project_dir.name, project_id or project_dir.name


def build_project_audit_context(
    config: AppConfig,
    project_dir: Path,
) -> ProjectContext:
    """Build a lightweight context for one persisted project vault."""
    project_slug, project_id = project_metadata_from_dir(project_dir)
    base_context = ProjectContext(
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
    )
    crypto = (
        load_configured_vault_crypto(config, base_context)
        if config.encryption_enabled
        else None
    )
    return ProjectContext(
        project_slug=base_context.project_slug,
        project_key=base_context.project_key,
        project_id=base_context.project_id,
        repo_root=base_context.repo_root,
        repo_remote=base_context.repo_remote,
        binding_source=base_context.binding_source,
        repo_env_path=base_context.repo_env_path,
        repo_contract_path=base_context.repo_contract_path,
        vault_project_dir=base_context.vault_project_dir,
        vault_values_path=base_context.vault_values_path,
        vault_state_path=base_context.vault_state_path,
        vault_key_path=base_context.vault_key_path,
        vault_crypto=crypto,
    )


def audit_project(
    config: AppConfig,
    project_dir: Path,
) -> VaultAuditProjectResult:
    """Audit one persisted project vault."""
    context = build_project_audit_context(config, project_dir)

    files: list[VaultAuditFileResult] = []
    candidate_paths = [context.vault_values_path]

    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if profiles_dir.exists():
        candidate_paths.extend(sorted(profiles_dir.glob("*.env")))

    for path in candidate_paths:
        state, detail = classify_vault_file(context, path)
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


def run_encrypt_for_context(context: ProjectContext) -> VaultEncryptResult:
    """Encrypt all plaintext vault profile files for one prepared context."""
    crypto = context.vault_crypto
    if crypto is None:
        raise ExecutionError(
            "Encryption is not enabled. "
            "Set 'encryption.enabled = true' in your config first, "
            "then re-run 'envctl vault encrypt'."
        )

    profile_paths = collect_vault_profile_paths(context)
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


def run_decrypt_for_context(context: ProjectContext) -> VaultDecryptResult:
    """Decrypt all encrypted vault profile files for one prepared context."""
    crypto = context.vault_crypto
    if crypto is None:
        raise ExecutionError(
            "Encryption is not enabled. "
            "Enable encryption and run 'envctl vault encrypt' to encrypt first."
        )

    profile_paths = collect_vault_profile_paths(context)
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
