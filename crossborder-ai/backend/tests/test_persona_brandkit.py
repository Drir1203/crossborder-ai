"""VeyaShip - CAP-04 Persona → Brand Kit 全链路统一注入测试

覆盖：
1. GET/PUT /settings/persona 透传 Brand Kit 三字段（target_market/product_category/image_style）
2. PUT 覆盖保存保持幂等 upsert，缺省时读回为空
3. build_persona_kit / format_persona_block / image_style_phrase 输出含新增字段
4. content 出口注入：mock DeepSeek 断言 system prompt 含「品牌档案」与 target_market 值
"""

import pytest
from httpx import AsyncClient

from app.models.product import Product
from app.routers import content as content_router
from app.routers.content import GenerateRequest
from app.services.ai.deepseek import DeepSeekService
from app.services.ai.persona_kit import (
    build_persona_kit,
    format_persona_block,
    image_style_phrase,
)


async def _put_persona(client: AsyncClient, auth_headers: dict, body: dict) -> dict:
    resp = await client.put("/api/v1/settings/persona", json=body, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_persona_default_empty(client: AsyncClient, auth_headers: dict):
    """未配置 persona 时 GET 返回默认空：Brand Kit 字段为 None"""
    resp = await client.get("/api/v1/settings/persona", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_market"] is None
    assert data["product_category"] is None
    assert data["image_style"] is None
    assert data["banned_words"] == []


@pytest.mark.asyncio
async def test_persona_brandkit_upsert_and_read(client: AsyncClient, auth_headers: dict):
    """PUT 写入 Brand Kit 三字段 → GET 读回一致"""
    body = {
        "brand_name": "Aurora Home",
        "tagline": "Cozy & durable",
        "description": "家居收纳品牌",
        "tone": "professional",
        "banned_words": ["best seller"],
        "target_market": "amazon.com",
        "product_category": "家居收纳",
        "image_style": "clean studio lighting, soft shadows",
    }
    saved = await _put_persona(client, auth_headers, body)

    assert saved["target_market"] == "amazon.com"
    assert saved["product_category"] == "家居收纳"
    assert saved["image_style"] == "clean studio lighting, soft shadows"
    assert saved["banned_words"] == ["best seller"]

    # GET 读回
    resp = await client.get("/api/v1/settings/persona", headers=auth_headers)
    data = resp.json()
    assert data["target_market"] == "amazon.com"
    assert data["product_category"] == "家居收纳"
    assert data["image_style"] == "clean studio lighting, soft shadows"


@pytest.mark.asyncio
async def test_persona_brandkit_partial_overwrite(client: AsyncClient, auth_headers: dict):
    """再次 PUT（覆盖保存，幂等 upsert）：只更新 brand_name，其它 Brand Kit 字段被覆盖为空"""
    await _put_persona(client, auth_headers, {
        "brand_name": "Aurora Home",
        "tone": "luxury",
        "target_market": "amazon.com",
        "product_category": "家居收纳",
        "image_style": "studio light",
    })
    # 只发 brand_name —— 覆盖保存后其它字段应为空
    await _put_persona(client, auth_headers, {"brand_name": "NewBrand"})

    resp = await client.get("/api/v1/settings/persona", headers=auth_headers)
    data = resp.json()
    assert data["brand_name"] == "NewBrand"
    assert data["target_market"] is None
    assert data["product_category"] is None
    assert data["image_style"] is None


@pytest.mark.asyncio
async def test_build_persona_kit_contains_new_fields(client: AsyncClient, auth_headers: dict):
    """build_persona_kit 输出含 Brand Kit 新增字段；format_persona_block 生成中文档案块"""
    await _put_persona(client, auth_headers, {
        "brand_name": "Aurora Home",
        "tone": "professional",
        "target_market": "amazon.com",
        "product_category": "家居收纳",
        "image_style": "clean studio lighting, soft shadows",
        "banned_words": ["cheapest"],
    })
    resp = await client.get("/api/v1/settings/persona", headers=auth_headers)
    data = resp.json()

    kit = build_persona_kit(data)
    assert kit["target_market"] == "amazon.com"
    assert kit["product_category"] == "家居收纳"
    assert kit["image_style"] == "clean studio lighting, soft shadows"

    block = format_persona_block(kit)
    assert "【品牌档案】" in block
    assert "品牌名称：Aurora Home" in block
    assert "目标市场：amazon.com" in block
    assert "主营类目：家居收纳" in block

    # 图片风格：有 image_style 直接用，无则退 tone + style
    assert image_style_phrase(kit) == "clean studio lighting, soft shadows"
    assert image_style_phrase({"tone": "minimal"}) == "minimal style"


@pytest.mark.asyncio
async def test_persona_block_skips_missing_fields():
    """缺失字段跳过，未配置任何字段返回空串（不注入）"""
    assert format_persona_block(None) == ""
    assert format_persona_block({}) == ""
    kit = build_persona_kit({"brand_name": "", "tone": "professional", "target_market": None})
    # 仅语气是非空缺省值，但要求缺失字段跳过——tone 默认存在时仍会输出语气行
    assert kit["target_market"] is None


@pytest.mark.asyncio
async def test_content_exit_injects_persona_block(
    client: AsyncClient, auth_headers: dict, db_session, monkeypatch
):
    """content 出口（描述生成）注入：system prompt 顶部含「品牌档案」与 target_market 值"""
    # 通过 settings PUT 写入，保证与真实路径一致
    await _put_persona(client, auth_headers, {
        "brand_name": "Aurora Home",
        "tagline": "Cozy & durable",
        "tone": "professional",
        "target_market": "amazon.com",
        "product_category": "家居收纳",
    })

    # 捕获 system prompt 的 mock：记录最后一次生成收到的 system prompt
    captured: list[str] = []

    async def fake_generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        captured.append(system_prompt)
        return "Aurora premium storage boxes"

    monkeypatch.setattr(DeepSeekService, "generate", fake_generate)

    # 构造最小的 product/payload 直接调用 content 出口函数
    product = Product(title="收纳箱", price=19.9, shop_name="Aurora")
    payload = GenerateRequest(product_id="x", platform="amazon", language="en")

    # 用真实 persona_kit 组装品牌档案块（与路由第 3 步同源）
    resp = await client.get("/api/v1/settings/persona", headers=auth_headers)
    kit = build_persona_kit(resp.json())
    block = format_persona_block(kit)
    assert "目标市场：amazon.com" in block

    llm = DeepSeekService()
    await content_router._generate_description(llm, product, payload, persona_block=block)

    assert captured, "应至少调用一次 DeepSeek generate"
    sys_prompt = captured[0]
    assert "【品牌档案】" in sys_prompt
    assert "目标市场：amazon.com" in sys_prompt
