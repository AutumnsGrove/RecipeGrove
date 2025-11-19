"""Configuration management for RecipeGrove."""

import json
import os
from pathlib import Path
from typing import Literal

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


class UserPreferences(BaseModel):
    """User preferences from ~/.recipegroverc."""

    favorite_emojis: list[str] = Field(default_factory=list)
    avoid_emojis: list[str] = Field(default_factory=list)
    default_emoji_density: str = "medium"
    default_emoji_path_mode: Literal["relative", "absolute", "base64", "unicode"] = "relative"
    default_export_format: str = "markdown"
    cache_location: Path | None = None
    enable_seasonal_themes: bool = True
    enable_shopping_lists: bool = False


class AppConfig(BaseModel):
    """Application configuration."""

    default_model: str = "anthropic/claude-3.5-sonnet"
    default_theme: str = "auto"
    default_emoji_density: str = "medium"
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".cache" / "recipegrove")
    output_suffix: str = "-grove"
    emoji_path_mode: Literal["relative", "absolute", "base64", "unicode"] = "relative"
    export_format: str = "markdown"


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


def load_user_preferences() -> UserPreferences:
    """Load user preferences from ~/.recipegroverc.

    Returns:
        UserPreferences object with loaded or default preferences
    """
    rc_path = Path.home() / ".recipegroverc"

    if not rc_path.exists():
        return UserPreferences()

    try:
        with open(rc_path) as f:
            data = json.load(f)

        # Convert cache_location string to Path if present
        if "cache_location" in data and data["cache_location"]:
            data["cache_location"] = Path(data["cache_location"]).expanduser()

        return UserPreferences(**data)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: Could not parse ~/.recipegroverc: {e}")
        return UserPreferences()


def get_config(preferences: UserPreferences | None = None) -> AppConfig:
    """Get application configuration.

    Args:
        preferences: Optional user preferences to override defaults

    Returns:
        AppConfig with user preferences applied
    """
    if preferences is None:
        preferences = load_user_preferences()

    config = AppConfig()

    # Apply user preferences
    if preferences.default_emoji_density:
        config.default_emoji_density = preferences.default_emoji_density
    if preferences.default_emoji_path_mode:
        config.emoji_path_mode = preferences.default_emoji_path_mode
    if preferences.default_export_format:
        config.export_format = preferences.default_export_format
    if preferences.cache_location:
        config.cache_dir = preferences.cache_location

    return config


class Config(BaseModel):
    """Combined configuration object."""

    secrets: SecretsConfig
    app: AppConfig
    preferences: UserPreferences


def load_config(secrets_path: Path | None = None) -> Config:
    """Load complete configuration.

    Args:
        secrets_path: Optional path to secrets.json file

    Returns:
        Config object with secrets, app config, and user preferences
    """
    preferences = load_user_preferences()
    return Config(
        secrets=load_secrets(secrets_path),
        app=get_config(preferences),
        preferences=preferences,
    )


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
