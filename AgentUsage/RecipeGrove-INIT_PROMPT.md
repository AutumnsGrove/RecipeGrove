# RecipeGrove - Agent Initialization Prompt

You are tasked with building **RecipeGrove**, a Python CLI tool that transforms ordinary recipes into emoji-enhanced markdown documents using intelligent, thematic emoji combinations.

## Project Context

RecipeGrove takes any recipe source (websites, PDFs, text files) and enhances them with contextually appropriate, custom-generated emoji combinations. For example, an Asian recipe might feature dragon emojis combined with food ingredients (🐉 + 🥟), while maintaining the recipe's original content and structure.

## Core Dependencies

This project builds on two existing tools that must be imported as library dependencies:

1. **OmniParser** - https://github.com/AutumnsGrove/OmniParser
   - Universal document parser converting any format to standardized markdown
   - Import as library, don't shell out to it

2. **EmojiKitchen** - https://github.com/AutumnsGrove/EmojiKitchen  
   - CLI tool for generating custom emoji combinations
   - Uses Google's Emoji Kitchen API (~100k combinations)
   - Import as library, don't shell out to it

## Technical Requirements

### Core Stack
- **Language**: Python
- **Distribution**: UV-installable tool (`uv tool install recipelgrove`)
- **LLM Provider**: OpenRouter API
- **Model**: Claude 4.5 Sonnet (with easy switching to Kimi k2 later)
- **Dependency Management**: All dependencies pulled in single UV install

### Architecture

```
Input → OmniParser → LLM Analysis → LLM Decision → EmojiKitchen → Enhanced Output
```

1. **Input Processing**: Accept URLs, PDFs, text files (anything OmniParser supports)
2. **Parsing**: Use OmniParser to convert to standardized markdown
3. **Analysis**: Send to LLM (via OpenRouter) to analyze:
   - Cuisine type/region
   - Ingredients and categories
   - Cooking techniques
   - Occasion/context
   - Appropriate theming factors
4. **Emoji Planning**: LLM decides:
   - Which emojis to combine (e.g., dragon + garlic for Asian cuisine)
   - Where to place them (headers, ingredients, steps)
   - Density and distribution
5. **Generation**: Use EmojiKitchen to create custom emoji combinations
   - Handle failed combinations with fallback/recursion
6. **Enhancement**: Insert emojis as inline markdown images
7. **Output**: Write enhanced recipe to new file (never overwrite original)

## Key Features to Implement

### Theming System
The LLM should analyze and theme based on:
- **Regional/Cuisine**: Asian, Italian, Mexican, Mediterranean, etc.
- **Occasion**: Romantic, quick meal, party, comfort food
- **Dietary**: Vegan, keto, gluten-free
- **Season/Holiday**: Summer dishes, holiday specials
- **Ingredients**: Proteins, vegetables, spices

### Emoji Placement Strategy
- Let LLM decide dynamically where emojis should appear
- Suggested locations: section headers, ingredient lists, cooking steps
- Emojis should be inline markdown images
- Size will be large initially (optimization later)
- Balance visual interest with readability

### Output Format
- Markdown file with proper recipe card structure
- Naming: `<original>-grove.<ext>` (e.g., `pad-thai-grove.md`)
- Never overwrite original files
- Include:
  - Title with thematic emoji
  - Ingredients with ingredient-specific emojis
  - Instructions with step/technique emojis  
  - Notes/tips if applicable

## CLI Interface

### Required Commands
```bash
recipelgrove <input> [options]
```

### Suggested Options
- `--theme <type>`: Override auto-detection
- `--model <name>`: Select LLM model
- `--output <path>`: Custom output location
- `--emoji-density <low|medium|high>`: Control frequency
- `--dry-run`: Preview without generating

### Example Usage
```bash
recipelgrove https://example.com/recipe
recipelgrove recipe.pdf --theme italian
recipelgrove recipe.txt --dry-run
```

## Implementation Guidelines

### OmniParser Integration
- Import OmniParser as a library module
- Call parsing functions directly (not via subprocess)
- Handle parsing errors with clear messages
- Ensure markdown output is clean and standardized

### EmojiKitchen Integration  
- Import EmojiKitchen as a library module
- Call emoji generation functions directly
- Implement fallback logic for failed combinations
- Consider caching successful combinations

### OpenRouter API
- Use async requests where possible
- Handle rate limits gracefully
- Provide clear error messages
- API key via environment variable (`OPENROUTER_API_KEY`)
- Make model selection configurable

### Error Handling
- Graceful failures at each pipeline stage
- Fallback to simpler emojis if combinations fail
- Clear error messages for users
- Log issues for debugging

## Project Structure

```
recipelgrove/
├── recipelgrove/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point (Click/Typer)
│   ├── parser.py           # OmniParser integration
│   ├── analyzer.py         # LLM analysis & planning
│   ├── emoji_generator.py  # EmojiKitchen integration
│   ├── recipe_enhancer.py  # Emoji insertion logic
│   ├── themes.py           # Theme definitions & rules
│   ├── config.py           # Configuration management
│   └── utils.py            # Shared utilities
├── tests/
│   ├── test_parser.py
│   ├── test_analyzer.py
│   ├── test_emoji_generator.py
│   └── test_enhancer.py
├── examples/
│   ├── sample-recipes/     # Test recipes
│   └── output-examples/    # Example outputs
├── pyproject.toml          # UV/pip configuration
├── README.md              # Usage documentation
└── LICENSE
```

## Development Phases

### Phase 1: MVP
1. Set up project structure with UV configuration
2. Integrate OmniParser for input processing
3. Set up OpenRouter client with Claude 4.5 Sonnet
4. Integrate EmojiKitchen for emoji generation
5. Implement basic emoji insertion
6. Create simple CLI interface
7. Test with sample recipes

### Phase 2: Enhancement
1. Sophisticated LLM prompting for theme detection
2. Multi-theme support (Asian, Italian, etc.)
3. Improved emoji placement logic
4. Error handling and fallbacks
5. Dry-run mode for preview
6. Configuration file support

### Phase 3: Polish
1. Model switching (add Kimi k2 support)
2. Performance optimization (caching, batching)
3. Comprehensive documentation
4. Usage examples and templates
5. Test coverage

## LLM Prompting Strategy

### Analysis Phase Prompt Structure
```
You are analyzing a recipe to add thematic emoji combinations.

Recipe content: <markdown>

Tasks:
1. Identify cuisine type/region
2. List key ingredients and categories
3. Identify cooking techniques
4. Suggest appropriate theme (regional symbols, occasion, etc.)
5. Recommend emoji combination strategy

Output format: JSON with structured recommendations
```

### Emoji Planning Prompt Structure
```
Based on this recipe analysis, plan emoji placements.

Recipe: <markdown>
Analysis: <from previous step>

For each location (title, ingredients, steps):
- Which emojis to combine (base emoji 1 + base emoji 2)
- Why this combination fits the theme
- Placement location and context

Output: JSON array of emoji placement instructions
```

## Testing Strategy

### Unit Tests
- Test OmniParser integration with various formats
- Test EmojiKitchen combination generation
- Test emoji insertion logic
- Test CLI argument parsing

### Integration Tests  
- End-to-end recipe processing
- Error handling scenarios
- Different recipe types and themes
- API failure scenarios

### Test Data
Include sample recipes for:
- Asian cuisine (Thai, Japanese, Chinese)
- Italian cuisine
- Mexican cuisine
- Vegan/dietary-specific
- Simple vs complex recipes

## Documentation Requirements

### README.md
- Project overview and purpose
- Installation instructions (UV)
- Basic usage examples
- Configuration (API keys)
- Theming options
- Troubleshooting

### Code Documentation
- Docstrings for all public functions
- Type hints throughout
- Inline comments for complex logic

### Examples
- Sample input recipes
- Generated output examples
- Screenshot or demo of results

## Success Criteria

The implementation is successful when:
- ✅ Single `uv tool install` pulls all dependencies
- ✅ Can process any recipe format OmniParser supports
- ✅ Generates contextually appropriate emoji combinations
- ✅ Produces enhanced markdown with inline emojis
- ✅ Never overwrites original files
- ✅ Handles errors gracefully with fallbacks
- ✅ CLI is intuitive and well-documented
- ✅ Can easily switch between LLM models

## Important Notes

1. **Library Integration**: Import OmniParser and EmojiKitchen as libraries, not CLI tools
2. **File Safety**: Always create new files, never overwrite originals
3. **Emoji Size**: Large inline emojis are acceptable for now
4. **Theming**: Focus on making recipes fun and unique
5. **Fallbacks**: Some emoji combinations will fail - handle gracefully
6. **Future-Proof**: Design for easy model switching
7. **User Experience**: Clear error messages and helpful CLI output

## Getting Started

1. Review the full PROJECT_SPEC.md for detailed technical specifications
2. Set up Python project with UV/pyproject.toml
3. Add OmniParser and EmojiKitchen as dependencies
4. Create basic CLI structure
5. Implement pipeline one component at a time
6. Test with simple recipes first
7. Iterate on LLM prompts for better theming

## Reference Materials

- **PROJECT_SPEC.md**: Complete technical specification
- **OmniParser Repo**: https://github.com/AutumnsGrove/OmniParser
- **EmojiKitchen Repo**: https://github.com/AutumnsGrove/EmojiKitchen
- **Original Concept**: See included design document/image

## Questions or Clarifications

If anything is unclear:
1. Check PROJECT_SPEC.md for details
2. Review the referenced GitHub repositories
3. Focus on MVP first, iterate on enhancements
4. Prioritize functionality over perfection initially

Good luck building RecipeGrove! 🌳✨
