from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.status_service as status_service
from envctl.errors import ContractError, ExecutionError
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_status_context


def test_run_status_reports_missing_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_status_context(tmp_path, contract_exists=False, vault_exists=False)

    monkeypatch.setattr(
        status_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )

    active_profile, report = status_service.run_status("local")

    assert active_profile == "local"
    assert report.project_slug == "demo"
    assert report.project_id == context.project_id
    assert report.contract_exists is False
    assert report.vault_exists is False
    assert report.resolved_valid is False
    assert report.summary == "The project is not ready because no contract file was found."
    assert report.issues == ["Contract file is missing"]
    assert report.suggested_action == "Create .envctl.yaml or run 'envctl add KEY VALUE'"


def test_run_status_reports_invalid_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_status_context(tmp_path, contract_exists=True, vault_exists=True)

    monkeypatch.setattr(
        status_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )

    def raise_contract_error(_context: object) -> object:
        raise ContractError("Contract is broken")

    monkeypatch.setattr(status_service, "load_contract_for_context", raise_contract_error)

    active_profile, report = status_service.run_status("local")

    assert active_profile == "local"
    assert report.contract_exists is True
    assert report.vault_exists is True
    assert report.resolved_valid is False
    assert report.summary == "The project contract is invalid."
    assert report.issues == ["Contract is broken"]
    assert report.suggested_action == "Fix the contract file"


def test_run_status_reports_valid_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_status_context(tmp_path, contract_exists=True, vault_exists=True)
    contract = object()
    resolution = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="vault",
                valid=True,
            )
        }
    )

    monkeypatch.setattr(
        status_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(status_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(
        status_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: resolution,
    )

    active_profile, report = status_service.run_status("local")

    assert active_profile == "local"
    assert report.contract_exists is True
    assert report.vault_exists is True
    assert report.resolved_valid is True
    assert report.issues == []
    assert report.suggested_action is None
    assert (
        report.summary
        == "The project contract is satisfied and the environment can be projected safely."
    )


def test_run_status_reports_missing_invalid_and_unknown_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_status_context(tmp_path, contract_exists=True, vault_exists=True)
    contract = object()
    resolution = make_resolution_report(
        values={
            "PORT": make_resolved_value(
                key="PORT",
                value="abc",
                source="vault",
                valid=False,
                detail="Expected an integer",
            )
        },
        missing_required=("APP_NAME", "DATABASE_URL"),
        unknown_keys=("OLD_KEY",),
        invalid_keys=("PORT",),
    )

    monkeypatch.setattr(
        status_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(status_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(
        status_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: resolution,
    )

    active_profile, report = status_service.run_status("local")

    assert active_profile == "local"
    assert report.resolved_valid is False
    assert report.summary == "The project contract is not satisfied yet."
    assert report.issues == [
        "Missing required keys: APP_NAME, DATABASE_URL",
        "Invalid values: PORT",
        "Unknown keys in vault: OLD_KEY",
    ]
    assert report.suggested_action == "Fix the invalid values in the local vault"


def test_run_status_fails_when_explicit_profile_file_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_status_context(tmp_path, contract_exists=True, vault_exists=True)
    contract = object()
    resolution = make_resolution_report()

    monkeypatch.setattr(
        status_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(status_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(
        status_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: resolution,
    )

    with pytest.raises(ExecutionError, match=r"Create it with 'envctl profile create staging'"):
        status_service.run_status("staging")
