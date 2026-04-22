from pokebenchmark_agent.llm.base import LLMProvider
from pokebenchmark_agent.llm.response import AgentResponse, VALID_ACTIONS


def create_provider(config) -> LLMProvider:
    if config.model_provider == "claude":
        from pokebenchmark_agent.llm.claude import ClaudeProvider
        return ClaudeProvider(api_key=config.api_key, model=config.model_name)
    elif config.model_provider == "openai":
        from pokebenchmark_agent.llm.openai_provider import OpenAIProvider
        return OpenAIProvider(
            api_key=config.api_key,
            model=config.model_name,
            base_url=config.api_base_url,
        )
    elif config.model_provider == "gemini":
        from pokebenchmark_agent.llm.gemini import GeminiProvider
        return GeminiProvider(api_key=config.api_key, model=config.model_name)
    elif config.model_provider == "ollama":
        from pokebenchmark_agent.llm.ollama_provider import OllamaProvider
        return OllamaProvider(model=config.model_name, host=config.api_base_url)
    else:
        raise ValueError(f"Unsupported provider: {config.model_provider}")


__all__ = ["LLMProvider", "AgentResponse", "VALID_ACTIONS", "create_provider"]
