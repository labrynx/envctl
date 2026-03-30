from __future__ import annotations

import pytest

import envctl.services.sync_service as sync_service
from envctl.errors import ValidationError
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_run_sync_writes_generated_repo_env_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_env_path="/tmp/demo/.env.local")
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(key="APP_NAME", value="demo", source="profile"),
            "DATABASE_URL": make_resolved_value(
                key="DATABASE_URL",
                value="https://db.example.com",
                source="profile",
                masked=True,
            ),
        },
    )
    captured: dict[str, object] = {}

    monkeypatch.setattr(sync_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: object())
    monkeypatch.setattr(
        sync_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )
    monkeypatch.setattr(
        sync_service,
        "dump_env",
        lambda values, header=None: "rendered-env\n",
    )
    monkeypatch.setattr(
        sync_service,
        "write_text_atomic",
        lambda path, text: captured.update({"path": path, "text": text}),
    )

    _context, active_profile, target_path = sync_service.run_sync("staging")

    assert active_profile == "staging"
    assert target_path == context.repo_env_path
    assert captured["path"] == context.repo_env_path
    assert captured["text"] == "rendered-env\n"


def test_run_sync_rejects_invalid_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    report = make_resolution_report(missing_required=("DATABASE_URL",))

    monkeypatch.setattr(sync_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(sync_service, "load_contract_for_context", lambda _context: object())
    monkeypatch.setattr(
        sync_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    with pytest.raises(ValidationError, match="Environment contract is not satisfied"):
        sync_service.run_sync("dev")
