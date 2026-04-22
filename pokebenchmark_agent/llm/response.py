import re
from dataclasses import dataclass

VALID_ACTIONS = {"up", "down", "left", "right", "A", "B", "L", "R", "start", "select"}
ACTION_PATTERN = re.compile(r"^ACTION:\s*(\S+)", re.MULTILINE)


@dataclass
class AgentResponse:
    reasoning: str
    action: str | None
    raw_text: str

    @classmethod
    def parse(cls, text: str) -> "AgentResponse":
        matches = ACTION_PATTERN.findall(text)
        action = None
        if matches:
            candidate = matches[-1]
            if candidate in VALID_ACTIONS:
                action = candidate
        reasoning = ACTION_PATTERN.sub("", text).strip()
        return cls(reasoning=reasoning, action=action, raw_text=text)
