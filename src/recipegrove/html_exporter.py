"""HTML export functionality for enhanced recipes."""

import re
from pathlib import Path
from typing import Optional

from recipegrove.utils import image_to_base64


class HTMLExporter:
    """Export recipes to standalone HTML with embedded CSS and emojis."""

    def __init__(self):
        """Initialize HTML exporter."""
        self.css_template = self._get_css_template()

    def export_to_html(
        self,
        markdown_content: str,
        title: str,
        emoji_paths: dict[str, Path] | None = None,
        embed_images: bool = True,
    ) -> str:
        """Convert enhanced recipe markdown to standalone HTML.

        Args:
            markdown_content: Recipe markdown content
            title: Recipe title
            emoji_paths: Optional mapping of emoji locations to paths
            embed_images: If True, embed emoji images as base64

        Returns:
            Complete HTML document string
        """
        # Convert markdown to HTML (basic conversion)
        html_body = self._markdown_to_html(markdown_content)

        # Embed emoji images if requested
        if embed_images and emoji_paths:
            html_body = self._embed_emoji_images(html_body, emoji_paths)

        # Build complete HTML document
        html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{self.css_template}
    </style>
</head>
<body>
    <div class="recipe-container">
{html_body}
    </div>
</body>
</html>"""

        return html_doc

    def _markdown_to_html(self, markdown: str) -> str:
        """Convert markdown to HTML (basic conversion).

        Args:
            markdown: Markdown content

        Returns:
            HTML string
        """
        html = markdown

        # Headers
        html = re.sub(r"^#{6}\s+(.+)$", r"<h6>\1</h6>", html, flags=re.MULTILINE)
        html = re.sub(r"^#{5}\s+(.+)$", r"<h5>\1</h5>", html, flags=re.MULTILINE)
        html = re.sub(r"^#{4}\s+(.+)$", r"<h4>\1</h4>", html, flags=re.MULTILINE)
        html = re.sub(r"^#{3}\s+(.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^#{2}\s+(.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^#{1}\s+(.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)

        # Lists
        lines = html.split("\n")
        in_list = False
        result_lines = []

        for line in lines:
            stripped = line.strip()

            # Unordered list
            if stripped.startswith("- ") or stripped.startswith("* "):
                if not in_list:
                    result_lines.append("<ul>")
                    in_list = True
                content = stripped[2:]
                result_lines.append(f"    <li>{content}</li>")
            # Ordered list
            elif re.match(r"^\d+\.\s+", stripped):
                if not in_list:
                    result_lines.append("<ol>")
                    in_list = "ordered"
                content = re.sub(r"^\d+\.\s+", "", stripped)
                result_lines.append(f"    <li>{content}</li>")
            else:
                if in_list:
                    if in_list == "ordered":
                        result_lines.append("</ol>")
                    else:
                        result_lines.append("</ul>")
                    in_list = False
                result_lines.append(line)

        if in_list:
            if in_list == "ordered":
                result_lines.append("</ol>")
            else:
                result_lines.append("</ul>")

        html = "\n".join(result_lines)

        # Bold and italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)

        # Links and images are already in markdown format, leave as is

        # Paragraphs - wrap non-tag lines
        lines = html.split("\n")
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("<"):
                result_lines.append(f"<p>{line}</p>")
            else:
                result_lines.append(line)

        return "\n".join(result_lines)

    def _embed_emoji_images(self, html: str, emoji_paths: dict[str, Path]) -> str:
        """Embed emoji images as base64 data URIs.

        Args:
            html: HTML content with image paths
            emoji_paths: Mapping of locations to emoji image paths

        Returns:
            HTML with embedded images
        """
        for location, emoji_path in emoji_paths.items():
            if emoji_path and emoji_path.exists():
                # Convert to base64
                base64_data = image_to_base64(emoji_path)

                # Replace file path with base64 data
                html = html.replace(str(emoji_path), base64_data)
                html = html.replace(str(emoji_path.absolute()), base64_data)

        return html

    def _get_css_template(self) -> str:
        """Get CSS template for recipe HTML.

        Returns:
            CSS string
        """
        return """
        /* RecipeGrove HTML Export Styles */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }

        .recipe-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        h2 {
            color: #34495e;
            font-size: 1.8em;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }

        h3 {
            color: #555;
            font-size: 1.4em;
            margin-top: 20px;
            margin-bottom: 10px;
        }

        p {
            margin-bottom: 15px;
            line-height: 1.8;
        }

        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }

        li {
            margin-bottom: 8px;
            line-height: 1.6;
        }

        img {
            max-width: 32px;
            max-height: 32px;
            vertical-align: middle;
            margin: 0 4px;
        }

        strong {
            color: #2c3e50;
            font-weight: 600;
        }

        em {
            color: #7f8c8d;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
                padding: 0;
            }

            .recipe-container {
                box-shadow: none;
                padding: 20px;
            }
        }

        /* Mobile responsive */
        @media (max-width: 600px) {
            .recipe-container {
                padding: 20px;
            }

            h1 {
                font-size: 2em;
            }

            h2 {
                font-size: 1.5em;
            }
        }
        """

    def write_html_file(
        self, html_content: str, output_path: Path
    ) -> Path:
        """Write HTML content to file.

        Args:
            html_content: HTML string
            output_path: Output file path

        Returns:
            Path to written file
        """
        output_path.write_text(html_content, encoding="utf-8")
        return output_path
