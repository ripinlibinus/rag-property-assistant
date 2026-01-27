# RAG Property Chatbot - Evaluation Results & Improvements (V1)

> **Note:** Dokumen ini berisi hasil evaluasi menggunakan metodologi V1 (IR metrics: MRR, Precision@K).
> Untuk hasil evaluasi terbaru menggunakan metodologi V2 (constraint-based dengan confusion matrix),
> lihat folder `data/evaluation/v2/` dan dokumentasi di [docs/18-evaluation-v2-confusion-matrix.md](18-evaluation-v2-confusion-matrix.md).

## Executive Summary

Dokumen ini merangkum hasil evaluasi sistem RAG Property Chatbot dan rencana improvement berdasarkan temuan evaluasi.

**Tanggal Evaluasi:** 24 Januari 2026
**Test Method:** Hybrid (60% Semantic, 40% API)
**LLM Model:** GPT-4o-mini
**Total Queries:** 30

---

## 1. Evaluation Results

### 1.1 Overall Metrics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Precision@5** | 44.14% | ~2 dari 5 hasil relevan |
| **Overall Precision** | 46.09% | < 50% hasil relevan |
| **MRR** | 0.476 | Relevan pertama ~rank 2-3 |
| **Success Rate** | 60% (18/30) | 12 query gagal |
| **Coverage** | 96.67% (29/30) | Hampir semua query ada hasil |
| **Response Quality** | 2.92/5 | Di bawah rata-rata |

### 1.2 Performance by Category

#### Excellent Performance (100% Success)

| Category | Queries | P@5 | MRR | Quality | Notes |
|----------|---------|-----|-----|---------|-------|
| location_simple | #1-3 | 100% | 1.000 | 5/5 | Pencarian lokasi dasar bekerja sempurna |
| project_search | #29-30 | 100% | 1.000 | 4.5/5 | Pencarian nama project bekerja baik |
| location_intent | #8 | 80% | 1.000 | 4/5 | "Client cari sewa dekat USU" |

#### Moderate Performance (50-80% Success)

| Category | Queries | P@5 | MRR | Quality | Issues |
|----------|---------|-----|-----|---------|--------|
| location_price | #4,7,9 | 60% | 0.548 | 2.67/5 | Query #7 "dekat podomoro" gagal |
| location_price_spec | #5,6,13 | 53% | 0.567 | 3.33/5 | Filter kombinasi kurang akurat |
| property_type | #10-12 | 53% | 0.667 | 3/5 | "Gudang di KIM" tidak ditemukan |
| context_followup | #14-15,17 | 20% | 0.400 | 2.33/5 | "Pilihan lain" tidak konsisten |
| context_modify | #16,18 | 20% | 0.125 | 1/5 | Filter "3 lantai" tidak dijalankan |

#### Failed Categories (0% Success)

| Category | Queries | P@5 | MRR | Quality | Root Cause |
|----------|---------|-----|-----|---------|------------|
| **feature_search** | #19-23 | 0% | N/A | 1/5 | Tidak bisa search fasilitas (CCTV, WiFi, AC) |
| **nearby_search** | #24-26 | 0% | N/A | N/A | "Dekat mall/sekolah" geocoding tidak akurat |
| **complex_query** | #27 | 0% | N/A | N/A | Kombinasi banyak filter gagal |

### 1.3 Detailed Query Analysis

#### Queries yang Berhasil Sempurna (Quality 5/5)

| # | Query | Category | Results | Relevant | Notes |
|---|-------|----------|---------|----------|-------|
| 1 | Carikan rumah dijual di daerah cemara | location_simple | 10 | 10 | Perfect |
| 2 | Carikan rumah dijual di daerah ringroad | location_simple | 10 | 10 | Perfect |
| 3 | Carikan rumah sewa di medan | location_simple | 10 | 10 | Perfect |
| 11 | Tanah dijual di marelan | property_type | 10 | 10 | Perfect |
| 28 | Apartment di podomoro dibawah 1.5M | complex_query | 5 | 5 | Perfect |
| 30 | Rumah dijual di givency one | project_search | 5 | 5 | Perfect |

#### Queries yang Gagal Total (Quality 1/5 atau 0)

| # | Query | Category | Results | Relevant | Problem Analysis |
|---|-------|----------|---------|----------|------------------|
| 7 | Rumah dekat podomoro harga dibawah 1M | location_price | 10 | 1 | Radius terlalu jauh, "dekat" harus < 1km |
| 12 | Gudang dijual/disewa di KIM | property_type | 10 | 0 | Data gudang di KIM tidak ada di database |
| 16 | Yang 3 lantai (follow-up) | context_modify | 5 | 2 | Filter `floors` tidak ada di tool schema |
| 17 | Berikan lagi pilihan lain | context_followup | 7 | 0 | Filter 3 lantai dari #16 hilang |
| 18 | Lantai sama, harga dibawah 800jt | context_modify | 8 | 0 | Filter lantai tidak dipertahankan |
| 19 | Rumah dengan fasilitas CCTV | feature_search | 5 | 0 | Tool tidak support filter fasilitas |
| 20 | Rumah dengan fasilitas WiFi | feature_search | 5 | 0 | Tool tidak support filter fasilitas |
| 21 | Rumah komplek dengan lapangan basket | feature_search | 0 | 0 | Tidak ada hasil sama sekali |
| 22 | Rumah parkir beberapa mobil | feature_search | 5 | 0 | Tidak bisa filter by parking |
| 23 | Rumah ada AC, lemari, dapur, tangki air | feature_search | 5 | 0 | Tidak bisa filter by amenities |
| 24 | Rumah dekat mall | nearby_search | 5 | 0 | Geocoding "mall" tidak spesifik |
| 25 | Rumah dekat sekolah di medan | nearby_search | 5 | 0 | Geocoding "sekolah" tidak spesifik |
| 26 | Rumah dekat mall dibawah 800jt | nearby_price | 5 | 0 | Kombinasi nearby + price gagal |
| 27 | Full furnished, dibawah 1M, lapangan basket | complex_query | 5 | 0 | Terlalu banyak filter sekaligus |

---

## 2. Root Cause Analysis

### 2.1 Missing Tool Parameters

**Problem:** Tool `search_properties` tidak memiliki parameter untuk:
- `min_floors` / `max_floors` - Filter jumlah lantai
- `amenities` - Filter fasilitas (CCTV, WiFi, AC, dll)

**Evidence:**
```python
# Current SearchPropertiesInput (tools.py line 54-87)
class SearchPropertiesInput(BaseModel):
    query: str
    property_type: Optional[str]
    listing_type: Optional[str]
    source: Optional[str]
    min_price: Optional[int]
    max_price: Optional[int]
    min_bedrooms: Optional[int]  # Ada tapi tidak dikirim ke API!
    city: Optional[str]
    # MISSING: min_floors, max_floors, amenities
```

**Impact:** Queries #16-18 (floor filter) dan #19-23 (amenity filter) gagal.

### 2.2 Bedroom Filter Bug

**Problem:** Parameter `min_bedrooms` diterima oleh tool tapi TIDAK dikirim ke API.

**Evidence:** Di `metaproperty.py`, tidak ada kode yang menambahkan `min_bedrooms` ke params API.

**Impact:** Query dengan filter kamar tidur tidak akurat.

### 2.3 Context Memory Loss

**Problem:** Ketika user mengatakan "pilihan lain yang 3 lantai", kriteria pencarian sebelumnya hilang.

**Evidence:**
- Session state (`active_search_criteria`) sudah didefinisikan di `session.py` tapi TIDAK DIGUNAKAN
- Agent hanya mengandalkan implicit context dari chat history
- Tidak ada explicit storage untuk search criteria

**Impact:** Queries #14-18 (context follow-up dan modify) gagal mempertahankan filter.

### 2.4 Generic Geocoding Issues

**Problem:** Pencarian "dekat mall" atau "dekat sekolah" menggunakan Nominatim geocoding yang mengembalikan lokasi arbitrer.

**Evidence:**
```
Query: "cari rumah dekat mall"
Nominatim: mall, Medan, Indonesia → returns random mall location
Result: Properties tidak benar-benar "dekat mall" yang user maksud
```

**Impact:** Queries #24-26 (nearby search) mengembalikan hasil yang tidak relevan.

### 2.5 No Amenity Metadata

**Problem:** Fasilitas properti (CCTV, WiFi, dll) hanya disimpan sebagai text di ChromaDB document, bukan sebagai structured metadata.

**Evidence:**
```python
# property_store.py - amenities hanya di-embed sebagai text
amenity_map = {
    "electricity": "listrik",
    "water": "air PDAM",
    "security_24": "security 24 jam",  # Bukan metadata!
    ...
}
```

**Impact:** Tidak bisa filter by amenities secara akurat.

---

## 3. Improvement Plan

### Stage 1: Fix Bugs (Quick Wins)

| # | Task | File | Effort | Impact |
|---|------|------|--------|--------|
| 1.1 | Add `min_floors`/`max_floors` to tool schema | `tools.py` | Low | High |
| 1.2 | Fix bedroom filter bug | `metaproperty.py` | Low | Medium |
| 1.3 | Pass floor params to API | `metaproperty.py` | Low | High |

**Expected Fix:** Queries #16-18 should work after this.

### Stage 2: Improve Context Memory

| # | Task | File | Effort | Impact |
|---|------|------|--------|--------|
| 2.1 | Add search criteria storage per user | `tools.py` | Medium | High |
| 2.2 | Update system prompt for "pilihan lain" | `react_agent.py` | Low | Medium |
| 2.3 | Implement criteria modification pattern | `tools.py` | Medium | High |

**Expected Fix:** Queries #14-18 (context follow-up) should improve.

### Stage 3: Add Amenity Search

| # | Task | File | Effort | Impact |
|---|------|------|--------|--------|
| 3.1 | Add `amenities` parameter to tool | `tools.py` | Medium | High |
| 3.2 | Store amenities as ChromaDB metadata | `property_store.py` | High | High |
| 3.3 | Add amenity filtering in hybrid search | `hybrid_search.py` | Medium | High |

**Expected Fix:** Queries #19-23 (feature search) should work.

### Stage 4: Improve Proximity Search

| # | Task | File | Effort | Impact |
|---|------|------|--------|--------|
| 4.1 | Add POI landmark mapping | `tools.py` | Low | Medium |
| 4.2 | Pre-define coordinates for malls, schools | `tools.py` | Low | Medium |

**Expected Fix:** Queries #24-26 (nearby search) should improve.

---

## 4. Expected Metrics After Improvement

| Metric | Before | Target | Improvement |
|--------|--------|--------|-------------|
| Precision@5 | 44.14% | >60% | +16% |
| Success Rate | 60% | >80% | +20% |
| MRR | 0.476 | >0.6 | +0.124 |
| Response Quality | 2.92/5 | >3.5/5 | +0.58 |

### By Category Improvement

| Category | Before | Target | Notes |
|----------|--------|--------|-------|
| feature_search | 0% | >50% | Needs amenity filtering |
| nearby_search | 0% | >60% | Needs POI mapping |
| context_modify | 33% | >80% | Needs floor filter + context storage |
| context_followup | 66% | >90% | Needs criteria persistence |

---

## 5. Test Data Reference

### 5.1 File Locations

```
data/evaluation/
├── hybrid/
│   ├── test_results_20260124_140507.json      # Raw test results
│   ├── test_results_latest.json               # Symlink to latest
│   ├── evaluation_template_20260124_140507.csv # Rated CSV
│   ├── evaluation_20260124_140507.html        # HTML rating interface
│   ├── full_responses_20260124_140507.txt     # Full response text
│   ├── evaluation_report_20260124_150634.json # Metrics report (JSON)
│   └── evaluation_report_20260124_150634.md   # Metrics report (Markdown)
```

### 5.2 Test Questions (30 Queries)

| # | Question | Category |
|---|----------|----------|
| 1 | Carikan rumah dijual di daerah cemara | location_simple |
| 2 | Carikan rumah dijual di daerah ringroad | location_simple |
| 3 | Carikan rumah sewa di medan | location_simple |
| 4 | Carikan rumah dijual di daerah cemara harga 1M an | location_price |
| 5 | Carikan rumah dijual daerah ringroad harga dibawah 800juta 3 kamar | location_price_spec |
| 6 | Apakah ada rumah sewa di medan yang dibawah 50juta 3 kamar? | location_price_spec |
| 7 | Saya ingin beli rumah di dekat podomoro medan harga dibawah 1M ada? | location_price |
| 8 | Client saya lagi cari sewa dekat usu, anaknya mau kuliah disana | location_intent |
| 9 | Carikan rumah di inti kota medan yang harganya dibawah 1M | location_price |
| 10 | Apakah ada ruko yang disewakan di daerah krakatau? | property_type |
| 11 | Saya lagi cari tanah yang dijual di marelan | property_type |
| 12 | Apakah ada gudang yang dijual atau disewa di KIM? | property_type |
| 13 | Carikan rumah dijual daerah ringroad harga 1M an 3 kamar | location_price_spec |
| 14 | Apakah masih ada pilihan lain? | context_followup |
| 15 | Berikan lagi pilihan lain | context_followup |
| 16 | Kasih pilihan lain, lokasi dan harga masih sama, tapi yang 3 lantai? | context_modify |
| 17 | Berikan lagi pilihan lain | context_followup |
| 18 | Kalau pilihan lain, lokasi dan jumlah lantai masih sama, tapi yang dibawah 800 juta ada? | context_modify |
| 19 | Carikan rumah dengan fasilitas cctv di medan | feature_search |
| 20 | Carikan rumah dengan fasilitas wifi di medan | feature_search |
| 21 | Cari rumah dalam komplek dengan fasilitas lapangan basket | feature_search |
| 22 | Cari rumah yang bisa parkir beberapa mobil | feature_search |
| 23 | Cari rumah yang sudah ada ac, lemari, dapur dan tangki air | feature_search |
| 24 | Cari rumah dekat mall | nearby_search |
| 25 | Cari rumah dekat sekolah di medan | nearby_search |
| 26 | Cari rumah dekat mall yang harganya dibawah 800 juta | nearby_price |
| 27 | Cari rumah full furnished yang harganya dibawah 1 M dalam komplek dengan fasilitas lapangan basket | complex_query |
| 28 | Cari apartment di podomoro yang bisa harganya dibawah 1.5 M | complex_query |
| 29 | Cari rumah di citraland bagya city medan | project_search |
| 30 | Cari rumah dijual di komplek givency one | project_search |

---

## 6. Implementation Checklist

### Stage 1: Fix Bugs ✅ COMPLETED
- [x] 1.1 Add `min_floors`/`max_floors` to `SearchPropertiesInput` in `tools.py`
- [x] 1.2 Fix `min_bedrooms` not passed to API in `metaproperty.py`
- [x] 1.3 Add floor params to API call in `metaproperty.py`
- [ ] Verify: Test query #16 "yang 3 lantai" works

### Stage 2: Improve Context Memory ✅ COMPLETED
- [x] 2.1 Add `_user_search_criteria` storage in `tools.py`
- [x] 2.2 Update system prompt in `react_agent.py` for context handling
- [x] 2.3 Implement criteria modification pattern (via system prompt)
- [ ] Verify: Test queries #14-18 maintain context

### Stage 3: Add Amenity Search ✅ COMPLETED (Partial)
- [x] 3.1 Add `amenities` parameter to tool schema
- [ ] 3.2 Store amenities as ChromaDB metadata during sync (Future: needs re-sync)
- [x] 3.3 Add amenity filtering in `hybrid_search.py`
- [ ] Verify: Test queries #19-23 return relevant results

### Stage 4: Improve Proximity Search ✅ COMPLETED
- [x] 4.1 Expand `LANDMARK_AREA_MAP` dict with mall coordinates
- [x] 4.2 Add school, hospital POI mappings
- [x] 4.3 Expand `landmarks_to_expand` for query expansion
- [ ] Verify: Test queries #24-26 use correct coordinates

### Stage 5: Re-run Evaluation
- [ ] Run test: `python scripts/test_sequential_chat.py --method hybrid`
- [ ] Generate HTML: `python scripts/generate_evaluation_html.py --method hybrid`
- [ ] Manual rating
- [ ] Calculate metrics: `python scripts/calculate_evaluation_metrics.py --method hybrid`
- [ ] Compare with baseline metrics

---

## 6.1 Implementation Details (Completed 24 Jan 2026)

### Files Modified

| File | Changes |
|------|---------|
| `src/agents/tools.py` | Added `min_floors`, `max_floors`, `amenities` params; Added criteria storage (`_user_search_criteria`, getter/setter); Expanded POI mappings |
| `src/adapters/metaproperty.py` | Fixed bedroom bug; Added floor params to API |
| `src/adapters/base.py` | Added `min_floors`, `max_floors`, `amenities` to `SearchCriteria` |
| `src/knowledge/hybrid_search.py` | Updated search method signature with new params |
| `src/agents/react_agent.py` | Added CONTEXT HANDLING section to system prompt |

### New POI Mappings Added

**Universities:** UNIMED, UINSU, UMSU, UNIKA, UNPRI, Mikro Skill

**Malls:** Manhattan, Plaza Medan Fair, Grand Palladium, Mall Medina, Carrefour, Lippo Plaza, Hermes Palace, Plaza Millenium + generic "mall" mapping

**Hospitals:** RS Columbia Asia, RS Elisabeth, RS Murni Teguh, RS Royal Prima, RS Pirngadi, RS Hermina, RS Siloam + generic "rumah sakit" mapping

**Schools:** Sutomo, Methodist, Al Azhar, Binus School + generic "sekolah" mapping

**Industrial:** KIM, Kawasan Industri Medan

### Context Handling System Prompt Addition

```
CONTEXT HANDLING FOR FOLLOW-UP QUERIES:
1. "Pilihan lain" / "Ada yang lain?" → SAME criteria, more results
2. Filter modifications ("yang 3 lantai") → Apply NEW filter on previous criteria
3. Always state active filters explicitly
4. Context keywords: "lainnya", "yang", "dengan", "tapi"
```

### New Tool: search_pois (Multi-Step POI Search)

**Added:** `search_pois` tool for discovering POIs (schools, malls, hospitals) in a city.

#### Tool Schema

```python
class SearchPOIsInput(BaseModel):
    poi_type: str       # "school", "mall", "hospital", "university"
    city: str = "Medan" # Default: Medan
    limit: int = 5      # Max POIs to return
```

#### Problem Solved

Query "rumah dekat sekolah" sebelumnya gagal karena geocoding "sekolah, Medan" memberikan hasil acak. Sekarang agent menggunakan **multi-step autonomous workflow**:

```
User: "cari rumah dekat mall di medan"

┌─────────────────────────────────────────────────────────────┐
│ Iteration 1: Discover POIs                                  │
├─────────────────────────────────────────────────────────────┤
│ Tool: search_pois(poi_type="mall", city="Medan")           │
│ Result: Sun Plaza, Centre Point, Plaza Medan Fair, ...      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Iteration 2: Search near EACH POI (parallel)               │
├─────────────────────────────────────────────────────────────┤
│ Tool: search_nearby(location_name="Sun Plaza", radius=2)    │
│ Tool: search_nearby(location_name="Centre Point", radius=2) │
│ Tool: search_nearby(location_name="Plaza Medan Fair", ...)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Iteration 3: Generate Response                              │
├─────────────────────────────────────────────────────────────┤
│ "Berikut rumah dekat mall di Medan:                        │
│                                                             │
│ **Dekat Sun Plaza:**                                        │
│ 1. Rumah A - 260m dari Sun Plaza                           │
│ 2. Rumah B - 450m dari Sun Plaza                           │
│                                                             │
│ **Dekat Centre Point:**                                     │
│ 1. Rumah C - 300m dari Centre Point"                       │
└─────────────────────────────────────────────────────────────┘
```

#### Test Results (24 Jan 2026)

```
Query: "cari rumah dekat mall di medan"

Tool calls: 6 total
  - search_pois: 1
  - search_nearby: 5 (parallel)

Successful results: 6/6 (no errors)
Final response: 2506 chars

Malls mentioned in response:
  ✓ Sun Plaza
  ✓ Centre Point
  ✓ Plaza Medan Fair
  ✓ Manhattan Times Square
```

#### Keywords yang Trigger Multi-Step POI Search

| User Query | Detected As | Action |
|------------|-------------|--------|
| "dekat sekolah" | Generic school | search_pois → search_nearby |
| "dekat mall" | Generic mall | search_pois → search_nearby |
| "dekat rumah sakit" | Generic hospital | search_pois → search_nearby |
| "dekat universitas" | Generic university | search_pois → search_nearby |
| "dekat Sun Plaza" | Specific POI | search_nearby directly |
| "dekat USU" | Specific POI | search_nearby directly |

#### Pre-defined POIs Database

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

#### Bugs Fixed (24 Jan 2026)

1. **System Prompt Issue**: LLM was outputting "Action: search_pois(...)" as text instead of actually calling the tool. Fixed by updating TOOL CALLING section in system prompt.

2. **Event Loop Closed Error**: When running multiple search_nearby in parallel, httpx.AsyncClient was shared across event loops causing errors. Fixed by using context manager `async with self._create_client() as client:` for each API call.

#### UX Improvement

Jika tidak ada hasil untuk beberapa POI, agent akan menyarankan:
> "Jika Anda memiliki nama sekolah/mall/rumah sakit tertentu yang ingin dicari, silakan beritahu saya agar saya bisa membantu mencari properti terdekat dengan lebih akurat."

---

## 7. References

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.
- Voorhees, E. M. (1999). The TREC-8 Question Answering Track Report. NIST.
- Voorhees, E. M. (2002). The philosophy of information retrieval evaluation. CLEF Workshop.

---

*Document created: 24 Januari 2026*
*Updated: 25 Januari 2026 - Marked as V1 results*
*Status: Superseded by V2 evaluation (constraint-based)*
*For: Thesis RAG Property Chatbot Evaluation*
