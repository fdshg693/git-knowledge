#!/usr/bin/env python3
"""
UV Basic Usage Examples

This module demonstrates fundamental UV operations and workflows
for mid-level Python developers. These examples show practical
scenarios you'll encounter in real projects.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description=""):
    """
    Helper function to run shell commands and display output.

    Args:
        command (str): Shell command to execute
        description (str): Description of what the command does
    """
    if description:
        print(f"\n{'='*50}")
        print(f"DEMO: {description}")
        print(f"Command: {command}")
        print(f"{'='*50}")

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        print(f"✅ Success: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None


def demonstrate_basic_installation():
    """Demonstrate basic package installation with UV."""

    print("\n" + "=" * 60)
    print("BASIC PACKAGE INSTALLATION PATTERNS")
    print("=" * 60)

    # Single package installation
    run_command("uv pip install requests", "Installing a single package")

    # Multiple packages at once
    run_command(
        "uv pip install pandas numpy matplotlib", "Installing multiple packages"
    )

    # Version-specific installation
    run_command(
        "uv pip install 'django>=4.0,<5.0'", "Installing with version constraints"
    )

    # Installing from requirements file
    # First, create a sample requirements.txt
    requirements_content = """
requests>=2.25.0
pandas>=1.3.0
numpy>=1.21.0
pytest>=6.0.0
black>=21.0.0
"""

    with open("sample_requirements.txt", "w") as f:
        f.write(requirements_content.strip())

    run_command(
        "uv pip install -r sample_requirements.txt", "Installing from requirements.txt"
    )

    # List installed packages
    run_command("uv pip list", "Listing installed packages")


def demonstrate_virtual_environment_management():
    """Demonstrate virtual environment creation and management."""

    print("\n" + "=" * 60)
    print("VIRTUAL ENVIRONMENT MANAGEMENT")
    print("=" * 60)

    # Create a virtual environment
    run_command("uv venv demo-env", "Creating a virtual environment")

    # Create with specific Python version
    run_command(
        "uv venv --python 3.11 demo-env-py311",
        "Creating environment with specific Python version",
    )

    # Show environment info
    if os.path.exists("demo-env"):
        print("\n📁 Virtual environment created at: demo-env/")
        print("📄 To activate:")
        print("   source demo-env/bin/activate  # Unix/macOS")
        print("   demo-env\\Scripts\\activate     # Windows")


def demonstrate_project_workflow():
    """Demonstrate modern project management workflow with UV."""

    print("\n" + "=" * 60)
    print("PROJECT MANAGEMENT WORKFLOW")
    print("=" * 60)

    # Initialize a new project
    project_name = "demo-web-app"

    run_command(f"uv init {project_name}", "Initializing a new project")

    # Change to project directory for subsequent commands
    original_dir = os.getcwd()

    try:
        if os.path.exists(project_name):
            os.chdir(project_name)

            # Add runtime dependencies
            run_command("uv add fastapi uvicorn", "Adding runtime dependencies")

            # Add development dependencies
            run_command(
                "uv add --dev pytest black ruff", "Adding development dependencies"
            )

            # Show project structure
            print("\n📁 Project structure created:")
            for root, dirs, files in os.walk("."):
                level = root.replace(".", "").count(os.sep)
                indent = " " * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files:
                    print(f"{subindent}{file}")

            # Generate lockfile
            run_command("uv lock", "Generating lockfile for reproducible builds")

            # Sync dependencies
            run_command("uv sync", "Installing dependencies from lockfile")

    finally:
        os.chdir(original_dir)


def demonstrate_performance_comparison():
    """Demonstrate UV's performance characteristics."""

    print("\n" + "=" * 60)
    print("PERFORMANCE DEMONSTRATION")
    print("=" * 60)

    # Create a requirements file with many packages for testing
    large_requirements = """
requests
pandas
numpy
matplotlib
seaborn
scikit-learn
flask
django
fastapi
pytest
black
ruff
mypy
jupyter
notebook
sqlalchemy
alembic
celery
redis
"""

    with open("performance_test_requirements.txt", "w") as f:
        f.write(large_requirements.strip())

    print("⏱️  Performance test: Installing 18 popular packages")
    print("This demonstrates UV's speed advantage over traditional pip")

    # Time the installation
    import time

    start_time = time.time()

    result = run_command(
        "uv pip install -r performance_test_requirements.txt",
        "Installing packages with UV (timed)",
    )

    end_time = time.time()
    duration = end_time - start_time

    print(f"⚡ UV Installation completed in: {duration:.2f} seconds")
    print("📊 Compare this with traditional pip install time!")


def demonstrate_advanced_features():
    """Demonstrate advanced UV features for experienced users."""

    print("\n" + "=" * 60)
    print("ADVANCED FEATURES")
    print("=" * 60)

    # Python version management
    run_command("uv python list", "Listing available Python versions")

    # Dependency tree inspection
    run_command("uv pip tree", "Showing dependency tree")

    # Cache management
    run_command("uv cache dir", "Showing cache directory location")

    run_command("uv cache size", "Showing cache size")

    # Show package information
    run_command("uv pip show requests", "Showing detailed package information")


def demonstrate_migration_helpers():
    """Demonstrate tools for migrating from other package managers."""

    print("\n" + "=" * 60)
    print("MIGRATION HELPERS")
    print("=" * 60)

    # Create sample files from other tools

    # Sample Pipfile content
    pipfile_content = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = "*"
flask = "*"

[dev-packages]
pytest = "*"
"""

    # Sample poetry pyproject.toml content
    poetry_content = """
[tool.poetry]
name = "sample-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.9"
requests = "^2.25.0"
flask = "^2.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^6.0.0"
"""

    print("📋 Migration examples:")
    print("1. From pip + requirements.txt:")
    print("   uv pip install -r requirements.txt")
    print("   uv init . && uv add $(cat requirements.txt)")

    print("\n2. From Pipenv:")
    print("   pipenv requirements > requirements.txt")
    print("   uv pip install -r requirements.txt")

    print("\n3. From Poetry:")
    print("   poetry export -f requirements.txt > requirements.txt")
    print("   uv pip install -r requirements.txt")


def cleanup_demo_files():
    """Clean up files created during the demonstration."""

    print("\n" + "=" * 60)
    print("CLEANUP")
    print("=" * 60)

    files_to_remove = ["sample_requirements.txt", "performance_test_requirements.txt"]

    dirs_to_remove = ["demo-env", "demo-env-py311", "demo-web-app"]

    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  Removed: {file}")

    import shutil

    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Removed directory: {dir_name}")


def main():
    """Main demonstration function."""

    print("🚀 UV Package Manager - Basic Usage Examples")
    print("=" * 60)
    print("This demo shows practical UV usage patterns for real projects.")
    print("Each section demonstrates different aspects of UV functionality.")

    try:
        # Check if UV is installed
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ UV is not installed. Please install UV first:")
            print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
            return

        print(f"✅ UV Version: {result.stdout.strip()}")

        # Run demonstrations
        demonstrate_basic_installation()
        demonstrate_virtual_environment_management()
        demonstrate_project_workflow()
        demonstrate_performance_comparison()
        demonstrate_advanced_features()
        demonstrate_migration_helpers()

    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    finally:
        # Always attempt cleanup
        cleanup_demo_files()

    print("\n✨ Demo completed!")
    print("💡 Pro tip: Use 'uv --help' for more commands and options")


if __name__ == "__main__":
    main()
