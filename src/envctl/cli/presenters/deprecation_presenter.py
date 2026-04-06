"""Presenters for contract deprecation warnings."""

from __future__ import annotations

from collections.abc import Sequence

import typer

from envctl.domain.deprecations import ContractDeprecationWarning


def render_contract_deprecation_warnings(
    warnings: Sequence[ContractDeprecationWarning],
    *,
    stderr: bool = False,
) -> None:
    for warning in warnings:
        typer.echo(warning.message, err=stderr)
        typer.echo(err=stderr)
