"""Human-facing CLI presenters."""

from envctl.cli.presenters.action_presenter import (
    render_add_result,
    render_config_init_result,
    render_explain_value,
    render_export_output,
    render_fill_no_changes,
    render_fill_result,
    render_inferred_spec,
    render_init_result,
    render_remove_result,
    render_set_result,
    render_sync_result,
    render_unset_result,
)
from envctl.cli.presenters.doctor_presenter import render_doctor_checks
from envctl.cli.presenters.profile_presenter import (
    render_profile_copy_result,
    render_profile_create_result,
    render_profile_list_result,
    render_profile_path_result,
    render_profile_remove_result,
)
from envctl.cli.presenters.project_presenter import (
    render_project_bind_result,
    render_project_rebind_result,
    render_project_repair_result,
    render_project_unbind_result,
)
from envctl.cli.presenters.resolution_presenter import (
    render_resolution,
    render_resolution_view,
)
from envctl.cli.presenters.status_presenter import (
    render_status,
    render_status_view,
)
from envctl.cli.presenters.vault_presenter import (
    render_vault_check_result,
    render_vault_edit_result,
    render_vault_path_result,
    render_vault_prune_cancelled,
    render_vault_prune_no_changes,
    render_vault_prune_result,
    render_vault_show_cancelled,
    render_vault_show_empty,
    render_vault_show_missing,
    render_vault_show_values,
)

__all__ = [
    "render_add_result",
    "render_config_init_result",
    "render_doctor_checks",
    "render_explain_value",
    "render_export_output",
    "render_fill_no_changes",
    "render_fill_result",
    "render_inferred_spec",
    "render_init_result",
    "render_profile_copy_result",
    "render_profile_create_result",
    "render_profile_list_result",
    "render_profile_path_result",
    "render_profile_remove_result",
    "render_project_bind_result",
    "render_project_rebind_result",
    "render_project_repair_result",
    "render_project_unbind_result",
    "render_remove_result",
    "render_resolution",
    "render_resolution_view",
    "render_set_result",
    "render_status",
    "render_status_view",
    "render_sync_result",
    "render_unset_result",
    "render_vault_check_result",
    "render_vault_edit_result",
    "render_vault_path_result",
    "render_vault_prune_cancelled",
    "render_vault_prune_no_changes",
    "render_vault_prune_result",
    "render_vault_show_cancelled",
    "render_vault_show_empty",
    "render_vault_show_missing",
    "render_vault_show_values",
]
