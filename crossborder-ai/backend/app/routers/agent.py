"""VeyaShip - AI Agent 智能助手路由

【F7 Concierge —— 一站式 AI 操作入口】

用户输入自然语言指令，Agent 自动规划并执行。
不需要用户手动切换页面，一个输入框搞定所有操作。

示例指令：
- "帮我抓取 https://detail.1688.com/offer/xxx.html 并生成 Amazon Listing"
- "售价$19.99，成本¥30，算下净利"
- "检查这段文本有没有违禁词：最好的商品"
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import RateLimit
from app.dependencies import get_current_user
from app.models.user import User
from app.services.ai.agent_orchestrator import AgentOrchestrator
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agent", tags=["AI 智能助手"])


class AgentRequest(BaseModel):
    """用户发给 Agent 的指令"""
    instruction: str = Field(..., min_length=2, max_length=2000, description="自然语言指令，如：帮我抓取这个商品并生成Listing")


class AgentResponse(BaseModel):
    """Agent 的执行结果"""
    summary: str = ""
    status: str = ""  # success | partial | failed
    steps: list = []


@router.post("/run", response_model=AgentResponse)
async def run_agent(
    payload: AgentRequest,
    request: Request,
    _ratelimit=Depends(RateLimit("ai_generate")),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI Agent 入口：理解用户指令并自动执行

    【全栈学习者必读】
    这个接口是 F7 Concierge 的核心——把多个独立功能整合为"一站式服务"。

    传统方式：用户要切换3个页面完成1个任务
    智能方式：用户说一句话，Agent 搞定

    执行流程：
    1. LLM 解析用户指令 → 生成执行计划（步骤列表）
    2. 按顺序执行每一步（抓取→创建→生成→发布）
    3. 汇总结果返回
    """
    if current_user.credits < 1:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="积分不足，每次 AI 操作消耗 1 积分",
        )

    orchestrator = AgentOrchestrator(current_user, db)

    try:
        result = await orchestrator.run(payload.instruction)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Agent 执行失败：{str(e)}",
        )

    # 扣积分（Agent 操作消耗 1 积分）
    await current_user.deduct_credits(db, 1)

    return AgentResponse(
        summary=result.get("summary", ""),
        status=result.get("status", "failed"),
        steps=result.get("steps", []),
    )
