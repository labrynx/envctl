from __future__ import annotations

from pathlib import Path

import envctl.utils.filesystem as filesystem_utils
from envctl.utils.filesystem import ensure_dir, ensure_file, is_world_writable


def test_ensure_dir_creates_directory_and_returns_path(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir"

    result = ensure_dir(target)

    assert result == target
    assert target.exists()
    assert target.is_dir()


def test_ensure_file_creates_parent_and_file_with_default_content(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "file.txt"

    result = ensure_file(target)

    assert result == target
    assert target.exists()
    assert target.read_text(encoding="utf-8") == ""


def test_ensure_file_does_not_overwrite_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("original", encoding="utf-8")

    ensure_file(target, content="new-value")

    assert target.read_text(encoding="utf-8") == "original"


def test_is_world_writable_returns_true_when_other_write_bit_is_set(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")
    target.chmod(0o666)

    assert is_world_writable(target) is True


def test_is_world_writable_returns_false_when_other_write_bit_is_not_set(tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")
    target.chmod(0o644)

    assert is_world_writable(target) is False


def test_is_world_writable_returns_false_on_stat_error(monkeypatch, tmp_path: Path) -> None:
    target = tmp_path / "file.txt"
    target.write_text("x", encoding="utf-8")

    def broken_stat(self):
        raise OSError("boom")

    monkeypatch.setattr(filesystem_utils.Path, "stat", broken_stat)

    assert is_world_writable(target) is False
