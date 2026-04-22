from abc import ABC, abstractmethod
from pokebenchmark_agent.llm.response import AgentResponse


class LLMProvider(ABC):
    @abstractmethod
    def send(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse: ...

    @abstractmethod
    def send_with_image(
        self,
        system_prompt: str,
        messages: list[dict],
        image_bytes: bytes,
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse: ...
