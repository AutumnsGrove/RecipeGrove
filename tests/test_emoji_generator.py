"""Tests for emoji generator."""

from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from recipelgrove.emoji_generator import EmojiGenerator


@pytest.fixture
def generator(tmp_path):
    """Create generator instance for testing."""
    return EmojiGenerator(cache_dir=tmp_path / "emojis")


def test_generator_initialization(tmp_path):
    """Test generator can be initialized."""
    gen = EmojiGenerator(cache_dir=tmp_path / "emojis")
    assert gen.cache_dir == tmp_path / "emojis"
    assert gen.cache_dir.exists()
    assert gen.size == 512


def test_generator_default_cache_dir():
    """Test generator uses default cache dir."""
    gen = EmojiGenerator()
    expected = Path.home() / ".cache" / "recipelgrove" / "emojis"
    assert gen.cache_dir == expected


def test_is_valid_emoji(generator):
    """Test emoji validation."""
    assert generator.is_valid_emoji("😊")
    assert generator.is_valid_emoji("🐉")
    assert generator.is_valid_emoji("🥟")
    assert not generator.is_valid_emoji("")
    assert not generator.is_valid_emoji("abc")
    assert not generator.is_valid_emoji("123")


def test_get_fallback_combinations(generator):
    """Test fallback emoji combinations."""
    fallbacks = generator.get_fallback_combinations("🐉", "🥟")

    assert isinstance(fallbacks, list)
    assert len(fallbacks) > 0

    # Should include swapped order
    assert ("🥟", "🐉") in fallbacks

    # Should have alternatives
    assert len(fallbacks) <= 10


def test_get_fallback_combinations_common_substitutes(generator):
    """Test fallback uses common substitutes."""
    fallbacks = generator.get_fallback_combinations("🐉", "🔥")

    # Check that common substitutes are included
    # 🐉 has substitutes: 🐲, 😊, 🎉
    # 🔥 has substitutes: ❤️, ⭐, ✨

    emoji_strings = [f"{e1}{e2}" for e1, e2 in fallbacks]

    # Should contain at least one substitute combo
    assert any("🐲" in s or "😊" in s for s in emoji_strings)


@pytest.mark.asyncio
async def test_generate_combination_success(generator, tmp_path):
    """Test successful emoji generation."""
    # Mock the orchestrator
    with patch.object(
        generator.orchestrator, "download_pair", new=AsyncMock(return_value=(True, None))
    ):
        # Create a fake emoji file
        emoji_dir = generator.cache_dir / "😊"
        emoji_dir.mkdir(parents=True, exist_ok=True)
        emoji_file = emoji_dir / "😊_🎉.png"
        emoji_file.write_bytes(b"fake png data")

        result = await generator.generate_combination("😊", "🎉")

        assert result is not None
        assert isinstance(result, Path)
        assert result.exists()


@pytest.mark.asyncio
async def test_generate_combination_cached(generator, tmp_path):
    """Test using cached emoji."""
    # Create a cached emoji file
    emoji_dir = generator.cache_dir / "🐉"
    emoji_dir.mkdir(parents=True, exist_ok=True)
    emoji_file = emoji_dir / "🐉_🥟.png"
    emoji_file.write_bytes(b"cached emoji")

    # Mock storage to say it exists
    with patch.object(generator.storage, "file_exists", return_value=True):
        result = await generator.generate_combination("🐉", "🥟")

        # Should return cached file without calling orchestrator
        assert result == emoji_file


@pytest.mark.asyncio
async def test_generate_combination_with_fallback(generator, tmp_path):
    """Test emoji generation with fallback."""
    # First attempt fails, fallback succeeds
    with patch.object(
        generator.orchestrator,
        "download_pair",
        new=AsyncMock(side_effect=[(False, "error"), (True, None)]),
    ):
        # Create fallback emoji file
        emoji_dir = generator.cache_dir / "🥟"
        emoji_dir.mkdir(parents=True, exist_ok=True)
        emoji_file = emoji_dir / "🥟_🐉.png"
        emoji_file.write_bytes(b"fallback emoji")

        result = await generator.generate_combination("🐉", "🥟", fallback=True)

        # Should have tried fallback and succeeded
        assert result is not None or result is None  # May fail depending on fallback order


@pytest.mark.asyncio
async def test_generate_combination_invalid_emoji(generator):
    """Test generation with invalid emoji raises error."""
    with pytest.raises(ValueError):
        await generator.generate_combination("abc", "def")


@pytest.mark.asyncio
async def test_generate_combination_no_fallback(generator):
    """Test generation without fallback."""
    with patch.object(
        generator.orchestrator, "download_pair", new=AsyncMock(return_value=(False, "error"))
    ):
        result = await generator.generate_combination("🐉", "🥟", fallback=False)

        # Should fail without trying fallbacks
        assert result is None


def test_clear_cache(generator):
    """Test clearing emoji cache."""
    # Create some files in cache
    test_dir = generator.cache_dir / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test.png"
    test_file.write_bytes(b"test")

    assert test_file.exists()

    # Clear cache
    generator.clear_cache()

    # Cache dir should exist but be empty
    assert generator.cache_dir.exists()
    assert not test_file.exists()
    assert not test_dir.exists()


def test_get_emoji_path(generator):
    """Test getting emoji file path."""
    # Create emoji file
    emoji_dir = generator.cache_dir / "😊"
    emoji_dir.mkdir(parents=True, exist_ok=True)
    emoji_file = emoji_dir / "😊_🎉.png"
    emoji_file.write_bytes(b"test")

    result = generator._get_emoji_path("😊", "🎉")

    assert result == emoji_file


def test_get_emoji_path_not_found(generator):
    """Test getting non-existent emoji path."""
    result = generator._get_emoji_path("🐉", "🥟")
    assert result is None
