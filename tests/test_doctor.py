from __future__ import annotations

import json
import os

from envctl.services.doctor_service import run_doctor


def test_doctor_uses_ok_when_config_file_is_missing(isolated_env) -> None:
    checks = run_doctor()
    config_check = next(check for check in checks if check.name == "config")

    assert config_check.status == "ok"
    assert "using defaults" in config_check.detail.lower()


def test_doctor_reports_vault_path_as_warn_when_missing(isolated_env) -> None:
    checks = run_doctor()
    vault_check = next(check for check in checks if check.name == "vault_path")

    assert vault_check.status == "warn"
    assert "has not been created yet" in vault_check.detail.lower()


def test_doctor_reports_vault_permissions_as_warn_when_vault_is_missing(isolated_env) -> None:
    checks = run_doctor()
    permissions_check = next(check for check in checks if check.name == "vault_permissions")

    assert permissions_check.status == "warn"
    assert "cannot be checked" in permissions_check.detail.lower()


def test_doctor_reports_repo_detection_warn_outside_git_repo(
    isolated_env, tmp_path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)

    checks = run_doctor()
    repo_check = next(check for check in checks if check.name == "repo_detection")

    assert repo_check.status == "warn"
    assert "no git repository detected" in repo_check.detail.lower()


def test_doctor_reports_repo_detection_ok_inside_git_repo(
    isolated_env, repo_dir, monkeypatch
) -> None:
    monkeypatch.chdir(repo_dir)

    checks = run_doctor()
    repo_check = next(check for check in checks if check.name == "repo_detection")

    assert repo_check.status == "ok"
    assert str(repo_dir) in repo_check.detail


def test_doctor_reports_invalid_config_as_fail(isolated_env, tmp_path, monkeypatch) -> None:
    config_dir = tmp_path / "config" / "envctl"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text("{ invalid json", encoding="utf-8")

    checks = run_doctor()
    config_check = next(check for check in checks if check.name == "config")

    assert config_check.status == "fail"
    assert "invalid json config" in config_check.detail.lower()


def test_doctor_reports_valid_config_as_ok(isolated_env, tmp_path) -> None:
    config_dir = tmp_path / "config" / "envctl"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "vault_dir": str(tmp_path / "custom-vault"),
                "env_filename": ".env.local",
            }
        ),
        encoding="utf-8",
    )

    checks = run_doctor()
    config_check = next(check for check in checks if check.name == "config")

    assert config_check.status == "ok"
    assert "using config file" in config_check.detail.lower()


def test_doctor_reports_fail_when_vault_is_world_writable(
    isolated_env,
    tmp_path,
) -> None:
    vault_dir = tmp_path / "custom-vault"
    vault_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(vault_dir, 0o777)

    config_dir = tmp_path / "config" / "envctl"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.json").write_text(
        json.dumps(
            {
                "vault_dir": str(vault_dir),
                "env_filename": ".env.local",
            }
        ),
        encoding="utf-8",
    )

    checks = run_doctor()
    permissions_check = next(check for check in checks if check.name == "vault_permissions")

    assert permissions_check.status == "fail"
    assert "world-writable" in permissions_check.detail.lower()


def test_doctor_includes_symlink_support_check(isolated_env) -> None:
    checks = run_doctor()
    symlink_check = next(check for check in checks if check.name == "symlink_support")

    assert symlink_check.status in {"ok", "fail"}
