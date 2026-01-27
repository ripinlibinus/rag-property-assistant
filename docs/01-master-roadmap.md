# 🎯 Full System Roadmap - AI Agent Multi-Purpose untuk Real Estate

> **Master Roadmap** untuk pengembangan sistem AI Agent lengkap.
> Untuk MVP 1 minggu, lihat [implementation_plan.md](./implementation_plan.md)

---

## 📋 Vision Statement

Membangun platform AI Agent komprehensif yang membantu profesional real estate dengan:
- Otomasi workflow penjualan (READ + WRITE operations)
- Knowledge assistant berbasis RAG
- Multi-channel communication (WhatsApp, Telegram, Web)
- Market intelligence & analytics dari berbagai sumber

---

## 🏗️ Core Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMMUNICATION LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│   WhatsApp        │   Telegram         │   Web Widget      │   Mobile App   │
│   (Baileys)       │   (Bot API)        │   (React)         │   (React Native)│
└────────┬──────────┴─────────┬──────────┴─────────┬─────────┴────────┬───────┘
         └────────────────────┴────────────────────┴──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │         API GATEWAY (FastAPI)        │
                    │   Auth │ Rate Limiting │ Logging     │
                    └──────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │      ORCHESTRATOR AGENT (LangGraph)  │
                    │   Intent Classification + Routing    │
                    └───┬─────────┬─────────┬─────────┬───┘
                        │         │         │         │
        ┌───────────────▼──┐  ┌───▼───┐  ┌──▼──┐  ┌──▼──────────┐
        │  PROPERTY AGENT  │  │ COACH │  │SCHED│  │   SCRAPER   │
        │  Search + CRUD   │  │ AGENT │  │ULER │  │    AGENT    │
        └────────┬─────────┘  └───┬───┘  └──┬──┘  └──────┬──────┘
                 │                │         │            │
        ┌────────▼────────────────▼─────────▼────────────▼────────┐
        │                    MEMORY LAYER                          │
        │  Redis (Session) │ PostgreSQL (Long-term) │ ChromaDB    │
        └─────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Adapter Architecture (Universal)

Semua data source menggunakan **Standard Adapter Interface** agar RAG fleksibel.

### Adapter Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    UNIVERSAL DATA ADAPTER INTERFACE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  class PropertyDataAdapter:                                                 │
│      # READ Operations                                                      │
│      def search(filters: SearchCriteria) -> list[Property]                 │
│      def get_by_id(id: str) -> Property                                    │
│      def get_all(page: int, limit: int) -> PaginatedResult                 │
│                                                                             │
│      # WRITE Operations (requires auth)                                     │
│      def create(data: PropertyCreate) -> Property                          │
│      def update(id: str, data: PropertyUpdate) -> Property                 │
│      def delete(id: str) -> bool                                           │
│                                                                             │
│  Standard Response Format:                                                  │
│  {                                                                          │
│    "properties": [                                                          │
│      { "id", "title", "type", "price", "location", "bedrooms",             │
│        "bathrooms", "land_area", "building_area", "images", "agent" }      │
│    ],                                                                       │
│    "meta": { "total", "page", "has_more" }                                 │
│  }                                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │ MetaProperty  │       │   Rumah123    │       │     OLX       │
    │   Adapter     │       │   Adapter     │       │   Adapter     │
    │   (API)       │       │  (Scraper)    │       │  (Scraper)    │
    └───────────────┘       └───────────────┘       └───────────────┘
```

---

## 🤖 Agent-Specific Data Sources

### Property Agent

| Source | Type | Purpose |
|--------|------|---------|
| MetaProperty API | Primary | READ + WRITE operations |
| ChromaDB (properties) | Cache | Semantic search / ranking |
| External Scrapers | Secondary | Market data aggregation |

### Coach Agent

| Source | Type | Purpose |
|--------|------|---------|
| Knowledge Documents | Primary | Sales tips, real estate law, processes |
| ChromaDB (knowledge) | Cache | Semantic retrieval |

**Knowledge Categories:**
```
knowledge-base/
├── sales-techniques/
│   ├── closing-strategies.md
│   ├── objection-handling.md
│   └── follow-up-best-practices.md
├── real-estate-knowledge/
│   ├── sertifikat-types.md      # SHM, SHGB, HGB
│   ├── proses-jual-beli.md      # AJB, Balik Nama
│   ├── pajak-properti.md        # BPHTB, PPh, PBB
│   └── kpr-guide.md
└── motivational/
    └── quotes-tips.md
```

### Scheduler Agent (Phase 2)

| Source | Type | Purpose |
|--------|------|---------|
| Redis | Primary | Task queue, reminders |
| Google Calendar API | External | Appointment scheduling |

### Scraper Agent (Phase 2)

| Source | Type | Purpose |
|--------|------|---------|
| Rumah123, OLX | External | Market monitoring |
| Price Database | Internal | Historical price trends |

---

## 🔄 Bidirectional Data Flow (READ + WRITE)

### Write Operations via Chat

```
User: "Update harga rumah di Jl. Pancing jadi 1.5M"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. INTENT DETECTION                                             │
│    → property_update                                            │
├─────────────────────────────────────────────────────────────────┤
│ 2. ENTITY EXTRACTION (LLM)                                      │
│    → listing: "rumah di Jl. Pancing"                           │
│    → field: "price"                                             │
│    → value: 1,500,000,000                                       │
├─────────────────────────────────────────────────────────────────┤
│ 3. PERMISSION CHECK                                             │
│    → User (WhatsApp: 08123xxx) → Agent ID: 5                   │
│    → Does Agent 5 own this listing? → YES                      │
├─────────────────────────────────────────────────────────────────┤
│ 4. CONFIRMATION PROMPT                                          │
│    → "Update harga menjadi Rp 1.5M? Ketik YA"                  │
├─────────────────────────────────────────────────────────────────┤
│ 5. EXECUTE WRITE                                                │
│    → PUT /api/listings/18 { price: 1500000000 }                │
├─────────────────────────────────────────────────────────────────┤
│ 6. SYNC TO CHROMADB                                             │
│    → Re-embed updated listing                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Supported Write Operations

| Operation | Example Chat Command |
|-----------|---------------------|
| Update Price | "Update harga jadi 1.5M" |
| Update Status | "Tandai listing sudah sold" |
| Create Listing | "Tambah listing baru: rumah 3KT di Sunggal 900jt" |
| Upload Photo | [Send image] "Tambahkan ke listing Jl. Pancing" |
| Generate Description | "Buatkan deskripsi marketing" |

---

## 🚀 Development Phases

### Phase 1: MVP (Tesis) - 1 Week ← CURRENT
**Goal:** Sistem dasar untuk evaluasi tesis

| Component | Scope | Status |
|-----------|-------|--------|
| Orchestrator | LangGraph ReAct (7 tools) | ✅ Done |
| Property Agent | Search + Detail via API | ✅ Done |
| Geocoding Tools | Location → Coords, Nearby search | ✅ Done |
| Coach Agent | Knowledge base RAG (ChromaDB) | 🔄 In Progress |
| Memory | SQLite persistent chat history | ✅ Done |
| Evaluation | 100+ test cases + metrics | 🔲 Pending |

**Day 4 Additions:**
- Token usage & cost tracking (USD + IDR)
- Language style matching (formal/casual)  
- Geocoding via OpenStreetMap Nominatim API
- Proximity search (search within radius)
- SQLite chat memory with sliding window

### Phase 2: Production Ready - Feb 2026
- Full knowledge base (100+ documents)
- Error recovery & fallbacks
- Admin dashboard
- Rate limiting

### Phase 3: Multi-Channel - Mar 2026
- Telegram Bot
- Web Widget
- Mobile App

### Phase 4: Market Intelligence - Q2 2026
- Portal scraping
- Price analytics
- Competition monitoring

### Phase 5: Automation Suite - Q3 2026
- Smart follow-up
- Campaign manager
- Lead scoring

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| AI Framework | LangGraph + LangChain |
| LLM | GPT-4o-mini (cost-effective) |
| Embeddings | text-embedding-3-small |
| Vector DB | ChromaDB → Qdrant (scale) |
| Database | PostgreSQL |
| Cache | Redis |
| Session Memory | SQLite (MVP) → PostgreSQL (Prod) |
| API | FastAPI |
| WhatsApp | Baileys (Node.js) |

---

## 📊 Success Metrics

| Metric | MVP Target | Production Target |
|--------|------------|-------------------|
| Intent Accuracy | >85% | >95% |
| Search Precision@5 | >70% | >85% |
| Response Latency | <3s | <2s |
| Write Success Rate | >90% | >99% |

---

## 🔗 Related Documents

- [MVP Implementation Plan](./implementation_plan.md) - Detail 7-hari development
- [Task Checklist](./task.md) - Progress tracking
- [Day 4 Progress Report](./07-progress-report-day4-continued.md) - Latest updates

---

*Last updated: 2026-01-23*
