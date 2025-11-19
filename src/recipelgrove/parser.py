"""OmniParser integration for universal document parsing."""

from pathlib import Path


class RecipeParser:
    """Wrapper for OmniParser to convert any format to standardized markdown."""

    def __init__(self):
        """Initialize the parser."""
        # TODO: Import and initialize OmniParser
        pass

    def parse(self, input_path: str | Path) -> str:
        """Parse input file/URL to markdown.

        Args:
            input_path: Path to file or URL to parse

        Returns:
            Standardized markdown content

        Raises:
            ValueError: If input format is not supported
            FileNotFoundError: If file does not exist
        """
        # TODO: Implement OmniParser integration
        # - Detect input type (URL, PDF, text, etc.)
        # - Call OmniParser with appropriate options
        # - Return standardized markdown
        raise NotImplementedError("Parser integration pending")

    def is_url(self, input_path: str) -> bool:
        """Check if input is a URL."""
        return input_path.startswith(("http://", "https://"))

    def get_file_type(self, input_path: Path) -> str:
        """Detect file type from extension."""
        return input_path.suffix.lower()
