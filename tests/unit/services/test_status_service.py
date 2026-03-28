from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.status_service as status_service
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.errors import ContractError
from envctl.services.status_service import run_status


def make_context(
    tmp_path: Path,
    *,
    contract_exists: bool,
    vault_exists: bool,
) -> SimpleNamespace:
    repo_contract_path = tmp_path / ".envctl.schema.yaml"
    vault_values_path = tmp_path / "vault.env"

    if contract_exists:
        repo_contract_path.write_text("version: 1\nvariables:\n  APP_NAME: {}\n", encoding="utf-8")
    if vault_exists:
        vault_values_path.write_text('APP_NAME="demo"\n', encoding="utf-8")

    return SimpleNamespace(
        project_slug="demo",
        project_id="abc123",
        repo_root=tmp_path,
        repo_contract_path=repo_contract_path,
        vault_values_path=vault_values_path,
    )


def test_run_status_reports_missing_contract(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path, contract_exists=False, vault_exists=False)

    monkeypatch.setattr(status_service, "load_project_context", lambda: (SimpleNamespace(), context))

    report = run_status()

    assert report.project_slug == "demo"
    assert report.project_id == "abc123"
    assert report.contract_exists is False
    assert report.vault_exists is False
    assert report.resolved_valid is False
    assert report.summary == "The project is not ready because no contract file was found."
    assert report.issues == ["Contract file is missing"]
    assert report.suggested_action == "Create .envctl.schema.yaml"


def test_run_status_reports_invalid_contract(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path, contract_exists=True, vault_exists=True)

    monkeypatch.setattr(status_service, "load_project_context", lambda: (SimpleNamespace(), context))

    def raise_contract_error(_context):
        raise ContractError("Contract is broken")

    monkeypatch.setattr(status_service, "load_contract_for_context", raise_contract_error)

    report = run_status()

    assert report.contract_exists is True
    assert report.vault_exists is True
    assert report.resolved_valid is False
    assert report.summary == "The project contract is invalid."
    assert report.issues == ["Contract is broken"]
    assert report.suggested_action == "Fix the contract file"


def test_run_status_reports_valid_environment(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path, contract_exists=True, vault_exists=True)
    contract = object()
    resolution = ResolutionReport(
        values={
            "APP_NAME": ResolvedValue(
                key="APP_NAME",
                value="demo",
                source="vault",
                masked=False,
                valid=True,
                detail=None,
            )
        },
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )

    monkeypatch.setattr(status_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(status_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(status_service, "resolve_environment", lambda _context, _contract: resolution)

    report = run_status()

    assert report.contract_exists is True
    assert report.vault_exists is True
    assert report.resolved_valid is True
    assert report.issues == []
    assert report.suggested_action is None
    assert report.summary == "The project contract is satisfied and the environment can be projected safely."


def test_run_status_reports_missing_invalid_and_unknown_values(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path, contract_exists=True, vault_exists=True)
    contract = object()
    resolution = ResolutionReport(
        values={
            "PORT": ResolvedValue(
                key="PORT",
                value="abc",
                source="vault",
                masked=False,
                valid=False,
                detail="Expected an integer",
            )
        },
        missing_required=["APP_NAME", "DATABASE_URL"],
        unknown_keys=["OLD_KEY"],
        invalid_keys=["PORT"],
    )

    monkeypatch.setattr(status_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(status_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(status_service, "resolve_environment", lambda _context, _contract: resolution)

    report = run_status()

    assert report.resolved_valid is False
    assert report.summary == "The project contract is not satisfied yet."
    assert report.issues == [
        "Missing required keys: APP_NAME, DATABASE_URL",
        "Invalid values: PORT",
        "Unknown keys in vault: OLD_KEY",
    ]
    assert report.suggested_action == "Fix the invalid values in the local vault"