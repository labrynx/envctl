"""Fill command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_fill_no_changes, render_fill_result
from envctl.cli.prompts.input import prompt_secret, prompt_string
from envctl.cli.runtime import get_active_profile
from envctl.services.fill_service import apply_fill, build_fill_plan


@handle_errors
@requires_writable_runtime("fill")
@text_output_only("fill")
def fill_command() -> None:
    """Interactively fill missing required values for the active profile."""
    context, active_profile, plan = build_fill_plan(get_active_profile())

    if not plan:
        render_fill_no_changes(profile=active_profile)
        return

    answers: dict[str, str] = {}
    for item in plan:
        prompt_label = item.key
        if item.description:
            prompt_label = f"{item.key} — {item.description}"

        answers[item.key] = (
            prompt_secret(prompt_label, default=item.default_value)
            if item.sensitive
            else prompt_string(prompt_label, default=item.default_value)
        )

    _context, resolved_profile, profile_path, changed_keys = apply_fill(
        answers,
        get_active_profile(),
    )

    render_fill_result(
        project_name=context.display_name,
        profile=resolved_profile,
        profile_path=profile_path,
        changed_keys=changed_keys,
    )
