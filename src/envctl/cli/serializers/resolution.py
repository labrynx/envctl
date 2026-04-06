"""Resolution serializers."""

from __future__ import annotations

from typing import Any

from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.domain.selection import ContractSelection
from envctl.utils.masking import mask_value


def serialize_resolved_value(item: ResolvedValue) -> dict[str, Any]:
    """Serialize one resolved value."""
    shown_raw_value = None if item.raw_value is None or item.masked else item.raw_value
    shown_value = mask_value(item.value) if item.masked else item.value

    return {
        "key": item.key,
        "raw_value": shown_raw_value,
        "value": shown_value,
        "source": item.source,
        "masked": item.masked,
        "expansion_status": item.expansion_status,
        "expansion_refs": list(item.expansion_refs),
        "expansion_error": (
            {
                "kind": item.expansion_error.kind,
                "detail": item.expansion_error.detail,
            }
            if item.expansion_error is not None
            else None
        ),
        "valid": item.valid,
        "detail": item.detail,
    }


def serialize_resolution_report(report: ResolutionReport) -> dict[str, Any]:
    """Serialize one resolution report."""
    return {
        "is_valid": report.is_valid,
        "values": {
            key: serialize_resolved_value(report.values[key]) for key in sorted(report.values)
        },
        "missing_required": list(report.missing_required),
        "unknown_keys": list(report.unknown_keys),
        "invalid_keys": list(report.invalid_keys),
    }


def serialize_contract_selection(selection: ContractSelection) -> dict[str, Any]:
    """Serialize one normalized selection scope."""
    return {
        "mode": selection.mode,
        "group": selection.group,
        "set": selection.set_name,
        "var": selection.variable,
    }
