import base64
import anthropic

from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse


class ClaudeProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def send(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        response = self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.content[0].text
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
        image_message = {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_b64,
                    },
                },
            ],
        }
        all_messages = list(messages) + [image_message]
        response = self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.content[0].text
        return AgentResponse.parse(text)
