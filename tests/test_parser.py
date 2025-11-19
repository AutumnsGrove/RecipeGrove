"""Tests for recipe parser."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from recipelgrove.parser import RecipeParser


def test_parser_initialization():
    """Test parser can be initialized."""
    parser = RecipeParser()
    assert parser is not None
    assert parser.extract_images is False
    assert parser.timeout == 30


def test_parser_with_options():
    """Test parser initialization with custom options."""
    parser = RecipeParser(
        extract_images=True, image_output_dir=Path("/tmp/images"), timeout=60
    )
    assert parser.extract_images is True
    assert parser.image_output_dir == Path("/tmp/images")
    assert parser.timeout == 60


def test_is_url():
    """Test URL detection."""
    parser = RecipeParser()
    assert parser.is_url("https://example.com/recipe")
    assert parser.is_url("http://example.com/recipe")
    assert not parser.is_url("/path/to/file.pdf")
    assert not parser.is_url("recipe.txt")


def test_get_file_type():
    """Test file type detection."""
    parser = RecipeParser()
    assert parser.get_file_type(Path("recipe.pdf")) == ".pdf"
    assert parser.get_file_type(Path("recipe.txt")) == ".txt"
    assert parser.get_file_type(Path("recipe.md")) == ".md"


@patch("recipelgrove.parser.parse_document")
def test_parse_url(mock_parse):
    """Test parsing URL."""
    mock_doc = Mock()
    mock_doc.content = "# Test Recipe\n\nIngredients..."
    mock_doc.word_count = 100
    mock_doc.chapters = []
    mock_parse.return_value = mock_doc

    parser = RecipeParser()
    result = parser.parse("https://example.com/recipe")

    assert result == "# Test Recipe\n\nIngredients..."
    mock_parse.assert_called_once()
    call_args = mock_parse.call_args
    assert call_args[0][0] == "https://example.com/recipe"
    assert call_args[1]["options"]["parallel_image_downloads"] is True


@patch("recipelgrove.parser.parse_document")
def test_parse_file(mock_parse, tmp_path):
    """Test parsing file."""
    # Create temp file
    test_file = tmp_path / "recipe.txt"
    test_file.write_text("Test recipe content")

    mock_doc = Mock()
    mock_doc.content = "# Test Recipe\n\nTest content"
    mock_doc.word_count = 50
    mock_doc.chapters = []
    mock_parse.return_value = mock_doc

    parser = RecipeParser()
    result = parser.parse(test_file)

    assert result == "# Test Recipe\n\nTest content"
    mock_parse.assert_called_once()


@patch("recipelgrove.parser.parse_document")
def test_parse_nonexistent_file(mock_parse):
    """Test parsing non-existent file raises error."""
    parser = RecipeParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("/nonexistent/file.pdf")


@patch("recipelgrove.parser.parse_document")
def test_parse_pdf_with_options(mock_parse, tmp_path):
    """Test parsing PDF includes PDF-specific options."""
    # Create temp PDF
    test_pdf = tmp_path / "recipe.pdf"
    test_pdf.write_bytes(b"%PDF-1.4 fake pdf")

    mock_doc = Mock()
    mock_doc.content = "# PDF Recipe"
    mock_doc.word_count = 75
    mock_doc.chapters = []
    mock_parse.return_value = mock_doc

    parser = RecipeParser()
    parser.parse(test_pdf)

    call_args = mock_parse.call_args
    assert call_args[1]["options"]["extract_tables"] is True
