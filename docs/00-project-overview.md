# RAG Property Agent - Project Overview

> Executive summary dan panduan navigasi untuk proyek RAG-Tesis

**Last Updated:** 2026-01-25

---

## Tentang Proyek

**RAG Property Agent** adalah sistem **Multi-Agent AI** untuk asisten penjualan properti real estate di Indonesia (fokus kota Medan). Proyek ini dikembangkan sebagai bagian dari tesis dengan fokus pada:

- **Hybrid Search**: Kombinasi API filtering + semantic search (ChromaDB)
- **Location Intelligence**: Geocoding + radius search untuk query berbasis lokasi
- **Constraint-based Evaluation**: Metodologi evaluasi untuk mengukur akurasi sistem

---

## Arsitektur Sistem

```
User (CLI/WhatsApp)
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│              ReAct Agent (LangGraph)                     │
│         LLM-driven tool selection (GPT-4o-mini)         │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                      9 Tools                             │
├─────────────────────────────────────────────────────────┤
│ Property Tools (6)        │ Knowledge Tools (3)          │
│ • search_properties       │ • search_knowledge           │
│ • get_property_detail     │ • get_sales_tips             │
│ • get_property_by_number  │ • get_motivation             │
│ • geocode_location        │                              │
│ • search_nearby           │                              │
│ • search_pois             │                              │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                    Data Sources                          │
├───────────────────┬───────────────────┬─────────────────┤
│  MetaProperty API │    ChromaDB       │  SQLite Memory  │
│  (structured      │  (semantic search │  (chat history  │
│   filters)        │   & knowledge)    │   & summary)    │
└───────────────────┴───────────────────┴─────────────────┘
```

---

## Komponen Utama

### Core Components

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **ReAct Agent** | [src/agents/react_agent.py](../src/agents/react_agent.py) | Agent utama dengan LangGraph, tool calling |
| **Tools** | [src/agents/tools.py](../src/agents/tools.py) | 9 tools (search, nearby, POI, knowledge) |
| **Hybrid Search** | [src/knowledge/hybrid_search.py](../src/knowledge/hybrid_search.py) | API + ChromaDB semantic re-ranking |
| **Property Store** | [src/knowledge/property_store.py](../src/knowledge/property_store.py) | ChromaDB untuk properti |
| **Knowledge Store** | [src/knowledge/knowledge_store.py](../src/knowledge/knowledge_store.py) | ChromaDB untuk knowledge base |

### Adapters

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **Base Adapter** | [src/adapters/base.py](../src/adapters/base.py) | Interface & data models (Property, SearchCriteria) |
| **MetaProperty** | [src/adapters/metaproperty.py](../src/adapters/metaproperty.py) | Adapter untuk MetaProperty API |

### Memory System

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **SQLite Memory** | [src/memory/sqlite_memory.py](../src/memory/sqlite_memory.py) | Persistent chat history + sliding window |
| **Summarizer** | [src/memory/summarizer.py](../src/memory/summarizer.py) | Auto-summarization untuk long conversations |

### Evaluation

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **Evaluator** | [src/evaluation/evaluator.py](../src/evaluation/evaluator.py) | Constraint-based evaluation engine |
| **Constraint Checker** | [src/evaluation/constraint_checker.py](../src/evaluation/constraint_checker.py) | Per-constraint validation |
| **Models** | [src/evaluation/models.py](../src/evaluation/models.py) | GoldQuestion, QueryEvaluation, Metrics |

### Utilities

| Komponen | File | Deskripsi |
|----------|------|-----------|
| **Metrics** | [src/utils/metrics.py](../src/utils/metrics.py) | Search & tool metrics logging |
| **Tokens** | [src/utils/tokens.py](../src/utils/tokens.py) | Token counting & cost estimation |
| **Logging** | [src/utils/logging.py](../src/utils/logging.py) | Structured logging (structlog) |
| **Geocoding** | [src/utils/geocoding.py](../src/utils/geocoding.py) | Location name to coordinates |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **AI Framework** | LangGraph + LangChain |
| **LLM** | GPT-4o-mini (default) |
| **Embeddings** | text-embedding-3-small |
| **Vector DB** | ChromaDB |
| **Chat Memory** | SQLite (local) |
| **API Client** | httpx (async) |
| **CLI UI** | Rich |
| **Config** | Pydantic Settings + python-dotenv |

---

## Struktur Data

```
data/
├── chromadb/
│   ├── knowledge/          # Vector store untuk knowledge base
│   └── properties/         # Vector store untuk properti (semantic)
├── knowledge-base/         # Markdown source files
│   ├── real-estate-knowledge/
│   │   ├── kpr-guide.md
│   │   ├── legal-documents.md
│   │   ├── pajak-properti.md
│   │   └── ...
│   ├── sales-techniques/
│   │   ├── closing-strategies.md
│   │   ├── handle-objection.md
│   │   └── ...
│   └── motivational/
│       └── mindset-tips.md
├── gold/                   # Gold standard untuk evaluation
│   ├── questions_v2.json   # Test questions dengan constraints
│   └── locations.json      # Known locations database
├── evaluation/             # Evaluation results
│   └── v2/                 # Latest evaluation runs
├── metrics/                # Runtime metrics (JSONL)
│   ├── search_YYYY-MM-DD.jsonl
│   └── tool_YYYY-MM-DD.jsonl
├── properties/
│   └── sample_properties.json
├── test_cases/
│   └── test_cases.json
└── chat_history.db         # SQLite chat memory
```

---

## Scripts

### Main Scripts

| Script | Command | Deskripsi |
|--------|---------|-----------|
| **Interactive Chat** | `python scripts/chat.py` | CLI chat dengan Rich UI |
| **Chat (verbose)** | `python scripts/chat.py -v` | Dengan tree display & token tracking |

### Data Management

| Script | Command | Deskripsi |
|--------|---------|-----------|
| **Ingest Knowledge** | `python scripts/ingest_knowledge.py` | Load knowledge base ke ChromaDB |
| **Sync Properties** | `python scripts/sync_properties.py` | Sync properti dari API ke ChromaDB |

### Evaluation

| Script | Command | Deskripsi |
|--------|---------|-----------|
| **Run Evaluation** | `python scripts/evaluate_v2.py` | Jalankan evaluation dengan gold standard |
| **Export Metrics** | `python scripts/export_metrics.py` | Export metrics untuk analisis |

### Testing

| Script | Command | Deskripsi |
|--------|---------|-----------|
| **Test Hybrid Search** | `python scripts/test_hybrid_search.py` | Test hybrid search |
| **Test Property Search** | `python scripts/test_property_search.py` | Test property tools |
| **Test ReAct Agent** | `python scripts/test_react_agent.py` | Test agent responses |

---

## Fitur Utama

### 1. Hybrid Search

Kombinasi dua strategi pencarian:

- **API Filtering**: Harga, tipe properti, jumlah kamar, lokasi (structured)
- **Semantic Re-ranking**: ChromaDB untuk query fuzzy ("rumah taman luas")

```
User Query → API Filter → Get Results → ChromaDB Re-rank → Final Results
```

### 2. Location Intelligence

- **Geocoding**: Konversi nama lokasi ke koordinat (Google Maps / Nominatim)
- **Radius Search**: Cari properti dalam radius dari landmark
- **POI Discovery**: Temukan sekolah/mall/RS lalu cari properti di sekitarnya
- **Smart Location Fallback**: Jika keyword tidak ada di DB, gunakan koordinat

### 3. Memory System

- **Sliding Window**: 20 pesan terakhir untuk LLM context
- **Auto-Summarization**: Summarize ketika >50 pesan
- **User Isolation**: Setiap user punya conversation terpisah
- **Persistent Storage**: SQLite untuk durability

### 4. Tools (9 Total)

**Property Tools:**
1. `search_properties` - Pencarian dengan filter lengkap
2. `get_property_detail` - Detail properti by ID
3. `get_property_by_number` - Detail by nomor hasil (1-10)
4. `geocode_location` - Nama lokasi → koordinat
5. `search_nearby` - Pencarian radius
6. `search_pois` - Discover POI (sekolah/mall/RS)

**Knowledge Tools:**
7. `search_knowledge` - Cari di knowledge base
8. `get_sales_tips` - Tips penjualan
9. `get_motivation` - Motivasi untuk agen

---

## Evaluation Methodology

### Constraint-based Evaluation

Setiap hasil pencarian dievaluasi berdasarkan constraint yang diminta user:

| Constraint | Contoh | Validasi |
|------------|--------|----------|
| `property_type` | "rumah" | Exact match |
| `listing_type` | "dijual" | Exact match |
| `location` | "cemara asri" | Substring match / geo distance |
| `price` | "maksimal 1M" | Range check dengan tolerance |
| `bedrooms` | "3 kamar" | Exact atau range match |
| `floors` | "2 lantai" | Exact atau range match |

### Metrics

- **PCA (Per-Constraint Accuracy)**: Akurasi per jenis constraint
- **CPR (Constraint Pass Rate)**: Rata-rata constraint yang pass per properti
- **Confusion Matrix**: TP/FP/TN/FN berdasarkan threshold
- **Query Success Rate**: Persentase query yang berhasil (CPR > threshold)

### Gold Standard

File: `data/gold/questions_v2.json`

```json
{
  "questions": [
    {
      "id": 1,
      "question": "cari rumah di cemara asri maksimal 1 miliar",
      "category": "location_price",
      "expected_result": true,
      "constraints": {
        "property_type": "house",
        "location": ["cemara asri"],
        "max_price": 1000000000
      }
    }
  ]
}
```

---

## Quick Start

### 1. Setup Environment

```bash
# Clone & setup
cd rag-tesis
python -m venv venv
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Configure
cp .env.example .env
# Edit .env dengan API keys (OPENAI_API_KEY, METAPROPERTY_API_URL, dll)
```

### 2. Ingest Data

```bash
# Load knowledge base ke ChromaDB
python scripts/ingest_knowledge.py

# Sync properti dari API ke ChromaDB
python scripts/sync_properties.py
```

### 3. Run Chat

```bash
# Simple mode
python scripts/chat.py

# Verbose mode (dengan tree display)
python scripts/chat.py -v
```

### 4. Run Evaluation

```bash
python scripts/evaluate_v2.py
```

---

## Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# MetaProperty API
METAPROPERTY_API_URL=http://localhost:8000
METAPROPERTY_API_TOKEN=your-token

# Optional
GOOGLE_MAPS_API_KEY=...  # Untuk geocoding (fallback: Nominatim)
```

---

## Dokumentasi Terkait

| Dokumen | Deskripsi |
|---------|-----------|
| [01-master-roadmap.md](01-master-roadmap.md) | Arsitektur lengkap & development phases |
| [02-mvp-implementation-plan.md](02-mvp-implementation-plan.md) | Detail implementasi MVP |
| [03-api-specification.md](03-api-specification.md) | API specification |
| [10-agents-and-tools-guide.md](10-agents-and-tools-guide.md) | Dokumentasi lengkap tools |
| [08-chromadb-ingestion-guide.md](08-chromadb-ingestion-guide.md) | Setup ChromaDB |
| [16-search-strategy.md](16-search-strategy.md) | Hybrid search strategy |
| [18-evaluation-v2-confusion-matrix.md](18-evaluation-v2-confusion-matrix.md) | Evaluation methodology |

---

## Fokus Riset (Tesis)

1. **Hybrid Search Strategy** - Efektivitas kombinasi API + semantic search
2. **Constraint-based Evaluation** - Metodologi evaluasi untuk property search
3. **Location Intelligence** - Akurasi geocoding + proximity search
4. **Memory Management** - Sliding window + summarization untuk long conversations

---

*Proyek Tesis - Sistem AI Agent Multi-Purpose untuk Asisten Penjualan Properti*
