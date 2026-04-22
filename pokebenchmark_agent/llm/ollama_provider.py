import base64
import ollama

from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse


class OllamaProvider(LLMProvider):
    def __init__(self, model: str, host: str | None = None) -> None:
        kwargs: dict = {}
        if host:
            kwargs["host"] = host
        self._client = ollama.Client(**kwargs)
        self._model = model

    def _build_messages(self, system_prompt: str, messages: list[dict]) -> list[dict]:
        all_messages = [{"role": "system", "content": system_prompt}]
        all_messages.extend(messages)
        return all_messages

    def send(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        all_messages = self._build_messages(system_prompt, messages)
        response = self._client.chat(
            model=self._model,
            messages=all_messages,
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        text = response.message.content
        return AgentResponse.parse(text)

    def send_with_image(
        self,
        system_prompt: str,
        messages: list[dict],
        image_bytes: bytes,
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        all_messages = self._build_messages(system_prompt, messages)
        all_messages.append(
            {
                "role": "user",
                "content": "",
                "images": [image_b64],
            }
        )
        response = self._client.chat(
            model=self._model,
            messages=all_messages,
            options={"temperature": temperature, "num_predict": max_tokens},
        )
        text = response.message.content
        return AgentResponse.parse(text)
