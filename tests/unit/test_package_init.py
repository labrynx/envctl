from __future__ import annotations

import importlib.metadata
import sys
from collections.abc import Callable
from types import ModuleType

import pytest


def reload_envctl_init(
    monkeypatch: pytest.MonkeyPatch,
    fake_version: Callable[[str], str],
) -> ModuleType:
    monkeypatch.setattr(importlib.metadata, "version", fake_version)

    sys.modules.pop("envctl", None)
    module = importlib.import_module("envctl")
    assert isinstance(module, ModuleType)
    return module


def test_package_init_uses_installed_version(monkeypatch: pytest.MonkeyPatch) -> None:
    module = reload_envctl_init(monkeypatch, lambda name: "1.2.3")

    assert isinstance(module, ModuleType)
    assert module.__version__ == "1.2.3"
    assert module.__all__ == ["__version__"]


def test_package_init_falls_back_to_dev_version(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_error(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError("version lookup failed")

    module = reload_envctl_init(monkeypatch, raise_error)

    assert module.__version__ == "0.0.0-dev"
    assert module.__all__ == ["__version__"]
