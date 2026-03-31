"""Presenters for project commands."""

from __future__ import annotations

from pathlib import Path

from envctl.utils.output import print_kv, print_success, print_warning


def render_project_bind_result(
    *,
    changed: bool,
    display_name: str,
    project_key: str,
    project_id: str,
    binding_source: str,
    repo_root: Path,
    vault_dir: Path,
    vault_values_path: Path,
) -> None:
    """Render project bind output."""
    if changed:
        print_success(f"Bound repository to {display_name}")
    else:
        print_warning(f"Repository already bound to {display_name}")

    print_kv("project_key", project_key)
    print_kv("project_id", project_id)
    print_kv("binding_source", binding_source)
    print_kv("repo_root", str(repo_root))
    print_kv("vault_dir", str(vault_dir))
    print_kv("vault_values", str(vault_values_path))


def render_project_rebind_result(
    *,
    display_name: str,
    previous_project_id: str | None,
    new_project_id: str,
    copied_values: bool,
    repo_root: Path,
    vault_dir: Path,
    vault_values_path: Path,
) -> None:
    """Render project rebind output."""
    print_success(f"Rebound repository to {display_name}")

    if previous_project_id is not None:
        print_kv("previous_project_id", previous_project_id)

    print_kv("new_project_id", new_project_id)
    print_kv("copied_values", "yes" if copied_values else "no")
    print_kv("repo_root", str(repo_root))
    print_kv("vault_dir", str(vault_dir))
    print_kv("vault_values", str(vault_values_path))


def render_project_repair_result(
    *,
    status: str,
    detail: str,
    project_id: str | None,
    binding_source: str | None,
    repo_root: Path | None,
    vault_dir: Path | None,
    vault_values_path: Path | None,
) -> None:
    """Render project repair output."""
    if status in {"healthy", "repaired", "created", "recreated"}:
        print_success(detail)
    else:
        print_warning(detail)

    if project_id is not None:
        print_kv("project_id", project_id)
    if binding_source is not None:
        print_kv("binding_source", binding_source)
    if repo_root is not None:
        print_kv("repo_root", str(repo_root))
    if vault_dir is not None:
        print_kv("vault_dir", str(vault_dir))
    if vault_values_path is not None:
        print_kv("vault_values", str(vault_values_path))


def render_project_unbind_result(
    *,
    removed: bool,
    repo_root: Path,
    previous_project_id: str | None,
) -> None:
    """Render project unbind output."""
    if removed:
        print_success("Removed local repository binding")
    else:
        print_warning("No local repository binding was present")

    print_kv("repo_root", str(repo_root))
    if previous_project_id is not None:
        print_kv("previous_project_id", previous_project_id)
