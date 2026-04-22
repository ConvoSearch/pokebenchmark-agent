from pokebenchmark_agent.agent.stuck_detector import StuckDetector

def test_not_stuck_initially():
    assert StuckDetector(threshold=5).is_stuck() is False

def test_not_stuck_with_changing_positions():
    d = StuckDetector(threshold=3)
    d.record(x=5, y=10, location="Town A")
    d.record(x=6, y=10, location="Town A")
    d.record(x=7, y=10, location="Town A")
    assert d.is_stuck() is False

def test_stuck_when_same_position_repeated():
    d = StuckDetector(threshold=3)
    d.record(x=5, y=10, location="Town A")
    d.record(x=5, y=10, location="Town A")
    d.record(x=5, y=10, location="Town A")
    assert d.is_stuck() is True

def test_stuck_resets_after_check():
    d = StuckDetector(threshold=3)
    for _ in range(3): d.record(x=5, y=10, location="Town A")
    assert d.is_stuck() is True
    d.reset()
    assert d.is_stuck() is False

def test_location_change_not_stuck():
    d = StuckDetector(threshold=3)
    d.record(x=5, y=10, location="Town A")
    d.record(x=5, y=10, location="Town B")
    d.record(x=5, y=10, location="Town A")
    assert d.is_stuck() is False

def test_threshold_respected():
    d = StuckDetector(threshold=5)
    for _ in range(4): d.record(x=5, y=10, location="Town A")
    assert d.is_stuck() is False
    d.record(x=5, y=10, location="Town A")
    assert d.is_stuck() is True

def test_steps_since_progress():
    d = StuckDetector(threshold=5)
    d.record(x=5, y=10, location="Town A")
    d.record(x=5, y=10, location="Town A")
    assert d.steps_since_progress == 1
    d.record(x=6, y=10, location="Town A")
    assert d.steps_since_progress == 0
