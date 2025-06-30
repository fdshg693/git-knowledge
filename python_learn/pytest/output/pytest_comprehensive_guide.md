# pytest: Comprehensive Guide for Mid-Level Python Developers

## Introduction

pytest is Python's most popular testing framework, known for its simplicity, powerful features, and extensive plugin ecosystem. Unlike unittest (Python's standard library testing framework), pytest offers a more pythonic approach to writing tests with minimal boilerplate code.

## Why pytest?

### Advantages over unittest
- **Simpler syntax**: No need for classes or special assertion methods
- **Better failure reporting**: Clear, detailed error messages
- **Powerful fixtures**: Flexible test setup and teardown
- **Parametrized testing**: Easy test data variation
- **Rich plugin ecosystem**: Extensive third-party extensions
- **Discovery**: Automatic test discovery without configuration

## Core Concepts

### 1. Basic Test Structure

pytest tests are simple functions that start with `test_` or end with `_test`. No classes required:

```python
def test_addition():
    assert 2 + 2 == 4

def test_string_operations():
    name = "pytest"
    assert name.upper() == "PYTEST"
    assert len(name) == 6
```

### 2. Assertions

pytest uses Python's built-in `assert` statement with intelligent introspection:

```python
def test_assertions():
    # Simple assertions
    assert 1 == 1
    assert "hello" in "hello world"
    assert [1, 2, 3] == [1, 2, 3]
    
    # pytest provides detailed failure information
    expected = {"name": "John", "age": 30}
    actual = {"name": "Jane", "age": 25}
    # This will show exactly what differs
    assert expected == actual  # Will fail with clear diff
```

### 3. Test Discovery

pytest automatically discovers tests based on naming conventions:
- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*()`
- Test classes: `Test*` (with `test_*` methods)
- Test methods: `test_*()`

## Fixtures: The Heart of pytest

Fixtures provide a way to set up test data, configure test environment, and share common functionality across tests.

### Basic Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Provides sample data for tests"""
    return {"users": ["alice", "bob"], "count": 2}

def test_user_count(sample_data):
    assert sample_data["count"] == len(sample_data["users"])
```

### Fixture Scopes

Fixtures can have different scopes controlling when they're created and destroyed:

- `function` (default): Created for each test function
- `class`: Created once per test class
- `module`: Created once per test module
- `package`: Created once per test package
- `session`: Created once per test session

```python
@pytest.fixture(scope="module")
def database_connection():
    """Expensive setup - only once per module"""
    connection = create_database_connection()
    yield connection
    connection.close()
```

### Built-in Fixtures

pytest provides many useful built-in fixtures:

- `tmp_path`: Temporary directory for file operations
- `capsys`: Capture stdout/stderr
- `monkeypatch`: Mock and patch objects
- `request`: Information about the requesting test

## Parametrized Testing

Test the same logic with different inputs using `@pytest.mark.parametrize`:

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
    (-2, 4),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

## Markers and Test Organization

Markers allow you to categorize and selectively run tests:

```python
import pytest

@pytest.mark.slow
def test_heavy_computation():
    # Time-consuming test
    pass

@pytest.mark.integration
def test_api_endpoint():
    # Integration test
    pass

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8+")
def test_modern_feature():
    pass
```

Run specific markers:
```bash
pytest -m slow          # Run only slow tests
pytest -m "not slow"    # Skip slow tests
pytest -m "slow or integration"  # Run slow OR integration tests
```

## Exception Testing

Test that code raises expected exceptions:

```python
def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        1 / 0

def test_value_error_message():
    with pytest.raises(ValueError, match="invalid literal"):
        int("not_a_number")
```

## Configuration and pytest.ini

Control pytest behavior with configuration files:

```ini
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = -ra -q --strict-markers
testpaths = tests
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

## Best Practices for Mid-Level Developers

### 1. Organize Tests Logically
```
tests/
├── unit/
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   └── test_api.py
└── conftest.py  # Shared fixtures
```

### 2. Use Descriptive Test Names
```python
# Good
def test_user_registration_with_valid_data_creates_user():
    pass

def test_user_registration_with_duplicate_email_raises_error():
    pass

# Avoid
def test_user():
    pass
```

### 3. Follow AAA Pattern
```python
def test_bank_account_withdrawal():
    # Arrange
    account = BankAccount(balance=100)
    
    # Act
    account.withdraw(30)
    
    # Assert
    assert account.balance == 70
```

### 4. Use Fixtures for Complex Setup
```python
@pytest.fixture
def authenticated_client():
    client = TestClient()
    client.login("test@example.com", "password")
    return client

def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/dashboard")
    assert response.status_code == 200
```

## Common Testing Patterns

### Testing Classes
```python
class TestCalculator:
    def test_addition(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5
    
    def test_division_by_zero(self):
        calc = Calculator()
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)
```

### Testing with Mock Objects
```python
from unittest.mock import Mock, patch

def test_api_call_with_mock():
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"status": "success"}
        
        result = fetch_user_data(user_id=123)
        
        assert result["status"] == "success"
        mock_get.assert_called_once_with("/api/users/123")
```

## Common Pitfalls and Solutions

### 1. Fixture Dependencies
```python
# Fixtures can depend on other fixtures
@pytest.fixture
def database():
    return create_test_database()

@pytest.fixture
def user(database):
    return database.create_user("test@example.com")

def test_user_creation(user):
    assert user.email == "test@example.com"
```

### 2. Proper Cleanup
```python
@pytest.fixture
def temporary_file():
    file_path = create_temp_file()
    yield file_path
    # Cleanup happens after yield
    os.remove(file_path)
```

### 3. Avoiding Test Interdependence
```python
# Bad - tests depend on each other
def test_create_user():
    global created_user
    created_user = User.create("test@example.com")

def test_user_exists():
    assert created_user.exists()  # Depends on previous test

# Good - each test is independent
@pytest.fixture
def user():
    return User.create("test@example.com")

def test_user_creation(user):
    assert user.email == "test@example.com"

def test_user_exists(user):
    assert user.exists()
```

## Performance Testing with pytest

```python
import time
import pytest

def test_function_performance():
    start_time = time.time()
    
    # Your code here
    result = expensive_function()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    assert execution_time < 1.0  # Should complete within 1 second
    assert result is not None
```

## Integration with CI/CD

pytest integrates well with continuous integration:

```bash
# Generate test reports
pytest --junitxml=report.xml
pytest --html=report.html --self-contained-html

# Coverage reporting
pytest --cov=myproject --cov-report=html
```

## Conclusion

pytest's power lies in its simplicity and extensibility. For mid-level Python developers, mastering pytest means:

1. **Understanding fixtures** for clean test setup
2. **Using parametrization** for comprehensive test coverage
3. **Organizing tests** with proper structure and markers
4. **Writing maintainable tests** following best practices
5. **Leveraging the plugin ecosystem** for specialized needs

The key is to start simple and gradually adopt more advanced features as your testing needs grow. pytest's excellent documentation and active community make it an excellent choice for any Python project.
