from __future__ import annotations

from typing import Any, cast

import pytest
import typer

import envctl.cli.commands.doctor.command as doctor_command_module
from envctl.cli.commands.doctor import doctor_command
from envctl.domain.doctor import DoctorCheck


def test_doctor_command_exits_with_code_1_when_failures_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda: ["dummy-check"],
    )
    monkeypatch.setattr(
        doctor_command_module,
        "render_doctor_checks",
        lambda checks: True,
    )
    monkeypatch.setattr(
        doctor_command_module,
        "is_json_output",
        lambda: False,
    )

    with pytest.raises(typer.Exit) as exc_info:
        doctor_command()

    assert exc_info.value.exit_code == 1


def test_doctor_command_returns_normally_when_no_failures_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda: ["dummy-check"],
    )
    monkeypatch.setattr(
        doctor_command_module,
        "render_doctor_checks",
        lambda checks: False,
    )
    monkeypatch.setattr(
        doctor_command_module,
        "is_json_output",
        lambda: False,
    )

    assert doctor_command() is None


def test_doctor_command_emits_json_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda: [
            DoctorCheck("config", "ok", "config ok"),
            DoctorCheck("vault", "warn", "vault warn"),
        ],
    )
    monkeypatch.setattr(
        doctor_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        doctor_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    doctor_command()

    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is True
    assert payload["command"] == "doctor"
    assert payload["data"]["has_failures"] is False
    assert len(payload["data"]["checks"]) == 2


def test_doctor_command_emits_json_and_exits_when_failures_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        doctor_command_module,
        "run_doctor",
        lambda: [
            DoctorCheck("git", "fail", "git fail"),
        ],
    )
    monkeypatch.setattr(
        doctor_command_module,
        "is_json_output",
        lambda: True,
    )
    monkeypatch.setattr(
        doctor_command_module,
        "emit_json",
        lambda payload: captured.update({"payload": payload}),
    )

    with pytest.raises(typer.Exit) as exc_info:
        doctor_command()

    assert exc_info.value.exit_code == 1
    payload = cast(dict[str, Any], captured["payload"])
    assert payload["ok"] is False
    assert payload["data"]["has_failures"] is True
