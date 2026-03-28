"""Explain command."""

from __future__ import annotations

import typer

from envctl.cli.decorators import handle_errors
from envctl.services.explain_service import run_explain
from envctl.utils.masking import mask_value
from envctl.utils.output import print_kv


@handle_errors
def explain_command(key: str = typer.Argument(...)) -> None:
    """Explain one resolved key."""
    _context, item = run_explain(key)
    print_kv("key", item.key)
    print_kv("source", item.source)
    print_kv("value", mask_value(item.value) if item.masked else item.value)
    print_kv("valid", "yes" if item.valid else "no")
    if item.detail:
        print_kv("detail", item.detail)
