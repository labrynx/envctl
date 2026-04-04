from __future__ import annotations

import pytest

import envctl.services.projection_validation as projection_validation
from envctl.errors import ValidationError
from tests.support.assertions import require_projection_validation_diagnostics
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec


def test_resolve_projectable_environment_returns_contract_and_report_when_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile")}
    )

    monkeypatch.setattr(
        projection_validation,
        "load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        projection_validation,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    resolved_contract, resolved_report = projection_validation.resolve_projectable_environment(
        context,
        active_profile="local",
        group=None,
        operation="export",
    )

    assert resolved_contract == contract
    assert resolved_report == report


def test_resolve_projectable_environment_raises_with_filtered_report_and_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", group="Network"),
            "API_URL": make_variable_spec(name="API_URL", group="Application"),
        }
    )
    report = make_resolution_report(
        values={
            "API_URL": make_resolved_value(
                key="API_URL",
                value="bad",
                source="profile",
                valid=False,
                detail="Expected a valid URL",
            ),
        },
        missing_required=("API_HOST",),
        invalid_keys=("API_URL",),
        unknown_keys=("OLD_KEY",),
    )

    monkeypatch.setattr(
        projection_validation,
        "load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        projection_validation,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    with pytest.raises(ValidationError, match=r"Cannot export because") as exc_info:
        projection_validation.resolve_projectable_environment(
            context,
            active_profile="staging",
            group="Application",
            operation="export",
        )

    diagnostics = require_projection_validation_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.operation == "export"
    assert diagnostics.active_profile == "staging"
    assert diagnostics.selected_group == "Application"
    assert diagnostics.report.missing_required == ()
    assert diagnostics.report.invalid_keys == ("API_URL",)
    assert diagnostics.report.unknown_keys == ()
    assert diagnostics.suggested_actions == ("envctl check", "envctl explain KEY")


def test_resolve_projectable_environment_deduplicates_actions_for_multiple_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        missing_required=("APP_NAME",),
        invalid_keys=("APP_NAME",),
        unknown_keys=("OLD_KEY",),
    )

    monkeypatch.setattr(
        projection_validation,
        "load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        projection_validation,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    with pytest.raises(ValidationError) as exc_info:
        projection_validation.resolve_projectable_environment(
            context,
            active_profile="local",
            group=None,
            operation="sync",
        )

    diagnostics = require_projection_validation_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.suggested_actions == (
        "envctl fill",
        "envctl set KEY VALUE",
        "envctl check",
        "envctl explain KEY",
        "envctl inspect",
    )
