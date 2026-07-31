"""VeyaShip - AI Agent 编排器

【功能】
用户用自然语言下达指令，Agent 自动规划并执行多步操作。
比如 "帮我抓取这个1688商品，生成Amazon Listing" → Agent 自动完成。

【工作流程】
1. 接收用户指令
2. LLM 解析意图，规划执行步骤
3. 按顺序执行每一步（可调用抓取、生成、发布等功能）
4. 返回执行结果

【可用工具】
- scrape_1688(url) → 抓取商品
- create_product(data) → 创建商品
- generate_listing(product_id, platform) → AI 生成 Listing
- check_compliance(text) → 合规审查
- calculate_profit(params) → 净利计算
"""

import json
import re
from typing import Any, Optional

from app.core.config import settings
from app.models.user import User
from app.services.ai.deepseek import DeepSeekService
from app.services.scraper import scrape_1688
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AgentOrchestrator:
    """AI Agent 编排器 —— 基于 ReAct + Function Calling 的决策 Agent"""

    # ── 工具注册表（DeepSeek Function Calling 格式） ─────────
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "analyze_category",
                "description": "分析一个品类在 Amazon 的市场情况",
                "parameters": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string", "description": "品类关键词，如蓝牙耳机"}},
                    "required": ["keyword"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "select_products",
                "description": "根据品类推荐值得做的商品，含利润估算",
                "parameters": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string", "description": "品类关键词，如宠物用品"}},
                    "required": ["keyword"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_product_decision",
                "description": "判断一个 1688 商品能不能做",
                "parameters": {
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "1688 商品链接"}},
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "scrape_1688",
                "description": "抓取 1688 商品信息",
                "parameters": {
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "1688 商品链接"}},
                    "required": ["url"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "generate_listing",
                "description": "为商品生成 AI Listing 文案",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string", "description": "商品 ID"},
                        "platform": {"type": "string", "description": "目标平台"},
                        "language": {"type": "string", "description": "目标语言"},
                    },
                    "required": ["product_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compliance_check",
                "description": "检查文本是否含违规内容",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "要检查的文本"}},
                    "required": ["text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "compliance_fix",
                "description": "检查文本并自动修复违规内容",
                "parameters": {
                    "type": "object",
                    "properties": {"text": {"type": "string", "description": "要检查修复的文本"}},
                    "required": ["text"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_profit",
                "description": "计算商品净利润",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selling_price": {"type": "number", "description": "售价"},
                        "product_cost": {"type": "number", "description": "成本"},
                        "platform_fee_rate": {"type": "number", "description": "平台费率"},
                        "shipping_cost": {"type": "number", "description": "运费"},
                        "exchange_rate": {"type": "number", "description": "汇率"},
                    },
                    "required": ["selling_price", "product_cost"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "store_check",
                "description": "巡检店铺所有商品，找出问题",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]

    def __init__(self, user: User, db: AsyncSession):
        self.llm = DeepSeekService()
        self.user = user
        self.db = db
        self.steps: list[dict] = []  # 记录执行步骤

    async def run_react(self, instruction: str, max_rounds: int = 6) -> dict:
        """ReAct 推理循环：思考 → 调用工具 → 观察 → 再思考

        直到模型认为任务完成（不再调用工具），或达到最大轮数。
        """
        self.steps = []
        system_prompt = (
            "你是跨境电商 AI 决策助手。你可以调用工具来完成任务。\n"
            "规则：\n"
            "1. 如果需要数据分析、选品、抓取、生成等操作，调用相应工具\n"
            "2. 每次调用工具后，根据结果决定下一步\n"
            "3. 任务完成后，用自然语言总结结果给用户\n"
            "4. 不要编造工具没返回的数据"
        )

        # 对话历史
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": instruction},
        ]

        for round_num in range(max_rounds):
            # 让模型思考并决定是否调用工具
            response = await self.llm.chat_with_tools(messages, tools=self.TOOLS)
            tool_calls = response.get("tool_calls", [])

            # 没有工具调用 → 模型认为任务完成，返回最终回答
            if not tool_calls:
                final_answer = response.get("content", "已完成")
                return {
                    "summary": final_answer,
                    "status": "success",
                    "steps": self.steps,
                }

            # 有工具调用 → 逐个执行
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                func_name = tc["function"]["name"]
                try:
                    func_args = json.loads(tc["function"]["arguments"])
                except (json.JSONDecodeError, KeyError):
                    func_args = {}

                # 执行工具
                result = await self._execute_step(func_name, func_args)
                self.steps.append(result)

                # 把工具结果返回给模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", str(round_num)),
                    "content": json.dumps(result, ensure_ascii=False, default=str)[:2000],
                })

        # 达到最大轮数
        return {
            "summary": "处理步骤较多，以下是已完成的步骤",
            "status": "success",
            "steps": self.steps,
        }

    async def run(self, instruction: str) -> dict:
        """执行用户指令

        Args:
            instruction: 用户输入的自然语言指令
                例如："帮我抓取 https://detail.1688.com/offer/xxx.html 并生成 Amazon Listing"

        Returns:
            {
                "summary": "执行总结",
                "steps": [每步的详细结果],
                "status": "success" | "partial" | "failed"
            }
        """
        # ── ReAct 推理循环：模型自己决定调用哪些工具 ────────
        result = await self.run_react(instruction)
        if result["status"] == "success":
            return result

        # ── 降级：如果 ReAct 失败，退回 Plan-and-Execute ──
        plan = await self._create_plan(instruction)
        self.steps = []

        for step in plan.get("steps", []):
            action = step.get("action", "")
            params = step.get("params", {})
            step_result = await self._execute_step(action, params)
            self.steps.append(step_result)

            if step_result["status"] == "failed" and step.get("critical", False):
                break

        # ── 汇总结果 ──────────────────────────────────────
        return self._build_summary()

    # ════════════════════════════════════════════════════════════
    # 工作流模板
    # ════════════════════════════════════════════════════════════
    WORKFLOWS = {
        "1688_to_shopify": {
            "name": "1688 → Shopify 上架",
            "steps": [
                {"action": "scrape_1688", "critical": True, "description": "抓取 1688 商品"},
                {"action": "create_product", "critical": True, "description": "创建商品"},
                {"action": "generate_listing", "critical": False, "description": "AI 生成 Listing"},
                {"action": "compliance_check", "critical": False, "description": "合规审查"},
                {"action": "push_to_shopify", "critical": False, "description": "发布到 Shopify"},
            ],
        },
        "1688_to_amazon": {
            "name": "1688 → Amazon 上架",
            "steps": [
                {"action": "scrape_1688", "critical": True},
                {"action": "create_product", "critical": True},
                {"action": "generate_listing", "critical": False, "params": {"platform": "amazon"}},
                {"action": "compliance_check", "critical": False},
            ],
        },
        "scrape_and_list": {
            "name": "抓取 + 生成 Listing",
            "steps": [
                {"action": "scrape_1688", "critical": True},
                {"action": "create_product", "critical": True},
                {"action": "generate_listing", "critical": False},
            ],
        },
        "store_check": {
            "name": "整店巡检",
            "steps": [
                {"action": "store_check", "critical": True, "description": "检查所有商品状态"},
            ],
        },
        "select_products": {
            "name": "AI 选品决策",
            "steps": [
                {"action": "select_products", "critical": True, "description": "AI 推荐值得做的商品"},
            ],
        },
        "decision_and_list": {
            "name": "判断商品 + 生成 Listing",
            "steps": [
                {"action": "analyze_product_decision", "critical": True, "description": "判断这个品能不能做"},
                {"action": "scrape_1688", "critical": True},
                {"action": "create_product", "critical": True},
                {"action": "generate_listing", "critical": False, "description": "AI 生成 Listing"},
                {"action": "compliance_fix", "critical": False, "description": "合规自动修复"},
            ],
        },
    }

    async def run_workflow(self, workflow_name: str, params: dict) -> dict:
        """执行预设工作流

        Args:
            workflow_name: 工作流名称（WORKFLOWS 的 key）
            params: 参数，如 {"url": "1688链接", "platform": "amazon", "language": "en"}
        """
        template = self.WORKFLOWS.get(workflow_name)
        if not template:
            return {"summary": f"未知工作流: {workflow_name}", "status": "failed", "steps": []}

        self.steps = []
        context = {}  # 步骤间传递数据

        for step_def in template["steps"]:
            action = step_def["action"]
            step_params = {**params, **step_def.get("params", {})}

            # 从上下文补充参数
            if "product_id" not in step_params and context.get("product_id"):
                step_params["product_id"] = context["product_id"]
            if "url" not in step_params and context.get("url"):
                step_params["url"] = context["url"]
            if "title" not in step_params and context.get("title"):
                step_params["title"] = context["title"]

            # 执行
            step_result = await self._execute_step(action, step_params)
            step_result["description"] = step_def.get("description", action)
            self.steps.append(step_result)

            # 传递数据到上下文
            data = step_result.get("data") or {}
            if data.get("url"): context["url"] = data["url"]
            if data.get("title"): context["title"] = data["title"]
            if data.get("product_id"): context["product_id"] = data["product_id"]
            if data.get("image_url"): context["image_url"] = data["image_url"]
            if step_result.get("summary"): context["last_summary"] = step_result["summary"]

            # 关键步骤失败则终止
            if step_result["status"] == "failed" and step_def.get("critical", False):
                break

        return self._build_summary()

    async def _create_plan(self, instruction: str) -> dict:
        """用 LLM 解析用户指令，生成执行计划

        让 AI 决定需要做什么、按什么顺序做。
        """
        system_prompt = """你是一个跨境电商 AI 助手，负责将用户的自然语言指令转为执行计划。

【核心规则】
- 你必须选择具体的工具来执行，不能只是回答问题
- 如果用户没有明确说要做什么，引导用户使用工具
- 用户提到分析/市场/能不能做/品类 → 用 analyze_category
- 用户提到选品/推荐/做点什么/想做XX → 用 select_products
- 用户提到检查店铺/巡检/看看我的商品 → 用 store_check
- 用户提到商品链接 + 能不能做/值不值得 → 用 analyze_product_decision
- 用户提到商品链接 → 用 scrape_1688
- 用户提到生成/发布/上架 → 用 generate_listing
- 用户提到利润/成本/计算 → 用 calculate_profit
- 用户提到检查/审核 → 用 compliance_check
- 不要使用 "answer" 工具，永远用具体工具

可用工具：
1. analyze_category — 品类市场分析
   参数: {"keyword": "品类关键词，如蓝牙耳机"}
   输出: 市场容量、竞争格局、利润模型、选品建议

2. select_products — 选品推荐
   参数: {"keyword": "品类关键词，如宠物用品"}
   输出: 推荐值得做的商品、利润估算、切入建议

3. analyze_product_decision — 单品决策
   参数: {"url": "1688商品链接"}
   输出: 能不能做、利润估算、建议定价

4. scrape_1688 — 抓取1688商品
   参数: {"url": "1688商品链接"}
   输出: 商品标题、价格、图片

5. create_product — 创建商品到系统
   参数: {"url": "...", "title": "...", "price": 数字}
   注意: scrape_1688 后才能拿到数据

6. generate_listing — AI 生成 Listing 内容
   参数: {"product_id": "商品ID", "platform": "amazon/ebay/shopify/etsy/walmart", "language": "en/ja/es等"}
   注意: 需要先有商品

7. compliance_check — 合规审查
   参数: {"text": "要检查的文本"}

8. calculate_profit — 净利计算
   参数: {"selling_price": 售价, "product_cost": 成本, "platform_fee_rate": 费率}

9. store_check — 整店巡检
   参数: 无（检查当前用户所有商品）
   输出: 有问题的商品列表（缺标题/价格等）

6. answer — 【仅当其他工具都不适用时】回答用户问题
   参数: {"message": "回答内容"}
   注意: 这是最后选项，优先用上面的工具

请分析用户的指令，返回 JSON 格式的执行计划：
{
    "summary": "对用户指令的理解",
    "steps": [
        {"action": "工具名", "params": {...}, "critical": true/false, "description": "这一步做什么"}
    ]
}

只返回 JSON，不要额外文字。"""

        result = await self.llm.generate(system_prompt, instruction, max_tokens=1000)
        # 提取 JSON
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"summary": "无法理解指令", "steps": [{"action": "answer", "params": {"message": "请更具体地描述你要做什么"}, "critical": False}]}

    async def _execute_step(self, action: str, params: dict) -> dict:
        """执行单个步骤"""
        try:
            if action == "scrape_1688":
                return await self._do_scrape(params)
            elif action == "analyze_product_decision":
                return await self._do_analyze_product_decision(params)
            elif action == "select_products":
                return await self._do_select_products(params)
            elif action == "store_check":
                return await self._do_store_check(params)
            elif action == "create_product":
                return await self._do_create_product(params)
            elif action == "generate_listing":
                return await self._do_generate_listing(params)
            elif action == "compliance_check":
                return await self._do_compliance(params)
            elif action == "compliance_fix":
                return await self._do_compliance_fix(params)
            elif action == "push_to_shopify":
                return await self._do_push_to_shopify(params)
            elif action == "calculate_profit":
                return await self._do_calculate_profit(params)
            elif action == "analyze_category":
                return await self._do_analyze_category(params)
            elif action == "answer":
                msg = params.get("message", "")
                return {"action": action, "status": "success", "result": msg, "summary": msg[:100]}
            else:
                return {"action": action, "status": "failed", "error": f"未知操作: {action}"}
        except Exception as e:
            return {"action": action, "status": "failed", "error": str(e)}

    async def _do_scrape(self, params: dict) -> dict:
        """执行 1688 抓取"""
        url = params.get("url", "")
        if not url:
            return {"action": "scrape_1688", "status": "failed", "error": "缺少URL"}

        # 从数据库读取 API Key 配置
        from app.models.system_config import SystemConfig
        config_rows = await self.db.execute(
            select(SystemConfig).where(
                SystemConfig.key.in_(["onebound_api_key", "onebound_api_secret"])
            )
        )
        sys_config = {row.key: row.value or "" for row in config_rows.scalars().all()}

        data = await scrape_1688(
            url,
            api_key=sys_config.get("onebound_api_key", ""),
            api_secret=sys_config.get("onebound_api_secret", ""),
        )

        # 自动创建商品
        product_data = {
            "url": data["url"],
            "title": data.get("title"),
            "main_image_url": data.get("main_image_url"),
            "price": data.get("price"),
            "sales_count": data.get("sales_count"),
            "shop_name": data.get("shop_name"),
        }

        return {
            "action": "scrape_1688",
            "status": "success",
            "data": product_data,
            "summary": f"已抓取商品：{data.get('title', '未知')}（¥{data.get('price', '?')}）",
        }

    async def _do_create_product(self, params: dict) -> dict:
        """创建商品到数据库"""
        from app.models.product import Product
        from uuid import UUID

        # 查重
        result = await self.db.execute(
            select(Product).where(Product.url == params.get("url", ""))
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {
                "action": "create_product",
                "status": "success",
                "product_id": str(existing.id),
                "summary": f"商品已存在：{existing.title}",
            }

        product = Product(
            user_id=self.user.id,
            url=params.get("url", ""),
            title=params.get("title"),
            main_image_url=params.get("main_image_url"),
            price=params.get("price"),
            sales_count=params.get("sales_count"),
            shop_name=params.get("shop_name"),
        )
        self.db.add(product)
        await self.db.flush()

        return {
            "action": "create_product",
            "status": "success",
            "product_id": str(product.id),
            "summary": f"已创建商品：{product.title}",
        }

    async def _do_generate_listing(self, params: dict) -> dict:
        """AI 生成 Listing"""
        from app.services.ai.deepseek import DeepSeekService
        from app.models.product import Product
        from uuid import UUID

        product_id = params.get("product_id", "")
        platform = params.get("platform", "amazon")
        language = params.get("language", "en")

        try:
            result = await self.db.execute(select(Product).where(Product.id == UUID(product_id)))
        except ValueError:
            return {"action": "generate_listing", "status": "failed", "error": "无效的商品ID"}

        product = result.scalar_one_or_none()
        if not product:
            return {"action": "generate_listing", "status": "failed", "error": "商品不存在"}

        llm = DeepSeekService()
        title = await llm.generate(
            f"You are an expert {platform} listing copywriter.",
            f"Generate a compelling product title for {platform} (max 200 chars):\nProduct: {product.title}",
            max_tokens=300,
        )
        description = await llm.generate_product_description(
            product_title=product.title or "",
            platform=platform,
        )
        bullets = await llm.generate_bullet_points(
            product_title=product.title or "",
            features=f"Price: {product.price}" if product.price else "",
            platform=platform,
        )

        return {
            "action": "generate_listing",
            "status": "success",
            "data": {"title": title, "description": description, "bullet_points": bullets},
            "summary": f"已为 {platform} 生成 Listing：{title[:50]}...",
        }

    async def _do_select_products(self, params: dict) -> dict:
        """选品决策：输入品类，AI 推荐值得做的商品"""
        from app.services.ai.deepseek import DeepSeekService

        keyword = params.get("keyword") or params.get("category") or params.get("query", "")
        if not keyword:
            return {"action": "select_products", "status": "failed", "error": "缺少品类关键词"}

        llm = DeepSeekService()
        try:
            # 让 AI 生成选品建议（市场分析 + 候选商品 + 利润估算）
            report = await llm.generate(
                "你是跨境电商选品专家。根据品类，推荐值得做的商品，给出详细分析和利润估算。",
                f"分析品类「{keyword}」的选品机会。\n"
                f"请输出：\n"
                f"1. 该品类在 Amazon 的市场概况（搜索量、竞争度）\n"
                f"2. 推荐 5 个值得做的具体商品（子品类/款式）\n"
                f"3. 每个商品：1688 采购价估算、建议 Amazon 定价、预计利润率、竞争度评估\n"
                f"4. 最终推荐 TOP 1 商品，说明理由\n"
                f"5. 给新手的切入建议\n"
                f"数据用具体数字，Markdown 格式。",
                max_tokens=4000,
            )

            # 额外算一个简化的推荐摘要
            summary = f"已完成「{keyword}」选品分析，推荐 5 个候选商品，含利润估算"
            return {
                "action": "select_products",
                "status": "success",
                "data": {"keyword": keyword, "report": report},
                "summary": summary,
            }
        except Exception as e:
            return {"action": "select_products", "status": "failed", "error": str(e)}

    async def _do_analyze_category(self, params: dict) -> dict:
        """品类分析"""
        from app.services.ai.deepseek import DeepSeekService
        keyword = params.get("keyword") or params.get("category") or params.get("query", "")
        if not keyword:
            return {"action": "analyze_category", "status": "failed", "error": "缺少品类关键词"}
        try:
            llm = DeepSeekService()
            report = await llm.generate(
                "你是一个跨境电商数据分析师。输出结构化市场分析报告，数据具体合理。",
                f"分析品类「{keyword}」Amazon US市场：1.市场概览（搜索量、商品数、均价）2.价格分布 3.竞争格局 4.用户痛点Top3 5.1688到Amazon利润模型 6.选品建议和评分。数据用具体数字。",
                max_tokens=4000,
            )
            return {"action": "analyze_category", "status": "success", "data": {"report": report}, "summary": f"{keyword} 市场分析完成"}
        except Exception as e:
            return {"action": "analyze_category", "status": "failed", "error": str(e)}

    async def _do_compliance(self, params: dict) -> dict:
        """合规审查（正则 + AI 双重检测）"""
        from app.routers.shopify import compliance_check
        from app.services.ai.deepseek import DeepSeekService

        text = params.get("text", "")
        if not text:
            return {"action": "compliance_check", "status": "failed", "error": "缺少要检查的文本"}

        violations = []

        # 第一层：广告法违禁词正则
        regex_violations = compliance_check(text)
        violations.extend(regex_violations)

        # 第二层：AI 检测不当用语（侮辱、攻击、虚假宣传等）
        try:
            llm = DeepSeekService()
            ai_result = await llm.generate(
                "你是电商内容合规审核员。判断以下文本是否存在问题，只返回JSON。",
                f"检查文本是否包含：1)侮辱/攻击性用语 2)虚假宣传 3)绝对化用语 4)其他违规内容。\n文本：{text}\n返回 JSON: {{\"has_issue\": true/false, \"issue_type\": \"类型\", \"reason\": \"原因\"}}",
                max_tokens=300,
            )
            import json as _json
            import re as _re
            match = _re.search(r'\{.*\}', ai_result, _re.DOTALL)
            if match:
                data = _json.loads(match.group())
                if data.get("has_issue"):
                    issue = data.get("reason", data.get("issue_type", "内容不当"))
                    violations.append(issue)
        except Exception:
            pass  # AI 检测失败则只依赖正则

        passed = len(violations) == 0
        return {
            "action": "compliance_check",
            "status": "success",
            "data": {"passed": passed, "violations": violations},
            "summary": "合规审查通过" if passed else f"发现违规内容：{'、'.join(violations)}",
        }

    async def _do_store_check(self, params: dict) -> dict:
        """整店巡检：检查用户所有商品，找出问题"""
        from app.models.product import Product
        from app.routers.shopify import compliance_check

        # 获取用户所有商品
        result = await self.db.execute(
            select(Product).where(Product.user_id == self.user.id).order_by(Product.created_at.desc())
        )
        products = result.scalars().all()

        if not products:
            return {"action": "store_check", "status": "success", "data": {"total": 0, "issues": []}, "summary": "暂无商品，先去添加商品吧"}

        issues = []
        ok_count = 0

        for p in products:
            product_issues = []
            if not p.title:
                product_issues.append("缺标题")
            if not p.price:
                product_issues.append("缺价格")
            if not p.url:
                product_issues.append("缺链接")
            if p.title and p.price:
                ok_count += 1

            if product_issues:
                issues.append({
                    "id": str(p.id),
                    "title": p.title or "未命名商品",
                    "price": p.price,
                    "issues": product_issues,
                })

        total = len(products)
        issue_count = len(issues)
        healthy = total - issue_count

        summary = f"巡检完成：共 {total} 个商品，{issue_count} 个有问题，{healthy} 个正常"
        if issues:
            summary += f"。待处理：{issue_count} 个"

        return {
            "action": "store_check",
            "status": "success",
            "data": {"total": total, "healthy": healthy, "issues": issues},
            "summary": summary,
        }

    async def _do_analyze_product_decision(self, params: dict) -> dict:
        """单品决策：判断一个 1688 商品能不能做

        流程：
        1. 抓取 1688 商品信息
        2. 算成本（采购价 + 运费）
        3. AI 分析市场竞争力
        4. 输出：能做/不能做 + 理由 + 建议定价
        """
        from app.services.ai.deepseek import DeepSeekService

        url = params.get("url", "")
        if not url:
            return {"action": "analyze_product_decision", "status": "failed", "error": "缺少商品链接"}

        # 1. 抓取商品
        try:
            data = await scrape_1688(url, api_key=params.get("api_key", ""), api_secret=params.get("api_secret", ""))
        except Exception as e:
            return {"action": "analyze_product_decision", "status": "failed", "error": f"抓取失败：{str(e)}"}

        title = data.get("title", "")
        price = data.get("price")  # 1688 供货价
        sales = data.get("sales_count")
        shop = data.get("shop_name")

        if not title:
            return {"action": "analyze_product_decision", "status": "failed", "error": "无法获取商品标题"}

        # 2. 算成本
        cost_cny = price or 0
        # 预估运费（跨境电商，按重量估，这里简化）
        shipping_cny = 15
        total_cost = cost_cny + shipping_cny

        # 3. AI 分析
        llm = DeepSeekService()
        try:
            analysis = await llm.generate(
                "你是跨境电商选品专家。根据商品信息和采购成本，判断这个品能不能做，给出结论和建议。",
                f"商品：{title}\n采购价：¥{cost_cny}\n预估总成本：¥{total_cost}\n销量参考：{sales or '未知'}\n店铺：{shop or '未知'}\n\n"
                f"请分析：\n1. Amazon 上类似产品的价格带\n2. 这个品的竞争力\n3. 利润空间估算（假设定价为采购价 3-5 倍）\n4. 最终结论：能做/谨慎/不能做 + 理由\n5. 建议定价和预计月利润",
                max_tokens=1500,
            )
        except Exception:
            analysis = f"AI 分析暂不可用，基础数据：采购价 ¥{cost_cny}，建议定价为采购价的 3-5 倍。"

        return {
            "action": "analyze_product_decision",
            "status": "success",
            "data": {
                "url": url,
                "title": title,
                "cost_cny": cost_cny,
                "analysis": analysis,
            },
            "summary": f"已分析「{title[:30]}」：采购价 ¥{cost_cny}",
        }

    async def _do_compliance_fix(self, params: dict) -> dict:
        """合规自动修复：检查文本，发现违禁词自动改写"""
        from app.routers.shopify import compliance_check
        from app.services.ai.deepseek import DeepSeekService

        text = params.get("text", "")
        if not text:
            return {"action": "compliance_fix", "status": "failed", "error": "缺少文本"}

        # 第一层：正则检查
        regex_violations = compliance_check(text)

        # 第二层：AI 检查
        ai_issue = ""
        try:
            llm = DeepSeekService()
            result = await llm.generate(
                "你是电商合规审核员。检查文本是否有问题，只返回JSON。",
                f"检查文本：{text}\n是否存在：侮辱性用语、虚假宣传、绝对化用语。\n返回 JSON: {{\"has_issue\": true/false, \"reason\": \"\"}}",
                max_tokens=200,
            )
            import json as _json
            import re as _re
            match = _re.search(r'\{.*\}', result, _re.DOTALL)
            if match:
                data = _json.loads(match.group())
                if data.get("has_issue"):
                    ai_issue = data.get("reason", "内容不当")
        except Exception:
            pass

        violations = list(regex_violations) + ([ai_issue] if ai_issue else [])

        if not violations:
            return {
                "action": "compliance_fix",
                "status": "success",
                "data": {"passed": True, "fixed": False, "text": text},
                "summary": "合规审查通过，无需修改",
            }

        # 发现违规 → AI 改写
        try:
            llm = DeepSeekService()
            fixed_text = await llm.generate(
                "你是电商文案合规优化师。重写文本，去掉违规内容，保留原意，输出优化后的文本。",
                f"原文：{text}\n违规原因：{'、'.join(violations)}\n请输出合规的改写版本，只输出文本本身。",
                max_tokens=1000,
            )
            return {
                "action": "compliance_fix",
                "status": "success",
                "data": {"passed": False, "fixed": True, "text": fixed_text.strip(), "violations": violations},
                "summary": f"发现违规内容（{'、'.join(violations)}），已自动改写",
            }
        except Exception as e:
            return {
                "action": "compliance_fix",
                "status": "success",
                "data": {"passed": False, "fixed": False, "text": text, "violations": violations},
                "summary": f"发现违规内容：{'、'.join(violations)}，请手动修改",
            }

    async def _do_push_to_shopify(self, params: dict) -> dict:
        """发布到 Shopify"""
        product_id = params.get("product_id")
        if not product_id:
            return {"action": "push_to_shopify", "status": "failed", "error": "缺少商品ID"}

        # 获取用户已绑定的 Shopify 店铺
        from app.models.shopify_channel import ShopifyChannel
        result = await self.db.execute(
            select(ShopifyChannel).where(
                ShopifyChannel.user_id == self.user.id,
                ShopifyChannel.is_active == True,
            )
        )
        channels = result.scalars().all()
        if not channels:
            return {"action": "push_to_shopify", "status": "failed", "error": "未绑定 Shopify 店铺，请先在 Shopify 页面绑定"}

        # 推送到第一个绑定的店铺
        import httpx
        from app.core.config import settings
        from app.models.product import Product
        from uuid import UUID

        prod_result = await self.db.execute(select(Product).where(Product.id == UUID(product_id)))
        product = prod_result.scalar_one_or_none()
        if not product:
            return {"action": "push_to_shopify", "status": "failed", "error": "商品不存在"}

        channel = channels[0]
        shop_url = f"https://{channel.shop_name}.myshopify.com/admin/api/2024-10"
        headers = {
            "X-Shopify-Access-Token": channel.access_token,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{shop_url}/products.json", json={
                "product": {
                    "title": product.title or "Untitled",
                    "body_html": product.description or "",
                    "status": "draft",
                    "variants": [{"price": str(product.price)}] if product.price else [],
                }
            }, headers=headers)

            if resp.status_code not in (200, 201):
                return {"action": "push_to_shopify", "status": "failed", "error": f"Shopify 发布失败：{resp.text[:150]}"}

            shopify_product = resp.json().get("product", {})
            shopify_url = f"https://{channel.shop_name}.myshopify.com/admin/products/{shopify_product.get('id')}"
            return {
                "action": "push_to_shopify",
                "status": "success",
                "data": {"shopify_product_id": shopify_product.get("id"), "shopify_url": shopify_url},
                "summary": f"已发布到 {channel.shop_name}（草稿状态）",
            }

    async def _do_calculate_profit(self, params: dict) -> dict:
        """净利计算"""
        selling_price = float(params.get("selling_price", 0))
        product_cost = float(params.get("product_cost", 0))
        platform_fee_rate = float(params.get("platform_fee_rate", 0.15))
        shipping_cost = float(params.get("shipping_cost", 0))
        exchange_rate = float(params.get("exchange_rate", 7.2))

        price_cny = selling_price * exchange_rate
        platform_fee = price_cny * platform_fee_rate
        total_cost = platform_fee + product_cost + shipping_cost
        net_profit = price_cny - total_cost
        margin = (net_profit / price_cny * 100) if price_cny > 0 else 0

        return {
            "action": "calculate_profit",
            "status": "success",
            "data": {
                "selling_price_cny": round(price_cny, 2),
                "net_profit": round(net_profit, 2),
                "profit_margin": round(margin, 1),
            },
            "summary": f"净利：¥{round(net_profit, 2)}，利润率：{round(margin, 1)}%",
        }

    def _build_summary(self) -> dict:
        """汇总执行结果"""
        success_steps = [s for s in self.steps if s["status"] == "success"]
        failed_steps = [s for s in self.steps if s["status"] == "failed"]

        if not failed_steps:
            status = "success"
            summary = "全部完成！" + " ".join(s.get("summary", "") for s in success_steps)
        elif success_steps:
            status = "partial"
            summary = "部分完成。成功：" + str(len(success_steps)) + "步，失败：" + str(len(failed_steps)) + "步"
        else:
            status = "failed"
            summary = failed_steps[0].get("error", "执行失败")

        return {
            "summary": summary,
            "status": status,
            "steps": self.steps,
        }
