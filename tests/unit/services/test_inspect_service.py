from __future__ import annotations

import pytest

import envctl.services.inspect_service as inspect_service
from envctl.domain.selection import group_selection
from envctl.services.inspect_service import run_inspect
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec


def test_run_inspect_returns_context_profile_report_and_warnings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo")}
    )

    monkeypatch.setattr(inspect_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        inspect_service,
        "load_contract_with_warnings",
        lambda _path: (contract, ()),
    )
    monkeypatch.setattr(
        inspect_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    resolved_context, resolved_profile, filtered_report, warnings = run_inspect("staging")

    assert resolved_context is context
    assert resolved_profile == "staging"
    assert filtered_report is report
    assert warnings == ()


def test_run_inspect_filters_report_by_group_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME", groups=("Application",)),
            "DATABASE_URL": make_variable_spec(
                name="DATABASE_URL",
                groups=("Database",),
            ),
        }
    )
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(key="APP_NAME", value="demo"),
            "DATABASE_URL": make_resolved_value(key="DATABASE_URL", value="db"),
        }
    )

    monkeypatch.setattr(inspect_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        inspect_service,
        "load_contract_with_warnings",
        lambda _path: (contract, ()),
    )
    monkeypatch.setattr(
        inspect_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    _context, _profile, filtered_report, _warnings = run_inspect(
        "staging",
        selection=group_selection("Application"),
    )

    assert tuple(filtered_report.values) == ("APP_NAME",)
