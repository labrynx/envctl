"""Status service."""

from __future__ import annotations

from envctl.domain.status import StatusActionKind, StatusIssue, StatusReport
from envctl.errors import ContractError
from envctl.observability.timing import observe_span
from envctl.repository.profile_repository import require_persisted_profile, resolve_profile_path
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.project_paths import normalize_profile_name


def run_status(active_profile: str | None = None) -> tuple[str, StatusReport]:
    """Compute a human-oriented status report for one active profile."""
    with observe_span(
        "resolution",
        module=__name__,
        operation="run_status",
        fields={},
    ) as span_fields:
        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)

        contract_exists = context.repo_contract_path.exists()
        if resolved_profile == "local":
            _resolved_profile, profile_env_path = resolve_profile_path(context, resolved_profile)
        else:
            _resolved_profile, profile_env_path = require_persisted_profile(
                context,
                resolved_profile,
            )
        vault_exists = profile_env_path.exists()

        issues: list[StatusIssue] = []
        suggested_action_kind: StatusActionKind | None = None

        if not contract_exists:
            issues.append(StatusIssue(kind="contract_missing"))
            span_fields["selected_profile"] = resolved_profile
            span_fields["exists"] = vault_exists
            return (
                resolved_profile,
                StatusReport(
                    project_slug=context.project_slug,
                    project_id=context.project_id,
                    repo_root=context.repo_root,
                    contract_exists=False,
                    vault_exists=vault_exists,
                    resolved_valid=False,
                    summary_kind="missing_contract",
                    issues=tuple(issues),
                    suggested_action_kind="create_contract_or_add_key",
                ),
            )

        try:
            contract = load_contract_for_context(context)
            report = resolve_environment(context, contract, active_profile=resolved_profile)
        except ContractError as exc:
            issues.append(StatusIssue(kind="contract_error", detail=str(exc)))
            span_fields["selected_profile"] = resolved_profile
            span_fields["problem_count"] = len(issues)
            return (
                resolved_profile,
                StatusReport(
                    project_slug=context.project_slug,
                    project_id=context.project_id,
                    repo_root=context.repo_root,
                    contract_exists=True,
                    vault_exists=vault_exists,
                    resolved_valid=False,
                    summary_kind="invalid_contract",
                    issues=tuple(issues),
                    suggested_action_kind="fix_contract_file",
                ),
            )

        if report.missing_required:
            issues.append(StatusIssue(kind="missing_required", keys=tuple(report.missing_required)))
            suggested_action_kind = "fill_or_set_values"

        if report.invalid_keys:
            issues.append(StatusIssue(kind="invalid_values", keys=tuple(report.invalid_keys)))
            suggested_action_kind = "fix_invalid_values"

        if report.unknown_keys:
            issues.append(StatusIssue(kind="unknown_keys", keys=tuple(report.unknown_keys)))
            if suggested_action_kind is None:
                suggested_action_kind = "add_or_remove_unknown_keys"

        resolved_valid = report.is_valid
        span_fields["selected_profile"] = resolved_profile
        span_fields["problem_count"] = len(issues)
        span_fields["missing_required_count"] = len(report.missing_required)
        span_fields["invalid_key_count"] = len(report.invalid_keys)
        span_fields["unknown_key_count"] = len(report.unknown_keys)
        return (
            resolved_profile,
            StatusReport(
                project_slug=context.project_slug,
                project_id=context.project_id,
                repo_root=context.repo_root,
                contract_exists=True,
                vault_exists=vault_exists,
                resolved_valid=resolved_valid,
                summary_kind="satisfied" if resolved_valid else "unsatisfied",
                issues=tuple(issues),
                suggested_action_kind=suggested_action_kind,
            ),
        )
