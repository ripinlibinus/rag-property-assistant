# RAG Property Search Assistant

> Hybrid RAG System for Real Estate Property Search - Thesis Project

## Overview

A production-ready AI assistant for real estate property search, using a **hybrid RAG (Retrieval-Augmented Generation)** approach that combines structured API filtering with semantic vector search. The system achieves **100% accuracy** in evaluation tests.

### Key Results

| Method | Accuracy | F1 Score | Description |
|--------|----------|----------|-------------|
| **Hybrid** | 100% | 1.00 | API filtering + semantic re-ranking |
| API-only | 73.33% | 0.73 | Structured filters only |
| Vector-only | 56.67% | 0.57 | Semantic search only |

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    ReAct Agent                          │
│  (LLM decides which tool to call, observes, repeats)   │
└─────────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐      ┌──────────────┐     ┌──────────────┐
│  Tools  │      │   Hybrid     │     │   Memory     │
│         │      │   Search     │     │   (SQLite)   │
│ - search│      │              │     │              │
│ - nearby│      │ API + Vector │     │ Multi-turn   │
│ - POIs  │      │  Re-ranking  │     │ Conversation │
└─────────┘      └──────────────┘     └──────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
┌──────────────┐               ┌──────────────┐
│ Property API │               │   ChromaDB   │
│  (Filters)   │               │  (Semantic)  │
└──────────────┘               └──────────────┘
```

### Search Methods

1. **Hybrid (Recommended)**: Combines structured API filters with semantic re-ranking
2. **API-only**: Uses database filters for exact matches
3. **Vector-only**: Pure semantic search for vague queries

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend)
- Docker (optional, for containerized deployment)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/rag-property-search.git
cd rag-property-search

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the API
uvicorn api.main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api
```

## API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/methods` | Available search methods |
| POST | `/api/v1/chat` | Main chat endpoint |
| POST | `/api/v1/chat/stream` | Streaming chat (SSE) |
| GET | `/docs` | Swagger UI |

### Chat Request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Cari rumah 3 kamar di medan harga di bawah 2M",
    "session_id": "user-123",
    "method": "hybrid"
  }'
```

### Response

```json
{
  "response": "Berikut 5 rumah di Medan dengan 3 kamar dan harga di bawah 2M:\n\n1. Rumah Minimalis Cemara Asri...",
  "properties": [...],
  "session_id": "user-123",
  "metadata": {
    "total_found": 15,
    "returned": 5,
    "method_used": "hybrid",
    "has_more": true
  }
}
```

## Project Structure

```
rag-property-search/
├── api/                    # FastAPI application
│   ├── main.py            # App entry point
│   ├── config.py          # Settings management
│   ├── dependencies.py    # Dependency injection
│   ├── routers/           # API routes
│   │   ├── chat.py
│   │   └── health.py
│   └── schemas/           # Pydantic models
│       ├── request.py
│       └── response.py
├── src/                    # Core source code
│   ├── agents/            # ReAct agent implementation
│   │   ├── react_agent.py
│   │   └── tools.py
│   ├── adapters/          # Data source adapters
│   │   └── metaproperty.py
│   ├── knowledge/         # Vector stores & search
│   │   ├── hybrid_search.py
│   │   └── property_store.py
│   └── memory/            # Chat memory
│       └── sqlite_memory.py
├── frontend/              # Vue 3 + Vite frontend
│   ├── src/
│   │   ├── App.vue
│   │   └── components/
│   └── package.json
├── data/
│   ├── chromadb/          # Vector database
│   ├── knowledge-base/    # RAG knowledge documents
│   └── gold/              # Evaluation test data
├── docs/                   # Documentation
├── scripts/               # Utility scripts
├── Dockerfile             # Production Docker image
├── docker-compose.yml     # Docker Compose config
└── requirements.txt       # Python dependencies
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `OPENAI_MODEL` | No | Model name (default: gpt-4o-mini) |
| `METAPROPERTY_API_URL` | Yes | Property data API URL |
| `METAPROPERTY_API_TOKEN` | No | API authentication token |
| `CHROMA_PERSIST_DIRECTORY` | No | ChromaDB data path |
| `DATABASE_PATH` | No | SQLite database path |
| `CORS_ORIGINS` | No | Allowed CORS origins |
| `LOG_LEVEL` | No | Logging level (INFO/DEBUG) |

## Features

### Multi-language Support
- Indonesian queries: "cari rumah di cemara asri medan"
- English queries: "find house near Central Park"
- Mixed: "rumah 3 bedroom harga below 2M"

### Smart Search Capabilities
- **Location-based**: "rumah di ringroad medan"
- **Proximity search**: "apartemen dekat USU"
- **POI discovery**: "rumah dekat mall" (discovers malls first)
- **Filter combinations**: "ruko 2 lantai harga 500jt-1M"

### Conversation Memory
- Multi-turn conversations with context
- Session-based chat history
- Pagination: "ada lagi?" / "show more"
- Filter refinement: "yang 3 kamar"

## Evaluation

The system was evaluated using 30 test queries covering:
- Location searches
- Price filtering
- Property type filtering
- Proximity searches
- Multi-constraint queries

### Results Summary

```
┌─────────────┬──────────┬────────────┬───────────┐
│ Method      │ Accuracy │ Precision  │ Recall    │
├─────────────┼──────────┼────────────┼───────────┤
│ Hybrid      │ 100.00%  │ 1.00       │ 1.00      │
│ API-only    │ 73.33%   │ 0.73       │ 0.73      │
│ Vector-only │ 56.67%   │ 0.57       │ 0.57      │
└─────────────┴──────────┴────────────┴───────────┘
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/

# Evaluation
python scripts/evaluate_v2.py --method hybrid
```

### Syncing Property Data

```bash
# Sync from MetaProperty API
python scripts/sync_properties.py

# Ingest knowledge base
python scripts/ingest_knowledge.py
```

## Deployment Options

### Docker (Recommended)

```bash
# Production
docker-compose up -d

# Development with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Manual Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (production)
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Citation

If you use this project for academic purposes:

```bibtex
@thesis{rag-property-search,
  title={Hybrid RAG System for Real Estate Property Search},
  author={Your Name},
  year={2026},
  institution={Your Institution}
}
```

---

*Thesis Project - RAG Property Search Assistant*
