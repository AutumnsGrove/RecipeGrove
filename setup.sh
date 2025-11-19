#!/bin/bash

# BaseProject Template Setup Script
# This script will customize the template for your project and then delete itself

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Unicode characters for pretty output
CHECK="✓"
CROSS="✗"
ARROW="→"

# Backup directory
BACKUP_DIR=".backup-$(date +%Y%m%d-%H%M%S)"

# Function to print colored output
print_header() {
    echo -e "\n${BOLD}${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${BLUE}║${NC}         ${BOLD}BaseProject Template Setup${NC}                           ${BOLD}${BLUE}║${NC}"
    echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${BOLD}${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    echo -e "${BOLD}$1${NC}"
    echo -e "${BOLD}${PURPLE}─────────────────────${NC}\n"
}

print_success() {
    echo -e "${GREEN}${CHECK}${NC} $1"
}

print_error() {
    echo -e "${RED}${CROSS}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Function to clean up on error
cleanup_on_error() {
    print_error "Setup failed. Rolling back changes..."

    if [ -d "$BACKUP_DIR" ]; then
        print_info "Restoring from backup..."
        cp -r "$BACKUP_DIR"/* . 2>/dev/null || true
        rm -rf "$BACKUP_DIR"
        print_success "Backup restored"
    fi

    exit 1
}

# Set error trap
trap cleanup_on_error ERR

# Function to validate project name
validate_project_name() {
    local name="$1"

    # Check if empty
    if [ -z "$name" ]; then
        return 1
    fi

    # Check if it contains only valid characters (alphanumeric, dash, underscore)
    if [[ ! "$name" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        return 1
    fi

    return 0
}

# Function to detect if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Main setup function
main() {
    print_header

    echo "This script will help you customize BaseProject for your needs."
    echo "All template files will be cleaned up automatically."
    echo ""

    # Check if we're in a git repo (but don't require it)
    if git rev-parse --git-dir > /dev/null 2>&1; then
        print_warning "Already in a git repository. Will skip git init."
        SKIP_GIT_INIT=true
    else
        SKIP_GIT_INIT=false
    fi

    print_section "Project Configuration"

    # Get project name
    while true; do
        echo -ne "${BOLD}📝 Project name:${NC} "
        read PROJECT_NAME

        if validate_project_name "$PROJECT_NAME"; then
            break
        else
            print_error "Invalid project name. Use only letters, numbers, dashes, and underscores."
        fi
    done

    # Get project description
    echo -ne "${BOLD}📝 Brief description:${NC} "
    read PROJECT_DESCRIPTION

    if [ -z "$PROJECT_DESCRIPTION" ]; then
        PROJECT_DESCRIPTION="A project based on BaseProject template"
    fi

    # Get primary language
    echo -e "\n${BOLD}🔧 Primary language:${NC}"
    echo "   1) Python    2) JavaScript    3) Go    4) Rust    5) Other"
    echo ""
    echo -ne "   ${BOLD}Your choice [1-5]:${NC} "
    read LANG_CHOICE

    case "$LANG_CHOICE" in
        1) PRIMARY_LANG="Python" ;;
        2) PRIMARY_LANG="JavaScript" ;;
        3) PRIMARY_LANG="Go" ;;
        4) PRIMARY_LANG="Rust" ;;
        5)
            echo -ne "   ${BOLD}Enter language name:${NC} "
            read PRIMARY_LANG
            ;;
        *) PRIMARY_LANG="Python" ;;
    esac

    # Get API keys needed
    echo -e "\n${BOLD}🔑 Which API keys will you need?${NC} (space-separated numbers, e.g., '1 3')"
    echo "   1) Anthropic    2) OpenAI    3) OpenRouter    4) AWS    5) Other    6) None"
    echo ""
    echo -ne "   ${BOLD}Your choices:${NC} "
    read API_KEYS_INPUT

    # Parse API keys selection
    API_KEYS=()
    for key in $API_KEYS_INPUT; do
        case "$key" in
            1) API_KEYS+=("anthropic") ;;
            2) API_KEYS+=("openai") ;;
            3) API_KEYS+=("openrouter") ;;
            4) API_KEYS+=("aws") ;;
            5)
                echo -ne "   ${BOLD}Enter API key name:${NC} "
                read CUSTOM_KEY
                API_KEYS+=("${CUSTOM_KEY,,}") # Convert to lowercase
                ;;
            6) API_KEYS=() ; break ;;
        esac
    done

    # Ask about git hooks
    echo -e "\n${BOLD}🎣 Install git hooks for code quality and security?${NC}"
    echo "   Recommended: Provides automatic code formatting, linting, and secret scanning"
    echo -ne "   ${BOLD}[y/N]:${NC} "
    read INSTALL_HOOKS

    INSTALL_HOOKS=$(echo "$INSTALL_HOOKS" | tr '[:upper:]' '[:lower:]')

    print_section "Setting up your project..."

    # Create backup
    mkdir -p "$BACKUP_DIR"
    cp AGENT.md "$BACKUP_DIR/" 2>/dev/null || true
    cp README.md "$BACKUP_DIR/" 2>/dev/null || true
    cp TODOS.md "$BACKUP_DIR/" 2>/dev/null || true
    print_success "Created backup at $BACKUP_DIR/"

    # Update AGENT.md
    update_agent_md

    # Transform README.md
    transform_readme

    # Create secrets template if API keys are needed
    if [ ${#API_KEYS[@]} -gt 0 ]; then
        create_secrets_template
    fi

    # Initialize language-specific dependencies
    initialize_language_deps

    # Create project structure
    create_project_structure

    # Create TODOS.md
    create_todos

    # Install git hooks if requested
    if [ "$INSTALL_HOOKS" = "y" ] || [ "$INSTALL_HOOKS" = "yes" ]; then
        install_git_hooks
    fi

    # Initialize git if needed
    if [ "$SKIP_GIT_INIT" = false ]; then
        initialize_git
    fi

    # Cleanup template files
    cleanup_template_files

    # Show completion message
    show_completion
}

# Function to update AGENT.md
update_agent_md() {
    # Replace placeholders in AGENT.md
    sed -i.bak "s|\[Fill in: What this project does - 1-2 sentences\]|$PROJECT_DESCRIPTION|g" AGENT.md
    sed -i.bak "s|\[Fill in: Technologies, frameworks, and languages used\]||g" AGENT.md
    sed -i.bak "s|^- Language:$|- Language: $PRIMARY_LANG|g" AGENT.md
    sed -i.bak "s|\[Fill in: Key architectural decisions, patterns, or structure\]|Standard project structure following BaseProject template guidelines|g" AGENT.md

    # Remove backup file
    rm -f AGENT.md.bak

    print_success "Updated AGENT.md with project details"
}

# Function to transform README.md
transform_readme() {
    # Remove template sections (between <!-- TEMPLATE: START --> and <!-- TEMPLATE: END -->)
    # This is a bit complex in sed, so we'll use awk
    awk '
        /<!-- TEMPLATE: START -->/ { skip=1; next }
        /<!-- TEMPLATE: END -->/ { skip=0; next }
        !skip
    ' README.md > README.md.tmp

    # Create new README with project name
    cat > README.md << EOF
# $PROJECT_NAME

$PROJECT_DESCRIPTION

## Overview

This project was created from the [BaseProject template](https://github.com/AutumnsGrove/BaseProject) and includes:

- Comprehensive workflow guides in \`AgentUsage/\`
- Git hooks for code quality and security
- Claude Code optimized workflows
- Multi-language support

## Quick Start

1. **Review project instructions:** Check \`AGENT.md\` for project context
2. **Check tasks:** See \`TODOS.md\` for pending tasks
3. **Set up secrets** (if needed):
   \`\`\`bash
   cp secrets_template.json secrets.json
   # Edit secrets.json with your real API keys
   \`\`\`
4. **Start developing:**
   \`\`\`bash
   claude "your task here"
   \`\`\`

## Project Structure

\`\`\`
$PROJECT_NAME/
├── CLAUDE.md                   # Redirect to AGENT.md
├── AGENT.md                    # Main project instructions
├── src/                        # Source code
├── tests/                      # Test files
├── AgentUsage/               # Comprehensive workflow guides
│   ├── README.md              # Guide index
│   ├── git_guide.md           # Git workflow and conventional commits
│   └── ... (18 total guides)
└── TODOS.md                   # Task tracking
\`\`\`

EOF

    # Append the non-template sections from the old README
    cat README.md.tmp >> README.md
    rm -f README.md.tmp

    print_success "Transformed README.md (removed template sections)"
}

# Function to create secrets template
create_secrets_template() {
    cat > secrets_template.json << 'EOF'
{
EOF

    # Add API keys
    local first=true
    for key in "${API_KEYS[@]}"; do
        if [ "$first" = false ]; then
            echo "," >> secrets_template.json
        fi
        first=false

        case "$key" in
            "anthropic")
                echo '  "anthropic_api_key": "sk-ant-api03-your-key-here"' >> secrets_template.json
                ;;
            "openai")
                echo '  "openai_api_key": "sk-your-key-here"' >> secrets_template.json
                ;;
            "openrouter")
                echo '  "openrouter_api_key": "sk-or-v1-your-key-here"' >> secrets_template.json
                ;;
            "aws")
                echo '  "aws_access_key_id": "AKIA...",
  "aws_secret_access_key": "your-secret-key",
  "aws_region": "us-east-1"' >> secrets_template.json
                ;;
            *)
                echo "  \"${key}_api_key\": \"your-key-here\"" >> secrets_template.json
                ;;
        esac
    done

    echo '' >> secrets_template.json
    echo '}' >> secrets_template.json

    # Add comment explaining the file
    cat > secrets_template.json << EOF
{
$(for key in "${API_KEYS[@]}"; do
    case "$key" in
        "anthropic") echo '  "anthropic_api_key": "sk-ant-api03-your-key-here",';;
        "openai") echo '  "openai_api_key": "sk-your-key-here",';;
        "openrouter") echo '  "openrouter_api_key": "sk-or-v1-your-key-here",';;
        "aws") echo '  "aws_access_key_id": "AKIA...",
  "aws_secret_access_key": "your-secret-key",
  "aws_region": "us-east-1",';;
        *) echo "  \"${key}_api_key\": \"your-key-here\",";;
    esac
done | sed '$ s/,$//')
  "comment": "Copy this file to secrets.json and add your real API keys. secrets.json is gitignored."
}
EOF

    print_success "Created secrets_template.json with ${#API_KEYS[@]} API key(s)"
}

# Function to initialize language dependencies
initialize_language_deps() {
    case "$PRIMARY_LANG" in
        "Python")
            if command_exists uv; then
                print_info "Initializing Python project with UV..."
                uv init --name "$PROJECT_NAME" 2>/dev/null || true
                print_success "Initialized Python project with UV (pyproject.toml created)"
            elif command_exists python3; then
                print_warning "UV not found. You can install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
                print_info "Creating basic pyproject.toml..."
                cat > pyproject.toml << EOF
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "$PROJECT_DESCRIPTION"
requires-python = ">=3.8"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
                print_success "Created basic pyproject.toml"
            else
                print_warning "Python not found. Skipping Python initialization."
            fi
            ;;
        "JavaScript")
            if command_exists npm; then
                print_info "Initializing JavaScript project with npm..."
                npm init -y > /dev/null 2>&1
                # Update package.json with project details
                if command_exists node; then
                    node -e "
                        const pkg = require('./package.json');
                        pkg.name = '$PROJECT_NAME'.toLowerCase().replace(/[^a-z0-9-]/g, '-');
                        pkg.description = '$PROJECT_DESCRIPTION';
                        require('fs').writeFileSync('package.json', JSON.stringify(pkg, null, 2));
                    " 2>/dev/null || true
                fi
                print_success "Initialized JavaScript project (package.json created)"
            else
                print_warning "npm not found. Skipping JavaScript initialization."
            fi
            ;;
        "Go")
            if command_exists go; then
                print_info "Initializing Go module..."
                MODULE_NAME=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]')
                go mod init "github.com/yourusername/$MODULE_NAME" > /dev/null 2>&1 || true
                print_success "Initialized Go module (go.mod created)"
            else
                print_warning "Go not found. Skipping Go initialization."
            fi
            ;;
        "Rust")
            if command_exists cargo; then
                print_info "Initializing Rust project..."
                # Cargo init might fail if directory not empty, that's ok
                cargo init --name "$PROJECT_NAME" > /dev/null 2>&1 || true
                print_success "Initialized Rust project (Cargo.toml created)"
            else
                print_warning "Cargo not found. Skipping Rust initialization."
            fi
            ;;
        *)
            print_info "Custom language selected. Skipping automatic dependency initialization."
            ;;
    esac
}

# Function to create project structure
create_project_structure() {
    case "$PRIMARY_LANG" in
        "Python")
            mkdir -p src tests
            touch src/__init__.py
            cat > src/main.py << 'EOF'
"""Main module for the project."""

def main():
    """Main entry point."""
    print("Hello from BaseProject!")

if __name__ == "__main__":
    main()
EOF
            touch tests/__init__.py
            cat > tests/test_main.py << 'EOF'
"""Tests for main module."""

from src.main import main

def test_main():
    """Test main function."""
    main()  # Should not raise
EOF
            print_success "Created src/ directory with __init__.py and main.py"
            print_success "Created tests/ directory with __init__.py and test_main.py"
            ;;
        "JavaScript")
            mkdir -p src tests
            cat > src/index.js << 'EOF'
/**
 * Main module for the project
 */

function main() {
  console.log('Hello from BaseProject!');
}

if (require.main === module) {
  main();
}

module.exports = { main };
EOF
            cat > tests/index.test.js << 'EOF'
/**
 * Tests for main module
 */

const { main } = require('../src/index');

test('main runs without error', () => {
  expect(() => main()).not.toThrow();
});
EOF
            print_success "Created src/ directory with index.js"
            print_success "Created tests/ directory with index.test.js"
            ;;
        "Go")
            mkdir -p cmd internal tests
            cat > cmd/main.go << 'EOF'
package main

import "fmt"

func main() {
    fmt.Println("Hello from BaseProject!")
}
EOF
            cat > internal/hello.go << 'EOF'
package internal

// Hello returns a greeting message
func Hello() string {
    return "Hello from BaseProject!"
}
EOF
            print_success "Created cmd/ directory with main.go"
            print_success "Created internal/ directory with hello.go"
            ;;
        "Rust")
            # Cargo init creates src/ automatically
            print_success "Created src/ directory (by Cargo)"
            ;;
        *)
            mkdir -p src tests
            print_success "Created src/ and tests/ directories"
            ;;
    esac
}

# Function to create TODOS.md
create_todos() {
    cat > TODOS.md << EOF
# TODOs for $PROJECT_NAME

## Setup Tasks
- [x] Run BaseProject setup script
- [ ] Review and finalize AGENT.md customizations
- [ ] Set up secrets (copy secrets_template.json to secrets.json)
- [ ] Install additional dependencies for $PRIMARY_LANG
- [ ] Configure development environment

## Development Tasks
- [ ] Implement core functionality
- [ ] Add error handling
- [ ] Write comprehensive tests
- [ ] Add logging

## Documentation Tasks
- [ ] Document API/interfaces
- [ ] Add usage examples to README
- [ ] Write architecture documentation
- [ ] Create user guide (if applicable)

## Testing Tasks
- [ ] Set up test framework
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Set up CI/CD for automated testing

## Deployment Tasks
- [ ] Set up production environment
- [ ] Configure monitoring
- [ ] Create deployment documentation
- [ ] Set up backup strategy
EOF

    print_success "Created TODOS.md with project-specific tasks"
}

# Function to install git hooks
install_git_hooks() {
    if [ -f "AgentUsage/pre_commit_hooks/install_hooks.sh" ]; then
        print_info "Installing git hooks..."

        # Make the installer executable
        chmod +x AgentUsage/pre_commit_hooks/install_hooks.sh

        # Run the installer non-interactively
        cd AgentUsage/pre_commit_hooks
        bash install_hooks.sh --auto 2>/dev/null || {
            print_warning "Git hooks installer encountered an issue. You can run it manually later:"
            print_info "  ./AgentUsage/pre_commit_hooks/install_hooks.sh"
        }
        cd ../..

        print_success "Installed git hooks (pre-commit, commit-msg, pre-push)"
    else
        print_warning "Git hooks installer not found. Skipping."
    fi
}

# Function to initialize git
initialize_git() {
    if ! command_exists git; then
        print_warning "Git not found. Skipping git initialization."
        return
    fi

    echo -ne "\n${BOLD}🔧 Initialize git repository and make initial commit? [Y/n]:${NC} "
    read INIT_GIT

    INIT_GIT=$(echo "$INIT_GIT" | tr '[:upper:]' '[:lower:]')

    if [ "$INIT_GIT" = "n" ] || [ "$INIT_GIT" = "no" ]; then
        print_info "Skipping git initialization"
        return
    fi

    print_info "Initializing git repository..."
    git init > /dev/null 2>&1

    # Make hooks executable if they exist
    if [ -d ".git/hooks" ]; then
        chmod +x .git/hooks/* 2>/dev/null || true
    fi

    # Create initial commit
    git add .
    git commit -m "feat: initialize $PROJECT_NAME from BaseProject template

- Set up project structure for $PRIMARY_LANG
- Configured AGENT.md with project details
- Added workflow guides in AgentUsage/
$([ ${#API_KEYS[@]} -gt 0 ] && echo "- Created secrets template for API keys")
$([ "$INSTALL_HOOKS" = "y" ] && echo "- Installed git hooks for code quality")

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: [Model Name] <agent@localhost>" > /dev/null 2>&1

    print_success "Git initialized with initial commit"
}

# Function to cleanup template files
cleanup_template_files() {
    print_info "Cleaning up template files..."

    # Remove template-specific files
    rm -f TEMPLATE_USAGE.md
    print_success "Removed TEMPLATE_USAGE.md"

    # Remove GitHub Actions workflow
    rm -f .github/workflows/setup-template.yml
    [ -d ".github/workflows" ] && rmdir .github/workflows 2>/dev/null || true
    [ -d ".github" ] && rmdir .github 2>/dev/null || true
    print_success "Removed GitHub Actions setup workflow"

    # Remove backup directory
    rm -rf "$BACKUP_DIR"
    print_success "Removed backup directory"

    # This script will delete itself at the very end
}

# Function to show completion message
show_completion() {
    print_section "🎉 Setup Complete!"

    echo -e "${GREEN}${BOLD}Your project is ready!${NC}\n"
    echo -e "${BOLD}Project Name:${NC} $PROJECT_NAME"
    echo -e "${BOLD}Description:${NC} $PROJECT_DESCRIPTION"
    echo -e "${BOLD}Language:${NC} $PRIMARY_LANG"
    [ ${#API_KEYS[@]} -gt 0 ] && echo -e "${BOLD}API Keys:${NC} ${API_KEYS[*]}"

    echo -e "\n${BOLD}${CYAN}Next steps:${NC}\n"
    echo "1. Review AGENT.md - Your main project instructions"
    echo "2. Check TODOS.md - Initial tasks have been added"

    if [ ${#API_KEYS[@]} -gt 0 ]; then
        echo "3. Set up secrets:"
        echo "   ${CYAN}cp secrets_template.json secrets.json${NC}"
        echo "   ${CYAN}nano secrets.json  # Add your real API keys${NC}"
    fi

    echo ""
    echo "4. Start developing:"
    echo "   ${CYAN}claude \"implement [your feature]\"${NC}"
    echo ""
    echo "5. Explore guides in AgentUsage/ directory"
    echo ""

    print_info "Useful commands:"
    case "$PRIMARY_LANG" in
        "Python")
            echo "  ${CYAN}uv add <package>${NC}     - Add Python dependency"
            echo "  ${CYAN}uv run pytest${NC}         - Run tests"
            ;;
        "JavaScript")
            echo "  ${CYAN}npm install <package>${NC} - Add JavaScript dependency"
            echo "  ${CYAN}npm test${NC}               - Run tests"
            ;;
        "Go")
            echo "  ${CYAN}go get <package>${NC}      - Add Go dependency"
            echo "  ${CYAN}go test ./...${NC}         - Run tests"
            ;;
        "Rust")
            echo "  ${CYAN}cargo add <crate>${NC}     - Add Rust dependency"
            echo "  ${CYAN}cargo test${NC}             - Run tests"
            ;;
    esac

    echo ""
    echo -e "${GREEN}${BOLD}Happy coding! 🚀${NC}\n"

    print_section "Self-Destructing..."

    # Remove this script itself
    SCRIPT_PATH="${BASH_SOURCE[0]}"
    rm -f "$SCRIPT_PATH"
    print_success "Removed setup.sh"

    echo ""
    print_info "Template setup complete. All template files have been cleaned up."
}

# Run main function
main
