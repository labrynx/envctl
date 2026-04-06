from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.projection_validation as projection_validation
from envctl.domain.contract import Contract, ResolvedContractGraph
from envctl.domain.selection import group_selection
from envctl.errors import ValidationError
from envctl.repository.contract_composition import ResolvedContractBundle
from tests.support.assertions import require_projection_validation_diagnostics
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_variable_spec


def _bundle_for(contract: Contract) -> ResolvedContractBundle:
    return ResolvedContractBundle(
        contract=contract,
        graph=ResolvedContractGraph(
            root_path=Path("/tmp/project/.envctl.yaml"),
            contract_paths=(Path("/tmp/project/.envctl.yaml"),),
            import_graph={Path("/tmp/project/.envctl.yaml"): ()},
            variables={},
            declared_in={},
            sets_index={},
            groups_index={},
        ),
        warnings=(),
        command_warnings=(),
    )


def test_resolve_projectable_environment_returns_contract_and_report_when_valid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="profile",
            )
        }
    )

    monkeypatch.setattr(
        projection_validation,
        "load_resolved_contract_bundle",
        lambda _repo_root: _bundle_for(contract),
    )
    monkeypatch.setattr(
        projection_validation,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    resolved_contract, resolved_report, warnings = (
        projection_validation.resolve_projectable_environment(
            context,
            active_profile="staging",
            selection=None,
            operation="export",
        )
    )

    assert resolved_contract is contract
    assert resolved_report is report
    assert warnings == ()


def test_resolve_projectable_environment_raises_validation_error_with_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", groups=("Network",)),
            "API_URL": make_variable_spec(
                name="API_URL",
                groups=("Application",),
            ),
        }
    )
    report = make_resolution_report(
        values={
            "API_HOST": make_resolved_value(key="API_HOST", value="host"),
            "API_URL": make_resolved_value(
                key="API_URL",
                value="bad",
                valid=False,
                detail="broken",
            ),
        },
        invalid_keys=("API_URL",),
    )

    monkeypatch.setattr(
        projection_validation,
        "load_resolved_contract_bundle",
        lambda _repo_root: _bundle_for(contract),
    )
    monkeypatch.setattr(
        projection_validation,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    with pytest.raises(ValidationError) as exc_info:
        projection_validation.resolve_projectable_environment(
            context,
            active_profile="staging",
            selection=group_selection("Application"),
            operation="sync",
        )

    diagnostics = require_projection_validation_diagnostics(exc_info.value)
    assert diagnostics.operation == "sync"
    assert diagnostics.active_profile == "staging"
    assert diagnostics.selection.describe() == "group=Application"
    assert diagnostics.report.invalid_keys == ("API_URL",)
