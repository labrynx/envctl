from __future__ import annotations

import pytest

from envctl.domain.diagnostics import DiagnosticSummary, InspectResult
from envctl.domain.selection import ContractSelection
from envctl.services.doctor_service import run_doctor
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def test_run_doctor_delegates_to_inspect(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    result = InspectResult(
        project=context,
        active_profile="staging",
        selection=ContractSelection(),
        contract_path=str(context.repo_contract_path),
        values_path=str(context.vault_values_path),
        summary=DiagnosticSummary(total=1, valid=1, invalid=0, unknown=0),
        variables=(make_resolved_value(key="APP_NAME", value="demo"),),
        problems=(),
    )

    monkeypatch.setattr(
        "envctl.services.doctor_service.run_inspect",
        lambda active_profile=None: (context, result, ()),
    )

    resolved_context, resolved_result, warnings = run_doctor("staging")

    assert resolved_context is context
    assert resolved_result is result
    assert warnings == ()
