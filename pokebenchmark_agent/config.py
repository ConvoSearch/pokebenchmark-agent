from dataclasses import dataclass, field
from typing import Literal


@dataclass
class RunConfig:
    # Required fields
    game: Literal["emerald", "firered"]
    rom_path: str
    model_provider: Literal["claude", "openai", "gemini", "ollama", "manual"]
    model_name: str

    # Optional fields with defaults
    input_mode: Literal["vision", "text"] = "vision"
    save_state_path: str | None = None
    save_file_path: str | None = None
    skill_files: list[str] = field(default_factory=list)
    api_key: str | None = None
    api_base_url: str | None = None
    auto_save_interval: int = 50
    stuck_threshold: int = 20
    max_history: int = 30
    temperature: float = 1.0
    max_tokens: int = 4096
    orchestrator_url: str | None = None
    run_id: str | None = None
    workspace_dir: str = "./workspace"
    skills_dir: str = "./skills"

    def __post_init__(self):
        if self.game not in ("emerald", "firered"):
            raise ValueError(
                f"game must be 'emerald' or 'firered', got '{self.game}'"
            )
        if self.input_mode not in ("vision", "text"):
            raise ValueError(
                f"input_mode must be 'vision' or 'text', got '{self.input_mode}'"
            )
