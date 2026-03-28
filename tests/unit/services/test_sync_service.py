from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import envctl.services.sync_service as sync_service
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.errors import ValidationError
from envctl.services.sync_service import run_sync


def test_run_sync_writes_materialized_env_when_resolution_is_valid(monkeypatch, tmp_path: Path) -> None:
    repo_env_path = tmp_path / ".env.local"
    context = SimpleNamespace(repo_env_path=repo_env_path)
    contract = object()
    report = ResolutionReport(
        values={
            "APP_NAME": ResolvedValue(
                key="APP_NAME",
                value="demo",
                source="vault",
                masked=False,
                valid=True,
                detail=None,
            ),
            "PORT": ResolvedValue(
                key="PORT",
                value="3000",
                source="default",
                masked=False,
                valid=True,
                detail=None,
            ),
        },
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )

    written: dict[str, str] = {}

    monkeypatch.setattr(sync_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(sync_service, "resolve_environment", lambda _context, _contract: report)
    monkeypatch.setattr(
        sync_service,
        "write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )

    result_context, result_report = run_sync()

    assert result_context is context
    assert result_report is report
    output = written[str(repo_env_path)]
    assert "APP_NAME=" in output
    assert "PORT=" in output


def test_run_sync_raises_when_environment_is_invalid(monkeypatch, tmp_path: Path) -> None:
    repo_env_path = tmp_path / ".env.local"
    context = SimpleNamespace(repo_env_path=repo_env_path)
    contract = object()
    report = ResolutionReport(
        values={},
        missing_required=["APP_NAME"],
        unknown_keys=[],
        invalid_keys=[],
    )

    monkeypatch.setattr(sync_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(sync_service, "resolve_environment", lambda _context, _contract: report)

    with pytest.raises(ValidationError, match="Cannot sync because the resolved environment is invalid"):
        run_sync()