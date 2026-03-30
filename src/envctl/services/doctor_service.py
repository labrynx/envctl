"""Doctor service."""

from __future__ import annotations

from envctl.config.loader import load_config
from envctl.constants import GIT_CONFIG_PROJECT_ID_KEY
from envctl.domain.doctor import DoctorCheck
from envctl.errors import EnvctlError, ProjectDetectionError
from envctl.repository.project_context import build_project_context
from envctl.utils.filesystem import is_world_writable


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
        context = build_project_context(config)

        checks.append(
            DoctorCheck(
                "project",
                "ok",
                f"Resolved project: {context.project_slug} ({context.project_id})",
            )
        )
        checks.append(
            DoctorCheck("binding_source", "ok", f"Binding source: {context.binding_source}"),
        )

        if context.binding_source == "local":
            checks.append(
                DoctorCheck(
                    "binding",
                    "ok",
                    f"Local git binding present in '{GIT_CONFIG_PROJECT_ID_KEY}'",
                )
            )
        elif context.binding_source == "recovered":
            checks.append(
                DoctorCheck(
                    "binding",
                    "warn",
                    (
                        "No local git binding found. "
                        "A matching vault was recovered from persisted state."
                    ),
                )
            )
        else:
            checks.append(
                DoctorCheck(
                    "binding",
                    "warn",
                    (
                        "No persisted binding found yet. "
                        "Run 'envctl init' or any mutating command to persist it."
                    ),
                )
            )

        if context.repo_contract_path.exists():
            checks.append(
                DoctorCheck("contract", "ok", f"Contract found: {context.repo_contract_path.name}")
            )
        else:
            checks.append(
                DoctorCheck("contract", "warn", f"Contract not found: {context.repo_contract_path}")
            )

        if context.vault_state_path.exists():
            checks.append(
                DoctorCheck("state", "ok", f"Vault state found: {context.vault_state_path}")
            )
        else:
            checks.append(DoctorCheck("state", "warn", "Vault state file does not exist yet"))

    except (EnvctlError, ProjectDetectionError) as exc:
        checks.append(DoctorCheck("project", "warn", str(exc)))

    return checks
