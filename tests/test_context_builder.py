from pokebenchmark_agent.agent.context import ContextBuilder
from pokebenchmark_emulator.adapters.base import GameState

def make_state(**overrides):
    defaults = dict(player_name="ASH", location="Town", x=5, y=10, facing="up",
                    badges=[], money=3000,
                    party=[{"species": "Mudkip", "level": 5, "hp": 20, "max_hp": 20, "moves": ["Tackle"]}],
                    bag=[], dialog="", in_battle=False, battle_state=None)
    defaults.update(overrides)
    return GameState(**defaults)

def test_build_with_state_only():
    text = ContextBuilder().build(state_text=make_state().to_text())
    assert "ASH" in text
    assert "Current game state:" in text

def test_build_with_skills():
    text = ContextBuilder().build(state_text=make_state().to_text(), skills_text="## Skill: Battle\nUse type advantages.")
    assert "type advantages" in text
    assert "ASH" in text

def test_build_with_plan():
    text = ContextBuilder().build(state_text=make_state().to_text(), plan_text="## Active Plan\nBeat Brock")
    assert "Beat Brock" in text

def test_build_with_memory():
    text = ContextBuilder().build(state_text=make_state().to_text(), memory_text="## Agent Memory\n\n### progress\n\n2 badges earned")
    assert "2 badges" in text

def test_build_with_everything():
    text = ContextBuilder().build(
        state_text=make_state().to_text(),
        skills_text="## Skill: Nav\nCheck exits.",
        plan_text="## Active Plan\nGo north.",
        memory_text="## Agent Memory\n\n### progress\nAt town.",
    )
    assert "Check exits" in text
    assert "Go north" in text
    assert "At town" in text
    assert "ASH" in text

def test_build_order():
    text = ContextBuilder().build(
        state_text=make_state().to_text(),
        skills_text="SKILLS_MARKER",
        plan_text="PLAN_MARKER",
        memory_text="MEMORY_MARKER",
    )
    assert text.index("SKILLS_MARKER") < text.index("PLAN_MARKER") < text.index("MEMORY_MARKER") < text.index("ASH")
