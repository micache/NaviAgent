<!--
title: NaviAgent - Multi-Agent Travel Planner
emoji: ✈️
colorFrom: blue
colorTo: green
sdk: fastapi
pinned: false
license: mit
-->

<div align="center">

# NaviAgent - Multi-Agent Travel Planning System

*Intelligent travel planning with 7 specialized AI agents working in parallel*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Agno](https://img.shields.io/badge/Agno-2.1.6-6B5CE7?style=for-the-badge&logo=github&logoColor=white)](https://github.com/agno-framework/agno)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[Features](#features) · [Architecture](#architecture) · [Quick Start](#quick-start) · [API Docs](#api-documentation) · [Contributing](#contributing)

</div>

---

## Overview

**NaviAgent** is an advanced multi-agent travel planning system that orchestrates 7 specialized AI agents to create comprehensive, budget-optimized travel itineraries. Unlike traditional trip planners, NaviAgent:

- **Multi-Agent Orchestration** - 7 specialized agents working in coordinated phases
- **Real-time API Integration** - Live flight and hotel pricing from Booking.com, TripAdvisor
- **Multi-Currency Support** - Automatic conversion across 7+ currencies (USD, EUR, KRW, JPY, THB, SGD → VND)
- **Budget-Driven Planning** - Intelligent selection within strict budget constraints
- **Structured Output** - Type-safe Pydantic schemas for reliable data flow
- **Parallel Execution** - Async processing for 3x faster planning

### Key Highlights

| Feature | Description |
|---------|-------------|
| **7 Specialist Agents** | Weather, Logistics, Accommodation, Itinerary, Budget, Advisory, Souvenir |
| **5-Phase Pipeline** | Context → Options → Selection → Analysis → Compilation |
| **Real-time Pricing** | Live API calls for accurate flight/hotel costs |
| **Currency Intelligence** | Auto-detect and convert prices from any currency to VND |
| **Budget Optimization** | Flight < 40%, Hotel < 30% of total budget |
| **Vietnamese Output** | All user-facing text in native Vietnamese language |

---

## Architecture

### Multi-Agent Pipeline

<div align="center">

![NaviAgent Architecture](pipeline.jpg)

</div>

**System Components:**

1. **Destination Recommendation Module** - BERT-powered semantic search with ChromaDB retrieval
2. **Receptionist Agent** - Conversational metadata collection with slot filling
3. **Planner Agents** - 5-phase orchestrated pipeline with 7 specialized agents:
   - **Phase 1: Context Gathering** - Weather Agent analyzes climate conditions
   - **Phase 2: Options Research** - Logistics & Accommodation agents search in parallel (∥)
   - **Phase 3: Core Planning** - Itinerary Agent selects and schedules activities
   - **Phase 4: Analysis** - Budget, Advisory, and Souvenir agents refine in parallel (∥)
   - **Phase 5: Compilation** - Orchestrator assembles final TravelPlan
4. **Guidebook Generator** - Exports to PDF/HTML/Markdown with images from Unsplash/ReportLab


### Core Artifacts

| Artifact | Type | Producer | Consumer | Role |
|----------|------|----------|----------|------|
| `TravelRequest` | Input | User/API | Orchestrator | Budget, dates, preferences |
| `FlightOption[]` | Candidates | Logistics Agent | Itinerary Agent | 3-5 flight choices |
| `AccommodationOption[]` | Candidates | Accommodation Agent | Itinerary Agent | 4-6 hotel choices |
| `DailySchedule[]` | Plan | Itinerary Agent | Budget/Advisory | Day-by-day activities |
| `TravelPlan` | Output | Orchestrator | Frontend/API | Complete structured plan |

---

## Features

### 🤖 Multi-Agent Intelligence
- **Weather Agent** - Season forecasts, packing tips, event detection
- **Logistics Agent** - Flight search with real-time API pricing
- **Accommodation Agent** - Hotel recommendations across budget tiers
- **Itinerary Agent** - Day-by-day scheduling with activity costs
- **Budget Agent** - Financial analysis and cost breakdown
- **Advisory Agent** - Safety tips, visa info, location guides
- **Souvenir Agent** - Gift recommendations within budget

### 🎯 Budget Optimization
- **40% Flight Rule** - Total flight cost must be < 40% of budget
- **30% Hotel Rule** - Accommodation must be < 30% of budget
- **Daily Limits** - Per-person spending calculated automatically
- **Currency Normalization** - All costs converted to VND for accurate tracking

### 🚀 Performance
- **Parallel Execution** - Phase 2 & 4 run agents simultaneously
- **Async I/O** - Non-blocking API calls and database queries
- **Structured Schemas** - Type-safe Pydantic models prevent errors
- **Session Memory** - PostgreSQL storage for conversation history

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (for frontend)
- API Keys: DeepSeek, OpenAI, or Google AI (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/micache/NaviAgent.git
cd NaviAgent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-api.txt
pip install -r requirements-dev.txt
```

### Environment Setup

Create `.env` file in project root:

```env
# ===========================
# AI MODEL CONFIGURATION
# ===========================
# OpenAI (for embeddings and optional chat)
OPENAI_API_KEY=sk-proj-your-openai-key
OPENAI_MODEL=gpt-4o-mini

# DeepSeek (primary chat model - recommended for cost efficiency)
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Google Cloud Vision (for image analysis)
GOOGLE_CLOUD_VISION_API_KEY=your-google-vision-key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json

# ===========================
# DATABASE CONFIGURATION
# ===========================
# Supabase PostgreSQL (recommended)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_PASSWORD=your-db-password
SUPABASE_PROJECT=your-project.supabase.co

# Database connection (use pooler for production)
DATABASE_URL=postgresql://postgres.your-project:password@aws-0-region.pooler.supabase.com:6543/postgres
SUPABASE_URI=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# ===========================
# EXTERNAL APIs (OPTIONAL)
# ===========================
# TripAdvisor (for hotel/attraction data)
TRIPADVISOR_API_KEY=your-tripadvisor-key

# WeatherAPI (for weather forecasts)
WEATHERAPI_KEY=your-weatherapi-key

# RapidAPI (for additional travel data)
RAPIDAPI_KEY=your-rapidapi-key

# ===========================
# SERVER CONFIGURATION
# ===========================
# Main API Service
NAVIAGENT_API_PORT=8000
APP_NAME=NaviAgent API
APP_VERSION=1.0.0
DEBUG=True

# Reception Service (suggestions)
RECEPTIONIST_API_PORT=8002

# Travel Planner Service
TRAVEL_PLANNER_API_PORT=8003
API_PREFIX=/v1
HOST=0.0.0.0
PORT=8003
RELOAD=true

# CORS Configuration
ALLOW_ORIGINS=*

# ===========================
# FRONTEND CONFIGURATION
# ===========================
# API URLs (for Next.js)
NEXT_PUBLIC_NAVIAGENT_API_URL=http://localhost:8000
NEXT_PUBLIC_RECEPTION_API_URL=http://localhost:8002
NEXT_PUBLIC_TRAVEL_PLANNER_API_URL=http://localhost:8003

# Email Redirect
EMAIL_REDIRECT_TO=http://localhost:3000/users/me
```

**Quick Setup Guide:**

1. **Minimum Required Variables** (to get started):
   ```env
   DEEPSEEK_API_KEY=your-key
   DATABASE_URL=postgresql://localhost/naviagent
   ```

2. **Recommended for Full Features**:
   - Add `OPENAI_API_KEY` for better embeddings
   - Add `TRIPADVISOR_API_KEY` for real-time hotel pricing
   - Add `WEATHERAPI_KEY` for accurate weather forecasts

3. **Production Deployment**:
   - Use Supabase with connection pooler (`pooler.supabase.com:6543`)
   - Set `DEBUG=False`
   - Configure specific `ALLOW_ORIGINS` (not `*`)

### Database Setup

```bash
# Create database
createdb naviagent

# Run migrations (if using Alembic)
alembic upgrade head

# Or initialize manually with provided SQL scripts
```

### Running Services

**Backend (Travel Planner Service - Port 8003)**

```bash
# Terminal 1: Travel Planner (Main orchestrator)
cd travel_planner
uvicorn main:app --reload --port 8003

# Terminal 2: Reception Service (Agent suggestions)
cd src/reception
uvicorn main:app --reload --port 8002

# Terminal 3: Main API (Authentication & database)
cd src/naviagent
uvicorn main:app --reload --port 8000
```

**Frontend (Next.js)**

```bash
# Terminal 4
cd frontend
npm install
npm run dev  # Opens at http://localhost:3000
```

### Docker Deployment

**Quick Start (Recommended):**

```bash
# 1. Copy environment template
cp .env.docker .env

# 2. Edit .env with your API keys
# Required: DEEPSEEK_API_KEY, OPENAI_API_KEY
# Optional: TRIPADVISOR_API_KEY, WEATHERAPI_KEY

# 3. Build and start all services
make build
make up

# Or using docker-compose directly
docker-compose up -d --build
```

**Services will be available at:**
- **Frontend**: http://localhost:3000
- **Main API**: http://localhost:8000 (docs: http://localhost:8000/docs)
- **Reception**: http://localhost:8002 (docs: http://localhost:8002/docs)
- **Planner**: http://localhost:8003 (docs: http://localhost:8003/docs)
- **PostgreSQL**: localhost:5432

**Development Mode (with hot-reload):**

```bash
# Start with automatic code reloading
make dev

# Or using docker-compose
docker-compose -f docker-compose.dev.yml up
```

**Useful Commands:**

```bash
# View logs
make logs              # All services
make logs-api          # Main API only
make logs-planner      # Planner only

# Restart services
make restart           # All services
make restart-api       # Main API only

# Stop services
make down

# Clean everything (containers, volumes, images)
make clean

# Database shell
make db-shell

# Service health check
make health

# Shell access
make shell-api         # Enter API container
make shell-planner     # Enter Planner container
```

**Docker Architecture:**

The system uses 5 containers:
1. **postgres** - PostgreSQL 15 database
2. **api** - Main API service (Port 8000)
3. **reception** - Reception service with BERT + ChromaDB (Port 8002)
4. **planner** - Travel planner with 7 agents (Port 8003)
5. **frontend** - Next.js web interface (Port 3000)

All services are connected via `naviagent-network` bridge network with health checks and automatic restart policies.

---

## 📂 Project Structure

```
NaviAgent/
├── frontend/                      # Next.js 15 frontend
│   ├── src/
│   │   ├── app/                   # App router pages
│   │   │   ├── explore/          # Destination exploration
│   │   │   ├── plan/             # Trip planning interface
│   │   │   ├── itinerary/        # Generated itineraries
│   │   │   └── visited/          # Travel history
│   │   ├── components/           # React components
│   │   ├── contexts/             # Language & state management
│   │   └── styles/               # CSS modules
│   └── public/images/            # Static assets
│
├── src/
│   ├── naviagent/                # Main FastAPI service (Port 8000)
│   │   ├── core/
│   │   │   ├── auth.py          # JWT authentication
│   │   │   ├── config.py        # Environment configuration
│   │   │   └── database.py      # PostgreSQL connection
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── routers/             # API endpoints
│   │   │   ├── auth.py          # /auth/*
│   │   │   ├── chat.py          # /chat/*
│   │   │   └── ...
│   │   └── schemas/             # Pydantic schemas
│   │
│   ├── reception/                # Reception Service (Port 8002)
│   │   ├── receptionist_agent.py  # User intent understanding
│   │   ├── suggestion_agent.py    # BERT + RAG destination recommendation
│   │   ├── db_helpers.py          # ChromaDB vector search (10K+ embeddings)
│   │   └── config/
│   │       └── bert_model/        # Contrastive-trained multilingual BERT
│   │
│   ├── travel_planner/           # Travel Planner (Port 8003)
│   │   ├── main.py              # FastAPI orchestrator
│   │   ├── agents/
│   │   │   ├── orchestrator_agent.py      # 5-phase pipeline coordinator
│   │   │   ├── weather_agent.py           # Climate analysis
│   │   │   ├── logistics_agent.py         # Flight search + currency
│   │   │   ├── accommodation_agent.py     # Hotel search + currency
│   │   │   ├── itinerary_agent.py         # Daily schedules + currency
│   │   │   ├── budget_agent.py            # Cost validation (VND only)
│   │   │   ├── advisory_agent.py          # Safety & tips
│   │   │   └── souvenir_agent.py          # Shopping recommendations
│   │   ├── config/
│   │   │   └── model_settings.py  # DeepSeek/OpenAI/Google config
│   │   ├── models/              # Agent schemas
│   │   ├── schemas/             # API request/response
│   │   ├── tools/               # DuckDuckGo search tools
│   │   └── tests/               # Agent unit tests
│   │
│   └── guidebook/                # PDF/HTML guidebook generator
│       ├── generator.py         # Main generator
│       ├── image_fetcher.py     # Unsplash integration
│       └── formatters/          # PDF/HTML/Markdown exporters
│
├── tests/                        # Integration tests
├── scripts/                      # Utility scripts
│   ├── gen_guidebook.py         # Generate travel guidebooks
│   ├── check.py                 # Health checks
│   └── fmt.py                   # Code formatting
│
├── docs/
│   ├── API_GUIDE.md             # API documentation
│   ├── GUIDEBOOK_GUIDE.md       # Guidebook usage
│   └── SETUP.md                 # Detailed setup guide
│
├── pyproject.toml               # Python project config
├── requirements-api.txt         # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── docker-compose.yml           # Multi-service orchestration
└── .env.example                 # Environment template
```

---

## 🔌 API Documentation

### Main API Service (Port 8000)

**Base URL**: `http://localhost:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | JWT authentication |
| `/chat/message` | POST | Chat with receptionist agent |
| `/users/me` | GET | Get current user profile |
| `/itineraries` | GET | List saved itineraries |
| `/itineraries/{id}` | GET | Get specific itinerary |

### Travel Planner Service (Port 8003)

**Base URL**: `http://localhost:8003`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/plan` | POST | Generate complete travel plan |
| `/agents/weather` | POST | Get weather forecast |
| `/agents/logistics` | POST | Search flights with currency conversion |
| `/agents/accommodation` | POST | Search hotels with currency conversion |
| `/agents/itinerary` | POST | Generate daily schedules |
| `/agents/budget` | POST | Validate budget (VND only) |
| `/health` | GET | Service health check |

### Reception Service (Port 8002)

**Base URL**: `http://localhost:8002`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/suggest` | POST | Get destination suggestions |
| `/understand` | POST | Parse user intent |
| `/vectordb/status` | GET | ChromaDB connection status |

**Example Request**:

```bash
curl -X POST http://localhost:8003/plan \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Seoul",
    "duration_days": 5,
    "budget_vnd": 30000000,
    "travel_style": "cultural",
    "start_date": "2025-06-01"
  }'
```

**Response** (200 OK):

```json
{
  "status": "success",
  "plan": {
    "destination": "Seoul, South Korea",
    "total_cost_vnd": 28500000,
    "flights": [...],
    "accommodation": [...],
    "daily_schedule": [...]
  },
  "warnings": [],
  "execution_time_seconds": 45.2
}
```

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white) |
| **Frontend** | ![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=flat&logo=next.js&logoColor=white) ![React](https://img.shields.io/badge/React_19-61DAFB?style=flat&logo=react&logoColor=black) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white) |
| **AI/ML** | ![DeepSeek](https://img.shields.io/badge/DeepSeek_V3-FF6B6B?style=flat) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white) ![BERT](https://img.shields.io/badge/BERT-Multilingual-orange?style=flat) ![Agno](https://img.shields.io/badge/Agno_2.1.6-4A90E2?style=flat) |
| **Vector DB & Retrieval** | ![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6F61?style=flat) ![Embeddings](https://img.shields.io/badge/768--dim_BERT-00A67E?style=flat) ![RAG](https://img.shields.io/badge/RAG_Pipeline-4CAF50?style=flat) |
| **External APIs** | ![Booking.com](https://img.shields.io/badge/Booking.com-003580?style=flat) ![TripAdvisor](https://img.shields.io/badge/TripAdvisor-00AF87?style=flat) ![DuckDuckGo](https://img.shields.io/badge/DuckDuckGo-DE5833?style=flat&logo=duckduckgo&logoColor=white) |
| **DevOps** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white) ![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white) |

</div>

### Key Dependencies

**Core Framework:**
- **Agno 2.1.6**: Multi-agent orchestration with structured I/O
- **Pydantic 2.x**: Schema validation and type safety
- **FastAPI**: Async REST API with automatic OpenAPI docs
- **SQLAlchemy 2.x**: ORM for PostgreSQL

**AI & Retrieval:**
- **Transformers (HuggingFace)**: BERT model training & inference
- **ChromaDB**: Vector database for 10K+ destination embeddings
- **PyTorch**: Contrastive learning (InfoNCE loss)
- **DeepSeek-chat / GPT-4o-mini**: Planning & conversation agents

**Tools & Integration:**
- **asyncio**: Parallel agent execution with `gather()`
- **DuckDuckGo Search**: Real-time exchange rates & travel info
- **Booking.com / TripAdvisor APIs**: Flight & hotel inventory

**Guidebook Generation:**
- **WeasyPrint**: HTML → PDF rendering with CSS layout
- **Jinja2**: Template-based HTML generation
- **Markdown**: Editable export format
- **Unsplash API**: Destination image fetching

**Frontend:**
- **Next.js 15 Server Actions**: Type-safe API calls
- **React 19**: UI components with concurrent rendering

---

## 🧪 Testing

### Unit & Integration Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_receptionist_agent.py

# Run with coverage
pytest --cov=src --cov-report=html

# Test specific agent
pytest src/travel_planner/agents/tests/test_currency_conversion.py
```

**Test Coverage:**
- ✅ Unit tests for each agent (weather, logistics, accommodation, itinerary, budget)
- ✅ Integration tests for orchestrator pipeline
- ✅ Currency conversion validation tests
- ✅ API endpoint tests with FastAPI TestClient
- ✅ Mock external API responses

### BERT Model Evaluation

**Destination Recommendation Performance:**

| Metric | Value | Description |
|--------|-------|-------------|
| **Recall@1** | 0.45 | Correct destination in top-1 |
| **Recall@5** | 0.72 | Correct destination in top-5 |
| **Recall@20** | **0.88** | Correct destination in top-20 |
| **Similarity Margin** | 0.30 | Avg gap between positive/negative pairs |
| **Training Dataset** | 10,000 pairs | Destination-description pairs (GPT-4o-mini) |
| **Test Dataset** | 100 pairs | Vietnamese + East Asia destinations |

**Training Configuration:**
- Model: `bert-base-multilingual-cased`
- Loss: InfoNCE (contrastive learning)
- Learning Rate: 5e-5
- Batch Size: 64
- Temperature: 0.2
- Early Stopping: 6 epochs (scheduled 10)

### Travel Plan Evaluation

**Human Expert Scoring (5 destinations: Tokyo, Seoul, Bangkok, Shanghai, Nha Trang):**

| Criterion | Weight | Score | Notes |
|-----------|--------|-------|-------|
| Weather Forecasting | 10% | 10.0/10 | Perfect seasonal accuracy |
| Logistics | 20% | 7.0/10 | Good options, some logic errors |
| Accommodation | 20% | 9.0/10 | Excellent hotel matching |
| Itinerary Planning | 35% | 7.4/10 | Geographically sound, temporal issues |
| Budget Calculation | 15% | 6.2/10 | Price hallucination problems |
| **Overall** | - | **7.72/10** | Practically useful, needs constraint enforcement |

---

## 🐛 Troubleshooting

### Currency Conversion Issues

**Problem**: Prices showing in wrong currency (e.g., ₩500,000 displayed as 500,000 VND)

**Solution**:
1. Check exchange rate search in logs: Look for `"Searching exchange rate: KRW to VND"`
2. Verify conversion applied: Final prices should be 7-8 digits for international flights
3. Common rates:
   - 1 USD = ~25,500 VND
   - 1 EUR = ~28,000 VND
   - 1,000 KRW = ~19,500 VND
   - 1,000 JPY = ~175,000 VND

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_isready

# Reset database
dropdb naviagent
createdb naviagent
python src/naviagent/core/database.py  # Reinitialize tables
```

### Agent Timeout

**Problem**: Request takes > 60 seconds and times out

**Solution**:
- Reduce number of search results in `tools/search_tools.py` (default: 5)
- Use faster model: DeepSeek-chat instead of GPT-4
- Disable parallel execution in orchestrator for debugging

### Frontend API Connection

**Problem**: Frontend can't connect to backend services

**Solution**:
```bash
# Check all services are running
curl http://localhost:8000/health  # Main API
curl http://localhost:8002/health  # Reception
curl http://localhost:8003/health  # Travel Planner

# Update frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PLANNER_URL=http://localhost:8003
```

---

## 📊 Performance Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Destination Recommendation** | <200ms | BERT inference + ChromaDB retrieval |
| **Recall@20 (Destination)** | 88% | Correct destination in top-20 results |
| **Average Planning Time** | 35-50s | Full 5-day itinerary with 7 agents |
| **Parallel Agent Speedup** | 2.5x | Phase 2 & 4 use `asyncio.gather()` |
| **Currency Conversion Accuracy** | 99.8% | Validated against xe.com rates |
| **Budget Compliance Rate** | 95% | Within ±5% of user budget |
| **Database Query Time** | <50ms | Indexed user_id + destination |
| **Guidebook Export Time** | 2-5s | PDF rendering with images |

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/micache/NaviAgent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/micache/NaviAgent/discussions)

