# Day 4 Progress Report (Continued): Major Feature Additions

**Date:** 2026-01-23  
**Session:** Afternoon/Evening

---

## Summary of Today's Work

Major additions to the ReAct Agent system:

1. ✅ Token usage & cost tracking
2. ✅ Language style matching (formal/casual)  
3. ✅ Geospatial/Proximity search tools
4. ✅ SQLite persistent chat memory
5. ✅ Updated documentation

---

## 1. Token Usage & Cost Tracking

**File:** [scripts/chat.py](../scripts/chat.py)

Added cost calculation for each chat:
- GPT-4o-mini pricing: $0.15/1M input, $0.60/1M output
- USD to IDR conversion (rate: 17,000)
- Per-chat and session totals

```
TOKEN USAGE & COST
----------------------------------------
  Input tokens:  1,234
  Output tokens: 456
  Total tokens:  1,690
  Cost: $0.000458 USD
        Rp 7.79 IDR
----------------------------------------
```

---

## 2. Language Style Matching

**File:** [src/agents/react_agent.py](../src/agents/react_agent.py)

Updated system prompt to properly mirror user's language style:

```
LANGUAGE & STYLE:
- ALWAYS mirror the user's language style exactly
- If user speaks formal Indonesian (saya, Anda, Bapak/Ibu) → respond formally
- If user speaks casual Indonesian (gue, lu, bro, kak) → respond casually  
- If user speaks English → respond in English
- Default to FORMAL polite Indonesian if user's style is unclear
```

---

## 3. Geospatial/Proximity Search

### New Tools

**File:** [src/agents/tools.py](../src/agents/tools.py)

| Tool | Description |
|------|-------------|
| `geocode_location` | Convert location name → lat/lng coordinates (via OpenStreetMap Nominatim) |
| `search_nearby` | Search properties within radius from a point |

### New Input Schemas

```python
class GeocodeLocationInput(BaseModel):
    location_name: str  # "USU Medan", "Sun Plaza", etc.

class SearchNearbyInput(BaseModel):
    location_name: str
    radius_km: float = 3.0  # Default 3km
    property_type: Optional[str]
    listing_type: Optional[str]
    min_price: Optional[int]
    max_price: Optional[int]
```

### Flow

```
User: "cari rumah dekat USU radius 3km"
     ↓
Agent: search_nearby(location_name="USU", radius_km=3, property_type="house")
     ↓
Tool: Geocode "USU" → lat=3.5656, lng=98.6595
     ↓
Tool: API call /api/v1/listings?lat=3.5656&lng=98.6595&radius=3
     ↓
Agent: Format and return results
```

### Backend Required

Documentation for Laravel API created:
- [metaproperty2026/docs/outstanding-session/proximity-search-api.md](../../Metaproperty/metaproperty2026/docs/outstanding-session/proximity-search-api.md)

Contains:
- Haversine formula implementation
- `scopeNearby()` model method
- API parameters: `lat`, `lng`, `radius`

---

## 4. SQLite Persistent Chat Memory

### Decision Change

Originally planned MySQL via MetaProperty API, but reconsidered:

| Option | Pros | Cons |
|--------|------|------|
| MySQL via MetaProperty API | Shared with MetaProperty | Wrong separation of concerns |
| **SQLite in Chatbot** | ✅ Simple, local, no deps | Not distributed |

**Decision:** Use SQLite locally in Rag-Tesis chatbot. Migrate to PostgreSQL for production later.

### Implementation

**File:** [src/memory/sqlite_memory.py](../src/memory/sqlite_memory.py)

Tables:
- `conversations` - thread_id, user_id, title, summary, message_count
- `messages` - role, content, tool_calls, tool_call_id, sequence

Classes:
- `SQLiteChatMemory` - Direct database access
- `SlidingWindowMemory` - Token-efficient wrapper (summary + recent N messages)

### Usage

```python
# Agent with SQLite memory (default)
agent = create_property_react_agent(adapter)

# Without memory
agent = create_property_react_agent(adapter, enable_memory=False)

# Custom database path
agent = create_property_react_agent(adapter, db_path="./custom.db")
```

### Database Location

Default: `data/chat_history.db`

---

## 5. Updated Files Summary

### New Files

| File | Description |
|------|-------------|
| `src/memory/sqlite_memory.py` | SQLite chat history storage |
| `src/agents/tools.py` | Now includes geo tools |
| `docs/06-nearby-search-architecture.md` | Geo search design |

### Modified Files

| File | Changes |
|------|---------|
| `src/agents/react_agent.py` | Added `chat_memory` param, SQLite integration |
| `src/agents/tools.py` | Added `geocode_location`, `search_nearby` tools |
| `src/adapters/base.py` | Added `latitude`, `longitude`, `radius_km` to SearchCriteria |
| `src/adapters/metaproperty.py` | Pass geo params to API |
| `src/memory/__init__.py` | Export SQLite memory classes |
| `scripts/chat.py` | Token tracking, cost display, verbose mode |

### Files to Remove (deprecated)

| File | Reason |
|------|--------|
| `src/memory/mysql_memory.py` | Replaced by SQLite |
| `metaproperty2026/docs/outstanding-session/chat-history-mysql.md` | No longer needed |

---

## 6. Current Agent Capabilities

### Tools Available

| # | Tool | Description |
|---|------|-------------|
| 1 | `search_properties` | Search by keywords, type, price |
| 2 | `get_property_detail` | Get single property by ID |
| 3 | `geocode_location` | Convert location → coordinates |
| 4 | `search_nearby` | Search within radius |
| 5 | `search_knowledge` | Search knowledge base |
| 6 | `get_sales_tips` | Sales coaching tips |
| 7 | `get_motivation` | Motivational messages |

### System Prompt Highlights

- Agent decides which tool to call (not hardcoded routing)
- Mirrors user language style (formal/casual/English)
- When to use `search_nearby` vs `search_properties`
- How to handle empty results

---

## 7. How to Test

```powershell
cd D:\Project\Rag-Tesis
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"

# Interactive chat (normal mode)
python scripts/chat.py

# Interactive chat (verbose - show all steps)
python scripts/chat.py -v
```

### Test Queries

| Query | Expected Tool |
|-------|---------------|
| "cari rumah di cemara asri" | `search_properties` |
| "rumah dekat USU radius 2km" | `search_nearby` |
| "tips closing sales" | `get_sales_tips` |
| "kasih motivasi dong" | `get_motivation` |

---

## 8. Next Steps (Backlog)

### Short Term
- [ ] Implement Haversine in Laravel API (proximity-search-api.md)
- [ ] Populate ChromaDB knowledge base
- [ ] Add conversation summary generation (for long conversations)

### Medium Term
- [ ] WhatsApp integration
- [ ] Migrate SQLite → PostgreSQL for production
- [ ] Add property recommendation based on history

### Long Term
- [ ] Multi-agent orchestration
- [ ] Scraper agents for external listings
- [ ] Analytics dashboard

---

## Architecture Diagram (Current)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         scripts/chat.py                               │
│   Interactive CLI with token tracking & verbose mode                  │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    ReActPropertyAgent                                 │
│   LangGraph ReAct pattern with tool calling                          │
│                                                                       │
│   ┌─────────────┐    ┌────────────────┐    ┌────────────────────┐   │
│   │ LLM (GPT-4o)│ ───▶│ Tool Decision  │ ───▶│ Tool Execution    │   │
│   │ bind_tools()│    │ (7 tools)      │    │ ToolNode          │   │
│   └─────────────┘    └────────────────┘    └────────────────────┘   │
│                                                                       │
│   ┌────────────────────────────────────────────────────────────────┐ │
│   │ SlidingWindowMemory (SQLite)                                    │ │
│   │ - Load last 20 messages                                        │ │
│   │ - Save user + assistant messages                               │ │
│   │ - Optional summary for older context                           │ │
│   └────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│  MetaProperty │        │  Nominatim    │        │   ChromaDB    │
│  API Adapter  │        │  Geocoding    │        │  (future)     │
│  (properties) │        │  (free/OSM)   │        │  (knowledge)  │
└───────────────┘        └───────────────┘        └───────────────┘
        │
        ▼
┌───────────────┐
│  MetaProperty │
│  Laravel API  │
│  (MySQL)      │
└───────────────┘
```

---

## Files Structure

```
Rag-Tesis/
├── data/
│   └── chat_history.db          # SQLite persistent memory (auto-created)
├── scripts/
│   └── chat.py                  # Interactive CLI with -v mode
├── src/
│   ├── adapters/
│   │   ├── base.py              # SearchCriteria with geo fields
│   │   └── metaproperty.py      # API adapter with geo support
│   ├── agents/
│   │   ├── react_agent.py       # Main agent with SQLite memory
│   │   └── tools.py             # 7 tools including geo
│   └── memory/
│       ├── sqlite_memory.py     # SQLite chat history
│       └── __init__.py
└── docs/
    ├── 01-master-roadmap.md
    ├── 02-mvp-implementation-plan.md
    ├── 05-progress-report-day4.md
    └── 07-progress-report-day4-continued.md  # This file
```
