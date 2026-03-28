from __future__ import annotations

from pathlib import Path

import envctl.utils.tilde as tilde_utils
from envctl.utils.masking import mask_value
from envctl.utils.project_names import resolve_project_name, slugify_project_name
from envctl.utils.tilde import to_tilde_path


def test_mask_value_returns_empty_string_for_empty_value() -> None:
    assert mask_value("") == ""


def test_mask_value_masks_short_values_fully() -> None:
    assert mask_value("a") == "*"
    assert mask_value("ab") == "**"
    assert mask_value("abcd") == "****"


def test_mask_value_preserves_edges_for_longer_values() -> None:
    assert mask_value("super-secret") == "su********et"


def test_slugify_project_name_normalizes_text() -> None:
    assert slugify_project_name(" My App ") == "my-app"
    assert slugify_project_name("hello___world") == "hello-world"
    assert slugify_project_name("a---b") == "a-b"


def test_slugify_project_name_falls_back_to_project() -> None:
    assert slugify_project_name("!!!") == "project"
    assert slugify_project_name("   ") == "project"


def test_resolve_project_name_prefers_explicit_name(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-name"
    repo_root.mkdir()

    assert resolve_project_name(repo_root, "My App") == "my-app"


def test_resolve_project_name_uses_repo_root_name_when_explicit_name_is_missing(tmp_path: Path) -> None:
    repo_root = tmp_path / "Repo Name"
    repo_root.mkdir()

    assert resolve_project_name(repo_root, None) == "repo-name"
    assert resolve_project_name(repo_root, "   ") == "repo-name"


def test_to_tilde_path_uses_home_prefix(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    target = home / ".envctl" / "vault"
    target.mkdir(parents=True)

    monkeypatch.setattr(tilde_utils.Path, "home", lambda: home)

    assert to_tilde_path(target) == "~/.envctl/vault"


def test_to_tilde_path_returns_absolute_path_when_outside_home(monkeypatch, tmp_path: Path) -> None:
    home = tmp_path / "home"
    outside = tmp_path / "outside"
    outside.mkdir()

    monkeypatch.setattr(tilde_utils.Path, "home", lambda: home)

    assert to_tilde_path(outside) == str(outside.resolve())