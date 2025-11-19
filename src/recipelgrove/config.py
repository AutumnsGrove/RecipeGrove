"""Configuration management for RecipeGrove."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()


class SecretsConfig(BaseModel):
    """API keys and secrets configuration."""

    openrouter_api_key: str | None = Field(None, alias="openrouter_api_key")
    anthropic_api_key: str | None = Field(None, alias="anthropic_api_key")
    moonshot_api_key: str | None = Field(None, alias="moonshot_api_key")

    class Config:
        populate_by_name = True


class AppConfig(BaseModel):
    """Application configuration."""

    default_model: str = "anthropic/claude-3.5-sonnet"
    default_theme: str = "auto"
    default_emoji_density: str = "medium"
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".cache" / "recipelgrove")
    output_suffix: str = "-grove"


def load_secrets(secrets_path: Path | None = None) -> SecretsConfig:
    """Load secrets from secrets.json or environment variables.

    Args:
        secrets_path: Optional path to secrets.json file

    Returns:
        SecretsConfig with loaded secrets
    """
    secrets_data = {}

    # Try loading from secrets.json
    if secrets_path is None:
        secrets_path = Path.cwd() / "secrets.json"

    if secrets_path.exists():
        try:
            with open(secrets_path) as f:
                secrets_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse secrets.json: {e}")

    # Override with environment variables if present
    env_keys = {
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "moonshot_api_key": os.getenv("MOONSHOT_API_KEY"),
    }

    for key, value in env_keys.items():
        if value:
            secrets_data[key] = value

    return SecretsConfig(**secrets_data)


def get_config() -> AppConfig:
    """Get application configuration."""
    return AppConfig()


def validate_config() -> tuple[bool, list[str]]:
    """Validate configuration and return any errors.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    secrets = load_secrets()

    if not secrets.openrouter_api_key:
        errors.append(
            "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable "
            "or add to secrets.json"
        )

    return len(errors) == 0, errors
