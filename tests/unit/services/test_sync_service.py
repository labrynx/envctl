from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.sync_service as sync_service
from envctl.errors import ValidationError
from envctl.services.sync_service import run_sync
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_run_sync_writes_materialized_env_when_resolution_is_valid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_env_path = tmp_path / ".env.local"
    context = make_project_context(repo_env_path=repo_env_path)
    contract = object()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="vault",
                valid=True,
            ),
            "PORT": make_resolved_value(
                key="PORT",
                value="3000",
                source="default",
                valid=True,
            ),
        }
    )

    written: dict[str, str] = {}

    monkeypatch.setattr(
        sync_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(sync_service, "resolve_environment", lambda _context, _contract: report)
    monkeypatch.setattr(
        sync_service,
        "write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )

    result_context, result_report = run_sync()

    assert result_context == context
    assert result_report is report
    output = written[str(repo_env_path)]
    assert "APP_NAME=" in output
    assert "PORT=" in output


def test_run_sync_raises_when_environment_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    repo_env_path = tmp_path / ".env.local"
    context = make_project_context(repo_env_path=repo_env_path)
    contract = object()
    report = make_resolution_report(missing_required=("APP_NAME",))

    monkeypatch.setattr(
        sync_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(sync_service, "resolve_environment", lambda _context, _contract: report)

    with pytest.raises(
        ValidationError,
        match="Cannot sync because the resolved environment is invalid",
    ):
        run_sync()
