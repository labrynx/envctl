from __future__ import annotations

import pytest

import envctl.services.remove_service as remove_service
from tests.support.contexts import make_project_context
from tests.support.contracts import make_standard_contract


def test_plan_remove_detects_other_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()

    def build_profile_path(profile: str) -> str:
        return "values.env" if profile == "local" else f"profiles/{profile}.env"

    monkeypatch.setattr(remove_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(remove_service, "load_contract", lambda path: contract)
    monkeypatch.setattr(
        remove_service,
        "list_persisted_profiles",
        lambda _context: ("local", "dev", "staging"),
    )
    monkeypatch.setattr(
        remove_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_project_dir / build_profile_path(profile),
            (
                {"APP_NAME": "demo"}
                if profile == "local"
                else {"APP_NAME": "demo-dev"}
                if profile == "dev"
                else {}
            ),
        ),
    )

    _context, plan = remove_service.plan_remove("APP_NAME", "local")

    assert plan.declared_in_contract is True
    assert plan.present_in_active_profile is True
    assert plan.present_in_other_profiles == ("dev",)
    assert plan.absent_in_other_profiles == ("staging",)


def test_run_remove_cleans_all_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()
    written_contracts: list[tuple[object, object]] = []

    def build_profile_path(profile: str) -> str:
        return "values.env" if profile == "local" else f"profiles/{profile}.env"

    monkeypatch.setattr(remove_service, "load_project_context", lambda: (object(), context))
    monkeypatch.setattr(remove_service, "load_contract", lambda path: contract)
    monkeypatch.setattr(
        remove_service,
        "write_contract",
        lambda path, contract_obj: written_contracts.append((path, contract_obj)),
    )
    monkeypatch.setattr(
        remove_service,
        "list_persisted_profiles",
        lambda _context: ("local", "dev", "staging"),
    )
    monkeypatch.setattr(
        remove_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_project_dir / build_profile_path(profile),
            (
                {"APP_NAME": "demo", "PORT": "3000"}
                if profile == "local"
                else {"APP_NAME": "demo-dev"}
                if profile == "dev"
                else {"PORT": "3000"}
            ),
        ),
    )
    monkeypatch.setattr(
        remove_service,
        "remove_key_from_profile",
        lambda context, profile, key: (
            profile,
            context.vault_project_dir / build_profile_path(profile),
            profile in {"local", "dev"},
        ),
    )

    _context, result = remove_service.run_remove("APP_NAME", "local")

    assert result.removed_from_contract is True
    assert result.inspected_profiles == ("local", "dev", "staging")
    assert result.removed_from_profiles == ("local", "dev")
    assert result.missing_from_profiles == ("staging",)
    assert len(result.affected_paths) == 2
    assert written_contracts[0][0] == context.repo_contract_path
