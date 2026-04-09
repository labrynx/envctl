from __future__ import annotations

import json
import re
from typing import Any

from typer.testing import CliRunner

from envctl.cli.app import app

_UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    flags=re.IGNORECASE,
)


def _prepare_valid_workspace(runner: CliRunner) -> None:
    runner.invoke(app, ["config", "init"], catch_exceptions=False)
    runner.invoke(app, ["init", "--contract", "starter"], catch_exceptions=False)
    runner.invoke(app, ["set", "APP_NAME", "demo"], catch_exceptions=False)
    runner.invoke(app, ["set", "PORT", "3000"], catch_exceptions=False)
    runner.invoke(app, ["set", "DATABASE_URL", "https://db.example.com"], catch_exceptions=False)


def _extract_json_trace_lines(output: str) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for line in output.splitlines():
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        payload = json.loads(candidate)
        if "event" in payload and "execution_id" in payload:
            lines.append(payload)
    return lines


def _normalize_human_trace(output: str) -> list[str]:
    normalized: list[str] = []
    for line in output.splitlines():
        if " status=" not in line and not line.startswith("Execution ID:"):
            continue
        line = _UUID_RE.sub("<execution-id>", line)
        line = re.sub(r"\[\d+ms\]", "[<ms>]", line)
        line = re.sub(r"Total \[\d+ms\]", "Total [<ms>]", line)
        line = re.sub(r" at .*", " at <timestamp>", line)
        normalized.append(line)
    return normalized


def test_trace_human_check_has_stable_core_shape(runner: CliRunner, workspace) -> None:
    del workspace
    _prepare_valid_workspace(runner)

    first = runner.invoke(
        app,
        ["--trace", "--trace-format", "human", "check"],
        catch_exceptions=False,
    )
    second = runner.invoke(
        app,
        ["--trace", "--trace-format", "human", "check"],
        catch_exceptions=False,
    )

    assert first.exit_code == 0
    assert second.exit_code == 0

    normalized_first = _normalize_human_trace(first.output)
    normalized_second = _normalize_human_trace(second.output)

    assert normalized_first
    assert normalized_first == normalized_second
    assert normalized_first[0] == "Execution ID: <execution-id> at <timestamp>"
    assert any("context.resolve" in line for line in normalized_first)
    assert any("resolution" in line for line in normalized_first)
    assert any(line.startswith("Total [<ms>] status=finish") for line in normalized_first)


def test_trace_json_emits_minimum_fields_and_event_sequence_stability(
    runner: CliRunner,
    workspace,
) -> None:
    del workspace
    _prepare_valid_workspace(runner)

    first = runner.invoke(
        app,
        ["--trace", "--trace-format", "jsonl", "check"],
        catch_exceptions=False,
    )
    second = runner.invoke(
        app,
        ["--trace", "--trace-format", "jsonl", "check"],
        catch_exceptions=False,
    )

    assert first.exit_code == 0
    assert second.exit_code == 0

    first_events = _extract_json_trace_lines(first.output)
    second_events = _extract_json_trace_lines(second.output)

    assert first_events
    assert second_events

    for payload in first_events:
        assert set(payload).issuperset(
            {
                "timestamp",
                "event",
                "execution_id",
                "status",
                "duration_ms",
                "module",
                "operation",
                "fields",
            }
        )
        assert isinstance(payload["fields"], dict)

    first_sequence = [(item["event"], item["status"]) for item in first_events]
    second_sequence = [(item["event"], item["status"]) for item in second_events]

    assert first_sequence == second_sequence
    assert first_sequence[0] == ("command.start", "start")
    assert first_sequence[-1] == ("command.finish", "finish")
