# VeyaShip 项目约定

## 项目定位
跨境电商 AI SaaS 平台。面向**跨境卖家**（非技术用户），所有功能必须开箱即用，无需配置 API Key、env 文件、服务器等。

## 技术栈
- **后端**: Python 3.12+ / FastAPI / SQLAlchemy 2.0 async / asyncpg / JWT / DeepSeek API / 阿里云通义万相(DashScope) / Replicate(降级) / LangChain+LangGraph
- **前端**: React 18 + TypeScript + Vite 5 + Tailwind CSS 3.4 + Shadcn/ui + Zustand + TanStack React Query + react-i18next
- **数据库**: PostgreSQL（生产）/ SQLite（开发，USE_SQLITE=true）
- **基础设施**: Docker + docker-compose / Nginx

---

## 目录结构

```
crossborder-ai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口，注册路由
│   │   ├── core/
│   │   │   ├── config.py         # pydantic-settings 环境变量
│   │   │   ├── database.py       # 异步数据库引擎 + 会话
│   │   │   └── security.py       # JWT + bcrypt
│   │   ├── models/               # SQLAlchemy 数据模型
│   │   ├── schemas/              # Pydantic 请求/响应校验
│   │   ├── routers/              # API 路由（按功能分文件）
│   │   ├── services/             # 业务逻辑层
│   │   │   ├── ai/               # AI 服务（DeepSeek / 通义万相 / Replicate 降级 / RAG / Agent）
│   │   │   ├── crawler/          # 爬虫服务（1688 / Shopify）
│   │   │   ├── scraper.py        # 1688 抓取核心
│   │   │   └── ...
│   │   └── dependencies.py       # FastAPI 依赖注入（鉴权）
│   ├── migrations/               # Alembic 数据库迁移
│   └── tests/                    # pytest 测试
├── frontend/
│   ├── src/
│   │   ├── api/                  # Axios API 客户端
│   │   ├── components/
│   │   │   ├── ui/               # Shadcn UI 组件
│   │   │   └── layout/           # 布局组件（Sidebar / Header / RootLayout）
│   │   ├── pages/                # 页面组件（按功能分文件夹）
│   │   ├── stores/               # Zustand 状态管理
│   │   ├── types/                # TypeScript 类型定义
│   │   ├── utils/                # 工具函数 / 主题配置
│   │   ├── i18n/                 # 多语言翻译
│   │   └── lib/ai/               # AI Prompt 构建工具
│   ├── tailwind.config.js
│   └── vite.config.ts
└── docker-compose.yml
```

---

## 后端编码规范

### API 路由
- 所有路由在 `routers/` 下按功能分文件
- 路由 prefix 统一：`/auth`、`/products`、`/content`、`/settings` 等
- 在 `main.py` 注册：`app.include_router(xxx.router, prefix=API_PREFIX)`
- 每个路由函数必须有类型注解和 docstring（中文）
- 错误返回：统一用 `HTTPException`，中文错误信息

### 数据模型
- 主键用 UUID（`uuid.uuid4`）
- 时间戳用 `server_default=func.now()`，不用 Python 生成
- 每新增模型要在 `models/__init__.py` 注册
- 模型字段要加中文注释

### 数据库操作
- 通过 `Depends(get_db)` 获取会话
- 查询用 `await db.execute(select(...))`
- 写入用 `db.add(obj)` + `await db.flush()`
- 事务自动管理：`get_db` 成功 commit，失败 rollback
- 并发扣减用 `select_for_update()` 行级锁

### API 设计原则
- **服务商配置**：DeepSeek / 阿里云通义万相 / Onebound 等 API Key 由平台配置，用户无感知
- **错误信息**：对终端用户展示中文、可理解的提示，不暴露技术细节
- **积分系统**：每次 AI 生成 / 抓取消耗 1 积分

---

## 前端编码规范

### React 组件
- 页面组件放在 `pages/{功能名}/PageName.tsx`
- UI 组件放在 `components/ui/`
- 布局组件放在 `components/layout/`
- 使用函数组件 + TypeScript

### 状态管理
- 全局状态用 Zustand（`stores/`）
- 服务端状态用 TanStack React Query（useQuery / useMutation）
- API 调用封装在 `api/` 目录

### 样式
- Tailwind CSS 类名优先
- 主题色通过 CSS 变量控制，不硬编码颜色值
- 组件使用 Shadcn/ui 基础组件（Button / Card / Input 等）

### 多语言
- 使用 `react-i18next` + `useTranslation()`
- 所有用户可见文本使用 `t('key')`，不硬编码中文或英文
- 翻译文件在 `i18n/locales/{lang}.json`

---

## 功能模块清单（F1-F9）

| 模块 | 路由 | 说明 |
|------|------|------|
| F1 Canvas | `/dashboard` | 仪表盘，中央输入框，积分显示 |
| F2 Refinery | `/products/scrape` + `/content/generate` | 1688 抓取 + DeepSeek 文案生成 |
| F3 Generator | `/images/generate` | 通义万相文生图（FLUX 降级） |
| F4 Batch | `/batch/*` | CSV 批量任务 |
| F5 Persona | `/settings/persona` | 品牌调性配置 |
| F6 Radar | `/radar/scrape` | 竞品分析 |
| F7 Concierge | `/shopify/orders` + `/shopify/auto-refund` | Shopify 订单 + 自动退款 |
| F8 Publisher | `/shopify/*` + compliance | Shopify OAuth + 发布 + 合规审查 |
| F9 Ledger | `/ledger/calculate` | 净利计算 |

---

## 最近进展（2026-08）

- **整店巡检闭环**：定时巡检 + 手动巡检 + 看板展示
- **ReAct + Function Calling Agent** + **Self-reflection agent 4.2**（`backend/app/services/ai/`）
- **Store health check closed loop**：店铺健康检查闭环
- **登录/注册 401 修复**、**前端构建改 vite build**、**GitHub Actions deploy.yml 部署**

> 与 i面试 共享阿里云服务器，nginx 路径隔离：crossborder 用 `/`、`/api/`，i面试 用 `/interview/`。改 nginx 前必须确认不劫持对方路径。

## 关键规则

1. **不要提 `.env`、`backend/`、API Key 给终端用户看** — 用户是跨境卖家，不是开发者
2. **实现后必须功能测试** — 不能只看编译通过
3. **改 bug 要先说原因再修** — 说明 root cause 再改代码
4. **所有用户可见文案用中文** — 系统提示、错误信息等
5. **API Key 通过网页设置页面配置** — 不改文件，不重启服务
