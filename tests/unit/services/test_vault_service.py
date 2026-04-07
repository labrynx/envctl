from __future__ import annotations

from types import SimpleNamespace

import pytest

import envctl.services.vault_service as vault_service
from tests.support.contexts import make_project_context
from tests.support.contracts import make_standard_contract


def test_run_vault_path_returns_explicit_profile_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    expected = context.vault_project_dir / "profiles" / "staging.env"

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: (SimpleNamespace(encryption_strict=False), context),
    )
    monkeypatch.setattr(
        vault_service,
        "require_persisted_profile",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
        ),
    )

    _context, active_profile, path = vault_service.run_vault_path("staging")

    assert active_profile == "staging"
    assert path == expected


def test_run_vault_show_returns_missing_file_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    expected = context.vault_values_path

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: (SimpleNamespace(encryption_strict=False), context),
    )
    monkeypatch.setattr(
        vault_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False, allow_plaintext=True: (
            profile,
            context.vault_values_path,
            {},
        ),
    )

    _context, active_profile, result = vault_service.run_vault_show("local")

    assert active_profile == "local"
    assert result.exists is False
    assert result.path == expected
    assert result.values == {}


def test_get_unknown_vault_keys_uses_active_profile_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: (SimpleNamespace(encryption_strict=False), context),
    )
    monkeypatch.setattr(
        vault_service,
        "load_contract_optional",
        lambda path: contract,
    )
    monkeypatch.setattr(
        vault_service,
        "require_persisted_profile",
        lambda context, profile: (profile, context.vault_project_dir / "profiles" / "dev.env"),
    )
    monkeypatch.setattr(
        vault_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False, allow_plaintext=True: (
            profile,
            context.vault_project_dir / "profiles" / "dev.env",
            {"APP_NAME": "demo", "UNKNOWN": "x"},
        ),
    )

    _context, active_profile, path, unknown_keys = vault_service.get_unknown_vault_keys("dev")

    assert active_profile == "dev"
    assert path == context.vault_project_dir / "profiles" / "dev.env"
    assert unknown_keys == ("UNKNOWN",)


def test_run_vault_prune_removes_unknown_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_standard_contract()
    written: dict[str, object] = {}

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: (SimpleNamespace(encryption_strict=False), context),
    )
    monkeypatch.setattr(
        vault_service,
        "load_contract_optional",
        lambda path: contract,
    )
    monkeypatch.setattr(
        vault_service,
        "require_persisted_profile",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
        ),
    )
    monkeypatch.setattr(
        vault_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False, allow_plaintext=True: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
            {"APP_NAME": "demo", "UNKNOWN": "x", "PORT": "3000"},
        ),
    )
    monkeypatch.setattr(
        vault_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
            profile,
            written.update(
                {
                    "path": context.vault_project_dir / "profiles" / "staging.env",
                    "values": values,
                }
            )
            or context.vault_project_dir / "profiles" / "staging.env",
        ),
    )

    _context, active_profile, path, result = vault_service.run_vault_prune("staging")

    assert active_profile == "staging"
    assert path == context.vault_project_dir / "profiles" / "staging.env"
    assert result.removed_keys == ("UNKNOWN",)
    assert result.kept_keys == 2
    assert written["values"] == {
        "APP_NAME": "demo",
        "PORT": "3000",
    }


def test_run_vault_edit_uses_active_profile_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    opened: dict[str, object] = {}

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: (SimpleNamespace(encryption_strict=False), context),
    )
    monkeypatch.setattr(
        vault_service,
        "require_persisted_profile",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
        ),
    )
    monkeypatch.setattr(
        "envctl.services.vault_service.editor_adapter.open_file",
        lambda path: opened.update({"path": path}),
    )
    monkeypatch.setattr(
        vault_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
        ),
    )
    monkeypatch.setattr(
        vault_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False, allow_plaintext=True: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
            {},
        ),
    )

    _context, result = vault_service.run_vault_edit("staging")

    assert result.profile == "staging"
    assert str(result.path).endswith("/profiles/staging.env")
    assert opened["path"] == str(result.path)
