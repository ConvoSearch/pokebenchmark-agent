import tempfile
import pytest
from pokebenchmark_agent.memory.store import MemoryStore

@pytest.fixture
def store():
    with tempfile.TemporaryDirectory() as d:
        yield MemoryStore(d)

def test_empty_initially(store):
    assert store.list_entries() == []

def test_write_and_read(store):
    store.write("progress", "Defeated Brock. Have 2 badges.")
    assert "Brock" in store.read("progress")

def test_list_entries(store):
    store.write("progress", "some progress")
    store.write("strategy", "some strategy")
    entries = store.list_entries()
    assert "progress" in entries
    assert "strategy" in entries

def test_update_existing(store):
    store.write("progress", "v1")
    store.write("progress", "v2")
    assert store.read("progress") == "v2"

def test_append(store):
    store.write("observations", "Gym uses water types.")
    store.append("observations", "Rival has Charizard.")
    content = store.read("observations")
    assert "water types" in content
    assert "Charizard" in content

def test_delete(store):
    store.write("temp", "temporary note")
    store.delete("temp")
    assert store.read("temp") is None

def test_read_nonexistent(store):
    assert store.read("nonexistent") is None

def test_format_for_context_empty(store):
    assert store.format_for_context() == ""

def test_format_for_context_with_entries(store):
    store.write("progress", "Have 3 badges")
    store.write("strategy", "Train water types")
    text = store.format_for_context()
    assert "progress" in text
    assert "3 badges" in text

def test_self_critique(store):
    store.write("self-critique", "Keep losing to electric types. Need ground type.")
    assert "ground type" in store.read("self-critique")
