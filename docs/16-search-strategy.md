# Strategi Pencarian Properti RAG Chatbot

Dokumen ini menjelaskan strategi dan konsep pencarian yang diimplementasikan dalam sistem RAG Property Chatbot.

## 1. Pemilihan Tool Pencarian

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Apakah ada kata "dekat [landmark spesifik]"?                   │
│  (dekat USU, dekat Sun Plaza, dekat RS Adam Malik)              │
└─────────────────────────────────────────────────────────────────┘
          │ YA                              │ TIDAK
          ▼                                 ▼
   search_nearby()              ┌───────────────────────────────┐
   + geocoding                  │ Apakah ada kata "dekat [POI   │
                                │ generic]"? (dekat mall,       │
                                │ dekat sekolah, dekat RS)      │
                                └───────────────────────────────┘
                                     │ YA              │ TIDAK
                                     ▼                 ▼
                              search_pois() →    search_properties()
                              search_nearby()    (keyword-based)
```

### Tool yang Tersedia

| Tool | Fungsi | Kapan Digunakan |
|------|--------|-----------------|
| `search_properties` | Pencarian keyword + filter | Query berbasis area/lokasi |
| `search_nearby` | Pencarian radius dari titik koordinat | Query dengan landmark spesifik |
| `search_pois` | Cari POI (sekolah, mall, RS) | Query "dekat [POI generic]" |
| `get_property_detail` | Detail properti by ID | User minta detail spesifik |
| `get_property_by_number` | Detail by nomor hasil | "nomor 3", "yang ke-5" |
| `geocode_location` | Konversi nama → koordinat | Internal untuk search_nearby |

---

## 2. Kategori Filter

| Kategori | Filter | Contoh Query |
|----------|--------|--------------|
| **Lokasi** | query, city, radius | "di cemara asri", "medan johor" |
| **Harga** | min_price, max_price | "harga 1M an", "dibawah 500 juta" |
| **Spesifikasi** | bedrooms, floors, facing | "3 kamar", "2 lantai", "hadap utara" |
| **Tipe** | property_type, listing_type | "rumah", "ruko", "dijual", "disewa" |
| **Sumber** | source, in_complex | "proyek baru", "dalam komplek" |
| **Fasilitas** | amenities | "CCTV", "kolam renang", "full furnished" |

### Detail Filter

#### Property Type
- `house` - Rumah
- `shophouse` - Ruko
- `land` - Tanah
- `apartment` - Apartemen
- `warehouse` - Gudang
- `office` - Kantor
- `villa` - Villa

#### Listing Type
- `sale` - Dijual
- `rent` - Disewa

#### Source (Market Type)
- `project` - Primary market (dari developer)
- `listing` - Secondary market (resale)

---

## 3. Hybrid Search Strategy (60/40)

```
┌─────────────────────────────────────────────────────────────────┐
│                     HYBRID SEARCH                                │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
┌───────────────────┐                    ┌───────────────────┐
│   API SEARCH      │                    │  CHROMADB SEARCH  │
│   (40% weight)    │                    │   (60% weight)    │
├───────────────────┤                    ├───────────────────┤
│ • Structured      │                    │ • Semantic        │
│   filters         │                    │   matching        │
│ • price_min/max   │                    │ • "taman luas"    │
│ • bedrooms        │                    │ • "view bagus"    │
│ • floors          │                    │ • "lokasi         │
│ • property_type   │                    │   strategis"      │
│ • in_complex      │                    │ • amenity         │
│ • facing          │                    │   keywords        │
└───────────────────┘                    └───────────────────┘
        │                                           │
        └─────────────────────┬─────────────────────┘
                              ▼
                    ┌───────────────────┐
                    │   RE-RANKING      │
                    │ combined_score =  │
                    │ 0.6×semantic +    │
                    │ 0.4×api_order     │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  FINAL RESULTS    │
                    │  (Top 10)         │
                    └───────────────────┘
```

### Kapan Menggunakan Masing-masing Search

| Kondisi | Search Method | Alasan |
|---------|---------------|--------|
| Query dengan filter exact | API Search | Filter struktural akurat |
| Query deskriptif | Semantic Search | "taman luas", "view bagus" |
| Query kombinasi | Hybrid | Gabungan keduanya |
| API return 0 results | Fallback Semantic | ChromaDB sebagai backup |

---

## 4. Filter Baru: Complex & Facing

### Complex/Standalone Filter (`in_complex`)

```python
# Data di ChromaDB metadata
"complex_name": "Cemara Asri"    # Nama komplek (jika ada)
"in_complex": 1                   # 1 = dalam komplek, 0 = standalone

# User query mapping
"rumah dalam komplek"     → in_complex=True
"rumah standalone"        → in_complex=False
"rumah di cluster"        → in_complex=True
"rumah berdiri sendiri"   → in_complex=False
```

**Keywords untuk deteksi:**
- **Dalam Komplek:** "dalam komplek", "di komplek", "di cluster", "perumahan", "di kompleks"
- **Standalone:** "standalone", "bukan komplek", "berdiri sendiri", "di luar komplek"

### Facing Direction Filter (`facing`)

```python
# Data di ChromaDB metadata
"facing": "utara"    # atau selatan, timur, barat, timur_laut, dll

# User query mapping
"hadap utara"         → facing="utara"
"menghadap timur"     → facing="timur"
"arah selatan"        → facing="selatan"
```

**Values yang didukung:**
- `utara` (North)
- `selatan` (South)
- `timur` (East)
- `barat` (West)
- `timur_laut` (Northeast)
- `tenggara` (Southeast)
- `barat_daya` (Southwest)
- `barat_laut` (Northwest)

---

## 5. Alur Data Filter

```
User: "cari rumah dalam komplek hadap utara di cemara asri harga 1M an"
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ LLM PARSING (GPT-4o-mini)                                       │
├─────────────────────────────────────────────────────────────────┤
│ query = "cemara asri"                                           │
│ property_type = "house"                                         │
│ in_complex = True          ← "dalam komplek"                    │
│ facing = "utara"           ← "hadap utara"                      │
│ min_price = 900000000      ← "harga 1M an"                      │
│ max_price = 1100000000                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ API REQUEST                                                      │
│ GET /api/v1/properties?                                         │
│   search=cemara+asri                                            │
│   property_type=house                                           │
│   in_complex=1                                                  │
│   facing=utara                                                  │
│   price_min=900000000                                           │
│   price_max=1100000000                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CHROMADB SEMANTIC RERANK                                        │
│ Query: "cemara asri rumah komplek hadap utara"                  │
│ Filter: in_complex=1, facing="utara"                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Radius Dinamis (Proximity Keywords)

| Keyword | Radius | Contoh |
|---------|--------|--------|
| "dekat" | 1 km | "rumah dekat USU" |
| "sekitar/sekitaran" | 2 km | "rumah sekitar Sun Plaza" |
| "kawasan/daerah/wilayah" | 3 km | "rumah di kawasan Cemara Asri" |
| "inti kota/pusat kota" | 3 km | "rumah di inti kota medan" |

### Special Cases

| Query Pattern | Tool | Behavior |
|---------------|------|----------|
| "daerah [area name]" | `search_properties` | Keyword search, no radius |
| "inti kota [city]" | `search_nearby` | Geocode city center + 3km radius |
| "dekat [landmark]" | `search_nearby` | Geocode landmark + 1km radius |

---

## 7. Bedroom/Floor Exact Match

```python
# "3 kamar" (exact) → agent harus set BOTH min dan max
min_bedrooms = 3
max_bedrooms = 3

# "minimal 3 kamar" → hanya min
min_bedrooms = 3
max_bedrooms = None

# "maksimal 3 kamar" → hanya max
min_bedrooms = None
max_bedrooms = 3
```

| User Query | min_bedrooms | max_bedrooms |
|------------|--------------|--------------|
| "3 kamar" | 3 | 3 |
| "minimal 3 kamar" | 3 | None |
| "paling sedikit 3 kamar" | 3 | None |
| "maksimal 3 kamar" | None | 3 |
| "paling banyak 3 kamar" | None | 3 |

Sama berlaku untuk `min_floors` / `max_floors`.

---

## 8. Amenity/Facility Search

### Unit Amenities (Individual Property)
```
cctv, wifi, ac, garage, carport, furnished, semi_furnished, water_heater
```

### Complex Facilities (Cluster/Perumahan)
```
swimming_pool, security_24, basketball_court, tennis_court,
jogging_track, playground, clubhouse, gym, taman
```

### Strategy untuk Complex Facilities

Untuk fasilitas komplek seperti "lapangan basket", sistem:
1. Tambahkan ke `amenities` list
2. **DAN** sertakan term Indonesia dalam query untuk semantic matching

```python
# Query: "rumah dalam komplek dengan lapangan basket"
amenities = ['basketball_court']
query = "komplek lapangan basket"  # Include Indonesian term!
```

Ini penting karena deskripsi properti di database biasanya menggunakan bahasa Indonesia.

---

## 9. Multi-Step POI Search

Ketika user bertanya "dekat mall/sekolah/RS" tanpa nama spesifik:

```
Step 1: search_pois(poi_type="mall", city="Medan")
        → Returns: "Sun Plaza", "Centre Point", "Plaza Medan Fair"

Step 2: search_nearby(location_name="Sun Plaza", radius_km=2)
        search_nearby(location_name="Centre Point", radius_km=2)

Step 3: Combine & present results grouped by POI
```

### POI Types Supported
- `school` / `sekolah`
- `mall` / `pusat perbelanjaan`
- `hospital` / `rumah sakit`
- `university` / `universitas`

---

## 10. Context Memory untuk Follow-up

Sistem menyimpan kriteria pencarian terakhir untuk mendukung percakapan multi-turn:

### "Pilihan lain" Pattern
```
User: "cari rumah di cemara asri"
Agent: [shows results]
User: "pilihan lain?"
Agent: [recalls criteria, searches again with same params]
```

### Filter Modification Pattern
```
User: "cari rumah di cemara asri"
Agent: [shows results]
User: "yang 3 lantai"
Agent: [adds min_floors=3, max_floors=3 to previous criteria]
```

### Keywords untuk Deteksi
- **More results:** "lainnya", "pilihan lain", "ada lagi", "selain itu"
- **Filter modify:** "yang", "dengan", "tapi", "kalau yang"
- **Price filter:** "di bawah", "maksimal", "minimal", "kisaran"
- **Room filter:** "kamar", "lantai", "tingkat"

---

## 11. File yang Terlibat

| File | Role |
|------|------|
| `src/agents/tools.py` | Tool definitions & input schemas |
| `src/agents/react_agent.py` | System prompt & agent logic |
| `src/knowledge/hybrid_search.py` | Hybrid search implementation |
| `src/knowledge/property_store.py` | ChromaDB metadata storage |
| `src/adapters/metaproperty.py` | API request building |
| `src/adapters/base.py` | SearchCriteria dataclass |

---

## 12. Diagram Lengkap

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUERY                                   │
│            "cari rumah dalam komplek dekat mall harga 1M"           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GPT-4o-mini (LLM Parsing)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Extracted Parameters:                                          │  │
│  │ - property_type: "house"                                       │  │
│  │ - in_complex: True                                             │  │
│  │ - min_price: 900000000                                         │  │
│  │ - max_price: 1100000000                                        │  │
│  │ - Tool: search_pois (karena "dekat mall" generic)             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Tool Execution Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │  search_pois    │→ │  search_nearby  │→ │ Combined Results    │  │
│  │  (Google Maps)  │  │  (per mall)     │  │                     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Hybrid Search Service                            │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │     API Search       │    │   ChromaDB Search    │               │
│  │  (40% weight)        │    │   (60% weight)       │               │
│  │  • price filter      │    │  • semantic match    │               │
│  │  • in_complex=1      │    │  • re-ranking        │               │
│  │  • geo radius        │    │                      │               │
│  └──────────────────────┘    └──────────────────────┘               │
│                    │                    │                            │
│                    └────────┬───────────┘                            │
│                             ▼                                        │
│                    ┌──────────────────┐                              │
│                    │  Final Ranking   │                              │
│                    │  (Top 10)        │                              │
│                    └──────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Response to User                             │
│  "Berikut rumah dalam komplek dekat mall dengan harga sekitar 1M:   │
│   1. Rumah di Cemara Asri (dekat Sun Plaza 1.2km)...                │
│   2. Rumah di Setia Budi (dekat Centre Point 0.8km)..."             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 13. URL Enrichment

Saat pencarian menggunakan ChromaDB (semantic search atau fallback), properti mungkin tidak memiliki `url_view` jika belum di-resync. Sistem otomatis menambahkan URL:

```
ChromaDB search → property IDs tanpa url_view
      ↓
API call: GET /api/v1/properties?ids=1,2,3
      ↓
Merge url_view dari API response
      ↓
Return hasil dengan URL lengkap
```

**Kondisi URL Enrichment:**
- Property dari ChromaDB tidak memiliki `slug` atau `url_view`
- Adapter tersedia (tidak None)
- Ada property IDs yang perlu di-enrich

**Lihat juga:** [docs/08-chromadb-ingestion-guide.md](08-chromadb-ingestion-guide.md#url-enrichment)

---

## Referensi

- [docs/18-evaluation-v2-confusion-matrix.md](18-evaluation-v2-confusion-matrix.md) - Metodologi evaluasi v2 (constraint-based)
- [docs/15-embedding-optimization-report.md](15-embedding-optimization-report.md) - Optimisasi embedding
- [src/agents/react_agent.py](../src/agents/react_agent.py) - System prompt lengkap

---

*Last updated: 2026-01-25*
