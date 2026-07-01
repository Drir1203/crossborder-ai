"""VeyaShip - Auth Endpoint Tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "VeyaShip" in data["app"]


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, sample_user_data: dict):
    """Test user registration."""
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, sample_user_data: dict
):
    """Test that duplicate email registration is rejected."""
    # First registration
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Second registration with same email
    response = await client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client: AsyncClient, sample_user_data: dict):
    """Test user login."""
    # Register first
    await client.post("/api/v1/auth/register", json=sample_user_data)

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with wrong password."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]
