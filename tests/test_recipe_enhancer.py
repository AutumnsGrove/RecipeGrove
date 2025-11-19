"""Tests for recipe enhancer."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from recipegrove.recipe_enhancer import RecipeEnhancer


@pytest.fixture
def enhancer():
    """Create enhancer instance for testing."""
    return RecipeEnhancer()


@pytest.fixture
def sample_recipe_markdown():
    """Sample recipe markdown."""
    return """# Pad Thai

## Ingredients
- Rice noodles
- Shrimp
- Eggs
- Peanuts

## Instructions
1. Soak the rice noodles
2. Stir fry shrimp with garlic
3. Add eggs and scramble
4. Toss with noodles

## Notes
Serve hot with lime wedges"""


def test_enhancer_initialization():
    """Test enhancer can be initialized."""
    enhancer = RecipeEnhancer()
    assert enhancer is not None


def test_generate_markdown_image(enhancer):
    """Test markdown image generation."""
    result = enhancer.generate_markdown_image("/path/to/emoji.png", "test emoji")
    assert result == "![test emoji](/path/to/emoji.png)"


def test_generate_markdown_image_default_alt(enhancer):
    """Test markdown image with default alt text."""
    result = enhancer.generate_markdown_image("/path/to/emoji.png")
    assert result == "![emoji](/path/to/emoji.png)"


def test_find_title_location(enhancer, sample_recipe_markdown):
    """Test finding title location."""
    idx = enhancer.find_title_location(sample_recipe_markdown)
    assert idx == 0  # First line is "# Pad Thai"


def test_find_ingredient_locations(enhancer, sample_recipe_markdown):
    """Test finding ingredient list locations."""
    locations = enhancer.find_ingredient_locations(sample_recipe_markdown)
    assert len(locations) == 4  # 4 ingredient items


def test_find_step_locations(enhancer, sample_recipe_markdown):
    """Test finding instruction step locations."""
    locations = enhancer.find_step_locations(sample_recipe_markdown)
    assert len(locations) == 4  # 4 numbered steps


def test_find_line_containing(enhancer):
    """Test finding line with specific text."""
    lines = ["First line", "Second line with shrimp", "Third line"]
    idx = enhancer._find_line_containing(lines, "shrimp")
    assert idx == 1


def test_find_step_line(enhancer):
    """Test finding specific step line."""
    lines = ["## Instructions", "1. First step", "2. Second step", "3. Third step"]
    idx = enhancer._find_step_line(lines, 2)
    assert idx == 2  # "2. Second step"


def test_find_section(enhancer):
    """Test finding section header."""
    lines = ["# Title", "## Ingredients", "- item", "## Instructions", "1. step"]
    idx = enhancer._find_section(lines, "ingredients")
    assert idx == 1


def test_enhance_recipe(enhancer, sample_recipe_markdown, tmp_path):
    """Test recipe enhancement."""
    # Create mock placements
    placements = [
        Mock(
            location="title",
            emoji_base_1="🐉",
            emoji_base_2="🥟"
        ),
        Mock(
            location="ingredient_shrimp",
            emoji_base_1="🦐",
            emoji_base_2="🔥"
        )
    ]

    # Create temp emoji files
    emoji1_path = tmp_path / "emoji1.png"
    emoji2_path = tmp_path / "emoji2.png"
    emoji1_path.write_bytes(b"fake emoji 1")
    emoji2_path.write_bytes(b"fake emoji 2")

    emoji_paths = {
        "title": emoji1_path,
        "ingredient_shrimp": emoji2_path,
    }

    result = enhancer.enhance_recipe(sample_recipe_markdown, placements, emoji_paths)

    # Check that emojis were inserted
    assert "![🐉+🥟]" in result
    assert "![🦐+🔥]" in result
    assert "# Pad Thai" in result  # Title preserved


def test_write_output(enhancer, tmp_path):
    """Test writing enhanced recipe to file."""
    content = "# Enhanced Recipe\n\nWith emojis!"
    original_path = tmp_path / "recipe.md"
    original_path.write_text("original")

    output_path = enhancer.write_output(content, original_path)

    assert output_path.name == "recipe-grove.md"
    assert output_path.parent == tmp_path
    assert output_path.read_text() == content


def test_write_output_with_output_dir(enhancer, tmp_path):
    """Test writing to custom output directory."""
    content = "# Enhanced Recipe"
    original_path = tmp_path / "recipe.md"
    output_dir = tmp_path / "output"

    output_path = enhancer.write_output(content, original_path, output_dir=output_dir)

    assert output_path.parent == output_dir
    assert output_path.name == "recipe-grove.md"
    assert output_path.read_text() == content
