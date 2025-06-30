"""
Ruff Basic Usage Examples
========================

This file demonstrates basic usage patterns of Ruff for Python code quality.
These examples show common scenarios and how Ruff helps improve code quality.
"""

# Example 1: Import Sorting and Organization
# Ruff automatically sorts and organizes imports using isort rules

# Before Ruff formatting:
# import os
# from typing import Dict, List
# import sys
# from collections import defaultdict
# import asyncio

# After Ruff formatting (with I001, I002 rules):
import asyncio
import os
import sys
from collections import defaultdict
from typing import Dict, List


# Example 2: Code Style Fixes
# Ruff fixes many PEP 8 violations automatically


def poorly_formatted_function(x, y, z):
    """Example of poorly formatted code that Ruff will fix."""
    # E701: Multiple statements on one line
    if x > 0:
        return x * y

    # E261: At least two spaces before inline comment
    result = x + y  # This comment needs spacing

    # E302: Expected 2 blank lines
    def nested_function():
        return z

    return result


# After Ruff formatting:
def well_formatted_function(x, y, z):
    """Example of properly formatted code after Ruff processing."""
    # Proper spacing and line breaks
    if x > 0:
        return x * y

    # Proper comment spacing
    result = x + y  # This comment has proper spacing

    # Proper blank lines between functions
    def nested_function():
        return z

    return result


# Example 3: Unused Variables and Imports Detection
# Ruff detects and can remove unused variables and imports


def function_with_unused_variables():
    """Demonstrates F841 (unused variable) detection."""
    # F841: Local variable is assigned to but never used
    unused_var = "This variable is never used"
    used_var = "This variable is used"

    # F401: Module imported but unused would be detected if we had unused imports

    return used_var


# Example 4: List/Dict Comprehension Improvements
# Ruff suggests better comprehensions using C4 rules


def comprehension_examples():
    """Examples of comprehension improvements."""

    # C401: Unnecessary generator - rewrite as a set comprehension
    # Before: set(x for x in range(10))
    better_set = {x for x in range(10)}

    # C402: Unnecessary generator - rewrite as a dict comprehension
    # Before: dict((x, x**2) for x in range(5))
    better_dict = {x: x**2 for x in range(5)}

    # C403: Unnecessary list call around generator
    # Before: list(x*2 for x in range(5))
    better_list = [x * 2 for x in range(5)]

    return better_set, better_dict, better_list


# Example 5: String Quote Consistency
# Ruff can enforce consistent quote usage


def quote_examples():
    """Examples of quote consistency."""
    # Ruff can enforce single or double quotes consistently
    single_quoted = "This uses single quotes"
    double_quoted = "This uses double quotes"

    # For strings with quotes inside, Ruff chooses appropriately
    contains_single = "This string contains 'single quotes' inside"
    contains_double = 'This string contains "double quotes" inside'

    return single_quoted, double_quoted, contains_single, contains_double


# Example 6: Modern Python Syntax (pyupgrade rules)
# Ruff can modernize Python syntax automatically


def modern_syntax_examples():
    """Examples of syntax modernization."""

    # UP006: Use `list` instead of `List` for type annotations (Python 3.9+)
    def old_style_typing(items: List[str]) -> Dict[str, int]:
        # UP007: Use `X | Y` for union types (Python 3.10+)
        result: Dict[str, int] = {}
        for item in items:
            result[item] = len(item)
        return result

    # Modern equivalent (after Ruff UP rules):
    def modern_style_typing(items: list[str]) -> dict[str, int]:
        result: dict[str, int] = {}
        for item in items:
            result[item] = len(item)
        return result

    return old_style_typing, modern_style_typing


# Example 7: Security Issues Detection
# Ruff includes bandit security rules (S prefix)


def security_examples():
    """Examples of security issue detection."""

    # S101: Use of assert detected (not recommended in production)
    def function_with_assert(value):
        assert value > 0, "Value must be positive"
        return value * 2

    # S102: Use of exec detected (security risk)
    def dangerous_exec_usage():
        # This would be flagged by Ruff
        # exec("print('Hello World')")
        pass

    # S108: Probable insecure usage of temp file/directory
    def temp_file_usage():
        import tempfile

        # Better: use tempfile.mkstemp() or tempfile.NamedTemporaryFile()
        temp_dir = tempfile.mkdtemp()
        return temp_dir

    return function_with_assert, dangerous_exec_usage, temp_file_usage


# Example 8: Complexity and Readability
# Ruff can detect overly complex code patterns


def complexity_examples():
    """Examples of complexity detection and improvement."""

    # C901: Function is too complex (McCabe complexity)
    def complex_function(a, b, c, d, e):
        """This function has high cyclomatic complexity."""
        if a > 0:
            if b > 0:
                if c > 0:
                    if d > 0:
                        if e > 0:
                            return a + b + c + d + e
                        else:
                            return a + b + c + d
                    else:
                        return a + b + c
                else:
                    return a + b
            else:
                return a
        else:
            return 0

    # Better approach with early returns
    def simplified_function(a, b, c, d, e):
        """Simplified version with lower complexity."""
        if a <= 0:
            return 0
        if b <= 0:
            return a
        if c <= 0:
            return a + b
        if d <= 0:
            return a + b + c
        if e <= 0:
            return a + b + c + d
        return a + b + c + d + e

    return complex_function, simplified_function


# Example 9: Docstring Improvements
# Ruff includes pydocstyle rules for better documentation


class DocumentationExample:
    """
    Example class showing docstring best practices.

    This class demonstrates proper docstring formatting that Ruff
    will validate using pydocstyle rules.
    """

    def __init__(self, name: str, value: int):
        """
        Initialize the example object.

        Args:
            name: The name of the object
            value: The initial value
        """
        self.name = name
        self.value = value

    def calculate(self, multiplier: float) -> float:
        """
        Calculate a result based on the value and multiplier.

        Args:
            multiplier: The multiplier to apply

        Returns:
            The calculated result

        Raises:
            ValueError: If multiplier is negative
        """
        if multiplier < 0:
            raise ValueError("Multiplier must be non-negative")
        return self.value * multiplier


# Example 10: File-level Configuration
# This comment shows how you might configure Ruff for specific files

# ruff: noqa: E501
# This disables line length checking for this entire file


def very_long_function_name_that_exceeds_normal_line_length_limits():
    """Sometimes you need to disable specific rules for specific cases."""
    return (
        "This function name is intentionally very long to demonstrate rule exceptions"
    )


if __name__ == "__main__":
    # Example usage of the functions above
    print("Ruff Basic Usage Examples")
    print("=" * 30)

    # Test comprehension examples
    sets, dicts, lists = comprehension_examples()
    print(f"Better comprehensions: {len(sets)} items in set")

    # Test quote examples
    quotes = quote_examples()
    print(f"Quote examples: {len(quotes)} strings")

    # Test documentation example
    doc_example = DocumentationExample("test", 42)
    result = doc_example.calculate(2.5)
    print(f"Documentation example result: {result}")
