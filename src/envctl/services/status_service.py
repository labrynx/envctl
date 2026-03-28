"""Status service."""

from __future__ import annotations

from envctl.domain.status import StatusReport
from envctl.errors import ContractError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment


def run_status() -> StatusReport:
    """Compute a human-oriented status report."""
    _config, context = load_project_context()
    contract_exists = context.repo_contract_path.exists()
    vault_exists = context.vault_values_path.exists()

    issues: list[str] = []
    resolved_valid = False
    suggested_action: str | None = None

    if not contract_exists:
        issues.append("Contract file is missing")
        suggested_action = "Create .envctl.schema.yaml"
        summary = "The project is not ready because no contract file was found."
        return StatusReport(
            project_slug=context.project_slug,
            project_id=context.project_id,
            repo_root=context.repo_root,
            contract_exists=contract_exists,
            vault_exists=vault_exists,
            resolved_valid=False,
            summary=summary,
            issues=issues,
            suggested_action=suggested_action,
        )

    try:
        contract = load_contract_for_context(context)
        report = resolve_environment(context, contract)
    except ContractError as exc:
        issues.append(str(exc))
        summary = "The project contract is invalid."
        return StatusReport(
            project_slug=context.project_slug,
            project_id=context.project_id,
            repo_root=context.repo_root,
            contract_exists=contract_exists,
            vault_exists=vault_exists,
            resolved_valid=False,
            summary=summary,
            issues=issues,
            suggested_action="Fix the contract file",
        )

    if report.missing_required:
        issues.append(f"Missing required keys: {', '.join(report.missing_required)}")
        suggested_action = "Run 'envctl fill' or 'envctl set KEY VALUE'"
    if report.invalid_keys:
        issues.append(f"Invalid values: {', '.join(report.invalid_keys)}")
        suggested_action = "Fix the invalid values in the local vault"
    if report.unknown_keys:
        issues.append(f"Unknown keys in vault: {', '.join(report.unknown_keys)}")

    resolved_valid = report.is_valid

    if resolved_valid:
        summary = "The project contract is satisfied and the environment can be projected safely."
    else:
        summary = "The project contract is not satisfied yet."

    return StatusReport(
        project_slug=context.project_slug,
        project_id=context.project_id,
        repo_root=context.repo_root,
        contract_exists=contract_exists,
        vault_exists=vault_exists,
        resolved_valid=resolved_valid,
        summary=summary,
        issues=issues,
        suggested_action=suggested_action,
    )
