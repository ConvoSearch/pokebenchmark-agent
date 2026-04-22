"""CLI entry point for pokebenchmark."""
import argparse
import logging

logger = logging.getLogger(__name__)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="pokebenchmark — run an LLM agent on a Pokemon GBA game"
    )
    parser.add_argument("--rom", required=True, help="Path to the GBA ROM file")
    parser.add_argument(
        "--game",
        required=True,
        choices=["emerald", "firered"],
        help="Which game the ROM is for",
    )
    parser.add_argument(
        "--provider",
        required=True,
        choices=["claude", "openai", "gemini", "ollama"],
        help="LLM provider to use",
    )
    parser.add_argument("--model", required=True, help="Model name/ID to use")
    parser.add_argument("--api-key", required=True, help="API key for the LLM provider")
    parser.add_argument("--api-base-url", default=None, help="Custom API base URL")
    parser.add_argument(
        "--input-mode",
        required=True,
        choices=["vision", "text"],
        help="Input mode: vision (screenshot) or text (state text)",
    )
    parser.add_argument("--steps", type=int, required=True, help="Number of agent steps")
    parser.add_argument("--max-history", type=int, required=True, help="Max message pairs in context")
    parser.add_argument("--temperature", type=float, required=True, help="LLM sampling temperature")
    parser.add_argument("--save-state", default=None, help="Path to a save state file to load")
    parser.add_argument("--save-file", default=None, help="Path to a .sav battery save file")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    from pokebenchmark_agent.config import RunConfig
    from pokebenchmark_emulator.gba import GBAEmulator
    from pokebenchmark_emulator.adapters.emerald import EmeraldAdapter
    from pokebenchmark_emulator.adapters.firered import FireRedAdapter
    from pokebenchmark_agent.llm import create_provider
    from pokebenchmark_agent.agent.loop import AgentLoop

    config = RunConfig(
        game=args.game,
        rom_path=args.rom,
        model_provider=args.provider,
        model_name=args.model,
        api_key=args.api_key,
        api_base_url=args.api_base_url,
        input_mode=args.input_mode,
        max_history=args.max_history,
        temperature=args.temperature,
        save_state_path=args.save_state,
        save_file_path=args.save_file,
    )

    emulator = GBAEmulator(rom_path=args.rom, save_file=args.save_file)
    if args.save_state:
        emulator.load_state_from_file(args.save_state)
        logger.info(f"Loaded save state from {args.save_state}")

    adapter = EmeraldAdapter() if args.game == "emerald" else FireRedAdapter()
    provider = create_provider(config)
    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)

    steps_run = loop.run(args.steps)
    logger.info(f"Completed {steps_run} steps.")
    return steps_run


if __name__ == "__main__":
    main()
