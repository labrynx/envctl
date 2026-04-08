"""Tests for profile presenters."""

from __future__ import annotations

from pathlib import Path

import pytest

from envctl.cli.presenters.profile_presenter import (
    render_profile_copy_result,
    render_profile_create_result,
    render_profile_list_result,
    render_profile_path_result,
    render_profile_remove_result,
)
from tests.support.paths import normalize_path_str


def test_render_profile_list_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render active profile and profile list."""
    render_profile_list_result(
        active_profile="local",
        profiles=("local", "prod", "staging"),
    )
    captured = capsys.readouterr().out

    assert "active_profile: local" in captured
    assert "profiles: local, prod, staging" in captured


def test_render_profile_create_result_created(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render created profile output."""
    render_profile_create_result(
        profile="prod",
        path=Path("/tmp/vault/profiles/prod.env"),
        created=True,
    )
    captured = normalize_path_str(capsys.readouterr().out)

    assert "[OK] Created profile 'prod'" in captured
    assert "profile: prod" in captured
    assert "path: /tmp/vault/profiles/prod.env" in captured


def test_render_profile_create_result_existing(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render existing profile warning."""
    render_profile_create_result(
        profile="prod",
        path=Path("/tmp/vault/profiles/prod.env"),
        created=False,
    )
    captured = capsys.readouterr().out

    assert "[WARN] Profile 'prod' already exists" in captured


def test_render_profile_copy_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render profile copy output."""
    render_profile_copy_result(
        source_profile="local",
        target_profile="prod",
        source_path=Path("/tmp/vault/values.env"),
        target_path=Path("/tmp/vault/profiles/prod.env"),
        copied_keys=5,
    )
    captured = normalize_path_str(capsys.readouterr().out)

    assert "[OK] Copied profile 'local' into 'prod'" in captured
    assert "source_profile: local" in captured
    assert "target_profile: prod" in captured
    assert "source_path: /tmp/vault/values.env" in captured
    assert "target_path: /tmp/vault/profiles/prod.env" in captured
    assert "copied_keys: 5" in captured


def test_render_profile_remove_result_removed(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render removed profile output."""
    render_profile_remove_result(
        profile="prod",
        path=Path("/tmp/vault/profiles/prod.env"),
        removed=True,
    )
    captured = normalize_path_str(capsys.readouterr().out)

    assert "[OK] Removed profile 'prod'" in captured
    assert "path: /tmp/vault/profiles/prod.env" in captured


def test_render_profile_remove_result_missing(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render missing profile warning."""
    render_profile_remove_result(
        profile="prod",
        path=Path("/tmp/vault/profiles/prod.env"),
        removed=False,
    )
    captured = normalize_path_str(capsys.readouterr().out)

    assert "[WARN] Profile 'prod' does not exist" in captured
    assert "path: /tmp/vault/profiles/prod.env" in captured


def test_render_profile_path_result(capsys: pytest.CaptureFixture[str]) -> None:
    """It should render profile path output."""
    render_profile_path_result(
        profile="staging",
        path=Path("/tmp/vault/profiles/staging.env"),
    )
    captured = normalize_path_str(capsys.readouterr().out)

    assert "profile: staging" in captured
    assert "path: /tmp/vault/profiles/staging.env" in captured
