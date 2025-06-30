"""
Practical pytest Examples: Real-World Testing Patterns
=====================================================

This file demonstrates practical pytest usage patterns that mid-level Python
developers encounter in real projects. Each example focuses on common testing
scenarios with clear explanations.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


# =============================================================================
# 1. Testing File Operations with Temporary Files
# =============================================================================


class FileProcessor:
    """Example class that processes files - common in data pipelines"""

    def read_json_file(self, file_path):
        """Read and parse JSON file"""
        with open(file_path, "r") as f:
            return json.load(f)

    def process_data(self, data):
        """Process data and return transformed result"""
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = value.upper()
            elif isinstance(value, (int, float)):
                result[key] = value * 2
            else:
                result[key] = str(value)

        return result


@pytest.fixture
def sample_json_data():
    """Provide sample JSON data for testing"""
    return {"name": "john doe", "age": 25, "score": 85.5, "active": True}


@pytest.fixture
def temp_json_file(sample_json_data, tmp_path):
    """Create a temporary JSON file for testing"""
    file_path = tmp_path / "test_data.json"
    with open(file_path, "w") as f:
        json.dump(sample_json_data, f)
    return file_path


def test_file_processor_read_json(temp_json_file, sample_json_data):
    """Test reading JSON files with temporary files"""
    processor = FileProcessor()
    result = processor.read_json_file(temp_json_file)

    assert result == sample_json_data
    assert result["name"] == "john doe"
    assert result["age"] == 25


def test_file_processor_invalid_file():
    """Test error handling for invalid file paths"""
    processor = FileProcessor()

    with pytest.raises(FileNotFoundError):
        processor.read_json_file("nonexistent_file.json")


@pytest.mark.parametrize(
    "input_data,expected",
    [
        ({"name": "alice", "count": 5}, {"name": "ALICE", "count": 10}),
        ({"title": "test", "value": 2.5}, {"title": "TEST", "value": 5.0}),
        (
            {"status": "active", "items": [1, 2, 3]},
            {"status": "ACTIVE", "items": "[1, 2, 3]"},
        ),
    ],
)
def test_file_processor_data_transformation(input_data, expected):
    """Test data processing with various input types"""
    processor = FileProcessor()
    result = processor.process_data(input_data)
    assert result == expected


# =============================================================================
# 2. Testing API Interactions with Mocking
# =============================================================================

import requests
from typing import Dict, Optional


class APIClient:
    """Example API client class"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Fetch user data from API"""
        response = self.session.get(f"{self.base_url}/users/{user_id}")

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user via API"""
        response = self.session.post(f"{self.base_url}/users", json=user_data)
        response.raise_for_status()
        return response.json()


@pytest.fixture
def api_client():
    """Create an API client for testing"""
    return APIClient("https://api.example.com", "test-api-key")


@pytest.fixture
def mock_user_data():
    """Sample user data for testing"""
    return {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com",
        "created_at": "2023-01-15T10:30:00Z",
    }


def test_api_client_get_user_success(api_client, mock_user_data):
    """Test successful user retrieval"""
    with patch.object(api_client.session, "get") as mock_get:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_user_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api_client.get_user(123)

        assert result == mock_user_data
        mock_get.assert_called_once_with("https://api.example.com/users/123")


def test_api_client_get_user_not_found(api_client):
    """Test handling of user not found"""
    with patch.object(api_client.session, "get") as mock_get:
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = api_client.get_user(999)

        assert result is None
        mock_get.assert_called_once_with("https://api.example.com/users/999")


def test_api_client_create_user(api_client, mock_user_data):
    """Test user creation"""
    with patch.object(api_client.session, "post") as mock_post:
        # Mock successful creation response
        mock_response = Mock()
        mock_response.json.return_value = mock_user_data
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        user_input = {"name": "John Doe", "email": "john@example.com"}
        result = api_client.create_user(user_input)

        assert result == mock_user_data
        mock_post.assert_called_once_with(
            "https://api.example.com/users", json=user_input
        )


# =============================================================================
# 3. Testing Database Operations (Mocked)
# =============================================================================


class UserRepository:
    """Example repository class for database operations"""

    def __init__(self, db_connection):
        self.db = db_connection

    def find_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email address"""
        cursor = self.db.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

        if row:
            return {"id": row[0], "name": row[1], "email": row[2]}
        return None

    def create_user(self, name: str, email: str) -> Dict:
        """Create a new user"""
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        user_id = cursor.lastrowid

        return {"id": user_id, "name": name, "email": email}


@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing"""
    mock_db = Mock()
    mock_cursor = Mock()
    mock_db.cursor.return_value = mock_cursor
    return mock_db


@pytest.fixture
def user_repository(mock_db_connection):
    """Create user repository with mocked database"""
    return UserRepository(mock_db_connection)


def test_user_repository_find_existing_user(user_repository, mock_db_connection):
    """Test finding an existing user"""
    # Setup mock cursor behavior
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchone.return_value = (1, "John Doe", "john@example.com")

    result = user_repository.find_by_email("john@example.com")

    assert result == {"id": 1, "name": "John Doe", "email": "john@example.com"}
    mock_cursor.execute.assert_called_once_with(
        "SELECT id, name, email FROM users WHERE email = ?", ("john@example.com",)
    )


def test_user_repository_user_not_found(user_repository, mock_db_connection):
    """Test handling when user is not found"""
    # Setup mock cursor to return None
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.fetchone.return_value = None

    result = user_repository.find_by_email("nonexistent@example.com")

    assert result is None


def test_user_repository_create_user(user_repository, mock_db_connection):
    """Test user creation"""
    # Setup mock cursor behavior
    mock_cursor = mock_db_connection.cursor.return_value
    mock_cursor.lastrowid = 42

    result = user_repository.create_user("Jane Doe", "jane@example.com")

    assert result == {"id": 42, "name": "Jane Doe", "email": "jane@example.com"}
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        ("Jane Doe", "jane@example.com"),
    )


# =============================================================================
# 4. Testing Time-Dependent Code
# =============================================================================


class TaskScheduler:
    """Example class that works with time-dependent operations"""

    def is_business_hour(self, dt: datetime = None) -> bool:
        """Check if given datetime is within business hours (9 AM - 5 PM)"""
        if dt is None:
            dt = datetime.now()

        # Business hours: Monday-Friday, 9 AM - 5 PM
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False

        return 9 <= dt.hour < 17

    def get_next_business_day(self, dt: datetime = None) -> datetime:
        """Get the next business day from given date"""
        if dt is None:
            dt = datetime.now()

        # Start from the next day
        next_day = dt + timedelta(days=1)

        # Skip weekends
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)

        return next_day.replace(hour=9, minute=0, second=0, microsecond=0)


@pytest.fixture
def scheduler():
    """Create task scheduler for testing"""
    return TaskScheduler()


@pytest.mark.parametrize(
    "test_datetime,expected",
    [
        (datetime(2023, 6, 15, 10, 30), True),  # Thursday 10:30 AM
        (datetime(2023, 6, 15, 8, 30), False),  # Thursday 8:30 AM (too early)
        (datetime(2023, 6, 15, 17, 30), False),  # Thursday 5:30 PM (too late)
        (datetime(2023, 6, 17, 10, 30), False),  # Saturday 10:30 AM (weekend)
        (datetime(2023, 6, 18, 10, 30), False),  # Sunday 10:30 AM (weekend)
    ],
)
def test_scheduler_business_hours(scheduler, test_datetime, expected):
    """Test business hour detection with various times"""
    result = scheduler.is_business_hour(test_datetime)
    assert result == expected


def test_scheduler_next_business_day_from_friday(scheduler):
    """Test getting next business day from Friday"""
    friday = datetime(2023, 6, 16, 15, 30)  # Friday 3:30 PM
    result = scheduler.get_next_business_day(friday)

    expected = datetime(2023, 6, 19, 9, 0)  # Monday 9:00 AM
    assert result == expected


def test_scheduler_next_business_day_from_weekend(scheduler):
    """Test getting next business day from weekend"""
    saturday = datetime(2023, 6, 17, 10, 0)  # Saturday 10:00 AM
    result = scheduler.get_next_business_day(saturday)

    expected = datetime(2023, 6, 19, 9, 0)  # Monday 9:00 AM
    assert result == expected


@patch("builtins.datetime")
def test_scheduler_business_hours_current_time(mock_datetime, scheduler):
    """Test business hours check with mocked current time"""
    # Mock datetime.now() to return a specific time
    mock_now = datetime(2023, 6, 15, 14, 30)  # Thursday 2:30 PM
    mock_datetime.now.return_value = mock_now
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

    result = scheduler.is_business_hour()
    assert result is True


# =============================================================================
# 5. Testing Configuration and Environment Variables
# =============================================================================


class AppConfig:
    """Example configuration class"""

    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///default.db")
        self.api_timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.feature_flags = self._parse_feature_flags()

    def _parse_feature_flags(self) -> Dict[str, bool]:
        """Parse feature flags from environment variables"""
        flags = {}
        flag_string = os.getenv("FEATURE_FLAGS", "")

        if flag_string:
            for flag in flag_string.split(","):
                key, value = flag.split("=")
                flags[key.strip()] = value.strip().lower() == "true"

        return flags

    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature flag is enabled"""
        return self.feature_flags.get(feature_name, False)


def test_app_config_defaults(monkeypatch):
    """Test configuration with default values"""
    # Clear environment variables
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("API_TIMEOUT", raising=False)
    monkeypatch.delenv("FEATURE_FLAGS", raising=False)

    config = AppConfig()

    assert config.debug is False
    assert config.database_url == "sqlite:///default.db"
    assert config.api_timeout == 30
    assert config.feature_flags == {}


def test_app_config_with_environment_variables(monkeypatch):
    """Test configuration with custom environment variables"""
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:5432/testdb")
    monkeypatch.setenv("API_TIMEOUT", "60")
    monkeypatch.setenv("FEATURE_FLAGS", "new_ui=true,beta_feature=false")

    config = AppConfig()

    assert config.debug is True
    assert config.database_url == "postgresql://localhost:5432/testdb"
    assert config.api_timeout == 60
    assert config.feature_flags == {"new_ui": True, "beta_feature": False}
    assert config.is_feature_enabled("new_ui") is True
    assert config.is_feature_enabled("beta_feature") is False
    assert config.is_feature_enabled("unknown_feature") is False


# =============================================================================
# Run the tests
# =============================================================================

if __name__ == "__main__":
    # This file can be run directly to see the test structure
    # In practice, you would run: pytest practical_patterns.py

    print("Practical pytest Examples")
    print("=" * 50)
    print("This file contains real-world testing patterns:")
    print("1. File operations with temporary files")
    print("2. API interactions with mocking")
    print("3. Database operations (mocked)")
    print("4. Time-dependent code testing")
    print("5. Configuration and environment testing")
    print("\nRun with: pytest practical_patterns.py")
