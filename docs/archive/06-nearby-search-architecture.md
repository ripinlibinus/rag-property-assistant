# Nearby/Area-Based Search Architecture

> ⚠️ **DEPRECATED / HISTORICAL REFERENCE ONLY**
> 
> Dokumen ini sudah **tidak digunakan lagi**. Pendekatan static `LANDMARK_AREAS` mapping sudah diganti dengan:
> - **Geocoding API** (OpenStreetMap Nominatim) - dynamic untuk semua lokasi
> - **Radius-based search** dengan koordinat lat/lng
> 
> Lihat implementasi terbaru di:
> - [src/agents/tools.py](../src/agents/tools.py) - `geocode_location()`, `search_nearby()`
> - [docs/07-progress-report-day4-continued.md](./07-progress-report-day4-continued.md)
>
> *Deprecated: 2026-01-23*

---

This document explains how the system handles location-based property searches, especially when users search using landmarks or relative locations.

## Overview

When a user asks: **"Carikan rumah di daerah USU"** or **"Find house near Kualanamu airport"**, the system:

1. **Detects** that this is a nearby/area-based search (not a direct location)
2. **Maps** the landmark to known nearby districts/areas
3. **Expands** the search criteria to include multiple relevant areas
4. **Responds** with context about the landmark

## Flow Diagram

```
User Input: "cari rumah dekat USU"
         │
         ▼
┌─────────────────────────────────────┐
│  1. ORCHESTRATOR - Intent Classify  │
│  - Detects: property_search         │
│  - Extracts: nearby=true            │
│  - Extracts: landmark="USU"         │
│  - Detects: language="id"           │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  2. PROPERTY AGENT - Parse Query    │
│  - SEARCH_PARSER_PROMPT extracts:   │
│    * nearby_search: true            │
│    * landmark: "USU"                │
│    * property_type: "house"         │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. _expand_nearby_search()         │
│  - Lookup LANDMARK_AREAS mapping    │
│  - USU → ["Padang Bulan",           │
│           "Dr. Mansyur",            │
│           "Medan Baru",             │
│           "Simpang Limun"]          │
│  - Add areas to search query        │
│  - Set default location             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  4. API + Vector Search             │
│  - Query API with expanded criteria │
│  - Semantic ranking via ChromaDB    │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  5. Format Response with Context    │
│  - "Ditemukan 5 properti di         │
│     sekitar **USU**:"               │
└─────────────────────────────────────┘
```

## Trigger Keywords

The system recognizes these patterns as nearby/area-based searches:

| Indonesian | English | Pattern |
|------------|---------|---------|
| dekat | near | "dekat USU" |
| sekitar | around | "sekitar kampus" |
| sekitaran | area of | "sekitaran Sun Plaza" |
| daerah | district/area | "daerah Kualanamu" |
| area | area | "area Centre Point" |

## Landmark Mapping

The system maintains a mapping of known landmarks to their nearby districts:

```python
LANDMARK_AREAS = {
    # Universities
    "usu": ["Padang Bulan", "Dr. Mansyur", "Medan Baru", "Simpang Limun"],
    "universitas sumatera utara": ["Padang Bulan", "Dr. Mansyur", "Medan Baru"],
    "uisu": ["Teladan", "Medan Kota", "Sukaramai"],
    
    # Transportation
    "kualanamu": ["Beringin", "Tanjung Morawa", "Batang Kuis"],
    "bandara kualanamu": ["Beringin", "Tanjung Morawa", "Batang Kuis"],
    
    # Shopping Centers
    "sun plaza": ["Medan Kota", "Simpang Limun", "Thamrin"],
    "centre point": ["Medan Maimun", "Kesawan", "Medan Kota"],
    "plaza medan fair": ["Petisah", "Sei Sikambing", "Medan Petisah"],
    
    # Areas
    "setia budi": ["Tanjung Sari", "Simpang Selayang", "Medan Selayang"],
    "ringroad": ["Medan Johor", "Medan Tuntungan", "Setia Budi"],
    "krakatau": ["Medan Timur", "Glugur Darat", "Pulo Brayan"],
    
    # Religious/Cultural
    "masjid raya": ["Medan Area", "Kesawan", "Petisah"],
}
```

## Search Expansion Logic

```python
def _expand_nearby_search(self, criteria: SearchCriteria, landmark: str) -> SearchCriteria:
    """
    Expand search criteria for nearby/area-based searches.
    
    Strategy:
    1. Lookup landmark in LANDMARK_AREAS mapping
    2. If found: add all nearby areas to semantic query
    3. If not found: use landmark as direct location
    """
    
    # Normalize landmark for lookup
    landmark_lower = landmark.lower().strip()
    
    # Find matching areas
    nearby_areas = []
    for key, areas in LANDMARK_AREAS.items():
        if key in landmark_lower or landmark_lower in key:
            nearby_areas = areas
            break
    
    if nearby_areas:
        # Add all areas to query for semantic matching
        areas_text = ", ".join(nearby_areas)
        if criteria.query:
            criteria.query = f"{criteria.query} {areas_text}"
        else:
            criteria.query = areas_text
        
        # Set first area as primary location for API filter
        if not criteria.location:
            criteria.location = nearby_areas[0]
    else:
        # Unknown landmark - use directly
        if not criteria.location:
            criteria.location = landmark
        criteria.query = f"{criteria.query or ''} {landmark}".strip()
    
    return criteria
```

## Response Formatting

When `landmark_context` is provided, responses include the landmark:

**Indonesian:**
```
🏠 Ditemukan 5 properti di sekitar **USU**:

**1. Rumah Minimalis Modern**
   📍 Padang Bulan, Medan
   💰 Rp 1,500,000,000
   ...
```

**English:**
```
🏠 Found 5 properties near **USU**:

**1. Modern Minimalist House**
   📍 Padang Bulan, Medan
   💰 Rp 1,500,000,000
   ...
```

## Adding New Landmarks

To add new landmark mappings:

1. Edit `src/agents/property_agent.py`
2. Add entry to `LANDMARK_AREAS` dictionary in `_expand_nearby_search()` method
3. Use lowercase keys for case-insensitive matching

```python
LANDMARK_AREAS = {
    # ... existing mappings ...
    
    # New landmark
    "rumah sakit adam malik": ["Medan Tuntungan", "Padang Bulan Selayang"],
}
```

## Multi-Language Support

The system uses a "universal code, adaptive response" approach:

| Aspect | Approach |
|--------|----------|
| Code | English variable names, comments |
| Prompts | Language-neutral instructions |
| Responses | Match user's language & style |

### Language Detection Flow

```
User: "cari rumah dekat USU dong bro"
         │
         ▼
Orchestrator detects:
- language: "id"
- style: casual (uses "dong", "bro")
         │
         ▼
Response adapts:
- Language: Indonesian
- Tone: Casual, friendly
- "Oke bro! Ini properti di sekitar USU... 🏠"
```

## Future Improvements

1. **Geocoding Integration**: Use Google Maps/OpenStreetMap API for unknown landmarks
2. **Distance-Based Search**: Calculate actual distances from landmark coordinates
3. **Dynamic Mapping**: Learn new landmarks from user queries
4. **Fuzzy Matching**: Handle typos in landmark names
