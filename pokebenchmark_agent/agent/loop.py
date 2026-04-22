import logging
from pokebenchmark_emulator.adapters.base import GameAdapter, GameState
from pokebenchmark_agent.agent.context import ContextBuilder
from pokebenchmark_agent.agent.stuck_detector import StuckDetector
from pokebenchmark_agent.config import RunConfig
from pokebenchmark_emulator.frame import capture_frame
from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI agent playing Pokemon. You can see the game state and must decide what button to press next.

Available buttons: up, down, left, right, A, B, L, R, start, select

After your reasoning, you MUST end your response with an ACTION line:
ACTION: <button>

Example:
I need to talk to this NPC by pressing A.
ACTION: A
"""


class AgentLoop:
    def __init__(self, emulator, adapter: GameAdapter, provider: LLMProvider, config: RunConfig):
        self.emulator = emulator
        self.adapter = adapter
        self.provider = provider
        self.config = config
        self.step_count = 0
        self.running = False
        self.messages: list[dict] = []
        self.context_builder = ContextBuilder()
        self.stuck_detector = StuckDetector(threshold=config.stuck_threshold)
        self._last_save_state: bytes | None = None
        self._skills_text: str = ""
        self._plan_text: str = ""
        self._memory_text: str = ""

    def set_skills_text(self, text: str):
        self._skills_text = text

    def set_plan_text(self, text: str):
        self._plan_text = text

    def set_memory_text(self, text: str):
        self._memory_text = text

    def step(self) -> AgentResponse:
        state = self.adapter.read_state(self.emulator)
        self.stuck_detector.record(x=state.x, y=state.y, location=state.location)

        if self.stuck_detector.is_stuck() and self._last_save_state is not None:
            self.emulator.load_state(self._last_save_state)
            self.stuck_detector.reset()
            state = self.adapter.read_state(self.emulator)

        user_message = self.context_builder.build(
            state_text=state.to_text(),
            skills_text=self._skills_text,
            plan_text=self._plan_text,
            memory_text=self._memory_text,
        )
        self.messages.append({"role": "user", "content": user_message})

        if self.config.input_mode == "vision":
            _, png_bytes = capture_frame(self.emulator)
            response = self.provider.send_with_image(
                system_prompt=SYSTEM_PROMPT,
                messages=self.messages,
                image_bytes=png_bytes,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        else:
            response = self.provider.send(
                system_prompt=SYSTEM_PROMPT,
                messages=self.messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

        self.messages.append({"role": "assistant", "content": response.raw_text})

        if response.action:
            self.emulator.press_button(response.action)
            logger.info(f"Step {self.step_count}: {response.action} \u2014 {response.reasoning[:80]}")
        else:
            logger.warning(f"Step {self.step_count}: no action parsed")

        self.step_count += 1

        if self.step_count % self.config.auto_save_interval == 0:
            self._last_save_state = self.emulator.save_state()

        self._trim_history()
        return response

    def run(self, num_steps: int) -> int:
        self.running = True
        steps = 0
        try:
            for _ in range(num_steps):
                if not self.running:
                    break
                self.step()
                steps += 1
        except KeyboardInterrupt:
            logger.info("Agent loop interrupted")
        finally:
            self.running = False
        return steps

    def stop(self):
        self.running = False

    def _trim_history(self):
        if len(self.messages) > self.config.max_history * 2:
            self.messages = self.messages[-(self.config.max_history * 2):]
