# Ruff: The Ultra-Fast Python Linter and Formatter

## Overview

Ruff is an extremely fast Python linter and code formatter written in Rust. It's designed to replace multiple tools (flake8, black, isort, pydocstyle, pyupgrade, autoflake, and more) with a single, unified tool that runs 10-100x faster than existing Python-based tools.

## Why Ruff Matters for Mid-Level Python Developers

### Performance Revolution
- **Speed**: 10-100x faster than traditional Python linters
- **Memory Efficiency**: Lower memory footprint compared to running multiple tools
- **Single Tool**: Replaces dozens of existing linting and formatting tools

### Developer Experience
- **Zero Configuration**: Works out of the box with sensible defaults
- **Incremental Adoption**: Can be gradually integrated into existing projects
- **IDE Integration**: Excellent support for VS Code, PyCharm, and other editors

## Core Concepts

### 1. Linting vs Formatting

**Linting** identifies potential issues in your code:
- Style violations (PEP 8)
- Potential bugs (unused variables, imports)
- Code complexity issues
- Security vulnerabilities

**Formatting** automatically fixes code style:
- Line length
- Indentation
- Import sorting
- Quote style consistency

### 2. Rule Categories

Ruff organizes rules into categories based on the tools they replace:

- **E/W**: pycodestyle errors and warnings
- **F**: Pyflakes
- **I**: isort (import sorting)
- **N**: pep8-naming
- **D**: pydocstyle (docstring conventions)
- **UP**: pyupgrade (syntax modernization)
- **S**: bandit (security)
- **B**: flake8-bugbear
- **A**: flake8-builtins
- **C4**: flake8-comprehensions
- **And many more...**

## Installation and Basic Setup

### Installation
```bash
# Via pip
pip install ruff

# Via conda
conda install -c conda-forge ruff

# Via homebrew (macOS)
brew install ruff
```

### Basic Usage
```bash
# Check code (linting)
ruff check .

# Format code
ruff format .

# Check and fix automatically fixable issues
ruff check --fix .

# Check specific files
ruff check path/to/file.py

# Show what would be fixed without applying changes
ruff check --fix --diff .
```

## Configuration

### pyproject.toml Configuration
```toml
[tool.ruff]
# Same as Black's default line length
line-length = 88

# Enable specific rule sets
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

# Ignore specific rules
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

# Exclude files/directories
exclude = [
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "build",
    "dist",
]

# Target Python version
target-version = "py311"

[tool.ruff.format]
# Use single quotes instead of double quotes
quote-style = "single"

# Indent with spaces, not tabs
indent-style = "space"

# Respect magic trailing commas
skip-magic-trailing-comma = false

[tool.ruff.isort]
# Known first-party imports
known-first-party = ["myproject"]

# Force single line imports
force-single-line = false

[tool.ruff.per-file-ignores]
# Ignore specific rules for specific files
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/*" = ["S101"]      # Allow assert statements in tests
```

## Real-World Applications

### 1. CI/CD Integration

**GitHub Actions Example:**
```yaml
name: Code Quality
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install ruff
    - name: Lint with ruff
      run: ruff check .
    - name: Check formatting
      run: ruff format --check .
```

### 2. Pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

### 3. VS Code Integration
```json
// settings.json
{
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        },
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

## Advanced Features

### 1. Custom Rules and Plugins
Ruff supports many flake8 plugins out of the box:
- `flake8-bugbear`: Additional bug and design problems
- `flake8-comprehensions`: Better list/dict/set comprehensions
- `flake8-simplify`: Simplification suggestions
- `bandit`: Security testing

### 2. Automatic Fixes
Many rules can be automatically fixed:
```bash
# Fix all auto-fixable issues
ruff check --fix .

# Show what would be fixed
ruff check --fix --diff .

# Fix specific rule categories
ruff check --fix --select "I,UP" .
```

### 3. Notebook Support
```bash
# Lint Jupyter notebooks
ruff check notebook.ipynb

# Format Jupyter notebooks
ruff format notebook.ipynb
```

## Migration Strategies

### From Black + isort + flake8
1. **Install Ruff**: `pip install ruff`
2. **Basic Configuration**: Start with minimal config
3. **Gradual Migration**: Enable rule sets one by one
4. **Remove Old Tools**: Uninstall replaced tools
5. **Update CI/CD**: Replace old tool commands with ruff

### Configuration Migration
```toml
# Old setup.cfg
[flake8]
max-line-length = 88
ignore = E203, W503

[isort]
profile = black

# New pyproject.toml
[tool.ruff]
line-length = 88
select = ["E", "W", "F", "I"]
ignore = ["E203", "W503"]

[tool.ruff.isort]
profile = "black"
```

## Best Practices

### 1. Gradual Adoption
- Start with basic rules (E, W, F)
- Add rule categories incrementally
- Use `--fix` to automatically resolve simple issues
- Review and adjust ignored rules regularly

### 2. Team Workflow
- Establish team-wide configuration in `pyproject.toml`
- Use pre-commit hooks to enforce standards
- Include formatting checks in CI/CD
- Document exceptions and custom rules

### 3. Performance Optimization
- Use `.ruffcache` for faster subsequent runs
- Configure appropriate `exclude` patterns
- Use `--select` to focus on specific rule categories
- Leverage parallel processing (automatic)

## Common Pitfalls and Solutions

### 1. Configuration Conflicts
**Problem**: Rules conflicting with existing code style
**Solution**: Use `per-file-ignores` and gradual rule adoption

### 2. Performance in Large Codebases
**Problem**: Even with Ruff's speed, very large codebases can be slow
**Solution**: Use appropriate exclusion patterns and focused rule selection

### 3. Integration Issues
**Problem**: Conflicts with existing tooling
**Solution**: Proper configuration and understanding of rule precedence

## Conclusion

Ruff represents a significant advancement in Python code quality tooling. For mid-level Python developers, it offers:

- **Efficiency**: Dramatically faster linting and formatting
- **Simplicity**: Single tool replacing multiple dependencies
- **Flexibility**: Extensive configuration options
- **Modern**: Built with current Python best practices in mind

The key to successful Ruff adoption is gradual integration, proper configuration, and understanding of its extensive rule system. Start simple, then expand your rule set as your team becomes comfortable with the tool.
