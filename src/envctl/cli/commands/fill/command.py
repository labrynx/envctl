"""Fill command."""

from __future__ import annotations

from envctl.cli.callbacks import typer_prompt
from envctl.cli.decorators import handle_errors
from envctl.services.fill_service import apply_fill, build_fill_plan
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def fill_command() -> None:
    """Interactively fill missing required values."""
    context, plan = build_fill_plan()

    if not plan:
        print_warning("No keys were changed")
        return

    collected: dict[str, str] = {}

    for item in plan:
        answer = typer_prompt(
            f"{item.key}: {item.description}",
            item.sensitive,
            item.default_value,
        ).strip()

        if not answer and item.default_value is not None:
            answer = item.default_value

        if answer:
            collected[item.key] = answer

    context, changed = apply_fill(collected)

    if changed:
        print_success(f"Filled {len(changed)} key(s) for {context.display_name}")
        print_kv("keys", ", ".join(changed))
    else:
        print_warning("No keys were changed")
