"""CLI interface for RecipeGrove."""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from recipelgrove.analyzer import RecipeAnalyzer
from recipelgrove.config import load_config
from recipelgrove.emoji_generator import EmojiGenerator
from recipelgrove.parser import RecipeParser
from recipelgrove.recipe_enhancer import RecipeEnhancer

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
@click.version_option(version="0.1.0", prog_name="recipelgrove")
def main(
    input_path: str,
    theme: str,
    model: str,
    output: str | None,
    emoji_density: str,
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
                model=model,
                output=output,
                emoji_density=emoji_density,
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
    model: str,
    output: str | None,
    emoji_density: str,
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

    # Step 4: Generate emoji combinations
    console.print("\n[bold cyan]Step 4:[/bold cyan] Generating emoji combinations")

    # Determine the recipe directory and create emojikitchen sidecar folder
    input_as_path = Path(input_path) if not parser.is_url(input_path) else Path("recipe.md")
    recipe_dir = input_as_path.parent if input_as_path.parent.exists() else Path.cwd()
    emoji_output_dir = recipe_dir / "emojikitchen"
    emoji_output_dir.mkdir(parents=True, exist_ok=True)

    generator = EmojiGenerator(output_dir=emoji_output_dir)

    emoji_paths = {}
    for placement in placements:
        try:
            emoji_path = await generator.generate_combination(
                placement.emoji_base_1,
                placement.emoji_base_2,
                fallback=True,
            )

            if emoji_path:
                emoji_paths[placement.location] = emoji_path
            elif verbose:
                console.print(
                    f"[yellow]⚠ Failed to generate {placement.emoji_base_1}+{placement.emoji_base_2}[/yellow]"
                )

        except Exception as e:
            if verbose:
                console.print(f"[yellow]⚠ Error generating emoji: {e}[/yellow]")
            continue

    console.print(f"[green]Generated {len(emoji_paths)}/{len(placements)} emojis[/green]")

    # Step 5: Enhance recipe with emojis
    console.print("\n[bold cyan]Step 5:[/bold cyan] Enhancing recipe")
    enhancer = RecipeEnhancer()

    # Use relative paths so markdown is portable
    enhanced_markdown = enhancer.enhance_recipe(
        markdown_content, placements, emoji_paths, relative_to=recipe_dir
    )

    # Step 6: Write output
    console.print("\n[bold cyan]Step 6:[/bold cyan] Saving enhanced recipe")

    # Determine output path
    output_dir_path = Path(output) if output else None

    output_path = enhancer.write_output(enhanced_markdown, input_as_path, output_dir_path)

    # Success summary
    console.print(
        Panel(
            f"[bold green]✓ Recipe enhanced successfully![/bold green]\n\n"
            f"[dim]Input:[/dim] {input_path}\n"
            f"[dim]Output:[/dim] {output_path}\n"
            f"[dim]Theme:[/dim] {analysis.suggested_theme}\n"
            f"[dim]Emojis:[/dim] {len(emoji_paths)} placed\n",
            title="Success",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
