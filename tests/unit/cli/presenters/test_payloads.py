from __future__ import annotations

from pathlib import Path

from envctl.cli.presenters.payloads import optional_path_to_str, path_to_str


def test_path_to_str() -> None:
    path = Path("/tmp/demo")
    assert path_to_str(path) == "/tmp/demo"


def test_optional_path_to_str_none() -> None:
    assert optional_path_to_str(None) is None


def test_optional_path_to_str_value() -> None:
    path = Path("/tmp/demo")
    assert optional_path_to_str(path) == "/tmp/demo"
