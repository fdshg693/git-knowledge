#!/usr/bin/env python3
"""
UV Project Templates and Initialization Patterns
================================================

This script demonstrates project template generation and initialization patterns
using UV for different types of Python projects, including microservices,
data science projects, library development, and testing workflows.

Target Audience: Mid-level Python developers
Focus: Project scaffolding and standardized workflows
"""

import subprocess
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class ProjectType(Enum):
    """Supported project types for template generation."""

    MICROSERVICE = "microservice"
    DATA_SCIENCE = "data_science"
    CLI_TOOL = "cli_tool"
    LIBRARY = "library"
    WEB_API = "web_api"
    DESKTOP_APP = "desktop_app"


@dataclass
class ProjectTemplate:
    """Configuration for a project template."""

    name: str
    description: str
    dependencies: List[str]
    dev_dependencies: List[str]
    directory_structure: List[str]
    config_files: Dict[str, str]
    python_version: str = ">=3.9"


class UVProjectTemplateManager:
    """
    Advanced project template manager using UV.

    Provides standardized project initialization patterns for different
    types of Python projects with best practices and modern tooling.
    """

    def __init__(self, base_directory: str = "."):
        self.base_dir = Path(base_directory)
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[ProjectType, ProjectTemplate]:
        """Initialize predefined project templates."""
        return {
            ProjectType.MICROSERVICE: ProjectTemplate(
                name="microservice",
                description="FastAPI-based microservice with monitoring and testing",
                dependencies=[
                    "fastapi>=0.104.0",
                    "uvicorn[standard]>=0.24.0",
                    "pydantic>=2.5.0",
                    "pydantic-settings>=2.1.0",
                    "httpx>=0.25.0",
                    "structlog>=23.2.0",
                    "prometheus-client>=0.19.0",
                ],
                dev_dependencies=[
                    "pytest>=7.4.0",
                    "pytest-asyncio>=0.21.0",
                    "pytest-cov>=4.1.0",
                    "httpx>=0.25.0",
                    "ruff>=0.1.0",
                    "mypy>=1.7.0",
                    "pre-commit>=3.5.0",
                ],
                directory_structure=[
                    "src/{project_name}",
                    "src/{project_name}/api",
                    "src/{project_name}/core",
                    "src/{project_name}/models",
                    "tests",
                    "tests/unit",
                    "tests/integration",
                    "docker",
                    "docs",
                    "scripts",
                ],
                config_files={
                    "main.py": self._get_microservice_main(),
                    "Dockerfile": self._get_microservice_dockerfile(),
                    "docker-compose.yml": self._get_microservice_docker_compose(),
                    ".pre-commit-config.yaml": self._get_precommit_config(),
                },
            ),
            ProjectType.DATA_SCIENCE: ProjectTemplate(
                name="data_science",
                description="Data science project with Jupyter, pandas, and MLOps tools",
                dependencies=[
                    "pandas>=2.1.0",
                    "numpy>=1.25.0",
                    "matplotlib>=3.8.0",
                    "seaborn>=0.13.0",
                    "scikit-learn>=1.3.0",
                    "jupyter>=1.0.0",
                    "plotly>=5.17.0",
                    "mlflow>=2.8.0",
                ],
                dev_dependencies=[
                    "pytest>=7.4.0",
                    "black>=23.0.0",
                    "isort>=5.12.0",
                    "flake8>=6.1.0",
                    "mypy>=1.7.0",
                    "nbqa>=1.7.0",
                ],
                directory_structure=[
                    "data/raw",
                    "data/processed",
                    "data/external",
                    "notebooks",
                    "src/{project_name}",
                    "src/{project_name}/data",
                    "src/{project_name}/features",
                    "src/{project_name}/models",
                    "src/{project_name}/visualization",
                    "tests",
                    "reports/figures",
                    "models",
                ],
                config_files={
                    "jupyter_config.py": self._get_jupyter_config(),
                    "cookiecutter.json": self._get_data_science_cookiecutter(),
                    ".gitignore": self._get_data_science_gitignore(),
                },
            ),
            ProjectType.CLI_TOOL: ProjectTemplate(
                name="cli_tool",
                description="Command-line interface tool with Click and rich output",
                dependencies=[
                    "click>=8.1.0",
                    "rich>=13.7.0",
                    "typer>=0.9.0",
                    "pydantic>=2.5.0",
                    "toml>=0.10.0",
                ],
                dev_dependencies=[
                    "pytest>=7.4.0",
                    "pytest-click>=1.1.0",
                    "black>=23.0.0",
                    "ruff>=0.1.0",
                    "mypy>=1.7.0",
                ],
                directory_structure=[
                    "src/{project_name}",
                    "src/{project_name}/commands",
                    "src/{project_name}/config",
                    "src/{project_name}/utils",
                    "tests",
                    "docs",
                ],
                config_files={
                    "cli.py": self._get_cli_main(),
                    "config.py": self._get_cli_config(),
                },
            ),
            ProjectType.LIBRARY: ProjectTemplate(
                name="library",
                description="Python library with comprehensive testing and documentation",
                dependencies=[],  # Minimal dependencies for libraries
                dev_dependencies=[
                    "pytest>=7.4.0",
                    "pytest-cov>=4.1.0",
                    "black>=23.0.0",
                    "ruff>=0.1.0",
                    "mypy>=1.7.0",
                    "sphinx>=7.2.0",
                    "sphinx-rtd-theme>=1.3.0",
                    "pre-commit>=3.5.0",
                    "tox>=4.11.0",
                ],
                directory_structure=[
                    "src/{project_name}",
                    "tests",
                    "docs",
                    "docs/source",
                    "examples",
                ],
                config_files={
                    "__init__.py": '"""Library module."""\n\n__version__ = "0.1.0"\n',
                    "py.typed": "",  # PEP 561 marker file
                    "tox.ini": self._get_tox_config(),
                    "docs/conf.py": self._get_sphinx_config(),
                },
            ),
        }

    def create_project(
        self, project_type: ProjectType, project_name: str, target_directory: str = None
    ) -> Path:
        """
        Create a new project from template.

        Args:
            project_type: Type of project to create
            project_name: Name of the project
            target_directory: Directory to create project in (default: current)

        Returns:
            Path to the created project directory
        """
        template = self.templates[project_type]
        target_dir = Path(target_directory) if target_directory else self.base_dir
        project_path = target_dir / project_name

        print(f"Creating {template.description}...")
        print(f"Project: {project_name}")
        print(f"Location: {project_path}")

        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)

        # Create directory structure
        self._create_directory_structure(project_path, template, project_name)

        # Generate pyproject.toml
        self._create_pyproject_toml(project_path, template, project_name)

        # Create configuration files
        self._create_config_files(project_path, template, project_name)

        # Initialize UV project
        self._initialize_uv_project(project_path)

        # Create README
        self._create_readme(project_path, template, project_name)

        print(f"✓ Project '{project_name}' created successfully!")
        print("Next steps:")
        print(f"  cd {project_name}")
        print("  uv sync")
        print(f"  uv run python -m {project_name}")

        return project_path

    def _create_directory_structure(
        self, project_path: Path, template: ProjectTemplate, project_name: str
    ):
        """Create the directory structure for the project."""
        for directory in template.directory_structure:
            dir_path = project_path / directory.format(project_name=project_name)
            dir_path.mkdir(parents=True, exist_ok=True)

            # Create __init__.py for Python packages
            if "src" in str(dir_path) and project_name in str(dir_path):
                (dir_path / "__init__.py").touch()

    def _create_pyproject_toml(
        self, project_path: Path, template: ProjectTemplate, project_name: str
    ):
        """Create pyproject.toml with project configuration."""
        pyproject_content = f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "{template.description}"
readme = "README.md"
requires-python = "{template.python_version}"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
{self._format_dependencies(template.dependencies)}
]

[project.optional-dependencies]
dev = [
{self._format_dependencies(template.dev_dependencies)}
]

[project.urls]
Homepage = "https://github.com/yourusername/{project_name}"
Repository = "https://github.com/yourusername/{project_name}.git"
Documentation = "https://{project_name}.readthedocs.io/"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{project_name}"]

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src/{project_name} --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["src/{project_name}"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
"""

        (project_path / "pyproject.toml").write_text(pyproject_content)

    def _format_dependencies(self, dependencies: List[str]) -> str:
        """Format dependencies for pyproject.toml."""
        if not dependencies:
            return ""
        formatted = []
        for dep in dependencies:
            formatted.append(f'    "{dep}",')
        return "\n".join(formatted)

    def _create_config_files(
        self, project_path: Path, template: ProjectTemplate, project_name: str
    ):
        """Create additional configuration files."""
        for filename, content in template.config_files.items():
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content.format(project_name=project_name))

    def _initialize_uv_project(self, project_path: Path):
        """Initialize UV project and install dependencies."""
        try:
            # Initialize git repository
            subprocess.run(
                ["git", "init"], cwd=project_path, check=True, capture_output=True
            )

            # Sync dependencies with UV
            subprocess.run(
                ["uv", "sync"], cwd=project_path, check=True, capture_output=True
            )

            print("✓ UV project initialized and dependencies installed")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not initialize UV project: {e}")
            print("You may need to run 'uv sync' manually")

    def _create_readme(
        self, project_path: Path, template: ProjectTemplate, project_name: str
    ):
        """Create a comprehensive README.md file."""
        readme_content = f"""# {project_name}

{template.description}

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name}.git
cd {project_name}

# Install dependencies with UV
uv sync

# Or install in development mode
uv pip install -e ".[dev]"
```

## Usage

```python
import {project_name}

# Your usage examples here
```

## Development

This project uses UV for dependency management and follows modern Python development practices.

### Setup Development Environment

```bash
# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies including dev dependencies
uv sync

# Install pre-commit hooks (if configured)
uv run pre-commit install
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov={project_name} --cov-report=html

# Run specific test file
uv run pytest tests/test_specific.py
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/

# Type checking
uv run mypy src/
```

### Building and Publishing

```bash
# Build the package
uv build

# Publish to PyPI (configure authentication first)
uv publish
```

## Project Structure

```
{project_name}/
├── src/{project_name}/     # Main package code
├── tests/                  # Test files
├── docs/                   # Documentation
├── pyproject.toml         # Project configuration
├── README.md              # This file
└── .gitignore            # Git ignore patterns
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure code quality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""

        (project_path / "README.md").write_text(readme_content)

    # Template content methods
    def _get_microservice_main(self) -> str:
        return '''"""
FastAPI microservice main application.
"""
from fastapi import FastAPI
from {project_name}.api import health, metrics

app = FastAPI(
    title="{project_name}",
    description="A FastAPI microservice",
    version="0.1.0"
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name} API"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

    def _get_microservice_dockerfile(self) -> str:
        return """FROM python:3.11-slim

# Install UV
RUN pip install uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ src/

# Install the application
RUN uv pip install -e .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uv", "run", "uvicorn", "{project_name}.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    def _get_microservice_docker_compose(self) -> str:
        return """version: '3.8'

services:
  {project_name}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - ./src:/app/src
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
"""

    def _get_precommit_config(self) -> str:
        return """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
"""

    def _get_jupyter_config(self) -> str:
        return """c = get_config()

# Notebook server configuration
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.port = 8888
c.NotebookApp.open_browser = False
c.NotebookApp.token = ''
c.NotebookApp.password = ''

# Enable extensions
c.NotebookApp.nbserver_extensions = {
    'jupyter_nbextensions_configurator': True,
}
"""

    def _get_data_science_cookiecutter(self) -> str:
        return """{
    "project_name": "Data Science Project",
    "repo_name": "data-science-project",
    "author_name": "Your Name",
    "description": "A short description of the project.",
    "open_source_license": ["MIT", "BSD-3-Clause", "No license file"],
    "python_interpreter": ["python3", "python"]
}
"""

    def _get_data_science_gitignore(self) -> str:
        return """# Data files
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Jupyter Notebook checkpoints
.ipynb_checkpoints/
*/.ipynb_checkpoints/*

# Model files
models/*.pkl
models/*.joblib
models/*.h5

# Large files
*.csv
*.json
*.parquet
*.feather

# Environment
.env
"""

    def _get_cli_main(self) -> str:
        return '''"""
Command-line interface for {project_name}.
"""
import click
from rich.console import Console
from {project_name}.commands import main_commands

console = Console()

@click.group()
@click.version_option()
def cli():
    """
    {project_name} - A modern CLI tool.
    """
    pass

# Register command groups
cli.add_command(main_commands.main)

if __name__ == "__main__":
    cli()
'''

    def _get_cli_config(self) -> str:
        return '''"""
Configuration management for {project_name}.
"""
from pathlib import Path
from typing import Dict, Any
import toml

DEFAULT_CONFIG = {{
    "output_format": "json",
    "verbose": False,
    "cache_dir": "~/.{project_name}/cache"
}}

def load_config(config_path: Path = None) -> Dict[str, Any]:
    """Load configuration from file or return defaults."""
    if config_path and config_path.exists():
        return toml.load(config_path)
    return DEFAULT_CONFIG
'''

    def _get_tox_config(self) -> str:
        return """[tox]
envlist = py39,py310,py311,py312,lint,type

[testenv]
deps = 
    pytest
    pytest-cov
commands = pytest tests/ --cov={project_name} --cov-report=xml

[testenv:lint]
deps = 
    black
    ruff
commands = 
    black --check src/ tests/
    ruff check src/ tests/

[testenv:type]
deps = mypy
commands = mypy src/
"""

    def _get_sphinx_config(self) -> str:
        return '''"""
Sphinx configuration file.
"""
project = '{project_name}'
copyright = '2024, Your Name'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
'''


def main():
    """
    Demonstration of UV project template functionality.
    """
    print("UV Project Template Manager Demo")
    print("=" * 50)

    manager = UVProjectTemplateManager()

    print("Available Project Templates:")
    for project_type in ProjectType:
        template = manager.templates[project_type]
        print(f"  {project_type.value}: {template.description}")

    print("\nExample: Creating a microservice project")
    print("Would run: manager.create_project(ProjectType.MICROSERVICE, 'my-api')")

    print("\nExample: Creating a data science project")
    print("Would run: manager.create_project(ProjectType.DATA_SCIENCE, 'ml-analysis')")

    print("\nExample: Creating a CLI tool")
    print("Would run: manager.create_project(ProjectType.CLI_TOOL, 'my-cli')")

    print("\nFeatures demonstrated:")
    print("• Template-based project generation")
    print("• Automatic UV project initialization")
    print("• Best practice project structure")
    print("• Modern Python tooling configuration")
    print("• Type-specific dependency management")
    print("• Comprehensive documentation generation")


if __name__ == "__main__":
    main()
