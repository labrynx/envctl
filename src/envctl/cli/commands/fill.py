"""Fill command."""

from __future__ import annotations

from envctl.cli.callbacks import typer_prompt
from envctl.cli.decorators import handle_errors
from envctl.services.fill_service import run_fill
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def fill_command() -> None:
    """Interactively fill missing required values."""
    context, changed = run_fill(prompt=typer_prompt)
    if changed:
        print_success(f"Filled {len(changed)} key(s) for {context.display_name}")
        print_kv("keys", ", ".join(changed))
    else:
        print_warning("No keys were changed")
