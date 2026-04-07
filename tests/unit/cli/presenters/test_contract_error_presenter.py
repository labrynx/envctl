from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.contract_error_presenter import render_contract_error
from envctl.domain.error_diagnostics import ContractDiagnosticIssue, ContractDiagnostics


def normalize_output(value: str) -> str:
    """Normalize path separators in presenter output."""
    return value.replace("\\", "/")


def test_render_contract_error_renders_summary_facts_and_next_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    render_contract_error(
        ContractDiagnostics(
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
        ),
        message="Invalid contract: validation failed",
    )
    captured = capsys.readouterr()

    assert captured.out == ""
    err = normalize_output(captured.err)
    assert "Error: Invalid contract: validation failed" in err
    assert "path: /tmp/demo/.envctl.yaml" in err
    assert "field: variables.PORT.type" in err
    assert "Contract issues" in err
    assert "variables.PORT.type: Input should be 'string', 'int', 'bool' or 'url'" in err
    assert "Run `envctl check`" in err
    assert "Run `fix .envctl.yaml`" in err
