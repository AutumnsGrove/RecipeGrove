# RecipeGrove - Project Specification

## Project Overview

**RecipeGrove** is a CLI tool that transforms ordinary recipes into fun, emoji-enhanced markdown documents with intelligent, thematic emoji combinations. By analyzing recipe content and context, it automatically generates and inserts custom emoji combinations that reflect the cuisine style, ingredients, and characteristics of each dish.

## Core Concept

Take any recipe source (website, PDF, text file) and enhance it with contextually appropriate emoji combinations. For example, an Asian recipe might use dragon emojis combined with food ingredients (🐉 + 🥟), while an Italian dish might use different regional theming. The tool makes recipes visually engaging and fun while maintaining readability.

## Dependencies

This project builds upon two existing tools:

- **OmniParser**: https://github.com/AutumnsGrove/OmniParser
  - Universal document parser that converts any format to standardized markdown
  - Handles websites, PDFs, images, and various document formats
  
- **EmojiKitchen**: https://github.com/AutumnsGrove/EmojiKitchen
  - CLI tool for generating custom emoji combinations
  - Uses Google's Emoji Kitchen API (~100k possible combinations)
  - Provides fallback/recursion for failed combinations

## Technical Architecture

### Language & Distribution
- **Language**: Python
- **Distribution**: UV-installable tool
- **Dependencies**: Import OmniParser and EmojiKitchen as libraries (not shell calls)
- **Installation**: Single `uv tool install` should pull all dependencies

### LLM Integration
- **Provider**: OpenRouter API
- **Initial Model**: Claude 4.5 Sonnet
- **Future Model**: Kimi k2 (plan for easy model switching)
- **Purpose**: 
  - Analyze recipe content and context
  - Determine appropriate theming
  - Decide emoji placement dynamically
  - Select emoji combinations that match ingredients and style

### Workflow Pipeline

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

## Features & Behavior

### Input Sources
- Recipe URLs (websites)
- PDF documents
- Text files
- Any format OmniParser supports

### Theming Factors
The LLM should analyze and theme based on:
- **Regional/Cuisine Type**: Asian, Italian, Mexican, Mediterranean, etc.
- **Occasion**: Romantic dinner, quick meal, party food, comfort food
- **Dietary Style**: Vegan, keto, gluten-free, traditional
- **Season/Holiday**: Summer dishes, holiday specials, seasonal ingredients
- **Ingredient Categories**: Proteins, vegetables, spices, techniques

### Emoji Placement
- **Dynamic**: LLM decides where emojis should appear
- **Suggestions**: Section headers, ingredient lists, cooking steps, serving suggestions
- **Inline**: Emojis rendered as inline markdown images
- **Size**: Initially large (optimization comes later)

### Output Format
- **Format**: Markdown file
- **Naming**: Original filename + suffix (e.g., `recipe.md` → `recipe-grove.md`)
- **Preservation**: Never overwrite original files
- **Structure**: Properly formatted recipe card with:
  - Title (with thematic emoji)
  - Ingredients (with ingredient-specific emojis)
  - Instructions (with step/technique emojis)
  - Notes/Tips (if applicable)

## Emoji Combination Strategy

### Regional Theming Examples
- **Asian Cuisine**: Dragon (🐉) + food items
- **Italian Cuisine**: Italian flag colors or Mediterranean symbols + ingredients
- **Mexican Cuisine**: Regional symbols + spices/ingredients
- **General Approach**: Match cultural/regional iconography with food elements

### Fallback Handling
Since some emoji combinations don't exist in Emoji Kitchen:
1. LLM requests emoji combination
2. EmojiKitchen attempts generation
3. If fails, recursively try alternative combinations
4. Log failed attempts for future optimization

### Combination Philosophy
- Mix regional/thematic symbols with food emojis
- Keep combinations fun and recognizable
- Prioritize uniqueness and visual interest
- Use the ~100k combinations available strategically

## CLI Interface

### Basic Usage
```bash
recipegrove <input> [options]
```

### Options (Suggested)
- `--theme <type>`: Override auto-detection (asian, italian, mexican, etc.)
- `--model <name>`: Select LLM model
- `--output <path>`: Custom output location
- `--emoji-density <low|medium|high>`: Control emoji frequency
- `--dry-run`: Show planned emojis without generating

### Examples
```bash
# Process URL
recipegrove https://example.com/pad-thai-recipe

# Process PDF
recipegrove grandmas-lasagna.pdf

# With custom theme
recipegrove recipe.txt --theme italian

# Dry run to preview
recipegrove recipe.md --dry-run
```

## Integration Details

### OmniParser Integration
- Import as library module
- Call parsing function directly
- Receive standardized markdown output
- Handle parsing errors gracefully

### EmojiKitchen Integration
- Import as library module
- Call emoji generation functions directly
- Handle failed combinations with fallback logic
- Cache successful combinations for performance

### OpenRouter API
- Use async requests where possible
- Handle rate limits appropriately
- Provide clear error messages
- Allow API key configuration via environment variable

## Obsidian Integration Notes

From original concept: Custom emojis need to be added to Obsidian via "Automating Emojis" script. The tool should:
- Generate emojis compatible with Obsidian markdown
- Optionally output Obsidian-specific formatting
- Document Obsidian setup process

## Future Considerations

### Model Flexibility
- Design with model-swapping in mind
- Abstract LLM calls for easy provider changes
- Support local models eventually (QwQ, Qwen 2.5 Coder, Mistral small 3)

### Performance
- Cache emoji combinations
- Batch LLM requests where possible
- Optimize markdown processing

### Enhancement Ideas
- Support recipe collections (batch processing)
- Generate recipe thumbnails
- Export to multiple formats
- Web interface option
- Community emoji themes

## Development Priorities

### Phase 1 (MVP)
1. Basic CLI structure
2. OmniParser integration
3. OpenRouter/Claude integration
4. EmojiKitchen integration
5. Simple emoji insertion
6. Markdown output

### Phase 2 (Enhancement)
1. Sophisticated theming logic
2. Multiple theme support
3. Error handling & fallbacks
4. Dry-run mode
5. Configuration options

### Phase 3 (Polish)
1. Model switching (Kimi k2)
2. Performance optimization
3. Obsidian integration refinement
4. Documentation
5. Examples & templates

## Success Criteria

A successful implementation should:
- Take any recipe source and produce enhanced markdown
- Generate contextually appropriate emoji combinations
- Place emojis in logical, visually appealing locations
- Handle errors gracefully with fallbacks
- Be easily installable via UV
- Support future model switching
- Maintain original recipe integrity (separate output file)

## Technical Constraints

- Python-based (existing ecosystem)
- Must work programmatically (no GUI required)
- UV-installable with all dependencies
- OpenRouter API required (cloud-based)
- Large inline emojis acceptable initially
- macOS primary target (but should be cross-platform)

## Project Structure (Suggested)

```
recipegrove/
├── recipegrove/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── parser.py           # OmniParser integration
│   ├── analyzer.py         # LLM analysis logic
│   ├── emoji_generator.py  # EmojiKitchen integration
│   ├── recipe_enhancer.py  # Emoji insertion logic
│   ├── themes.py           # Theming rules
│   └── utils.py            # Helpers
├── tests/
├── examples/
│   ├── sample-recipes/
│   └── output-examples/
├── pyproject.toml
├── README.md
└── LICENSE
```

## Notes

- Original concept image included in project context
- Focus on making recipes fun and unique
- Embrace the playfulness of emoji combinations
- Don't overthink initial implementation - iterate based on results
- The tool should feel magical but remain practical
