from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "smartops.db")
MODEL_ID: str = os.getenv("SMARTOPS_MODEL", "claude-sonnet-4-6")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
