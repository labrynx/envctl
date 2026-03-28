from __future__ import annotations

from types import SimpleNamespace

from envctl.services.fill_service import run_fill
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context
from tests.support.contracts import make_fill_contract


def test_run_fill_prompts_for_missing_required_keys_and_writes_file(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)
    contract = make_fill_contract()
    report = make_resolution_report(
        missing_required=["API_KEY", "PORT"],
    )

    written: dict[str, str] = {}
    permissions_called: list[str] = []
    prompts: list[tuple[str, bool, str | None]] = []

    def fake_prompt(message: str, sensitive: bool, default: str | None) -> str:
        prompts.append((message, sensitive, default))
        if message.startswith("API_KEY:"):
            return "secret-value"
        return ""

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.resolve_environment",
        lambda _context, _contract: report,
    )
    monkeypatch.setattr("envctl.services.fill_service.load_env_file", lambda _path: {})
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.ensure_private_file_permissions",
        lambda path: permissions_called.append(str(path)),
    )

    result_context, changed = run_fill(fake_prompt)

    assert result_context is context
    assert changed == ["API_KEY", "PORT"]

    assert prompts == [
        ("API_KEY: API key", True, None),
        ("PORT: Port number", False, "3000"),
    ]

    output = written[str(vault_values_path)]
    assert 'API_KEY="secret-value"' in output
    assert 'PORT="3000"' in output
    assert permissions_called == [str(vault_values_path)]


def test_run_fill_skips_blank_answers_without_defaults(monkeypatch, tmp_path) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)
    contract = make_fill_contract()
    report = make_resolution_report(missing_required=["API_KEY"])

    write_calls: list[str] = []

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.resolve_environment",
        lambda _context, _contract: report,
    )
    monkeypatch.setattr("envctl.services.fill_service.load_env_file", lambda _path: {})
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: write_calls.append(f"{path}:{content}"),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.ensure_private_file_permissions",
        lambda _path: None,
    )

    result_context, changed = run_fill(lambda _message, _sensitive, _default: "   ")

    assert result_context is context
    assert changed == []
    assert write_calls == []


def test_run_fill_preserves_existing_values_and_only_writes_changed_keys(
    monkeypatch, tmp_path
) -> None:
    vault_values_path = tmp_path / "vault.env"
    context = make_project_context(vault_values_path=vault_values_path)
    contract = make_fill_contract()
    report = make_resolution_report(
        values={
            "ALREADY_SET": make_resolved_value(
                key="ALREADY_SET",
                value="yes",
                source="vault",
                valid=True,
            )
        },
        missing_required=["API_KEY"],
    )

    written: dict[str, str] = {}

    monkeypatch.setattr(
        "envctl.services.fill_service.load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.resolve_environment",
        lambda _context, _contract: report,
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.load_env_file",
        lambda _path: {"ALREADY_SET": "yes"},
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.write_text_atomic",
        lambda path, content: written.update({str(path): content}),
    )
    monkeypatch.setattr(
        "envctl.services.fill_service.ensure_private_file_permissions",
        lambda _path: None,
    )

    _, changed = run_fill(lambda _message, _sensitive, _default: "new-secret")

    assert changed == ["API_KEY"]
    output = written[str(vault_values_path)]
    assert 'ALREADY_SET="yes"' in output
    assert 'API_KEY="new-secret"' in output
