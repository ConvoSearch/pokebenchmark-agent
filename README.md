# pokebenchmark-agent

LLM agent framework for playing Pokemon GBA games. Part of the [pokebenchmark](https://github.com/ConvoSearch/pokebenchmark-platform) benchmarking stack.

## What's here

- **Agent loop** (`pokebenchmark_agent.agent`) — step/run cycle with stuck detection and context building
- **LLM providers** (`pokebenchmark_agent.llm`) — unified interface across Claude, OpenAI, Gemini, Ollama, with vision and text-only modes
- **Skill system** (`pokebenchmark_agent.skills`) — markdown files organized by scope (common + per-game) that carry operational knowledge into the agent's context
- **Planning workspace** (`pokebenchmark_agent.planning`) — active-plan file management the agent reads and writes
- **Memory store** (`pokebenchmark_agent.memory`) — persistent progress/strategy/self-critique across sessions
- **Session runner** (`pokebenchmark_agent.session`) — in-container entry point that wires the above together from environment variables

## Install

```bash
pip install pokebenchmark-agent
```

## CLI

```bash
pokebenchmark-agent \
  --rom firered.gba \
  --game firered \
  --provider claude \
  --model claude-sonnet-4-5 \
  --api-key $ANTHROPIC_API_KEY \
  --input-mode vision \
  --steps 100 \
  --max-history 30 \
  --temperature 1.0
```

## Library

```python
from pokebenchmark_emulator import GBAEmulator
from pokebenchmark_emulator.adapters import FireRedAdapter
from pokebenchmark_agent import RunConfig
from pokebenchmark_agent.llm import create_provider
from pokebenchmark_agent.agent.loop import AgentLoop

config = RunConfig(
    game="firered", rom_path="firered.gba",
    model_provider="claude", model_name="claude-sonnet-4-5",
    api_key="sk-ant-...", input_mode="vision",
    max_history=30, temperature=1.0,
)
emu = GBAEmulator("firered.gba")
loop = AgentLoop(
    emulator=emu,
    adapter=FireRedAdapter(),
    provider=create_provider(config),
    config=config,
)
loop.run(num_steps=100)
```

## License

MIT
