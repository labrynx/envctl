from __future__ import annotations

import logging

import pytest

from envctl.utils import logging as logging_utils


@pytest.fixture(autouse=True)
def _reset_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, raising=False)


def test_mask_value_for_log_masks_sensitive_values() -> None:
    assert logging_utils.mask_value_for_log("supersecret") == "su*********"


def test_mask_value_for_log_keeps_non_sensitive_values() -> None:
    assert logging_utils.mask_value_for_log("visible", sensitive=False) == "visible"


def test_sanitize_command_for_log_masks_sensitive_assignments() -> None:
    sanitized = logging_utils.sanitize_command_for_log(
        ["docker", "run", "API_KEY=supersecret", "PASSWORD=hunter2", "plain=value"]
    )

    assert sanitized == (
        "docker",
        "run",
        "API_KEY=su*********",
        "PASSWORD=hu*****",
        "plain=value",
    )


def test_ensure_logging_configured_honors_env_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = logging.getLogger()
    original_level = root.level
    monkeypatch.setenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, "DEBUG")

    try:
        logging_utils.ensure_logging_configured()
        assert root.level == logging.DEBUG
    finally:
        root.setLevel(original_level)


def test_ensure_logging_configured_falls_back_for_invalid_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = logging.getLogger()
    original_level = root.level
    monkeypatch.setenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, "trace")

    try:
        logging_utils.ensure_logging_configured()
        assert root.level == logging.WARNING
    finally:
        root.setLevel(original_level)


def test_summarize_keys_truncates_long_lists() -> None:
    assert logging_utils.summarize_keys(["A", "B", "C"], limit=2) == "A, B, … (+1 more)"
