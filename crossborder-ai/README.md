# VeyaShip AI 🌐

> **AI-Powered Cross-Border Decision Engine**
>
> Tell AI what you want to sell — it analyzes the market, calculates profit, generates listings, and publishes to Shopify.

---

**中文介绍**

**VeyaShip AI** 是一个面向跨境电商卖家的 AI 决策引擎。输入品类名，AI 自动分析 Amazon 市场容量、竞争格局、利润空间。从"这个品能不能做"到生成 Listing 再到上架，一个平台完成。

**标语：这个品能不能做？AI 帮你做跨境决策。**

### 跟其他平台有什么不同？

| 维度 | VeyaShip AI | 其他同类工具 |
|------|------------|------------|
| **两种货源都支持** | 1688 抓取 + 自有商品 CSV 批量导入 | 大多只支持 1688，或只支持自有商品 |
| **合规审查** | 正则 + AI 双重检测违禁词 | ❌ 多数没有 |
| **利润计算器** | 输入售价成本自动算净利 | ❌ 多数没有 |
| **翻译对照** | 原文 vs 译文并排显示，质量可查验 | ❌ 只给译文 |
| **完整 Web UI** | 浏览器打开即用，不是 CLI 工具 | 竞品多是命令行/Skill 形式 |
| **AI 智能助手** | 说一句话执行多步操作 | 需手动逐页操作 |
| **一键工作流** | 粘贴链接 → 自动抓取 → 生成 → 发布 | 需切换多个页面 |
| **部署方式** | 浏览器直接使用，无需安装 | 部分需自建环境 |

### 核心能力

- **1688 商品抓取** — 粘贴链接，自动抓取商品信息
- **AI 生成 Listing** — 自动生成适配 Amazon/Shopify/eBay 的标题、描述、卖点
- **多语言翻译** — 支持 16 种语言，原文译文对照显示
- **合规审查** — 自动检测违禁词，避免下架罚款
- **利润计算** — 输入售价成本，自动算净利
- **一键发布** — AI 生成后直接发布到 Shopify
- **AI 智能助手** — 说一句话，自动执行多步操作
- **批量处理** — CSV 导入，批量 AI 生成和发布
- **A+ 内容生成** — AI 生成带 HTML 格式的丰富商品描述

> 适合两类卖家：
> - **1688 拿货卖家**：粘贴链接 → AI 抓取 → 生成 Listing → 上架
> - **自有货源卖家**：CSV 批量导入 → AI 生成 Listing → 上架

---

## 📋 Overview

VeyaShip AI is a SaaS platform that helps cross-border e-commerce sellers create, optimize, and publish product listings using AI. It supports **two sourcing modes**: 1688 product scraping and自有货源 (own inventory) CSV import.

### Core Features

- 🤖 **AI Listing Generation** — Generate titles, descriptions, bullet points, and SEO metadata for Amazon / Shopify / eBay
- 🖼️ **AI Image Generation** — Generate product images via Aliyun 通义万相 (¥0.02/image)
- 🌍 **Multi-Language Translation** — 16 languages with原文对照显示
- ✅ **Compliance Check** — Regex + AI double-layer banned word detection
- 💰 **Profit Calculator** — Calculate net profit and margin automatically
- 🏪 **Shopify Publishing** — One-click publish from AI-generated content
- 🗣️ **AI Agent** — Natural language instruction: "scrape this for me" / "calculate profit" / "publish to Shopify"
- 📦 **Batch CSV Import** — Bulk import products with AI-generated listings
- 📊 **A+ Content** — Generate rich HTML product descriptions
- 🔄 **Multi-Store Switching** — Switch between Shopify stores from the header
- 📈 **Workflow Templates** — One-click workflows: 1688→Shopify, 1688→Amazon, Scrape+List

---

## 🏗️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.12+ / FastAPI | REST API framework |
| SQLAlchemy 2.0 async + asyncpg | Async PostgreSQL ORM |
| Alembic | Database migrations |
| JWT (python-jose + bcrypt) | Authentication |
| DeepSeek V4 | LLM text generation |
| Aliyun 通义万相 / Replicate | AI image generation |
| LangGraph | Agent workflows |
| httpx + BeautifulSoup | Web scraping / 1688 data |
| pytest | Testing |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 + TypeScript | UI framework |
| Vite 5 | Build tool |
| Tailwind CSS 3.4 + Shadcn/ui | Styling & components |
| React Router v6 | Routing |
| Zustand | State management |
| TanStack React Query | Server state |
| Axios | HTTP client |
| Lucide React + Framer Motion | Icons & animations |

### Infrastructure
- **PostgreSQL 15** — Primary database
- **Nginx** — Reverse proxy + HTTPS
- **systemd** — Service management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15 (or SQLite for dev)

### 1. Clone & Setup
```bash
git clone https://github.com/Drir1203/crossborder-ai.git
cd crossborder-ai
cp .env.example .env  # Edit with your API keys
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Access
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📁 Project Structure

```
crossborder-ai/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, database, security, rate limiting
│   │   ├── models/         # SQLAlchemy models (11 tables)
│   │   ├── routers/        # API routes (auth, products, content, images, agent, batch, radar, ledger, shopify, settings, analytics)
│   │   └── services/
│   │       ├── ai/         # DeepSeek, Aliyun Image, Replicate, Agent, RAG
│   │       └── scraper.py # 1688 multi-tier scraper
│   ├── tests/              # 17+ pytest tests
│   └── migrations/         # Alembic migrations
├── frontend/
│   └── src/
│       ├── api/            # Axios API client
│       ├── components/     # UI & layout components
│       ├── pages/          # 12 pages (dashboard, products, content, images, agent, shopify, batch, radar, ledger, billing, settings, landing)
│       ├── stores/         # Zustand state (auth, store)
│       ├── i18n/           # 9-language i18n
│       └── utils/          # Themes, utilities
├── nginx/                  # Nginx config
├── deploy.sh               # One-click deployment script
├── docker-compose.prod.yml # Production Docker setup
└── .env.production         # Production environment template
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login & get JWT |
| GET | `/api/v1/auth/me` | Current user info |
| POST | `/api/v1/products/manual` | Create product manually |
| POST | `/api/v1/products/scrape` | Scrape 1688 product |
| GET | `/api/v1/products` | List products |
| DELETE | `/api/v1/products/{id}` | Delete product |
| POST | `/api/v1/products/batch-delete` | Batch delete products |
| POST | `/api/v1/content/generate` | AI generate listing |
| POST | `/api/v1/content/a-plus` | Generate A+ HTML content |
| POST | `/api/v1/images/generate` | Submit image generation (async) |
| GET | `/api/v1/images/status/{task_id}` | Poll image generation result |
| POST | `/api/v1/agent/run` | AI Agent (natural language) |
| POST | `/api/v1/agent/workflow` | Execute workflow template |
| GET | `/api/v1/agent/workflows` | List workflow templates |
| GET/POST | `/api/v1/agent/conversations` | Conversation management |
| GET | `/api/v1/analytics/dashboard` | Dashboard stats |
| GET | `/api/v1/analytics/insights` | AI business insights |
| POST | `/api/v1/ledger/calculate` | Profit calculation |
| POST | `/api/v1/shopify/push` | Push product to Shopify |
| GET | `/api/v1/shopify/orders` | List Shopify orders |
| POST | `/api/v1/shopify/compliance` | Compliance check |
| POST | `/api/v1/batch/upload` | Upload CSV batch |
| POST | `/api/v1/batch/process-ai` | Batch AI process |
| GET/PUT | `/api/v1/settings/persona` | Brand tone settings |

---

## 🤖 AI Features

### Listing Generation
- Product titles, descriptions & bullet points per platform (Amazon/Shopify/eBay/Etsy...)
- SEO meta data generation
- Multi-language translation (16 languages) with side-by-side comparison
- A+ Content (rich HTML descriptions)

### Image Generation
- Aliyun 通义万相 (preferred, ¥0.02/image)
- Replicate FLUX (fallback)
- Asynchronous task mode (submit → poll → result)

### AI Agent
- Natural language instruction: "scrape this product" / "calculate profit" / "generate listing"
- Conversation persistence with chat history
- Workflow templates: 1688→Shopify, 1688→Amazon, Scrape+List

### Business Tools
- Profit calculator (cost + fees + shipping → net profit)
- Compliance check (banned words detection)
- 1688 product scraper (API + direct fallback)
- Batch CSV import with AI processing

---

## 🚀 Production Deployment

### One-Click Deploy
```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

### Manual Deploy
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Configuration
Copy `.env.production` to `.env` and configure:
- `DEEPSEEK_API_KEY` — Required for AI generation
- `ALIYUN_DASHSCOPE_API_KEY` — For AI image generation (optional)
- `SHOPIFY_API_KEY` — For Shopify integration (optional)
- `POSTGRES_PASSWORD` — Database password
- `APP_URL` — Your domain

See `DEPLOYMENT_CHECKLIST.md` for detailed deployment steps.

---

## 📄 License
Private / Proprietary — All rights reserved.

---

## 📊 Feature Status

| Module | Status | Description |
|--------|--------|-------------|
| F1 Dashboard | ✅ | Business overview + quick actions |
| F1 AI Agent | ✅ | Natural language + workflow templates |
| F2 1688 Scraper | ✅ | Multi-tier scraping (API + direct) |
| F2 Listing Gen | ✅ | AI titles, descriptions, bullets, SEO |
| F3 Image Gen | ✅ | Aliyun 通义万相 / Replicate (async) |
| F4 Batch CSV | ✅ | Import + AI processing |
| F5 Brand Tone | ✅ | Per-user persona configuration |
| F6 Radar | ✅ | Multi-competitor comparison |
| F7 Shopify | ✅ | Orders, refunds, publishing |
| F8 Compliance | ✅ | Regex + AI double check |
| F9 Profit Calc | ✅ | Net profit & margin calculator |
| A+ Content | ✅ | Rich HTML descriptions |
| Multi-Language | ✅ | 16 languages with原文对照 |
| Multi-Store | ✅ | Shopify store switcher |
| Translations | ⚠️ | Partial (core pages done) |
| ICP Filing | ⏳ | Required for China servers |
