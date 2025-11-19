"""CLI interface for RecipeGrove."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
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
@click.version_option(version="0.1.0", prog_name="recipelgrove")
def main(
    input_path: str,
    theme: str,
    model: str,
    output: str | None,
    emoji_density: str,
    dry_run: bool,
) -> None:
    """Transform recipes into emoji-enhanced markdown.

    INPUT_PATH: Path to recipe file (URL, PDF, text file, etc.)
    """
    console.print("[bold green]RecipeGrove 🌳✨[/bold green]")
    console.print(f"Processing: {input_path}")

    if dry_run:
        console.print("[yellow]Dry run mode - no emojis will be generated[/yellow]")

    # TODO: Implement pipeline
    # 1. Parse input with OmniParser
    # 2. Analyze with LLM
    # 3. Generate emojis with EmojiKitchen
    # 4. Enhance recipe
    # 5. Write output

    console.print("[red]Pipeline not yet implemented[/red]")
    console.print("This is a placeholder. Implementation coming in Phase 1.")


if __name__ == "__main__":
    main()
