from __future__ import annotations

import pytest

from envctl.services.inspect_service import run_inspect
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_run_inspect_returns_context_and_resolution_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    contract = object()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo-app",
                source="vault",
                valid=True,
            )
        },
        unknown_keys=("LEGACY_KEY",),
    )

    monkeypatch.setattr(
        "envctl.services.inspect_service.load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(
        "envctl.services.inspect_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.inspect_service.resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    result_context, active_profile, result_report = run_inspect()

    assert result_context == context
    assert active_profile == "local"
    assert result_report is report
    assert result_report.values["APP_NAME"].value == "demo-app"
    assert result_report.unknown_keys == ("LEGACY_KEY",)
