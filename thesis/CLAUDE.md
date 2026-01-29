# CLAUDE.md - Panduan Pengerjaan Thesis RAG Property Search

> **PENTING**: Baca file ini terlebih dahulu sebelum mengerjakan thesis.

---

## 1. INFORMASI THESIS

### Judul
**Perancangan dan Implementasi Chatbot AI Berbasis RAG untuk Asisten Virtual Agen Properti**

### Fokus Utama
Perbandingan 3 strategi retrieval:
1. **Vector-Only** - Semantic search menggunakan ChromaDB
2. **API-Only** - Structured query ke Property API
3. **Hybrid** - Kombinasi keduanya dengan score fusion

### Institusi
- **Universitas**: Bina Nusantara University
- **Program**: BINUS Graduate Program - Master of Computer Science
- **Pembimbing**: Dr. Suryadiputra Liawatimena, S.Kom, PgDip.App.Sci

### Target
- **Halaman**: ~70 halaman (tidak termasuk lampiran)
- **Referensi**: Minimal 25 sumber (prioritas jurnal Q1-Q2)
- **Format**: APA 7th Edition

---

## 2. STRUKTUR FILE THESIS

```
d:\Project\Rag-Tesis\thesis\
├── CLAUDE.md                              ← FILE INI (panduan kerja)
├── Thesis_2026_v2_structure.md            ← Struktur thesis (clean, untuk Word)
├── Thesis_2026_v2_structure.docx          ← Versi Word dari struktur
├── Thesis_2026_v2_structure_with_refs.md  ← Struktur + code path references
├── Thesis 2026.docx                       ← Dokumen thesis utama (WIP)
├── Thesis 2026.md                         ← Versi MD dari docx (untuk AI baca)
├── paper_full.md                          ← Paper/draft untuk konsistensi data
├── Pedoman Penulisan Tesis...pdf          ← Pedoman resmi BINUS
└── Template penulisan Tesis BGP NEW.dotx  ← Template resmi BINUS
```

### Fungsi Setiap File
| File | Kapan Digunakan |
|------|-----------------|
| `Thesis_2026_v2_structure.md` | Referensi struktur saat menulis |
| `Thesis_2026_v2_structure_with_refs.md` | Mencari code path untuk penjelasan teknis |
| `Thesis 2026.md` | Melihat progress penulisan saat ini |
| `paper_full.md` | Memastikan konsistensi angka/data |
| `Pedoman Penulisan Tesis...pdf` | Cek aturan format BINUS |

---

## 3. STATUS PENGERJAAN

### Progress per BAB

| BAB | Status | Catatan |
|-----|--------|---------|
| Bagian Awal | ⬜ Belum | Halaman sampul, judul, abstrak, dll |
| BAB I: Pendahuluan | ✅ Selesai | File: BAB_I.md |
| BAB II: Tinjauan Pustaka | ✅ Selesai | File: BAB_II.md |
| BAB III: Metodologi | ✅ Selesai | File: BAB_III.md |
| BAB IV: Hasil | ✅ Selesai | File: BAB_IV.md |
| BAB V: Simpulan | ✅ Selesai | File: BAB_V.md |
| Daftar Pustaka | ✅ Selesai | File: REFERENCES.md (35 referensi) |
| Lampiran | ⬜ Belum | Gold questions, hasil detail, code |

### Prioritas Pengerjaan
1. **BAB IV** - Data sudah ada dari evaluasi
2. **BAB III** - Code sudah ada, tinggal dokumentasi
3. **BAB II** - Perlu research paper terdahulu
4. **BAB I** - Pendahuluan
5. **BAB V** - Simpulan (setelah semua selesai)

---

## 4. DATA HASIL EVALUASI

### Summary Metrics (30 Gold Questions)

| Method | Query Success | Mean CPR | Strict Success |
|--------|--------------|----------|----------------|
| **Hybrid** | **100%** | **97.61%** | **96.62%** |
| API Only | 73.33% | 73.35% | 72.62% |
| Vector Only | 50% | 55.33% | 33.04% |

### Confusion Matrix - Hybrid
```
                 Predicted
              Neg    Pos
Actual Neg    TN:2   FP:0
Actual Pos    FN:0   TP:28
```
- **Accuracy**: 100%
- **Total Questions**: 30 (28 positive, 2 negative)

### Hipotesis
- **H1**: Hybrid > Vector & API ✅ TERBUKTI
- **H2**: Akurasi > 80% ✅ TERBUKTI (100%)
- **H3**: Perbedaan signifikan antar strategi ✅ TERBUKTI

---

## 5. CODE PATH REFERENCES

### Core Implementation
| Komponen | Path |
|----------|------|
| ReAct Agent | `src/agents/react_agent.py` |
| Property Agent | `src/agents/property_agent.py` |
| Hybrid Search | `src/knowledge/hybrid_search.py` |
| MetaProperty Adapter | `src/adapters/metaproperty.py` |
| Settings/Config | `config/settings.py` |

### Frontend
| Komponen | Path |
|----------|------|
| Main App | `frontend/src/App.vue` |
| Chat Interface | `frontend/src/components/ChatInterface.vue` |
| Documentation Page | `frontend/src/components/DocumentationPage.vue` |

### Evaluation
| Komponen | Path |
|----------|------|
| Evaluation Script | `scripts/evaluate_v2.py` |
| Run Evaluation | `scripts/run_evaluation.py` |
| Gold Questions | `data/gold_questions.xlsx` |

### Important Code Sections
| Section | File:Line |
|---------|-----------|
| API Contract / Response Format | `frontend/src/components/DocumentationPage.vue:489-520` |
| 9 Agent Tools | `frontend/src/components/DocumentationPage.vue:211-244` |
| Evaluation Results Display | `frontend/src/components/DocumentationPage.vue:248-380` |
| Architecture Diagram | `frontend/src/components/DocumentationPage.vue:82-104` |
| Score Fusion Formula | `src/knowledge/hybrid_search.py` (0.6×semantic + 0.4×api_position) |

---

## 6. PANDUAN PENULISAN

### Bahasa
- **Indonesia formal akademis**
- Hindari kata-kata informal/slang
- Gunakan kalimat pasif untuk metodologi

### Terminologi Resmi BINUS
| Salah | Benar |
|-------|-------|
| Batasan Masalah | Ruang Lingkup Penelitian |
| Pernyataan Orisinalitas | Pernyataan Keaslian Tesis |
| Kerangka Penelitian | Kerangka Pemikiran |
| Kesimpulan | Simpulan |

### Format
- Referensi: **APA 7th Edition**
- Margin: Sesuai template BINUS
- Font: Times New Roman 12pt (atau sesuai template)
- Spasi: 1.5 atau 2.0 (sesuai pedoman)

### Konsistensi Data
- Semua angka harus sama antara `paper_full.md` dan thesis
- Pastikan tabel dan grafik konsisten
- Cross-check dengan hasil evaluasi aktual

---

## 7. API CONTRACT (PENTING)

Sistem ini dirancang **database-agnostic** - bisa menerima data dari sumber manapun selama response sesuai format.

### Required Endpoints
```
GET /api/properties
  Query Parameters:
  - listing_type: rent | sale
  - property_type: house | apartment | ...
  - min_price, max_price
  - bedrooms, bathrooms
  - location
  - lat, lng, radius (untuk nearby search)

GET /api/properties/{id}
  - Detail properti by ID
```

### Response Format
```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": number,
      "listing_type": "rent | sale",
      "property_type": "house | apartment | ...",
      "bedrooms": number,
      "bathrooms": number,
      "land_area": number,
      "building_area": number,
      "location": {
        "address": "string",
        "city": "string",
        "district": "string",
        "lat": number,
        "lng": number
      },
      "images": ["url1", "url2"],
      "url": "string"
    }
  ],
  "meta": {
    "total": number,
    "page": number,
    "per_page": number
  }
}
```

---

## 8. DAFTAR 9 AGENT TOOLS

| No | Tool | Fungsi |
|----|------|--------|
| 1 | `search_properties` | Pencarian dengan filter (harga, lokasi, tipe) |
| 2 | `search_nearby` | Pencarian dalam radius tertentu |
| 3 | `geocode_location` | Konversi alamat ke koordinat lat/lng |
| 4 | `search_knowledge` | Vector search di ChromaDB |
| 5 | `rerank_results` | Cross-encoder reranking |
| 6 | `get_property_details` | Ambil detail properti by ID |
| 7 | `get_property_types` | Daftar tipe properti tersedia |
| 8 | `get_locations` | Daftar lokasi/area tersedia |
| 9 | `no_properties_found` | Handler jika tidak ada hasil |

---

## 9. WORKFLOW PENGERJAAN

### Memulai Session Baru
1. Baca `CLAUDE.md` (file ini)
2. Cek status progress di section 3
3. Baca `Thesis 2026.md` untuk melihat tulisan terkini
4. Lanjutkan dari BAB yang sedang dikerjakan

### Menulis BAB Baru
1. Buka `Thesis_2026_v2_structure.md` untuk outline
2. Buka `Thesis_2026_v2_structure_with_refs.md` untuk code references
3. Tulis di `Thesis 2026.md` (atau langsung di .docx)
4. Cross-check angka dengan `paper_full.md`

### Setelah Selesai Menulis
1. Update status di section 3 file ini
2. Pastikan format sesuai pedoman BINUS
3. Convert ke Word jika perlu:
   ```bash
   pandoc "Thesis 2026.md" -o "Thesis 2026.docx" --reference-doc="Template penulisan Tesis BGP NEW.dotx"
   ```

---

## 10. CATATAN KHUSUS

### Yang Sudah Diputuskan
- ✅ Tidak perlu ERD database (arsitektur berbasis API Contract)
- ✅ Hipotesis opsional (sudah ditambahkan untuk jaga-jaga)
- ✅ User Experience Survey opsional (tujuan penelitian fokus teknis)
- ✅ Menggunakan 9 tools (bukan 6)

### Yang Perlu Diperhatikan
- ⚠️ Penelitian Terdahulu: Perlu cari 10+ paper relevan
- ⚠️ Tinjauan Pustaka: Semua sub-bab perlu ditulis
- ⚠️ Daftar Pustaka: Kumpulkan referensi selama menulis

### Konversi Word
Gunakan perintah ini untuk hasil yang konsisten:
```bash
pandoc "[source].md" -o "[output].docx" --reference-doc="Thesis 2026.docx"
```

---

## 11. QUICK COMMANDS

```bash
# Convert struktur ke Word
pandoc "Thesis_2026_v2_structure.md" -o "Thesis_2026_v2_structure.docx" --reference-doc="Thesis 2026.docx"

# List files di thesis folder
ls "d:/Project/Rag-Tesis/thesis"

# Cari keyword di codebase
grep -r "keyword" "d:/Project/Rag-Tesis/src"
```

---

**Last Updated**: 2026-01-29
**Session Context**: Struktur thesis sudah final, siap mulai penulisan per BAB
