"""Load config from .vncoderc or vncode-config.yaml."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import os
import yaml
from pydantic import BaseModel, Field


class MeetingConfig(BaseModel):
    max_perspective_rounds: int = 1
    max_debate_rounds: int = 2
    max_perspective_debate_rounds: int = 1
    total_max: int = 5


class LLMConfig(BaseModel):
    primary: str = "claude-sonnet-4-6"
    secondary: str = "gemini-2-5-pro"
    max_retries: int = 3
    max_tokens_per_task: int = 100_000
    max_cost_usd_per_task: float = 2.0


class Config(BaseModel):
    vault_path: Optional[str] = None
    meeting: MeetingConfig = Field(default_factory=MeetingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)


def load_config(path: Optional[Path] = None) -> Config:
    """Load config from path, ~/.vncoderc, or return defaults."""
    if path and path.exists():
        return Config(**yaml.safe_load(path.read_text(encoding="utf-8")))
    home_path = Path.home() / ".vncoderc"
    if home_path.exists():
        return Config(**yaml.safe_load(home_path.read_text(encoding="utf-8")))
    return Config()
