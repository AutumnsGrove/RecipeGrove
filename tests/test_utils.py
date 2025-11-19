"""Tests for utility functions."""

from pathlib import Path

from recipelgrove.utils import (
    generate_cache_key,
    get_output_path,
    is_url,
    sanitize_filename,
)


def test_generate_cache_key():
    """Test cache key generation."""
    key1 = generate_cache_key("test", "data")
    key2 = generate_cache_key("test", "data")
    key3 = generate_cache_key("different", "data")

    assert key1 == key2  # Same inputs = same key
    assert key1 != key3  # Different inputs = different key
    assert len(key1) == 64  # SHA256 hash length


def test_sanitize_filename():
    """Test filename sanitization."""
    assert sanitize_filename("normal.txt") == "normal.txt"
    assert sanitize_filename("file:with:colons.txt") == "file_with_colons.txt"
    assert sanitize_filename("file/with/slashes.txt") == "file_with_slashes.txt"
    assert sanitize_filename('file"with"quotes.txt') == "file_with_quotes.txt"


def test_is_url():
    """Test URL detection."""
    assert is_url("https://example.com")
    assert is_url("http://example.com")
    assert is_url("ftp://example.com")
    assert not is_url("/path/to/file")
    assert not is_url("file.txt")


def test_get_output_path():
    """Test output path generation."""
    input_path = Path("/tmp/recipe.md")
    output = get_output_path(input_path)

    assert output.name == "recipe-grove.md"
    assert output.parent == input_path.parent


def test_get_output_path_with_custom_suffix():
    """Test output path with custom suffix."""
    input_path = Path("/tmp/recipe.md")
    output = get_output_path(input_path, suffix="-enhanced")

    assert output.name == "recipe-enhanced.md"


def test_get_output_path_with_output_dir():
    """Test output path with custom output directory."""
    input_path = Path("/tmp/recipe.md")
    output_dir = Path("/tmp/output")
    output = get_output_path(input_path, output_dir=output_dir)

    assert output.name == "recipe-grove.md"
    assert output.parent == output_dir
