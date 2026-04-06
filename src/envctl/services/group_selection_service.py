"""Backward-compatible imports for contract selection helpers."""

from envctl.services.contract_selection_service import (  # noqa: F401
    build_variable_groups,
    filter_projection_values,
    filter_resolution_report,
    resolve_selected_variable_names,
    resolve_variable_names_for_group,
    resolve_variable_names_for_set,
    resolve_variable_names_for_var,
)
