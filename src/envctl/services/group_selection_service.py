"""Helpers for optional contract group targeting."""

from __future__ import annotations

from collections.abc import Mapping

from envctl.domain.contract import Contract
from envctl.domain.resolution import ResolutionReport, ResolvedValue


def get_group_target_keys(
    contract: Contract,
    *,
    group: str | None,
) -> frozenset[str]:
    """Return the declared contract keys targeted by one exact group label."""
    if group is None:
        return frozenset(contract.variables)

    return frozenset(key for key, spec in contract.variables.items() if spec.group == group)


def filter_projection_values(
    values: Mapping[str, str],
    contract: Contract,
    *,
    group: str | None,
) -> dict[str, str]:
    """Filter resolved projection values to the selected group when requested."""
    if group is None:
        return dict(values)

    target_keys = get_group_target_keys(contract, group=group)
    return {key: value for key, value in values.items() if key in target_keys}


def filter_resolution_report(
    report: ResolutionReport,
    contract: Contract,
    *,
    group: str | None,
) -> ResolutionReport:
    """Filter a resolution report to the selected group when requested."""
    if group is None:
        return report

    target_keys = get_group_target_keys(contract, group=group)
    values: dict[str, ResolvedValue] = {
        key: value for key, value in report.values.items() if key in target_keys
    }

    return ResolutionReport.from_parts(
        values=values,
        missing_required=[key for key in report.missing_required if key in target_keys],
        unknown_keys=(),
        invalid_keys=[key for key in report.invalid_keys if key in target_keys],
    )


def build_variable_groups(
    contract: Contract,
    values: Mapping[str, str],
) -> dict[str, str | None]:
    """Return group labels for the provided projection keys."""
    return {key: contract.variables[key].group for key in values if key in contract.variables}
