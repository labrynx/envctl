from __future__ import annotations

import json

import pytest

from envctl.config.defaults import get_default_config_path, get_default_vault_dir
from envctl.config.loader import load_config
from envctl.errors import ConfigError
from envctl.services.config_service import run_config_init


def test_load_config_uses_defaults(isolated_env) -> None:
    config = load_config()
    assert config.env_filename == ".env.local"
    assert config.vault_dir == get_default_vault_dir()
    assert str(config.vault_dir).endswith(".envctl/vault")


def test_config_init_creates_default_config_file(isolated_env) -> None:
    config_path = run_config_init()

    assert config_path == get_default_config_path()
    assert config_path.exists()

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    assert raw["env_filename"] == ".env.local"
    assert raw["vault_dir"] == "~/.envctl/vault"

    resolved_vault_dir = load_config().vault_dir
    assert resolved_vault_dir == get_default_vault_dir()


def test_config_init_refuses_to_overwrite_existing_config(isolated_env) -> None:
    run_config_init()

    with pytest.raises(ConfigError):
        run_config_init()