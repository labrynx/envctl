from __future__ import annotations

from types import SimpleNamespace

import envctl.services.resolution_service as resolution_service
from envctl.domain.contract import Contract, VariableSpec
from envctl.services.resolution_service import resolve_environment


def test_resolve_environment_marks_unsupported_type_as_invalid(monkeypatch) -> None:
    contract = Contract(
        version=1,
        variables={
            "WEIRD": VariableSpec(
                name="WEIRD",
                type="mystery",
                required=True,
                description="",
                sensitive=False,
                default=None,
                provider=None,
                example=None,
                pattern=None,
                choices=(),
            ),
        },
    )
    context = SimpleNamespace(vault_values_path="/tmp/vault.env")

    monkeypatch.setattr(
        resolution_service,
        "load_env_file",
        lambda _path: {"WEIRD": "value"},
    )

    report = resolve_environment(context, contract)

    assert report.invalid_keys == ["WEIRD"]
    assert report.values["WEIRD"].valid is False
    assert report.values["WEIRD"].detail == "Unsupported type: mystery"