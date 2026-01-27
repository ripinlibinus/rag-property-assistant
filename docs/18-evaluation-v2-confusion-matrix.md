# Evaluation V2: Constraint-Based Evaluation with Confusion Matrix

## Overview

Dokumen ini menjelaskan metodologi evaluasi V2 untuk sistem RAG Property Chatbot. V2 menggunakan **constraint-based evaluation** yang mengevaluasi setiap properti berdasarkan constraint yang didefinisikan di gold standard, kemudian menghitung **Confusion Matrix** untuk mengukur performa query-level.

### Perbandingan V1 vs V2

| Aspek | V1 (MRR-based) | V2 (Constraint-based) |
|-------|----------------|----------------------|
| Penilaian | Binary relevance (relevan/tidak) | Multi-constraint check |
| Granularitas | Per-properti | Per-constraint + per-properti |
| Metrics utama | MRR, Precision@K | PCA, CPR, Confusion Matrix |
| Gold Standard | Implicit (manual rating) | Explicit (constraint JSON) |
| Reproducibility | Subjektif | Objektif & reproducible |

---

## 1. Core Concepts

### 1.1 Constraint Types

Setiap gold standard question memiliki constraint yang harus dipenuhi:

| Constraint | Deskripsi | Contoh |
|------------|-----------|--------|
| `property_type` | Tipe properti | house, apartment, ruko, land |
| `listing_type` | Tipe listing | sale, rent |
| `location` | Lokasi (keyword atau geo) | cemara, ringroad, lat/lng |
| `price` | Range harga | min: 500M, max: 1B |
| `bedrooms` | Jumlah kamar | min: 3, exact: 4 |
| `floors` | Jumlah lantai | min: 2, max: 3, exact: 2 |

### 1.2 Constraint Result

Setiap constraint dievaluasi dengan 4 kemungkinan hasil:

| Result | Arti |
|--------|------|
| **PASS** | Properti memenuhi constraint |
| **FAIL** | Properti tidak memenuhi constraint |
| **NA** | Constraint tidak applicable (tidak ada di gold) |
| **MISSING** | Data properti tidak tersedia untuk constraint ini |

### 1.3 Constraint Pass Ratio (CPR)

CPR mengukur seberapa banyak constraint yang dipenuhi oleh sebuah properti:

$$CPR_{property} = \frac{\text{Count}(PASS)}{\text{Count}(PASS) + \text{Count}(FAIL)}$$

**Note:** NA dan MISSING tidak dihitung dalam CPR.

**Contoh:**
```
Properti: Rumah di Cemara, 900jt, 2 kamar, 2 lantai
Gold: house, sale, cemara, price 800jt-1.2B, bedrooms >= 3, floors >= 2

property_type: PASS (house = house)
listing_type: PASS (sale = sale)
location: PASS (cemara match)
price: PASS (900jt dalam range)
bedrooms: FAIL (2 < 3)
floors: PASS (2 >= 2)

CPR = 5/6 = 0.833 (83.3%)
```

---

## 2. Metrics

### 2.1 Per-Constraint Accuracy (PCA)

PCA mengukur akurasi sistem untuk setiap constraint type secara terpisah:

$$PCA_{constraint} = \frac{\text{Total PASS untuk constraint}}{\text{Total evaluasi untuk constraint}}$$

**Contoh output:**
```
PCA:
  property_type: 95.0%
  listing_type: 92.5%
  location: 78.3%
  price: 85.0%
  bedrooms: 70.0%
  floors: 88.0%
```

PCA berguna untuk mengidentifikasi constraint mana yang lemah.

### 2.2 Mean CPR

Rata-rata CPR dari semua properti yang dikembalikan:

$$Mean\ CPR = \frac{\sum_{i=1}^{n} CPR_i}{n}$$

### 2.3 Strict Success Ratio

Persentase properti yang **semua** constraint-nya PASS:

$$Strict\ Success = \frac{\text{Count}(CPR = 100\%)}{\text{Total properti}}$$

### 2.4 Query Success

Query dianggap sukses jika:
- **has_data expected:** Ada hasil DAN Mean CPR >= Threshold T
- **no_data expected:** Tidak ada hasil

$$Success = \begin{cases} 1 & \text{if } expected=has\_data \land has\_results \land CPR \geq T \\ 1 & \text{if } expected=no\_data \land \neg has\_results \\ 0 & \text{otherwise} \end{cases}$$

Default Threshold T = 0.6 (60%)

### 2.5 Confusion Matrix

Query-level confusion matrix:

|  | Predicted Positive (has results, CPR >= T) | Predicted Negative |
|--|-------------------------------------------|-------------------|
| **Actual Positive (expected: has_data)** | TP | FN |
| **Actual Negative (expected: no_data)** | FP | TN |

**Derived Metrics:**

$$Precision = \frac{TP}{TP + FP}$$

$$Recall = \frac{TP}{TP + FN}$$

$$F1 = \frac{2 \times Precision \times Recall}{Precision + Recall}$$

$$Accuracy = \frac{TP + TN}{TP + FP + TN + FN}$$

---

## 3. Gold Standard Format

### 3.1 File Structure

```
data/gold/
├── locations.json       # Master lokasi dengan koordinat
├── questions_v2.json    # Gold standard questions
└── gold_editor.html     # UI untuk edit gold (dengan Google Maps picker)
```

### 3.2 Gold Editor Features

Buka `data/gold/gold_editor.html` di browser untuk mengedit gold standard:

**Features:**
- Load/Export JSON file
- Add, edit, delete, duplicate questions
- Set constraints: property_type, listing_type, price, bedrooms
- **🗺️ Map Picker** - Klik "Pick on Map" untuk set koordinat dari Google Maps:
  - Search lokasi (e.g., "Ringroad Medan", "Cemara Asri")
  - Klik peta untuk pilih titik
  - Drag marker untuk adjust
  - Set radius coverage (km)
  - Visualisasi radius dengan circle overlay
- Live JSON preview
- Stats: total questions, categories, expected results

### 3.2 locations.json

```json
{
  "version": "1.0",
  "locations": {
    "cemara_asri": {
      "name": "Cemara Asri",
      "keywords": ["cemara", "cemara asri"],
      "lat": 3.6234,
      "lng": 98.7012,
      "radius_km": 2.0
    }
  }
}
```

### 3.3 questions_v2.json

```json
{
  "version": "2.0",
  "threshold_t": 0.6,
  "price_tolerance": 0.10,
  "questions": [
    {
      "id": 1,
      "question": "Carikan rumah dijual di daerah cemara",
      "category": "location_simple",
      "expected_result": "has_data",
      "constraints": {
        "property_type": "house",
        "listing_type": "sale",
        "location": {
          "keywords": ["cemara", "cemara asri"],
          "lat": 3.6234,
          "lng": 98.7012,
          "radius_km": 2.0
        }
      },
      "notes": "Simple location search"
    }
  ]
}
```

---

## 4. Location Matching

### 4.1 Keyword Match (Primary)

Sistem pertama mencoba keyword matching pada field location/address properti:

```python
for keyword in gold.location.keywords:
    if keyword.lower() in property.location.lower():
        return PASS
```

### 4.2 Geo Distance (Fallback)

Jika keyword tidak cocok tapi koordinat tersedia, gunakan Haversine distance:

$$d = 2R \arcsin\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}$$

Dimana:
- R = 6371 km (radius bumi)
- φ = latitude dalam radian
- λ = longitude dalam radian

```python
if distance_km <= gold.location.radius_km:
    return PASS
```

---

## 5. Price Interpretation Rules

### 5.1 Indonesian Price Range Patterns

Suffix "-an" dalam Bahasa Indonesia berarti "dalam kisaran angka tersebut":

| Pattern | Interpretasi | Min | Max |
|---------|-------------|-----|-----|
| "harga 1M an" | Kisaran 1 Milyar | 1.000.000.000 | 1.999.999.999 |
| "harga 800jt an" | Kisaran 800 juta | 800.000.000 | 899.999.999 |
| "harga 500jt an" | Kisaran 500 juta | 500.000.000 | 599.999.999 |
| "harga 2M an" | Kisaran 2 Milyar | 2.000.000.000 | 2.999.999.999 |

**Analogi:**
- "umur 20-an" = 20-29 tahun
- "tahun 90-an" = 1990-1999

### 5.2 Explicit Range Patterns

| Pattern | Interpretasi | Min | Max |
|---------|-------------|-----|-----|
| "dibawah X" / "maksimal X" | Batas atas | - | X |
| "diatas X" / "minimal X" | Batas bawah | X | - |
| "sekitar X" / "kurang lebih X" | ±10% | X × 0.9 | X × 1.1 |
| "antara X sampai Y" | Range eksplisit | X | Y |

### 5.3 Constraint Evaluation

Untuk constraint dengan min/max eksplisit, toleransi dapat diterapkan:

$$valid = price_{min} \times (1 - tolerance) \leq actual \leq price_{max} \times (1 + tolerance)$$

Default tolerance = 10% (hanya untuk "sekitar X" queries)

---

## 5.4 Future Work: Confirmation for Ambiguous Queries

**Problem:** User sering mengetik cepat tanpa detail lengkap. "harga 1M an" bisa berarti:
- 1B - 2B (interpretasi linguistik standar)
- User sebenarnya tidak mau di atas 1.5B

**Proposed Solution:** Agent melakukan konfirmasi untuk query yang bersifat persepsi:

```
User: Carikan rumah di cemara harga 1M an
Agent: Saya akan mencari rumah dengan harga 1 Milyar - 2 Milyar.
       Apakah range ini sesuai, atau Anda memiliki batas maksimal tertentu?

User: maksimal 1.5M saja
Agent: Baik, saya cari rumah di Cemara dengan harga 1M - 1.5M...
```

**Implementation Notes:**
- Detect ambiguous price patterns ("-an", "sekitar", "kurang lebih")
- Generate confirmation message before search
- Allow user to adjust or confirm
- Log user preference for personalization

---

## 6. Evaluation Workflow

### 6.1 Run Evaluation

```bash
# Run with 5 questions first
python scripts/evaluate_v2.py --limit 5

# Run full evaluation
python scripts/evaluate_v2.py

# With specific method
python scripts/evaluate_v2.py --method hybrid --llm openai

# Incremental evaluation (re-run Q4-Q8)
python scripts/evaluate_v2.py --from 4 --to 8 --output data/evaluation/v2/existing_dir/

# Use existing results (skip agent run)
python scripts/evaluate_v2.py --results path/to/results.json --skip-run

# With API verification (fetch actual property data)
python scripts/evaluate_v2.py --verify

# Recalculate metrics only (from existing results)
python scripts/evaluate_v2.py --skip-run --output data/evaluation/v2/existing_dir/
```

**CLI Options:**
| Option | Description |
|--------|-------------|
| `--gold PATH` | Gold standard JSON (default: data/gold/questions_v2.json) |
| `--method` | Search method: hybrid, api_only, vector_only |
| `--llm` | LLM provider: openai, anthropic, google |
| `--limit N` | Run only first N questions |
| `--from N` | Start from question N (1-indexed) |
| `--to N` | End at question N (1-indexed) |
| `--output DIR` | Custom output directory |
| `--results PATH` | Use existing results JSON |
| `--skip-run` | Don't run agent, only recalculate |
| `--verify` | Verify extracted properties against API |
| `--reparse` | Re-parse properties from response text |
| `--threshold` | Override CPR threshold |
| `-v, --verbose` | Verbose logging |

### 6.2 Output Files

```
data/evaluation/v2/{method}_{llm}_{timestamp}/
├── results.json      # Raw agent results with properties
├── metrics.json      # Calculated metrics
├── evaluation.html   # Detail HTML report
└── run_log.json      # Audit trail of runs
```

### 6.3 Review HTML Report

Buka `evaluation.html` di browser untuk:
- Summary cards (Total, CPR, F1, etc.)
- PCA breakdown chart
- Confusion matrix visualization
- Per-query constraint table dengan expandable property details
- Filter by passed/failed
- **Manual review features** (lihat Section 6.4)

### 6.4 Manual Review UI

HTML report mendukung manual override per-constraint:

**Fitur:**
1. **Clickable Constraint Badges (Q1-Q21)**
   - Klik badge PASS/FAIL untuk toggle ke status lain
   - Cycle: original → pass → fail → na → original
   - Badge yang di-override ditandai dengan border ungu dan "*"

2. **Manual Evaluation Buttons (Q22-Q30)**
   - Untuk pertanyaan yang butuh evaluasi manual (e.g., feature search: CCTV, kolam renang)
   - Klik tombol **PASS** atau **FAIL** pada property card
   - Tambahkan komentar untuk dokumentasi

3. **Real-time CPR Recalculation**
   - Setiap klik badge/button, CPR property otomatis dihitung ulang
   - CPR query juga di-update

4. **Save All Evaluations**
   - Tombol ungu di header "Query Details"
   - Export semua overrides + manual evaluations ke `manual_input.json`
   - File ini digunakan untuk regenerate report dengan metrics final

### 6.5 Manual Evaluation Workflow (Complete)

Workflow lengkap untuk evaluasi dengan revisi manual:

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Jalankan evaluasi awal                                 │
├─────────────────────────────────────────────────────────────────┤
│  python scripts/evaluate_v2.py --verify                         │
│                                                                 │
│  Output: data/evaluation/v2/{method}_{llm}_{timestamp}/         │
│          ├── results.json                                       │
│          ├── metrics.json                                       │
│          └── evaluation.html                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Buka evaluation.html di browser                        │
├─────────────────────────────────────────────────────────────────┤
│  Q1-Q21 (Auto evaluation):                                      │
│  - Expand query → expand property → klik badge constraint       │
│  - Toggle: PASS ↔ FAIL ↔ NA                                     │
│                                                                 │
│  Q22-Q30 (Manual evaluation):                                   │
│  - Lihat detail properti (foto, lokasi, spesifikasi)            │
│  - Klik tombol PASS atau FAIL                                   │
│  - Tambahkan komentar untuk dokumentasi                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Klik "Save All Evaluations"                            │
├─────────────────────────────────────────────────────────────────┤
│  → Download manual_input.json                                   │
│  → Pindahkan ke folder project atau evaluation                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Re-run dengan manual input                             │
├─────────────────────────────────────────────────────────────────┤
│  python scripts/evaluate_v2.py \                                │
│    --results data/evaluation/v2/{folder}/results.json \         │
│    --manual-input manual_input.json \                           │
│    --output data/evaluation/v2/{folder}_final                   │
│                                                                 │
│  Output: Folder baru dengan metrics FINAL                       │
│          ├── evaluation.html  ← Report dengan metrics final     │
│          ├── metrics.json     ← Metrics untuk thesis            │
│          └── run_log.json                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 6.6 Format manual_input.json

```json
{
  "timestamp": "2026-01-26T12:30:00.000Z",
  "source_report": "hybrid_openai_20260126_122531",
  "summary": {
    "constraint_overrides_count": 5,
    "manual_evaluations_count": 12
  },
  "constraint_overrides": {
    "1": {
      "0": {"location": "pass"},
      "2": {"price": "fail", "bedrooms": "pass"}
    },
    "5": {
      "1": {"property_type": "pass"}
    }
  },
  "manual_evaluations": {
    "22": {
      "0": {"result": "pass", "comment": "CCTV visible in listing photos"},
      "1": {"result": "fail", "comment": "No CCTV mentioned"}
    },
    "25": {
      "0": {"result": "pass", "comment": "Swimming pool confirmed in images"}
    }
  }
}
```

**Struktur:**
- `constraint_overrides`: Revisi constraint untuk Q1-Q21
  - Key level 1: Query ID
  - Key level 2: Property index (0-based)
  - Key level 3: Constraint name → new value (pass/fail/na)

- `manual_evaluations`: Evaluasi manual untuk Q22-Q30
  - Key level 1: Query ID
  - Key level 2: Property index (0-based)
  - Value: `{result: "pass"|"fail", comment: "..."}`

### 6.7 CLI Options (Updated)

| Option | Description |
|--------|-------------|
| `--gold PATH` | Gold standard JSON (default: data/gold/questions_v2.json) |
| `--method` | Search method: hybrid, api_only, vector_only |
| `--llm` | LLM provider: openai, anthropic, google |
| `--limit N` | Run only first N questions |
| `--from N` | Start from question N (1-indexed) |
| `--to N` | End at question N (1-indexed) |
| `--output DIR` | Custom output directory |
| `--results PATH` | Use existing results JSON |
| `--manual-input PATH` | **Apply manual evaluations from JSON file** |
| `--skip-run` | Don't run agent, only recalculate |
| `--verify` | Verify extracted properties against API |
| `--reparse` | Re-parse properties from response text |
| `--threshold` | Override CPR threshold |
| `-v, --verbose` | Verbose logging |

### 6.8 API Verification

Untuk memverifikasi extracted properties dengan data API:

```bash
# Run dengan --verify flag
python scripts/evaluate_v2.py --verify

# Atau reparse dan verify dari existing results
python scripts/evaluate_v2.py --results path/to/results.json --reparse --verify
```

**Verification Features:**
- Fetch actual property data dari API by slug
- Compare extracted vs API values (price, bedrooms, bathrooms, etc.)
- Mark mismatches dalam results untuk audit
- Display "Verified" badge di HTML report

---

## 7. Incremental Evaluation

### 7.1 Use Case

Setelah review HTML, temukan masalah di Q4-Q8. Setelah optimize RAG/prompt:

```bash
# Re-run hanya Q4-Q8, merge dengan existing
python scripts/evaluate_v2.py --from 4 --to 8 \
    --output data/evaluation/v2/hybrid_openai_20260125_120000/
```

### 7.2 Behavior

1. Load existing results.json dari output dir
2. Run agent hanya untuk Q4-Q8
3. Merge hasil baru dengan existing (replace by query_id)
4. Recalculate metrics dari merged data
5. Regenerate HTML

---

## 8. Module Structure

```
src/evaluation/
├── __init__.py
├── models.py              # Data classes
│   ├── ConstraintResult   # Enum: PASS, FAIL, NA, MISSING
│   ├── GoldQuestion       # Gold standard question
│   ├── PropertyCheck      # Per-property results
│   ├── QueryEvaluation    # Per-query results
│   ├── EvaluationMetrics  # Final metrics
│   └── ConfusionMatrix    # CM with P/R/F1
├── constraint_checker.py  # Constraint checking logic
│   ├── haversine_distance()
│   ├── check_property_type()
│   ├── check_listing_type()
│   ├── check_location()
│   ├── check_price()
│   ├── check_bedrooms()
│   ├── check_floors()
│   └── check_all()
├── evaluator.py           # Main evaluation engine
│   ├── load_gold_standard()
│   ├── evaluate_query()
│   ├── calculate_pca()
│   ├── calculate_confusion_matrix()
│   ├── calculate_metrics()
│   └── run_evaluation()
└── html_report.py         # HTML report generator
```

---

## 9. Interpreting Results

### 9.1 Good Performance

```
Mean CPR: >= 80%
Strict Success: >= 60%
F1 Score: >= 80%
Precision: >= 85%
Recall: >= 75%
```

### 9.2 Areas to Investigate

| Symptom | Possible Cause |
|---------|----------------|
| Low PCA location | Location extraction/matching issue |
| Low PCA price | Price parsing atau API filter |
| High FP | System returning irrelevant results |
| High FN | System missing relevant results |
| Low Strict Success | Multiple constraints failing |

### 9.3 Per-Category Analysis

Review category_metrics untuk identifikasi:
- `location_simple` low? → Basic location search problem
- `location_price` low? → Price filtering issue
- `feature_search` low? → Feature extraction problem
- `context_followup` low? → Context handling issue

---

## 10. Comparison with V1

### 10.1 When to Use V1

- Quick subjective assessment
- Early prototyping
- When gold standard not ready

### 10.2 When to Use V2

- Thesis/paper evaluation (recommended)
- Systematic comparison of methods
- Identifying specific failure modes
- Reproducible benchmarks

### 10.3 Migration

V1 results archived di:
```
data/evaluation-v1-mrr/
├── hybrid/
├── scripts_backup/
└── README.md
```

---

## 11. References

### Constraint-Based Evaluation

- Dalvi et al. (2022). Towards Trustworthy Entity Alignment Using Constraint-Based Evaluation.

### Confusion Matrix for IR

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Chapter 8.

### RAG Evaluation

- ES, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated Evaluation of Retrieval Augmented Generation.

---

---

## 12. URL Enrichment

### 12.1 Problem

Ketika search menggunakan ChromaDB fallback (semantic search), property URL tidak tersedia karena ChromaDB metadata tidak menyimpan `slug` atau `url_view`. Ini menyulitkan verifikasi manual.

### 12.2 Solution

Sistem melakukan **URL enrichment** setelah ChromaDB search:

```
ChromaDB semantic search → property IDs
                              ↓
              API call: GET /api/v1/properties?ids=123,456,789
                              ↓
              Enrich properties with url_view from API
                              ↓
              Return ke LLM dengan URL lengkap
```

### 12.3 Implementation

**API Requirement:**
- Endpoint: `GET /api/v1/properties?ids=1,2,3`
- Response harus include `url_view` field

**Code Flow (hybrid_search.py):**
1. `_fallback_semantic_search()` runs ChromaDB query
2. Collects property IDs from results
3. Calls `_fetch_urls_from_api()` with IDs
4. Updates `prop.url_view` for each property

### 12.4 Usage

URL akan muncul di:
- Chat response (untuk user verification)
- Evaluation HTML report (untuk reviewer)
- Test results JSON (untuk automated processing)

---

*Document created: 25 January 2026*
*Last updated: 26 January 2026*
*For: Thesis RAG Property Chatbot Evaluation V2*
