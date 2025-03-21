"""Configuration settings for the BCBA MCQ Generator."""

from dotenv import load_dotenv
import logging
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
PROMPTS_DIR = BASE_DIR / "prompts"

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    class Config:
        env_file = f"{BASE_DIR}/.env"

@lru_cache
def get_settings() -> Settings:
    logging.info("Loading settings")
    return Settings()