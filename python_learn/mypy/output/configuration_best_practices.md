# MyPy Configuration and Best Practices

## Configuration File (mypy.ini)

MyPy can be configured using several file formats. The most common is `mypy.ini`:

```ini
[mypy]
# Global options
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True

# Strict mode (recommended for new projects)
strict = True

# Output options
show_error_codes = True
pretty = True
color_output = True

# Per-module options
[mypy-requests.*]
ignore_missing_imports = True

[mypy-pytest.*]
ignore_missing_imports = True

# Legacy code with gradual adoption
[mypy-legacy.*]
ignore_errors = True
```

## Alternative Configuration Formats

### pyproject.toml (Recommended for Modern Projects)

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
strict = true
show_error_codes = true

[[tool.mypy.overrides]]
module = ["requests.*", "pytest.*"]
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "legacy.*"
ignore_errors = true
```

### setup.cfg

```ini
[mypy]
python_version = 3.9
strict = True
show_error_codes = True

[mypy-requests.*]
ignore_missing_imports = True
```

## Best Practices for Type Hinting

### 1. Start Gradually

```python
# Begin with function signatures
def calculate_total(items: List[Dict[str, Any]]) -> float:
    # Implementation can remain untyped initially
    total = 0
    for item in items:
        total += item.get('price', 0)
    return total

# Then add internal type annotations
def calculate_total(items: List[Dict[str, Any]]) -> float:
    total: float = 0.0
    for item in items:
        price: float = item.get('price', 0.0)
        total += price
    return total
```

### 2. Use Specific Types Over Generic Ones

```python
# Avoid
def process_data(data: Any) -> Any:
    return data

# Prefer
def process_user_data(data: Dict[str, Union[str, int]]) -> UserProfile:
    return UserProfile(
        name=data['name'],
        age=data['age']
    )
```

### 3. Leverage Type Aliases for Complex Types

```python
# Define reusable type aliases
UserId = int
UserData = Dict[str, Union[str, int, bool]]
UserCollection = List[UserData]

def get_user(user_id: UserId) -> Optional[UserData]:
    # Implementation
    pass

def process_users(users: UserCollection) -> List[UserId]:
    # Implementation
    pass
```

### 4. Use NewType for Domain-Specific Types

```python
from typing import NewType

# Create distinct types for similar data
UserId = NewType('UserId', int)
ProductId = NewType('ProductId', int)

def get_user(user_id: UserId) -> User:
    # Implementation
    pass

def get_product(product_id: ProductId) -> Product:
    # Implementation
    pass

# Prevents mixing up IDs
user_id = UserId(123)
product_id = ProductId(456)

get_user(product_id)  # MyPy error!
```

### 5. Handle Optional Types Properly

```python
# Explicit None checking
def format_username(name: Optional[str]) -> str:
    if name is None:
        return "Anonymous"
    return name.title()

# Using walrus operator (Python 3.8+)
def process_config(config: Optional[Dict[str, str]]) -> str:
    if (host := config and config.get('host')):
        return f"Connecting to {host}"
    return "No host configured"
```

### 6. Use Protocols for Duck Typing

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def serialize(self) -> Dict[str, Any]: ...

class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
    
    def serialize(self) -> Dict[str, Any]:
        return {"name": self.name, "email": self.email}

def save_data(obj: Serializable) -> None:
    data = obj.serialize()
    # Save data logic
    pass
```

## Common Configuration Scenarios

### Strict Mode for New Projects

```ini
[mypy]
strict = True
# This enables:
# - disallow_any_generics
# - disallow_subclassing_any
# - disallow_untyped_calls
# - disallow_untyped_defs
# - disallow_incomplete_defs
# - check_untyped_defs
# - disallow_untyped_decorators
# - no_implicit_optional
# - warn_redundant_casts
# - warn_unused_ignores
# - warn_return_any
# - no_implicit_reexport
# - strict_equality
```

### Gradual Adoption for Legacy Projects

```ini
[mypy]
# Start with basic checks
check_untyped_defs = True
warn_return_any = True
warn_unused_ignores = True

# Gradually increase strictness
# disallow_incomplete_defs = True  # Enable later
# disallow_untyped_defs = True     # Enable last

# Ignore problematic modules initially
[mypy-legacy.old_module]
ignore_errors = True

[mypy-third_party_without_stubs.*]
ignore_missing_imports = True
```

### Team Collaboration Settings

```ini
[mypy]
# Consistent experience across team
python_version = 3.9
strict = True
show_error_codes = True
pretty = True

# Helpful for team reviews
warn_unused_configs = True
warn_redundant_casts = True

# Cache for faster subsequent runs
cache_dir = .mypy_cache
```

## Handling Third-Party Libraries

### Type Stubs

```bash
# Install official type stubs
pip install types-requests types-PyYAML types-redis

# Check available stubs
mypy --install-types
```

### Custom Stub Files

Create `.pyi` files for libraries without type information:

```python
# stubs/external_lib.pyi
from typing import Any, Dict, Optional

class APIClient:
    def __init__(self, api_key: str) -> None: ...
    def get(self, endpoint: str) -> Dict[str, Any]: ...
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: ...
```

## Performance Optimization

### Caching

```ini
[mypy]
# Enable incremental mode (default)
incremental = True
cache_dir = .mypy_cache

# Skip cache validation for faster runs (use with caution)
# skip_cache_mtime_checks = True
```

### Parallel Processing

```bash
# Use multiple processes for large codebases
mypy --processes 4 src/
```

### Exclude Patterns

```ini
[mypy]
# Exclude generated files, migrations, etc.
exclude = (?x)(
    migrations/
    | __pycache__/
    | \.git/
    | build/
    | dist/
    | \.venv/
)
```

## Error Suppression Strategies

### Inline Suppressions

```python
# Suppress specific error types
result = some_untyped_function()  # type: ignore[no-untyped-call]

# Suppress all errors (use sparingly)
problematic_line = legacy_code()  # type: ignore

# Suppress with explanation
data = json.loads(response)  # type: ignore[no-untyped-call]  # json.loads typing issue
```

### File-level Suppressions

```python
# mypy: disable-error-code="no-untyped-def,no-untyped-call"

# For entire file (use very sparingly)
# mypy: ignore-errors
```

## Testing with MyPy

### Type Testing

```python
# test_types.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only evaluated during type checking
    from mypy_extensions import TypedDict
    
    class UserDict(TypedDict):
        name: str
        age: int

def test_user_creation() -> None:
    user: UserDict = {"name": "Alice", "age": 30}
    assert user["name"] == "Alice"
```

### Assert Type

```python
from typing import assert_type

def get_user_name(user_id: int) -> str:
    # Implementation
    return "Alice"

# Verify return type in tests
result = get_user_name(123)
assert_type(result, str)  # Passes type checking
```

## Common Pitfalls and Solutions

### 1. Mutable Default Arguments

```python
# Problematic
def add_item(items: List[str] = []) -> List[str]:  # mypy warning
    items.append("new_item")
    return items

# Solution
def add_item(items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append("new_item")
    return items
```

### 2. Covariance and Contravariance

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item

# This might seem correct but can cause issues
def process_containers(containers: List[Container[object]]) -> None:
    pass

# Better approach with bounds
AnyContainer = TypeVar('AnyContainer', bound=Container[object])

def process_containers(containers: List[AnyContainer]) -> None:
    pass
```

### 3. Circular Imports

```python
# Use TYPE_CHECKING for type-only imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User

def process_user(user: 'User') -> str:  # Forward reference
    return user.name
```

## Monitoring and Maintenance

### Coverage Reports

```bash
# Generate HTML coverage report
mypy --html-report mypy-report/ src/

# Text coverage summary
mypy --txt-report mypy-report/ src/
```

### CI/CD Integration

```yaml
# .github/workflows/type-check.yml
name: Type Check
on: [push, pull_request]
jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install mypy types-requests
      - name: Run MyPy
        run: mypy --strict src/
```

This guide provides comprehensive configuration options and best practices for integrating mypy effectively into your Python development workflow.
