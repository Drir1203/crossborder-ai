"""VeyaShip - Product Endpoint Tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product(client: AsyncClient, sample_user_data: dict):
    """Test creating a new product."""
    # Register and login
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product
    response = await client.post(
        "/api/v1/products",
        json={
            "title": "Test Product",
            "description": "A test product description",
            "price": 29.99,
            "sku": "TP-001",
            "stock_quantity": 100,
            "category": "Electronics",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Product"
    assert data["sku"] == "TP-001"
    assert data["price"] == 29.99


@pytest.mark.asyncio
async def test_list_products(client: AsyncClient, sample_user_data: dict):
    """Test listing products."""
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"],
        },
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a product
    await client.post(
        "/api/v1/products",
        json={"title": "Product 1", "price": 10.0},
        headers=headers,
    )

    # List products
    response = await client.get("/api/v1/products", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
