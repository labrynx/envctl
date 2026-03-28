from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from envctl.errors import ProjectDetectionError
from envctl.services.doctor_service import run_doctor


def test_run_doctor_reports_ok_for_existing_private_vault_and_git_repo(
    monkeypatch, tmp_path: Path
) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: SimpleNamespace(
            config_path=tmp_path / "config.json",
            vault_dir=vault_dir,
        ),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: False,
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.resolve_repo_root",
        lambda: tmp_path / "repo",
    )

    checks = run_doctor()

    assert [(check.name, check.status) for check in checks] == [
        ("config", "ok"),
        ("vault", "ok"),
        ("vault_permissions", "ok"),
        ("git", "ok"),
    ]
    assert "Using config path:" in checks[0].detail
    assert "Using vault path:" in checks[1].detail
    assert "not world-writable" in checks[2].detail
    assert "Inside Git repository:" in checks[3].detail


def test_run_doctor_warns_when_vault_is_world_writable(monkeypatch, tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: SimpleNamespace(
            config_path=tmp_path / "config.json",
            vault_dir=vault_dir,
        ),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: True,
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.resolve_repo_root",
        lambda: tmp_path / "repo",
    )

    checks = run_doctor()

    assert checks[2].name == "vault_permissions"
    assert checks[2].status == "warn"
    assert "world-writable" in checks[2].detail


def test_run_doctor_warns_when_vault_does_not_exist(monkeypatch, tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: SimpleNamespace(
            config_path=tmp_path / "config.json",
            vault_dir=vault_dir,
        ),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.resolve_repo_root",
        lambda: tmp_path / "repo",
    )

    checks = run_doctor()

    assert checks[2].name == "vault_permissions"
    assert checks[2].status == "warn"
    assert "does not exist yet" in checks[2].detail


def test_run_doctor_warns_when_not_inside_git_repo(monkeypatch, tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: SimpleNamespace(
            config_path=tmp_path / "config.json",
            vault_dir=vault_dir,
        ),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: False,
    )

    def raise_not_repo():
        raise ProjectDetectionError("Not inside a Git repository")

    monkeypatch.setattr(
        "envctl.services.doctor_service.resolve_repo_root",
        raise_not_repo,
    )

    checks = run_doctor()

    assert checks[-1].name == "git"
    assert checks[-1].status == "warn"
    assert checks[-1].detail == "Not inside a Git repository"
