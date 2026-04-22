class StuckDetector:
    def __init__(self, threshold: int = 20):
        self.threshold = threshold
        self._history: list[tuple[int, int, str]] = []
        self.steps_since_progress = 0
        self._last_position: tuple[int, int, str] | None = None

    def record(self, x: int, y: int, location: str):
        current = (x, y, location)
        if self._last_position is None or current != self._last_position:
            self.steps_since_progress = 0
        else:
            self.steps_since_progress += 1
        self._last_position = current
        self._history.append(current)

    def is_stuck(self) -> bool:
        return self.steps_since_progress >= max(0, self.threshold - 1)

    def reset(self):
        self._history.clear()
        self.steps_since_progress = 0
        self._last_position = None
