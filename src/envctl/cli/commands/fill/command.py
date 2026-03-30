"""Fill command."""

from __future__ import annotations

from envctl.cli.callbacks import typer_prompt
from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.runtime import get_active_profile
from envctl.services.fill_service import apply_fill, build_fill_plan
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
@requires_writable_runtime("fill")
def fill_command() -> None:
    """Interactively fill missing required values for the active profile."""
    context, active_profile, plan = build_fill_plan(get_active_profile())

    if not plan:
        print_warning("No keys were changed")
        print_kv("profile", active_profile)
        return

    answers: dict[str, str] = {}
    for item in plan:
        prompt_label = item.key
        if item.description:
            prompt_label = f"{item.key} — {item.description}"

        answers[item.key] = typer_prompt(
            prompt_label,
            item.sensitive,
            item.default_value,
        )

    _context, resolved_profile, profile_path, changed_keys = apply_fill(
        answers,
        get_active_profile(),
    )

    if not changed_keys:
        print_warning("No keys were changed")
        print_kv("profile", resolved_profile)
        print_kv("vault_values", str(profile_path))
        return

    print_success(f"Filled {len(changed_keys)} key(s) for {context.display_name}")
    print_kv("profile", resolved_profile)
    print_kv("vault_values", str(profile_path))
    print_kv("keys", ", ".join(changed_keys))
