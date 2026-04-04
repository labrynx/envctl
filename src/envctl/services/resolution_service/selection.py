from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.services.resolution_service.types import SelectedValue


def select_contract_values(
    contract: Contract,
    *,
    profile_values: dict[str, str],
    profile_source: str,
) -> tuple[dict[str, SelectedValue], list[str]]:
    """Select raw values before expansion."""
    selected_values: dict[str, SelectedValue] = {}
    missing_required: list[str] = []

    for key, spec in contract.variables.items():
        raw_value: str | None = None
        source: str | None = None

        if key in profile_values:
            raw_value = profile_values[key]
            source = profile_source
        elif spec.default is not None:
            raw_value = str(spec.default)
            source = "default"

        if raw_value is None:
            if spec.required:
                missing_required.append(key)
            continue

        selected_values[key] = SelectedValue(
            key=key,
            raw_value=raw_value,
            source=source or "unknown",
            masked=spec.sensitive,
        )

    return selected_values, missing_required
