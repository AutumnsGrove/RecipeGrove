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

## Phase 1: MVP - Core Functionality ✅

### CLI & Infrastructure ✅
- [x] Implement basic CLI command structure with Click
- [x] Add input validation (file exists, URL is valid)
- [x] Set up rich console output with progress indicators
- [x] Implement config loading from secrets.json and env vars
- [x] Add error handling and user-friendly error messages

### OmniParser Integration ✅
- [x] Research OmniParser package installation (PyPI or git)
- [x] Add OmniParser as dependency to pyproject.toml
- [x] Implement `parser.py` - parse URLs to markdown
- [x] Implement `parser.py` - parse PDF files to markdown
- [x] Implement `parser.py` - parse text files to markdown
- [x] Add error handling for unsupported formats
- [x] Write tests for parser module

### OpenRouter/LLM Integration ✅
- [x] Implement OpenRouter API client in `analyzer.py`
- [x] Create prompt template for recipe analysis
- [x] Implement `analyze_recipe()` function
- [x] Create prompt template for emoji planning
- [x] Implement `plan_emoji_placements()` function
- [x] Add retry logic and rate limiting
- [x] Write tests for analyzer module

### EmojiKitchen Integration ✅
- [x] Research EmojiKitchen package installation (PyPI or git)
- [x] Add EmojiKitchen as dependency to pyproject.toml
- [x] Implement `emoji_generator.py` - generate combinations
- [x] Implement emoji caching system
- [x] Implement fallback logic for failed combinations
- [x] Write tests for emoji generator

### Recipe Enhancement ✅
- [x] Implement markdown parsing in `recipe_enhancer.py`
- [x] Implement title emoji insertion
- [x] Implement ingredient list emoji insertion
- [x] Implement cooking step emoji insertion
- [x] Implement inline markdown image generation
- [x] Add output file generation (name-grove.md)
- [x] Write tests for enhancer module

### Integration & Testing ✅
- [x] Create end-to-end pipeline integration (in cli.py)
- [x] Create sample recipes for testing (Pad Thai, Spaghetti Carbonara)
- [x] All unit tests passing (55 tests)
- [ ] Test with real API (requires OpenRouter key)
- [ ] Add integration tests for full pipeline with mocked services

### Documentation 🚧
- [x] Code docstrings in all modules
- [ ] Document CLI usage with examples
- [ ] Document API key setup process
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
- [ ] Add configuration file support (.recipegroverc)
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

## 🚀 Phase 1.5: Testing Feedback Implementation (IN PROGRESS)

### HIGH PRIORITY - Portability & Testing
- [ ] **Emoji Path Portability** (CRITICAL)
  - [ ] Add `--emoji-path` option (relative/absolute/base64/unicode)
  - [ ] Implement relative path mode (copy emojis to ./grove-emojis/)
  - [ ] Implement base64 embedding for single-file portability
  - [ ] Make relative mode the default
- [ ] **OmniParser Testing**
  - [ ] Test URL parsing with recipe websites
  - [ ] Test PDF parsing (text and scanned)
  - [ ] Document supported formats and limitations

### HIGH PRIORITY - Performance
- [ ] **Parallel Emoji Generation**
  - [ ] Refactor emoji generation to use asyncio.gather()
  - [ ] Update CLI to handle parallel generation
  - [ ] Add progress tracking for parallel tasks
- [ ] **Enhanced Caching**
  - [ ] Verify emoji cache works correctly
  - [ ] Add cache statistics/reporting
  - [ ] Implement cache warming command

### HIGH PRIORITY - User Experience
- [ ] **Custom Emoji Preferences (~/.recipegroverc)**
  - [ ] Create UserPreferences model
  - [ ] Load preferences from home directory
  - [ ] Support favorite_emojis, avoid_emojis, defaults
  - [ ] Document preference file format
- [ ] **Input Sanitization**
  - [ ] Add prompt injection protection
  - [ ] Sanitize recipe content before LLM calls
  - [ ] Add security tests

### MEDIUM PRIORITY - Export Formats
- [ ] **HTML Export**
  - [ ] Create HTML template with embedded CSS
  - [ ] Add `--format html` option
  - [ ] Embed emojis as base64 in HTML
  - [ ] Make HTML responsive and printable

### MEDIUM PRIORITY - Seasonal Features
- [ ] **Seasonal Theme Detection**
  - [ ] Detect summer/winter/holiday recipes
  - [ ] Add seasonal emoji suggestions
  - [ ] Update themes.py with seasonal logic
  - [ ] Add `--season` override option

### MEDIUM PRIORITY - Shopping Features
- [ ] **Shopping List Generator**
  - [ ] Extract ingredients from recipe
  - [ ] Categorize by department (produce, proteins, pantry)
  - [ ] Add checkboxes for shopping
  - [ ] Add `--shopping-list` flag
  - [ ] Export as separate markdown file

### Testing & Documentation
- [ ] Add integration tests for new features
- [ ] Update README with new options
- [ ] Create EXAMPLES.md with before/after
- [ ] Create TROUBLESHOOTING.md
- [ ] Add API cost transparency to README

---

**Current Focus**: Phase 1.5 - Testing Feedback Implementation
**Next Milestone**: Production-ready with portability, performance, and enhanced features
