# NaviAgent

An intelligent multi-agent travel planning system that transforms travel planning from a tedious task into an effortless experience. Unlike traditional travel booking platforms with generic suggestions, this project addresses the unique challenges of:

- **Personalized itinerary generation** based on individual preferences and constraints
- **Real-time budget optimization** across flights, accommodations, and activities
- **Multi-agent collaboration** for comprehensive travel planning (logistics, advisory, souvenirs)
- **Session-based conversational AI** for natural travel consultation
- **Interactive 3D visualization** of visited destinations and travel history
- **Automated guidebook generation** with professional formatting and local insights

Using the Agno multi-agent framework with specialized travel agents, the system delivers end-to-end travel planning including flight bookings, hotel recommendations, daily itineraries, budget breakdowns, and safety advisories—all through natural conversation.

## Key Highlights

| Feature | Description |
|---------|-------------|
| **Multi-Agent Architecture** | Orchestrated specialist agents (Itinerary, Budget, Advisory, Logistics, Accommodation, Weather, Souvenir) working collaboratively |
| **Conversational Interface** | Natural language trip planning with session-based memory and context awareness |
| **Real-time Integration** | Live flight search, hotel availability, weather forecasts via external APIs |
| **Smart Recommendations** | AI-powered destination suggestions from text descriptions or uploaded images |
| **Interactive 3D Map** | Globe visualization of visited places with location tracking |
| **Professional Guidebooks** | Auto-generated HTML guidebooks with itineraries, budgets, and travel tips |
| **Multi-language Support** | Vietnamese and English interfaces with localized content |
| **Session Persistence** | Database-backed chat history and travel data management |

## Tech Stack

**Frontend:**
- Next.js 15 (React 19) with TypeScript
- Tailwind CSS for responsive design
- React-Globe for 3D map visualization
- Markdown rendering for rich content

**Backend:**
- FastAPI (Python) microservices architecture
- Agno framework for multi-agent orchestration
- PostgreSQL (Supabase) for session/memory storage
- External APIs: Amadeus (flights), Google Places, OpenWeatherMap, Unsplash

**AI/ML:**
- GPT-4 for intelligent agent responses
- CLIP for image-based destination matching
- Sentence transformers for semantic search

## Demo

### 🌍 Explore Page - AI-Powered Destination Discovery
Intelligent destination recommendations based on text descriptions or image uploads. Features interactive chat with travel assistant and beautiful destination galleries.

![Explore Page](images/anh1.jpg)

### 📝 Travel Journal - 3D Globe Visualization
Track and visualize your travel history on an interactive 3D globe. Add visited destinations and relive your journey with location markers.

![Travel Journal](images/anh2.jpg)

### 🗓️ Trip Planning - Multi-Agent Conversation
Natural language trip planning with AI agents. Collaborate with specialist agents for itinerary, budget, logistics, and accommodation recommendations.

![Trip Planning](images/anh3.jpg)

### 📚 Auto-Generated Guidebook
Professional travel guidebooks with complete itineraries, budget breakdowns, flight options, hotel recommendations, and local tips—all automatically generated.

![Guidebook](images/anh4.jpg)

## Features

- 🎨 **Code Style**: Automated formatting with Black and isort
- 🔍 **Linting**: Comprehensive checking with Flake8 and plugins
- ✅ **Testing**: Unit tests with pytest and coverage reporting
- 🔐 **Security**: Security scanning with Bandit
- 📝 **Documentation**: Google-style docstring enforcement
- 🔄 **CI/CD**: Automated checks with GitHub Actions
- 🪝 **Pre-commit Hooks**: Automated checks before every commit

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/micache/NaviAgent.git
cd NaviAgent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

### Code Style

```bash
# Format code
black --line-length 100 .
isort --profile black --line-length 100 .

# Check code style
flake8 . --max-line-length=100
mypy --ignore-missing-imports .

# Run all pre-commit hooks
pre-commit run --all-files
```

## Documentation

- [Development Setup Guide](SETUP.md) - Detailed setup and usage instructions
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

## Code Quality Standards

This project adheres to:

- **Google Python Style Guide**
- **PEP 8** coding conventions
- **Type hints** for all functions
- **Google-style docstrings** for documentation
- **100% test coverage** goal

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

- ✅ Code style checks (Black, isort, Flake8)
- ✅ Unit tests with coverage (Python 3.8-3.12)
- ✅ Type checking (mypy)
- ✅ Security scanning (Bandit)
- ✅ Documentation checks (pydocstyle)

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.

## Run Local
# NaviAgent FastAPI server

```bash
cd src/naviagent
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Reception FastAPI server
```bash
cd src/reception
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

# Travel Planner FastAPI server

```bash
cd src/travel_planner
uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

# Frontend React server

```bash
cd frontend
npm install
npm start / npm run dev
```
