from __future__ import annotations

from types import SimpleNamespace

from envctl.domain.operations import FillPlanItem
from envctl.services.fill_service import apply_fill, build_fill_plan
from tests.support.builders import make_resolution_report
from tests.support.contexts import make_project_context
from tests.support.contracts import make_fill_contract


def test_build_fill_plan_returns_missing_required_keys_with_metadata(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)
    contract = make_fill_contract()
    report = make_resolution_report(
        missing_required=["API_KEY", "PORT"],
    )

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.resolve_environment",
        lambda _context, _contract: report,
    )

    result_context, plan = build_fill_plan()

    assert result_context is context
    assert plan == (
        FillPlanItem(
            key="API_KEY",
            description="API key",
            sensitive=True,
            default_value=None,
        ),
        FillPlanItem(
            key="PORT",
            description="Port number",
            sensitive=False,
            default_value="3000",
        ),
    )


def test_build_fill_plan_returns_empty_tuple_when_nothing_is_missing(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)
    contract = make_fill_contract()
    report = make_resolution_report(missing_required=[])

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.resolve_environment",
        lambda _context, _contract: report,
    )

    result_context, plan = build_fill_plan()

    assert result_context is context
    assert plan == ()


def test_apply_fill_writes_trimmed_values(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)

    written: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr("envctl.services.fill_service.load_env_file", lambda _path: {})
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )

    result_context, changed = apply_fill(
        {
            "API_KEY": "  secret-value  ",
            "PORT": "3000",
        }
    )

    assert result_context is context
    assert changed == ["API_KEY", "PORT"]

    output = written[str(vault_values_path)]
    assert "API_KEY=secret-value" in output
    assert "PORT=3000" in output


def test_apply_fill_skips_blank_values(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)

    write_calls: list[str] = []

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr("envctl.services.fill_service.load_env_file", lambda _path: {})
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: write_calls.append(f"{path}:{content}"),
    )

    result_context, changed = apply_fill(
        {
            "API_KEY": "   ",
            "PORT": "",
        }
    )

    assert result_context is context
    assert changed == []
    assert write_calls == []


def test_apply_fill_preserves_existing_values_and_only_writes_changed_keys(
    monkeypatch, tmp_path
) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)

    written: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_env_file",
        lambda _path: {"ALREADY_SET": "yes"},
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )

    result_context, changed = apply_fill({"API_KEY": "new-secret"})

    assert result_context is context
    assert changed == ["API_KEY"]

    output = written[str(vault_values_path)]
    assert "ALREADY_SET=yes" in output
    assert "API_KEY=new-secret" in output
