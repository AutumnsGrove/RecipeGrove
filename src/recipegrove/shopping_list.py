"""Shopping list generation from recipes."""

import re
from pathlib import Path
from typing import Optional


class ShoppingListGenerator:
    """Extract and organize ingredients into shopping lists."""

    def __init__(self):
        """Initialize shopping list generator."""
        self.category_keywords = {
            "produce": [
                "lettuce", "tomato", "onion", "garlic", "pepper", "carrot",
                "celery", "cucumber", "spinach", "kale", "potato", "broccoli",
                "cauliflower", "mushroom", "zucchini", "squash", "bean", "peas",
                "corn", "avocado", "lime", "lemon", "orange", "apple", "banana",
                "berries", "strawberries", "blueberries", "ginger", "herbs",
                "cilantro", "parsley", "basil", "mint", "thyme", "rosemary",
            ],
            "proteins": [
                "chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna",
                "shrimp", "prawn", "tofu", "egg", "turkey", "duck", "bacon",
                "sausage", "ham", "steak", "ground", "mince",
            ],
            "dairy": [
                "milk", "cream", "butter", "cheese", "yogurt", "sour cream",
                "parmesan", "mozzarella", "cheddar", "feta", "ricotta",
            ],
            "pantry": [
                "rice", "pasta", "noodles", "flour", "sugar", "salt", "pepper",
                "oil", "olive oil", "vegetable oil", "vinegar", "soy sauce",
                "sauce", "stock", "broth", "can", "canned", "dried", "beans",
            ],
            "spices": [
                "cumin", "paprika", "chili", "cinnamon", "nutmeg", "oregano",
                "turmeric", "coriander", "cardamom", "clove", "ginger powder",
                "garlic powder", "onion powder", "cayenne", "curry",
            ],
            "bakery": [
                "bread", "rolls", "buns", "tortilla", "pita", "baguette",
                "croissant",
            ],
            "frozen": [
                "frozen", "ice cream",
            ],
            "beverages": [
                "wine", "beer", "juice", "coffee", "tea", "water",
            ],
        }

    def extract_ingredients(self, markdown_content: str) -> list[str]:
        """Extract ingredient list from recipe markdown.

        Args:
            markdown_content: Recipe markdown content

        Returns:
            List of ingredient strings
        """
        ingredients = []
        lines = markdown_content.split("\n")

        in_ingredients = False
        for line in lines:
            line_lower = line.lower()

            # Check if we're entering ingredients section
            if "ingredient" in line_lower and line.strip().startswith("#"):
                in_ingredients = True
                continue

            # Check if we're leaving ingredients section
            if in_ingredients and line.strip().startswith("#"):
                break

            # Extract list items in ingredients section
            if in_ingredients:
                stripped = line.strip()
                if stripped.startswith(("- ", "* ")):
                    # Remove list marker and add to ingredients
                    ingredient = stripped[2:].strip()
                    # Remove emoji markdown if present
                    ingredient = re.sub(r"!\[.*?\]\(.*?\)", "", ingredient).strip()
                    if ingredient:
                        ingredients.append(ingredient)
                elif re.match(r"^\d+\.", stripped):
                    # Numbered list
                    ingredient = re.sub(r"^\d+\.\s*", "", stripped).strip()
                    ingredient = re.sub(r"!\[.*?\]\(.*?\)", "", ingredient).strip()
                    if ingredient:
                        ingredients.append(ingredient)

        return ingredients

    def categorize_ingredient(self, ingredient: str) -> str:
        """Categorize ingredient into shopping department.

        Args:
            ingredient: Ingredient string

        Returns:
            Category name
        """
        ingredient_lower = ingredient.lower()

        # Check each category for keyword matches
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in ingredient_lower:
                    return category

        return "other"

    def generate_shopping_list(
        self, markdown_content: str, include_emojis: bool = True
    ) -> str:
        """Generate formatted shopping list from recipe.

        Args:
            markdown_content: Recipe markdown content
            include_emojis: If True, add category emojis

        Returns:
            Formatted shopping list markdown
        """
        ingredients = self.extract_ingredients(markdown_content)

        if not ingredients:
            return "# Shopping List\n\nNo ingredients found."

        # Categorize ingredients
        categorized = {}
        for ingredient in ingredients:
            category = self.categorize_ingredient(ingredient)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(ingredient)

        # Category emojis
        category_emojis = {
            "produce": "🥬",
            "proteins": "🥩",
            "dairy": "🥛",
            "pantry": "🥫",
            "spices": "🌶️",
            "bakery": "🥖",
            "frozen": "🧊",
            "beverages": "🥤",
            "other": "🛒",
        }

        # Build shopping list
        shopping_list = "# 🛒 Shopping List\n\n"

        # Sort categories for consistent order
        category_order = [
            "produce", "proteins", "dairy", "bakery",
            "pantry", "spices", "frozen", "beverages", "other"
        ]

        for category in category_order:
            if category in categorized:
                emoji = category_emojis.get(category, "📦") if include_emojis else ""
                shopping_list += f"## {emoji} {category.title()}\n\n"

                for ingredient in sorted(categorized[category]):
                    shopping_list += f"- [ ] {ingredient}\n"

                shopping_list += "\n"

        return shopping_list

    def write_shopping_list(
        self, shopping_list: str, output_path: Path
    ) -> Path:
        """Write shopping list to file.

        Args:
            shopping_list: Shopping list markdown
            output_path: Output file path

        Returns:
            Path to written file
        """
        output_path.write_text(shopping_list, encoding="utf-8")
        return output_path

    def generate_from_recipe_file(
        self, recipe_path: Path, output_dir: Optional[Path] = None
    ) -> Path:
        """Generate shopping list from recipe file.

        Args:
            recipe_path: Path to recipe markdown file
            output_dir: Optional output directory

        Returns:
            Path to generated shopping list file
        """
        # Read recipe
        markdown_content = recipe_path.read_text(encoding="utf-8")

        # Generate shopping list
        shopping_list = self.generate_shopping_list(markdown_content)

        # Determine output path
        output_name = f"{recipe_path.stem}-shopping-list.md"
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / output_name
        else:
            output_path = recipe_path.parent / output_name

        # Write to file
        return self.write_shopping_list(shopping_list, output_path)
