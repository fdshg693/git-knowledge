"""
Advanced pytest Integration Examples
===================================

This file demonstrates advanced pytest patterns and integration techniques
for mid-level Python developers working on complex projects.
"""

import pytest
import asyncio
import sqlite3
import threading
import time
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
from typing import List, Dict, Any, AsyncGenerator
from unittest.mock import Mock, patch, AsyncMock


# =============================================================================
# 1. Advanced Fixture Patterns and Dependency Injection
# =============================================================================


@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True


class UserService:
    """Service layer for user operations"""

    def __init__(self, repository, email_service, cache_service):
        self.repository = repository
        self.email_service = email_service
        self.cache_service = cache_service

    def create_user(self, name: str, email: str) -> User:
        """Create a new user with email notification"""
        user = self.repository.create(name, email)
        self.email_service.send_welcome_email(user)
        self.cache_service.invalidate_user_cache()
        return user

    def get_user(self, user_id: int) -> User:
        """Get user with caching"""
        cached_user = self.cache_service.get_user(user_id)
        if cached_user:
            return cached_user

        user = self.repository.get_by_id(user_id)
        if user:
            self.cache_service.set_user(user)
        return user


# Fixture hierarchy with dependency injection
@pytest.fixture
def mock_repository():
    """Mock repository with common behaviors"""
    repo = Mock()
    repo.create.return_value = User(1, "Test User", "test@example.com")
    repo.get_by_id.return_value = User(1, "Test User", "test@example.com")
    return repo


@pytest.fixture
def mock_email_service():
    """Mock email service"""
    service = Mock()
    service.send_welcome_email.return_value = True
    return service


@pytest.fixture
def mock_cache_service():
    """Mock cache service"""
    service = Mock()
    service.get_user.return_value = None  # Cache miss by default
    service.set_user.return_value = True
    service.invalidate_user_cache.return_value = True
    return service


@pytest.fixture
def user_service(mock_repository, mock_email_service, mock_cache_service):
    """Complete user service with all dependencies"""
    return UserService(mock_repository, mock_email_service, mock_cache_service)


class TestUserServiceIntegration:
    """Test suite demonstrating advanced fixture usage"""

    def test_create_user_flow(
        self, user_service, mock_repository, mock_email_service, mock_cache_service
    ):
        """Test complete user creation flow"""
        result = user_service.create_user("John Doe", "john@example.com")

        # Verify all service interactions
        mock_repository.create.assert_called_once_with("John Doe", "john@example.com")
        mock_email_service.send_welcome_email.assert_called_once()
        mock_cache_service.invalidate_user_cache.assert_called_once()

        assert result.name == "Test User"
        assert result.email == "test@example.com"

    def test_get_user_cache_hit(
        self, user_service, mock_cache_service, mock_repository
    ):
        """Test user retrieval with cache hit"""
        cached_user = User(1, "Cached User", "cached@example.com")
        mock_cache_service.get_user.return_value = cached_user

        result = user_service.get_user(1)

        # Should not hit repository when cache has data
        mock_repository.get_by_id.assert_not_called()
        mock_cache_service.set_user.assert_not_called()
        assert result == cached_user

    def test_get_user_cache_miss(
        self, user_service, mock_cache_service, mock_repository
    ):
        """Test user retrieval with cache miss"""
        mock_cache_service.get_user.return_value = None  # Cache miss

        result = user_service.get_user(1)

        # Should hit repository and update cache
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_cache_service.set_user.assert_called_once()
        assert result.name == "Test User"


# =============================================================================
# 2. Testing Async Code with pytest-asyncio
# =============================================================================


class AsyncAPIClient:
    """Example async API client"""

    def __init__(self, session):
        self.session = session

    async def fetch_user(self, user_id: int) -> Dict[str, Any]:
        """Fetch user data asynchronously"""
        async with self.session.get(f"/users/{user_id}") as response:
            return await response.json()

    async def bulk_fetch_users(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch multiple users concurrently"""
        tasks = [self.fetch_user(user_id) for user_id in user_ids]
        return await asyncio.gather(*tasks)


@pytest.fixture
async def mock_async_session():
    """Mock async HTTP session"""
    session = AsyncMock()

    # Mock context manager behavior
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "name": "Test User"}

    # Mock async context manager
    session.get.return_value.__aenter__.return_value = mock_response
    session.get.return_value.__aexit__.return_value = None

    return session


@pytest.fixture
async def async_api_client(mock_async_session):
    """Async API client for testing"""
    return AsyncAPIClient(mock_async_session)


class TestAsyncOperations:
    """Test suite for async code"""

    @pytest.mark.asyncio
    async def test_fetch_single_user(self, async_api_client, mock_async_session):
        """Test fetching a single user"""
        result = await async_api_client.fetch_user(1)

        assert result == {"id": 1, "name": "Test User"}
        mock_async_session.get.assert_called_once_with("/users/1")

    @pytest.mark.asyncio
    async def test_bulk_fetch_users(self, async_api_client):
        """Test concurrent user fetching"""
        user_ids = [1, 2, 3]
        results = await async_api_client.bulk_fetch_users(user_ids)

        assert len(results) == 3
        # Each result should be the same due to our mock
        for result in results:
            assert result == {"id": 1, "name": "Test User"}


# =============================================================================
# 3. Database Integration Testing with Real Database
# =============================================================================


class DatabaseManager:
    """Database manager for testing"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Connect to database"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def setup_schema(self):
        """Create database schema"""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        self.connection.commit()

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


class UserRepository:
    """User repository with real database operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create(self, name: str, email: str) -> User:
        """Create user in database"""
        cursor = self.db.connection.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        self.db.connection.commit()

        user_id = cursor.lastrowid
        return User(user_id, name, email)

    def get_by_id(self, user_id: int) -> User:
        """Get user by ID"""
        cursor = self.db.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            return User(row["id"], row["name"], row["email"])
        return None


@pytest.fixture(scope="function")
def test_database(tmp_path):
    """Create isolated test database for each test"""
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(str(db_path))
    db_manager.connect()
    db_manager.setup_schema()

    yield db_manager

    db_manager.close()


@pytest.fixture
def user_repository(test_database):
    """User repository with test database"""
    return UserRepository(test_database)


class TestDatabaseIntegration:
    """Integration tests with real database"""

    def test_create_and_retrieve_user(self, user_repository):
        """Test creating and retrieving user from database"""
        # Create user
        user = user_repository.create("John Doe", "john@example.com")
        assert user.id is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

        # Retrieve user
        retrieved_user = user_repository.get_by_id(user.id)
        assert retrieved_user.id == user.id
        assert retrieved_user.name == user.name
        assert retrieved_user.email == user.email

    def test_get_nonexistent_user(self, user_repository):
        """Test retrieving non-existent user"""
        result = user_repository.get_by_id(999)
        assert result is None


# =============================================================================
# 4. Multi-threading and Concurrency Testing
# =============================================================================


class ThreadSafeCounter:
    """Thread-safe counter implementation"""

    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        """Thread-safe increment"""
        with self._lock:
            self._value += 1

    def get_value(self):
        """Get current value"""
        with self._lock:
            return self._value


def worker_function(counter, iterations):
    """Worker function for threading tests"""
    for _ in range(iterations):
        counter.increment()


class TestConcurrency:
    """Test suite for concurrent operations"""

    def test_thread_safe_counter(self):
        """Test thread-safe counter with multiple threads"""
        counter = ThreadSafeCounter()
        threads = []
        iterations_per_thread = 100
        num_threads = 5

        # Create and start threads
        for _ in range(num_threads):
            thread = threading.Thread(
                target=worker_function, args=(counter, iterations_per_thread)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final count
        expected_count = num_threads * iterations_per_thread
        assert counter.get_value() == expected_count

    def test_counter_performance(self):
        """Test counter performance under load"""
        counter = ThreadSafeCounter()
        start_time = time.time()

        # Perform many increments
        for _ in range(10000):
            counter.increment()

        end_time = time.time()
        execution_time = end_time - start_time

        assert counter.get_value() == 10000
        assert execution_time < 1.0  # Should complete within 1 second


# =============================================================================
# 5. Custom Pytest Plugins and Hooks
# =============================================================================


class TestMetrics:
    """Custom test metrics collector"""

    def __init__(self):
        self.test_results = {}
        self.slow_tests = []

    def record_test(self, test_name, duration, outcome):
        """Record test execution details"""
        self.test_results[test_name] = {"duration": duration, "outcome": outcome}

        if duration > 0.5:  # Consider tests > 0.5s as slow
            self.slow_tests.append((test_name, duration))

    def get_summary(self):
        """Get test execution summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(
            1 for r in self.test_results.values() if r["outcome"] == "passed"
        )
        avg_duration = (
            sum(r["duration"] for r in self.test_results.values()) / total_tests
            if total_tests > 0
            else 0
        )

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "average_duration": avg_duration,
            "slow_tests": self.slow_tests,
        }


# Global test metrics instance
test_metrics = TestMetrics()


@pytest.fixture(autouse=True)
def record_test_metrics(request):
    """Automatically record metrics for all tests"""
    start_time = time.time()

    yield

    end_time = time.time()
    duration = end_time - start_time

    # Record test metrics
    test_name = request.node.name
    outcome = "passed"  # Simplified - in real implementation, check actual outcome
    test_metrics.record_test(test_name, duration, outcome)


class TestCustomMetrics:
    """Test suite demonstrating custom metrics collection"""

    def test_fast_operation(self):
        """Fast test that should complete quickly"""
        result = 2 + 2
        assert result == 4

    def test_slow_operation(self):
        """Slow test for metrics demonstration"""
        time.sleep(0.6)  # Simulate slow operation
        assert True

    def test_metrics_collection(self):
        """Test that metrics are being collected"""
        # This would typically be in a separate test file or conftest.py
        summary = test_metrics.get_summary()
        assert summary["total_tests"] > 0


# =============================================================================
# 6. Advanced Parametrization and Test Generation
# =============================================================================


def generate_test_data():
    """Dynamically generate test data"""
    return [
        ("user1@example.com", True),
        ("invalid-email", False),
        ("user2@domain.co.uk", True),
        ("@invalid.com", False),
        ("user.name+tag@domain.com", True),
    ]


def validate_email(email: str) -> bool:
    """Simple email validation function"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


class TestAdvancedParametrization:
    """Advanced parametrization examples"""

    @pytest.mark.parametrize("email,expected", generate_test_data())
    def test_email_validation_dynamic(self, email, expected):
        """Test email validation with dynamically generated data"""
        result = validate_email(email)
        assert result == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            pytest.param("valid@example.com", True, id="valid_email"),
            pytest.param("invalid", False, id="invalid_format"),
            pytest.param("", False, id="empty_string"),
            pytest.param("test@", False, id="incomplete_domain"),
            pytest.param("@example.com", False, id="missing_user"),
        ],
    )
    def test_email_validation_with_ids(self, test_input, expected):
        """Test with custom test IDs for better test reporting"""
        result = validate_email(test_input)
        assert result == expected


# =============================================================================
# Conftest.py patterns for advanced setups
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom settings"""
    # This would typically be in conftest.py
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


if __name__ == "__main__":
    print("Advanced pytest Integration Examples")
    print("=" * 50)
    print("This file demonstrates:")
    print("1. Advanced fixture patterns and dependency injection")
    print("2. Testing async code with pytest-asyncio")
    print("3. Database integration testing")
    print("4. Multi-threading and concurrency testing")
    print("5. Custom pytest plugins and hooks")
    print("6. Advanced parametrization techniques")
    print("\nRun with: pytest advanced_integration.py")
    print("For async tests: pytest advanced_integration.py -m asyncio")
