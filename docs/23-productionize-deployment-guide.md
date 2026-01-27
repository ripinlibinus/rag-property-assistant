# Productionize & Deployment Guide

**Project:** RAG Property Search Assistant (Thesis)
**Created:** 26 January 2026
**Purpose:** Step-by-step guide for cleaning up codebase, creating production API, and deploying

---

## Overview

Setelah evaluasi selesai dengan hasil Hybrid 100% accuracy, langkah selanjutnya adalah:
1. Rapikan codebase (cleanup unused files, standardize structure)
2. Buat production-ready API dengan FastAPI
3. Publish ke GitHub dengan dokumentasi lengkap
4. Deploy ke cloud platform dengan demo URL

---

## Phase 1: Codebase Cleanup

### 1.1 Audit File Structure

**Prompt untuk Claude:**
```
Tolong audit struktur folder project Rag-Tesis ini:
1. Identifikasi file/folder yang tidak digunakan (archive, backup, test files)
2. Identifikasi file yang duplikat atau redundant
3. Buat rekomendasi struktur folder yang clean untuk production

Fokus pada:
- scripts/ folder - mana yang production vs development/testing
- data/ folder - mana yang perlu di-gitignore
- docs/ folder - mana yang relevan untuk thesis vs internal notes
```

### 1.2 Cleanup Tasks

**Files to Review:**
- [ ] `scripts/archive/` - pindahkan atau hapus
- [ ] `data/archive/` - pindahkan atau hapus
- [ ] `scripts/chat_*.py` - konsolidasi menjadi satu entry point
- [ ] File-file `*_test.py` atau `test_*.py` - pindahkan ke folder `tests/`
- [ ] `.env.example` - pastikan ada untuk reproducibility

**Prompt untuk Claude:**
```
Tolong rapikan codebase dengan:
1. Hapus/archive file-file yang tidak diperlukan untuk production
2. Buat folder structure yang standard:
   - src/ untuk source code
   - scripts/ untuk utility scripts
   - tests/ untuk test files
   - docs/ untuk dokumentasi
   - data/ untuk data files (dengan .gitignore yang proper)
3. Update import paths jika ada perubahan struktur
```

### 1.3 Dependencies Cleanup

**Prompt untuk Claude:**
```
Tolong buat requirements.txt atau pyproject.toml yang proper:
1. Scan semua import statements di codebase
2. Identifikasi dependencies yang sebenarnya digunakan
3. Pin version numbers untuk reproducibility
4. Pisahkan dev dependencies dari production dependencies
```

---

## Phase 2: Production API dengan FastAPI

### 2.1 API Design

**Target Endpoints:**
```
POST /api/v1/chat
  - Input: { "message": "...", "session_id": "...", "method": "hybrid" }
  - Output: { "response": "...", "properties": [...], "metadata": {...} }

GET /api/v1/health
  - Output: { "status": "ok", "version": "1.0.0" }

GET /api/v1/methods
  - Output: { "methods": ["vector_only", "api_only", "hybrid"] }
```

**Prompt untuk Claude:**
```
Buatkan FastAPI application untuk RAG Property Search dengan spesifikasi:

1. File structure:
   - api/
     - __init__.py
     - main.py (FastAPI app)
     - routers/
       - chat.py
       - health.py
     - schemas/
       - request.py
       - response.py
     - dependencies.py

2. Endpoints:
   - POST /api/v1/chat - main chat endpoint
   - GET /api/v1/health - health check
   - GET /docs - Swagger UI (auto-generated)

3. Features:
   - CORS middleware untuk cross-origin requests
   - Request validation dengan Pydantic
   - Error handling yang proper
   - Logging untuk debugging
   - Session management untuk multi-turn conversation

4. Integration dengan existing code:
   - Gunakan src/agents/react_agent.py untuk chat logic
   - Gunakan src/knowledge/hybrid_search.py untuk retrieval
   - Support semua 3 methods (vector_only, api_only, hybrid)

Pastikan API bisa dijalankan dengan:
uvicorn api.main:app --reload
```

### 2.2 Request/Response Schemas

**Prompt untuk Claude:**
```
Buatkan Pydantic schemas untuk API:

1. ChatRequest:
   - message: str (required)
   - session_id: str (optional, auto-generate if not provided)
   - method: Literal["vector_only", "api_only", "hybrid"] = "hybrid"
   - max_results: int = 10

2. ChatResponse:
   - response: str (natural language response)
   - properties: List[PropertySummary] (list of matching properties)
   - session_id: str
   - method_used: str
   - search_metadata: SearchMetadata

3. PropertySummary:
   - id: int
   - title: str
   - price: int
   - location: str
   - property_type: str
   - listing_type: str
   - bedrooms: Optional[int]
   - url: str

4. SearchMetadata:
   - total_found: int
   - returned: int
   - search_time_ms: float
   - constraints_detected: List[str]
```

### 2.3 Environment Configuration

**Prompt untuk Claude:**
```
Buatkan configuration management untuk API:

1. Buat config.py dengan Pydantic Settings:
   - OPENAI_API_KEY
   - METAPROPERTY_API_URL
   - METAPROPERTY_API_KEY
   - CHROMADB_PATH
   - LOG_LEVEL
   - CORS_ORIGINS

2. Buat .env.example dengan semua variables (tanpa values)

3. Update .gitignore untuk exclude:
   - .env
   - data/chromadb/ (atau buat setup script untuk initialize)
   - __pycache__/
   - *.pyc
```

---

## Phase 3: GitHub Repository Setup

### 3.1 Repository Structure

**Target Structure:**
```
rag-property-search/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   └── schemas/
├── src/
│   ├── adapters/
│   ├── agents/
│   ├── knowledge/
│   └── utils/
├── scripts/
│   ├── chat_cli.py
│   └── evaluate.py
├── tests/
├── docs/
│   ├── architecture.md
│   ├── api-reference.md
│   └── evaluation-results.md
├── data/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
└── LICENSE
```

### 3.2 README.md

**Prompt untuk Claude:**
```
Buatkan README.md yang comprehensive untuk GitHub repository:

# RAG Property Search Assistant

## Overview
Briefly explain what this is (thesis project, RAG for property search)

## Key Results
- Hybrid: 100% accuracy, F1=1.0
- API-only: 73.33% accuracy
- Vector-only: 56.67% accuracy

## Architecture
- High-level architecture diagram (ASCII or link to image)
- Tri-path retrieval explanation

## Quick Start
```bash
# Clone
git clone ...

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run API
uvicorn api.main:app --reload

# Or run CLI
python scripts/chat_cli.py
```

## API Documentation
Link to /docs endpoint or API reference

## Evaluation
Summary of evaluation methodology and results

## Citation
If using this for academic purposes

## License
MIT or appropriate license
```

### 3.3 Architecture Documentation

**Prompt untuk Claude:**
```
Buatkan docs/architecture.md dengan:

1. System Overview
   - High-level diagram
   - Component descriptions

2. Retrieval Pipelines
   - Vector-only flow
   - API-only flow
   - Hybrid flow dengan re-ranking

3. Data Flow
   - Query → Intent Extraction → Retrieval → Re-ranking → Response

4. Key Components
   - ReactAgent
   - HybridSearch
   - PropertyStore
   - ChromaDB integration

5. Configuration Options
   - Environment variables
   - Tunable parameters
```

---

## Phase 4: Deployment

### 4.1 Platform Options

| Platform | Pros | Cons | Cost |
|----------|------|------|------|
| Railway | Easy deploy, good free tier | Limited resources | Free tier available |
| Render | Auto-deploy from GitHub | Cold starts | Free tier available |
| Fly.io | Good performance, global | More complex setup | Pay as you go |
| Heroku | Simple, well-documented | No more free tier | $7/month minimum |

**Rekomendasi: Railway atau Render** untuk thesis demo

### 4.2 Railway Deployment

**Prompt untuk Claude:**
```
Buatkan konfigurasi untuk deploy ke Railway:

1. Buat Procfile:
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT

2. Buat railway.json atau railway.toml jika diperlukan

3. Update requirements.txt dengan:
   - uvicorn[standard]
   - gunicorn (optional, untuk production)

4. Buat runtime.txt:
   python-3.12

5. Instruksi deployment:
   - Connect GitHub repo ke Railway
   - Set environment variables
   - Deploy
```

### 4.3 Render Deployment

**Prompt untuk Claude:**
```
Buatkan konfigurasi untuk deploy ke Render:

1. Buat render.yaml:
   services:
     - type: web
       name: rag-property-search
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT

2. Instruksi:
   - Create new Web Service di Render
   - Connect GitHub repo
   - Set environment variables
   - Deploy
```

### 4.4 Environment Variables for Production

**Required Environment Variables:**
```
OPENAI_API_KEY=sk-...
METAPROPERTY_API_URL=https://api.metaproperty.id
METAPROPERTY_API_KEY=...
CHROMADB_PATH=/app/data/chromadb
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 4.5 ChromaDB Considerations

**Issue:** ChromaDB persistence di cloud deployment

**Options:**
1. **Rebuild on deploy** - Re-index saat startup (lambat tapi simple)
2. **Persistent volume** - Mount volume untuk ChromaDB data
3. **Remote ChromaDB** - Host ChromaDB terpisah

**Prompt untuk Claude:**
```
Untuk deployment, bagaimana handle ChromaDB:

Option 1 - Rebuild on startup:
- Buat startup script yang check if ChromaDB exists
- Jika tidak, run ingestion script
- Cocok untuk demo dengan data kecil

Option 2 - Include in deployment:
- Commit ChromaDB data ke repo (jika ukuran kecil)
- Atau upload ke cloud storage dan download saat deploy

Buatkan solusi yang paling practical untuk thesis demo dengan ~2800 properties.
```

---

## Phase 5: Testing & Verification

### 5.1 Local Testing

**Prompt untuk Claude:**
```
Buatkan test script untuk verify API sebelum deploy:

1. Health check test
2. Chat endpoint test dengan sample queries
3. Method switching test (vector, api, hybrid)
4. Session persistence test
5. Error handling test

Output: Summary pass/fail untuk setiap test
```

### 5.2 Production Verification

**Checklist setelah deploy:**
- [ ] Health endpoint returns 200
- [ ] Swagger docs accessible at /docs
- [ ] Chat endpoint responds correctly
- [ ] CORS working untuk frontend access
- [ ] Environment variables properly set
- [ ] Logs accessible untuk debugging

---

## Execution Checklist

### Day 1: Codebase Cleanup
- [ ] Audit current file structure
- [ ] Remove/archive unused files
- [ ] Standardize folder structure
- [ ] Create proper requirements.txt
- [ ] Create .env.example

### Day 2: API Development
- [ ] Create FastAPI application structure
- [ ] Implement chat endpoint
- [ ] Implement health endpoint
- [ ] Add request/response schemas
- [ ] Add CORS and error handling
- [ ] Test locally

### Day 3: GitHub & Documentation
- [ ] Create/update README.md
- [ ] Create architecture documentation
- [ ] Create API reference
- [ ] Setup .gitignore properly
- [ ] Push to GitHub

### Day 4: Deployment
- [ ] Choose deployment platform
- [ ] Configure deployment files
- [ ] Set environment variables
- [ ] Deploy
- [ ] Test production endpoint
- [ ] Get final demo URL

---

## Quick Reference Commands

```bash
# Local development
uvicorn api.main:app --reload --port 8000

# Test API locally
curl http://localhost:8000/api/v1/health
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "cari rumah di cemara", "method": "hybrid"}'

# Railway deploy
railway login
railway init
railway up

# Render deploy (via GitHub connection)
# Just push to main branch
```

---

## Notes for Next Session

Saat melanjutkan di sesi berikutnya, gunakan prompt berikut:

```
Lanjutkan dari docs/23-productionize-deployment-guide.md

Status saat ini:
- Evaluasi selesai (Hybrid 100%, API 73.33%, Vector 56.67%)
- Thesis draft selesai di docs/22-thesis-draft-sections.md
- HTML report di data/evaluation/thesis_metrics_report.html

Yang perlu dikerjakan:
1. [Phase yang akan dikerjakan dari guide]

Mulai dengan [step spesifik]
```

---

*Document created: 26 January 2026*
*For thesis: RAG Property Search Assistant*
