from __future__ import annotations

from pathlib import Path

import envctl.utils.permissions as permissions_utils
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions


def test_ensure_private_dir_permissions_applies_chmod(tmp_path: Path) -> None:
    target = tmp_path / "dir"
    target.mkdir()

    ensure_private_dir_permissions(target)

    assert (target.stat().st_mode & 0o777) == 0o700


def test_ensure_private_file_permissions_applies_chmod(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")

    ensure_private_file_permissions(target)

    assert (target.stat().st_mode & 0o777) == 0o600


def test_ensure_private_dir_permissions_ignores_oserror(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "dir"
    target.mkdir()

    def broken_chmod(self, mode: int) -> None:
        raise OSError("boom")

    monkeypatch.setattr(permissions_utils.Path, "chmod", broken_chmod)

    assert ensure_private_dir_permissions(target) is None


def test_ensure_private_file_permissions_ignores_oserror(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")

    def broken_chmod(self, mode: int) -> None:
        raise OSError("boom")

    monkeypatch.setattr(permissions_utils.Path, "chmod", broken_chmod)

    assert ensure_private_file_permissions(target) is None