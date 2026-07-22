# VeyaShip 🌐

> **AI-Powered Cross-Border E-Commerce Platform**
>
> Generate, optimize, and publish multi-platform product listings with AI.

---

## 📋 Overview

VeyaShip is a SaaS platform that helps cross-border e-commerce sellers create compelling, localized product listings using AI. It leverages **DeepSeek LLM** for content generation, **FLUX** for AI image generation, and **LangGraph** for multi-step agent workflows.

### Core Features

- 🤖 **AI Content Generation** — Product titles, descriptions, bullet points, and SEO metadata
- 🖼️ **AI Image Generation** — Generate product images via Replicate FLUX
- 🌍 **Multi-Platform** — Amazon, Shopify, eBay, Etsy, Walmart, Shopee, Lazada
- 🔄 **Translation & Localization** — 10+ language support
- 📊 **RAG Knowledge Base** — Qdrant vector database for brand-aware content
- 🏪 **Shopify Integration** — Import products, sync listings bi-directionally
- 📈 **Analytics Dashboard** — Track usage, credits, and platform performance
- 💳 **Subscription Billing** — Creem.io payment integration

---

## 🏗️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.11+ / FastAPI | REST API framework |
| SQLAlchemy 2.0 async + asyncpg | Async PostgreSQL ORM |
| Alembic | Database migrations |
| JWT (python-jose + bcrypt) | Authentication |
| DeepSeek API | LLM text generation |
| Replicate API | FLUX image generation |
| LangChain + LangGraph | RAG + Agent workflows |
| Qdrant | Vector database |
| httpx + BeautifulSoup + Playwright | Web scraping |
| APScheduler | Task scheduling |
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
| React Hook Form + Zod | Form validation |
| Lucide React + Framer Motion | Icons & animations |

### Infrastructure
- **PostgreSQL 15** — Primary database
- **Qdrant** — Vector search
- **Docker + docker-compose** — Containerization
- **Nginx** — Reverse proxy

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15
- Docker & docker-compose (optional)

### 1. Clone & Environment Setup

```bash
git clone <repo-url> crossborder-ai
cd crossborder-ai

# Backend environment
cp .env.example .env
# Edit .env with your API keys and database settings

# Frontend environment
cp frontend/.env.example frontend/.env
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Docker (Full Stack)

```bash
docker-compose up -d
```

Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Qdrant Dashboard**: http://localhost:6333

---

## 📁 Project Structure

```
crossborder-ai/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API routes
│   │   │   ├── auth.py           # Login, register, refresh
│   │   │   ├── users.py          # Profile management
│   │   │   ├── products.py       # Product CRUD
│   │   │   ├── listings.py       # Multi-platform listings
│   │   │   ├── content.py        # AI content generation
│   │   │   ├── images.py         # AI image generation
│   │   │   ├── payments.py       # Subscription & billing
│   │   │   └── analytics.py      # Dashboard analytics
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic settings
│   │   │   ├── database.py       # SQLAlchemy async engine
│   │   │   ├── security.py       # JWT & password hashing
│   │   │   └── deps.py           # FastAPI dependencies
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   ├── deepseek.py   # DeepSeek LLM client
│   │   │   │   ├── replicate.py  # FLUX image generation
│   │   │   │   ├── rag.py        # Qdrant vector search
│   │   │   │   └── agent.py      # LangGraph workflows
│   │   │   ├── crawler/
│   │   │   │   ├── scraper.py    # Web scraping
│   │   │   │   └── shopify.py    # Shopify REST API
│   │   │   ├── payment.py        # Creem.io integration
│   │   │   └── scheduler.py      # APScheduler tasks
│   │   └── main.py               # FastAPI application
│   ├── tests/
│   ├── alembic/                  # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                  # API client & services
│   │   ├── components/
│   │   │   ├── ui/               # Shadcn UI components
│   │   │   └── layout/           # App layout (sidebar, header)
│   │   ├── pages/
│   │   │   ├── auth/             # Login & Register
│   │   │   ├── dashboard/        # Dashboard
│   │   │   └── ...               # Other pages
│   │   ├── stores/               # Zustand state
│   │   ├── types/                # TypeScript types
│   │   └── utils/                # Utilities
│   ├── Dockerfile
│   └── nginx.conf
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
└── .env.example
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login & get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Current user info |
| GET/PUT | `/api/v1/users/profile` | User profile |
| GET/POST | `/api/v1/products` | Product CRUD |
| GET/POST | `/api/v1/listings` | Listing CRUD |
| POST | `/api/v1/content/generate` | AI content generation |
| POST | `/api/v1/images/generate` | AI image generation |
| GET | `/api/v1/analytics/dashboard` | Dashboard stats |
| GET | `/api/v1/payments/plans` | Subscription plans |
| POST | `/api/v1/payments/create-checkout` | Checkout session |

---

## 🤖 AI Features

### Content Generation
- Product titles & descriptions optimized per platform
- SEO meta data generation
- Multi-language translation & localization
- A/B testing variations

### Image Generation
- FLUX model via Replicate API
- Product photography with customizable styles
- Background removal & replacement (coming soon)

### RAG Knowledge Base
- Brand voice & guideline preservation
- Product catalog context
- Market-specific terminology

### Agent Workflows (LangGraph)
- **ListingAgent**: End-to-end listing creation pipeline
  - Product analysis → Title generation → Description → Bullet points → SEO → Image → Review

---

## 🔒 Security

- JWT-based authentication with access/refresh token rotation
- Passwords hashed with bcrypt
- CORS configured for frontend origins
- SQLAlchemy parameterized queries (no SQL injection)
- Environment-based configuration (no hardcoded secrets)

---

## 📄 License

Private / Proprietary — All rights reserved.

---

## 🛠️ Development Roadmap

- [x] Project structure & configuration
- [x] Database models & migrations
- [x] Authentication system
- [x] Product & Listing CRUD
- [x] AI content generation (DeepSeek)
- [x] AI image generation (FLUX)
- [x] RAG with Qdrant
- [x] LangGraph agent workflows
- [x] Shopify integration
- [x] Frontend foundation
- [x] Docker setup
- [ ] Frontend product pages
- [ ] Frontend listing pages
- [ ] Frontend AI content UI
- [ ] Payment integration
- [ ] Testing suite
- [ ] Production deployment
- [ ] Frontend batch processing UI
- [ ] Frontend competitor analysis UI
- [ ] Frontend profit calculator UI

---

## 🚀 Production Deployment

### Prerequisites

| 需求 | 推荐方案 | 费用 |
|------|---------|------|
| **服务器** | Ubuntu 22.04+, 2核4G, 50GB SSD | ~$12-24/月 (DigitalOcean) 或 ¥68/月 (阿里云) |
| **域名** | 任意域名 | ~¥50-80/年 |
| **DeepSeek API Key** | [platform.deepseek.com](https://platform.deepseek.com) | 按量计费，新用户送额度 |
| **Replicate API Key** | [replicate.com](https://replicate.com/account/api-tokens) | 按量计费 |

### 推荐服务器配置

| 规模 | CPU | 内存 | 存储 | 月流量 | 参考价格 |
|------|-----|------|------|--------|---------|
| 入门（个人卖家） | 2核 | 4G | 50GB | 2TB | ~$12/月 |
| 标准（小团队） | 4核 | 8G | 100GB | 4TB | ~$24/月 |
| 高负载（企业） | 8核 | 16G | 200GB | 8TB | ~$48/月 |

### 部署步骤

#### 1️⃣ 服务器初始化

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 更新系统
apt update && apt upgrade -y

# 安装 Git
apt install -y git

# 安装 Docker（一步脚本）
curl -fsSL https://get.docker.com | bash
```

#### 2️⃣ 获取代码

```bash
git clone https://github.com/你的仓库/crossborder-ai.git /opt/veyaship
cd /opt/veyaship
```

#### 3️⃣ 一键部署

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

脚本会自动完成：
1. ✅ 安装 Docker + Docker Compose
2. ✅ 生成随机密钥（SECRET_KEY, JWT_SECRET_KEY）
3. ✅ 申请 Let's Encrypt SSL 证书（需域名已指向服务器）
4. ✅ 构建 Docker 镜像并启动所有服务
5. ✅ 健康检查确认服务正常

#### 4️⃣ 手动配置（如果一键脚本走到一半停了）

```bash
# 编辑环境变量
nano /opt/veyaship/.env
# 填入：APP_URL, BACKEND_CORS_ORIGINS, DEEPSEEK_API_KEY, REPLICATE_API_KEY, POSTGRES_PASSWORD

# 修改 Nginx 域名
sed -i 's/example.com/你的域名.com/g' /opt/veyaship/nginx/nginx.conf

# 启动服务
cd /opt/veyaship
docker compose -f docker-compose.prod.yml up -d
```

### 服务管理

```bash
# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend

# 重启服务
docker compose -f docker-compose.prod.yml restart backend

# 更新到最新版本
cd /opt/veyaship
git pull
docker compose -f docker-compose.prod.yml up -d --build

# 停止所有服务
docker compose -f docker-compose.prod.yml down

# 停止并删除数据（⚠️ 会丢数据！）
docker compose -f docker-compose.prod.yml down -v
```

### 数据库备份

```bash
# 手动备份
docker exec crossborder-postgres pg_dump -U crossborder crossborder_ai > backup_$(date +%Y%m%d).sql

# 定时备份（每天凌晨 3 点）
(crontab -l 2>/dev/null; echo "0 3 * * * docker exec crossborder-postgres pg_dump -U crossborder crossborder_ai > /opt/veyaship/backups/veyaship_\$(date +\\%Y\\%m\\%d).sql && find /opt/veyaship/backups -name '*.sql' -mtime +30 -delete") | crontab -
```

### 监控

```bash
# 健康检查
curl https://你的域名.com/health

# 查看容器资源占用
docker stats

# 查看 PostgreSQL 日志
docker compose -f docker-compose.prod.yml logs postgres
```

### 故障排查

| 问题 | 可能原因 | 解决 |
|------|---------|------|
| 502 Bad Gateway | 后端未启动 | `docker compose logs backend` |
| 413 Request Entity Too Large | 上传文件太大 | 检查 nginx.conf 的 `client_max_body_size` |
| 429 Too Many Requests | 触发了限流 | 等 1 分钟自动恢复 |
| SSL 证书过期 | Certbot 续期失败 | `certbot renew` 手动续期 |
| 数据库连不上 | PostgreSQL 未就绪 | `docker compose logs postgres` 确认健康检查通过 |
