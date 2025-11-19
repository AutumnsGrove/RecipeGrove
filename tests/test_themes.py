"""Tests for theme system."""

from recipelgrove.themes import THEMES, CuisineType, get_theme


def test_themes_exist():
    """Test predefined themes are available."""
    assert "asian" in THEMES
    assert "italian" in THEMES
    assert "mexican" in THEMES
    assert "mediterranean" in THEMES


def test_get_theme():
    """Test getting theme by name."""
    asian_theme = get_theme("asian")
    assert asian_theme is not None
    assert asian_theme.cuisine == CuisineType.ASIAN
    assert len(asian_theme.primary_emojis) > 0


def test_get_theme_case_insensitive():
    """Test theme lookup is case-insensitive."""
    assert get_theme("ASIAN") == get_theme("asian")
    assert get_theme("Italian") == get_theme("italian")


def test_invalid_theme():
    """Test getting non-existent theme returns None."""
    assert get_theme("nonexistent") is None


# TODO: Add more tests once theme logic is implemented
