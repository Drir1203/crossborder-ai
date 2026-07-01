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
