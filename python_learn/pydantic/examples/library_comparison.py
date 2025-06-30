"""
Pydantic vs. Dataclasses vs. Attrs: Side-by-Side Comparison

This file demonstrates the same functionality implemented using
Pydantic, dataclasses, and attrs to highlight their differences.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json
import attrs
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# Scenario 1: Simple Data Container
# ============================================================================


# Pydantic Implementation
class PydanticPerson(BaseModel):
    name: str
    age: int
    email: Optional[str] = None

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v < 0:
            raise ValueError("Age must be non-negative")
        return v


# Dataclass Implementation
@dataclass
class DataclassPerson:
    name: str
    age: int
    email: Optional[str] = None

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age must be non-negative")


# Attrs Implementation
@attrs.define
class AttrsPerson:
    name: str
    age: int = attrs.field(validator=attrs.validators.instance_of(int))
    email: Optional[str] = None

    @age.validator
    def _validate_age(self, attribute, value):
        if value < 0:
            raise ValueError("Age must be non-negative")


# ============================================================================
# Scenario 2: Complex Validation and Serialization
# ============================================================================


# Pydantic Implementation
class PydanticOrder(BaseModel):
    order_id: str = Field(..., pattern=r"^ORD-\d{6}$")
    customer_name: str = Field(..., min_length=1)
    items: List[str] = Field(default_factory=list)
    total_amount: float = Field(..., gt=0)
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("customer_name")
    @classmethod
    def validate_customer_name(cls, v):
        return v.strip().title()

    def to_json(self) -> str:
        return self.model_dump_json()

    @classmethod
    def from_json(cls, json_str: str):
        return cls.model_validate_json(json_str)


# Dataclass Implementation
@dataclass
class DataclassOrder:
    order_id: str
    customer_name: str
    total_amount: float
    items: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        import re

        if not re.match(r"^ORD-\d{6}$", self.order_id):
            raise ValueError("Invalid order ID format")
        if len(self.customer_name.strip()) == 0:
            raise ValueError("Customer name cannot be empty")
        if self.total_amount <= 0:
            raise ValueError("Total amount must be positive")

        # Transform data
        self.customer_name = self.customer_name.strip().title()

    def to_json(self) -> str:
        # Manual serialization required
        data = {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "total_amount": self.total_amount,
            "items": self.items,
            "created_at": self.created_at.isoformat(),
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str):
        # Manual deserialization required
        data = json.loads(json_str)
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


# Attrs Implementation
def validate_order_id(instance, attribute, value):
    import re

    if not re.match(r"^ORD-\d{6}$", value):
        raise ValueError("Invalid order ID format")


def validate_positive(instance, attribute, value):
    if value <= 0:
        raise ValueError(f"{attribute.name} must be positive")


def transform_customer_name(value):
    return value.strip().title()


@attrs.define
class AttrsOrder:
    order_id: str = attrs.field(validator=validate_order_id)
    customer_name: str = attrs.field(converter=transform_customer_name)
    total_amount: float = attrs.field(validator=validate_positive)
    items: List[str] = attrs.field(factory=list)
    created_at: datetime = attrs.field(factory=datetime.now)

    @customer_name.validator
    def _validate_customer_name(self, attribute, value):
        if len(value.strip()) == 0:
            raise ValueError("Customer name cannot be empty")

    def to_json(self) -> str:
        # Manual serialization using attrs.asdict
        data = attrs.asdict(self)
        data["created_at"] = data["created_at"].isoformat()
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


# ============================================================================
# Comparison Demonstration
# ============================================================================


def demonstrate_differences():
    """Demonstrate key differences between the three approaches"""

    print("=== Pydantic vs. Dataclasses vs. Attrs Comparison ===\n")

    # Test 1: Type Coercion
    print("1. Type Coercion Test:")
    print("   Input: name='John', age='25' (age as string)")

    try:
        # Pydantic: Automatic type coercion
        pydantic_person = PydanticPerson(name="John", age="25")  # age coerced to int
        print(
            f"   ✅ Pydantic: {pydantic_person.name}, age={pydantic_person.age} (type: {type(pydantic_person.age)})"
        )
    except Exception as e:
        print(f"   ❌ Pydantic failed: {e}")

    try:
        # Dataclass: No type coercion
        dataclass_person = DataclassPerson(name="John", age="25")  # This will fail
        print(f"   ✅ Dataclass: {dataclass_person.name}, age={dataclass_person.age}")
    except Exception as e:
        print(f"   ❌ Dataclass failed: {e}")

    try:
        # Attrs: Depends on configuration
        attrs_person = AttrsPerson(
            name="John", age="25"
        )  # This will fail due to validator
        print(f"   ✅ Attrs: {attrs_person.name}, age={attrs_person.age}")
    except Exception as e:
        print(f"   ❌ Attrs failed: {e}")

    print("\n" + "=" * 60 + "\n")

    # Test 2: Validation and Transformation
    print("2. Validation and Transformation Test:")
    order_data = {
        "order_id": "ORD-123456",
        "customer_name": "  alice smith  ",  # Needs trimming and title case
        "total_amount": 99.99,
        "items": ["item1", "item2"],
    }

    print(f"   Input: customer_name='{order_data['customer_name']}'")

    # Pydantic
    pydantic_order = PydanticOrder(**order_data)
    print(f"   Pydantic result: '{pydantic_order.customer_name}'")

    # Dataclass
    dataclass_order = DataclassOrder(**order_data)
    print(f"   Dataclass result: '{dataclass_order.customer_name}'")

    # Attrs
    attrs_order = AttrsOrder(**order_data)
    print(f"   Attrs result: '{attrs_order.customer_name}'")

    print("\n" + "=" * 60 + "\n")

    # Test 3: Serialization
    print("3. Serialization Test:")

    # Test JSON serialization
    pydantic_json = pydantic_order.to_json()
    dataclass_json = dataclass_order.to_json()
    attrs_json = attrs_order.to_json()

    print("   Pydantic JSON (first 100 chars):", pydantic_json[:100] + "...")
    print("   Dataclass JSON (first 100 chars):", dataclass_json[:100] + "...")
    print("   Attrs JSON (first 100 chars):", attrs_json[:100] + "...")

    print("\n" + "=" * 60 + "\n")

    # Test 4: Performance and Memory
    print("4. Feature Comparison Summary:")

    features = [
        ("Runtime Type Validation", "✅", "❌", "✅*"),
        ("Automatic Type Coercion", "✅", "❌", "❌"),
        ("Built-in Serialization", "✅", "❌", "✅*"),
        ("JSON Schema Generation", "✅", "❌", "❌"),
        ("Memory Efficiency", "⚠️", "✅", "✅"),
        ("Performance", "⚠️", "✅", "✅"),
        ("Learning Curve", "📚", "📖", "📚📚"),
        ("Ecosystem Support", "🌐", "🔧", "🔧"),
    ]

    print("   Feature                 | Pydantic | Dataclass | Attrs")
    print("   " + "-" * 55)
    for feature, pyd, dc, att in features:
        print(f"   {feature:<22} | {pyd:^8} | {dc:^9} | {att:^5}")

    print("\n   ✅ = Full support, ⚠️ = With caveats, ❌ = Not supported")
    print("   * = Requires additional configuration")

    print("\n" + "=" * 60 + "\n")

    # Test 5: Error Messages
    print("5. Error Message Quality:")

    invalid_data = {
        "order_id": "INVALID",
        "customer_name": "",
        "total_amount": -10,
        "items": ["item1"],
    }

    print("   Testing with invalid data:")
    print(f"   {invalid_data}")

    # Pydantic error
    try:
        PydanticOrder(**invalid_data)
    except Exception as e:
        print(f"\n   Pydantic error:\n   {str(e)[:200]}...")

    # Dataclass error
    try:
        DataclassOrder(**invalid_data)
    except Exception as e:
        print(f"\n   Dataclass error:\n   {str(e)[:200]}...")

    # Attrs error
    try:
        AttrsOrder(**invalid_data)
    except Exception as e:
        print(f"\n   Attrs error:\n   {str(e)[:200]}...")


# ============================================================================
# Use Case Recommendations
# ============================================================================


def print_recommendations():
    """Print recommendations for when to use each approach"""

    print("\n" + "=" * 60)
    print("WHEN TO USE EACH APPROACH")
    print("=" * 60)

    print("\n🟢 Use PYDANTIC when:")
    print("   • Building APIs (FastAPI, REST services)")
    print("   • Handling external data (JSON, forms, configs)")
    print("   • Need automatic validation and type coercion")
    print("   • Want built-in serialization/deserialization")
    print("   • Working with settings management")

    print("\n🔵 Use DATACLASSES when:")
    print("   • Simple data containers with minimal logic")
    print("   • Performance is critical")
    print("   • Memory usage is a concern")
    print("   • Working with pure Python (no dependencies)")
    print("   • Type hints are sufficient for your needs")

    print("\n🟡 Use ATTRS when:")
    print("   • Need more features than dataclasses")
    print("   • Want fine-grained control over behavior")
    print("   • Working with complex object hierarchies")
    print("   • Need advanced features (slots, frozen, etc.)")
    print("   • Don't need runtime type coercion")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Install required packages first:
    # pip install pydantic attrs

    demonstrate_differences()
    print_recommendations()
