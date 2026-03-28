from __future__ import annotations

import pytest

from envctl.errors import ProjectDetectionError, ValidationError
from envctl.services.init_service import run_init
from envctl.services.set_service import run_set


def test_set_adds_new_key_to_managed_vault_env(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    result = run_set("APP_ENV", "development")

    assert result.project_slug == context.project_slug
    assert result.vault_env_path.exists()
    assert result.vault_env_path.read_text(encoding="utf-8") == (
        "# Managed by envctl\nAPP_ENV=development\n"
    )


def test_set_updates_existing_key_in_managed_vault_env(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.write_text(
        "# Managed by envctl\nAPP_ENV=development\n",
        encoding="utf-8",
    )

    run_set("APP_ENV", "production")

    assert context.vault_env_path.read_text(encoding="utf-8") == (
        "# Managed by envctl\nAPP_ENV=production\n"
    )


def test_set_preserves_comments_and_unrelated_keys(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.write_text(
        "# Managed by envctl\n# Existing comment\nAPP_ENV=development\nDEBUG=true\n",
        encoding="utf-8",
    )

    run_set("APP_ENV", "staging")

    assert context.vault_env_path.read_text(encoding="utf-8") == (
        "# Managed by envctl\n# Existing comment\nAPP_ENV=staging\nDEBUG=true\n"
    )


def test_set_requires_initialized_repository(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)

    with pytest.raises(ProjectDetectionError):
        run_set("APP_ENV", "development")


def test_set_fails_when_managed_vault_env_is_missing(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.unlink()

    with pytest.raises(ProjectDetectionError):
        run_set("APP_ENV", "development")


def test_set_rejects_empty_key(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    run_init()

    with pytest.raises(ValidationError):
        run_set("", "development")


def test_set_rejects_invalid_key_with_equals(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    run_init()

    with pytest.raises(ValidationError):
        run_set("APP=ENV", "development")


def test_set_rejects_invalid_key_format(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    run_init()

    with pytest.raises(ValidationError):
        run_set("1INVALID", "development")

    with pytest.raises(ValidationError):
        run_set("INVALID-KEY", "development")


def test_set_rejects_multiline_value(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    run_init()

    with pytest.raises(ValidationError):
        run_set("APP_ENV", "line1\nline2")


def test_set_allows_equals_and_spaces_in_value(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    run_set("DATABASE_URL", "postgres://user:pass@host/db?sslmode=disable")
    run_set("APP_NAME", "My Local App")

    assert context.vault_env_path.read_text(encoding="utf-8") == (
        "# Managed by envctl\n"
        "DATABASE_URL=postgres://user:pass@host/db?sslmode=disable\n"
        "APP_NAME=My Local App\n"
    )
