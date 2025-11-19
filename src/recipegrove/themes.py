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


class SeasonType(Enum):
    """Season types for seasonal themes."""

    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"


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

# Seasonal themes
SEASONAL_THEMES = {
    "winter": ThemeConfig(
        name="Winter Comfort",
        cuisine=CuisineType.GENERAL,
        primary_emojis=["❄️", "☃️", "🔥", "🎄"],
        accent_emojis=["🍲", "🥘", "☕", "🍵", "🥧", "🎁"],
        color_palette=["#4A90E2", "#FFFFFF", "#D0021B"],
        description="Cozy winter themes with comfort foods and warm drinks",
    ),
    "spring": ThemeConfig(
        name="Spring Fresh",
        cuisine=CuisineType.GENERAL,
        primary_emojis=["🌸", "🌷", "🦋", "🌱"],
        accent_emojis=["🥗", "🌿", "🌼", "🐝", "🍓"],
        color_palette=["#B8E986", "#FFE66D", "#FF6B6B"],
        description="Fresh spring themes with light dishes and vibrant colors",
    ),
    "summer": ThemeConfig(
        name="Summer Vibes",
        cuisine=CuisineType.GENERAL,
        primary_emojis=["☀️", "🏖️", "🌊", "🌴"],
        accent_emojis=["🍉", "🍓", "🥤", "🍦", "🏄"],
        color_palette=["#FFD93D", "#6BCB77", "#4D96FF"],
        description="Bright summer themes with refreshing foods and drinks",
    ),
    "fall": ThemeConfig(
        name="Autumn Harvest",
        cuisine=CuisineType.GENERAL,
        primary_emojis=["🍂", "🍁", "🎃", "🌾"],
        accent_emojis=["🍎", "🍇", "🌰", "🥧", "🦃"],
        color_palette=["#FF6B35", "#F7931E", "#C1292E"],
        description="Harvest themes with autumn ingredients and warm colors",
    ),
}


def get_theme(theme_name: str) -> ThemeConfig | None:
    """Get theme configuration by name."""
    return THEMES.get(theme_name.lower())


def get_seasonal_theme(season: str) -> ThemeConfig | None:
    """Get seasonal theme configuration.

    Args:
        season: Season name ('winter', 'spring', 'summer', 'fall')

    Returns:
        ThemeConfig for the season or None
    """
    return SEASONAL_THEMES.get(season.lower())


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
