"""
Pydantic Practical Examples: Real-World Patterns

This file demonstrates practical Pydantic usage patterns that showcase
the library's strengths compared to dataclasses and attrs.
"""

from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict, Union, Literal
from decimal import Decimal
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    computed_field,
    ConfigDict,
)
import json


# Example 1: API Data Validation (Common Web Development Scenario)
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """
    Demonstrates: Field validation, enums, computed fields
    Real-world use: User registration/profile APIs
    """

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    id: int = Field(..., gt=0, description="User ID must be positive")
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    email: str = Field(..., description="User email address")
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Union[str, int]] = Field(default_factory=dict)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Custom email validation with transformation"""
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @computed_field
    @property
    def display_name(self) -> str:
        """Computed field demonstrating derived properties"""
        return f"{self.username} ({self.role.value})"

    @model_validator(mode="after")
    def validate_admin_user(self):
        """Cross-field validation example"""
        if self.role == UserRole.ADMIN and not self.username.startswith("admin_"):
            raise ValueError('Admin users must have username starting with "admin_"')
        return self


# Example 2: Configuration Management (DevOps/Settings Pattern)
class DatabaseConfig(BaseModel):
    """
    Demonstrates: Environment variable parsing, validation
    Real-world use: Application configuration from environment
    """

    model_config = ConfigDict(env_prefix="DB_", case_sensitive=False)

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535)
    username: str = Field(..., min_length=1)
    password: str = Field(
        ..., min_length=8, repr=False
    )  # repr=False hides in string representation
    database: str = Field(..., min_length=1)
    pool_size: int = Field(default=10, ge=1, le=100)
    ssl_mode: Literal["disable", "require", "verify-ca", "verify-full"] = "disable"

    @computed_field
    @property
    def connection_url(self) -> str:
        """Generate connection URL from components"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


# Example 3: E-commerce/Financial Data (Precision & Validation)
class Money(BaseModel):
    """
    Demonstrates: Decimal handling, custom validation
    Real-world use: E-commerce, financial applications
    """

    amount: Decimal = Field(..., decimal_places=2, ge=0)
    currency: str = Field(..., min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        valid_currencies = {"USD", "EUR", "GBP", "JPY", "CAD"}
        if v not in valid_currencies:
            raise ValueError(f"Currency must be one of {valid_currencies}")
        return v

    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"


class Product(BaseModel):
    """
    Demonstrates: Complex nested validation, business logic
    Real-world use: Product catalog, inventory management
    """

    id: str = Field(..., pattern=r"^PROD-\d{6}$")
    name: str = Field(..., min_length=1, max_length=200)
    price: Money
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    in_stock: bool = True
    tags: List[str] = Field(default_factory=list, max_length=10)

    @computed_field
    @property
    def final_price(self) -> Money:
        """Calculate price after discount"""
        if self.discount_percentage:
            discounted_amount = self.price.amount * (1 - self.discount_percentage / 100)
            return Money(amount=discounted_amount, currency=self.price.currency)
        return self.price

    @model_validator(mode="after")
    def validate_discount_logic(self):
        """Business rule validation"""
        if (
            self.discount_percentage
            and self.discount_percentage > 0
            and not self.in_stock
        ):
            raise ValueError("Cannot apply discount to out-of-stock items")
        return self


# Example 4: Data Transformation Pipeline (ETL/Data Processing)
class RawEventData(BaseModel):
    """
    Demonstrates: Flexible input handling, data transformation
    Real-world use: Log processing, analytics pipelines
    """

    model_config = ConfigDict(extra="allow")  # Allow extra fields

    timestamp: Union[datetime, str, int]  # Multiple input formats
    event_type: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    properties: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def parse_timestamp(cls, v):
        """Handle multiple timestamp formats"""
        if isinstance(v, datetime):
            return v
        elif isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("Invalid timestamp format")
        elif isinstance(v, (int, float)):
            return datetime.fromtimestamp(v)
        else:
            raise ValueError("Timestamp must be datetime, string, or number")

    @field_validator("event_type")
    @classmethod
    def normalize_event_type(cls, v: str) -> str:
        """Normalize event type format"""
        return v.lower().replace(" ", "_").replace("-", "_")


class ProcessedEvent(BaseModel):
    """
    Demonstrates: Data transformation, computed analytics
    Real-world use: Processed analytics data
    """

    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now().timestamp()}")
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    processed_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_raw_event(cls, raw: RawEventData) -> "ProcessedEvent":
        """Factory method for data transformation"""
        return cls(
            timestamp=raw.timestamp,
            event_type=raw.event_type,
            user_id=raw.user_id,
            session_id=raw.session_id,
        )


# Example 5: API Response Models (Serialization Patterns)
class APIResponse(BaseModel):
    """
    Demonstrates: Serialization aliases, response formatting
    Real-world use: API response standardization
    """

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both alias and field name
        alias_generator=lambda field_name: "".join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(field_name.split("_"))
        ),  # snake_case to camelCase
    )

    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[Dict] = None
    error_code: Optional[str] = Field(None, alias="errorCode")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: str = Field(..., alias="requestId")


# Demonstration Function
def demonstrate_pydantic_usage():
    """
    Demonstrates practical usage patterns and error handling
    """
    print("=== Pydantic Practical Examples ===\n")

    # Example 1: User validation with automatic coercion
    print("1. User Validation with Type Coercion:")
    try:
        # Notice: id is passed as string but converted to int
        user_data = {
            "id": "123",  # String converted to int
            "username": "  john_doe  ",  # Whitespace stripped
            "email": "JOHN@EXAMPLE.COM",  # Converted to lowercase
            "role": "admin",
        }
        user = User(**user_data)
        print(f"Created user: {user.display_name}")
        print(f"Email (normalized): {user.email}")
        print(f"User ID type: {type(user.id)}")
    except Exception as e:
        print(f"Validation error: {e}")

    print("\n" + "=" * 50 + "\n")

    # Example 2: Configuration from environment-like data
    print("2. Configuration Management:")
    config_data = {
        "host": "production-db.example.com",
        "port": "5432",  # String converted to int
        "username": "app_user",
        "password": "secure_password_123",
        "database": "production_db",
    }
    db_config = DatabaseConfig(**config_data)
    print(f"Database URL: {db_config.connection_url}")

    print("\n" + "=" * 50 + "\n")

    # Example 3: E-commerce with business logic
    print("3. E-commerce Product with Business Logic:")
    product_data = {
        "id": "PROD-123456",
        "name": "Premium Widget",
        "price": {"amount": "99.99", "currency": "USD"},  # Nested validation
        "discount_percentage": 15.0,
        "tags": ["premium", "widget", "bestseller"],
    }
    product = Product(**product_data)
    print(f"Product: {product.name}")
    print(f"Original price: {product.price}")
    print(f"Final price: {product.final_price}")

    print("\n" + "=" * 50 + "\n")

    # Example 4: Data transformation pipeline
    print("4. Data Transformation Pipeline:")
    raw_data = {
        "timestamp": "2024-01-15T10:30:00Z",
        "event_type": "User Login",
        "user_id": "user_123",
        "extra_field": "This will be preserved",  # Extra field allowed
    }
    raw_event = RawEventData(**raw_data)
    processed_event = ProcessedEvent.from_raw_event(raw_event)
    print(f"Raw event type: {raw_data['event_type']}")
    print(f"Processed event type: {processed_event.event_type}")
    print(f"Processing time: {processed_event.processed_at}")

    print("\n" + "=" * 50 + "\n")

    # Example 5: API response serialization
    print("5. API Response Serialization:")
    response = APIResponse(
        data={"user_count": 1500, "active_sessions": 45}, request_id="req_12345"
    )
    print("JSON serialization with aliases:")
    print(json.dumps(response.model_dump(by_alias=True), indent=2, default=str))


if __name__ == "__main__":
    demonstrate_pydantic_usage()
