from __future__ import annotations

from pathlib import Path

from envctl.utils.project_names import resolve_project_name, slugify_project_name


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


def test_resolve_project_name_uses_repo_root_name_when_explicit_name_is_missing(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "Repo Name"
    repo_root.mkdir()

    assert resolve_project_name(repo_root, None) == "repo-name"
    assert resolve_project_name(repo_root, "   ") == "repo-name"
