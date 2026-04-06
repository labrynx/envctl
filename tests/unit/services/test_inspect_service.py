from __future__ import annotations

import pytest

import envctl.services.inspect_service as inspect_service
from envctl.domain.contract import ResolvedContractGraph
from envctl.domain.selection import group_selection
from envctl.repository.contract_composition import ResolvedContractBundle
from envctl.services.inspect_service import run_inspect, run_inspect_key
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec


def test_run_inspect_returns_context_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
            )
        }
    )

    monkeypatch.setattr(inspect_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        inspect_service,
        "load_resolved_contract_bundle",
        lambda _repo_root: ResolvedContractBundle(
            contract=contract,
            graph=ResolvedContractGraph(),
            warnings=(),
        ),
    )
    monkeypatch.setattr(
        inspect_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    resolved_context, result, warnings = run_inspect("staging")

    assert resolved_context is context
    assert result.active_profile == "staging"
    assert result.summary.valid == 1
    assert warnings == ()


def test_run_inspect_filters_report_by_group_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(
                name="APP_NAME",
                groups=("Application",),
            ),
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
        "load_resolved_contract_bundle",
        lambda _repo_root: ResolvedContractBundle(
            contract=contract,
            graph=ResolvedContractGraph(),
            warnings=(),
        ),
    )
    monkeypatch.setattr(
        inspect_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    _context, result, _warnings = run_inspect(
        "staging",
        selection=group_selection("Application"),
    )

    assert tuple(item.key for item in result.variables) == ("APP_NAME",)


def test_run_inspect_key_returns_detailed_item(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(
                name="APP_NAME",
                groups=("Application",),
            )
        }
    )
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
            )
        }
    )

    monkeypatch.setattr(inspect_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(
        inspect_service,
        "load_resolved_contract_bundle",
        lambda _repo_root: ResolvedContractBundle(
            contract=contract,
            graph=ResolvedContractGraph(),
            warnings=(),
        ),
    )
    monkeypatch.setattr(
        inspect_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    _context, result, _warnings = run_inspect_key("APP_NAME", "staging")

    assert result.item.key == "APP_NAME"
    assert result.groups == ("Application",)
