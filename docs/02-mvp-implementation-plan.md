# 🎓 MVP Development Plan untuk Tesis

> **MVP Implementation Plan** - Detail 7 hari development
> Untuk master roadmap lengkap, lihat [01-master-roadmap.md](./01-master-roadmap.md)

**Goal:** Develop sistem AI Agent MVP, testing dengan data real, analisa hasil untuk laporan tesis.

**Timeline:** 1 Minggu | **Developer:** 1 Orang

**Status:** Day 4 Complete | Next: Day 5 (Testing & Evaluation)

---

## 🎯 MVP Scope

### Yang AKAN dibuat:

| Component | Scope | Status |
|-----------|-------|--------|
| **ReAct Agent** | LangGraph ReAct pattern, LLM decides tool calls | ✅ Done |
| **Property Tools** | search_properties, get_property_detail, search_nearby | ✅ Done |
| **Geocoding Tools** | geocode_location (Nominatim API) | ✅ Done |
| **Coach Tools** | search_knowledge, get_sales_tips, get_motivation | ✅ Done |
| **Data Adapter** | MetaPropertyAPIAdapter dengan geo support | ✅ Done |
| **Memory System** | SQLite persistent chat history | ✅ Done |
| **WhatsApp Integration** | Connect ke existing Baileys forwarder | 🔲 Pending |
| **Evaluation Framework** | Automated testing + metrics untuk tesis | 🔲 Pending |

### Perubahan dari Rencana Awal:
- ~~Orchestrator + separate agents~~ → **Single ReAct agent with 7 tools**
- ~~Redis + PostgreSQL~~ → **SQLite local** (simpler, migrate to PostgreSQL later)
- ~~Hybrid search~~ → **API-first + semantic ranking** (via tools)
- **Added:** Geocoding & proximity search tools

### Yang TIDAK termasuk MVP:
- Web Scraper Agent (external portals) → Phase 2
- Telegram integration → Phase 2
- Web Widget → Phase 2
- Scheduler Agent → Phase 2
- CRUD operations (create/update/delete) → Phase 2

---

## 🏗️ Technical Architecture (MVP)

### Data Flow (Actual Implementation)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER (CLI / WhatsApp)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        scripts/chat.py (CLI)                                 │
│                  Token tracking, cost display, verbose mode                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ReActPropertyAgent (LangGraph)                         │
│    LLM (GPT-4o-mini) decides which tool to call based on user query         │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                         7 TOOLS AVAILABLE                             │  │
│   ├──────────────────────────────────────────────────────────────────────┤  │
│   │ search_properties  │ get_property_detail │ geocode_location          │  │
│   │ search_nearby      │ search_knowledge    │ get_sales_tips            │  │
│   │ get_motivation     │                     │                           │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │ SlidingWindowMemory (SQLite) - Persistent chat history               │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
         │                        │                         │
         ▼                        ▼                         ▼
┌─────────────────┐     ┌─────────────────┐      ┌─────────────────┐
│ MetaProperty    │     │   Nominatim     │      │   ChromaDB      │
│ API Adapter     │     │   Geocoding     │      │   (pending)     │
│ (properties)    │     │   (free API)    │      │   (knowledge)   │
└────────┬────────┘     └─────────────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│ MetaProperty DB │
│ (MySQL via API) │
└─────────────────┘
```

### Universal Data Adapter Interface

```python
class PropertyDataAdapter(Protocol):
    """Standard interface for all property data sources"""
    
    # READ Operations
    async def search(self, criteria: SearchCriteria) -> list[Property]
    async def get_by_id(self, id: str) -> Property | None
    
    # WRITE Operations (requires auth)
    async def create(self, data: PropertyCreate) -> Property
    async def update(self, id: str, data: PropertyUpdate) -> Property
    async def delete(self, id: str) -> bool

# Standard Property Schema
@dataclass
class Property:
    id: str
    title: str
    property_type: str      # rumah, ruko, tanah, apartment
    listing_type: str       # sale, rent
    price: float
    location: str
    city: str
    bedrooms: int | None
    bathrooms: int | None
    land_area: float | None
    building_area: float | None
    features: list[str]
    images: list[str]
    agent_name: str | None
    agent_phone: str | None
```

---

## 📅 Day-by-Day Breakdown

### Day 1: Foundation & Data Preparation ✅ DONE

**Morning:**
- [x] Setup project structure
- [x] Install dependencies (LangGraph, LangChain, dll)
- [x] Setup evaluation framework skeleton

**Afternoon:**
- [x] Generate test dataset (30 test cases)
- [x] Prepare sample property data
- [x] Create docs structure

---

### Day 2: Property Agent + Data Adapter ✅ DONE

**Morning:**
- [x] Implement `PropertyDataAdapter` base interface → `src/adapters/base.py`
- [x] Implement `MetaPropertyAPIAdapter` → `src/adapters/metaproperty.py`
  - [x] READ: search, get_by_id
  - [x] Geo params: lat, lng, radius_km
- [x] Setup authentication (Bearer token)

**Afternoon:**
- [x] Implement tools: `search_properties`, `get_property_detail`
- [x] API filtering (price, location, type, bedrooms, etc.)
- [x] Connect to LangGraph ReAct pattern

**Deliverables:**
- ✅ Working Property tools with MetaProperty API
- ✅ API filtering functional
- ⏭️ CRUD deferred to Phase 2

---

### Day 3: Coach Agent & Memory ✅ DONE

**Morning:**
- [x] Create knowledge base document structure
  - [x] sales-techniques/ folder created
  - [x] real-estate-knowledge/ folder created
  - [x] motivational/ folder created
- [x] Implement Coach tools: `search_knowledge`, `get_sales_tips`, `get_motivation`

**Afternoon:**
- [x] Implement ReAct agent with LangGraph
- [x] System prompt with language style matching
- [x] Basic error handling

**Deliverables:**
- ✅ Coach tools implemented
- ✅ ReAct agent working
- 🔲 ChromaDB ingestion pending (using placeholder responses)

---

### Day 4: Integration & Features ✅ DONE

**Morning:**
- [x] Token usage & cost tracking (USD + IDR)
- [x] Language style matching fix (formal/casual)
- [x] Verbose mode (-v flag) for debugging

**Afternoon:**
- [x] Geocoding tools: `geocode_location` (Nominatim API)
- [x] Proximity search: `search_nearby` (coords + radius)
- [x] SQLite persistent chat memory
- [x] Update documentation

**Deliverables:**
- ✅ 7 tools fully integrated
- ✅ SQLite memory working
- ✅ Geocoding functional
- 🔲 WhatsApp integration → moved to Day 6

---

### Day 5: ChromaDB & Testing ← NEXT

**Morning:**
- [ ] Ingest knowledge base to ChromaDB
  - [ ] Create ingestion script
  - [ ] Index sales-techniques/*.md
  - [ ] Index real-estate-knowledge/*.md
  - [ ] Index motivational/*.md
- [ ] Update `search_knowledge` tool to use ChromaDB

**Afternoon:**
- [ ] Expand test cases to 100+
- [ ] Implement automated test runner
- [ ] Run all test cases
- [ ] Collect raw metrics

**Deliverables:**
- Knowledge base indexed in ChromaDB
- Test suite ready
- Initial metrics collected

---

### Day 6: WhatsApp & Edge Cases

**Morning:**
- [ ] Integrate dengan WhatsApp forwarder (existing Baileys)
- [ ] Create FastAPI endpoint for WhatsApp webhook
- [ ] Test real WhatsApp flow

**Afternoon:**
- [ ] Edge case testing & fixes
- [ ] Error handling improvements
- [ ] Performance testing

**Deliverables:**
- WhatsApp integration working
- Error cases handled gracefully
- Performance baseline established

---

### Day 7: Analysis & Documentation

**Morning:**
- [ ] Calculate accuracy metrics
  - [ ] Tool selection accuracy
  - [ ] Search precision/recall
  - [ ] Response relevance scoring
- [ ] Performance analysis
  - [ ] Response time distribution
  - [ ] Token usage per query type
  - [ ] Cost analysis (already tracked!)

**Afternoon:**
- [ ] Generate visualizations
- [ ] Write thesis analysis chapter
- [ ] Final documentation

**Deliverables:**
- Accuracy & performance report
- Charts & graphs
- Thesis-ready analysis document

---

## 📊 Test Dataset Plan

### Property Test Data
Menggunakan data real dari MetaProperty API + sample data.

### Test Cases (Target: 100+)

| Category | Count | Examples |
|----------|-------|----------|
| **Property Search** | 40 | Simple, complex, follow-up queries |
| **Property CRUD** | 20 | Update price, status, create listing |
| **Coaching** | 25 | Sales tips, knowledge, motivation |
| **Greeting/General** | 10 | Hello, thanks, general |
| **Multi-turn** | 10 | Contextual conversations |

---

## 📈 Metrics to Collect

### Accuracy
- Intent classification accuracy
- Search Precision@K, Recall, MRR
- Response relevance score (1-5)

### Performance
- Total latency (mean, p95, p99)
- Token usage per query
- Cost per query (USD)

### Write Operations
- Success rate
- Confirmation flow completion rate

---

## 🛠️ Tech Stack

| Component | Technology | Status |
|-----------|------------|--------|
| AI Framework | LangGraph + LangChain | ✅ |
| LLM | GPT-4o-mini (temperature=0) | ✅ |
| Vector DB | ChromaDB | 🔲 Pending |
| Chat Memory | SQLite (local) | ✅ |
| Geocoding | OpenStreetMap Nominatim (free) | ✅ |
| API | FastAPI | 🔲 Pending |
| Data Source | MetaProperty Laravel API | ✅ |
| WhatsApp | Baileys (Node.js) | 🔲 Pending |

---

## ⚙️ Configuration Required

```env
# .env file (current)
OPENAI_API_KEY=sk-xxx
METAPROPERTY_API_URL=http://api.metaproperty.local/api/v1
METAPROPERTY_API_TOKEN=xxx

# SQLite (auto-created)
# data/chat_history.db

# ChromaDB (when implemented)
# CHROMA_PERSIST_DIR=./data/chromadb
```

---

## 📁 Key Files

| File | Purpose |
|------|--------|
| `scripts/chat.py` | Interactive CLI with token tracking |
| `src/agents/react_agent.py` | Main ReAct agent |
| `src/agents/tools.py` | All 7 tools |
| `src/adapters/metaproperty.py` | API adapter |
| `src/memory/sqlite_memory.py` | Chat persistence |

---

*Last updated: 2026-01-23*
