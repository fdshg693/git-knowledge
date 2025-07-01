# MyPy: Static Type Checking for Python

## Overview

MyPy is a static type checker for Python that helps catch type-related errors before runtime. It's designed to work with Python's type hints (introduced in Python 3.5+) to provide compile-time type safety while maintaining Python's dynamic nature.

## Why Use MyPy?

### Benefits for Mid-Level Developers

1. **Early Error Detection**: Catch type-related bugs before they reach production
2. **Improved Code Documentation**: Type hints serve as self-documenting code
3. **Better IDE Support**: Enhanced autocomplete, refactoring, and navigation
4. **Safer Refactoring**: Confidence when making large-scale changes
5. **Team Collaboration**: Clear contracts between functions and modules

### Real-World Impact

```python
# Without type hints - potential runtime error
def calculate_discount(price, discount):
    return price * discount  # What if discount is "50%" instead of 0.5?

# With type hints and mypy - error caught at check time
def calculate_discount(price: float, discount: float) -> float:
    return price * discount
```

## Core Concepts

### Type Annotations

MyPy works with Python's type annotation syntax:

```python
# Basic types
name: str = "Alice"
age: int = 30
is_active: bool = True

# Function annotations
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Collection types
from typing import List, Dict, Optional

users: List[str] = ["alice", "bob"]
scores: Dict[str, int] = {"alice": 100, "bob": 85}
middle_name: Optional[str] = None  # Can be str or None
```

### Gradual Typing

MyPy supports gradual typing - you can add type hints incrementally:

```python
# Untyped function - mypy will infer types where possible
def add_numbers(a, b):
    return a + b

# Partially typed
def multiply(a: int, b):  # b will be inferred from usage
    return a * b

# Fully typed
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

## Installation and Basic Usage

### Installation

```bash
pip install mypy
```

### Running MyPy

```bash
# Check a single file
mypy script.py

# Check entire project
mypy .

# Check specific directory
mypy src/

# Exclude certain files/patterns
mypy --exclude 'tests/' src/
```

### Command Line Options

```bash
# Show error codes
mypy --show-error-codes script.py

# Strict mode (recommended for new projects)
mypy --strict script.py

# Ignore missing imports
mypy --ignore-missing-imports script.py

# Generate coverage report
mypy --html-report mypy_report/ src/
```

## Common MyPy Error Types

### Type Mismatch

```python
# Error: Argument 1 to "len" has incompatible type "int"; expected "Sized"
def get_length(value: int) -> int:
    return len(value)  # mypy error!

# Fixed version
def get_length(value: str) -> int:
    return len(value)
```

### Missing Type Annotations

```python
# Error: Function is missing a return type annotation
def process_data(data):  # mypy error in strict mode
    return data.upper()

# Fixed version
def process_data(data: str) -> str:
    return data.upper()
```

### None/Optional Handling

```python
# Error: Item "None" of "Optional[str]" has no attribute "upper"
def format_name(name: Optional[str]) -> str:
    return name.upper()  # mypy error!

# Fixed version
def format_name(name: Optional[str]) -> str:
    if name is None:
        return "Unknown"
    return name.upper()
```

## Advanced Type Features

### Union Types

```python
from typing import Union

def process_id(user_id: Union[int, str]) -> str:
    if isinstance(user_id, int):
        return f"User #{user_id}"
    return f"User {user_id}"

# Python 3.10+ syntax
def process_id_modern(user_id: int | str) -> str:
    if isinstance(user_id, int):
        return f"User #{user_id}"
    return f"User {user_id}"
```

### Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(42)  # OK
int_stack.push("hello")  # mypy error!
```

### Protocols (Structural Typing)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Both work without explicit inheritance
render(Circle())  # OK
render(Square())  # OK
```

## Integration with Development Workflow

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run MyPy
  run: |
    pip install mypy
    mypy --strict src/
```

### IDE Integration

Most modern IDEs (VS Code, PyCharm, etc.) support mypy integration:
- Real-time error highlighting
- Type information on hover
- Enhanced autocomplete

## Next Steps

This README provides a foundation for understanding mypy. For deeper exploration, check out:
- `configuration_best_practices.md` for advanced configuration options
- `examples/` directory for practical code samples
- `next_step.md` for additional topics to explore

## References

- [MyPy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Python Typing Module](https://docs.python.org/3/library/typing.html)
