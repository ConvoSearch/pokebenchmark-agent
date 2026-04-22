"""In-container session runner — reads configuration from environment variables and runs the agent loop."""
import logging
import os

from pokebenchmark_agent.config import RunConfig

logger = logging.getLogger(__name__)


REQUIRED_ENV = [
    "GAME",
    "MODEL_PROVIDER",
    "MODEL_NAME",
    "API_KEY",
    "INPUT_MODE",
    "ROM_PATH",
    "RUN_ID",
    "STEPS",
    "AUTO_SAVE_INTERVAL",
    "STUCK_THRESHOLD",
    "MAX_HISTORY",
    "WORKSPACE_DIR",
    "SKILLS_DIR",
    "ORCHESTRATOR_URL",
]


def build_config_from_env() -> RunConfig:
    missing = [k for k in REQUIRED_ENV if k not in os.environ]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}")

    return RunConfig(
        game=os.environ["GAME"],
        rom_path=os.environ["ROM_PATH"],
        model_provider=os.environ["MODEL_PROVIDER"],
        model_name=os.environ["MODEL_NAME"],
        api_key=os.environ["API_KEY"],
        input_mode=os.environ["INPUT_MODE"],
        save_state_path=os.environ.get("SAVE_STATE_PATH"),
        run_id=os.environ["RUN_ID"],
        orchestrator_url=os.environ["ORCHESTRATOR_URL"],
        workspace_dir=os.environ["WORKSPACE_DIR"],
        skills_dir=os.environ["SKILLS_DIR"],
        auto_save_interval=int(os.environ["AUTO_SAVE_INTERVAL"]),
        stuck_threshold=int(os.environ["STUCK_THRESHOLD"]),
        max_history=int(os.environ["MAX_HISTORY"]),
    )


def run_session():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    config = build_config_from_env()
    steps = int(os.environ["STEPS"])

    logger.info(
        "Starting session: game=%s provider=%s model=%s steps=%d",
        config.game, config.model_provider, config.model_name, steps,
    )

    from pokebenchmark_emulator.gba import GBAEmulator
    from pokebenchmark_emulator.adapters.emerald import EmeraldAdapter
    from pokebenchmark_emulator.adapters.firered import FireRedAdapter
    from pokebenchmark_agent.llm import create_provider
    from pokebenchmark_agent.agent.loop import AgentLoop
    from pokebenchmark_agent.skills.loader import SkillLoader
    from pokebenchmark_agent.planning.workspace import PlanningWorkspace
    from pokebenchmark_agent.memory.store import MemoryStore

    emulator = GBAEmulator(rom_path=config.rom_path)
    if config.save_state_path:
        emulator.load_state_from_file(config.save_state_path)
        logger.info("Loaded save state from %s", config.save_state_path)

    adapter = EmeraldAdapter() if config.game == "emerald" else FireRedAdapter()
    provider = create_provider(config)
    loop = AgentLoop(emulator=emulator, adapter=adapter, provider=provider, config=config)

    skill_loader = SkillLoader(skills_dir=config.skills_dir, game=config.game)
    loop.set_skills_text(skill_loader.format_for_context())

    plans_dir = os.path.join(config.workspace_dir, "plans")
    planning = PlanningWorkspace(plans_dir=plans_dir)
    loop.set_plan_text(planning.format_for_context())

    memory_dir = os.path.join(config.workspace_dir, "memory")
    memory = MemoryStore(memory_dir=memory_dir)
    loop.set_memory_text(memory.format_for_context())

    steps_run = loop.run(steps)
    logger.info("Session complete: %d steps run.", steps_run)
    return steps_run
