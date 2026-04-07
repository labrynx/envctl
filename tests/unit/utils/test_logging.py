from __future__ import annotations

import io
import logging
from collections.abc import Generator
from typing import cast

import pytest

from envctl.utils import logging as logging_utils


@pytest.fixture(autouse=True)
def _reset_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, raising=False)


@pytest.fixture(autouse=True)
def _reset_envctl_logger() -> Generator[None, None, None]:
    logger = logging.getLogger("envctl")
    original_handlers = list(logger.handlers)
    original_level = logger.level
    original_propagate = logger.propagate

    for handler in list(logger.handlers):
        if getattr(handler, "_envctl_handler", False):
            logger.removeHandler(handler)
            handler.close()

    try:
        yield
    finally:
        for handler in list(logger.handlers):
            if handler not in original_handlers:
                logger.removeHandler(handler)
                handler.close()

        logger.handlers = original_handlers
        logger.setLevel(original_level)
        logger.propagate = original_propagate


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
    logger = logging.getLogger("envctl")
    monkeypatch.setenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, "DEBUG")

    logging_utils.ensure_logging_configured()

    assert logger.level == logging.DEBUG
    assert logger.propagate is False


def test_ensure_logging_configured_falls_back_for_invalid_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = logging.getLogger("envctl")
    monkeypatch.setenv(logging_utils.ENVCTL_LOG_LEVEL_ENVVAR, "trace")

    logging_utils.ensure_logging_configured()

    assert logger.level == logging.WARNING


def test_summarize_keys_truncates_long_lists() -> None:
    assert logging_utils.summarize_keys(["A", "B", "C"], limit=2) == "A, B, … (+1 more)"


def test_ensure_logging_configured_does_not_duplicate_handlers() -> None:
    logger = logging.getLogger("envctl")

    logging_utils.ensure_logging_configured()
    logging_utils.ensure_logging_configured()

    envctl_handlers = [
        handler for handler in logger.handlers if getattr(handler, "_envctl_handler", False)
    ]
    assert len(envctl_handlers) == 1


def test_formatter_only_includes_extra_context() -> None:
    stream = io.StringIO()
    logger = logging.getLogger("envctl")

    logging_utils.ensure_logging_configured()

    envctl_handler = next(
        handler for handler in logger.handlers if getattr(handler, "_envctl_handler", False)
    )
    stream_handler = cast(logging.StreamHandler[io.StringIO], envctl_handler)

    original_stream = stream_handler.stream
    stream_handler.setStream(stream)

    try:
        child_logger = logging_utils.get_logger("envctl.tests.logging")
        child_logger.warning("Hello", extra={"repo_root": "/tmp/repo"})
    finally:
        stream_handler.setStream(original_stream)

    rendered = stream.getvalue().strip()
    assert "repo_root=/tmp/repo" in rendered
    assert "message=" not in rendered
    assert "asctime=" not in rendered
