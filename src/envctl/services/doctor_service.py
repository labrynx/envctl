"""Environment diagnostics service."""

from __future__ import annotations

import tempfile
from pathlib import Path

from envctl.config.loader import load_config
from envctl.errors import ConfigError
from envctl.models import DoctorCheck
from envctl.utils.paths import detect_repo_root
from envctl.utils.permissions import is_path_world_writable


def _check_symlink_support() -> DoctorCheck:
    """Check whether symlink creation works in the current environment."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.txt"
        target = root / "target.txt"
        source.write_text("ok", encoding="utf-8")

        try:
            target.symlink_to(source)
            ok = target.is_symlink() and target.resolve() == source.resolve()
            return DoctorCheck(
                name="symlink_support",
                status="ok" if ok else "fail",
                detail="Symlink creation works" if ok else "Symlink creation failed",
            )
        except OSError as exc:
            return DoctorCheck(
                name="symlink_support",
                status="fail",
                detail=f"Symlink creation failed: {exc}",
            )


def run_doctor() -> list[DoctorCheck]:
    """Run read-only diagnostics for the local environment.

    v1 focuses on environment readiness:
    - configuration loading
    - vault path presence
    - vault path permissions
    - repository detection
    - symlink support

    TODO(v1.1):
    - add heuristic orphan env key analysis
    - add optional metadata parse checks when inside a managed repository
    - add machine-readable output formats
    """
    try:
        config = load_config()
    except ConfigError as exc:
        return [
            DoctorCheck(
                name="config",
                status="fail",
                detail=str(exc),
            ),
            _check_symlink_support(),
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
        vault_permissions_status = "fail" if is_path_world_writable(config.vault_dir) else "ok"
        vault_permissions_detail = (
            "Vault directory appears world-writable"
            if vault_permissions_status == "fail"
            else "Vault directory is not world-writable"
        )
    else:
        vault_permissions_status = "warn"
        vault_permissions_detail = "Vault permissions cannot be checked until the vault directory exists"

    checks.append(
        DoctorCheck(
            name="vault_permissions",
            status=vault_permissions_status,
            detail=vault_permissions_detail,
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

    checks.append(_check_symlink_support())
    return checks