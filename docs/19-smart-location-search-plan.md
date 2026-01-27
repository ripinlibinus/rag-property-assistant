# Smart Location Search Implementation Plan

**Last Updated:** 2026-01-25 (v2.0 - Revised Architecture)

## Overview

Implementasi pendekatan **separation of concerns** untuk location search:
- `search_properties` → Filter + text search (NO location)
- `search_properties_by_location` → Location-based search dengan auto-geocoding
- `search_nearby` → Proximity search near landmarks

API Laravel menggunakan **smart location logic**: cek keyword di database dulu, jika tidak ada fallback ke geo search.

---

## Problem Statement (Original)

Agent salah memilih tool untuk lokasi seperti "KIM" (Kawasan Industri Medan):
- Agent menggunakan `search_properties` dengan text search
- Keyword "KIM" tidak ada di field address/district/city
- API mengembalikan hasil yang salah lokasi (gudang di Medan Binjai, bukan KIM)

---

## Solution Architecture (v2.0)

### Tool Separation

```
User Query
    │
    ├─ "rumah murah 3 kamar" (features only)
    │   └─ search_properties(property_type="house", min_bedrooms=3)
    │       → API: filter only, no geo
    │
    ├─ "rumah di ringroad" (location-based)
    │   └─ search_properties_by_location(location_keyword="ringroad", city="Medan")
    │       → Tool: geocode("ringroad, Medan") → lat=3.58, lng=98.65
    │       → API: lat=3.58, lng=98.65, radius=3
    │       → API Logic: cek "ringroad" di DB? → fallback geo
    │
    └─ "rumah dekat USU" (proximity)
        └─ search_nearby(location_name="USU", city="Medan", radius_km=1)
            → Tool: geocode("USU, Medan") → lat=3.57, lng=98.66
            → API: lat=3.57, lng=98.66, radius=1
```

### API Smart Location Logic

```
RAG-Tesis (Python)                    Laravel API
        │                                   │
        │  {                                │
        │    location_keyword: "ringroad",  │
        │    latitude: 3.58,                │
        │    longitude: 98.65,              │
        │    radius_km: 3,                  │
        │    property_type: "house"         │
        │  }                                │
        │──────────────────────────────────>│
        │                                   │
        │                     ┌─────────────┴─────────────┐
        │                     │ Check: "ringroad" exists  │
        │                     │ in address/district/city? │
        │                     └─────────────┬─────────────┘
        │                                   │
        │                        ┌──────────┴──────────┐
        │                        │                     │
        │                       YES                   NO
        │                        │                     │
        │               Use keyword search    Use geo search
        │               WHERE address LIKE    Haversine formula
        │               '%ringroad%'          lat/lng + radius
        │                        │                     │
        │                        └──────────┬──────────┘
        │                                   │
        │<──────────────────────────────────│
        │         Return results            │
```

---

## Implementation Status

### RAG-Tesis Side (Python) - ✅ COMPLETED

| Task | Status | Description |
|------|--------|-------------|
| New tool: `search_properties_by_location` | ✅ Done | Location search dengan auto-geocode |
| Update `search_properties` | ✅ Done | Remove location params, features only |
| Update `search_nearby` | ✅ Done | Add all filters (bedrooms, floors, etc.) |
| Update `SearchCriteria` | ✅ Done | Has lat/lng/radius fields |
| Update `HybridSearchService` | ✅ Done | Supports geo params |
| Update `metaproperty.py` adapter | ✅ Done | Sends lat/lng to API |
| Update `REACT_SYSTEM_PROMPT` | ✅ Done | New tool selection logic |
| Remove Medan-specific code | ✅ Done | Global support |

### Laravel API Side - ✅ COMPLETED

| Task | Status | Description |
|------|--------|-------------|
| Smart location logic | ✅ Done | Check keyword first in district/city, fallback to geo |
| Haversine formula | ✅ Done | Distance calculation with 6371km Earth radius |
| `location_keyword` param | ✅ Done | Alias for `search`, receives from RAG-Tesis |
| `query` param | ✅ Done | Feature/amenity search (separate from location) |
| `in_complex` filter | ✅ Done | Filter by complex/standalone (Listing only) |
| `facing` filter | ✅ Done | Filter by direction (both Listing and Project) |

---

## Laravel API Implementation

### Required Changes

**File:** Controller yang handle property search

```php
public function search(Request $request)
{
    $query = Property::query();

    // Get params from RAG-Tesis
    $locationKeyword = $request->input('location_keyword');  // NEW
    $searchQuery = $request->input('query');  // For features (furnished, pool, etc.)
    $latitude = $request->input('lat');
    $longitude = $request->input('lng');
    $radiusKm = $request->input('radius_km', 3);

    // Smart Location Logic
    if ($locationKeyword) {
        // Check if keyword exists in location fields
        $keywordExists = Property::where(function($q) use ($locationKeyword) {
            $q->where('address', 'LIKE', "%{$locationKeyword}%")
              ->orWhere('district', 'LIKE', "%{$locationKeyword}%")
              ->orWhere('city', 'LIKE', "%{$locationKeyword}%")
              ->orWhere('title', 'LIKE', "%{$locationKeyword}%");
        })->exists();

        if ($keywordExists) {
            // PRIORITY 1: Use keyword search (more accurate)
            $query->where(function($q) use ($locationKeyword) {
                $q->where('address', 'LIKE', "%{$locationKeyword}%")
                  ->orWhere('district', 'LIKE', "%{$locationKeyword}%")
                  ->orWhere('city', 'LIKE', "%{$locationKeyword}%")
                  ->orWhere('title', 'LIKE', "%{$locationKeyword}%");
            });
        } elseif ($latitude && $longitude) {
            // PRIORITY 2: Fallback to geo search
            $query->selectRaw("
                *,
                (6371 * acos(
                    cos(radians(?)) * cos(radians(latitude)) *
                    cos(radians(longitude) - radians(?)) +
                    sin(radians(?)) * sin(radians(latitude))
                )) AS distance_km
            ", [$latitude, $longitude, $latitude])
            ->having('distance_km', '<=', $radiusKm)
            ->orderBy('distance_km');
        }
    } elseif ($latitude && $longitude) {
        // Direct geo search (no keyword)
        $query->selectRaw("
            *,
            (6371 * acos(
                cos(radians(?)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(?)) +
                sin(radians(?)) * sin(radians(latitude))
            )) AS distance_km
        ", [$latitude, $longitude, $latitude])
        ->having('distance_km', '<=', $radiusKm)
        ->orderBy('distance_km');
    }

    // Feature text search (separate from location)
    if ($searchQuery) {
        $query->where(function($q) use ($searchQuery) {
            $q->where('title', 'LIKE', "%{$searchQuery}%")
              ->orWhere('description', 'LIKE', "%{$searchQuery}%");
        });
    }

    // Apply other filters...
    if ($request->has('property_type')) {
        $query->where('property_type', $request->input('property_type'));
    }
    if ($request->has('listing_type')) {
        $query->where('listing_type', $request->input('listing_type'));
    }
    if ($request->has('min_price')) {
        $query->where('price', '>=', $request->input('min_price'));
    }
    if ($request->has('max_price')) {
        $query->where('price', '<=', $request->input('max_price'));
    }
    if ($request->has('min_bedrooms')) {
        $query->where('bedrooms', '>=', $request->input('min_bedrooms'));
    }
    if ($request->has('max_bedrooms')) {
        $query->where('bedrooms', '<=', $request->input('max_bedrooms'));
    }
    // ... other filters

    return $query->paginate($request->input('limit', 10));
}
```

### API Parameters (Laravel)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `location_keyword` | string | Location to check in DB (alias: `search`) | "ringroad", "cemara asri" |
| `search` | string | Alias for location_keyword | "ringroad" |
| `query` | string | Feature/amenity search (separate from location) | "furnished", "pool" |
| `lat` | float | Latitude from geocoding | 3.5800 |
| `lng` | float | Longitude from geocoding | 98.6500 |
| `radius` | float | Search radius (km) | 3.0 |
| `property_type` | string | house, apartment, etc. | "house" |
| `listing_type` | string | sale or rent | "sale" |
| `price_min` | int | Minimum price | 500000000 |
| `price_max` | int | Maximum price | 2000000000 |
| `bedrooms_min` | int | Minimum bedrooms | 3 |
| `bedrooms_max` | int | Maximum bedrooms | 3 |
| `floors_min` | int | Minimum floors | 2 |
| `floors_max` | int | Maximum floors | 2 |
| `in_complex` | string | "1" or "0" (Listing only) | "1" |
| `facing` | string | Facing direction | "utara" |
| `source` | string | project or listing | "project" |
| `page` | int | Page number | 1 |
| `per_page` | int | Results per page | 10 |

---

## Testing Plan

### Test Case 1: Ringroad (Keyword TIDAK ada di DB)

```
Input: "rumah dijual di ringroad"
Tool: search_properties_by_location(
    location_keyword="ringroad",
    city="Medan",
    property_type="house",
    listing_type="sale"
)

RAG-Tesis sends to API:
{
    "location_keyword": "ringroad",
    "lat": 3.5800,
    "lng": 98.6500,
    "radius_km": 3,
    "property_type": "house",
    "listing_type": "sale"
}

API Logic:
1. Check: "ringroad" in address/district/city? → NO (not in DB)
2. Fallback: Use geo search (lat/lng + radius)
3. Return: Properties within 3km of ringroad coordinates
```

### Test Case 2: Cemara Asri (Keyword ADA di DB)

```
Input: "rumah di cemara asri"
Tool: search_properties_by_location(
    location_keyword="cemara asri",
    city="Medan",
    property_type="house"
)

RAG-Tesis sends to API:
{
    "location_keyword": "cemara asri",
    "lat": 3.6289,
    "lng": 98.6960,
    "radius_km": 3,
    "property_type": "house"
}

API Logic:
1. Check: "cemara asri" in address/district/city? → YES (in DB)
2. Use keyword search (more accurate)
3. Return: Properties with "cemara asri" in location fields
```

### Test Case 3: Feature-only Search

```
Input: "apartemen furnished 2 kamar"
Tool: search_properties(
    query="furnished",
    property_type="apartment",
    min_bedrooms=2,
    max_bedrooms=2
)

RAG-Tesis sends to API:
{
    "query": "furnished",
    "property_type": "apartment",
    "min_bedrooms": 2,
    "max_bedrooms": 2
}

API Logic:
1. No location_keyword, no lat/lng
2. Filter by property_type, bedrooms
3. Text search "furnished" in title/description
4. Return: Furnished apartments with 2 bedrooms (any location)
```

### Test Case 4: Proximity Search (USU)

```
Input: "rumah 3 kamar dekat USU"
Tool: search_nearby(
    location_name="USU",
    city="Medan",
    property_type="house",
    min_bedrooms=3,
    max_bedrooms=3,
    radius_km=1
)

RAG-Tesis sends to API:
{
    "location_keyword": "USU",
    "lat": 3.5656,
    "lng": 98.6565,
    "radius_km": 1,
    "property_type": "house",
    "min_bedrooms": 3,
    "max_bedrooms": 3
}

API Logic:
1. Check: "USU" in address/district? → NO (landmark, not area name)
2. Fallback: Use geo search
3. Return: Houses within 1km of USU with 3 bedrooms
```

---

## Decision Matrix: Keyword vs Geo Search

| Scenario | Keyword in DB? | Has Lat/Lng? | Search Method |
|----------|---------------|--------------|---------------|
| "rumah di cemara asri" | YES | YES | Keyword search |
| "rumah di ringroad" | NO | YES | Geo search |
| "rumah dekat USU" | NO | YES | Geo search |
| "rumah di marelan" | YES | YES | Keyword search |
| "rumah di KIM" | NO | YES | Geo search |
| "apartemen furnished" | N/A | NO | Text search only |

**Why keyword search is prioritized:**
- More accurate for known areas (exact match in database)
- Geo search may include properties from adjacent areas
- Keyword search respects database boundaries

**Why geo search as fallback:**
- Handles landmarks not in database (USU, Sun Plaza, KIM)
- Handles typos or variations (ringroad vs ring road)
- Provides results when keyword not found

---

## Backward Compatibility

1. `location_keyword` is optional - API works without it
2. `lat`/`lng` are optional - API falls back to text search
3. Existing clients continue working (no breaking changes)

---

## Notes

- Geocoding dilakukan di RAG-Tesis (Python) menggunakan Google Maps API / Nominatim
- Laravel API tidak perlu geocoding, hanya terima lat/lng
- Smart logic ada di Laravel API untuk memutuskan keyword vs geo search
- Semua filter tetap bisa dikombinasikan dengan location search

---

---

## Implementation Notes

### Laravel API (`PropertyController.php`)

**File:** `app/Http/Controllers/Api/Website/PropertyController.php`

**Key Implementation Details:**
1. **`location_keyword` / `search`** - Both accepted, `location_keyword` takes priority
2. **`query`** - Separate feature search (searches title/description)
3. **Smart Logic in `checkKeywordExistsInLocationFields()`**:
   - Only checks `district` and `city` fields (not title/address)
   - Avoids false positives from substring matching
   - Returns `true` if keyword ≥ 3 chars found in location fields
4. **Geo Search** - Haversine formula with 6371km Earth radius
5. **`in_complex`** - Only for Listings (Projects are always in complex)
6. **`facing`** - String for Listings, JSON array for Projects (via complex.types)

---

*Document created: 2026-01-24*
*Last updated: 2026-01-25 (v2.1 - Laravel API implementation completed)*
