"""
Tests for API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mluv-me"
        assert data["version"] == "1.0.0"

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "Nazdar" in data["message"]


@pytest.mark.asyncio
class TestUserEndpoints:
    """Tests for user endpoints."""

    async def test_create_user(self, client: AsyncClient, user_data):
        """Test creating a user."""
        response = await client.post("/api/v1/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["telegram_id"] == user_data["telegram_id"]
        assert data["username"] == user_data["username"]
        assert data["first_name"] == user_data["first_name"]
        assert data["ui_language"] == user_data["ui_language"]
        assert data["level"] == user_data["level"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_duplicate_user(self, client: AsyncClient, user_data):
        """Test creating duplicate user fails."""
        # Create first user
        await client.post("/api/v1/users", json=user_data)

        # Try to create again
        response = await client.post("/api/v1/users", json=user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_user_by_telegram_id(self, client: AsyncClient, user_data):
        """Test getting user by Telegram ID."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)

        # Get user
        telegram_id = user_data["telegram_id"]
        response = await client.get(f"/api/v1/users/telegram/{telegram_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == telegram_id

    async def test_get_user_by_id(self, client: AsyncClient, user_data):
        """Test getting user by ID."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Get user
        response = await client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id

    async def test_get_nonexistent_user(self, client: AsyncClient):
        """Test getting nonexistent user."""
        response = await client.get("/api/v1/users/999999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_user(self, client: AsyncClient, user_data, user_update_data):
        """Test updating user."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Update user
        response = await client.patch(
            f"/api/v1/users/{user_id}",
            json=user_update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["level"] == user_update_data["level"]
        assert data["ui_language"] == user_update_data["ui_language"]

    async def test_get_user_settings(self, client: AsyncClient, user_data):
        """Test getting user settings."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Get settings
        response = await client.get(f"/api/v1/users/{user_id}/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_style"] == "friendly"
        assert data["voice_speed"] == "normal"
        assert data["corrections_level"] == "balanced"
        assert data["notifications_enabled"] is True

    async def test_update_user_settings(
        self,
        client: AsyncClient,
        user_data,
        settings_update_data
    ):
        """Test updating user settings."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Update settings
        response = await client.patch(
            f"/api/v1/users/{user_id}/settings",
            json=settings_update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["conversation_style"] == settings_update_data["conversation_style"]
        assert data["voice_speed"] == settings_update_data["voice_speed"]
        assert data["corrections_level"] == settings_update_data["corrections_level"]


@pytest.mark.asyncio
class TestValidation:
    """Tests for input validation."""

    async def test_create_user_invalid_language(self, client: AsyncClient, user_data):
        """Test creating user with invalid language."""
        invalid_data = {**user_data, "ui_language": "invalid"}
        response = await client.post("/api/v1/users", json=invalid_data)

        assert response.status_code == 422  # Validation error

    async def test_create_user_invalid_level(self, client: AsyncClient, user_data):
        """Test creating user with invalid level."""
        invalid_data = {**user_data, "level": "invalid"}
        response = await client.post("/api/v1/users", json=invalid_data)

        assert response.status_code == 422  # Validation error

    async def test_create_user_missing_required_fields(self, client: AsyncClient):
        """Test creating user without required fields."""
        response = await client.post("/api/v1/users", json={})

        assert response.status_code == 422  # Validation error

    async def test_update_settings_invalid_style(
        self,
        client: AsyncClient,
        user_data
    ):
        """Test updating settings with invalid style."""
        # Create user
        create_response = await client.post("/api/v1/users", json=user_data)
        user_id = create_response.json()["id"]

        # Try to update with invalid style
        response = await client.patch(
            f"/api/v1/users/{user_id}/settings",
            json={"conversation_style": "invalid"}
        )

        assert response.status_code == 422  # Validation error



