"""Shared utility functions."""

import hashlib
from pathlib import Path


def emoji_to_codepoint(emoji: str) -> str:
    """Convert emoji character(s) to Unicode codepoint string.

    Args:
        emoji: Emoji character(s)

    Returns:
        Codepoint string like '1f60a' or '1f1fa-1f1f8' for multi-codepoint emojis
    """
    codepoints = []
    for char in emoji:
        cp = ord(char)
        # Skip variation selectors and zero-width joiners for cleaner names
        if cp not in (0xFE0F, 0x200D):
            codepoints.append(f"{cp:x}")
    return "-".join(codepoints) if codepoints else "unknown"


def emoji_pair_to_filename(emoji1: str, emoji2: str) -> str:
    """Convert emoji pair to filesystem-safe filename.

    Args:
        emoji1: First emoji
        emoji2: Second emoji

    Returns:
        Safe filename like '1f60a_1f389.png'
    """
    cp1 = emoji_to_codepoint(emoji1)
    cp2 = emoji_to_codepoint(emoji2)
    return f"{cp1}_{cp2}.png"


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
