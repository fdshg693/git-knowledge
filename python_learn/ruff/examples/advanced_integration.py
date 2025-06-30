"""
Ruff Advanced Integration Examples
=================================

This file demonstrates advanced usage patterns of Ruff in real-world scenarios,
including custom configurations, CI/CD integration, and advanced rule management.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class RuffConfigManager:
    """
    Advanced Ruff configuration management for complex projects.

    This class demonstrates how to programmatically manage Ruff configurations
    for different project contexts and environments.
    """

    def __init__(self, project_root: Path):
        """Initialize the configuration manager."""
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "pyproject.toml"

    def generate_base_config(self) -> Dict[str, Any]:
        """Generate a base Ruff configuration for most projects."""
        return {
            "tool": {
                "ruff": {
                    "line-length": 88,
                    "target-version": "py311",
                    "select": [
                        "E",  # pycodestyle errors
                        "W",  # pycodestyle warnings
                        "F",  # Pyflakes
                        "I",  # isort
                        "B",  # flake8-bugbear
                        "C4",  # flake8-comprehensions
                        "UP",  # pyupgrade
                        "N",  # pep8-naming
                        "S",  # bandit
                        "A",  # flake8-builtins
                    ],
                    "ignore": [
                        "E501",  # line too long (handled by formatter)
                        "S101",  # assert detected (OK in tests)
                        "S311",  # random module (OK for non-crypto use)
                    ],
                    "exclude": [
                        ".git",
                        "__pycache__",
                        "venv",
                        ".venv",
                        "build",
                        "dist",
                        "migrations",
                        "node_modules",
                    ],
                    "per-file-ignores": {
                        "__init__.py": ["F401"],  # Unused imports OK
                        "tests/*": [
                            "S101",
                            "S106",
                        ],  # Assert and hardcoded passwords OK
                        "scripts/*": ["T201"],  # Print statements OK
                        "conftest.py": ["F401", "F403"],  # Star imports OK
                    },
                },
                "ruff.format": {
                    "quote-style": "double",
                    "indent-style": "space",
                    "skip-magic-trailing-comma": False,
                    "line-ending": "auto",
                },
                "ruff.isort": {
                    "known-first-party": ["myproject"],
                    "force-single-line": False,
                    "lines-after-imports": 2,
                },
            }
        }

    def customize_for_web_framework(self, framework: str) -> Dict[str, Any]:
        """Customize configuration for web framework projects."""
        config = self.generate_base_config()

        if framework.lower() == "django":
            config["tool"]["ruff"]["select"].extend(["DJ"])  # Django-specific rules
            config["tool"]["ruff"]["per-file-ignores"].update(
                {
                    "settings/*.py": ["F405"],  # Star imports OK in settings
                    "*/migrations/*": ["E501"],  # Long lines OK in migrations
                    "manage.py": ["T201"],  # Print statements OK
                }
            )

        elif framework.lower() == "fastapi":
            config["tool"]["ruff"]["select"].extend(["ASYNC"])  # Async rules
            config["tool"]["ruff"]["per-file-ignores"].update(
                {
                    "*/api/*": ["B008"],  # Function calls in defaults OK
                    "*/dependencies.py": ["B008"],  # Common in FastAPI
                }
            )

        return config

    def customize_for_data_science(self) -> Dict[str, Any]:
        """Customize configuration for data science projects."""
        config = self.generate_base_config()

        # Relax some rules common in data science contexts
        config["tool"]["ruff"]["ignore"].extend(
            [
                "T201",  # Print statements (common in notebooks/exploration)
                "E402",  # Module imports not at top (common in notebooks)
                "F841",  # Unused variables (exploration variables)
            ]
        )

        # Add data science specific rules
        config["tool"]["ruff"]["select"].extend(
            [
                "PD",  # pandas-vet
                "NPY",  # NumPy-specific rules
            ]
        )

        # Notebook-specific ignores
        config["tool"]["ruff"]["per-file-ignores"].update(
            {
                "*.ipynb": ["E402", "F841", "T201"],
                "notebooks/*": ["E402", "F841", "T201", "E501"],
                "exploratory/*": ["ALL"],  # Very permissive for exploration
            }
        )

        return config


class RuffRunner:
    """
    Advanced Ruff execution wrapper for automated workflows.

    This class provides methods for running Ruff with different configurations
    and handling the results programmatically.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the Ruff runner."""
        self.project_root = Path(project_root) if project_root else Path.cwd()

    async def run_check_async(
        self,
        paths: List[str],
        fix: bool = False,
        select: Optional[List[str]] = None,
        ignore: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Run Ruff check asynchronously and return structured results."""
        cmd = ["ruff", "check", "--output-format=json"]

        if fix:
            cmd.append("--fix")

        if select:
            cmd.extend(["--select", ",".join(select)])

        if ignore:
            cmd.extend(["--ignore", ",".join(ignore)])

        cmd.extend(paths)

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.project_root,
            )

            stdout, stderr = await process.communicate()

            result = {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "issues": [],
            }

            if stdout:
                try:
                    # Parse JSON output from Ruff
                    issues = json.loads(stdout.decode())
                    result["issues"] = issues
                except json.JSONDecodeError:
                    result["raw_output"] = stdout.decode()

            return result

        except Exception as e:
            return {"returncode": 1, "error": str(e), "issues": []}

    def run_format_check(self, paths: List[str]) -> Dict[str, Any]:
        """Check if files need formatting without applying changes."""
        cmd = ["ruff", "format", "--check", "--diff"] + paths

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            return {
                "returncode": result.returncode,
                "needs_formatting": result.returncode != 0,
                "diff": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.SubprocessError as e:
            return {"returncode": 1, "error": str(e), "needs_formatting": None}

    def analyze_codebase(self, target_dir: str = ".") -> Dict[str, Any]:
        """Perform comprehensive codebase analysis with Ruff."""
        analysis = {
            "total_files": 0,
            "issues_by_category": {},
            "most_common_issues": [],
            "files_with_issues": [],
            "summary": {},
        }

        # Run check to get all issues
        cmd = ["ruff", "check", target_dir, "--output-format=json"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.stdout:
                issues = json.loads(result.stdout)

                # Categorize issues
                issue_counts = {}
                files_with_issues = set()

                for issue in issues:
                    rule_code = issue.get("code", "UNKNOWN")
                    files_with_issues.add(issue.get("filename", "unknown"))

                    if rule_code not in issue_counts:
                        issue_counts[rule_code] = 0
                    issue_counts[rule_code] += 1

                analysis["issues_by_category"] = issue_counts
                analysis["files_with_issues"] = list(files_with_issues)
                analysis["total_issues"] = len(issues)

                # Most common issues
                sorted_issues = sorted(
                    issue_counts.items(), key=lambda x: x[1], reverse=True
                )
                analysis["most_common_issues"] = sorted_issues[:10]

                # Generate summary
                analysis["summary"] = {
                    "total_issues": len(issues),
                    "files_affected": len(files_with_issues),
                    "most_common_rule": sorted_issues[0][0] if sorted_issues else None,
                    "auto_fixable": sum(1 for issue in issues if issue.get("fix")),
                }

        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            analysis["error"] = str(e)

        return analysis


class RuffPreCommitHook:
    """
    Custom pre-commit hook implementation using Ruff.

    This class provides a more flexible alternative to the standard
    pre-commit hook, with custom logic for handling different file types.
    """

    def __init__(self, project_root: Path):
        """Initialize the pre-commit hook."""
        self.project_root = Path(project_root)
        self.runner = RuffRunner(project_root)

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if a file should be checked by Ruff."""
        if not file_path.suffix == ".py":
            return False

        # Skip generated files
        generated_patterns = [
            "migrations/",
            "__pycache__/",
            ".git/",
            "venv/",
            ".venv/",
            "build/",
            "dist/",
        ]

        file_str = str(file_path)
        return not any(pattern in file_str for pattern in generated_patterns)

    async def run_pre_commit_check(self, staged_files: List[Path]) -> Dict[str, Any]:
        """Run pre-commit checks on staged files."""
        python_files = [str(f) for f in staged_files if self.should_check_file(f)]

        if not python_files:
            return {
                "success": True,
                "message": "No Python files to check",
                "issues": [],
            }

        # Check formatting first
        format_result = self.runner.run_format_check(python_files)

        # Then run linting
        lint_result = await self.runner.run_check_async(
            python_files, fix=False  # Don't auto-fix in pre-commit
        )

        success = format_result["returncode"] == 0 and lint_result["returncode"] == 0

        return {
            "success": success,
            "format_issues": format_result.get("diff", ""),
            "lint_issues": lint_result.get("issues", []),
            "files_checked": python_files,
        }


class RuffCIIntegration:
    """
    CI/CD integration utilities for Ruff.

    This class provides methods for integrating Ruff into various
    CI/CD systems with proper reporting and error handling.
    """

    @staticmethod
    def generate_github_actions_workflow() -> str:
        """Generate a GitHub Actions workflow for Ruff."""
        return """
name: Code Quality with Ruff

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  ruff:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install Ruff
      run: pip install ruff
    
    - name: Run Ruff linter
      run: ruff check --output-format=github .
    
    - name: Run Ruff formatter check
      run: ruff format --check .
      
    - name: Generate Ruff report
      if: always()
      run: |
        ruff check --output-format=json . > ruff-report.json || true
        echo "Ruff analysis complete"
    
    - name: Upload Ruff report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: ruff-report-${{ matrix.python-version }}
        path: ruff-report.json
        """

    @staticmethod
    def generate_gitlab_ci_config() -> str:
        """Generate a GitLab CI configuration for Ruff."""
        return """
stages:
  - quality

ruff-check:
  stage: quality
  image: python:3.11
  before_script:
    - pip install ruff
  script:
    - ruff check --output-format=gitlab .
    - ruff format --check .
  artifacts:
    reports:
      codequality: ruff-codequality.json
    paths:
      - ruff-report.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
        """


# Example usage and testing functions
async def demonstrate_advanced_usage():
    """Demonstrate advanced Ruff usage patterns."""
    print("Ruff Advanced Integration Examples")
    print("=" * 40)

    # Configuration management
    config_manager = RuffConfigManager(Path.cwd())
    base_config = config_manager.generate_base_config()
    django_config = config_manager.customize_for_web_framework("django")

    print(f"Base config rules: {len(base_config['tool']['ruff']['select'])}")
    print(f"Django config rules: {len(django_config['tool']['ruff']['select'])}")

    # Async execution
    runner = RuffRunner()
    current_file = [__file__]

    check_result = await runner.run_check_async(current_file)
    print(f"Issues found: {len(check_result.get('issues', []))}")

    # Codebase analysis
    analysis = runner.analyze_codebase(".")
    print(f"Analysis: {analysis.get('summary', {})}")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_advanced_usage())
