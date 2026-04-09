from __future__ import annotations

from pathlib import Path

import envctl.services.unbind_service as unbind_service


def test_run_unbind_returns_not_removed_when_no_binding_exists(
    monkeypatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(unbind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        unbind_service,
        "get_local_git_config",
        lambda _repo_root, _key: None,
    )

    result_repo_root, result = unbind_service.run_unbind()

    assert result_repo_root == repo_root
    assert result.removed is False
    assert result.previous_project_id is None


def test_run_unbind_removes_existing_binding(
    monkeypatch,
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    calls: list[tuple[Path, str]] = []

    monkeypatch.setattr(unbind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        unbind_service,
        "get_local_git_config",
        lambda _repo_root, _key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        unbind_service,
        "unset_local_git_config",
        lambda repo_root_arg, key: calls.append((repo_root_arg, key)),
    )

    result_repo_root, result = unbind_service.run_unbind()

    assert result_repo_root == repo_root
    assert result.removed is True
    assert result.previous_project_id == "prj_aaaaaaaaaaaaaaaa"
    assert calls
