"""VeyaShip - 看板测试（F1 Dashboard）

覆盖：dashboard 统计接口（GET /api/v1/analytics/dashboard）。

注：listings/content/platforms 字段与 /usage-trend 接口在当前系统从未实现
（app/api/v1/endpoints/ 下有未挂载的旧 schema 版本），对应过时测试已删除。
"""

import pytest
from httpx import AsyncClient


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


