"""Tests for configuration management."""

from recipegrove.config import AppConfig, SecretsConfig, get_config


def test_app_config_defaults():
    """Test application config has sensible defaults."""
    config = AppConfig()
    assert config.default_model == "anthropic/claude-3.5-sonnet"
    assert config.default_theme == "auto"
    assert config.default_emoji_density == "medium"
    assert config.output_suffix == "-grove"


def test_secrets_config_initialization():
    """Test secrets config can be initialized."""
    secrets = SecretsConfig()
    # All should be None by default
    assert secrets.openrouter_api_key is None
    assert secrets.anthropic_api_key is None
    assert secrets.moonshot_api_key is None


def test_get_config():
    """Test getting application config."""
    config = get_config()
    assert isinstance(config, AppConfig)


# TODO: Add more tests once config loading is implemented
