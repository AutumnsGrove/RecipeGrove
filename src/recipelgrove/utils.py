"""Shared utility functions."""

import hashlib
from pathlib import Path


def generate_cache_key(*args: str) -> str:
    """Generate cache key from arguments.

    Args:
        *args: Strings to hash for cache key

    Returns:
        Hash string suitable for cache key
    """
    content = "|".join(args)
    return hashlib.sha256(content.encode()).hexdigest()


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, creating if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def is_url(path: str) -> bool:
    """Check if string is a URL."""
    return path.startswith(("http://", "https://", "ftp://"))


def get_output_path(
    input_path: Path, suffix: str = "-grove", output_dir: Path | None = None
) -> Path:
    """Generate output path for enhanced recipe.

    Args:
        input_path: Original input file path
        suffix: Suffix to add before extension
        output_dir: Optional output directory

    Returns:
        Path for output file
    """
    output_name = f"{input_path.stem}{suffix}{input_path.suffix}"

    if output_dir:
        return output_dir / output_name
    else:
        return input_path.parent / output_name


def format_error_message(error: Exception, context: str = "") -> str:
    """Format error message for user display.

    Args:
        error: Exception that occurred
        context: Additional context about where error occurred

    Returns:
        Formatted error message
    """
    msg = f"Error: {type(error).__name__}: {str(error)}"
    if context:
        msg = f"{context}\n{msg}"
    return msg
