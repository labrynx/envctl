"""Status service."""

from __future__ import annotations

from envctl.domain.status import StatusReport
from envctl.errors import ContractError
from envctl.repository.profile_repository import require_persisted_profile, resolve_profile_path
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import normalize_profile_name

logger = get_logger(__name__)


def run_status(active_profile: str | None = None) -> tuple[str, StatusReport]:
    """Compute a human-oriented status report for one active profile."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Running status",
        extra={
            "active_profile": resolved_profile,
            "repo_root": context.repo_root,
        },
    )

    contract_exists = context.repo_contract_path.exists()
    if resolved_profile == "local":
        _resolved_profile, profile_env_path = resolve_profile_path(context, resolved_profile)
    else:
        _resolved_profile, profile_env_path = require_persisted_profile(context, resolved_profile)
    vault_exists = profile_env_path.exists()
    logger.debug(
        "Resolved status inputs",
        extra={
            "active_profile": resolved_profile,
            "contract_exists": contract_exists,
            "vault_exists": vault_exists,
            "profile_path": profile_env_path,
        },
    )

    issues: list[str] = []
    suggested_action: str | None = None

    if not contract_exists:
        issues.append("Contract file is missing")
        suggested_action = "Create .envctl.yaml or run 'envctl add KEY VALUE'"
        summary = "The project is not ready because no contract file was found."
        logger.debug(
            "Status returning early because contract is missing",
            extra={
                "active_profile": resolved_profile,
                "vault_exists": vault_exists,
            },
        )
        return (
            resolved_profile,
            StatusReport(
                project_slug=context.project_slug,
                project_id=context.project_id,
                repo_root=context.repo_root,
                contract_exists=False,
                vault_exists=vault_exists,
                resolved_valid=False,
                summary=summary,
                issues=issues,
                suggested_action=suggested_action,
            ),
        )

    try:
        contract = load_contract_for_context(context)
        report = resolve_environment(context, contract, active_profile=resolved_profile)
    except ContractError as exc:
        issues.append(str(exc))
        summary = "The project contract is invalid."
        logger.debug(
            "Status returning invalid contract result",
            extra={
                "active_profile": resolved_profile,
                "issue_count": len(issues),
            },
        )
        return (
            resolved_profile,
            StatusReport(
                project_slug=context.project_slug,
                project_id=context.project_id,
                repo_root=context.repo_root,
                contract_exists=True,
                vault_exists=vault_exists,
                resolved_valid=False,
                summary=summary,
                issues=issues,
                suggested_action="Fix the contract file",
            ),
        )

    if report.missing_required:
        issues.append(f"Missing required keys: {', '.join(report.missing_required)}")
        suggested_action = "Run 'envctl fill' or 'envctl set KEY VALUE'"

    if report.invalid_keys:
        issues.append(f"Invalid values: {', '.join(report.invalid_keys)}")
        suggested_action = "Fix the invalid values in the local vault"

    if report.unknown_keys:
        issues.append(f"Unknown keys in vault: {', '.join(report.unknown_keys)}")
        if suggested_action is None:
            suggested_action = "Use 'envctl add KEY VALUE' or remove unknown keys"

    resolved_valid = report.is_valid
    logger.debug(
        "Computed status report details",
        extra={
            "active_profile": resolved_profile,
            "missing_required_count": len(report.missing_required),
            "invalid_key_count": len(report.invalid_keys),
            "unknown_key_count": len(report.unknown_keys),
        },
    )

    if resolved_valid:
        summary = "The project contract is satisfied and the environment can be projected safely."
    else:
        summary = "The project contract is not satisfied yet."
    logger.debug(
        "Status result ready",
        extra={
            "active_profile": resolved_profile,
            "resolved_valid": resolved_valid,
            "issue_count": len(issues),
        },
    )

    return (
        resolved_profile,
        StatusReport(
            project_slug=context.project_slug,
            project_id=context.project_id,
            repo_root=context.repo_root,
            contract_exists=True,
            vault_exists=vault_exists,
            resolved_valid=resolved_valid,
            summary=summary,
            issues=issues,
            suggested_action=suggested_action,
        ),
    )
