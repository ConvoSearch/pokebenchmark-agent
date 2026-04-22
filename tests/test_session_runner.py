"""Tests for the in-container session runner."""
import os
import pytest
from unittest.mock import patch

from pokebenchmark_agent.session.runner import build_config_from_env, REQUIRED_ENV


FULL_ENV = {
    "GAME": "emerald",
    "ROM_PATH": "/roms/emerald.gba",
    "MODEL_PROVIDER": "claude",
    "MODEL_NAME": "claude-3-5-sonnet-20241022",
    "API_KEY": "sk-test-key",
    "INPUT_MODE": "vision",
    "RUN_ID": "run-abc-123",
    "ORCHESTRATOR_URL": "http://orchestrator:8080",
    "WORKSPACE_DIR": "/data/workspace",
    "SKILLS_DIR": "/data/skills",
    "AUTO_SAVE_INTERVAL": "25",
    "STUCK_THRESHOLD": "10",
    "MAX_HISTORY": "15",
    "STEPS": "100",
}


def _clear_env():
    """Remove all session-related env vars so tests don't leak."""
    for key in REQUIRED_ENV + ["SAVE_STATE_PATH"]:
        os.environ.pop(key, None)


def test_build_config_from_env():
    _clear_env()
    env = {**FULL_ENV, "SAVE_STATE_PATH": "/app/saves/my.ss"}
    with patch.dict("os.environ", env, clear=False):
        config = build_config_from_env()

    assert config.game == "emerald"
    assert config.rom_path == "/roms/emerald.gba"
    assert config.model_provider == "claude"
    assert config.model_name == "claude-3-5-sonnet-20241022"
    assert config.api_key == "sk-test-key"
    assert config.input_mode == "vision"
    assert config.save_state_path == "/app/saves/my.ss"
    assert config.run_id == "run-abc-123"
    assert config.orchestrator_url == "http://orchestrator:8080"
    assert config.workspace_dir == "/data/workspace"
    assert config.skills_dir == "/data/skills"
    assert config.auto_save_interval == 25
    assert config.stuck_threshold == 10
    assert config.max_history == 15


def test_build_config_from_env_text_mode():
    _clear_env()
    env = {**FULL_ENV, "GAME": "firered", "MODEL_PROVIDER": "openai", "MODEL_NAME": "gpt-4o", "INPUT_MODE": "text"}
    with patch.dict("os.environ", env, clear=False):
        config = build_config_from_env()

    assert config.game == "firered"
    assert config.input_mode == "text"
    assert config.model_provider == "openai"
    assert config.model_name == "gpt-4o"


def test_build_config_missing_env_raises():
    _clear_env()
    env = {"GAME": "emerald", "MODEL_PROVIDER": "gemini", "MODEL_NAME": "gemini-1.5-pro"}
    with patch.dict("os.environ", env, clear=False):
        with pytest.raises(RuntimeError, match="Missing required env vars"):
            build_config_from_env()


def test_save_state_path_is_optional():
    _clear_env()
    with patch.dict("os.environ", FULL_ENV, clear=False):
        config = build_config_from_env()
    assert config.save_state_path is None
