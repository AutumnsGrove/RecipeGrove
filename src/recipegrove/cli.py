"""CLI interface for RecipeGrove."""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from recipegrove.analyzer import RecipeAnalyzer
from recipegrove.config import load_config
from recipegrove.emoji_generator import EmojiGenerator
from recipegrove.html_exporter import HTMLExporter
from recipegrove.parser import RecipeParser
from recipegrove.recipe_enhancer import RecipeEnhancer
from recipegrove.shopping_list import ShoppingListGenerator
from recipegrove.utils import detect_season

console = Console()


@click.command()
@click.argument("input_path", type=str)  # Allow URLs too, so don't require exists=True
@click.option(
    "--theme",
    type=click.Choice(["asian", "italian", "mexican", "mediterranean", "auto"]),
    default="auto",
    help="Override automatic theme detection",
)
@click.option(
    "--season",
    type=click.Choice(["winter", "spring", "summer", "fall", "auto"]),
    default="auto",
    help="Apply seasonal theme (auto-detects by default)",
)
@click.option(
    "--model",
    type=str,
    default="anthropic/claude-3.5-sonnet",
    help="LLM model to use for analysis",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Custom output location",
)
@click.option(
    "--emoji-density",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    help="Control emoji frequency",
)
@click.option(
    "--emoji-path",
    type=click.Choice(["relative", "absolute", "base64", "unicode"]),
    default="relative",
    help="How to handle emoji paths (relative=portable, base64=embedded)",
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "html"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--shopping-list",
    is_flag=True,
    help="Also generate a shopping list",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview planned emojis without generating",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.version_option(version="0.1.0", prog_name="recipegrove")
def main(
    input_path: str,
    theme: str,
    season: str,
    model: str,
    output: str | None,
    emoji_density: str,
    emoji_path: str,
    format: str,
    shopping_list: bool,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Transform recipes into emoji-enhanced markdown.

    INPUT_PATH: Path to recipe file or URL (PDF, text, HTML, etc.)
    """
    try:
        # Run async pipeline
        asyncio.run(
            run_pipeline(
                input_path=input_path,
                theme=theme,
                season=season,
                model=model,
                output=output,
                emoji_density=emoji_density,
                emoji_path=emoji_path,
                export_format=format,
                generate_shopping_list=shopping_list,
                dry_run=dry_run,
                verbose=verbose,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


async def run_pipeline(
    input_path: str,
    theme: str,
    season: str,
    model: str,
    output: str | None,
    emoji_density: str,
    emoji_path: str,
    export_format: str,
    generate_shopping_list: bool,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Execute the RecipeGrove pipeline."""
    console.print(Panel("[bold green]RecipeGrove 🌳✨[/bold green]", expand=False))
    console.print(f"[dim]Processing:[/dim] {input_path}\n")

    if dry_run:
        console.print("[yellow]⚠ Dry run mode - emojis will not be generated[/yellow]\n")

    # Load configuration
    config = load_config()

    # Detect season if auto
    current_season = detect_season() if season == "auto" else season
    if verbose and season == "auto":
        console.print(f"[dim]Detected season: {current_season}[/dim]\n")

    # Check for API key
    if not config.secrets.openrouter_api_key:
        console.print(
            "[red]Error: OpenRouter API key not found![/red]\n"
            "Please set OPENROUTER_API_KEY environment variable or add to secrets.json"
        )
        sys.exit(1)

    # Step 1: Parse input with OmniParser
    console.print("[bold cyan]Step 1:[/bold cyan] Parsing recipe")
    parser = RecipeParser()

    try:
        markdown_content = parser.parse(input_path)
        if verbose:
            console.print(f"[dim]Parsed {len(markdown_content)} characters[/dim]")
    except Exception as e:
        console.print(f"[red]✗ Parsing failed: {e}[/red]")
        raise

    # Step 2: Analyze recipe with LLM
    console.print("\n[bold cyan]Step 2:[/bold cyan] Analyzing recipe with LLM")
    analyzer = RecipeAnalyzer(
        api_key=config.secrets.openrouter_api_key,
        model=model,
    )

    try:
        analysis = await analyzer.analyze_recipe(markdown_content)

        if verbose:
            # Display analysis results
            table = Table(title="Recipe Analysis")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Cuisine Type", analysis.cuisine_type)
            table.add_row("Regional Style", analysis.regional_style or "N/A")
            table.add_row("Theme", analysis.suggested_theme)
            table.add_row("Ingredients", ", ".join(analysis.ingredients[:5]))
            table.add_row("Techniques", ", ".join(analysis.cooking_techniques[:3]))

            console.print(table)

    except Exception as e:
        await analyzer.close()
        console.print(f"[red]✗ Analysis failed: {e}[/red]")
        raise

    # Step 3: Plan emoji placements
    console.print("\n[bold cyan]Step 3:[/bold cyan] Planning emoji placements")

    try:
        placements = await analyzer.plan_emoji_placements(
            markdown_content, analysis, emoji_density=emoji_density
        )

        if dry_run or verbose:
            # Show planned placements
            table = Table(title="Planned Emoji Placements")
            table.add_column("Location", style="cyan")
            table.add_column("Emojis", style="magenta")
            table.add_column("Context", style="dim")

            for p in placements:
                table.add_row(
                    p.location,
                    f"{p.emoji_base_1} + {p.emoji_base_2}",
                    p.context[:50] + "..." if len(p.context) > 50 else p.context,
                )

            console.print(table)

        await analyzer.close()

    except Exception as e:
        await analyzer.close()
        console.print(f"[red]✗ Planning failed: {e}[/red]")
        raise

    if dry_run:
        console.print("\n[green]✓ Dry run complete![/green]")
        return

    # Step 4: Generate emoji combinations (in parallel!)
    console.print("\n[bold cyan]Step 4:[/bold cyan] Generating emoji combinations (parallel)")
    generator = EmojiGenerator()

    # Generate all emojis in parallel using asyncio.gather()
    async def generate_one(placement):
        """Generate a single emoji combination."""
        try:
            emoji_path = await generator.generate_combination(
                placement.emoji_base_1,
                placement.emoji_base_2,
                fallback=True,
            )
            return (placement.location, emoji_path)
        except Exception as e:
            if verbose:
                console.print(f"[yellow]⚠ Error generating emoji: {e}[/yellow]")
            return (placement.location, None)

    # Generate all emojis in parallel
    results = await asyncio.gather(*[generate_one(p) for p in placements])

    # Build emoji_paths dict from results
    emoji_paths = {loc: path for loc, path in results if path is not None}

    console.print(f"[green]Generated {len(emoji_paths)}/{len(placements)} emojis (parallel)[/green]")

    # Step 5: Enhance recipe with emojis
    console.print("\n[bold cyan]Step 5:[/bold cyan] Enhancing recipe")
    enhancer = RecipeEnhancer(emoji_path_mode=emoji_path)

    enhanced_markdown = enhancer.enhance_recipe(
        markdown_content, placements, emoji_paths
    )

    # Step 6: Write output
    console.print("\n[bold cyan]Step 6:[/bold cyan] Saving enhanced recipe")

    # Determine output path
    input_as_path = Path(input_path) if not parser.is_url(input_path) else Path("recipe.md")
    output_dir = Path(output) if output else None

    output_path = enhancer.write_output(enhanced_markdown, input_as_path, output_dir)

    # Copy emojis to relative directory if needed
    if emoji_path == "relative":
        enhancer._copy_emojis_to_relative_dir(emoji_paths, output_path)

    # Generate HTML export if requested
    html_path = None
    if export_format == "html":
        console.print("\n[bold cyan]Bonus:[/bold cyan] Exporting to HTML")
        html_exporter = HTMLExporter()

        # Extract title from markdown
        title_match = markdown_content.split("\n")[0]
        title = title_match.replace("#", "").strip() if title_match.startswith("#") else "Recipe"

        html_content = html_exporter.export_to_html(
            enhanced_markdown,
            title=title,
            emoji_paths=emoji_paths,
            embed_images=(emoji_path == "base64")
        )

        html_path = output_path.with_suffix(".html")
        html_exporter.write_html_file(html_content, html_path)
        console.print(f"[green]✓ HTML exported to {html_path}[/green]")

    # Generate shopping list if requested
    shopping_list_path = None
    if generate_shopping_list:
        console.print("\n[bold cyan]Bonus:[/bold cyan] Generating shopping list")
        shopping_gen = ShoppingListGenerator()
        shopping_list_path = shopping_gen.generate_from_recipe_file(
            output_path, output_dir=output_dir
        )
        console.print(f"[green]✓ Shopping list saved to {shopping_list_path}[/green]")

    # Success summary
    summary = (
        f"[bold green]✓ Recipe enhanced successfully![/bold green]\n\n"
        f"[dim]Input:[/dim] {input_path}\n"
        f"[dim]Output:[/dim] {output_path}\n"
        f"[dim]Theme:[/dim] {analysis.suggested_theme}\n"
        f"[dim]Season:[/dim] {current_season}\n"
        f"[dim]Emojis:[/dim] {len(emoji_paths)} placed\n"
        f"[dim]Emoji Mode:[/dim] {emoji_path}\n"
    )

    if html_path:
        summary += f"[dim]HTML Export:[/dim] {html_path}\n"
    if shopping_list_path:
        summary += f"[dim]Shopping List:[/dim] {shopping_list_path}\n"

    console.print(
        Panel(
            summary,
            title="Success",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
