# RecipeGrove 🌳✨

Transform ordinary recipes into fun, emoji-enhanced markdown documents with intelligent, thematic emoji combinations.

## Overview

**RecipeGrove** is a Python CLI tool that takes any recipe source (websites, PDFs, text files) and enhances them with contextually appropriate, custom-generated emoji combinations. For example, an Asian recipe might feature dragon emojis combined with food ingredients (🐉 + 🥟), while maintaining the recipe's original content and structure.

## Key Features

- 📄 **Universal Input Support** - Process URLs, PDFs, text files, or any format
- 🧠 **AI-Powered Analysis** - LLM analyzes cuisine type, ingredients, and context
- 🎨 **Custom Emoji Generation** - ~100k emoji combinations via Google's Emoji Kitchen
- 🌍 **Intelligent Theming** - Regional, seasonal, and dietary-specific emoji combinations
- 📝 **Markdown Output** - Clean, readable recipe cards with inline emojis
- 🔒 **Safe by Default** - Never overwrites original files

## How It Works

```
Input (URL/PDF/file)
  ↓
OmniParser (standardize to markdown)
  ↓
LLM Analysis (identify themes, ingredients, style)
  ↓
LLM Decision (select emojis and placement)
  ↓
EmojiKitchen (generate custom emoji combinations)
  ↓
Recipe Enhancement (insert emojis inline)
  ↓
Output (enhanced markdown file)
```

## Installation

### Prerequisites

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) package manager
- OpenRouter API key

### Install via UV

```bash
uv tool install recipelgrove
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AutumnsGrove/RecipeGrove.git
cd RecipeGrove

# Install dependencies
uv sync

# Set up API keys
cp secrets_template.json secrets.json
# Edit secrets.json with your OpenRouter API key
```

## Usage

### Basic Commands

```bash
# Process a recipe file
recipelgrove examples/sample-recipes/pad-thai.md

# Process a recipe URL
recipelgrove https://example.com/pad-thai-recipe

# Process a PDF
recipelgrove grandmas-lasagna.pdf
```

### Options

```bash
# Override theme detection
recipelgrove recipe.pdf --theme italian

# Control emoji density (low/medium/high)
recipelgrove recipe.txt --emoji-density high

# Preview without generating emojis (dry-run)
recipelgrove recipe.md --dry-run

# Verbose output with analysis tables
recipelgrove recipe.txt --verbose

# Custom output location
recipelgrove recipe.txt --output ./enhanced/

# Specify LLM model
recipelgrove recipe.md --model anthropic/claude-3.5-sonnet
```

### Full CLI Reference

```
recipelgrove [OPTIONS] INPUT_PATH

Arguments:
  INPUT_PATH              Path to recipe file or URL

Options:
  --theme [asian|italian|mexican|mediterranean|auto]
                          Override automatic theme detection (default: auto)
  --model TEXT            LLM model to use (default: anthropic/claude-3.5-sonnet)
  -o, --output PATH       Custom output location
  --emoji-density [low|medium|high]
                          Control emoji frequency (default: medium)
  --dry-run               Preview planned emojis without generating
  -v, --verbose           Enable verbose output with analysis details
  --version               Show version
  --help                  Show this message
```

## Configuration

### API Keys

RecipeGrove requires an OpenRouter API key. Set it up in one of two ways:

**Option 1: secrets.json (Recommended)**
```json
{
  "openrouter_api_key": "sk-or-v1-..."
}
```

**Option 2: Environment Variable**
```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Model Selection

By default, RecipeGrove uses Claude 4.5 Sonnet via OpenRouter. Future support planned for:
- Kimi k2
- Moonshot models
- Direct Anthropic API
- Local models (QwQ, Qwen 2.5 Coder, Mistral Small 3)

## Theming Examples

RecipeGrove analyzes recipes and applies appropriate themes based on:

- **Regional/Cuisine**: Asian, Italian, Mexican, Mediterranean
- **Occasion**: Romantic dinner, quick meal, party food, comfort food
- **Dietary Style**: Vegan, keto, gluten-free, traditional
- **Season/Holiday**: Summer dishes, holiday specials, seasonal ingredients
- **Ingredient Categories**: Proteins, vegetables, spices, techniques

Example output:
```markdown
# 🐉🥟 Authentic Pad Thai

## Ingredients
- 🍤 8 oz rice noodles
- 🥚 3 eggs
- 🌶️ 2 tbsp tamarind paste
...
```

## Project Structure

```
recipelgrove/
├── recipelgrove/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── parser.py           # OmniParser integration
│   ├── analyzer.py         # LLM analysis logic
│   ├── emoji_generator.py  # EmojiKitchen integration
│   ├── recipe_enhancer.py  # Emoji insertion logic
│   ├── themes.py           # Theming rules
│   ├── config.py           # Configuration management
│   └── utils.py            # Shared utilities
├── tests/                  # Test suite
├── examples/               # Sample recipes and outputs
├── pyproject.toml          # Project configuration
└── README.md
```

## Dependencies

RecipeGrove builds upon:

- **[OmniParser](https://github.com/AutumnsGrove/OmniParser)** - Universal document parser
- **[EmojiKitchen](https://github.com/AutumnsGrove/EmojiKitchen)** - Custom emoji generation
- **OpenRouter API** - LLM access for analysis

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

This project uses pre-commit hooks for code quality:
- Black (formatter)
- Ruff (linter)
- pytest (test runner)
- Secrets scanner (prevents API key leaks)

Install hooks:
```bash
./AgentUsage/pre_commit_hooks/install_hooks.sh
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to RecipeGrove.

## Roadmap

### ✅ Phase 1 (MVP) - Complete!
- [x] Project setup and structure
- [x] CLI with full option support
- [x] OmniParser integration (URLs, PDFs, text files)
- [x] OpenRouter/Claude LLM integration
- [x] EmojiKitchen integration with caching
- [x] Intelligent emoji insertion
- [x] Markdown output with inline emojis
- [x] Dry-run and verbose modes
- [x] 55 unit tests passing

### Phase 2 (Enhancement) - Next
- [ ] More cuisine themes (Indian, French, American)
- [ ] Occasion-based theming (romantic, party, etc.)
- [ ] Dietary style detection improvements
- [ ] Batch processing for multiple recipes
- [ ] Configuration file support (.recipelgroverc)
- [ ] Integration tests with mocked services

### Phase 3 (Polish) - Future
- [ ] Model switching (Kimi k2, Moonshot, direct Anthropic)
- [ ] Performance optimization and benchmarks
- [ ] Obsidian integration
- [ ] PyPI package distribution
- [ ] Example gallery and demo video
- [ ] Local model support

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

- Google's Emoji Kitchen API for emoji combinations
- OpenRouter for LLM access
- The recipe communities for inspiration

---

**Status**: ✅ Phase 1 MVP Complete - 55 tests passing

**Next Steps**: Add your OpenRouter API key and test with real recipes!

**Created**: 2025-11-19
**Maintained by**: [@AutumnsGrove](https://github.com/AutumnsGrove)
