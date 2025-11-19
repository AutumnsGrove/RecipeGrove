"""Recipe enhancement - emoji insertion into markdown."""

import re
import shutil
from pathlib import Path
from typing import Literal, Optional

from rich.console import Console
from recipegrove.utils import image_to_base64

console = Console()


class RecipeEnhancer:
    """Inserts emojis into recipe markdown at specified locations."""

    def __init__(
        self,
        emoji_path_mode: Literal["relative", "absolute", "base64", "unicode"] = "relative"
    ):
        """Initialize recipe enhancer.

        Args:
            emoji_path_mode: How to handle emoji paths in output
                - relative: Copy emojis to ./grove-emojis/ and use relative paths
                - absolute: Use absolute paths (current behavior)
                - base64: Embed emojis as base64 data URIs
                - unicode: Just use unicode emoji, no images
        """
        self.emoji_path_mode = emoji_path_mode
        self.emoji_output_dir: Optional[Path] = None

    def enhance_recipe(
        self,
        markdown_content: str,
        emoji_placements: list,  # list[EmojiPlacement] from analyzer
        emoji_paths: dict[str, Path | str],  # mapping of placement location to emoji path
    ) -> str:
        """Insert emojis into recipe markdown.

        Args:
            markdown_content: Original recipe markdown
            emoji_placements: List of placement instructions
            emoji_paths: Generated emoji images mapped to placement locations

        Returns:
            Enhanced markdown with emojis inserted
        """
        console.print(
            f"[cyan]Enhancing recipe with {len(emoji_placements)} emoji placements...[/cyan]"
        )

        lines = markdown_content.split("\n")

        # Process each placement
        for placement in emoji_placements:
            location = placement.location
            emoji_path = emoji_paths.get(location)

            if not emoji_path:
                console.print(f"[yellow]⚠ No emoji generated for {location}[/yellow]")
                continue

            # Generate emoji markdown
            emoji_md = self.generate_markdown_image(
                str(emoji_path),
                alt_text=f"{placement.emoji_base_1}+{placement.emoji_base_2}"
            )

            # Determine where to insert based on location type
            if location == "title":
                # Insert at title
                title_idx = self.find_title_location(markdown_content)
                if title_idx is not None and title_idx < len(lines):
                    lines[title_idx] = f"{lines[title_idx]} {emoji_md}"

            elif location.startswith("ingredient"):
                # Extract ingredient name and find matching line
                ingredient_name = location.replace("ingredient_", "").replace("_", " ")
                ingredient_idx = self._find_line_containing(lines, ingredient_name)
                if ingredient_idx is not None:
                    lines[ingredient_idx] = f"{lines[ingredient_idx]} {emoji_md}"

            elif location.startswith("step"):
                # Extract step number
                match = re.match(r"step_(\d+)", location)
                if match:
                    step_num = int(match.group(1))
                    step_idx = self._find_step_line(lines, step_num)
                    if step_idx is not None:
                        lines[step_idx] = f"{lines[step_idx]} {emoji_md}"

            elif location in ["serving", "serving_suggestion", "notes", "tips"]:
                # Find section and add at end
                section_idx = self._find_section(lines, location)
                if section_idx is not None:
                    # Add emoji to section header or first line
                    if section_idx < len(lines):
                        lines[section_idx] = f"{lines[section_idx]} {emoji_md}"

            else:
                # Generic search for location keyword
                keyword_idx = self._find_line_containing(lines, location)
                if keyword_idx is not None:
                    lines[keyword_idx] = f"{lines[keyword_idx]} {emoji_md}"

        enhanced = "\n".join(lines)
        console.print(f"[green]✓ Recipe enhanced with emojis[/green]")
        return enhanced

    def generate_markdown_image(
        self,
        emoji_path: str | Path,
        alt_text: str = "emoji"
    ) -> str:
        """Generate markdown image syntax for emoji.

        Args:
            emoji_path: Path or URL to emoji image
            alt_text: Alt text for accessibility

        Returns:
            Markdown image syntax
        """
        if self.emoji_path_mode == "unicode":
            # Just use the alt text as unicode emoji
            return alt_text.split("+")[0] if "+" in alt_text else alt_text

        if self.emoji_path_mode == "base64":
            # Embed as base64 data URI
            if isinstance(emoji_path, (str, Path)):
                path_obj = Path(emoji_path) if isinstance(emoji_path, str) else emoji_path
                if path_obj.exists():
                    base64_data = image_to_base64(path_obj)
                    return f"![{alt_text}]({base64_data})"
            return f"![{alt_text}]({emoji_path})"

        if self.emoji_path_mode == "relative":
            # Use relative path (will be copied to grove-emojis/)
            if isinstance(emoji_path, Path):
                emoji_filename = emoji_path.name
                return f"![{alt_text}](./grove-emojis/{emoji_filename})"
            return f"![{alt_text}]({emoji_path})"

        # absolute mode (default/original behavior)
        if isinstance(emoji_path, Path):
            emoji_path = str(emoji_path.absolute())
        return f"![{alt_text}]({emoji_path})"

    def _copy_emojis_to_relative_dir(
        self,
        emoji_paths: dict[str, Path | str],
        output_path: Path
    ) -> None:
        """Copy emoji files to relative directory for portability.

        Args:
            emoji_paths: Mapping of locations to emoji paths
            output_path: Path to output recipe file
        """
        # Create grove-emojis directory next to output file
        emoji_dir = output_path.parent / "grove-emojis"
        emoji_dir.mkdir(parents=True, exist_ok=True)
        self.emoji_output_dir = emoji_dir

        # Copy each emoji file
        for location, emoji_path in emoji_paths.items():
            if isinstance(emoji_path, Path) and emoji_path.exists():
                dest_path = emoji_dir / emoji_path.name
                if not dest_path.exists():
                    shutil.copy2(emoji_path, dest_path)
                    console.print(f"[dim]Copied emoji: {emoji_path.name}[/dim]")

    def find_title_location(self, markdown: str) -> Optional[int]:
        """Find position to insert title emoji."""
        # Look for first # heading
        lines = markdown.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("# "):
                return i
        return None

    def _find_line_containing(self, lines: list[str], text: str) -> Optional[int]:
        """Find line number containing specific text (case-insensitive).

        Args:
            lines: List of markdown lines
            text: Text to search for

        Returns:
            Line index or None
        """
        search_text = text.lower()
        for i, line in enumerate(lines):
            if search_text in line.lower():
                return i
        return None

    def _find_step_line(self, lines: list[str], step_num: int) -> Optional[int]:
        """Find line for a specific step number.

        Args:
            lines: List of markdown lines
            step_num: Step number to find

        Returns:
            Line index or None
        """
        # Look for numbered list items or "Step N" patterns
        patterns = [
            f"{step_num}.",  # Numbered list
            f"{step_num})",  # Alternative numbering
            f"step {step_num}",  # "Step 1"
        ]

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            for pattern in patterns:
                if line_lower.startswith(pattern):
                    return i

        return None

    def _find_section(self, lines: list[str], section_name: str) -> Optional[int]:
        """Find section header by name.

        Args:
            lines: List of markdown lines
            section_name: Section name to find

        Returns:
            Line index of section header or None
        """
        search_terms = [section_name, section_name.replace("_", " ")]

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            # Check if it's a header containing the section name
            if line_lower.startswith("#"):
                for term in search_terms:
                    if term.lower() in line_lower:
                        return i

        return None

    def find_ingredient_locations(self, markdown: str) -> list[int]:
        """Find line numbers of ingredient list items."""
        lines = markdown.split("\n")
        locations = []

        # Find ingredients section
        in_ingredients = False
        for i, line in enumerate(lines):
            if "ingredient" in line.lower() and line.strip().startswith("#"):
                in_ingredients = True
                continue

            # Stop at next section
            if in_ingredients and line.strip().startswith("#"):
                break

            # Collect list items in ingredients section
            if in_ingredients and (line.strip().startswith("-") or line.strip().startswith("*")):
                locations.append(i)

        return locations

    def find_step_locations(self, markdown: str) -> list[int]:
        """Find line numbers of instruction steps."""
        lines = markdown.split("\n")
        locations = []

        # Find instructions/steps section
        in_steps = False
        for i, line in enumerate(lines):
            lower_line = line.lower()
            if any(keyword in lower_line for keyword in ["instruction", "direction", "step"]) \
               and line.strip().startswith("#"):
                in_steps = True
                continue

            # Stop at next section
            if in_steps and line.strip().startswith("#"):
                break

            # Collect numbered or bulleted items in steps section
            stripped = line.strip()
            if in_steps and (stripped and (
                stripped[0].isdigit() or
                stripped.startswith("-") or
                stripped.startswith("*")
            )):
                locations.append(i)

        return locations

    def write_output(
        self,
        enhanced_markdown: str,
        original_path: Path,
        output_dir: Optional[Path] = None
    ) -> Path:
        """Write enhanced recipe to file.

        Args:
            enhanced_markdown: Enhanced recipe content
            original_path: Original recipe file path
            output_dir: Optional output directory

        Returns:
            Path to output file
        """
        # Generate output filename: original-grove.md
        output_name = f"{original_path.stem}-grove{original_path.suffix}"

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / output_name
        else:
            output_path = original_path.parent / output_name

        output_path.write_text(enhanced_markdown, encoding="utf-8")
        console.print(f"[green]✓ Saved enhanced recipe to {output_path}[/green]")
        return output_path
