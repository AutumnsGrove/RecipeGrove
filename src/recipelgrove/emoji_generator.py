"""EmojiKitchen integration for custom emoji generation."""

import asyncio
import hashlib
import re
import shutil
from pathlib import Path
from typing import Optional

from emoji_kitchen import DownloadOrchestrator, StorageManager
from rich.console import Console

from recipelgrove.utils import emoji_pair_to_filename, emoji_to_codepoint

console = Console()

# =============================================================================
# EmojiKitchen Combination Compatibility
# =============================================================================
#
# IMPORTANT FINDING: Not all emoji combinations exist in EmojiKitchen.
#
# Through testing, we discovered that "base emojis" (faces, hearts, etc.)
# have near-100% compatibility with other emojis, while arbitrary emoji+emoji
# combinations (like 🇹🇭+🍜 or 🦐+🌟) may not exist.
#
# RELIABLE BASE EMOJIS (work with almost everything):
#   😊 😂 🥺 😍 🤔 - Face emojis
#   ❤️ - Heart
#   🔥 - Fire
#   ⭐ - Star
#
# When a requested combination fails, we fall back to pairing one of the
# original emojis with a reliable base emoji to ensure we always get a result.
#
# Test results: 112/112 combinations worked when pairing food/flag emojis
# with base emojis (😊, ❤️, 🔥, ⭐).
# =============================================================================

# Super reliable base emojis that combine with almost anything
# These are the "safe" emojis to fall back to
RELIABLE_BASE_EMOJIS = ["😊", "❤️", "🔥", "⭐", "😂", "🥺", "😍", "🤔"]

# Minimum file size for a valid emoji (empty/error images are smaller)
MIN_VALID_FILE_SIZE = 1000  # 1KB minimum (for 80px images)

# MD5 hash of the EmojiKitchen "Not Found" placeholder image
# This image is returned when a combination doesn't exist
# Note: Hash differs by image size - this is for 80px
NOT_FOUND_PLACEHOLDER_HASH = "b1d323a07c4ba79fa1f220841797b5a1"


class EmojiGenerator:
    """Wrapper for EmojiKitchen to generate custom emoji combinations."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        size: int = 80,
        delay_ms: int = 100,
    ):
        """Initialize emoji generator.

        Args:
            cache_dir: Optional directory for caching downloaded emojis
            output_dir: Directory to save generated emojis (sidecar folder)
            size: Emoji image size in pixels (default 80 for inline display)
            delay_ms: Delay between requests in milliseconds
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "recipelgrove" / "emojis"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir  # Sidecar folder for final output
        self.size = size

        # Initialize EmojiKitchen orchestrator
        self.orchestrator = DownloadOrchestrator(
            output_dir=self.cache_dir,
            log_dir=self.cache_dir / "logs",
            delay_ms=delay_ms,
            max_concurrent=10,
            skip_existing=True,  # Built-in caching
        )

        # Storage manager for checking files
        self.storage = StorageManager(self.cache_dir, filename_format="emoji")

    def set_output_dir(self, output_dir: Path) -> None:
        """Set the output directory for generated emojis.

        Args:
            output_dir: Directory to save generated emojis
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_combination(
        self, emoji1: str, emoji2: str, fallback: bool = True
    ) -> Optional[Path]:
        """Generate custom emoji combination.

        Args:
            emoji1: First base emoji
            emoji2: Second base emoji
            fallback: If True, try alternative combinations on failure

        Returns:
            Path to generated emoji image or None if generation failed

        Raises:
            ValueError: If emojis are invalid
        """
        # Validate emojis
        if not self.is_valid_emoji(emoji1) or not self.is_valid_emoji(emoji2):
            raise ValueError(f"Invalid emoji characters: {emoji1}, {emoji2}")

        # Check if already exists in output directory and is valid
        output_path = self._get_output_path(emoji1, emoji2)
        if output_path and self._is_valid_emoji_file(output_path):
            console.print(f"[green]✓ Using cached emoji {emoji1}+{emoji2}[/green]")
            return output_path

        # Try to download primary combination
        console.print(f"[cyan]Generating emoji combination {emoji1}+{emoji2}...[/cyan]")
        success, error = await self.orchestrator.download_pair(
            emoji1, emoji2, size=self.size
        )

        if success:
            cache_path = self._get_cache_path(emoji1, emoji2)
            if self._is_valid_emoji_file(cache_path):
                output_path = self._copy_to_output(cache_path, emoji1, emoji2)
                if output_path and self._is_valid_emoji_file(output_path):
                    console.print(f"[green]✓ Generated emoji {emoji1}+{emoji2}[/green]")
                    return output_path

        # Primary failed or produced invalid file - try fallbacks
        if fallback:
            console.print(f"[yellow]Combination {emoji1}+{emoji2} not available, trying alternatives...[/yellow]")
            fallbacks = self.get_fallback_combinations(emoji1, emoji2)

            for alt_emoji1, alt_emoji2 in fallbacks:
                # Check if we already have this one cached and valid
                alt_output = self._get_output_path(alt_emoji1, alt_emoji2)
                if alt_output and self._is_valid_emoji_file(alt_output):
                    console.print(
                        f"[green]✓ Using fallback {alt_emoji1}+{alt_emoji2}[/green]"
                    )
                    return alt_output

                # Try to download
                success, error = await self.orchestrator.download_pair(
                    alt_emoji1, alt_emoji2, size=self.size
                )

                if success:
                    cache_path = self._get_cache_path(alt_emoji1, alt_emoji2)
                    if self._is_valid_emoji_file(cache_path):
                        output_path = self._copy_to_output(cache_path, alt_emoji1, alt_emoji2)
                        if output_path and self._is_valid_emoji_file(output_path):
                            console.print(
                                f"[green]✓ Generated fallback {alt_emoji1}+{alt_emoji2}[/green]"
                            )
                            return output_path

        console.print(f"[red]✗ Failed to generate emoji {emoji1}+{emoji2}[/red]")
        return None

    def _copy_to_output(self, cache_path: Path, emoji1: str, emoji2: str) -> Optional[Path]:
        """Copy emoji from cache to output directory with codepoint filename.

        Args:
            cache_path: Path to cached emoji file
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            Path to output file or None
        """
        if not self.output_dir:
            # No output dir set, return cache path (backwards compatibility)
            return cache_path

        self.output_dir.mkdir(parents=True, exist_ok=True)
        filename = emoji_pair_to_filename(emoji1, emoji2)
        output_path = self.output_dir / filename

        try:
            shutil.copy2(cache_path, output_path)
            return output_path
        except Exception as e:
            console.print(f"[yellow]⚠ Failed to copy emoji: {e}[/yellow]")
            return None

    def _is_valid_emoji_file(self, file_path: Path) -> bool:
        """Check if emoji file is valid (not empty/error/placeholder).

        Args:
            file_path: Path to check

        Returns:
            True if file exists, is large enough, and is not the Not Found placeholder
        """
        if not file_path or not file_path.exists():
            return False

        if file_path.stat().st_size < MIN_VALID_FILE_SIZE:
            return False

        # Check if it's the "Not Found" placeholder image
        file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
        if file_hash == NOT_FOUND_PLACEHOLDER_HASH:
            console.print(f"[yellow]⚠ Detected 'Not Found' placeholder for {file_path.name}[/yellow]")
            return False

        return True

    def _get_output_path(self, emoji1: str, emoji2: str) -> Optional[Path]:
        """Get the output path for an emoji combination.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            Path to output file or None
        """
        if not self.output_dir:
            return None

        filename = emoji_pair_to_filename(emoji1, emoji2)
        return self.output_dir / filename

    def _get_cache_path(self, emoji1: str, emoji2: str) -> Optional[Path]:
        """Get the cache path for an emoji combination (EmojiKitchen format).

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            Path to cached file or None
        """
        # EmojiKitchen saves as: cache_dir/[emoji1]/[emoji1]_[emoji2].png
        emoji1_dir = self.cache_dir / emoji1
        if emoji1_dir.exists():
            pattern = f"{emoji1}_{emoji2}.png"
            for file in emoji1_dir.iterdir():
                if file.name == pattern:
                    return file
        return None


    def get_fallback_combinations(self, emoji1: str, emoji2: str) -> list[tuple[str, str]]:
        """Get alternative emoji combinations if primary fails.

        Uses super reliable base emojis that work with almost anything.

        Args:
            emoji1: First base emoji
            emoji2: Second base emoji

        Returns:
            List of alternative (emoji1, emoji2) pairs to try
        """
        fallbacks = []

        # Strategy 1: Swap order (sometimes works)
        fallbacks.append((emoji2, emoji1))

        # Strategy 2: Pair each original emoji with reliable bases
        # These emojis combine successfully with almost everything
        for reliable in RELIABLE_BASE_EMOJIS:
            if reliable != emoji1 and reliable != emoji2:
                # Try emoji1 with reliable (both orders)
                fallbacks.append((emoji1, reliable))
                fallbacks.append((reliable, emoji1))
                # Try emoji2 with reliable (both orders)
                fallbacks.append((emoji2, reliable))
                fallbacks.append((reliable, emoji2))

        # Strategy 3: Ultimate fallback - just two reliable emojis
        # If nothing works, at least give them something
        fallbacks.append(("😊", "❤️"))
        fallbacks.append(("🔥", "❤️"))
        fallbacks.append(("⭐", "😊"))

        # Remove duplicates while preserving order
        seen = set()
        unique_fallbacks = []
        for pair in fallbacks:
            if pair not in seen and pair != (emoji1, emoji2):
                seen.add(pair)
                unique_fallbacks.append(pair)

        return unique_fallbacks[:20]  # Try more fallbacks

    def is_valid_emoji(self, emoji: str) -> bool:
        """Check if string is a valid emoji.

        Args:
            emoji: String to validate

        Returns:
            True if valid emoji character
        """
        if not emoji or len(emoji) == 0:
            return False

        # Check if it contains emoji characters
        # Extended emoji ranges covering most emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # geometric shapes
            "\U0001F800-\U0001F8FF"  # supplemental arrows
            "\U0001F900-\U0001F9FF"  # supplemental symbols (includes food emojis)
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            "\U00002600-\U000026FF"  # miscellaneous symbols
            "\U00002700-\U000027BF"  # dingbats
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE,
        )

        return bool(emoji_pattern.search(emoji))

    def clear_cache(self):
        """Clear emoji cache directory."""
        if self.cache_dir.exists():
            import shutil

            console.print(f"[yellow]Clearing emoji cache: {self.cache_dir}[/yellow]")
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True)
            console.print("[green]✓ Cache cleared[/green]")
