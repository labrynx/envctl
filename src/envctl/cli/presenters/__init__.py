"""Human-facing CLI presenters."""

from envctl.cli.presenters.action_presenter import (
    render_add_result,
    render_config_init_result,
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
from envctl.cli.presenters.check_presenter import render_check_result
from envctl.cli.presenters.config_error_presenter import render_config_error
from envctl.cli.presenters.contract_error_presenter import render_contract_error
from envctl.cli.presenters.deprecation_presenter import render_contract_deprecation_warnings
from envctl.cli.presenters.inspect_presenter import render_inspect_key_result, render_inspect_result
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
from envctl.cli.presenters.projection_error_presenter import render_projection_validation_failure
from envctl.cli.presenters.repository_error_presenter import (
    render_project_binding_error,
    render_repository_discovery_error,
)
from envctl.cli.presenters.run_presenter import render_run_warnings
from envctl.cli.presenters.state_error_presenter import render_state_error
from envctl.cli.presenters.status_presenter import render_status, render_status_view
from envctl.cli.presenters.vault_presenter import (
    render_vault_audit_result,
    render_vault_check_result,
    render_vault_decrypt_result,
    render_vault_edit_result,
    render_vault_encrypt_result,
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
    "render_check_result",
    "render_config_error",
    "render_config_init_result",
    "render_contract_deprecation_warnings",
    "render_contract_error",
    "render_export_output",
    "render_fill_no_changes",
    "render_fill_result",
    "render_inferred_spec",
    "render_init_result",
    "render_inspect_key_result",
    "render_inspect_result",
    "render_profile_copy_result",
    "render_profile_create_result",
    "render_profile_list_result",
    "render_profile_path_result",
    "render_profile_remove_result",
    "render_project_bind_result",
    "render_project_binding_error",
    "render_project_rebind_result",
    "render_project_repair_result",
    "render_project_unbind_result",
    "render_projection_validation_failure",
    "render_remove_result",
    "render_repository_discovery_error",
    "render_run_warnings",
    "render_set_result",
    "render_state_error",
    "render_status",
    "render_status_view",
    "render_sync_result",
    "render_unset_result",
    "render_vault_audit_result",
    "render_vault_check_result",
    "render_vault_decrypt_result",
    "render_vault_edit_result",
    "render_vault_encrypt_result",
    "render_vault_path_result",
    "render_vault_prune_cancelled",
    "render_vault_prune_no_changes",
    "render_vault_prune_result",
    "render_vault_show_cancelled",
    "render_vault_show_empty",
    "render_vault_show_missing",
    "render_vault_show_values",
]
