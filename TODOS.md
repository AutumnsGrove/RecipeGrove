# RecipeGrove TODOs

## Stage 0: Project Setup ✅
- [x] Clean up BaseProject template artifacts
- [x] Update AGENT.md with project details
- [x] Create RecipeGrove README
- [x] Set up Python/UV project structure
- [x] Create module structure (cli, parser, analyzer, etc.)
- [x] Generate secrets_template.json
- [x] Create initial test files
- [ ] Install git hooks for code quality
- [ ] Make initial commit

## Phase 1: MVP - Core Functionality

### CLI & Infrastructure
- [ ] Implement basic CLI command structure with Click
- [ ] Add input validation (file exists, URL is valid)
- [ ] Set up rich console output with progress indicators
- [ ] Implement config loading from secrets.json and env vars
- [ ] Add error handling and user-friendly error messages

### OmniParser Integration
- [ ] Research OmniParser package installation (PyPI or git)
- [ ] Add OmniParser as dependency to pyproject.toml
- [ ] Implement `parser.py` - parse URLs to markdown
- [ ] Implement `parser.py` - parse PDF files to markdown
- [ ] Implement `parser.py` - parse text files to markdown
- [ ] Add error handling for unsupported formats
- [ ] Write tests for parser module

### OpenRouter/LLM Integration
- [ ] Implement OpenRouter API client in `analyzer.py`
- [ ] Create prompt template for recipe analysis
- [ ] Implement `analyze_recipe()` function
- [ ] Create prompt template for emoji planning
- [ ] Implement `plan_emoji_placements()` function
- [ ] Add retry logic and rate limiting
- [ ] Write tests for analyzer module

### EmojiKitchen Integration
- [ ] Research EmojiKitchen package installation (PyPI or git)
- [ ] Add EmojiKitchen as dependency to pyproject.toml
- [ ] Implement `emoji_generator.py` - generate combinations
- [ ] Implement emoji caching system
- [ ] Implement fallback logic for failed combinations
- [ ] Write tests for emoji generator

### Recipe Enhancement
- [ ] Implement markdown parsing in `recipe_enhancer.py`
- [ ] Implement title emoji insertion
- [ ] Implement ingredient list emoji insertion
- [ ] Implement cooking step emoji insertion
- [ ] Implement inline markdown image generation
- [ ] Add output file generation (name-grove.md)
- [ ] Write tests for enhancer module

### Integration & Testing
- [ ] Create end-to-end pipeline integration
- [ ] Test with sample Asian recipe
- [ ] Test with sample Italian recipe
- [ ] Test with sample Mexican recipe
- [ ] Test error cases (invalid input, API failures)
- [ ] Add integration tests

### Documentation
- [ ] Document CLI usage with examples
- [ ] Document API key setup process
- [ ] Add code docstrings where missing
- [ ] Create CONTRIBUTING.md

## Phase 2: Enhancement

### Theming
- [ ] Implement sophisticated theme detection
- [ ] Add Mediterranean theme
- [ ] Add American theme
- [ ] Add French theme
- [ ] Add Indian theme
- [ ] Implement occasion-based theming (romantic, party, etc.)
- [ ] Add dietary style detection (vegan, keto, etc.)

### Features
- [ ] Implement dry-run mode
- [ ] Add emoji density controls (low/medium/high)
- [ ] Implement custom output directory option
- [ ] Add configuration file support (.recipelgroverc)
- [ ] Implement batch processing for multiple recipes
- [ ] Add verbose/debug logging mode

### Error Handling
- [ ] Improve fallback logic for emoji generation
- [ ] Add graceful degradation (use simple emojis if combinations fail)
- [ ] Implement retry logic with exponential backoff
- [ ] Add comprehensive error logging

## Phase 3: Polish

### Model Flexibility
- [ ] Add Kimi k2 model support
- [ ] Add Moonshot model support
- [ ] Add direct Anthropic API support
- [ ] Implement model switching via CLI flag
- [ ] Add model comparison/testing utilities

### Performance
- [ ] Implement emoji combination caching
- [ ] Add parallel processing for batch mode
- [ ] Optimize markdown parsing
- [ ] Add performance benchmarks

### Obsidian Integration
- [ ] Research Obsidian emoji format requirements
- [ ] Implement Obsidian-specific output mode
- [ ] Document "Automating Emojis" script setup
- [ ] Test with Obsidian vault

### Distribution
- [ ] Create PyPI package configuration
- [ ] Test `uv tool install` workflow
- [ ] Add installation docs for multiple platforms
- [ ] Create demo video/screenshots

### Documentation & Examples
- [ ] Create example gallery (input/output pairs)
- [ ] Add cookbook with common usage patterns
- [ ] Document theming system for contributors
- [ ] Add troubleshooting guide

## Future Ideas (Backlog)
- [ ] Web interface option
- [ ] Recipe thumbnail generation
- [ ] Export to multiple formats (HTML, PDF)
- [ ] Community emoji theme sharing
- [ ] Local model support (QwQ, Qwen 2.5 Coder, Mistral Small 3)
- [ ] Recipe collection management
- [ ] Smart recipe recommendations based on ingredients

---

**Current Focus**: Stage 0 → Phase 1 MVP
**Next Milestone**: Complete basic pipeline with OpenRouter + EmojiKitchen
