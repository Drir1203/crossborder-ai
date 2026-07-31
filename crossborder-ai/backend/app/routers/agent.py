"""VeyaShip AI - AI Agent 智能助手路由

支持持久化对话、上下文记忆、继续对话。
"""

import json
import uuid as uuid_lib

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import RateLimit
from app.core.access_control import check_feature_access
from app.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationMessage
from app.services.ai.agent_orchestrator import AgentOrchestrator
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agent", tags=["AI 智能助手"])

# ════════════════════════════════════════════════════════════════
# 工作流模板（预设）
# ════════════════════════════════════════════════════════════════

@router.get("/workflows")
async def list_workflows():
    return {
        "workflows": [
            {"id": "select_products", "name": "AI 选品决策", "desc": "输入品类 → AI 推荐值得做的商品 + 利润估算", "cost": 2},
            {"id": "decision_and_list", "name": "判断商品 + 生成 Listing", "desc": "分析能不能做 → 生成 Listing → 合规修复", "cost": 2},
            {"id": "1688_to_shopify", "name": "1688 → Shopify 上架", "desc": "抓取商品 → AI 生成 Listing → 发布到 Shopify", "cost": 2},
            {"id": "1688_to_amazon", "name": "1688 → Amazon 上架", "desc": "抓取商品 → AI 生成 Amazon Listing", "cost": 2},
            {"id": "scrape_and_list", "name": "抓取 + 生成 Listing", "desc": "抓取 1688 商品 → AI 生成 Listing", "cost": 1},
        ]
    }

# ════════════════════════════════════════════════════════════════
# 对话管理
# ════════════════════════════════════════════════════════════════

@router.get("/conversations")
async def list_conversations(
    page: int = Query(1, ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的对话历史列表"""
    query = select(Conversation).where(Conversation.user_id == current_user.id).order_by(desc(Conversation.updated_at))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.offset((page - 1) * 20).limit(20))
    convs = result.scalars().all()

    return {
        "items": [{"id": str(c.id), "title": c.title or "新对话", "created_at": str(c.created_at), "message_count": 0} for c in convs],
        "total": total or 0,
    }


@router.post("/conversations")
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新的对话会话"""
    conv = Conversation(user_id=current_user.id)
    db.add(conv)
    await db.flush()
    return {"id": str(conv.id), "title": "新对话"}


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取对话的完整消息历史"""
    from uuid import UUID
    try:
        cid = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的对话ID")

    conv = (await db.execute(select(Conversation).where(Conversation.id == cid, Conversation.user_id == current_user.id))).scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    msgs = (await db.execute(
        select(ConversationMessage).where(ConversationMessage.conversation_id == cid).order_by(ConversationMessage.created_at)
    )).scalars().all()

    return {
        "id": str(conv.id),
        "title": conv.title or "新对话",
        "messages": [
            {"role": m.role, "content": m.content, "steps": json.loads(m.steps) if m.steps else None, "created_at": str(m.created_at)}
            for m in msgs
        ],
    }

# ════════════════════════════════════════════════════════════════
# Agent 执行（支持对话持久化）
# ════════════════════════════════════════════════════════════════

class AgentRequest(BaseModel):
    instruction: str = Field(..., min_length=2, max_length=2000)
    conversation_id: str = Field("", description="对话ID，留空创建新对话")


class AgentResponse(BaseModel):
    summary: str = ""
    status: str = ""
    steps: list = []
    conversation_id: str = ""


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    payload: AgentRequest,
    request: Request,
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行 AI Agent 指令（自动保存对话历史）"""
    from uuid import UUID

    if not check_feature_access(current_user, "agent"):
        raise HTTPException(status_code=403, detail="AI 智能助手仅限 Standard 及以上套餐使用")

    if current_user.credits < 1:
        raise HTTPException(status_code=402, detail="积分不足")

    # 查找或创建对话
    conv_id = None
    if payload.conversation_id:
        try:
            cid = UUID(payload.conversation_id)
            conv = (await db.execute(select(Conversation).where(Conversation.id == cid, Conversation.user_id == current_user.id))).scalar_one_or_none()
            if conv:
                conv_id = conv.id
        except ValueError:
            pass

    if not conv_id:
        conv = Conversation(user_id=current_user.id)
        db.add(conv)
        await db.flush()
        conv_id = conv.id

    # 保存用户消息
    db.add(ConversationMessage(conversation_id=conv_id, role="user", content=payload.instruction))

    # 执行 Agent
    orchestrator = AgentOrchestrator(current_user, db)
    try:
        result = await orchestrator.run(payload.instruction)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent 执行失败：{str(e)}")

    # 自动生成对话标题（第一条消息时）
    if not conv.title:
        conv.title = payload.instruction[:50] + ("..." if len(payload.instruction) > 50 else "")
        db.add(conv)

    # 保存助手回复
    db.add(ConversationMessage(
        conversation_id=conv_id,
        role="assistant",
        content=result.get("summary", ""),
        steps=json.dumps(result.get("steps", []), ensure_ascii=False),
    ))
    await db.flush()

    await current_user.deduct_credits(db, 1)

    return AgentResponse(
        summary=result.get("summary", ""),
        status=result.get("status", "failed"),
        steps=result.get("steps", []),
        conversation_id=str(conv_id),
    )


class WorkflowRequest(BaseModel):
    workflow: str = Field(...)
    url: str = Field("")
    platform: str = Field("amazon")
    language: str = Field("en")


@router.post("/workflow", response_model=AgentResponse)
async def run_workflow(
    payload: WorkflowRequest,
    request: Request,
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行预设工作流"""
    if current_user.credits < 2:
        raise HTTPException(status_code=402, detail="积分不足")

    orchestrator = AgentOrchestrator(current_user, db)
    params = {"url": payload.url, "platform": payload.platform, "language": payload.language}

    try:
        result = await orchestrator.run_workflow(payload.workflow, params)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"工作流执行失败：{str(e)}")

    await current_user.deduct_credits(db, 2)

    return AgentResponse(
        summary=result.get("summary", ""),
        status=result.get("status", "failed"),
        steps=result.get("steps", []),
    )
