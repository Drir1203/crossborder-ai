# VeyaShip - 项目上下文快照

> 生成时间: 2026-06-19
> 用户画像: **跨境卖家**（不懂技术、服务器、API，只关心功能能不能用）

---

## 项目定位

跨境 AI 辅助 SaaS 平台，帮助跨境卖家通过 AI 生成、优化、发布多平台商品 Listing。

## 技术栈

### 后端
Python 3.12+ / FastAPI / SQLAlchemy 2.0 async / asyncpg / Alembic / JWT (python-jose + passlib bcrypt) / DeepSeek API / 阿里云通义万相(DashScope) / Replicate FLUX(降级) / LangChain + LangGraph / Qdrant / httpx + BeautifulSoup + Playwright / APScheduler / pytest / curl_cffi

### 前端
React 18 + TypeScript + Vite 5 + Tailwind CSS 3.4 + Shadcn/ui + React Router v6 + Zustand + TanStack React Query + Axios + React Hook Form + Zod + Lucide React + Framer Motion + react-i18next + i18next-browser-languagedetector

### 基础设施
PostgreSQL 15 / Qdrant / Docker + docker-compose / Nginx

### 外部平台
Shopify REST API / Creem.io 支付 / Onebound 1688 数据接口

---

## 项目结构

```
crossborder-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI 入口，注册路由
│   │   ├── config.py                  # pydantic-settings 环境变量
│   │   ├── dependencies.py            # JWT 鉴权依赖
│   │   ├── database.py → core/database.py  # 异步数据库会话
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                # User: UUID, email, username, password_hash, credits, plan
│   │   │   ├── product.py             # Product: UUID, url, title, price, sales, shop_name, images
│   │   │   ├── system_config.py       # SystemConfig: key-value 系统配置
│   │   │   ├── content.py             # 内容生成记录 + 模板
│   │   │   ├── listing.py             # 多平台 Listing
│   │   │   └── payment.py             # 订阅 + 发票
│   │   ├── schemas/                   # Pydantic 校验
│   │   ├── routers/
│   │   │   ├── auth.py                # POST /register, /login, GET /me
│   │   │   ├── users.py               # GET /credits, POST /credits/deduct
│   │   │   ├── products.py            # POST /scrape, POST /manual, GET /, GET /{id}
│   │   │   └── settings.py            # GET/PUT /scraping (API Key 配置)
│   │   ├── services/
│   │   │   ├── scraper.py             # 1688 爬虫（Onebound API → curl_cffi → httpx）
│   │   │   ├── ai/                    # DeepSeek, 通义万相, Replicate 降级, RAG, LangGraph Agent
│   │   │   └── crawler/               # 网页爬虫 + Shopify
│   │   └── core/
│   │       ├── config.py              # Settings 类
│   │       ├── database.py            # async engine + session + init_db
│   │       └── security.py            # JWT + bcrypt
│   ├── tests/
│   ├── migrations/                    # Alembic 迁移
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/                       # Axios 客户端
│   │   ├── components/
│   │   │   ├── ui/                    # Shadcn 组件
│   │   │   └── layout/                # Sidebar, Header, RootLayout
│   │   ├── pages/
│   │   │   ├── auth/                  # Login, Register
│   │   │   ├── dashboard/             # Dashboard
│   │   │   ├── products/              # 1688 商品抓取 + 手动录入
│   │   │   └── settings/              # 系统设置（API Key 配置）
│   │   ├── stores/                    # Zustand
│   │   ├── types/                     # TypeScript 类型
│   │   ├── i18n/locales/              # 9 国语言翻译
│   │   └── utils/
│   ├── tailwind.config.js
│   └── vite.config.ts
├── docker-compose.yml
├── nginx/
└── README.md
```

---

## 数据模型

### User
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| email | String(255) | 唯一、索引 |
| username | String(100) | 可空、索引、显示用 |
| password_hash | String(255) | bcrypt 加密 |
| credits | Integer | 默认 100 |
| plan | String(50) | 默认 "free" |
| created_at | DateTime | |

### Product
| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| url | String(500) | 唯一、索引 |
| title | String(500) | 可空 |
| main_image_url | String(1000) | 可空 |
| price | Float | 可空 |
| sales_count | Integer | 可空 |
| shop_name | String(255) | 可空 |
| created_at / updated_at | DateTime | |

### SystemConfig
| 字段 | 类型 | 说明 |
|------|------|------|
| key | String(100) | 主键 |
| value | Text | |
| updated_at | DateTime | |

---

## API 接口

| 方法 | 路径 | 说明 | Day |
|------|------|------|-----|
| GET | /health | 健康检查 | 1 |
| POST | /api/v1/auth/register | 注册 | 1 |
| POST | /api/v1/auth/login | 登录 | 1 |
| GET | /api/v1/auth/me | 当前用户 | 2 |
| GET | /api/v1/users/credits | 查询积分 | 2 |
| POST | /api/v1/users/credits/deduct | 扣减积分（行级锁） | 2 |
| POST | /api/v1/products/scrape | 1688 自动抓取 | 3 |
| POST | /api/v1/products/manual | 手动录入 | 3 |
| GET | /api/v1/products | 商品列表（分页+搜索） | 3 |
| GET | /api/v1/products/{id} | 商品详情（10分钟缓存） | 3 |
| GET | /api/v1/settings/scraping | 查看爬虫配置 | 3 |
| PUT | /api/v1/settings/scraping | 保存爬虫配置 | 3 |

---

## 核心业务流程

### 1688 商品抓取（重点）

```
用户粘贴 1688 链接
    │
    ├─ Onebound API Key 已配置?
    │   ├─ 是 → 调用 Onebound 官方接口 → 返回结构化数据 ✅
    │   └─ 否 → 直连尝试（大概率被 1688 反爬拦截）
    │             → 提示用户「请在设置页面配置数据接口」
    │
    └─ 无论哪种方式失败 → 提供「手动录入」兜底
```

**服务商配置路径：** 设置页面 → 输入 Onebound API Key/Secret → 点保存 → 存入 DB → 立即生效
**用户使用路径：** 粘贴 1688 链接 → 点抓取 → 拿到数据

### 积分系统
- 注册赠送 100 积分
- `deduct_credits` 方法使用 `select_for_update()` 行级锁保证原子性
- 积分不足返回 400 + 中文提示

### 认证系统
- JWT HS256，过期 7 天
- 401 返回 `{"code": 401, "message": "未授权"}`

---

## 前端功能

### 已完成页面
| 页面 | 功能 |
|------|------|
| 登录 | email + password，Zod 校验 |
| 注册 | 两步注册，支持 username |
| 仪表盘 | 统计卡片、积分条、快捷操作 |
| 商品管理 | 1688 链接抓取、手动录入、列表、搜索、分页 |
| 设置 | Onebound API Key/Secret 配置表单 |

### 多语言
9 种语言：EN / ZH / JA / KO / ES / FR / DE / PT / RU
已翻译组件：登录、注册、侧边栏、顶栏、仪表盘

---

## 当前运行状态

```
Frontend: http://localhost:5173  ✅ 运行中
Backend:  http://localhost:8000  ✅ 运行中
Swagger:  http://localhost:8000/docs  ✅ 可用
Database: SQLite（开发模式）/ USE_SQLITE=False 时为 PostgreSQL
```

---

## 待办/可继续方向

- [ ] Day 4: 前端商品详情页完整版
- [ ] AI 文案生成接入 DeepSeek
- [x] AI 图片生成（阿里云通义万相 + FLUX 降级）
- [ ] Shopify 集成
- [ ] 支付系统 Creem.io
- [ ] RAG 知识库
- [ ] LangGraph 多步骤 Agent
- [ ] 生产环境 Docker 部署
