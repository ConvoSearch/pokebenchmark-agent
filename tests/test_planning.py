import tempfile
import pytest
from pokebenchmark_agent.planning.workspace import PlanningWorkspace

@pytest.fixture
def workspace():
    with tempfile.TemporaryDirectory() as d:
        yield PlanningWorkspace(d)

def test_no_active_plan_initially(workspace):
    assert workspace.get_active_plan() is None

def test_write_and_read_plan(workspace):
    workspace.write_plan("plan_001.md", "goal: Get to Cerulean City\nsteps:\n- Go north")
    content = workspace.read_plan("plan_001.md")
    assert "Cerulean City" in content

def test_get_active_plan_returns_latest(workspace):
    workspace.write_plan("plan_001.md", "old plan")
    workspace.set_active("plan_001.md")
    assert workspace.get_active_plan() == "old plan"

def test_set_active_plan(workspace):
    workspace.write_plan("plan_001.md", "first plan")
    workspace.write_plan("plan_002.md", "second plan")
    workspace.set_active("plan_002.md")
    assert workspace.get_active_plan() == "second plan"

def test_list_plans(workspace):
    workspace.write_plan("plan_001.md", "first")
    workspace.write_plan("plan_002.md", "second")
    plans = workspace.list_plans()
    assert "plan_001.md" in plans
    assert "plan_002.md" in plans

def test_delete_plan(workspace):
    workspace.write_plan("plan_001.md", "to delete")
    workspace.delete_plan("plan_001.md")
    assert workspace.read_plan("plan_001.md") is None

def test_clear_active(workspace):
    workspace.write_plan("plan_001.md", "active plan")
    workspace.set_active("plan_001.md")
    workspace.clear_active()
    assert workspace.get_active_plan() is None

def test_format_for_context_no_plan(workspace):
    assert workspace.format_for_context() == ""

def test_format_for_context_with_plan(workspace):
    workspace.write_plan("plan_001.md", "goal: Beat Brock")
    workspace.set_active("plan_001.md")
    text = workspace.format_for_context()
    assert "Beat Brock" in text
    assert "Active Plan" in text
