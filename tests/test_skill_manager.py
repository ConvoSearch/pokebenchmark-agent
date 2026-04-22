import os
import tempfile
import pytest
from pokebenchmark_agent.skills.manager import SkillManager, Skill


@pytest.fixture
def mgr():
    with tempfile.TemporaryDirectory() as d:
        yield SkillManager(d, allowed_games=["firered", "emerald"])


def test_init_creates_scope_dirs(mgr):
    assert os.path.isdir(os.path.join(mgr.skills_dir, "common"))
    assert os.path.isdir(os.path.join(mgr.skills_dir, "firered"))
    assert os.path.isdir(os.path.join(mgr.skills_dir, "emerald"))


def test_list_skills_empty(mgr):
    assert mgr.list_skills() == []


def test_write_and_get_skill(mgr):
    mgr.write_skill("firered", "gym-order", "# Gym Order\n\nBrock first.")
    skill = mgr.get_skill("firered", "gym-order")
    assert skill is not None
    assert skill.scope == "firered"
    assert skill.name == "gym-order"
    assert "Brock" in skill.content


def test_list_skills_returns_all_scopes(mgr):
    mgr.write_skill("common", "battle", "# Battle")
    mgr.write_skill("firered", "kanto", "# Kanto")
    mgr.write_skill("emerald", "hoenn", "# Hoenn")
    skills = mgr.list_skills()
    assert len(skills) == 3
    scopes = {s.scope for s in skills}
    assert scopes == {"common", "firered", "emerald"}


def test_list_skills_filtered_by_scope(mgr):
    mgr.write_skill("common", "a", "a")
    mgr.write_skill("firered", "b", "b")
    result = mgr.list_skills(scope="firered")
    assert len(result) == 1
    assert result[0].name == "b"


def test_delete_skill(mgr):
    mgr.write_skill("common", "temp", "temp content")
    assert mgr.delete_skill("common", "temp") is True
    assert mgr.get_skill("common", "temp") is None


def test_delete_nonexistent_skill(mgr):
    assert mgr.delete_skill("common", "nonexistent") is False


def test_get_nonexistent_skill(mgr):
    assert mgr.get_skill("common", "nope") is None


def test_invalid_scope_raises(mgr):
    with pytest.raises(ValueError, match="Invalid scope"):
        mgr.write_skill("pokemon_red", "a", "b")


def test_invalid_name_raises(mgr):
    with pytest.raises(ValueError, match="Invalid skill name"):
        mgr.write_skill("common", "../etc/passwd", "hack")
    with pytest.raises(ValueError, match="Invalid skill name"):
        mgr.write_skill("common", "", "empty")
    with pytest.raises(ValueError, match="Invalid skill name"):
        mgr.write_skill("common", ".hidden", "dotfile")


def test_update_existing_skill(mgr):
    mgr.write_skill("firered", "battle", "v1")
    mgr.write_skill("firered", "battle", "v2")
    skill = mgr.get_skill("firered", "battle")
    assert skill.content == "v2"


def test_skill_to_dict():
    s = Skill(scope="common", name="x", content="y")
    d = s.to_dict()
    assert d == {"scope": "common", "name": "x", "content": "y"}
