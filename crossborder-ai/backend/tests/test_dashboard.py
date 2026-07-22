"""VeyaShip - 看板和统计测试（F1 Dashboard）

覆盖：
1. dashboard 统计接口（GET /api/v1/analytics/dashboard）
2. 使用趋势接口（GET /api/v1/analytics/usage-trend）
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_stats(client: AsyncClient, auth_headers: dict):
    """测试看板统计

    验证返回的数据结构包含 products、listings、content 字段。
    """
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert "products" in data
    assert "listings" in data
    assert "content" in data
    assert "platforms" in data

    # 新用户应该没有商品
    assert data["products"]["total"] == 0


@pytest.mark.asyncio
async def test_dashboard_product_count(client: AsyncClient, auth_headers: dict):
    """测试看板商品计数

    创建 2 个商品后，dashboard 的商品数应为 2。
    """
    # 创建 2 个商品
    for i in range(2):
        await client.post(
            "/api/v1/products/manual",
            json={
                "url": f"https://detail.1688.com/offer/{300000 + i}.html",
                "title": f"看板商品{i}",
            },
            headers=auth_headers,
        )

    # 查看 dashboard 统计
    response = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["products"]["total"] == 2


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    """测试未认证时返回 401"""
    response = await client.get("/api/v1/analytics/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_usage_trend(client: AsyncClient, auth_headers: dict):
    """测试使用趋势接口"""
    response = await client.get(
        "/api/v1/analytics/usage-trend",
        params={"days": 30},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["days"] == 30
    assert "trend" in data
    assert data["total"] == 0
