"""Presenters for profile commands."""

from __future__ import annotations

from pathlib import Path

from envctl.utils.output import print_kv, print_success, print_warning


def render_profile_list_result(*, active_profile: str, profiles: tuple[str, ...]) -> None:
    """Render profile list output."""
    print_kv("active_profile", active_profile)
    print_kv("profiles", ", ".join(profiles))


def render_profile_create_result(*, profile: str, path: Path, created: bool) -> None:
    """Render profile create output."""
    if created:
        print_success(f"Created profile '{profile}'")
    else:
        print_warning(f"Profile '{profile}' already exists")

    print_kv("profile", profile)
    print_kv("path", str(path))


def render_profile_copy_result(
    *,
    source_profile: str,
    target_profile: str,
    source_path: Path,
    target_path: Path,
    copied_keys: int,
) -> None:
    """Render profile copy output."""
    print_success(f"Copied profile '{source_profile}' into '{target_profile}'")
    print_kv("source_profile", source_profile)
    print_kv("target_profile", target_profile)
    print_kv("source_path", str(source_path))
    print_kv("target_path", str(target_path))
    print_kv("copied_keys", str(copied_keys))


def render_profile_remove_result(*, profile: str, path: Path, removed: bool) -> None:
    """Render profile remove output."""
    if removed:
        print_success(f"Removed profile '{profile}'")
    else:
        print_warning(f"Profile '{profile}' does not exist")

    print_kv("profile", profile)
    print_kv("path", str(path))


def render_profile_path_result(*, profile: str, path: Path) -> None:
    """Render profile path output."""
    print_kv("profile", profile)
    print_kv("path", str(path))
