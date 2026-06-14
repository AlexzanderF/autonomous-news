# Autonomous News

**An LLM-Powered Autonomous News Platform** — Automatically discovers trending headlines, generates high-quality articles using LLMs, and publishes them to a modern frontend.

Built as a full-stack, production-ready system with Docker, FastAPI, Next.js, Celery, and Postgres. Perfect demonstration of end-to-end AI system engineering, async task orchestration, and modern web development.

## ✨ Features

### Backend (FastAPI + Python)
- **AI News Generation**: Powered by Google Gemini and Anthropic Claude via LangChain
- **Headline Discovery**: RSS scrapers + Tavily Search API for featured articles
- **Async Processing**: Celery workers with Redis broker + beat scheduler for periodic tasks
- **Database**: PostgreSQL with SQLAlchemy + Alembic migrations
- **API**: RESTful endpoints with pagination, filtering, and OpenAPI docs
- **Media Handling**: Thumbnail generation and storage (AVIF support)

### Frontend (Next.js 16)
- Modern React 19 + TypeScript + Tailwind CSS
- Server-side rendering and static optimization
- React Markdown rendering with custom components
- Recharts for data visualizations (e.g., economic calendar)
- Responsive design with clean UI

### Infrastructure
- Full **Docker Compose** setup (Nginx reverse proxy + SSL via Certbot)
- Multi-container architecture: API, Next.js, Postgres, Redis, Celery workers, Flower
- Production-ready deployment scripts
- Health checks and monitoring support

## 🛠 Tech Stack

- **Backend**: Python 3.13, FastAPI, SQLAlchemy, Celery, LangChain, Gemini/Claude/Tavily
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **Deployment**: Docker, Docker Compose, Nginx, Certbot
- **Other**: Alembic, Pydantic, Pillow, BeautifulSoup, Slugify

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys for:
  - Google Gemini (`GEMINI_API_KEY`)
  - Anthropic Claude (`ANTHROPIC_API_KEY`)
  - Tavily (`TAVILY_API_KEY`)

## 📁 Project Structure

```
autonomous-news/
├── backend/                    # FastAPI backend
│   ├── api/                    # API routes & main app
│   ├── db/                     # Models, migrations, CRUD
│   ├── news_generation_workers/# Celery tasks & LLM logic
│   └── services/               # Shared services
├── nextjs/                     # Next.js frontend
│   ├── app/                    # App Router pages
│   ├── components/             # Reusable UI components
│   └── services/               # API client
├── nginx/                      # Reverse proxy config
├── docker-compose.yml
├── deploy.sh
└── init-ssl.sh
```

## 🔄 How It Works

1. **Scheduled Tasks** (Celery Beat) → Pick trending headlines via RSS + Tavily
2. **AI Generation** → LLMs create full articles with key points, metadata, and thumbnails
3. **Storage** → Articles saved to PostgreSQL with status tracking
4. **Publishing** → Available via API and rendered beautifully on the Next.js frontend

## 🎯 Use Cases & Portfolio Highlights

- **Full-Stack AI Application**: Demonstrates complete ownership from data ingestion to user-facing product
- **Distributed Systems**: Celery + Redis task queue in production Docker setup
- **LLM Integration**: Multi-provider LangChain orchestration with prompt engineering
- **Modern Frontend**: Next.js 16 App Router, TypeScript, performant rendering

Great for showcasing skills in **AI Engineering**, **Backend Development**, **DevOps**, and **Full-Stack Development**.

## 🛣 Roadmap

- [ ] More LLM providers (OpenAI, Grok, etc.)
- [ ] User authentication & admin panel
- [ ] SEO optimization & sitemaps
- [ ] Analytics dashboard
- [ ] Newsletter / RSS output
- [ ] Multi-language support
