from __future__ import annotations

import importlib
import sys
from types import ModuleType


def reload_envctl_init(monkeypatch, fake_version):
    import importlib.metadata

    monkeypatch.setattr(importlib.metadata, "version", fake_version)

    sys.modules.pop("envctl", None)
    module = importlib.import_module("envctl")
    return module


def test_package_init_uses_installed_version(monkeypatch) -> None:
    module = reload_envctl_init(monkeypatch, lambda name: "1.2.3")

    assert isinstance(module, ModuleType)
    assert module.__version__ == "1.2.3"
    assert module.__all__ == ["__version__"]


def test_package_init_falls_back_to_dev_version(monkeypatch) -> None:
    def raise_error(name: str) -> str:
        raise RuntimeError("version lookup failed")

    module = reload_envctl_init(monkeypatch, raise_error)

    assert module.__version__ == "0.0.0-dev"
    assert module.__all__ == ["__version__"]