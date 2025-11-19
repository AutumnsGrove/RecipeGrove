"""Theme definitions and rules for recipe enhancement."""

from dataclasses import dataclass
from enum import Enum


class CuisineType(Enum):
    """Supported cuisine types."""

    ASIAN = "asian"
    ITALIAN = "italian"
    MEXICAN = "mexican"
    MEDITERRANEAN = "mediterranean"
    AMERICAN = "american"
    FRENCH = "french"
    INDIAN = "indian"
    MIDDLE_EASTERN = "middle_eastern"
    GENERAL = "general"


class OccasionType(Enum):
    """Recipe occasion types."""

    ROMANTIC = "romantic"
    QUICK_MEAL = "quick_meal"
    PARTY = "party"
    COMFORT = "comfort"
    HOLIDAY = "holiday"
    EVERYDAY = "everyday"


@dataclass
class ThemeConfig:
    """Configuration for a recipe theme."""

    name: str
    cuisine: CuisineType
    primary_emojis: list[str]  # Primary emoji palette for this theme
    accent_emojis: list[str]  # Accent emojis to combine with food items
    color_palette: list[str]  # For future UI use
    description: str


# Predefined themes
THEMES = {
    "asian": ThemeConfig(
        name="Asian Cuisine",
        cuisine=CuisineType.ASIAN,
        primary_emojis=["🐉", "🏮", "🎋", "🥢"],
        accent_emojis=["🍜", "🥟", "🍱", "🍣", "🥠"],
        color_palette=["#FF6B6B", "#FFD93D", "#6BCB77"],
        description="Dragon and lantern themes with traditional Asian food items",
    ),
    "italian": ThemeConfig(
        name="Italian Cuisine",
        cuisine=CuisineType.ITALIAN,
        primary_emojis=["🇮🇹", "🍷", "🌿", "🏛️"],
        accent_emojis=["🍝", "🍕", "🧀", "🍅", "🥖"],
        color_palette=["#008C45", "#FFFFFF", "#CD212A"],
        description="Italian flag and Mediterranean symbols with classic ingredients",
    ),
    "mexican": ThemeConfig(
        name="Mexican Cuisine",
        cuisine=CuisineType.MEXICAN,
        primary_emojis=["🇲🇽", "🌵", "🎺", "☀️"],
        accent_emojis=["🌮", "🌯", "🫔", "🌶️", "🥑"],
        color_palette=["#006847", "#FFFFFF", "#CE1126"],
        description="Mexican symbols with traditional spices and ingredients",
    ),
    "mediterranean": ThemeConfig(
        name="Mediterranean Cuisine",
        cuisine=CuisineType.MEDITERRANEAN,
        primary_emojis=["🌊", "☀️", "🫒", "🏺"],
        accent_emojis=["🥗", "🐟", "🍋", "🧄", "🌿"],
        color_palette=["#0077BE", "#FFFFFF", "#FFD700"],
        description="Sea and sun themes with fresh Mediterranean ingredients",
    ),
}


def get_theme(theme_name: str) -> ThemeConfig | None:
    """Get theme configuration by name."""
    return THEMES.get(theme_name.lower())


def suggest_emojis_for_ingredient(ingredient: str, theme: ThemeConfig) -> list[str]:
    """Suggest emoji combinations for an ingredient based on theme."""
    # TODO: Implement intelligent emoji suggestion
    # - Match ingredient keywords to emoji mappings
    # - Combine with theme's accent emojis
    # - Return list of possible combinations
    return []


def suggest_emojis_for_technique(technique: str, theme: ThemeConfig) -> list[str]:
    """Suggest emoji combinations for cooking technique."""
    # TODO: Map techniques (boil, fry, bake) to appropriate emojis
    return []
