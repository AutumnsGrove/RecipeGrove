"""Shared utility functions."""

import base64
import hashlib
import re
from datetime import datetime
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


def sanitize_input(text: str, max_length: int = 50000) -> str:
    """Sanitize user input before sending to LLM.

    Protects against prompt injection and other security issues.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    # Remove common prompt injection patterns (case-insensitive)
    injection_patterns = [
        r"ignore\s+(previous|all|above)\s+instructions?",
        r"disregard\s+(previous|all|above)",
        r"forget\s+(previous|all|above)",
        r"system\s*prompt",
        r"you\s+are\s+now",
        r"new\s+instructions?",
    ]

    for pattern in injection_patterns:
        text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)

    return text


def image_to_base64(image_path: Path) -> str:
    """Convert image to base64 string for embedding.

    Args:
        image_path: Path to image file

    Returns:
        Base64-encoded image data URI
    """
    with open(image_path, "rb") as f:
        image_data = f.read()
        b64_data = base64.b64encode(image_data).decode("utf-8")

    # Determine mime type
    suffix = image_path.suffix.lower()
    mime_type = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(
        suffix[1:], "image/png"
    )

    return f"data:{mime_type};base64,{b64_data}"


def detect_season() -> str:
    """Detect current season based on current date.

    Returns:
        Season name: 'winter', 'spring', 'summer', or 'fall'
    """
    month = datetime.now().month

    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:  # 9, 10, 11
        return "fall"


def get_seasonal_emojis(season: str) -> list[str]:
    """Get emoji suggestions for a season.

    Args:
        season: Season name

    Returns:
        List of appropriate emoji characters
    """
    seasonal_emojis = {
        "winter": ["❄️", "☃️", "🔥", "🍲", "🥘", "☕", "🍵", "🧣", "🎄"],
        "spring": ["🌸", "🌷", "🌺", "🌼", "🦋", "🐝", "🌱", "🌿", "🥗"],
        "summer": ["☀️", "🏖️", "🍉", "🍓", "🥤", "🍦", "🌊", "🏄", "🌴"],
        "fall": ["🍂", "🍁", "🎃", "🍎", "🍇", "🌰", "🥧", "🦃", "🌾"],
    }

    return seasonal_emojis.get(season, [])
