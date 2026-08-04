# VeyaShip 简历文档（AI 全栈岗）

> 面向岗位：AI 全栈 / AI 应用开发
> 更新：2026-08-04
> 定位：展示「一个人端到端交付 AI 产品的全链路能力」——AI 深度 + 工程广度 + 快速迭代

---

## 一、项目标题（Boss 字数安全版）

| 优先级 | 标题 | 字数* | 说明 |
|--------|------|-------|------|
| ⭐ 推荐 | `VeyaShip·跨境电商AI决策引擎` | 19 | 任何字段限制下都安全 |
| 备选 1 | `跨境电商 AI 决策引擎 VeyaShip` | 21 | 品牌放末尾，读起来更自然 |
| 备选 2 | `VeyaShip · 跨境电商 AI 决策引擎` | 23 | 带空格可读性最好，仅限限制较宽时 |

> *字数按「每个字母/汉字/符号 = 1 字」估算。Boss 直聘「项目经历」项目名称字段限制较严（约 20 字）；「作品集名称」官方限制 50 字。
> 若投递后标题显示被截断，改用更短一档。

---

## 二、主版本（完整描述）

```
【个人开源项目 / Side Projects】
▪️ VeyaShip·跨境电商AI决策引擎 (AI-Native 全栈应用)
▸ 技术栈：Python 3.12 / FastAPI / SQLAlchemy 2.0 async / LangGraph / DeepSeek API / 阿里云通义万相 / React 18 / TypeScript / Vite / TailwindCSS / Shadcn/ui / Zustand / PostgreSQL / Docker
▸ 核心亮点：
  • 自研 AI Agent 引擎：基于 DeepSeek Function Calling 实现 ReAct 推理循环（思考→调工具→观察→再思考），注册 9 个业务工具，LLM 自动决策工具调用链、多轮推理直至任务完成；失败自动降级 Plan-and-Execute 预设工作流（6 个模板），并预留 Qdrant 向量检索接口用于知识库增强。
  • 落地 4 个业务闭环 + 质检机制：选品决策、单品判断、合规自动修复（广告法违禁词正则 + LLM 双层检测，命中自动改写）、整店巡检（APScheduler 每日 2:30 无人值守定时巡检 + 手动触发 + 看板展示）；生成内容经 LLM 按完整性/平台适配/SEO/转化/合规 5 维评分，低于阈值自动重做。
  • 多模态 AI 能力：接入阿里云通义万相文生图（DashScope），异步任务式生成（提交即返 task_id，前端轮询结果，不阻塞请求），结合品牌调性做提示词工程，异常自动降级 Replicate FLUX；合规审查采用"正则 + LLM"双通道，一方失效自动降级。
  • 全栈工程交付：FastAPI + SQLAlchemy 2.0 async + PostgreSQL 后端，React 18 + TS + Vite + Shadcn/ui + Zustand + React Query 前端，9 语言 i18n、5 套主题、JWT 认证 + 积分系统；阿里云 2C2G 单机 Nginx 反向代理 + uvicorn(4 workers) + GitHub Actions CI/CD，全程 AI 辅助编程（Vibe Coding）快速迭代。
▸ 在线体验：https://veyaship.com（阿里云国内服务器，ICP 备案流程中，可用 IP http://47.116.138.61 访问，推荐 PC 端）
▸ 源码地址：github.com/Drir1203/crossborder-ai
```

---

## 三、精简版（投递 / 简历格子小时用）

```
▪️ VeyaShip·跨境电商AI决策引擎（AI-Native 全栈应用，个人独立开发）
技术栈：Python/FastAPI/SQLAlchemy async/LangGraph/DeepSeek/React 18/TS/Vite/Shadcn/ui/PostgreSQL/Docker
亮点：自研 ReAct + Function Calling AI Agent（9 工具自动规划，失败降级工作流）；落地选品/合规修复/整店巡检 4 个业务闭环 + LLM 5 维自检自动重做 + 每日定时无人值守巡检；接入阿里云通义文生图（FLUX 降级）；全栈独立交付前后端 + 阿里云部署 + GitHub Actions CI/CD。
线上：https://veyaship.com（备案中） 源码：github.com/Drir1203/crossborder-ai
```

---

## 四、面试准备要点（追问 → 回答 → 代码定位）

| 简历点 | 会被追问 | 对应代码 |
|--------|----------|----------|
| ReAct 推理循环 | 工具结果怎么回喂给模型？最多几轮？超了怎么办？ | `backend/app/services/ai/agent_orchestrator.py` `run_react` |
| 降级 Plan-and-Execute | 什么场景触发降级？ | `agent_orchestrator.py` `run` |
| 自我反思 | 评分标准怎么定的？低于阈值怎么处理？ | `agent_orchestrator.py` `_do_self_reflect` |
| 定时巡检 | 定时任务怎么实现？用户隔离怎么做？ | `backend/app/services/scheduler.py` `_run_store_checks` |
| LangGraph 条件回环 | 为什么用图？回环怎么触发？ | `backend/app/services/ai/agent.py` `_build_graph` |
| 部署 | 为什么 Nginx + uvicorn 4 workers 而不是 Docker？ | `DEPLOYMENT.md`（完整架构决策） |

---

## 五、诚实性备注（写简历和面试前必读）

1. **RAG 不要写成已交付能力**：`rag.py` 目前是占位实现（embedding 用假向量），路线图标注"待做"。想提就写「预留 Qdrant 向量检索接口」，面试时主动说"下一步接入 embedding 模型完善知识库"。
2. **备案状态**：域名 `veyaship.com` 备案中，备案通过前可用 IP `http://47.116.138.61` 访问——在线体验务必同时给出 IP，避免面试官打不开。
3. **多语言**：9 语言 i18n（含中英日德法西葡韩俄），不要写成全站完整翻译（部分页面仍为中文）。
