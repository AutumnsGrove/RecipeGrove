# Contributing to RecipeGrove

Thanks for your interest in contributing!

## Getting Started

1. **Fork and clone** the repository
2. **Install dependencies**: `uv sync`
3. **Run tests**: `uv run pytest`

## Development Setup

### Requirements
- Python 3.11+
- UV package manager
- OpenRouter API key (for testing with real API)

### Install
```bash
git clone https://github.com/AutumnsGrove/RecipeGrove.git
cd RecipeGrove
uv sync
```

### API Keys
Copy `secrets_template.json` to `secrets.json` and add your keys:
```json
{
  "openrouter_api_key": "your-key-here"
}
```

Or use environment variables:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Making Changes

### Code Style
- Follow existing patterns in the codebase
- Use type hints
- Add docstrings to functions
- Keep functions small and focused

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_parser.py

# Run with coverage
uv run pytest --cov=recipegrove
```

### Before Submitting
1. Run tests: `uv run pytest`
2. Format code: `uv run black src/ tests/`
3. Check types: `uv run mypy src/`
4. Lint: `uv run ruff check src/`

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes with clear commits
3. Add/update tests for your changes
4. Ensure all tests pass
5. Push and create a PR

### Commit Messages
Use conventional commits:
- `feat: add new feature`
- `fix: bug fix`
- `docs: documentation update`
- `test: add tests`
- `refactor: code refactoring`

## Areas We Need Help

- **More cuisine themes** (Indian, French, Mediterranean, etc.)
- **Better emoji fallback strategies**
- **Integration tests** with mocked services
- **Documentation** improvements
- **Bug fixes** and error handling

## Questions?

Open an issue or reach out to the maintainers.

---

**Note:** This project uses UV for package management. All commands should use `uv run` prefix.
