"""EmojiKitchen integration for custom emoji generation."""

import asyncio
import re
from pathlib import Path
from typing import Optional

from emoji_kitchen import DownloadOrchestrator, StorageManager
from rich.console import Console

console = Console()


class EmojiGenerator:
    """Wrapper for EmojiKitchen to generate custom emoji combinations."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        size: int = 512,
        delay_ms: int = 100,
    ):
        """Initialize emoji generator.

        Args:
            cache_dir: Optional directory for caching generated emojis
            size: Emoji image size in pixels (default 512)
            delay_ms: Delay between requests in milliseconds
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "recipegrove" / "emojis"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
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

        # Check if already exists
        if self.storage.file_exists(emoji1, emoji2):
            file_path = self._get_emoji_path(emoji1, emoji2)
            if file_path and file_path.exists():
                console.print(f"[green]✓ Using cached emoji {emoji1}+{emoji2}[/green]")
                return file_path

        # Try to generate
        console.print(f"[cyan]Generating emoji combination {emoji1}+{emoji2}...[/cyan]")
        success, error = await self.orchestrator.download_pair(
            emoji1, emoji2, size=self.size
        )

        if success:
            file_path = self._get_emoji_path(emoji1, emoji2)
            if file_path and file_path.exists():
                console.print(f"[green]✓ Generated emoji {emoji1}+{emoji2}[/green]")
                return file_path

        # Try fallback combinations
        if fallback and not success:
            console.print(f"[yellow]Primary combination failed, trying alternatives...[/yellow]")
            fallbacks = self.get_fallback_combinations(emoji1, emoji2)

            for alt_emoji1, alt_emoji2 in fallbacks[:3]:  # Try up to 3 alternatives
                success, error = await self.orchestrator.download_pair(
                    alt_emoji1, alt_emoji2, size=self.size
                )

                if success:
                    file_path = self._get_emoji_path(alt_emoji1, alt_emoji2)
                    if file_path and file_path.exists():
                        console.print(
                            f"[green]✓ Generated fallback emoji {alt_emoji1}+{alt_emoji2}[/green]"
                        )
                        return file_path

        console.print(f"[red]✗ Failed to generate emoji {emoji1}+{emoji2}[/red]")
        return None

    def _get_emoji_path(self, emoji1: str, emoji2: str) -> Optional[Path]:
        """Get the file path for an emoji combination.

        Args:
            emoji1: First emoji
            emoji2: Second emoji

        Returns:
            Path to emoji file if it exists
        """
        # EmojiKitchen saves as: output_dir/[emoji1]/[emoji1]_[emoji2].png
        emoji1_dir = self.cache_dir / emoji1
        if emoji1_dir.exists():
            # Look for the combination file
            pattern = f"{emoji1}_{emoji2}.png"
            for file in emoji1_dir.iterdir():
                if file.name == pattern:
                    return file

        return None

    def get_fallback_combinations(self, emoji1: str, emoji2: str) -> list[tuple[str, str]]:
        """Get alternative emoji combinations if primary fails.

        Args:
            emoji1: First base emoji
            emoji2: Second base emoji

        Returns:
            List of alternative (emoji1, emoji2) pairs to try
        """
        fallbacks = []

        # Strategy 1: Swap order
        fallbacks.append((emoji2, emoji1))

        # Strategy 2: Use simpler/more common emojis
        # Map to more common alternatives
        common_substitutes = {
            "🐉": ["🐲", "😊", "🎉"],
            "🔥": ["❤️", "⭐", "✨"],
            "🥟": ["🍜", "🍱", "🥡"],
            "🦐": ["🦞", "🐟", "🍤"],
        }

        # Try substituting emoji1
        if emoji1 in common_substitutes:
            for alt in common_substitutes[emoji1]:
                fallbacks.append((alt, emoji2))

        # Try substituting emoji2
        if emoji2 in common_substitutes:
            for alt in common_substitutes[emoji2]:
                fallbacks.append((emoji1, alt))

        # Strategy 3: Use very common emojis
        common_emojis = ["😊", "❤️", "🎉", "⭐", "✨"]
        for common in common_emojis:
            if common != emoji1 and common != emoji2:
                fallbacks.append((emoji1, common))
                fallbacks.append((emoji2, common))

        # Remove duplicates while preserving order
        seen = set()
        unique_fallbacks = []
        for pair in fallbacks:
            if pair not in seen:
                seen.add(pair)
                unique_fallbacks.append(pair)

        return unique_fallbacks[:10]  # Limit to 10 fallbacks

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
