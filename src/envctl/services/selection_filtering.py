from collections.abc import Mapping

from envctl.domain.contract import Contract
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.domain.selection import ContractSelection
from envctl.domain.selection_resolution import resolve_selected_variable_names


def filter_projection_values(
    values: Mapping[str, str],
    contract: Contract,
    *,
    selection: ContractSelection | None,
) -> dict[str, str]:
    active_selection = selection or ContractSelection()
    if active_selection.mode == "full":
        return dict(values)

    target_keys = set(resolve_selected_variable_names(contract, active_selection))
    return {key: value for key, value in values.items() if key in target_keys}


def filter_resolution_report(
    report: ResolutionReport,
    contract: Contract,
    *,
    selection: ContractSelection | None,
) -> ResolutionReport:
    active_selection = selection or ContractSelection()
    if active_selection.mode == "full":
        return report

    target_keys = set(resolve_selected_variable_names(contract, active_selection))
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
    """Return one deterministic display group for each projected key."""
    result: dict[str, str | None] = {}
    for key in values:
        spec = contract.variables.get(key)
        if spec is None or not spec.normalized_groups:
            result[key] = None
            continue
        result[key] = spec.normalized_groups[0]
    return result
