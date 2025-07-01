"""
MyPy Practical Examples: E-commerce Order Processing System

This module demonstrates various mypy features through a realistic e-commerce
order processing system. It showcases type hints, generics, protocols, and
common patterns that mid-level Python developers encounter.
"""

from typing import (
    Dict,
    List,
    Optional,
    Union,
    Protocol,
    TypeVar,
    Generic,
    Literal,
    TypedDict,
    Callable,
    Any,
    cast,
)
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
from datetime import datetime
import json


# =============================================================================
# Domain Models with Type Hints
# =============================================================================


class OrderStatus(Enum):
    """Order status enumeration with type safety."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Product:
    """Product model with comprehensive type annotations."""

    id: int
    name: str
    price: Decimal
    category: str
    in_stock: bool
    tags: List[str]
    metadata: Dict[str, Union[str, int, bool]]

    def __post_init__(self) -> None:
        """Validate product data after initialization."""
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if not self.name.strip():
            raise ValueError("Product name is required")


@dataclass
class Customer:
    """Customer model demonstrating Optional types."""

    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None  # Optional field
    address: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Computed property with return type annotation."""
        return f"{self.first_name} {self.last_name}"


# TypedDict for structured dictionaries
class OrderData(TypedDict):
    """Typed dictionary for order data from external sources."""

    customer_id: int
    products: List[Dict[str, Union[int, str]]]
    total_amount: float
    order_date: str
    status: str


# =============================================================================
# Generic Classes and Type Variables
# =============================================================================

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class Repository(Generic[T]):
    """Generic repository pattern with type safety."""

    def __init__(self) -> None:
        self._items: Dict[int, T] = {}
        self._next_id: int = 1

    def save(self, item: T) -> int:
        """Save an item and return its ID."""
        item_id = self._next_id
        self._items[item_id] = item
        self._next_id += 1
        return item_id

    def get_by_id(self, item_id: int) -> Optional[T]:
        """Retrieve item by ID, returns None if not found."""
        return self._items.get(item_id)

    def get_all(self) -> List[T]:
        """Get all items as a list."""
        return list(self._items.values())

    def delete(self, item_id: int) -> bool:
        """Delete item by ID, returns True if deleted."""
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


# =============================================================================
# Protocols for Structural Typing
# =============================================================================


class Serializable(Protocol):
    """Protocol for objects that can be serialized."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert object to dictionary representation."""
        ...


class Cacheable(Protocol):
    """Protocol for objects that can be cached."""

    def cache_key(self) -> str:
        """Return unique cache key for the object."""
        ...


class Discountable(Protocol):
    """Protocol for items that can have discounts applied."""

    def apply_discount(self, percentage: float) -> None:
        """Apply discount percentage to the item."""
        ...


# =============================================================================
# Advanced Type Patterns
# =============================================================================

# Union types for flexible APIs
CustomerIdentifier = Union[int, str]  # ID or email
PaymentMethod = Literal["credit_card", "paypal", "bank_transfer"]

# Function type annotations
PriceCalculator = Callable[[Decimal, int], Decimal]
OrderProcessor = Callable[[OrderData], bool]


class Order:
    """Order class demonstrating complex type relationships."""

    def __init__(
        self,
        customer: Customer,
        products: List[Product],
        payment_method: PaymentMethod,
        discount_percentage: float = 0.0,
    ) -> None:
        self.id: Optional[int] = None
        self.customer = customer
        self.products = products
        self.payment_method = payment_method
        self.discount_percentage = discount_percentage
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.total_amount = self._calculate_total()

    def _calculate_total(self) -> Decimal:
        """Calculate order total with discount applied."""
        subtotal = sum(product.price for product in self.products)
        discount_amount = subtotal * Decimal(str(self.discount_percentage))
        return subtotal - discount_amount

    def add_product(self, product: Product) -> None:
        """Add product to order and recalculate total."""
        self.products.append(product)
        self.total_amount = self._calculate_total()

    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status with validation."""
        if not isinstance(new_status, OrderStatus):
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status


# =============================================================================
# Service Classes with Type Safety
# =============================================================================


class OrderService:
    """Service class demonstrating practical mypy usage patterns."""

    def __init__(
        self,
        product_repo: Repository[Product],
        customer_repo: Repository[Customer],
        order_repo: Repository[Order],
    ) -> None:
        self.product_repo = product_repo
        self.customer_repo = customer_repo
        self.order_repo = order_repo

    def create_order(
        self,
        customer_id: int,
        product_ids: List[int],
        payment_method: PaymentMethod,
        discount_percentage: float = 0.0,
    ) -> Optional[Order]:
        """Create new order with type validation."""
        # Get customer
        customer = self.customer_repo.get_by_id(customer_id)
        if customer is None:
            return None

        # Get products
        products: List[Product] = []
        for product_id in product_ids:
            product = self.product_repo.get_by_id(product_id)
            if product is None or not product.in_stock:
                return None
            products.append(product)

        # Create and save order
        order = Order(customer, products, payment_method, discount_percentage)
        order_id = self.order_repo.save(order)
        order.id = order_id

        return order

    def process_order_from_data(self, order_data: OrderData) -> Optional[Order]:
        """Process order from external data source."""
        try:
            # Type-safe data extraction
            customer_id: int = order_data["customer_id"]
            product_data: List[Dict[str, Union[int, str]]] = order_data["products"]

            # Extract product IDs with type casting
            product_ids: List[int] = []
            for item in product_data:
                product_id = cast(int, item["product_id"])  # Safe cast
                product_ids.append(product_id)

            # Validate payment method
            payment_method_str = order_data["status"]
            if payment_method_str not in ["credit_card", "paypal", "bank_transfer"]:
                return None
            payment_method = cast(PaymentMethod, payment_method_str)

            return self.create_order(customer_id, product_ids, payment_method)

        except (KeyError, TypeError, ValueError):
            return None

    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get orders filtered by status."""
        all_orders = self.order_repo.get_all()
        return [order for order in all_orders if order.status == status]

    def calculate_customer_total(self, customer_id: int) -> Decimal:
        """Calculate total amount for all customer orders."""
        customer_orders = [
            order
            for order in self.order_repo.get_all()
            if order.customer.id == customer_id
        ]
        return sum(order.total_amount for order in customer_orders)


# =============================================================================
# Utility Functions with Advanced Types
# =============================================================================


def find_item_by_predicate(
    items: List[T], predicate: Callable[[T], bool]
) -> Optional[T]:
    """Generic function to find item by predicate."""
    for item in items:
        if predicate(item):
            return item
    return None


def group_by_key(items: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
    """Group items by key function result."""
    groups: Dict[K, List[T]] = {}
    for item in items:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups


def safe_json_load(data: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON with proper error handling."""
    try:
        result = json.loads(data)
        if isinstance(result, dict):
            return result
        return None
    except (json.JSONDecodeError, TypeError):
        return None


# =============================================================================
# Example Usage and Testing
# =============================================================================


def demo_usage() -> None:
    """Demonstrate the type-safe order processing system."""
    # Initialize repositories
    product_repo: Repository[Product] = Repository()
    customer_repo: Repository[Customer] = Repository()
    order_repo: Repository[Order] = Repository()

    # Create sample data
    product = Product(
        id=1,
        name="Python Programming Book",
        price=Decimal("39.99"),
        category="Books",
        in_stock=True,
        tags=["programming", "python", "education"],
        metadata={"pages": 500, "author": "Jane Doe", "digital": True},
    )

    customer = Customer(
        id=1,
        email="alice@example.com",
        first_name="Alice",
        last_name="Smith",
        phone="+1-555-0123",
    )

    # Save to repositories
    product_id = product_repo.save(product)
    customer_id = customer_repo.save(customer)

    # Create order service
    order_service = OrderService(product_repo, customer_repo, order_repo)

    # Create order with type safety
    order = order_service.create_order(
        customer_id=customer_id,
        product_ids=[product_id],
        payment_method="credit_card",  # Type-checked literal
        discount_percentage=0.1,
    )

    if order:
        print(f"Order created: {order.id}")
        print(f"Customer: {order.customer.full_name}")
        print(f"Total: ${order.total_amount}")
        print(f"Status: {order.status.value}")

    # Demonstrate generic functions
    all_orders = order_repo.get_all()
    pending_order = find_item_by_predicate(
        all_orders, lambda o: o.status == OrderStatus.PENDING
    )

    if pending_order:
        print(f"Found pending order: {pending_order.id}")

    # Group orders by status
    orders_by_status = group_by_key(all_orders, lambda o: o.status)
    for status, orders in orders_by_status.items():
        print(f"{status.value}: {len(orders)} orders")


if __name__ == "__main__":
    demo_usage()
