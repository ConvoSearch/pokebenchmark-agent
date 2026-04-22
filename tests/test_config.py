import pytest
from pokebenchmark_agent.config import RunConfig


def test_run_config_defaults():
    config = RunConfig(
        game="emerald",
        rom_path="/path/to/rom.gba",
        model_provider="claude",
        model_name="claude-3-5-sonnet-20241022",
    )
    assert config.game == "emerald"
    assert config.rom_path == "/path/to/rom.gba"
    assert config.model_provider == "claude"
    assert config.model_name == "claude-3-5-sonnet-20241022"
    assert config.input_mode == "vision"
    assert config.save_state_path is None
    assert config.save_file_path is None
    assert config.skill_files == []
    assert config.api_key is None
    assert config.api_base_url is None
    assert config.auto_save_interval == 50
    assert config.stuck_threshold == 20
    assert config.max_history == 30
    assert config.temperature == 1.0
    assert config.max_tokens == 4096
    assert config.orchestrator_url is None
    assert config.run_id is None


def test_run_config_text_only():
    config = RunConfig(
        game="firered",
        rom_path="/path/to/firered.gba",
        model_provider="openai",
        model_name="gpt-4o",
        input_mode="text",
    )
    assert config.input_mode == "text"
    assert config.game == "firered"


def test_run_config_invalid_game():
    with pytest.raises(ValueError):
        RunConfig(
            game="pokemon_red",
            rom_path="/path/to/rom.gba",
            model_provider="claude",
            model_name="claude-3-5-sonnet-20241022",
        )


def test_run_config_invalid_input_mode():
    with pytest.raises(ValueError):
        RunConfig(
            game="emerald",
            rom_path="/path/to/rom.gba",
            model_provider="claude",
            model_name="claude-3-5-sonnet-20241022",
            input_mode="audio",
        )


def test_run_config_workspace_dir_default():
    config = RunConfig(
        game="emerald", rom_path="/path/to/rom.gba",
        model_provider="claude", model_name="claude-sonnet-4-20250514",
    )
    assert config.workspace_dir == "./workspace"

def test_run_config_workspace_dir_custom():
    config = RunConfig(
        game="emerald", rom_path="/path/to/rom.gba",
        model_provider="claude", model_name="claude-sonnet-4-20250514",
        workspace_dir="/tmp/my_workspace",
    )
    assert config.workspace_dir == "/tmp/my_workspace"
