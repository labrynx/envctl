from __future__ import annotations

import json
from pathlib import Path

import pytest

from envctl.config.loader import load_config, resolve_default_profile
from envctl.constants import ENVCTL_PROFILE_ENVVAR, ENVCTL_RUNTIME_MODE_ENVVAR
from envctl.domain.runtime import RuntimeMode
from envctl.errors import ConfigError
from tests.support.assertions import require_config_diagnostics


def _prepare_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Prepare an isolated HOME/XDG_CONFIG_HOME layout for config tests."""
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))

    return home


def test_load_config_uses_local_runtime_mode_by_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prepare_home(tmp_path, monkeypatch)

    config = load_config()

    assert config.runtime_mode == RuntimeMode.LOCAL
    assert config.default_profile == "local"


def test_load_config_reads_runtime_mode_from_config_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "runtime_mode": "ci",
            }
        ),
        encoding="utf-8",
    )

    config = load_config()

    assert config.runtime_mode == RuntimeMode.CI
    assert config.default_profile == "local"


def test_load_config_reads_default_profile_from_config_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "default_profile": "dev",
            }
        ),
        encoding="utf-8",
    )

    config = load_config()

    assert config.default_profile == "dev"


def test_load_config_environment_override_wins_over_config_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv(ENVCTL_RUNTIME_MODE_ENVVAR, "ci")

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "runtime_mode": "local",
            }
        ),
        encoding="utf-8",
    )

    config = load_config()

    assert config.runtime_mode == RuntimeMode.CI


def test_load_config_rejects_invalid_runtime_mode_in_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "runtime_mode": "banana",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Invalid runtime mode"):
        load_config()


def test_load_config_rejects_invalid_runtime_mode_in_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prepare_home(tmp_path, monkeypatch)
    monkeypatch.setenv(ENVCTL_RUNTIME_MODE_ENVVAR, "banana")

    with pytest.raises(ConfigError, match="Invalid runtime mode"):
        load_config()


def test_load_config_rejects_invalid_default_profile_in_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "default_profile": "",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="Invalid profile"):
        load_config()


def test_load_config_attaches_structured_diagnostics_for_invalid_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_json"
    assert diagnostics.path == config_path


def test_load_config_attaches_structured_diagnostics_for_invalid_shape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_config_shape"
    assert diagnostics.path == config_path
    assert diagnostics.field == "root"


def test_load_config_attaches_structured_diagnostics_for_unsupported_keys(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps({"oops": True}), encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "unsupported_keys"
    assert diagnostics.path == config_path
    assert diagnostics.key == "oops"


def test_load_config_attaches_structured_diagnostics_for_invalid_runtime_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps({"runtime_mode": "banana"}), encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_runtime_mode"
    assert diagnostics.path == config_path
    assert diagnostics.source_label == "config file"
    assert diagnostics.value == "'banana'"


def test_load_config_attaches_structured_diagnostics_for_invalid_default_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps({"default_profile": ""}), encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_default_profile"
    assert diagnostics.path == config_path
    assert diagnostics.key == "default_profile"
    assert diagnostics.source_label == "config file"


def test_load_config_attaches_structured_diagnostics_for_invalid_filename(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text(json.dumps({"env_filename": "nested/.env"}), encoding="utf-8")

    with pytest.raises(ConfigError) as exc_info:
        load_config()

    diagnostics = require_config_diagnostics(exc_info.value.diagnostics)
    assert diagnostics is not None
    assert diagnostics.category == "invalid_filename"
    assert diagnostics.path == config_path
    assert diagnostics.key == "env_filename"
    assert diagnostics.source_label == "config file"


def test_resolve_default_profile_uses_env_when_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prepare_home(tmp_path, monkeypatch)
    monkeypatch.setenv(ENVCTL_PROFILE_ENVVAR, "staging")

    assert resolve_default_profile() == "staging"


def test_resolve_default_profile_falls_back_to_config_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    home = _prepare_home(tmp_path, monkeypatch)
    config_dir = home / ".config" / "envctl"
    config_dir.mkdir(parents=True)

    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "default_profile": "dev",
            }
        ),
        encoding="utf-8",
    )

    assert resolve_default_profile() == "dev"


def test_resolve_default_profile_rejects_invalid_env_profile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _prepare_home(tmp_path, monkeypatch)
    monkeypatch.setenv(ENVCTL_PROFILE_ENVVAR, "bad/name")

    with pytest.raises(ConfigError, match="Invalid profile"):
        resolve_default_profile()
