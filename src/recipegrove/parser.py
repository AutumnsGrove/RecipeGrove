"""OmniParser integration for universal document parsing."""

from pathlib import Path
from typing import Optional

from omniparser import (
    parse_document,
    OmniparserError,
    UnsupportedFormatError,
    ParsingError,
    FileReadError,
    NetworkError,
    ValidationError,
)
from rich.console import Console

console = Console()


class RecipeParser:
    """Wrapper for OmniParser to convert any format to standardized markdown."""

    def __init__(
        self,
        extract_images: bool = False,
        image_output_dir: Optional[Path] = None,
        timeout: int = 30,
    ):
        """Initialize the parser.

        Args:
            extract_images: Whether to extract images from documents
            image_output_dir: Directory to save extracted images
            timeout: Request timeout in seconds
        """
        self.extract_images = extract_images
        self.image_output_dir = image_output_dir
        self.timeout = timeout

    def parse(self, input_path: str | Path) -> str:
        """Parse input file/URL to markdown.

        Args:
            input_path: Path to file or URL to parse

        Returns:
            Standardized markdown content

        Raises:
            ValueError: If input format is not supported
            FileNotFoundError: If file does not exist
            RuntimeError: If parsing fails
        """
        input_str = str(input_path)

        # Build options
        options = {
            "extract_images": self.extract_images,
            "timeout": self.timeout,
            "clean_text": True,
        }

        if self.extract_images and self.image_output_dir:
            options["image_output_dir"] = str(self.image_output_dir)

        # Add format-specific options
        if self.is_url(input_str):
            options["parallel_image_downloads"] = True
        else:
            # Check file exists
            path = Path(input_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {input_path}")

            # Add PDF-specific options
            if self.get_file_type(path) == ".pdf":
                options["extract_tables"] = True

        try:
            console.print(f"[cyan]Parsing {input_str}...[/cyan]")
            doc = parse_document(input_str, options=options)

            console.print(
                f"[green]✓ Parsed successfully[/green] "
                f"({doc.word_count} words, {len(doc.chapters)} sections)"
            )

            return doc.content

        except UnsupportedFormatError as e:
            raise ValueError(f"Unsupported format: {e}")
        except FileReadError as e:
            raise FileNotFoundError(f"Cannot read file: {e}")
        except NetworkError as e:
            raise RuntimeError(f"Network error: {e}")
        except ValidationError as e:
            raise ValueError(f"Invalid input: {e}")
        except ParsingError as e:
            raise RuntimeError(f"Parsing failed: {e}")
        except OmniparserError as e:
            raise RuntimeError(f"Parser error: {e}")

    def is_url(self, input_path: str) -> bool:
        """Check if input is a URL."""
        return input_path.startswith(("http://", "https://"))

    def get_file_type(self, input_path: Path) -> str:
        """Detect file type from extension."""
        return input_path.suffix.lower()
