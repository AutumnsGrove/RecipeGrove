"""LLM analysis and emoji planning via OpenRouter API."""

import json
import asyncio
from typing import Optional

import httpx
from pydantic import BaseModel, ValidationError
from rich.console import Console

from recipegrove.utils import sanitize_input, detect_season, get_seasonal_emojis

console = Console()


class RecipeAnalysis(BaseModel):
    """Structured recipe analysis results."""

    cuisine_type: str
    regional_style: str | None
    ingredients: list[str]
    cooking_techniques: list[str]
    occasion: str | None
    dietary_tags: list[str]
    suggested_theme: str
    emoji_strategy: str


class EmojiPlacement(BaseModel):
    """Emoji placement instruction."""

    location: str  # "title", "ingredient_X", "step_Y"
    emoji_base_1: str  # First emoji for combination
    emoji_base_2: str  # Second emoji for combination
    context: str  # Why this combination fits
    reasoning: str


class RecipeAnalyzer:
    """Analyzes recipes using LLM via OpenRouter API."""

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-3.5-sonnet",
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """Initialize analyzer with API credentials.

        Args:
            api_key: OpenRouter API key
            model: Model identifier for OpenRouter
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def _make_request(
        self, messages: list[dict], temperature: float = 0.7
    ) -> dict:
        """Make API request to OpenRouter with retry logic.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature

        Returns:
            API response dict

        Raises:
            RuntimeError: If all retries fail
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AutumnsGrove/RecipeGrove",
            "X-Title": "RecipeGrove",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        for attempt in range(self.max_retries):
            try:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 2**attempt
                    console.print(
                        f"[yellow]Rate limited, waiting {wait_time}s...[/yellow]"
                    )
                    await asyncio.sleep(wait_time)
                    continue
                elif attempt == self.max_retries - 1:
                    raise RuntimeError(
                        f"API request failed: {e.response.status_code} - {e.response.text}"
                    )
                else:
                    await asyncio.sleep(1)
                    continue

            except httpx.RequestError as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Network error: {e}")
                await asyncio.sleep(2**attempt)
                continue

        raise RuntimeError(f"Failed after {self.max_retries} retries")

    async def analyze_recipe(
        self,
        markdown_content: str,
        enable_seasonal: bool = True
    ) -> RecipeAnalysis:
        """Analyze recipe content to determine theming.

        Args:
            markdown_content: Recipe in markdown format
            enable_seasonal: If True, include seasonal context

        Returns:
            Structured analysis results
        """
        console.print("[cyan]Analyzing recipe with LLM...[/cyan]")

        # Sanitize input to protect against prompt injection
        sanitized_content = sanitize_input(markdown_content)

        # Detect current season for context
        season_context = ""
        if enable_seasonal:
            current_season = detect_season()
            seasonal_emojis = get_seasonal_emojis(current_season)
            season_context = f"\n\nCurrent season: {current_season.title()}\nSeasonal emoji suggestions: {', '.join(seasonal_emojis[:5])}"

        prompt = f"""You are analyzing a recipe to add thematic emoji combinations.{season_context}

Recipe content:
{sanitized_content}

Tasks:
1. Identify the cuisine type and regional style (e.g., Thai, Japanese, Italian, Mexican)
2. Extract key ingredients
3. Identify cooking techniques used
4. Determine the occasion or context (romantic, quick meal, comfort food, etc.)
5. Identify any dietary tags (vegan, vegetarian, gluten-free, etc.)
6. Suggest an appropriate theme based on the above analysis
7. Recommend an emoji combination strategy

Output your analysis as a JSON object with this exact structure:
{{
    "cuisine_type": "string",
    "regional_style": "string or null",
    "ingredients": ["ingredient1", "ingredient2"],
    "cooking_techniques": ["technique1", "technique2"],
    "occasion": "string or null",
    "dietary_tags": ["tag1", "tag2"],
    "suggested_theme": "string",
    "emoji_strategy": "string describing the emoji combination approach"
}}

Respond with ONLY the JSON object, no additional text."""

        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, temperature=0.3)
        content = response["choices"][0]["message"]["content"]

        # Extract JSON from response
        try:
            # Try to parse as JSON directly
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse LLM response as JSON: {e}")

        try:
            analysis = RecipeAnalysis(**data)
            console.print(
                f"[green]✓ Analysis complete[/green] "
                f"(cuisine: {analysis.cuisine_type}, theme: {analysis.suggested_theme})"
            )
            return analysis
        except ValidationError as e:
            raise RuntimeError(f"Invalid analysis structure: {e}")

    async def plan_emoji_placements(
        self,
        markdown_content: str,
        analysis: RecipeAnalysis,
        emoji_density: str = "medium",
    ) -> list[EmojiPlacement]:
        """Plan where and which emojis to place.

        Args:
            markdown_content: Recipe markdown
            analysis: Previous analysis results
            emoji_density: Density level (low, medium, high)

        Returns:
            List of emoji placement instructions
        """
        console.print("[cyan]Planning emoji placements...[/cyan]")

        density_guide = {
            "low": "Place 3-5 emojis total, only in key locations",
            "medium": "Place 5-10 emojis, balanced throughout the recipe",
            "high": "Place 10-15 emojis, creating rich visual interest",
        }

        prompt = f"""Based on this recipe analysis, plan emoji placements.

Recipe:
{markdown_content}

Analysis:
- Cuisine: {analysis.cuisine_type}
- Regional Style: {analysis.regional_style}
- Theme: {analysis.suggested_theme}
- Strategy: {analysis.emoji_strategy}
- Key Ingredients: {', '.join(analysis.ingredients[:5])}

Emoji Density: {emoji_density} - {density_guide.get(emoji_density, density_guide['medium'])}

For each placement, specify:
- Location identifier (e.g., "title", "ingredient_tomato", "step_1", "serving_suggestion")
- Base emoji 1 (single emoji character)
- Base emoji 2 (single emoji character to combine with emoji 1)
- Context explaining why this combination fits
- Reasoning for the placement

Important guidelines:
- Use emoji combinations that reflect the {analysis.suggested_theme} theme
- Match emojis to specific ingredients or techniques
- Ensure visual variety (don't reuse the same combination)
- Consider the {analysis.cuisine_type} cuisine style

Output as a JSON array with this exact structure:
[
    {{
        "location": "title",
        "emoji_base_1": "🐉",
        "emoji_base_2": "🥟",
        "context": "Dragon represents Asian cuisine power and dumplings are the dish",
        "reasoning": "Title needs strong thematic presence"
    }}
]

Respond with ONLY the JSON array, no additional text."""

        messages = [{"role": "user", "content": prompt}]

        response = await self._make_request(messages, temperature=0.7)
        content = response["choices"][0]["message"]["content"]

        # Extract JSON from response
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Failed to parse emoji placements as JSON: {e}")

        try:
            placements = [EmojiPlacement(**item) for item in data]
            console.print(
                f"[green]✓ Planned {len(placements)} emoji placements[/green]"
            )
            return placements
        except ValidationError as e:
            raise RuntimeError(f"Invalid placement structure: {e}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
