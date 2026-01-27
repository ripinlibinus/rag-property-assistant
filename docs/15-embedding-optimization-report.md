# Data Preparation & Embedding Optimization Report

## Research Context

**Tanggal:** 24 Januari 2026
**Chapter:** Data Preparation & Preprocessing
**Objective:** Optimasi domain-specific embedding untuk meningkatkan kualitas semantic search pada sistem RAG Property Chatbot

---

## Executive Summary

Dokumen ini merupakan laporan teknis tahap **Data Preparation** dalam penelitian RAG Property Chatbot. Proses ini mencakup:

1. **Audit Data Source** - Identifikasi inkonsistensi dan missing fields
2. **API Optimization** - Perbaikan endpoint untuk data extraction
3. **Embedding Strategy** - Domain-specific field selection dan text preprocessing
4. **Quality Assurance** - Validasi data sebelum dan sesudah preprocessing

---

## Data Preparation Methodology

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA PREPARATION PIPELINE                        │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  MetaProperty│    │   Data       │    │  Embedding   │    │   ChromaDB   │
│  MySQL DB    │───▶│   Extraction │───▶│  Processing  │───▶│   Vector     │
│              │    │   (API)      │    │              │    │   Store      │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
     7,531              2,913              Optimized           Ready for
   (all data)      (filtered active)      Text + Metadata      Search

                    ┌─────────────────────────────────────┐
                    │         FILTERING CRITERIA          │
                    ├─────────────────────────────────────┤
                    │ • status IN (active, sold, rented)  │
                    │ • user_id IS NOT NULL               │
                    │ • projects: active status only      │
                    └─────────────────────────────────────┘
```

### Data Sources

| Source | Type | Total Records | After Filter | Description |
|--------|------|---------------|--------------|-------------|
| `listings` | Secondary Market | 7,531 | 2,568 | Individual property listings |
| `projects` | Primary Market | 445 | 345 | Developer projects/perumahan |
| **Combined** | - | **7,976** | **2,913** | Total untuk embedding |

---

## 1. Permasalahan yang Ditemukan

### 1.1 Data Embedding Tidak Optimal

**Kondisi Sebelum:**

Analisis terhadap ChromaDB yang sudah di-embed menunjukkan:

```
PAGE_CONTENT (yang di-embed):
- Habitat
- Lokasi: Jl. Pasar III..., Medan Sunggal, Medan
- Tipe: perumahan

MASALAH:
- Description: TIDAK ADA
- Features/Amenities: TIDAK ADA
- Certificate type: TIDAK ADA
- Listing type (dijual/sewa): TIDAK ADA
```

**Impact:**
- Semantic search tidak bisa match query seperti "rumah dengan kolam renang"
- Query "properti dijual" tidak bisa dibedakan dengan "disewa"
- Informasi penting seperti SHM/SHGB tidak ter-index

### 1.2 Inkonsistensi Data Antara Endpoint

| Endpoint | Count | Masalah |
|----------|-------|---------|
| `/api/v1/listings` | 2,568 | Sudah filter active status |
| `/api/v1/properties` | 100 | Hardcoded limit! |
| `/api/v1/sync/stats` | 7,531 | Tidak filter status (semua termasuk inactive) |
| `/api/v1/sync/pending-ingest` | 3,585 | Filter berbeda |

**Impact:**
- Statistik sync tidak akurat
- Data inactive ikut di-embed (waste token)
- Pagination tidak berfungsi dengan benar

### 1.3 Field Penting Tidak Di-return oleh Sync API

Endpoint `pending-ingest` tidak return field yang penting untuk embedding:

| Field | Status di API | Penting untuk Embedding? |
|-------|---------------|--------------------------|
| `additional_info` | TIDAK ADA | Ya - sering berisi detail |
| `area_listing` | TIDAK ADA | Ya - area name |
| `certificate_type` | TIDAK ADA | Ya - SHM, SHGB |
| `amenities` | ADA | Ya |
| `complex_name` | TIDAK ADA | Ya - nama komplek |

---

## 2. Solusi yang Diimplementasikan

### 2.1 Optimasi Laravel API (Backend)

#### A. SyncController - `stats()` Method

**Perubahan:** Menambahkan filter status yang sama dengan `pending-ingest`

```php
// BEFORE
$totalListings = Listing::count();  // Semua status

// AFTER
$activeListingStatuses = ['active', 'sold', 'sold_by_owner', 'rented'];
$totalListings = Listing::whereIn('status', $activeListingStatuses)
    ->whereNotNull('user_id')
    ->count();
```

**Hasil:**
- Before: 7,531 listings
- After: 2,568 listings (sama dengan `/listings`)

#### B. SyncController - `fetchPendingListings()` Method

**Perubahan:** Menambahkan 8 field baru untuk embedding

```php
// Fields yang ditambahkan:
'additional_info',      // Detail tambahan
'area_listing',         // Area name (e.g., "padang bulan")
'floors',               // Jumlah lantai
'certificate_type',     // SHM, SHGB, etc.
'carport_capacity',     // Kapasitas carport
'electricity_wattage',  // Daya listrik
'is_in_complex',        // Dalam komplek atau tidak
'complex_name',         // Nama komplek
```

**Hasil:**
- Before: 22 fields
- After: 30 fields

#### C. PropertyController - Limit Fix

**Perubahan:** Menaikkan hardcoded limit

```php
// BEFORE
$listings = $query->limit(100)->get();

// AFTER
$listings = $query->limit(500)->get();
```

### 2.2 Optimasi PropertyStore (RAG System)

#### A. `_create_document_text()` - Semantic Content Optimization

**Strategi baru untuk page_content (yang di-embed):**

```python
def _create_document_text(self, listing: dict) -> str:
    parts = []

    # 1. Title
    parts.append(listing["title"])

    # 2. Listing type context
    if listing_type == "sale":
        parts.append("Properti dijual")
    elif listing_type == "rent":
        parts.append("Properti disewakan")

    # 3. Source type (project/listing)
    if source_type == "project":
        parts.append(f"Proyek baru dari developer {developer}")

    # 4. Description dengan HTML stripping
    clean_desc = re.sub(r'<[^>]+>', ' ', str(description))
    parts.append(clean_desc)

    # 5. Additional info
    parts.append(additional_info)

    # 6. Location dengan area_listing
    parts.append("Lokasi: " + ", ".join([area_listing, complex_name, district, city]))

    # 7. Property type dengan mapping Indonesia
    type_map = {"house": "Rumah", "shophouse": "Ruko", ...}
    parts.append(f"Tipe: {type_map.get(prop_type)}")

    # 8. Certificate type
    cert_map = {"shm": "SHM (Sertifikat Hak Milik)", ...}
    parts.append(f"Sertifikat: {cert_map.get(cert)}")

    # 9. Amenities dengan mapping
    amenity_map = {"electricity": "listrik", "swimming_pool": "kolam renang", ...}
    parts.append("Fasilitas: " + ", ".join(readable_amenities))

    return "\n\n".join(parts)
```

#### B. Metadata Enhancement

**Field metadata yang ditambahkan:**

```python
metadata = {
    # Existing
    "property_id", "title", "property_type", "city", "district",
    "price", "bedrooms", "bathrooms", "land_area", "building_area",

    # NEW
    "listing_type",      # sale/rent - untuk filtering
    "area_listing",      # area name
    "floors",            # jumlah lantai
    "certificate_type",  # SHM, SHGB, etc.
    "status",            # active, sold, rented
}
```

---

## 3. Perbandingan Hasil

### 3.1 Contoh PAGE_CONTENT

**SEBELUM:**
```
Habitat

Lokasi: Jl. Pasar III..., Medan Sunggal, Medan

Tipe: perumahan
```

**SESUDAH:**
```
Jual Rugi Ruko Ayahanda

Properti dijual

Siap cepat tang dapat. Bisa KPR!
Biaya masing masing Tanggungan Pembeli BPHtB, biaya notaris dan biaya KPR,

Lokasi: Sekip, ayahanda, petisah, jalan cangkir, dekat UNPRI,
        Komplek Centrium Ayahanda, Medan Petisah, Kota Medan,
        Jl. Cangkir, Komp. Centrium Ayahanda...

Tipe: Ruko

Sertifikat: SHM (Sertifikat Hak Milik)

Fasilitas: listrik, air PDAM
```

### 3.2 Improvement Metrics

| Aspek | Sebelum | Sesudah | Improvement |
|-------|---------|---------|-------------|
| Fields di-embed | 4 | 9 | +125% |
| Fields di API | 22 | 30 | +36% |
| Content richness | ~50 chars | ~500 chars | +900% |
| Data accuracy | 7,531 (all) | 2,568 (active) | Correct filter |

### 3.3 Project Unit Types Enhancement

**Masalah:** Projects (developer/perumahan) tidak memiliki data spesifik seperti `bedrooms`, `building_area` karena ini adalah data development-level, bukan unit-level.

**Solusi:** Mengambil data dari relasi `complex.types` (ComplexType model) yang berisi spesifikasi tiap tipe unit.

**Contoh PAGE_CONTENT Project (SESUDAH):**
```
Perumahan Green Valley

Properti dijual

Proyek baru dari developer PT Maju Jaya

Tipe unit tersedia: Type 36 2 kamar LB 36m² LT 72m², Type 54 3 kamar LB 54m² LT 90m²

Tersedia rumah 2-3 kamar tidur

Bangunan 1-2 lantai

Luas bangunan 36-54m²

Luas tanah 72-90m²

Perumahan modern dengan konsep minimalis...

Lokasi: Medan Sunggal, Kota Medan

Tipe: Perumahan

Fasilitas: security 24 jam, kolam renang, taman, playground
```

**Data yang di-aggregate dari Unit Types:**

| Field | Source | Contoh |
|-------|--------|--------|
| `unit_types` | ComplexType.name + specs | ["Type 36 2 kamar LB 36m²", ...] |
| `bedrooms_available` | ComplexType.bedrooms | [2, 3, 4] |
| `bathrooms_available` | ComplexType.bathrooms | [1, 2] |
| `building_area_min/max` | ComplexType.building_area | 36, 120 |
| `land_area_min/max` | ComplexType.land_area | 72, 200 |
| `floors_available` | ComplexType.floors | [1, 2] |
| `amenities` | ComplexType.amenities | ["ac", "water_heater", ...] |

**Query yang Sekarang Bisa Dijawab:**
- "proyek baru 3 kamar tidur" → match project dengan bedrooms_available contains 3
- "perumahan 2 lantai" → match project dengan floors_available contains 2
- "proyek luas tanah 100m²" → match project dengan land_area range includes 100

---

## 4. File yang Dimodifikasi

### Laravel API (metaproperty2026)

| File | Perubahan |
|------|-----------|
| `app/Http/Controllers/Api/Sync/SyncController.php` | Stats filter, fetchPendingListings fields, fetchPendingProjects unit types |
| `app/Http/Controllers/Api/Website/PropertyController.php` | Limit 100 → 500 |

### RAG System (Rag-Tesis)

| File | Perubahan |
|------|-----------|
| `src/knowledge/property_store.py` | `_create_document_text()` (incl. project unit types), metadata fields with min/max |
| `scripts/sync_properties.py` | Emoji encoding fix |

---

## 5. Text Preprocessing Details

### 5.1 HTML Cleaning

Beberapa deskripsi properti mengandung HTML tags dari rich text editor:

```python
# Input (raw dari database):
"<div><h1>Rumah Dijual</h1><p>Lokasi strategis...</p></div>"

# Processing:
clean_desc = re.sub(r'<[^>]+>', ' ', description)  # Remove HTML tags
clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()  # Normalize whitespace

# Output:
"Rumah Dijual Lokasi strategis..."
```

### 5.2 Terminology Mapping (Domain-Specific)

Mapping dari technical terms ke bahasa Indonesia untuk better semantic matching:

**Property Type Mapping:**
```python
type_map = {
    "house": "Rumah",
    "shophouse": "Ruko",
    "land": "Tanah",
    "apartment": "Apartemen",
    "warehouse": "Gudang",
    "perumahan": "Perumahan",
}
```

**Certificate Type Mapping:**
```python
cert_map = {
    "shm": "SHM (Sertifikat Hak Milik)",
    "shgb": "SHGB (Sertifikat Hak Guna Bangunan)",
    "hgb": "HGB",
    "girik": "Girik",
    "ppjb": "PPJB",
}
```

**Amenities Mapping:**
```python
amenity_map = {
    "electricity": "listrik",
    "water": "air PDAM",
    "furnished": "full furnished",
    "semi_furnished": "semi furnished",
    "swimming_pool": "kolam renang",
    "security_24": "security 24 jam",
    "playground": "playground",
    "jogging_track": "jogging track",
    "garden": "taman",
    "garage": "garasi",
    "carport": "carport",
}
```

### 5.3 Field Selection Strategy

**Embedded (page_content) - untuk Semantic Search:**

| Field | Importance | Rationale |
|-------|------------|-----------|
| `title` | High | Primary identifier |
| `description` | High | Rich semantic content |
| `additional_info` | Medium | Supplementary details |
| `amenities/facilities` | High | Key differentiator |
| `location` (area, district, city) | High | Location-based queries |
| `property_type` | Medium | Type filtering |
| `certificate_type` | Medium | Important for buyers |
| `listing_type` | Medium | sale vs rent context |

**Metadata (tidak di-embed) - untuk Filtering:**

| Field | Type | Use Case |
|-------|------|----------|
| `price` | float | Range filtering |
| `bedrooms` | int | Exact/range filtering |
| `bathrooms` | int | Exact/range filtering |
| `land_area` | float | Range filtering |
| `building_area` | float | Range filtering |
| `floors` | float | Range filtering |
| `status` | string | Status filtering |

---

## 6. Implikasi untuk Thesis

### 5.1 Research Contribution

1. **Domain-Specific Embedding Strategy**
   - Identifikasi field yang optimal untuk property domain
   - Mapping terminology (electricity → listrik)
   - Separation of semantic vs filter content

2. **Data Quality Impact on RAG**
   - Konsistensi filter antara data source dan embedding
   - Importance of rich content untuk semantic matching

### 5.2 Metrics yang Bisa Diukur

Setelah re-sync dengan data live, bisa diukur:

1. **Retrieval Quality**
   - Precision@5 sebelum vs sesudah optimasi
   - Recall untuk query semantic (e.g., "kolam renang")

2. **Query Coverage**
   - % query yang sebelumnya gagal, sekarang berhasil
   - Query types: location, features, certificate, price

3. **Token Efficiency**
   - Tokens per document sebelum vs sesudah
   - Cost per embedding operation

### 5.3 Novelty Claim

> "Domain-specific embedding optimization untuk Indonesian property market menunjukkan peningkatan retrieval quality melalui:
> 1. Field selection yang targeted untuk property attributes
> 2. Terminology mapping dari English technical terms ke Indonesian colloquial
> 3. Separation of semantic content (untuk embedding) dan categorical/numeric data (untuk metadata filtering)"

---

## 6. Next Steps

1. [ ] Deploy Laravel API changes ke server live
2. [ ] Update `.env` dengan URL API live
3. [ ] Run full sync dengan data production (~2,900 properties)
4. [ ] Measure retrieval quality dengan 30 test queries
5. [ ] Compare hasil dengan baseline (sebelum optimasi)
6. [ ] Implement multi-model comparison
7. [ ] Expand test queries ke 100

---

*Dokumen ini dibuat: 24 Januari 2026*
*Untuk: Thesis RAG Property Chatbot - Optimasi Embedding*
