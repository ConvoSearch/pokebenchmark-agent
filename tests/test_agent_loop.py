"""Tests for AgentLoop (Tasks 12-13)."""
import pytest
from unittest.mock import MagicMock, patch, call

from pokebenchmark_emulator.adapters.base import GameState
from pokebenchmark_agent.agent.loop import AgentLoop
from pokebenchmark_agent.agent.stuck_detector import StuckDetector
from pokebenchmark_agent.agent.context import ContextBuilder
from pokebenchmark_agent.config import RunConfig
from pokebenchmark_agent.llm.response import AgentResponse


def make_game_state(**overrides):
    defaults = dict(
        player_name="ASH",
        location="Littleroot Town",
        x=5,
        y=10,
        facing="up",
        badges=[],
        money=3000,
        party=[{"species": "Mudkip", "level": 5, "hp": 20, "max_hp": 20, "moves": ["Tackle"]}],
        bag=[],
        dialog="",
        in_battle=False,
        battle_state=None,
    )
    defaults.update(overrides)
    return GameState(**defaults)


def make_config(**overrides):
    defaults = dict(
        game="emerald",
        rom_path="/path/to/rom.gba",
        model_provider="claude",
        model_name="claude-sonnet-4-20250514",
        api_key="test-key",
    )
    defaults.update(overrides)
    return RunConfig(**defaults)


# ---------------------------------------------------------------------------
# Test 1: Initialisation
# ---------------------------------------------------------------------------

def test_agent_loop_init():
    emulator = MagicMock()
    adapter = MagicMock()
    provider = MagicMock()
    config = make_config()

    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)

    assert loop.step_count == 0
    assert loop.running is False
    assert loop.messages == []


# ---------------------------------------------------------------------------
# Test 2: Single step in text mode
# ---------------------------------------------------------------------------

def test_agent_loop_single_step_text_mode():
    emulator = MagicMock()
    adapter = MagicMock()
    provider = MagicMock()
    config = make_config(input_mode="text")

    state = make_game_state()
    adapter.read_state.return_value = state

    response = AgentResponse(
        reasoning="I should move up.",
        action="up",
        raw_text="I should move up.\nACTION: up",
    )
    provider.send.return_value = response

    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
    result = loop.step()

    # Provider.send should be called (not send_with_image)
    provider.send.assert_called_once()
    provider.send_with_image.assert_not_called()

    # Button should be pressed
    emulator.press_button.assert_called_once_with("up")

    assert result.action == "up"
    assert loop.step_count == 1


# ---------------------------------------------------------------------------
# Test 3: Single step in vision mode
# ---------------------------------------------------------------------------

def test_agent_loop_single_step_vision_mode():
    emulator = MagicMock()
    adapter = MagicMock()
    provider = MagicMock()
    config = make_config(input_mode="vision")

    state = make_game_state()
    adapter.read_state.return_value = state

    response = AgentResponse(
        reasoning="I see the town.",
        action="A",
        raw_text="I see the town.\nACTION: A",
    )
    provider.send_with_image.return_value = response

    fake_png = b"\x89PNG\r\n\x1a\n"

    with patch("pokebenchmark.agent.loop.capture_frame") as mock_capture:
        mock_capture.return_value = (MagicMock(), fake_png)
        loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
        result = loop.step()

    mock_capture.assert_called_once_with(emulator)
    provider.send_with_image.assert_called_once()
    provider.send.assert_not_called()

    emulator.press_button.assert_called_once_with("A")
    assert result.action == "A"
    assert loop.step_count == 1


# ---------------------------------------------------------------------------
# Test 4: No action — press_button must NOT be called
# ---------------------------------------------------------------------------

def test_agent_loop_no_action_does_not_press():
    emulator = MagicMock()
    adapter = MagicMock()
    provider = MagicMock()
    config = make_config(input_mode="text")

    state = make_game_state()
    adapter.read_state.return_value = state

    response = AgentResponse(
        reasoning="I have no idea what to do.",
        action=None,
        raw_text="I have no idea what to do.",
    )
    provider.send.return_value = response

    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
    result = loop.step()

    emulator.press_button.assert_not_called()
    assert result.action is None
    assert loop.step_count == 1


# ---------------------------------------------------------------------------
# Test 5: run(3) executes 3 steps and returns 3
# ---------------------------------------------------------------------------

def test_agent_loop_run_multiple_steps():
    emulator = MagicMock()
    adapter = MagicMock()
    provider = MagicMock()
    config = make_config(input_mode="text")

    state = make_game_state()
    adapter.read_state.return_value = state

    response = AgentResponse(
        reasoning="Moving.",
        action="right",
        raw_text="Moving.\nACTION: right",
    )
    provider.send.return_value = response

    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
    steps_run = loop.run(3)

    assert steps_run == 3
    assert loop.step_count == 3
    assert loop.running is False
    assert emulator.press_button.call_count == 3


# ---------------------------------------------------------------------------
# Test 6: AgentLoop has a ContextBuilder
# ---------------------------------------------------------------------------

def test_agent_loop_has_context_builder():
    loop = AgentLoop(emulator=MagicMock(), adapter=MagicMock(), provider=MagicMock(), config=make_config())
    assert isinstance(loop.context_builder, ContextBuilder)


# ---------------------------------------------------------------------------
# Test 7: AgentLoop has a StuckDetector
# ---------------------------------------------------------------------------

def test_agent_loop_has_stuck_detector():
    loop = AgentLoop(emulator=MagicMock(), adapter=MagicMock(), provider=MagicMock(), config=make_config())
    assert isinstance(loop.stuck_detector, StuckDetector)
    assert loop.stuck_detector.threshold == loop.config.stuck_threshold


# ---------------------------------------------------------------------------
# Test 8: step() records position in stuck detector
# ---------------------------------------------------------------------------

def test_agent_loop_step_records_position():
    emulator, adapter, provider = MagicMock(), MagicMock(), MagicMock()
    config = make_config(input_mode="text")
    state = make_game_state(x=5, y=10, location="Littleroot Town")
    adapter.read_state.return_value = state
    provider.send.return_value = AgentResponse(reasoning="Go", action="up", raw_text="Go\nACTION: up")
    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
    loop.step()
    assert loop.stuck_detector.steps_since_progress == 0


# ---------------------------------------------------------------------------
# Test 9: stuck state triggers backtrack via load_state
# ---------------------------------------------------------------------------

def test_agent_loop_stuck_triggers_backtrack():
    emulator, adapter, provider = MagicMock(), MagicMock(), MagicMock()
    config = make_config(input_mode="text", stuck_threshold=2)
    state = make_game_state(x=5, y=10, location="Town")
    adapter.read_state.return_value = state
    provider.send.return_value = AgentResponse(reasoning="Go", action="up", raw_text="Go\nACTION: up")
    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)
    loop._last_save_state = b"fake_state"
    loop.step()  # same pos
    loop.step()  # stuck — backtrack
    emulator.load_state.assert_called_once_with(b"fake_state")
