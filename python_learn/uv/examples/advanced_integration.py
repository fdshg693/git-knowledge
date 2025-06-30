#!/usr/bin/env python3
"""
UV Advanced Integration Patterns
================================

This script demonstrates advanced UV integration patterns for real-world scenarios,
including CI/CD pipelines, Docker multi-stage builds, workspace management,
and custom repository configurations.

Target Audience: Mid-level Python developers
Focus: Production-ready patterns and enterprise usage
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict


class UVIntegrationManager:
    """
    Advanced UV integration manager for complex development workflows.

    Demonstrates enterprise-grade patterns for:
    - CI/CD pipeline integration
    - Docker multi-stage builds
    - Workspace and monorepo management
    - Custom index and private repository usage
    - Advanced dependency resolution
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.uv_available = self._check_uv_availability()

    def _check_uv_availability(self) -> bool:
        """Check if UV is available in the system."""
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, check=True
            )
            print(f"✓ UV detected: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "⚠ UV not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
            return False

    def setup_ci_cd_pipeline(self) -> Dict[str, str]:
        """
        Generate CI/CD pipeline configurations for popular platforms.

        Returns optimized workflows for GitHub Actions, GitLab CI, and Jenkins
        that leverage UV's speed and caching capabilities.
        """
        github_actions = """
name: CI/CD with UV
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Install UV
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
      
    - name: Install dependencies
      run: |
        uv sync --frozen
        uv run pip list
      
    - name: Run tests
      run: |
        uv run pytest tests/ --cov=src/ --cov-report=xml
        
    - name: Build package
      run: uv build
      
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
"""

        gitlab_ci = """
# GitLab CI with UV caching
image: python:3.11

variables:
  UV_CACHE_DIR: .uv-cache

cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .uv-cache/

before_script:
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - export PATH="$HOME/.cargo/bin:$PATH"

stages:
  - test
  - build
  - deploy

test:
  stage: test
  script:
    - uv sync --frozen
    - uv run pytest tests/ --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml

build:
  stage: build
  script:
    - uv build
  artifacts:
    paths:
      - dist/
"""

        return {
            "github_actions": github_actions,
            "gitlab_ci": gitlab_ci,
            "jenkins": self._generate_jenkins_pipeline(),
        }

    def _generate_jenkins_pipeline(self) -> str:
        """Generate Jenkins pipeline configuration."""
        return """
pipeline {
    agent any
    
    environment {
        UV_CACHE_DIR = "${WORKSPACE}/.uv-cache"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'export PATH="$HOME/.cargo/bin:$PATH"'
            }
        }
        
        stage('Dependencies') {
            steps {
                sh 'uv sync --frozen'
            }
        }
        
        stage('Test') {
            steps {
                sh 'uv run pytest tests/ --junitxml=results.xml'
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }
        
        stage('Build') {
            steps {
                sh 'uv build'
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
"""

    def create_docker_multistage_build(self) -> str:
        """
        Create optimized Docker multi-stage build using UV.

        This pattern significantly reduces build times and image sizes
        by leveraging UV's performance and efficient dependency management.
        """
        dockerfile_content = """
# Multi-stage Docker build with UV
# Optimized for production deployments

# Build stage - includes UV and build dependencies
FROM python:3.11-slim as builder

# Install UV
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Install dependencies and build the application
RUN uv sync --frozen --no-dev
RUN uv build

# Production stage - minimal runtime image
FROM python:3.11-slim as production

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies only
WORKDIR /app
COPY --from=builder /app/dist/*.whl .

# Install the built wheel
RUN pip install --no-cache-dir *.whl && rm *.whl

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "your_app"]

# Development stage - includes dev dependencies
FROM builder as development

# Install development dependencies
RUN uv sync --frozen

# Install debugging tools
RUN uv add --dev debugpy pytest-xdist

# Expose debug port
EXPOSE 5678

CMD ["uv", "run", "python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "your_app"]
"""
        return dockerfile_content

    def setup_workspace_management(self) -> Dict[str, str]:
        """
        Configure workspace management for monorepos and multi-project setups.

        Demonstrates advanced patterns for managing multiple related projects
        with shared dependencies and coordinated development workflows.
        """
        workspace_config = {
            "pyproject.toml": """
[tool.uv.workspace]
members = [
    "packages/core",
    "packages/api", 
    "packages/cli",
    "services/web",
    "services/worker"
]

[tool.uv.workspace.dependencies]
# Shared dependencies across workspace
requests = "^2.31.0"
pydantic = "^2.5.0"
pytest = "^7.4.0"

[project]
name = "my-workspace"
version = "0.1.0"
requires-python = ">=3.9"
""",
            "workspace_manager.py": """
#!/usr/bin/env python3
import subprocess
from pathlib import Path

class WorkspaceManager:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root)
    
    def sync_all_projects(self):
        '''Sync dependencies for all workspace members'''
        subprocess.run(["uv", "sync", "--all-packages"], check=True)
    
    def run_tests_all(self):
        '''Run tests across all workspace packages'''
        for member_dir in ["packages", "services"]:
            if (self.root / member_dir).exists():
                subprocess.run([
                    "uv", "run", "--all-packages", 
                    "pytest", f"{member_dir}/*/tests/"
                ], check=True)
    
    def build_all_packages(self):
        '''Build all distributable packages'''
        subprocess.run(["uv", "build", "--all"], check=True)
""",
        }
        return workspace_config

    def configure_private_repositories(self) -> Dict[str, str]:
        """
        Configure UV for private repositories and custom indexes.

        Essential for enterprise environments with proprietary packages
        and secure development workflows.
        """
        configurations = {
            "uv.toml": """
[tool.uv]
# Configure private repository access
index-url = "https://pypi.org/simple/"
extra-index-url = [
    "https://pypi.private-company.com/simple/",
    "https://artifacts.company.com/pypi/simple/"
]

# Authentication via environment variables
# Set UV_INDEX_<NAME>_USERNAME and UV_INDEX_<NAME>_PASSWORD
index-strategy = "first-index"

# Cache configuration for enterprise networks
cache-dir = "~/.cache/uv"
no-cache = false

# Network configuration
timeout = 30
retries = 3

[tool.uv.pip]
# Additional pip-specific configurations
trusted-host = [
    "pypi.private-company.com",
    "artifacts.company.com"
]
""",
            "authentication_setup.py": """
import os
import keyring
from getpass import getpass

def setup_private_repo_auth():
    '''Setup authentication for private repositories'''
    
    # Option 1: Environment variables (recommended for CI/CD)
    repos = {
        "PRIVATE_COMPANY": "https://pypi.private-company.com/simple/",
        "ARTIFACTS": "https://artifacts.company.com/pypi/simple/"
    }
    
    for repo_name, repo_url in repos.items():
        username_key = f"UV_INDEX_{repo_name}_USERNAME"
        password_key = f"UV_INDEX_{repo_name}_PASSWORD"
        
        if not os.getenv(username_key):
            username = input(f"Username for {repo_url}: ")
            password = getpass(f"Password for {repo_url}: ")
            
            # Store in system keyring
            keyring.set_password(f"uv_{repo_name.lower()}", "username", username)
            keyring.set_password(f"uv_{repo_name.lower()}", "password", password)
            
            print(f"Set environment variables:")
            print(f"export {username_key}={username}")
            print(f"export {password_key}='<password>'")

def test_private_repo_access():
    '''Test access to configured private repositories'''
    import subprocess
    
    try:
        # Test installation from private repo
        result = subprocess.run([
            "uv", "pip", "install", "--dry-run", "private-package-name"
        ], capture_output=True, text=True, check=True)
        
        print("✓ Private repository access configured correctly")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Private repository access failed: {e.stderr}")
        return False
""",
        }
        return configurations

    def demonstrate_advanced_resolution(self):
        """
        Demonstrate advanced dependency resolution scenarios.

        Shows how UV handles complex dependency conflicts and provides
        tools for analyzing and resolving resolution issues.
        """
        if not self.uv_available:
            print("UV not available for demonstration")
            return

        print("\n=== Advanced Dependency Resolution Demo ===")

        # Create a temporary project with complex dependencies
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a pyproject.toml with potentially conflicting dependencies
            pyproject_content = """
[project]
name = "complex-deps-demo"
version = "0.1.0"
requires-python = ">=3.9"
dependencies = [
    "django>=4.0,<5.0",
    "fastapi>=0.100.0",
    "requests>=2.30.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]

data = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
]

web = [
    "gunicorn>=21.0.0",
    "uvicorn[standard]>=0.23.0",
]
"""

            (temp_path / "pyproject.toml").write_text(pyproject_content)

            try:
                # Demonstrate resolution with conflict analysis
                print("Analyzing dependency resolution...")
                result = subprocess.run(
                    [
                        "uv",
                        "pip",
                        "compile",
                        "pyproject.toml",
                        "--annotation-style",
                        "line",
                    ],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                print("✓ Dependency resolution successful")
                print("Lock file preview (first 10 lines):")
                lines = result.stdout.split("\n")[:10]
                for line in lines:
                    print(f"  {line}")

                # Show resolution tree
                tree_result = subprocess.run(
                    ["uv", "pip", "tree"], cwd=temp_path, capture_output=True, text=True
                )

                if tree_result.returncode == 0:
                    print("\nDependency tree structure:")
                    print(
                        tree_result.stdout[:500] + "..."
                        if len(tree_result.stdout) > 500
                        else tree_result.stdout
                    )

            except subprocess.CalledProcessError as e:
                print(f"Resolution conflict detected: {e.stderr}")
                print("UV provides detailed conflict analysis to help resolve issues")


def main():
    """
    Main demonstration function showcasing advanced UV integration patterns.
    """
    print("UV Advanced Integration Patterns Demo")
    print("=" * 50)

    manager = UVIntegrationManager()

    if not manager.uv_available:
        print("Please install UV to run the full demonstration")
        return

    # 1. CI/CD Pipeline Generation
    print("\n1. Generating CI/CD Pipeline Configurations...")
    pipelines = manager.setup_ci_cd_pipeline()
    print(f"✓ Generated configurations for {len(pipelines)} platforms")

    # 2. Docker Multi-stage Build
    print("\n2. Creating Docker Multi-stage Build Configuration...")
    dockerfile = manager.create_docker_multistage_build()
    print(f"✓ Generated Dockerfile ({len(dockerfile.splitlines())} lines)")

    # 3. Workspace Management
    print("\n3. Setting up Workspace Management...")
    workspace_configs = manager.setup_workspace_management()
    print(f"✓ Generated {len(workspace_configs)} workspace configuration files")

    # 4. Private Repository Configuration
    print("\n4. Configuring Private Repository Access...")
    private_configs = manager.configure_private_repositories()
    print(f"✓ Generated {len(private_configs)} private repository configuration files")

    # 5. Advanced Dependency Resolution Demo
    print("\n5. Demonstrating Advanced Dependency Resolution...")
    manager.demonstrate_advanced_resolution()

    print("\n" + "=" * 50)
    print("Advanced Integration Demo Complete!")
    print("\nKey Benefits Demonstrated:")
    print("• 10-100x faster CI/CD pipelines")
    print("• Optimized Docker builds with multi-stage patterns")
    print("• Enterprise-grade workspace management")
    print("• Secure private repository integration")
    print("• Advanced dependency conflict resolution")

    print("\nNext Steps:")
    print("• Implement these patterns in your production workflows")
    print("• Customize configurations for your specific environment")
    print("• Monitor performance improvements in your CI/CD pipelines")


if __name__ == "__main__":
    main()
