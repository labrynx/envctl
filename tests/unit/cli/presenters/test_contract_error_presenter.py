from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.contract_error_presenter import render_contract_error
from envctl.domain.error_diagnostics import ContractDiagnosticIssue, ContractDiagnostics


def test_render_contract_error_renders_summary_facts_and_next_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    diagnostics = ContractDiagnostics(
        category="validation_failed",
        path=Path("/tmp/demo/.envctl.yaml"),
        field="variables.PORT.type",
        issues=(
            ContractDiagnosticIssue(
                field="variables.PORT.type",
                detail="Input should be 'string', 'int', 'bool' or 'url'",
            ),
        ),
        suggested_actions=("envctl check", "fix .envctl.yaml"),
    )

    render_contract_error(
        diagnostics,
        message="Invalid contract: validation failed",
    )
    captured = capsys.readouterr()

    assert captured.out == ""
    assert "Error: Invalid contract: validation failed" in captured.err
    assert "path: /tmp/demo/.envctl.yaml" in captured.err
    assert "field: variables.PORT.type" in captured.err
    assert "Contract issues" in captured.err
    assert "variables.PORT.type: Input should be 'string', 'int', 'bool' or 'url'" in captured.err
    assert "Next steps" in captured.err
    assert "Run `envctl check`" in captured.err
    assert "Run `fix .envctl.yaml`" in captured.err
