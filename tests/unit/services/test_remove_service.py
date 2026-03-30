from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.remove_service as remove_service
from tests.support.contexts import make_project_context
from tests.support.contracts import make_standard_contract


def test_plan_remove_detects_other_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()

    monkeypatch.setattr(remove_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(remove_service, "load_contract", lambda path: contract)
    monkeypatch.setattr(
        remove_service,
        "run_profile_list",
        lambda active_profile=None: (
            context,
            type("Result", (), {"profiles": ("local", "dev", "staging")})(),
        ),
    )

    def fake_load_env_file(path: Path) -> dict[str, str]:
        if str(path).endswith("values.env"):
            return {"APP_NAME": "demo"}
        if str(path).endswith("dev.env"):
            return {"APP_NAME": "demo-dev"}
        return {}

    monkeypatch.setattr(remove_service, "load_env_file", fake_load_env_file)

    _context, plan = remove_service.plan_remove("APP_NAME", "local")

    assert plan.declared_in_contract is True
    assert plan.present_in_active_profile is True
    assert plan.present_in_other_profiles == ("dev",)


def test_run_remove_cleans_all_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()
    written_contracts: list[tuple[Path, object]] = []
    writes: list[tuple[Path, dict[str, str]]] = []

    monkeypatch.setattr(remove_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(remove_service, "load_contract", lambda path: contract)
    monkeypatch.setattr(
        remove_service,
        "write_contract",
        lambda path, contract_obj: written_contracts.append((path, contract_obj)),
    )
    monkeypatch.setattr(
        remove_service,
        "run_profile_list",
        lambda active_profile=None: (
            context,
            type("Result", (), {"profiles": ("local", "dev", "staging")})(),
        ),
    )

    def fake_load_env_file(path: Path) -> dict[str, str]:
        if str(path).endswith("values.env"):
            return {"APP_NAME": "demo", "PORT": "3000"}
        if str(path).endswith("dev.env"):
            return {"APP_NAME": "demo-dev"}
        if str(path).endswith("staging.env"):
            return {"PORT": "3000"}
        return {}

    monkeypatch.setattr(remove_service, "load_env_file", fake_load_env_file)
    monkeypatch.setattr(
        remove_service,
        "_write_profile_values",
        lambda path, values: writes.append((path, values)),
    )

    _context, result = remove_service.run_remove("APP_NAME", "local")

    assert result.removed_from_contract is True
    assert result.removed_from_profiles == ("local", "dev")
    assert len(result.affected_paths) == 2
    assert written_contracts[0][0] == context.repo_contract_path
