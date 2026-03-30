from __future__ import annotations

from pathlib import Path

import pytest

from envctl.domain.project import BindingSource, ProjectContext
from envctl.errors import ProjectDetectionError
from envctl.services.doctor_service import run_doctor
from tests.support.contexts import make_project_context


def make_context(
    tmp_path: Path,
    *,
    binding_source: BindingSource = "local",
    contract_exists: bool = True,
    state_exists: bool = True,
    create_vault_project_dir: bool = True,
) -> ProjectContext:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_project_dir = tmp_path / "vault" / "projects" / "demo--prj_aaaaaaaaaaaaaaaa"
    if create_vault_project_dir:
        vault_project_dir.mkdir(parents=True, exist_ok=True)

    repo_contract_path = repo_root / ".envctl.schema.yaml"
    if contract_exists:
        repo_contract_path.write_text("version: 1\nvariables: {}\n", encoding="utf-8")

    vault_state_path = vault_project_dir / "state.json"
    if state_exists:
        vault_project_dir.mkdir(parents=True, exist_ok=True)
        vault_state_path.write_text("{}", encoding="utf-8")

    return make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_remote=None,
        binding_source=binding_source,
        repo_contract_path=repo_contract_path,
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_project_dir / "values.env",
        vault_state_path=vault_state_path,
    )


def make_config(tmp_path: Path, vault_dir: Path) -> object:
    class ConfigStub:
        def __init__(self) -> None:
            self.config_path = tmp_path / "config.json"
            self.vault_dir = vault_dir
            self.projects_dir = vault_dir / "projects"
            self.env_filename = ".env.local"
            self.schema_filename = ".envctl.schema.yaml"

    return ConfigStub()


def test_run_doctor_reports_ok_for_existing_private_vault_and_git_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    context = make_context(
        tmp_path,
        binding_source="local",
        contract_exists=True,
        state_exists=True,
    )

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
        lambda config: context,
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


def test_run_doctor_warns_when_vault_is_world_writable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    context = make_context(
        tmp_path,
        binding_source="local",
        contract_exists=False,
        state_exists=False,
    )

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
        lambda config: context,
    )

    checks = run_doctor()

    assert checks[2].name == "vault_permissions"
    assert checks[2].status == "warn"
    assert "world-writable" in checks[2].detail


def test_run_doctor_warns_when_vault_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    vault_dir = tmp_path / "vault"
    context = make_context(
        tmp_path,
        binding_source="local",
        contract_exists=False,
        state_exists=False,
        create_vault_project_dir=False,
    )

    monkeypatch.setattr(
        "envctl.services.doctor_service.load_config",
        lambda: make_config(tmp_path, vault_dir),
    )
    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        lambda config: context,
    )

    checks = run_doctor()

    assert checks[2].name == "vault_permissions"
    assert checks[2].status == "warn"
    assert "does not exist yet" in checks[2].detail


def test_run_doctor_warns_when_not_inside_git_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
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

    def raise_not_repo(config: object) -> ProjectContext:
        raise ProjectDetectionError("Not inside a Git repository")

    monkeypatch.setattr(
        "envctl.services.doctor_service.build_project_context",
        raise_not_repo,
    )

    checks = run_doctor()

    assert checks[-1].name == "project"
    assert checks[-1].status == "warn"
    assert checks[-1].detail == "Not inside a Git repository"
