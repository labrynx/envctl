from __future__ import annotations

from pathlib import Path

import pytest

import envctl.utils.tilde as tilde_utils


def normalize_path_str(value: str) -> str:
    """Normalize path separators for assertions."""
    return value.replace("\\", "/")


def test_to_tilde_path_uses_home_prefix(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    target = home / ".envctl" / "vault"
    target.mkdir(parents=True)

    monkeypatch.setattr(Path, "home", lambda: home)

    assert normalize_path_str(tilde_utils.to_tilde_path(target)) == "~/.envctl/vault"


def test_to_tilde_path_returns_absolute_path_when_outside_home(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    home = tmp_path / "home"
    outside = tmp_path / "outside"
    outside.mkdir()

    monkeypatch.setattr(Path, "home", lambda: home)

    assert normalize_path_str(tilde_utils.to_tilde_path(outside)) == normalize_path_str(
        str(outside.resolve())
    )
