"""Environment diagnostics service."""

from __future__ import annotations

from pathlib import Path

from envctl.config.loader import load_config
from envctl.domain.doctor import DoctorCheck
from envctl.errors import ConfigError
from envctl.utils.git import detect_repo_root
from envctl.utils.permissions import is_path_world_writable
from envctl.utils.symlinks import check_symlink_support


def run_doctor() -> list[DoctorCheck]:
    """Run read-only diagnostics for the local environment."""
    try:
        config = load_config()
    except ConfigError as exc:
        return [
            DoctorCheck(
                name="config",
                status="fail",
                detail=str(exc),
            ),
            check_symlink_support(),
        ]

    repo_root = detect_repo_root(Path.cwd())
    vault_exists = config.vault_dir.exists()

    checks: list[DoctorCheck] = []

    if config.config_path.exists():
        checks.append(
            DoctorCheck(
                name="config",
                status="ok",
                detail=f"Using config file: {config.config_path}",
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="config",
                status="ok",
                detail=f"Using defaults (no config file at {config.config_path})",
            )
        )

    checks.append(
        DoctorCheck(
            name="vault_path",
            status="ok" if vault_exists else "warn",
            detail=(
                f"Vault directory exists: {config.vault_dir}"
                if vault_exists
                else f"Vault directory has not been created yet: {config.vault_dir}"
            ),
        )
    )

    if vault_exists:
        is_insecure = is_path_world_writable(config.vault_dir)
        checks.append(
            DoctorCheck(
                name="vault_permissions",
                status="fail" if is_insecure else "ok",
                detail=(
                    "Vault directory appears world-writable"
                    if is_insecure
                    else "Vault directory is not world-writable"
                ),
            )
        )
    else:
        checks.append(
            DoctorCheck(
                name="vault_permissions",
                status="warn",
                detail="Vault permissions cannot be checked until the vault directory exists",
            )
        )

    checks.append(
        DoctorCheck(
            name="repo_detection",
            status="ok" if repo_root is not None else "warn",
            detail=(
                f"Git repository detected at {repo_root}"
                if repo_root is not None
                else "No Git repository detected from the current working directory"
            ),
        )
    )

    checks.append(check_symlink_support())
    return checks
