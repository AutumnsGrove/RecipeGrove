"""Tests for recipe parser."""

from recipelgrove.parser import RecipeParser


def test_parser_initialization():
    """Test parser can be initialized."""
    parser = RecipeParser()
    assert parser is not None


def test_is_url():
    """Test URL detection."""
    parser = RecipeParser()
    assert parser.is_url("https://example.com/recipe")
    assert parser.is_url("http://example.com/recipe")
    assert not parser.is_url("/path/to/file.pdf")
    assert not parser.is_url("recipe.txt")


# TODO: Add more tests once parser is implemented
