# Pydantic: Deep Dive for Type-Aware Developers

## Overview

Pydantic is a Python library that provides data validation and settings management using Python type annotations. While you might be familiar with `dataclasses` and `attrs`, Pydantic goes beyond simple data containers by providing runtime validation, serialization, and powerful configuration management.

## Core Philosophy & Design Principles

### 1. Type Annotations as Single Source of Truth
Unlike `dataclasses` where type hints are mainly for static analysis, Pydantic uses them as the foundation for runtime validation:

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str | None = None
```

The type annotations here aren't just documentation—they're actively used at runtime to validate and coerce data.

### 2. Parse, Don't Validate
Pydantic follows the "parse, don't validate" philosophy. Instead of just checking if data is valid, it actively transforms input data into the expected types when possible:

```python
user = User(name="John", age="25")  # age="25" is coerced to int(25)
```

## Pydantic vs. Alternatives: Deep Comparison

### Pydantic vs. dataclasses

| Feature | Pydantic | dataclasses |
|---------|----------|-------------|
| **Runtime Validation** | ✅ Built-in | ❌ None |
| **Type Coercion** | ✅ Automatic | ❌ None |
| **Serialization** | ✅ JSON/dict built-in | ❌ Manual |
| **Performance** | ⚡ Fast (Rust core) | ⚡ Fastest (no validation) |
| **Memory Usage** | 📊 Higher | 📊 Lower |
| **Use Case** | Data validation, APIs | Simple data containers |

### Pydantic vs. attrs

| Feature | Pydantic | attrs |
|---------|----------|-------------|
| **Validation** | ✅ Type-based + custom | ✅ Custom validators |
| **Serialization** | ✅ Built-in JSON | ✅ Via converters |
| **Ecosystem** | 🌐 Web/API focused | 🔧 General purpose |
| **Learning Curve** | 📈 Moderate | 📈 Steep |

## Core Concepts

### 1. BaseModel: The Foundation

Every Pydantic model inherits from `BaseModel`, which provides:
- Automatic validation based on type hints
- Serialization methods (`.model_dump()`, `.model_dump_json()`)
- Parsing methods (`.model_validate()`, `.model_validate_json()`)

### 2. Field Validation Hierarchy

Pydantic validates fields in this order:
1. **Type validation** (based on type annotations)
2. **Field validators** (custom validation functions)
3. **Model validators** (cross-field validation)

### 3. Validation vs. Serialization

- **Validation**: Converting input data to Python objects
- **Serialization**: Converting Python objects back to serializable formats

### 4. Strict vs. Lax Mode

- **Lax mode** (default): Attempts type coercion (`"123"` → `123`)
- **Strict mode**: Requires exact types (`"123"` would raise ValidationError for int field)

## Advanced Concepts

### 1. Field Configuration

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Price in USD")
    tags: list[str] = Field(default_factory=list)
```

### 2. Custom Validators

```python
from pydantic import BaseModel, field_validator, model_validator

class User(BaseModel):
    name: str
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @model_validator(mode='after')
    def validate_user(self):
        # Cross-field validation
        if self.name.lower() in self.email.lower():
            raise ValueError('Name cannot be part of email')
        return self
```

### 3. Computed Fields

```python
from pydantic import BaseModel, computed_field

class Circle(BaseModel):
    radius: float
    
    @computed_field
    @property
    def area(self) -> float:
        return 3.14159 * self.radius ** 2
```

## When to Use Pydantic

### ✅ Perfect for:
- **API development** (FastAPI, Django REST)
- **Configuration management** (settings, environment variables)
- **Data validation** (user input, external APIs)
- **Data transformation** (JSON to Python objects)

### ❌ Consider alternatives for:
- **Pure data containers** (use `dataclasses`)
- **Performance-critical code** (use `dataclasses` or `attrs`)
- **Complex object relationships** (use ORMs like SQLAlchemy)

## Performance Considerations

### Memory Usage
Pydantic models have higher memory overhead due to validation metadata:
- `dataclass`: ~56 bytes per instance
- `Pydantic BaseModel`: ~120 bytes per instance

### Validation Cost
- First validation: ~2-3x slower than direct assignment
- Subsequent access: Same as regular attributes
- Parsing JSON: Often faster than `json.loads()` + manual validation

## Best Practices

### 1. Use Type Unions Wisely
```python
# Good: Clear intent
status: Literal['active', 'inactive', 'pending']

# Avoid: Too permissive
data: str | int | float | None
```

### 2. Leverage Field Aliases
```python
class APIResponse(BaseModel):
    user_id: int = Field(alias='userId')
    created_at: datetime = Field(alias='createdAt')
```

### 3. Use Config for Model Behavior
```python
class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
```

## Common Pitfalls

### 1. Mutable Default Values
```python
# Wrong
class User(BaseModel):
    tags: list[str] = []  # Shared across instances!

# Correct
class User(BaseModel):
    tags: list[str] = Field(default_factory=list)
```

### 2. Validation Performance
```python
# Inefficient: Validates on every assignment
user.name = "John"
user.email = "john@example.com"

# Efficient: Validate once
user = User.model_validate({"name": "John", "email": "john@example.com"})
```

## Conclusion

Pydantic bridges the gap between Python's type system and runtime validation. While `dataclasses` and `attrs` excel at creating data containers, Pydantic excels at ensuring data integrity and providing seamless serialization. Understanding when and how to use each tool is crucial for writing maintainable, robust Python applications.

For developers already comfortable with type hints and mypy, Pydantic feels natural while providing powerful runtime guarantees that static analysis alone cannot provide.
