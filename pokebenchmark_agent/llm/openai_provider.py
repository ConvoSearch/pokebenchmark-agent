import base64
import openai

from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = openai.OpenAI(**kwargs)
        self._model = model

    def send(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        all_messages = [{"role": "system", "content": system_prompt}] + list(messages)
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = completion.choices[0].message.content
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
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                    },
                },
            ],
        }
        all_messages = (
            [{"role": "system", "content": system_prompt}]
            + list(messages)
            + [image_message]
        )
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = completion.choices[0].message.content
        return AgentResponse.parse(text)
