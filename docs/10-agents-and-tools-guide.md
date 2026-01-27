# Agents & Tools Architecture Guide

Dokumentasi lengkap tentang **agents** dan **tools** yang ada dalam sistem RAG-Tesis.

**Last Updated:** 2026-01-25 (v2.0 - Global Support)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agents](#agents)
3. [Tools](#tools)
4. [Tool Selection Logic](#tool-selection-logic)
5. [Examples](#examples)
6. [Adding New Tools](#adding-new-tools)

---

## Overview

Sistem RAG-Tesis menggunakan **LangGraph ReAct Pattern** dengan:
- **1 Agent** (ReActPropertyAgent) - LLM yang memutuskan tool mana yang akan dipanggil
- **10 Tools** - Divided into Property Tools (7) dan Knowledge Tools (3)

### v2.0 Changes - Global Support

**Breaking Changes:**
- ❌ Removed: `LANDMARK_AREA_MAP` (Medan-specific hardcoding)
- ❌ Removed: `landmarks_to_expand` dari search_properties
- ❌ Removed: Default "Medan" dari semua tools
- ✅ Added: `search_properties_by_location` (location-based search dengan geocoding)
- ✅ Updated: Semua tools sekarang support global (multi-city, multi-country)

### Architecture Pattern

```
User Query
    ↓
ReActPropertyAgent (LLM)
    ↓
Decide: Which tool(s) to call?
    ↓
Execute Tool(s)
    ↓
Observe Results
    ↓
Decide: Need more info or respond?
    ↓
[Loop or Respond]
```

**Key Difference from Traditional Chains:**
- **OLD:** Hardcoded routing (if intent=search → search_chain)
- **NEW:** LLM decides which tool based on reasoning (ReAct pattern)

---

## 🤖 Agents

### ReActPropertyAgent

**Location:** [src/agents/react_agent.py](../src/agents/react_agent.py)

**Description:**
Agent utama yang menggunakan LangGraph untuk implement ReAct (Reasoning + Acting) pattern.

**Key Components:**

#### 1. State Definition
```python
class ReActAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: Optional[str]
    user_role: Optional[str]  # "agent", "admin", "user"
```

#### 2. System Prompt
Located at `react_agent.py:54-124`

Defines:
- Available tools dengan descriptions
- When to use which tool
- Source type detection (project vs listing)
- Language mirroring rules
- Workflow instructions

**Key Instructions:**
```
CAPABILITIES (Tools you can use):
1. search_properties - Search by filters/features (NO location)
2. search_properties_by_location - Search by location (auto-geocode) ✨ NEW
3. get_property_detail - Get details by ID
4. get_property_by_number - Get from last search by number
5. geocode_location - Convert location to coordinates (Global)
6. search_nearby - Search near landmark with radius (Global)
7. search_pois - Discover POIs in any city (Global)
8. search_knowledge - Search knowledge base
9. get_sales_tips - Get sales techniques
10. get_motivation - Get motivational message
```

#### 3. Graph Structure

```
START
  ↓
┌──────────────────────────────────┐
│  agent (LLM with tools bound)    │
│  - Receives messages             │
│  - Decides: call tools OR respond│
└──────────────────────────────────┘
  ↓
┌──────────────────────────────────┐
│  tools_condition                 │
│  - If tool_calls → go to tools   │
│  - If no tool_calls → END        │
└──────────────────────────────────┘
  ↓
┌──────────────────────────────────┐
│  tools (ToolNode)                │
│  - Execute tool(s)               │
│  - Return ToolMessage            │
└──────────────────────────────────┘
  ↓
[Loop back to agent]
```

#### 4. Key Features

| Feature | Implementation | Location |
|---------|---------------|----------|
| Tool Binding | `llm.bind_tools(self.tools)` | Line 181 |
| Memory | SQLite-based SlidingWindowMemory | Line 168, 287-289 |
| Checkpointing | In-memory MemorySaver | Line 184 |
| Hybrid Search | Configurable via `use_hybrid_search` | Line 150 |
| Streaming | `stream_chat()` method | Line 370-397 |

#### 5. Chat Interfaces

**Synchronous:**
```python
response = agent.chat(
    message="cari rumah di cemara asri",
    thread_id="user_123"
)
# Returns: string (agent's response)
```

**Asynchronous:**
```python
response = await agent.achat(
    message="cari rumah di cemara asri",
    thread_id="user_123"
)
```

**Streaming:**
```python
for event in agent.stream_chat(message, thread_id):
    print(event)  # Real-time updates
```

#### 6. Configurations

**Factory Function:** `create_property_react_agent()`

```python
agent = create_property_react_agent(
    property_adapter=adapter,
    model_name="gpt-4o-mini",        # LLM model
    temperature=0,                    # Deterministic
    enable_knowledge=True,            # Load knowledge base
    enable_memory=True,               # Persistent SQLite memory
    db_path="data/chat_history.db",  # Custom DB path
    max_history_messages=20,          # Sliding window size
)
```

**Direct Instantiation:**
```python
agent = ReActPropertyAgent(
    property_adapter=adapter,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    use_hybrid_search=True,           # API + ChromaDB re-ranking
    chat_memory=sqlite_memory,        # Optional persistent memory
)
```

---

## 🛠️ Tools

Total: **10 Tools** (7 Property + 3 Knowledge)

### Property Tools

#### 1. search_properties (UPDATED - No Location)

**Location:** [src/agents/tools.py:526-728](../src/agents/tools.py#L526-L728)

**Purpose:**
Search properties by **filters and text only** - NO specific location.
For location-based search, use `search_properties_by_location` instead.

**Input Schema:**
```python
class SearchPropertiesInput(BaseModel):
    query: Optional[str]            # Text for features/amenities (NOT location)
    property_type: Optional[str]    # "house", "shophouse", "land", "apartment"
    listing_type: Optional[str]     # "sale" or "rent"
    source: Optional[str]           # "project" (new) or "listing" (resale)
    min_price: Optional[int]        # Minimum price
    max_price: Optional[int]        # Maximum price
    min_bedrooms: Optional[int]     # Minimum bedrooms
    max_bedrooms: Optional[int]     # Maximum bedrooms
    min_floors: Optional[int]       # Minimum floors
    max_floors: Optional[int]       # Maximum floors
    amenities: Optional[List[str]]  # e.g., ["cctv", "swimming_pool"]
    in_complex: Optional[bool]      # True for properties in complex
    facing: Optional[str]           # Facing direction
    page: int = 1                   # Pagination
```

**When to Use:**
| Query Type | Use This Tool? |
|------------|----------------|
| "rumah murah 3 kamar" | ✅ Yes |
| "apartemen furnished" | ✅ Yes |
| "rumah **di ringroad**" | ❌ No → use search_properties_by_location |
| "house **in Brooklyn**" | ❌ No → use search_properties_by_location |

**Examples:**
```python
# Filter only
search_properties(min_bedrooms=3, max_bedrooms=3, property_type="house")

# Feature search
search_properties(query="furnished", property_type="apartment")

# Price filter
search_properties(listing_type="sale", max_price=1000000000)
```

---

#### 2. search_properties_by_location ✨ NEW

**Location:** [src/agents/tools.py:1348-1563](../src/agents/tools.py#L1348-L1563)

**Purpose:**
Search properties in a **specific location/area** with auto-geocoding.
Global support - works for any city/country.

**Input Schema:**
```python
class SearchPropertiesByLocationInput(BaseModel):
    location_keyword: str           # REQUIRED: Location to geocode ("ringroad", "Brooklyn")
    city: Optional[str]             # City context ("Medan", "New York")
    country: str = "Indonesia"      # Country context ("Indonesia", "USA")
    radius_km: float = 3.0          # Search radius
    query: Optional[str]            # Text for features (SEPARATE from location)
    property_type: Optional[str]    # "house", "shophouse", etc.
    listing_type: Optional[str]     # "sale" or "rent"
    source: Optional[str]           # "project" or "listing"
    min_price: Optional[int]
    max_price: Optional[int]
    min_bedrooms: Optional[int]
    max_bedrooms: Optional[int]
    # ... all other filters
    page: int = 1
```

**How It Works:**
```
User: "rumah furnished di ringroad medan"
                    ↓
LLM extracts:
  - location_keyword = "ringroad"
  - city = "Medan"
  - query = "furnished" (feature, not location)
                    ↓
Tool internally:
  1. Geocode("ringroad, Medan, Indonesia") → lat=3.58, lng=98.65
  2. API call: lat=3.58, lng=98.65, radius=3, search="furnished"
                    ↓
Result: Properties within 3km of ringroad with "furnished" keyword
```

**Examples (Global):**
```python
# Indonesian
search_properties_by_location(
    location_keyword="ringroad",
    city="Medan",
    property_type="house",
    listing_type="sale"
)

# English
search_properties_by_location(
    location_keyword="Brooklyn",
    city="New York",
    country="USA",
    property_type="house"
)

# With features
search_properties_by_location(
    location_keyword="Kemang",
    city="Jakarta",
    query="furnished",  # Feature search
    property_type="apartment"
)
```

**Output Format:**
```
Found 15 properties within 3km of ringroad (🔀 Hybrid):
📍 Center: Jl. Ring Road, Medan Sunggal, Medan, Indonesia
📌 Coordinates: 3.580123, 98.651234

1. **Rumah Modern Ring Road** 📏 0.5km
   🏗️ New by ABC Developer
   🔗 https://...
   📍 Jl. Ring Road No.10, Medan Sunggal
   💰 Rp 1.200.000.000 (sale)
   🏠 4 BR, 3 BA, LT 200m², LB 150m²

2. **Villa Ring Road Residence** 📏 1.2km
   ...
```

**Key Difference from search_properties:**
| Feature | search_properties | search_properties_by_location |
|---------|------------------|------------------------------|
| Location | ❌ No | ✅ Required (auto-geocode) |
| Coordinates | ❌ No | ✅ Yes (lat/lng/radius) |
| Global Support | N/A | ✅ Any city/country |
| Use Case | Features/filters only | "di [area]", "in [area]" |

---

#### 2. get_property_detail

**Location:** [src/agents/tools.py:367-409](../src/agents/tools.py#L367-L409)

**Purpose:**
Mendapatkan detail lengkap properti by ID.

**Input Schema:**
```python
class GetPropertyDetailInput(BaseModel):
    property_id: str  # Unique property ID
```

**Use Cases:**
- User asks for specific property by ID
- Need complete property information
- Update or detailed description required

**Output Format:**
```markdown
# Rumah Modern Cemara Asri

**ID:** prop-12345-abc
**Type:** house (sale)
**Price:** Rp 850.000.000

**Location:**
  - Address: Jl. Cemara No.10
  - Area: Cemara Asri
  - City: Medan

**Specifications:**
  - Bedrooms: 3
  - Bathrooms: 2
  - Land Area: 120 m²
  - Building Area: 90 m²

**Description:**
Rumah minimalis modern dengan taman luas...

**Features:** Taman, Garasi, Carport, CCTV
```

---

#### 3. get_property_by_number

**Location:** [src/agents/tools.py:411-492](../src/agents/tools.py#L411-L492)

**Purpose:**
Get detailed info dari cached search results by nomor urut.

**Input Schema:**
```python
class GetPropertyByNumberInput(BaseModel):
    number: int  # Result number from last search (1-10)
```

**Use Cases:**
User refers to property by number:
- "detail nomor 3"
- "yang ke-5 gimana?"
- "info lebih lanjut untuk no 8"

**Features:**
- Accesses `_last_search_results` cache
- Shows full details + contact info
- Includes agent/developer information

**Cache Behavior:**
- Max 10 results cached
- Cleared on new search
- Shared across search_properties and search_nearby

**Output Format:**
Similar to `get_property_detail`, plus:
```markdown
**Contact:**
- Agent: John Doe
- Phone: +62 812-3456-7890
- Developer: ABC Property
```

---

#### 4. geocode_location (UPDATED - Global Support)

**Location:** [src/agents/tools.py:1002-1030](../src/agents/tools.py#L1002-L1030)

**Purpose:**
Convert location name → coordinates (lat/lng). **Global support.**

**Input Schema:**
```python
class GeocodeLocationInput(BaseModel):
    location_name: str              # Location, landmark, or address
    city: Optional[str] = None      # City context for accuracy
    country: str = "Indonesia"      # Country context
```

**Technology:**
- Uses **Google Maps Geocoding API** (if configured)
- Fallback: **OpenStreetMap Nominatim** (free)
- No hardcoded city defaults

**Examples (Global):**
```python
# Indonesia
geocode_location(location_name="USU", city="Medan")

# Singapore
geocode_location(location_name="Orchard Road", city="Singapore", country="Singapore")

# USA
geocode_location(location_name="Central Park", city="New York", country="USA")
```

**Output Format:**
```
Coordinates for "Orchard Road":
- Latitude: 1.3048
- Longitude: 103.8318
- Full address: Orchard Road, Singapore 238840

Use these coordinates with search_nearby or search_properties_by_location.
```

---

#### 5. search_nearby (UPDATED - Global Support)

**Location:** [src/agents/tools.py:1032-1226](../src/agents/tools.py#L1032-L1226)

**Purpose:**
Search properties near a **landmark/POI** with proximity words.
Use for "dekat", "near", "sekitar" queries. **Global support.**

**Input Schema:**
```python
class SearchNearbyInput(BaseModel):
    location_name: str              # Landmark or POI name
    city: Optional[str] = None      # City context
    country: str = "Indonesia"      # Country context
    radius_km: float = 3.0          # Search radius
    property_type: Optional[str]
    listing_type: Optional[str]
    source: Optional[str]
    min_price: Optional[int]
    max_price: Optional[int]
```

**When to Use (vs search_properties_by_location):**
| Query | Tool |
|-------|------|
| "rumah **dekat** USU" | ✅ search_nearby |
| "house **near** Central Park" | ✅ search_nearby |
| "rumah **di** ringroad" | ❌ search_properties_by_location |
| "apartment **in** Orchard" | ❌ search_properties_by_location |

**Radius Guidelines:**
```
"dekat" / "near"     → radius_km=1
"sekitar" / "around" → radius_km=2
"kawasan" / "area"   → radius_km=3 (default)
```

**Examples (Global):**
```python
# Indonesian
search_nearby(location_name="USU", city="Medan", radius_km=1)

# English
search_nearby(
    location_name="Central Park",
    city="New York",
    country="USA",
    radius_km=2
)

# Singapore
search_nearby(
    location_name="Orchard MRT",
    city="Singapore",
    country="Singapore",
    radius_km=1
)
```

**Output Format:**
```
Ditemukan 12 properti dalam radius 3.0km dari USU:
(Koordinat pusat: 3.568200, 98.653900)
(Diurutkan dari yang terdekat)

1. **Rumah Padang Bulan** 📏 0.5km
   🏗️ Proyek Baru by XYZ Developer
   📍 Jl. Dr. Mansyur No.20, Padang Bulan
   💰 Rp 1.200.000.000 (sale)
   🏠 4 KT, 3 KM, LT 150m²
```

---

#### 6. search_pois (UPDATED - Global Support)

**Location:** [src/agents/tools.py:1228-1346](../src/agents/tools.py#L1228-L1346)

**Purpose:**
Discover POIs (Points of Interest) in **any city worldwide**.
First step when user asks for properties near a generic POI type.

**Input Schema:**
```python
class SearchPOIsInput(BaseModel):
    poi_type: str                   # "school", "mall", "hospital", "university"
    city: str                       # REQUIRED - no default
    country: str = "Indonesia"      # Country context
    limit: int = 5                  # Max POIs to return
```

**Problem Solved:**
Query "rumah dekat sekolah" sebelumnya gagal karena geocoding "sekolah, Medan" memberikan hasil acak. Sekarang agent menggunakan **multi-step autonomous workflow**.

**When to Use:**
| User Query | Action |
|------------|--------|
| "dekat sekolah" (generic) | ✓ Use search_pois first |
| "dekat mall" (generic) | ✓ Use search_pois first |
| "dekat Sun Plaza" (specific) | ✗ Use search_nearby directly |
| "dekat USU" (specific) | ✗ Use search_nearby directly |

**Multi-Step Workflow:**

```
User: "cari rumah dekat mall di medan"

┌───────────────────────────────────────────────────────────┐
│ ITERATION 1: Discover POIs                                │
├───────────────────────────────────────────────────────────┤
│ Tool: search_pois(poi_type="mall", city="Medan")         │
│ Result:                                                   │
│   1. Sun Plaza (Medan Kota)                              │
│   2. Centre Point (Medan Maimun)                         │
│   3. Plaza Medan Fair (Medan Petisah)                    │
│   4. Manhattan Times Square (Medan Petisah)              │
│   5. Delipark Podomoro (Medan Timur)                     │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ ITERATION 2: Search near EACH POI (parallel)             │
├───────────────────────────────────────────────────────────┤
│ Tool: search_nearby(location_name="Sun Plaza", radius=2)  │
│ Tool: search_nearby(location_name="Centre Point", ...)    │
│ Tool: search_nearby(location_name="Plaza Medan Fair", ...)│
│ (... executed in parallel for efficiency ...)             │
└───────────────────────────────────────────────────────────┘
                          ↓
┌───────────────────────────────────────────────────────────┐
│ ITERATION 3: Generate Response                           │
├───────────────────────────────────────────────────────────┤
│ "Berikut rumah dekat mall di Medan:                      │
│                                                           │
│ **Dekat Sun Plaza:**                                      │
│ 1. Rumah A - 260m dari Sun Plaza                         │
│ 2. Rumah B - 450m dari Sun Plaza                         │
│                                                           │
│ **Dekat Centre Point:**                                   │
│ 1. Rumah C - 300m dari Centre Point"                     │
└───────────────────────────────────────────────────────────┘
```

**Pre-defined POIs Database:**

**Schools (5):**
| Name | Area | Coordinates |
|------|------|-------------|
| SMA Negeri 1 Medan | Medan Kota | 3.5847, 98.6733 |
| Sekolah Sutomo 1 | Medan Timur | 3.5912, 98.6789 |
| SMA Methodist 1 | Medan Kota | 3.5856, 98.6678 |
| SMA Al-Azhar Medan | Helvetia | 3.5634, 98.6234 |
| SD Binus School Medan | Ring Road | 3.5423, 98.6123 |

**Malls (7):**
| Name | Area | Coordinates |
|------|------|-------------|
| Sun Plaza | Medan Kota | 3.5901, 98.6739 |
| Centre Point Medan | Medan Maimun | 3.5850, 98.6700 |
| Plaza Medan Fair | Medan Petisah | 3.5890, 98.6650 |
| Manhattan Times Square | Medan Petisah | 3.5823, 98.6612 |
| Delipark Podomoro | Medan Timur | 3.5789, 98.6567 |
| Grand Palladium | Medan Area | 3.5512, 98.6834 |
| Cambridge City Square | Medan Marelan | 3.6123, 98.6234 |

**Hospitals (6):**
| Name | Area | Coordinates |
|------|------|-------------|
| RS Adam Malik | Padang Bulan | 3.5648, 98.6568 |
| RS Columbia Asia Medan | Medan Kota | 3.5867, 98.6712 |
| RS Elisabeth Medan | Medan Kota | 3.5834, 98.6689 |
| RS Murni Teguh | Sunggal | 3.5523, 98.6234 |
| RS Royal Prima | Medan Marelan | 3.6123, 98.6345 |
| RS Siloam Medan | Medan Kota | 3.5789, 98.6623 |

**Universities (5):**
| Name | Area | Coordinates |
|------|------|-------------|
| USU | Padang Bulan | 3.5648, 98.6568 |
| UNIMED | Medan Tuntungan | 3.6120, 98.7000 |
| UINSU | Medan Perjuangan | 3.5723, 98.6834 |
| UMSU | Medan Area | 3.5656, 98.6878 |
| Universitas Katolik St. Thomas | Medan Selayang | 3.5534, 98.6123 |

**Output Format:**
```
Ditemukan 5 Mall/Pusat Perbelanjaan di Medan:

Gunakan nama-nama ini dengan search_nearby untuk mencari properti di sekitarnya:

1. **Sun Plaza**
   📍 Area: Medan Kota
   📌 Koordinat: 3.5901, 98.6739

2. **Centre Point Medan**
   📍 Area: Medan Maimun
   📌 Koordinat: 3.5850, 98.6700

...

**Contoh penggunaan:**
- search_nearby(location_name="Sun Plaza", radius_km=2)
```

**Test Results (24 Jan 2026):**
```
Query: "cari rumah dekat mall di medan"

Tool calls: 6 total
  - search_pois: 1
  - search_nearby: 5 (parallel)

Successful results: 6/6 (no errors)
Final response: 2506 chars

Malls in response: Sun Plaza, Centre Point, Plaza Medan Fair, Manhattan
```

**UX Enhancement:**
Jika tidak ada hasil untuk beberapa POI, agent akan menyarankan:
> "Jika Anda memiliki nama sekolah/mall/rumah sakit tertentu yang ingin dicari, silakan beritahu saya agar saya bisa membantu mencari properti terdekat dengan lebih akurat."

---

### Knowledge Tools

#### 6. search_knowledge

**Location:** [src/agents/tools.py:700-747](../src/agents/tools.py#L700-L747)

**Purpose:**
Search knowledge base (ChromaDB) untuk real estate info, sales techniques, motivation.

**Input Schema:**
```python
class SearchKnowledgeInput(BaseModel):
    query: str                      # Question or topic
    category: Optional[str]         # Filter by category
```

**Categories:**
- `sales-techniques` - First meeting, negotiation, objection handling, marketing
- `real-estate-knowledge` - Area guide, KPR, legal docs, pajak properti
- `motivational` - Motivasi untuk agen

**Technology:**
- ChromaDB vector similarity search
- Markdown documents chunked (500 chars, 50 overlap)
- Returns top 5 most similar chunks

**Examples:**
```python
# Search real estate knowledge
search_knowledge(query="apa itu SHM?", category="real-estate-knowledge")

# Search sales techniques
search_knowledge(query="cara handle objection", category="sales-techniques")

# General search (all categories)
search_knowledge(query="tips closing deal")
```

**Output Format:**
```
Berikut informasi terkait 'SHM':

**1. From: legal-documents.md**
SHM (Sertifikat Hak Milik) adalah bukti kepemilikan tanah yang paling kuat di Indonesia. SHM memberikan hak penuh kepada pemilik untuk menggunakan, menjual, atau mewariskan tanah tersebut...

**2. From: pajak-properti.md**
Properti dengan SHM umumnya memiliki nilai lebih tinggi karena status kepemilikan yang jelas...
```

---

#### 7. get_sales_tips

**Location:** [src/agents/tools.py:749-794](../src/agents/tools.py#L749-L794)

**Purpose:**
Mendapatkan curated sales tips untuk topik tertentu.

**Input:**
```python
@tool
def get_sales_tips(topic: str) -> str:
```

**Curated Topics:**

**1. Closing:**
```
Tips untuk Closing yang Efektif:
1. Bangun trust terlebih dahulu - jangan buru-buru closing
2. Pahami kebutuhan dan concern klien
3. Gunakan teknik "assumptive close"
4. Atasi objection dengan empati
5. Berikan deadline yang wajar
6. Follow up secara konsisten
```

**2. Objection Handling:**
```
Cara Handle Objection:
1. Dengarkan sampai selesai, jangan interrupt
2. Validasi concern: "Saya mengerti..."
3. Tanyakan lebih detail
4. Berikan solusi, bukan excuses
5. Gunakan social proof jika ada
```

**3. Follow Up:**
```
Tips Follow Up:
1. Follow up dalam 24 jam setelah meeting
2. Variasikan channel: WA, call, email
3. Berikan nilai tambah setiap follow up
4. Jangan hanya tanya "sudah ada keputusan?"
5. Update info property baru yang relevan
```

**Fallback:**
Generic tips jika topic tidak match.

---

#### 8. get_motivation

**Location:** [src/agents/tools.py:796-838](../src/agents/tools.py#L796-L838)

**Purpose:**
Memberikan motivational message untuk agen properti.

**Input:**
```python
@tool
def get_motivation() -> str:
```

**Features:**
- Random selection dari 3 curated messages
- Quotes + practical tips
- Encouraging tone

**Sample Messages:**

**Message 1:**
```
🌟 Ingat, setiap "tidak" adalah langkah menuju "ya" berikutnya!

"Success is not final, failure is not fatal: it is the courage to continue that counts."
- Winston Churchill

Kamu sudah berani memilih karir sebagai agen properti.
Itu sudah setengah dari kesuksesan.
Tetap semangat, hasil akan mengikuti usaha! 💪
```

**Message 2:**
```
💪 Hari ini mungkin berat, tapi ingat:

Setiap agen top pernah di posisimu sekarang.
Yang membedakan adalah mereka tidak berhenti.

Tips untuk hari ini:
1. Fokus pada 1 prospek terbaik
2. Berikan service terbaik
3. Sisanya serahkan pada proses

Kamu bisa! 🚀
```

**Message 3:**
```
🔥 The harder you work, the luckier you get!

Di properti, konsistensi mengalahkan bakat.
Yang follow up 10x akan menang dari yang pintar tapi malas.

Terus bergerak, terus connect dengan orang.
Rezekimu tidak akan tertukar! 💫
```

---

## 🎯 Tool Selection Logic

### How Agent Decides Which Tool to Use

Agent (LLM) memutuskan berdasarkan:

#### 1. Keyword Detection

| User Input | Detected Intent | Tool Called |
|------------|----------------|-------------|
| "rumah murah 3 kamar" | Features only | `search_properties` |
| "apartemen furnished" | Features only | `search_properties` |
| **"rumah di ringroad"** | **Location search** | **`search_properties_by_location`** |
| **"house in Brooklyn"** | **Location search** | **`search_properties_by_location`** |
| "dekat USU" | Proximity (specific) | `search_nearby` |
| "near Central Park" | Proximity (specific) | `search_nearby` |
| "dekat sekolah" | Generic POI | `search_pois` → `search_nearby` |
| "near mall" | Generic POI | `search_pois` → `search_nearby` |
| "detail nomor 3" | Get by number | `get_property_by_number` |
| "koordinat Kemang" | Geocoding | `geocode_location` |
| "tips closing" | Sales tips | `get_sales_tips` |
| "butuh motivasi" | Motivation | `get_motivation` |
| "apa itu SHM?" | Knowledge search | `search_knowledge` |

#### 2. Source Type Detection

| Keywords | Detected Source | Parameter |
|----------|----------------|-----------|
| "proyek", "project", "developer", "primary" | New properties | `source="project"` |
| "secondary", "second", "bekas", "resale" | Resale properties | `source="listing"` |
| No keywords | Search both | `source=None` |

#### 3. Property Type Detection

| Keywords | Detected Type | Parameter |
|----------|--------------|-----------|
| "rumah", "house" | House | `property_type="house"` |
| "ruko", "shophouse" | Shophouse | `property_type="shophouse"` |
| "tanah", "land" | Land | `property_type="land"` |
| "apartemen", "apartment" | Apartment | `property_type="apartment"` |

#### 4. Comparative Questions

**Special Handling:**
Questions like "yang paling murah?", "mana yang terluas?" → **No tool call**

Agent analyzes from previous search results in chat history.

Example:
```
User: "cari rumah di sunggal"
Agent: [calls search_properties, shows 10 results]

User: "yang paling murah?"
Agent: [NO tool call, analyzes previous results]
Response: "Yang paling murah adalah nomor 5: Rumah Sunggal dengan harga Rp 650 juta..."
```

---

## 📚 Examples

### Example 1: Basic Search

```
User: "cari rumah di cemara asri"

Agent Decision:
→ Tool: search_properties
→ Parameters: query="cemara asri", property_type="house"

Execution:
1. Hybrid search: API + ChromaDB re-ranking
2. Cache top 10 results
3. Format with emoji indicators

Response:
Ditemukan 15 properti (🔀 Hybrid):

1. **Rumah Modern Cemara Asri** [relevance: 0.87]
   🏗️ Proyek Baru
   📍 Cemara Asri, Medan
   💰 Rp 850.000.000 (sale)
   🏠 3 KT, 2 KM, LT 120m², LB 90m²
...
```

### Example 2: Multi-Tool Orchestration

```
User: "cari rumah dekat USU radius 3km, nomor 2 gimana detailnya?"

Agent Decision (Turn 1):
→ Tool: search_nearby
→ Parameters: location_name="USU", radius_km=3, property_type="house"

Agent Response:
Ditemukan 8 properti dalam radius 3km dari USU...

Agent Decision (Turn 2):
→ Tool: get_property_by_number
→ Parameters: number=2

Agent Response:
# Rumah Padang Bulan

**ID:** prop-789
**Contact:**
- Agent: Jane Doe
- Phone: +62 811-2345-6789
...
```

### Example 3: Complex Query with Filters

```
User: "cari proyek baru di medan, 3 kamar, maksimal 1 miliar"

Agent Decision:
→ Tool: search_properties
→ Parameters:
  - query="medan"
  - source="project"
  - min_bedrooms=3
  - max_price=1000000000

Execution:
1. API filters: source=project, bedrooms≥3, price≤1M
2. Semantic re-ranking untuk "proyek baru"
3. Return sorted results

Response:
Ditemukan 5 properti (🔀 Hybrid):

1. **Cluster Baru Setia Budi** [relevance: 0.92]
   🏗️ Proyek Baru by XYZ Developer
   💰 Rp 950.000.000
   🏠 3 KT, 2 KM
...
```

### Example 4: Knowledge Query

```
User: "bagaimana cara handle objection dari client yang bilang harga terlalu mahal?"

Agent Decision:
→ Tool: get_sales_tips
→ Parameters: topic="objection"

Response:
Cara Handle Objection:
1. Dengarkan sampai selesai, jangan interrupt
2. Validasi concern mereka: "Saya mengerti..."
3. Tanyakan lebih detail: "Bisa jelaskan lebih lanjut?"
4. Berikan solusi, bukan excuses
5. Gunakan social proof jika ada

Untuk objection harga, coba tunjukkan:
- Value yang didapat (lokasi, fasilitas, ROI)
- Comparable properties di area yang sama
- Fleksibilitas payment terms
```

---

## 🔧 Adding New Tools

### Step 1: Define Input Schema

```python
# In src/agents/tools.py

class MyNewToolInput(BaseModel):
    """Input schema for my new tool"""
    param1: str = Field(description="Description for LLM")
    param2: Optional[int] = Field(default=None, description="Optional param")
```

### Step 2: Create Tool Function

```python
@tool(args_schema=MyNewToolInput)
def my_new_tool(param1: str, param2: Optional[int] = None) -> str:
    """
    Tool description for LLM to understand when to use this.

    Use this when:
    - Specific use case 1
    - Specific use case 2

    Examples:
    - User asks "..." -> my_new_tool(param1="...")
    """
    try:
        # Implementation
        result = do_something(param1, param2)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Step 3: Add to Tool Factory

```python
def create_property_tools(...) -> list:
    # ... existing tools ...

    @tool(args_schema=MyNewToolInput)
    def my_new_tool(...):
        # implementation
        pass

    return [
        search_properties,
        get_property_detail,
        # ... other tools ...
        my_new_tool,  # Add here
    ]
```

### Step 4: Update System Prompt

```python
# In src/agents/react_agent.py:REACT_SYSTEM_PROMPT

REACT_SYSTEM_PROMPT = """
...
CAPABILITIES (Tools you can use):
1. search_properties - ...
2. get_property_detail - ...
...
9. my_new_tool - Description of what this tool does

WHEN TO USE MY_NEW_TOOL:
- Use case 1
- Use case 2
...
"""
```

### Step 5: Test the Tool

```python
# scripts/test_new_tool.py

from src.adapters.metaproperty import MetaPropertyAPIAdapter
from src.agents.react_agent import create_property_react_agent

adapter = MetaPropertyAPIAdapter(...)
agent = create_property_react_agent(adapter)

# Test via agent
response = agent.chat("test query that should trigger new tool")
print(response)
```

---

## 📊 Tools Summary Table

| # | Tool Name | Category | Input Params | Primary Use Case | Global |
|---|-----------|----------|--------------|------------------|--------|
| 1 | search_properties | Property | query, filters | Filter + text search (NO location) | N/A |
| 2 | **search_properties_by_location** ✨ | **Property** | **location, city, country** | **Search by location (auto-geocode)** | ✅ |
| 3 | get_property_detail | Property | property_id | Get full details by ID | N/A |
| 4 | get_property_by_number | Property | number | Get from cached results | N/A |
| 5 | geocode_location | Property | location, city, country | Name → coordinates | ✅ |
| 6 | search_nearby | Property | location, city, country, radius | Search near landmark ("dekat", "near") | ✅ |
| 7 | search_pois | Property | poi_type, city, country | Discover POIs in any city | ✅ |
| 8 | search_knowledge | Knowledge | query, category | Search knowledge base | N/A |
| 9 | get_sales_tips | Knowledge | topic | Get sales tips | N/A |
| 10 | get_motivation | Knowledge | (none) | Get motivation | N/A |

### Tool Selection Decision Tree

```
User Query
    │
    ├─ Contains location ("di", "in", "daerah")?
    │   │
    │   ├─ Yes + proximity word ("dekat", "near", "sekitar")?
    │   │   └─ → search_nearby
    │   │
    │   └─ Yes + area keyword only?
    │       └─ → search_properties_by_location
    │
    ├─ Generic POI ("dekat sekolah", "near mall")?
    │   └─ → search_pois → search_nearby (multi-step)
    │
    └─ No location (features/filters only)?
        └─ → search_properties
```

---

## 🚀 Best Practices

### 1. Tool Design
- **Single Responsibility:** Each tool does one thing well
- **Clear Description:** Help LLM understand when to use
- **Error Handling:** Always return string (never raise)
- **Type Safety:** Use Pydantic schemas

### 2. Agent Usage
- **Thread IDs:** Use unique thread_id per user/conversation
- **Memory Management:** Clear old conversations periodically
- **Error Recovery:** Agent retries with different tools on failure

### 3. Performance
- **Caching:** Cache results untuk reference by number
- **Hybrid Search:** Balance API speed + semantic relevance
- **Lazy Loading:** Only load knowledge base if needed

---

## 📖 Related Documentation

- [06-nearby-search-architecture.md](./06-nearby-search-architecture.md) - Legacy nearby search (deprecated)
- [08-chromadb-ingestion-guide.md](./08-chromadb-ingestion-guide.md) - Knowledge base setup
- [09-improvement-roadmap.md](./09-improvement-roadmap.md) - Future improvements

---

*Last updated: 2026-01-25 (v2.0)*

**Changelog v2.0:**
- ✨ Added: `search_properties_by_location` - Location-based search with auto-geocoding
- 🌍 Updated: All location tools now support global (any city/country)
- 🗑️ Removed: `LANDMARK_AREA_MAP` - No more Medan-specific hardcoding
- 🗑️ Removed: `landmarks_to_expand` - Geocoding handles all locations dynamically
- ✏️ Updated: `search_properties` - Now for filters/features only (no location)
- ✏️ Updated: `geocode_location` - Added city/country params
- ✏️ Updated: `search_nearby` - Added city/country params
- ✏️ Updated: `search_pois` - City is now required (no default)

**Total Tools: 10** (was 9)
