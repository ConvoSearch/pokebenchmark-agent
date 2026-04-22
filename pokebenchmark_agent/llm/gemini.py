import base64
from google.genai import Client
from google.genai import types

from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model: str) -> None:
        self._client = Client(api_key=api_key)
        self._model = model

    def _build_contents(self, system_prompt: str, messages: list[dict]) -> list:
        contents = []
        for msg in messages:
            role = msg.get("role", "user")
            # Gemini uses "user" and "model" roles
            if role == "assistant":
                role = "model"
            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part(text=msg.get("content", ""))],
                )
            )
        return contents

    def send(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        contents = self._build_contents(system_prompt, messages)
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=config,
        )
        return AgentResponse.parse(response.text)

    def send_with_image(
        self,
        system_prompt: str,
        messages: list[dict],
        image_bytes: bytes,
        temperature: float = 1.0,
        max_tokens: int = 4096,
    ) -> AgentResponse:
        contents = self._build_contents(system_prompt, messages)
        image_part = types.Part(
            inline_data=types.Blob(mime_type="image/png", data=image_bytes)
        )
        contents.append(
            types.Content(role="user", parts=[image_part])
        )
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=config,
        )
        return AgentResponse.parse(response.text)
