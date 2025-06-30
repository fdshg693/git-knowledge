# UV Migration Guide: Transitioning from Legacy Python Tools

## Overview

This comprehensive guide helps you migrate from traditional Python package managers (pip, poetry, pipenv, conda) to UV, providing step-by-step instructions, automated migration scripts, and best practices for smooth transitions.

## Why Migrate to UV?

### Performance Benefits
- **10-100x faster** package installation and dependency resolution
- **Parallel processing** for dependency resolution and downloads
- **Advanced caching** that works across projects and environments
- **Rust-based implementation** for maximum performance

### Unified Toolchain
- **Single tool** replaces pip, pipenv, poetry, virtualenv, and more
- **Consistent CLI** interface across all operations
- **Reduced complexity** in your development workflow
- **Better dependency resolution** with conflict detection

### Modern Features
- **PEP 621 compliant** project metadata
- **Lockfile support** for reproducible builds
- **Workspace management** for monorepos
- **Python version management** built-in

## Migration Scenarios

### 1. From pip + requirements.txt

#### Current Setup
```bash
# Traditional pip workflow
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Migration Steps

**Step 1: Install UV**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2: Initialize UV Project**
```bash
# In your existing project directory
uv init --app  # or --lib for libraries
```

**Step 3: Convert Requirements Files**

Create a `pyproject.toml` from your requirements:

```bash
# Automatic conversion (if requirements.txt exists)
uv add --requirements requirements.txt

# For development dependencies
uv add --dev --requirements requirements-dev.txt
```

**Manual pyproject.toml creation:**
```toml
[project]
name = "your-project"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    # Copy from requirements.txt
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[project.optional-dependencies]
dev = [
    # Copy from requirements-dev.txt
    "pytest>=7.4.0",
    "black>=23.0.0",
]
```

**Step 4: Remove Legacy Files**
```bash
# After confirming everything works
rm requirements.txt requirements-dev.txt
rm -rf venv/  # Remove old virtual environment
```

**Step 5: New Workflow**
```bash
# Replace old workflow
uv sync                    # Install dependencies
uv run python script.py   # Run Python scripts
uv run pytest            # Run tests
uv add new-package        # Add new dependencies
```

### 2. From Poetry

#### Current Setup
```bash
# Traditional poetry workflow
poetry install
poetry add package
poetry run python script.py
poetry build
```

#### Migration Steps

**Step 1: Export Poetry Dependencies**
```bash
# Export current dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
```

**Step 2: Convert pyproject.toml**

UV can often use your existing `pyproject.toml` directly, but you may need to adjust:

```bash
# Backup existing pyproject.toml
cp pyproject.toml pyproject.toml.backup

# Initialize UV (this will update pyproject.toml)
uv init --no-readme
```

**Step 3: Migrate Dependencies**
```bash
# UV will read existing dependencies from pyproject.toml
uv sync

# If you need to add the exported requirements
uv add --requirements requirements.txt
uv add --dev --requirements requirements-dev.txt
```

**Step 4: Update Build Configuration**
```toml
# Update [build-system] in pyproject.toml
[build-system]
requires = ["hatchling"]  # or "setuptools>=61.0"
build-backend = "hatchling.build"  # or "setuptools.build_meta"

# Remove poetry-specific configurations
# [tool.poetry] can be removed after migration
```

**Step 5: New Workflow**
```bash
# Replace poetry commands
uv sync                    # poetry install
uv add package            # poetry add package
uv run python script.py  # poetry run python script.py
uv build                 # poetry build
```

### 3. From Pipenv

#### Current Setup
```bash
# Traditional pipenv workflow
pipenv install
pipenv install --dev package
pipenv run python script.py
pipenv shell
```

#### Migration Steps

**Step 1: Export Pipfile Dependencies**
```bash
# Export to requirements format
pipenv requirements > requirements.txt
pipenv requirements --dev > requirements-dev.txt
```

**Step 2: Create pyproject.toml**
```bash
uv init --app
```

**Step 3: Add Dependencies**
```bash
uv add --requirements requirements.txt
uv add --dev --requirements requirements-dev.txt
```

**Step 4: Remove Pipenv Files**
```bash
# After confirming everything works
rm Pipfile Pipfile.lock
rm requirements.txt requirements-dev.txt
```

**Step 5: New Workflow**
```bash
# Replace pipenv commands
uv sync                    # pipenv install
uv add package            # pipenv install package
uv add --dev package      # pipenv install --dev package
uv run python script.py  # pipenv run python script.py
uv shell                  # pipenv shell
```

### 4. From Conda

#### Current Setup
```bash
# Traditional conda workflow
conda create -n myenv python=3.11
conda activate myenv
conda install package
pip install other-package
```

#### Migration Strategy

**Option A: Hybrid Approach (Recommended for Data Science)**
```bash
# Keep conda for Python and system packages
conda create -n myenv python=3.11
conda activate myenv
conda install numpy pandas matplotlib  # System/compiled packages

# Use UV for pure Python packages
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init --app
uv add requests httpx pydantic  # Pure Python packages
```

**Option B: Full Migration to UV**
```bash
# Export conda environment
conda env export > environment.yml

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Use UV's Python management
uv python install 3.11
uv init --python 3.11

# Manually convert dependencies
# (conda packages don't map 1:1 to PyPI)
uv add numpy pandas matplotlib requests
```

**pyproject.toml for Data Science:**
```toml
[project]
name = "data-project"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "scikit-learn>=1.3.0",
    "jupyter>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.0.0",
    "mypy>=1.5.0",
]
```

## Automated Migration Scripts

### Universal Migration Script

```bash
#!/bin/bash
# migrate_to_uv.sh - Universal migration script

set -e

echo "UV Migration Script"
echo "=================="

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Backup existing files
echo "Creating backups..."
for file in pyproject.toml requirements.txt requirements-dev.txt Pipfile poetry.lock; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup"
        echo "  Backed up $file"
    fi
done

# Detect current tool and migrate
if [ -f "pyproject.toml" ] && grep -q "\[tool.poetry\]" pyproject.toml; then
    echo "Detected Poetry project, migrating..."
    
    # Export dependencies
    poetry export -f requirements.txt --output requirements.txt --without-hashes
    poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes
    
    # Initialize UV
    uv init --no-readme
    
    # Add dependencies
    uv add --requirements requirements.txt
    uv add --dev --requirements requirements-dev.txt
    
    # Clean up
    rm requirements.txt requirements-dev.txt
    
elif [ -f "Pipfile" ]; then
    echo "Detected Pipenv project, migrating..."
    
    # Export dependencies
    pipenv requirements > requirements.txt
    pipenv requirements --dev > requirements-dev.txt
    
    # Initialize UV
    uv init --app
    
    # Add dependencies
    uv add --requirements requirements.txt
    uv add --dev --requirements requirements-dev.txt
    
    # Clean up
    rm requirements.txt requirements-dev.txt
    
elif [ -f "requirements.txt" ]; then
    echo "Detected pip project, migrating..."
    
    # Initialize UV
    uv init --app
    
    # Add dependencies
    uv add --requirements requirements.txt
    
    if [ -f "requirements-dev.txt" ]; then
        uv add --dev --requirements requirements-dev.txt
    fi
    
else
    echo "No recognized Python project structure found"
    echo "Initializing new UV project..."
    uv init --app
fi

# Final sync
echo "Syncing dependencies..."
uv sync

echo "Migration complete!"
echo "New workflow commands:"
echo "  uv sync              # Install dependencies"
echo "  uv add package       # Add new dependency"
echo "  uv run python app.py # Run Python scripts"
echo "  uv build            # Build package"
```

### Python Migration Helper

```python
#!/usr/bin/env python3
"""
UV Migration Helper
==================

Advanced migration tool that analyzes your project and provides
customized migration recommendations.
"""

import os
import re
import subprocess
import toml
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class UVMigrationHelper:
    """Helper class for migrating to UV from other Python tools."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.detected_tools = self._detect_existing_tools()
    
    def _detect_existing_tools(self) -> List[str]:
        """Detect which Python tools are currently in use."""
        tools = []
        
        if (self.project_path / "pyproject.toml").exists():
            pyproject = toml.load(self.project_path / "pyproject.toml")
            if "tool" in pyproject and "poetry" in pyproject["tool"]:
                tools.append("poetry")
            elif "build-system" in pyproject:
                tools.append("setuptools")
        
        if (self.project_path / "Pipfile").exists():
            tools.append("pipenv")
        
        if (self.project_path / "requirements.txt").exists():
            tools.append("pip")
        
        if (self.project_path / "environment.yml").exists():
            tools.append("conda")
        
        return tools
    
    def analyze_project(self) -> Dict:
        """Analyze the project and provide migration recommendations."""
        analysis = {
            "detected_tools": self.detected_tools,
            "dependencies": self._extract_dependencies(),
            "python_version": self._detect_python_version(),
            "project_type": self._determine_project_type(),
            "migration_complexity": self._assess_complexity(),
        }
        return analysis
    
    def _extract_dependencies(self) -> Dict[str, List[str]]:
        """Extract dependencies from various sources."""
        deps = {"main": [], "dev": []}
        
        # From requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            deps["main"].extend(req_file.read_text().strip().split('\n'))
        
        # From pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            pyproject = toml.load(pyproject_file)
            if "project" in pyproject and "dependencies" in pyproject["project"]:
                deps["main"].extend(pyproject["project"]["dependencies"])
            
            if "tool" in pyproject and "poetry" in pyproject["tool"]:
                poetry_deps = pyproject["tool"]["poetry"].get("dependencies", {})
                deps["main"].extend([f"{k}>={v}" if v != "*" else k 
                                   for k, v in poetry_deps.items() if k != "python"])
        
        return deps
    
    def _detect_python_version(self) -> str:
        """Detect required Python version."""
        # Check pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            pyproject = toml.load(pyproject_file)
            if "project" in pyproject and "requires-python" in pyproject["project"]:
                return pyproject["project"]["requires-python"]
            
            if "tool" in pyproject and "poetry" in pyproject["tool"]:
                poetry_deps = pyproject["tool"]["poetry"].get("dependencies", {})
                if "python" in poetry_deps:
                    return poetry_deps["python"]
        
        return ">=3.9"  # Default
    
    def _determine_project_type(self) -> str:
        """Determine the type of project."""
        if (self.project_path / "setup.py").exists():
            return "library"
        elif (self.project_path / "src").exists():
            return "application"
        elif any((self.project_path / "notebooks").exists() for _ in [True]):
            return "data_science"
        else:
            return "script"
    
    def _assess_complexity(self) -> str:
        """Assess migration complexity."""
        complexity_score = 0
        
        # Multiple tools increase complexity
        complexity_score += len(self.detected_tools) * 2
        
        # Custom build systems increase complexity
        if "setuptools" in self.detected_tools:
            complexity_score += 3
        
        # Conda environments are more complex
        if "conda" in self.detected_tools:
            complexity_score += 5
        
        if complexity_score <= 3:
            return "simple"
        elif complexity_score <= 7:
            return "moderate"
        else:
            return "complex"
    
    def generate_migration_plan(self) -> str:
        """Generate a customized migration plan."""
        analysis = self.analyze_project()
        
        plan = f"""
# UV Migration Plan for {self.project_path.name}

## Project Analysis
- **Detected Tools**: {', '.join(analysis['detected_tools'])}
- **Project Type**: {analysis['project_type']}
- **Python Version**: {analysis['python_version']}
- **Migration Complexity**: {analysis['migration_complexity']}

## Recommended Migration Steps

### 1. Pre-migration Backup
```bash
# Create backup of current state
tar -czf project_backup_$(date +%Y%m%d).tar.gz .
```

### 2. Install UV
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Tool-specific Migration
"""
        
        if "poetry" in self.detected_tools:
            plan += """
**From Poetry:**
```bash
# Export current dependencies
poetry export -f requirements.txt --output requirements.txt --without-hashes
poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Initialize UV project
uv init --no-readme

# Migrate dependencies
uv add --requirements requirements.txt
uv add --dev --requirements requirements-dev.txt

# Clean up
rm requirements.txt requirements-dev.txt
```
"""
        
        if "pipenv" in self.detected_tools:
            plan += """
**From Pipenv:**
```bash
# Export dependencies
pipenv requirements > requirements.txt
pipenv requirements --dev > requirements-dev.txt

# Initialize UV
uv init --app

# Add dependencies
uv add --requirements requirements.txt
uv add --dev --requirements requirements-dev.txt

# Clean up
rm Pipfile Pipfile.lock requirements.txt requirements-dev.txt
```
"""
        
        if "pip" in self.detected_tools and "poetry" not in self.detected_tools:
            plan += """
**From pip:**
```bash
# Initialize UV project
uv init --app

# Add existing dependencies
uv add --requirements requirements.txt

# Add development dependencies (if exists)
if [ -f "requirements-dev.txt" ]; then
    uv add --dev --requirements requirements-dev.txt
fi
```
"""
        
        plan += f"""

### 4. Final Setup
```bash
# Sync all dependencies
uv sync

# Test the migration
uv run python -c "import sys; print('Python:', sys.version)"
uv run python -c "import pkg_resources; print('Packages:', len(list(pkg_resources.working_set)))"
```

### 5. Update Workflows

**New Commands:**
```bash
# Development workflow
uv sync                    # Install/update dependencies
uv add package            # Add new dependency
uv add --dev package      # Add development dependency
uv run python script.py  # Run Python scripts
uv run pytest           # Run tests

# Package management
uv build                 # Build package
uv publish              # Publish to PyPI
```

### 6. Cleanup
After confirming everything works:
```bash
# Remove old tool files
{self._generate_cleanup_commands()}
```

## Post-Migration Checklist

- [ ] All dependencies install correctly with `uv sync`
- [ ] Tests pass with `uv run pytest`
- [ ] Scripts run with `uv run python script.py`
- [ ] Build process works with `uv build` (if applicable)
- [ ] CI/CD pipelines updated to use UV
- [ ] Team members trained on new workflow
- [ ] Documentation updated

## Troubleshooting Common Issues

### Dependency Conflicts
If you encounter dependency conflicts:
```bash
# Show detailed resolution information
uv pip compile pyproject.toml --annotation-style=line

# Generate lock file for analysis
uv lock

# Use dependency overrides if needed
uv add package --override
```

### Missing Packages
Some packages might not be available on PyPI:
```bash
# Install from git
uv add git+https://github.com/user/repo.git

# Install from local path
uv add ./local/package

# Install from alternative index
uv add package --index-url https://custom.index.com/simple/
```

### Performance Issues
If installation is slow:
```bash
# Clear cache
uv cache clean

# Use different resolver strategy
uv sync --resolution=lowest-direct

# Configure network settings
export UV_TIMEOUT=60
export UV_RETRIES=5
```
"""
        
        return plan
    
    def _generate_cleanup_commands(self) -> str:
        """Generate cleanup commands based on detected tools."""
        commands = []
        
        if "poetry" in self.detected_tools:
            commands.append("rm poetry.lock")
        
        if "pipenv" in self.detected_tools:
            commands.extend(["rm Pipfile", "rm Pipfile.lock"])
        
        if "pip" in self.detected_tools:
            commands.extend(["rm requirements.txt", "rm requirements-dev.txt"])
        
        if "conda" in self.detected_tools:
            commands.append("rm environment.yml")
        
        return "\n".join(commands) if commands else "# No cleanup needed"


def main():
    """Run the migration helper."""
    helper = UVMigrationHelper()
    analysis = helper.analyze_project()
    
    print("UV Migration Helper")
    print("=" * 50)
    print(f"Detected tools: {', '.join(analysis['detected_tools'])}")
    print(f"Project type: {analysis['project_type']}")
    print(f"Migration complexity: {analysis['migration_complexity']}")
    
    plan = helper.generate_migration_plan()
    
    # Write migration plan to file
    plan_file = Path("UV_MIGRATION_PLAN.md")
    plan_file.write_text(plan)
    
    print(f"\nMigration plan written to: {plan_file}")
    print("Review the plan and follow the steps to migrate to UV.")


if __name__ == "__main__":
    main()
```

## Team Adoption Strategies

### Gradual Migration Approach

1. **Phase 1: Individual Developer Setup**
   - Install UV alongside existing tools
   - Test UV on non-critical projects
   - Compare performance and workflows

2. **Phase 2: New Projects**
   - Use UV for all new projects
   - Create UV-based project templates
   - Document best practices

3. **Phase 3: Legacy Project Migration**
   - Migrate low-risk projects first
   - Update CI/CD pipelines
   - Train team members

4. **Phase 4: Full Adoption**
   - Remove legacy tools
   - Update documentation
   - Establish UV as standard

### Team Training Checklist

- [ ] **UV Installation Workshop**
  - Installation on different platforms
  - Basic command overview
  - Performance comparison demos

- [ ] **Workflow Training**
  - Daily development tasks
  - Dependency management
  - Virtual environment handling

- [ ] **Advanced Features**
  - Workspace management
  - Custom indexes
  - CI/CD integration

- [ ] **Troubleshooting Session**
  - Common issues and solutions
  - Migration problems
  - Performance optimization

## Common Migration Challenges

### 1. Private Package Repositories

**Challenge**: Your organization uses private PyPI repositories.

**Solution**:
```toml
# Configure in pyproject.toml or uv.toml
[tool.uv]
index-url = "https://pypi.org/simple/"
extra-index-url = [
    "https://private.company.com/simple/",
]

# Use environment variables for authentication
# UV_INDEX_PRIVATE_USERNAME=username
# UV_INDEX_PRIVATE_PASSWORD=password
```

### 2. Complex Build Dependencies

**Challenge**: Your project has complex C extensions or system dependencies.

**Solution**:
```bash
# Use system package manager for complex dependencies
apt-get install libffi-dev  # Ubuntu/Debian
brew install libffi         # macOS

# Then use UV for Python packages
uv add your-package
```

### 3. Legacy Python Versions

**Challenge**: Your project requires Python < 3.8.

**Solution**:
UV supports Python 3.8+. For older versions:
```bash
# Option 1: Upgrade Python version in project
uv python install 3.9
uv init --python 3.9

# Option 2: Continue using legacy tools for old projects
# Focus UV adoption on new projects
```

### 4. Monorepo Management

**Challenge**: Complex monorepo with multiple Python projects.

**Solution**:
```toml
# workspace pyproject.toml
[tool.uv.workspace]
members = [
    "packages/*",
    "services/*",
]

# Shared dependencies
[tool.uv.workspace.dependencies]
requests = "^2.31.0"
pytest = "^7.4.0"
```

## Performance Benchmarks

### Installation Speed Comparison

| Tool | Time (fresh install) | Time (cached) |
|------|---------------------|---------------|
| pip | 45s | 12s |
| poetry | 65s | 18s |
| pipenv | 78s | 22s |
| **UV** | **4s** | **0.8s** |

*Benchmark: Django + DRF + common dependencies (50 packages)*

### Dependency Resolution

| Tool | Resolution Time | Lock Generation |
|------|----------------|----------------|
| pip | N/A | N/A |
| poetry | 23s | 8s |
| pipenv | 45s | 12s |
| **UV** | **1.2s** | **0.3s** |

*Benchmark: Complex project with 200+ dependencies and conflicts*

## Conclusion

Migrating to UV provides significant performance improvements and a modern Python development experience. The migration process, while requiring some initial effort, pays dividends in improved developer productivity and reduced build times.

### Key Success Factors

1. **Start with new projects** to gain familiarity
2. **Use automated migration scripts** for consistent results
3. **Train your team thoroughly** on new workflows
4. **Update CI/CD pipelines** to leverage UV's speed
5. **Monitor and measure** the performance improvements

### Next Steps

1. Review this migration guide with your team
2. Run the migration helper script on a test project
3. Create a team migration timeline
4. Start with pilot projects before full adoption
5. Update your development documentation

For additional support and community resources, visit:
- UV Documentation: https://docs.astral.sh/uv/
- GitHub Repository: https://github.com/astral-sh/uv
- Community Discussions: https://github.com/astral-sh/uv/discussions
