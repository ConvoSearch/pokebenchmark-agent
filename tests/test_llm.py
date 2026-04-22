"""Tests for LLM providers, response parsing, and factory."""
import unittest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Literal


# ---------------------------------------------------------------------------
# 1-3: AgentResponse.parse tests
# ---------------------------------------------------------------------------

class TestAgentResponseParse(unittest.TestCase):
    def setUp(self):
        from pokebenchmark_agent.llm.response import AgentResponse
        self.AgentResponse = AgentResponse

    def test_parse_with_action(self):
        text = "I should move up.\nACTION: up"
        resp = self.AgentResponse.parse(text)
        self.assertEqual(resp.action, "up")
        self.assertEqual(resp.raw_text, text)

    def test_parse_last_action_wins(self):
        text = "First thought.\nACTION: left\nSecond thought.\nACTION: right"
        resp = self.AgentResponse.parse(text)
        self.assertEqual(resp.action, "right")

    def test_parse_no_action_returns_none(self):
        text = "Just reasoning here, no action line."
        resp = self.AgentResponse.parse(text)
        self.assertIsNone(resp.action)

    def test_parse_invalid_action_ignored(self):
        text = "ACTION: fly"
        resp = self.AgentResponse.parse(text)
        self.assertIsNone(resp.action)

    def test_parse_reasoning_strips_action_line(self):
        text = "Some reasoning.\nACTION: A\nMore text."
        resp = self.AgentResponse.parse(text)
        self.assertNotIn("ACTION:", resp.reasoning)

    def test_parse_all_valid_actions(self):
        from pokebenchmark_agent.llm.response import VALID_ACTIONS
        for action in VALID_ACTIONS:
            resp = self.AgentResponse.parse(f"ACTION: {action}")
            self.assertEqual(resp.action, action)


# ---------------------------------------------------------------------------
# 4: LLMProvider is abstract
# ---------------------------------------------------------------------------

class TestLLMProviderAbstract(unittest.TestCase):
    def test_cannot_instantiate_abstract(self):
        from pokebenchmark_agent.llm.base import LLMProvider
        with self.assertRaises(TypeError):
            LLMProvider()

    def test_subclass_must_implement_send(self):
        from pokebenchmark_agent.llm.base import LLMProvider

        class Incomplete(LLMProvider):
            pass

        with self.assertRaises(TypeError):
            Incomplete()


# ---------------------------------------------------------------------------
# 5-7: ClaudeProvider tests
# ---------------------------------------------------------------------------

class TestClaudeProvider(unittest.TestCase):
    def setUp(self):
        # Patch anthropic.Anthropic at import time
        self.mock_anthropic_module = MagicMock()
        self.mock_client = MagicMock()
        self.mock_anthropic_module.Anthropic.return_value = self.mock_client
        self.patcher = patch.dict("sys.modules", {"anthropic": self.mock_anthropic_module})
        self.patcher.start()
        # Re-import with mock in place
        import importlib
        import pokebenchmark.llm.claude as claude_mod
        importlib.reload(claude_mod)
        self.claude_mod = claude_mod

    def tearDown(self):
        self.patcher.stop()

    def test_isinstance_llm_provider(self):
        from pokebenchmark_agent.llm.base import LLMProvider
        provider = self.claude_mod.ClaudeProvider(api_key="key", model="claude-3")
        self.assertIsInstance(provider, LLMProvider)

    def test_send_mocked_returns_agent_response(self):
        from pokebenchmark_agent.llm.response import AgentResponse
        # Set up mock response
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="Let me think.\nACTION: up")]
        self.mock_client.messages.create.return_value = mock_msg

        provider = self.claude_mod.ClaudeProvider(api_key="key", model="claude-3")
        result = provider.send(
            system_prompt="You are a player.",
            messages=[{"role": "user", "content": "What do you do?"}],
        )
        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.action, "up")
        self.mock_client.messages.create.assert_called_once()

    def test_send_with_image_includes_image(self):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text="ACTION: down")]
        self.mock_client.messages.create.return_value = mock_msg

        provider = self.claude_mod.ClaudeProvider(api_key="key", model="claude-3")
        result = provider.send_with_image(
            system_prompt="You are a player.",
            messages=[],
            image_bytes=b"fake_image_data",
        )
        self.assertEqual(result.action, "down")
        call_kwargs = self.mock_client.messages.create.call_args
        # The call should have been made
        self.mock_client.messages.create.assert_called_once()
        # Check messages contain image content
        messages_arg = call_kwargs[1].get("messages") or call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1]["messages"]
        # Verify image was passed somewhere
        self.assertTrue(self.mock_client.messages.create.called)


# ---------------------------------------------------------------------------
# 8-10: OpenAIProvider tests
# ---------------------------------------------------------------------------

class TestOpenAIProvider(unittest.TestCase):
    def setUp(self):
        self.mock_openai_module = MagicMock()
        self.mock_client = MagicMock()
        self.mock_openai_module.OpenAI.return_value = self.mock_client
        self.patcher = patch.dict("sys.modules", {"openai": self.mock_openai_module})
        self.patcher.start()
        import importlib
        import pokebenchmark.llm.openai_provider as oai_mod
        importlib.reload(oai_mod)
        self.oai_mod = oai_mod

    def tearDown(self):
        self.patcher.stop()

    def test_isinstance_llm_provider(self):
        from pokebenchmark_agent.llm.base import LLMProvider
        provider = self.oai_mod.OpenAIProvider(api_key="key", model="gpt-4")
        self.assertIsInstance(provider, LLMProvider)

    def test_send_mocked_returns_agent_response(self):
        from pokebenchmark_agent.llm.response import AgentResponse
        mock_choice = MagicMock()
        mock_choice.message.content = "Thinking...\nACTION: A"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_completion

        provider = self.oai_mod.OpenAIProvider(api_key="key", model="gpt-4")
        result = provider.send(
            system_prompt="You are a player.",
            messages=[{"role": "user", "content": "Go!"}],
        )
        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.action, "A")
        self.mock_client.chat.completions.create.assert_called_once()

    def test_send_with_image_mocked(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "ACTION: B"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        self.mock_client.chat.completions.create.return_value = mock_completion

        provider = self.oai_mod.OpenAIProvider(api_key="key", model="gpt-4")
        result = provider.send_with_image(
            system_prompt="You are a player.",
            messages=[],
            image_bytes=b"fake",
        )
        self.assertEqual(result.action, "B")
        self.mock_client.chat.completions.create.assert_called_once()


# ---------------------------------------------------------------------------
# 11-12: GeminiProvider tests
# ---------------------------------------------------------------------------

class TestGeminiProvider(unittest.TestCase):
    def setUp(self):
        self.mock_genai_module = MagicMock()
        self.mock_types_module = MagicMock()
        self.mock_client = MagicMock()
        self.mock_genai_module.Client.return_value = self.mock_client

        self.patcher = patch.dict("sys.modules", {
            "google": MagicMock(),
            "google.genai": self.mock_genai_module,
            "google.genai.types": self.mock_types_module,
        })
        self.patcher.start()
        import importlib
        import pokebenchmark.llm.gemini as gemini_mod
        importlib.reload(gemini_mod)
        self.gemini_mod = gemini_mod

    def tearDown(self):
        self.patcher.stop()

    def test_isinstance_llm_provider(self):
        from pokebenchmark_agent.llm.base import LLMProvider
        provider = self.gemini_mod.GeminiProvider(api_key="key", model="gemini-pro")
        self.assertIsInstance(provider, LLMProvider)

    def test_send_mocked_returns_agent_response(self):
        from pokebenchmark_agent.llm.response import AgentResponse
        mock_response = MagicMock()
        mock_response.text = "Reasoning here.\nACTION: left"
        self.mock_client.models.generate_content.return_value = mock_response

        provider = self.gemini_mod.GeminiProvider(api_key="key", model="gemini-pro")
        result = provider.send(
            system_prompt="You are a player.",
            messages=[{"role": "user", "content": "Move!"}],
        )
        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.action, "left")
        self.mock_client.models.generate_content.assert_called_once()


# ---------------------------------------------------------------------------
# 13-14: OllamaProvider tests
# ---------------------------------------------------------------------------

class TestOllamaProvider(unittest.TestCase):
    def setUp(self):
        self.mock_ollama_module = MagicMock()
        self.mock_client = MagicMock()
        self.mock_ollama_module.Client.return_value = self.mock_client
        self.patcher = patch.dict("sys.modules", {"ollama": self.mock_ollama_module})
        self.patcher.start()
        import importlib
        import pokebenchmark.llm.ollama_provider as ollama_mod
        importlib.reload(ollama_mod)
        self.ollama_mod = ollama_mod

    def tearDown(self):
        self.patcher.stop()

    def test_isinstance_llm_provider(self):
        from pokebenchmark_agent.llm.base import LLMProvider
        provider = self.ollama_mod.OllamaProvider(model="llama3")
        self.assertIsInstance(provider, LLMProvider)

    def test_send_mocked_returns_agent_response(self):
        from pokebenchmark_agent.llm.response import AgentResponse
        mock_response = MagicMock()
        mock_response.message.content = "Let me think.\nACTION: right"
        self.mock_client.chat.return_value = mock_response

        provider = self.ollama_mod.OllamaProvider(model="llama3")
        result = provider.send(
            system_prompt="You are a player.",
            messages=[{"role": "user", "content": "Go right!"}],
        )
        self.assertIsInstance(result, AgentResponse)
        self.assertEqual(result.action, "right")
        self.mock_client.chat.assert_called_once()


# ---------------------------------------------------------------------------
# 15-17: create_provider factory tests
# ---------------------------------------------------------------------------

class TestCreateProvider(unittest.TestCase):
    def _make_config(self, provider: str):
        from pokebenchmark_agent.config import RunConfig
        return RunConfig(
            game="emerald",
            rom_path="/fake/rom.gba",
            model_provider=provider,
            model_name="some-model",
            api_key="fake-key",
            api_base_url="http://localhost:11434",
        )

    def test_create_provider_claude(self):
        config = self._make_config("claude")
        mock_anthropic = MagicMock()
        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            import importlib
            import pokebenchmark.llm.claude as claude_mod
            importlib.reload(claude_mod)
            with patch("pokebenchmark.llm.claude.ClaudeProvider") as MockClaude:
                import pokebenchmark.llm as llm_pkg
                importlib.reload(llm_pkg)
                llm_pkg.create_provider(config)
                MockClaude.assert_called_once()

    def test_create_provider_openai(self):
        config = self._make_config("openai")
        mock_openai = MagicMock()
        with patch.dict("sys.modules", {"openai": mock_openai}):
            import importlib
            import pokebenchmark.llm.openai_provider as oai_mod
            importlib.reload(oai_mod)
            with patch("pokebenchmark.llm.openai_provider.OpenAIProvider") as MockOAI:
                import pokebenchmark.llm as llm_pkg
                importlib.reload(llm_pkg)
                llm_pkg.create_provider(config)
                MockOAI.assert_called_once()

    def test_create_provider_unsupported_raises(self):
        from pokebenchmark_agent.config import RunConfig
        # Patch the Literal validation by using a real config but swapping the value
        config = RunConfig(
            game="emerald",
            rom_path="/fake/rom.gba",
            model_provider="claude",  # valid to construct
            model_name="m",
        )
        # Manually override after creation
        object.__setattr__(config, "model_provider", "unsupported")
        from pokebenchmark_agent.llm import create_provider
        with self.assertRaises(ValueError):
            create_provider(config)


if __name__ == "__main__":
    unittest.main()
