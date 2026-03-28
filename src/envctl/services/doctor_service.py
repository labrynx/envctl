"""Doctor service."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.domain.doctor import DoctorCheck
from envctl.errors import ProjectDetectionError
from envctl.utils.filesystem import is_world_writable
from envctl.utils.git import resolve_repo_root


def run_doctor() -> list[DoctorCheck]:
    """Run local diagnostics."""
    config = load_config()
    checks: list[DoctorCheck] = [
        DoctorCheck("config", "ok", f"Using config path: {config.config_path}"),
        DoctorCheck("vault", "ok", f"Using vault path: {config.vault_dir}"),
    ]

    if config.vault_dir.exists():
        if is_world_writable(config.vault_dir):
            checks.append(
                DoctorCheck("vault_permissions", "warn", "Vault directory is world-writable"),
            )
        else:
            checks.append(
                DoctorCheck("vault_permissions", "ok", "Vault directory is not world-writable"),
            )
    else:
        checks.append(
            DoctorCheck("vault_permissions", "warn", "Vault directory does not exist yet")
        )

    try:
        repo_root = resolve_repo_root()
    except ProjectDetectionError as exc:
        checks.append(DoctorCheck("git", "warn", str(exc)))
    else:
        checks.append(DoctorCheck("git", "ok", f"Inside Git repository: {repo_root}"))

    return checks
