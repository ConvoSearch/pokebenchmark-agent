import os
import tempfile
import pytest
from pokebenchmark_agent.skills.loader import SkillLoader

@pytest.fixture
def skills_dir():
    with tempfile.TemporaryDirectory() as d:
        common = os.path.join(d, "common")
        os.makedirs(common)
        with open(os.path.join(common, "battle-strategy.md"), "w") as f:
            f.write("# Battle Strategy\nAlways consider type matchups.\n")
        with open(os.path.join(common, "navigation.md"), "w") as f:
            f.write("# Navigation\nCheck exits before moving.\n")
        emerald = os.path.join(d, "emerald")
        os.makedirs(emerald)
        with open(os.path.join(emerald, "weather.md"), "w") as f:
            f.write("# Weather\nUse rain teams against fire gyms.\n")
        firered = os.path.join(d, "firered")
        os.makedirs(firered)
        with open(os.path.join(firered, "kanto-gyms.md"), "w") as f:
            f.write("# Kanto Gyms\nBrock uses rock types.\n")
        yield d

def test_load_common_skills(skills_dir):
    loader = SkillLoader(skills_dir, game="emerald")
    skills = loader.load_common()
    assert len(skills) == 2
    assert any("Battle Strategy" in s for s in skills)

def test_load_game_skills(skills_dir):
    loader = SkillLoader(skills_dir, game="emerald")
    skills = loader.load_game_specific()
    assert len(skills) == 1
    assert "Weather" in skills[0]

def test_load_game_skills_firered(skills_dir):
    loader = SkillLoader(skills_dir, game="firered")
    skills = loader.load_game_specific()
    assert len(skills) == 1
    assert "Kanto Gyms" in skills[0]

def test_load_all(skills_dir):
    loader = SkillLoader(skills_dir, game="emerald")
    skills = loader.load_all()
    assert len(skills) == 3

def test_load_specific_files(skills_dir):
    loader = SkillLoader(skills_dir, game="emerald")
    battle_path = os.path.join(skills_dir, "common", "battle-strategy.md")
    skills = loader.load_files([battle_path])
    assert len(skills) == 1
    assert "Battle Strategy" in skills[0]

def test_missing_dir_returns_empty():
    loader = SkillLoader("/nonexistent/path", game="emerald")
    skills = loader.load_all()
    assert skills == []

def test_format_for_context(skills_dir):
    loader = SkillLoader(skills_dir, game="emerald")
    text = loader.format_for_context()
    assert "## Skill:" in text
    assert "Battle Strategy" in text
