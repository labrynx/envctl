from __future__ import annotations

import pytest

from envctl.services.inspect_service import run_inspect
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec


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


def test_run_inspect_filters_report_by_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME", group="Application"),
            "DATABASE_URL": make_variable_spec(name="DATABASE_URL", group="Database"),
        }
    )
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(key="APP_NAME", value="demo-app"),
            "DATABASE_URL": make_resolved_value(key="DATABASE_URL", value="db"),
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

    _context, _profile, filtered_report = run_inspect(group="Application")

    assert tuple(filtered_report.values) == ("APP_NAME",)
    assert filtered_report.unknown_keys == ()
