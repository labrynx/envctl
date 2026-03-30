from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from envctl.errors import ProjectDetectionError
from envctl.services.doctor_service import run_doctor


def make_config(tmp_path: Path, vault_dir: Path) -> SimpleNamespace:
    return SimpleNamespace(
        config_path=tmp_path / "config.json",
        vault_dir=vault_dir,
        projects_dir=vault_dir / "projects",
        env_filename=".env.local",
        schema_filename=".envctl.schema.yaml",
    )


def test_run_doctor_reports_ok_for_existing_private_vault_and_git_repo(
    monkeypatch, tmp_path: Path
) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    repo_contract_path = tmp_path / "repo" / ".envctl.schema.yaml"
    repo_contract_path.parent.mkdir(parents=True, exist_ok=True)
    repo_contract_path.write_text("version: 1\nvariables: {}\n", encoding="utf-8")

    vault_state_path = tmp_path / "vault" / "projects" / "demo--prj_aaaaaaaaaaaaaaaa" / "state.json"
    vault_state_path.parent.mkdir(parents=True, exist_ok=True)
    vault_state_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: make_config(tmp_path, vault_dir),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: False,
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        lambda config: SimpleNamespace(
            project_slug="demo",
            project_key="demo",
            project_id="prj_aaaaaaaaaaaaaaaa",
            binding_source="local",
            repo_contract_path=repo_contract_path,
            vault_state_path=vault_state_path,
        ),
    )

    checks = run_doctor()

    assert [(check.name, check.status) for check in checks] == [
        ("config", "ok"),
        ("vault", "ok"),
        ("vault_permissions", "ok"),
        ("project", "ok"),
        ("binding_source", "ok"),
        ("binding", "ok"),
        ("contract", "ok"),
        ("state", "ok"),
    ]
    assert "Using config path:" in checks[0].detail
    assert "Using vault path:" in checks[1].detail
    assert "not world-writable" in checks[2].detail
    assert "Resolved project:" in checks[3].detail
    assert "Binding source:" in checks[4].detail
    assert "Local git binding present" in checks[5].detail
    assert "Contract found:" in checks[6].detail
    assert "Vault state found:" in checks[7].detail


def test_run_doctor_warns_when_vault_is_world_writable(monkeypatch, tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: make_config(tmp_path, vault_dir),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: True,
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        lambda config: SimpleNamespace(
            project_slug="demo",
            project_key="demo",
            project_id="prj_aaaaaaaaaaaaaaaa",
            binding_source="local",
            repo_contract_path=tmp_path / "repo" / ".envctl.schema.yaml",
            vault_state_path=tmp_path
            / "vault"
            / "projects"
            / "demo--prj_aaaaaaaaaaaaaaaa"
            / "state.json",
        ),
    )

    checks = run_doctor()

    assert checks[2].name == "vault_permissions"
    assert checks[2].status == "warn"
    assert "world-writable" in checks[2].detail


def test_run_doctor_warns_when_vault_does_not_exist(monkeypatch, tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: make_config(tmp_path, vault_dir),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        lambda config: SimpleNamespace(
            project_slug="demo",
            project_key="demo",
            project_id="prj_aaaaaaaaaaaaaaaa",
            binding_source="local",
            repo_contract_path=tmp_path / "repo" / ".envctl.schema.yaml",
            vault_state_path=tmp_path
            / "vault"
            / "projects"
            / "demo--prj_aaaaaaaaaaaaaaaa"
            / "state.json",
        ),
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
        lambda: make_config(tmp_path, vault_dir),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.is_world_writable",
        lambda _path: False,
    )

    def raise_not_repo(config):
        raise ProjectDetectionError("Not inside a Git repository")

    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        raise_not_repo,
    )

    checks = run_doctor()

    assert checks[-1].name == "project"
    assert checks[-1].status == "warn"
    assert checks[-1].detail == "Not inside a Git repository"
