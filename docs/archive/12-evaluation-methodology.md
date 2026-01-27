# Evaluation Methodology for RAG Property Chatbot

> **Note:** This document describes the V1 evaluation methodology using IR metrics (MRR, Precision@K).
> For the updated V2 methodology using constraint-based evaluation with confusion matrix,
> see [docs/18-evaluation-v2-confusion-matrix.md](./18-evaluation-v2-confusion-matrix.md).

## Overview

Dokumen ini menjelaskan metode evaluasi untuk mengukur kualitas hasil pencarian properti dari sistem RAG chatbot. Evaluasi menggunakan kombinasi metrics standar Information Retrieval (IR) yang telah divalidasi secara akademis.

---

## 3-Phase Evaluation Framework

Evaluasi sistem RAG Property Chatbot dilakukan dalam **3 Phase** untuk mendapatkan hasil yang komprehensif:

| Phase | Fokus | Variabel | Konstanta |
|-------|-------|----------|-----------|
| 1 | Search Method | API, Vector, Hybrid | LLM: GPT-4o-mini |
| 2 | LLM Model | GPT, Claude, Gemini | Search: Best from Phase 1 |
| 3 | User Testing | Real Users | Best Config from Phase 2 |

### Phase 1: Search Method Comparison

**Objective:** Membandingkan 3 metode search untuk menemukan yang terbaik.

| Method | Deskripsi |
|--------|-----------|
| API Only | Hanya menggunakan REST API search |
| Vector Only | Hanya menggunakan ChromaDB semantic search |
| Hybrid (60/40) | Kombinasi keduanya dengan bobot 60% semantic, 40% API |

**Command:**
```bash
python scripts/test_sequential_chat.py --method hybrid
python scripts/test_sequential_chat.py --method api_only
python scripts/test_sequential_chat.py --method vector_only
```

### Phase 2: LLM Model Comparison

**Objective:** Membandingkan 3 LLM model dengan search method terbaik dari Phase 1.

| Model | Provider |
|-------|----------|
| GPT-4o-mini | OpenAI |
| Claude 3 Haiku | Anthropic |
| Gemini 1.5 Flash | Google |

**Command:**
```bash
python scripts/test_sequential_chat.py --method [best] --llm openai
python scripts/test_sequential_chat.py --method [best] --llm anthropic
python scripts/test_sequential_chat.py --method [best] --llm google
```

### Phase 3: User Testing

**Objective:** Validasi dengan real users menggunakan konfigurasi terbaik.

| Aspek | Detail |
|-------|--------|
| Jumlah User | 5-10 orang |
| Query per User | 10 pertanyaan bebas |
| Evaluasi | User menilai hasil via HTML interface |
| Feedback | Kuantitatif + Kualitatif |

### Generate Comparison Report

```bash
python scripts/compare_methods.py --phase 1  # Search method comparison
python scripts/compare_methods.py --phase 2  # LLM model comparison
```

---

## 1. Metrics yang Digunakan

### 1.1 Precision@K

Mengukur proporsi hasil yang relevan dari K hasil pertama (Manning et al., 2008).

$$Precision@K = \frac{\text{Jumlah hasil relevan dalam K teratas}}{K}$$

**Contoh:** Query mengembalikan 5 hasil, 4 relevan:
$$Precision@5 = \frac{4}{5} = 0.80 = 80\%$$

**Catatan:** Jika hasil < K, maka denominator = jumlah hasil aktual.

### 1.2 Overall Precision

Mengukur proporsi hasil relevan dari **semua** hasil yang dikembalikan (Manning et al., 2008).

$$Overall\ Precision = \frac{\text{Jumlah hasil relevan}}{\text{Total hasil dikembalikan}}$$

**Contoh:** Query mengembalikan 8 hasil, 6 relevan:
$$Overall\ Precision = \frac{6}{8} = 0.75 = 75\%$$

**Perbedaan dengan Precision@K:**
- Precision@K hanya menghitung K hasil pertama
- Overall Precision menghitung semua hasil

### 1.3 Mean Reciprocal Rank (MRR)

Mengukur seberapa cepat sistem menemukan hasil relevan **pertama** (Voorhees, 1999; Craswell, 2009).

$$MRR = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{rank_i}$$

Dimana:
- $|Q|$ = jumlah query
- $rank_i$ = posisi hasil relevan pertama untuk query ke-i
- Jika tidak ada hasil relevan, reciprocal rank = 0

**Contoh:**

| Query | Posisi Relevan Pertama | Reciprocal Rank |
|-------|------------------------|-----------------|
| Q1 | 1 | 1/1 = 1.000 |
| Q2 | 3 | 1/3 = 0.333 |
| Q3 | 2 | 1/2 = 0.500 |
| Q4 | Tidak ada | 0.000 |

$$MRR = \frac{1.000 + 0.333 + 0.500 + 0.000}{4} = 0.458$$

**Interpretasi MRR:**
- MRR = 1.0 → Hasil relevan selalu di posisi pertama
- MRR = 0.5 → Rata-rata hasil relevan di posisi kedua
- MRR mendekati 0 → Hasil relevan jauh di bawah atau tidak ada

**Mengapa MRR penting untuk chatbot:**
User chatbot cenderung melihat hasil pertama. MRR mengukur seberapa baik sistem menempatkan hasil relevan di posisi teratas.

### 1.4 Success Rate (Binary)

Mengukur apakah query berhasil mendapatkan **minimal 1** hasil yang relevan (Voorhees, 2002).

$$Success\ Rate = \frac{\text{Query dengan } \geq 1 \text{ hasil relevan}}{\text{Total query}}$$

**Definisi Success (Binary Relevance):**
```
success = 1  jika  relevant_count >= 1
success = 0  jika  relevant_count == 0
```

**Catatan:** Pendekatan binary ini adalah standar dalam TREC (Text REtrieval Conference) dan telah divalidasi secara akademis (Voorhees, 2002).

### 1.5 Coverage

Mengukur berapa persen query yang bisa dijawab sistem (ada hasil).

$$Coverage = \frac{\text{Query dengan hasil} > 0}{\text{Total query}}$$

**Perbedaan Success vs Coverage:**
- **Coverage:** Sistem mengembalikan hasil (bisa relevan atau tidak)
- **Success:** Sistem mengembalikan hasil yang relevan

---

## 2. Skala Penilaian

### 2.1 Binary Relevance (Per Properti)

Setiap properti dinilai secara binary:

| Skor | Arti | Kriteria |
|------|------|----------|
| 1 | Relevan | Properti sesuai dengan kriteria query |
| 0 | Tidak relevan | Properti tidak sesuai kriteria query |

**Contoh penilaian:**
| Query | Properti | Penilaian | Alasan |
|-------|----------|-----------|--------|
| "rumah dijual di cemara" | Rumah di Cemara, Dijual | 1 (Relevan) | Lokasi dan tipe sesuai |
| "rumah dijual di cemara" | Ruko di Cemara, Dijual | 0 (Tidak) | Tipe tidak sesuai |
| "rumah harga < 1M" | Rumah 800jt | 1 (Relevan) | Harga sesuai |
| "rumah harga < 1M" | Rumah 1.2M | 0 (Tidak) | Harga tidak sesuai |

### 2.2 Query-Level Rating (Response Quality)

Rating subjektif untuk kualitas keseluruhan respons:

| Skor | Kriteria |
|------|----------|
| 5 | Semua hasil sangat relevan |
| 4 | Mayoritas relevan (>70%) |
| 3 | Cukup relevan (50-70%) |
| 2 | Sedikit relevan (<50%) |
| 1 | Tidak ada yang relevan |
| 0 | Error / tidak ada hasil |

---

## 3. Menangani Query dengan 0 Hasil

### Kasus 1: Correct Empty (Memang Tidak Ada di Database)

Query: "cari gudang di KIM" → Database tidak punya gudang di KIM

| Metric | Nilai | Keterangan |
|--------|-------|------------|
| Precision | N/A | Tidak dihitung |
| MRR | N/A | Tidak dihitung |
| Success | 1 | Correct empty - sistem benar |
| Notes | "no data exists" | |

### Kasus 2: False Negative (Seharusnya Ada, Tapi Tidak Ditemukan)

Query: "cari rumah di cemara" → Harusnya ada, tapi sistem return 0

| Metric | Nilai | Keterangan |
|--------|-------|------------|
| Precision | N/A | Tidak dihitung |
| MRR | 0 | Gagal menemukan |
| Success | 0 | Gagal |
| Notes | "should have results" | |

---

## 4. Confusion Matrix Interpretation

Untuk memahami performa sistem secara keseluruhan:

### 4.1 Definisi

|  | **Actual: Relevan** | **Actual: Tidak Relevan** |
|--|---------------------|---------------------------|
| **Predicted: Returned** | True Positive (TP) | False Positive (FP) |
| **Predicted: Not Returned** | False Negative (FN) | True Negative (TN) |

### 4.2 Dalam Konteks RAG Property

| Komponen | Definisi |
|----------|----------|
| **TP** | Properti relevan yang dikembalikan sistem |
| **FP** | Properti tidak relevan yang dikembalikan sistem |
| **FN** | Properti relevan yang TIDAK dikembalikan (missed) |
| **TN** | Properti tidak relevan yang tidak dikembalikan |

### 4.3 Hubungan dengan Success Field

| Situasi | Success | Alasan |
|---------|---------|--------|
| Query dengan ≥1 hasil relevan | 1 | Ada TP |
| Query dengan hasil tapi semua tidak relevan | 0 | Hanya FP |
| Query tanpa hasil, data memang tidak ada | 1 | Correct empty (TN) |
| Query tanpa hasil, seharusnya ada | 0 | False Negative |

---

## 5. Format Evaluasi Manual

### 5.1 Data yang Dikumpulkan per Query

| Field | Tipe | Sumber | Deskripsi |
|-------|------|--------|-----------|
| query_id | int | Auto | ID pertanyaan (1-30) |
| question | string | Auto | Teks pertanyaan |
| category | string | Auto | Kategori query |
| results_count | int | Auto | Jumlah hasil dikembalikan |
| relevant_count | int | **Manual** | Jumlah hasil relevan |
| first_relevant_rank | int | **Manual/Auto** | Posisi hasil relevan pertama (1-based) |
| overall_precision | float | Auto | relevant_count / results_count |
| precision_at_5 | float | Auto | relevan di top 5 / min(results, 5) |
| mrr | float | Auto | 1 / first_relevant_rank |
| success | 0/1 | Auto | 1 jika relevant_count ≥ 1 |
| response_quality | 0-5 | **Manual** | Rating subjektif |
| notes | string | **Manual** | Catatan (misal: "no data exists") |

### 5.2 Contoh CSV

```csv
query_id,question,category,results_count,relevant_count,first_relevant_rank,overall_precision,precision_at_5,mrr,success,response_quality,notes
1,Carikan rumah dijual di daerah cemara,location_simple,5,4,1,0.80,0.80,1.00,1,4,
2,Carikan rumah dijual di daerah ringroad,location_simple,5,5,1,1.00,1.00,1.00,1,5,
3,apakah ada gudang di KIM?,property_type,0,0,,,,0,1,0,no data exists
4,cari rumah di cemara,location_simple,0,0,,,,0,0,0,should have results
5,cari rumah harga 1M di cemara,location_price,5,3,2,0.60,0.60,0.50,1,3,
```

---

## 6. Cara Menghitung Metrics Akhir

### 6.1 Mean Precision@5

Hanya dari query yang memiliki hasil (results_count > 0):

$$Mean\ Precision@5 = \frac{\sum Precision@5}{n_{queries\ with\ results}}$$

### 6.2 Mean Overall Precision

Hanya dari query yang memiliki hasil:

$$Mean\ Overall\ Precision = \frac{\sum Overall\ Precision}{n_{queries\ with\ results}}$$

### 6.3 Mean Reciprocal Rank (MRR)

Dari query yang memiliki hasil (RR = 0 jika tidak ada relevan):

$$MRR = \frac{\sum RR}{n_{queries\ with\ results}}$$

### 6.4 Success Rate

Dari semua query:

$$Success\ Rate = \frac{\sum success}{n_{total\ queries}}$$

### 6.5 Coverage

Dari semua query:

$$Coverage = \frac{n_{queries\ with\ results}}{n_{total\ queries}}$$

### 6.6 Mean Response Quality

Dari semua query:

$$Mean\ Response\ Quality = \frac{\sum response\_quality}{n_{total\ queries}}$$

---

## 7. Test Questions (30 Query)

Pertanyaan test diambil dari `old-version/RagChatBot-python/test_question.py`:

1. Carikan rumah dijual di daerah cemara
2. Carikan rumah dijual di daerah ringroad
3. Carikan rumah sewa di medan
4. Carikan rumah dijual di daerah cemara harga 1M an
5. Carikan rumah dijual daerah ringroad harga dibawah 800juta 3 kamar
6. apakah ada rumah sewa di medan yang dibawah 50juta 3 kamar?
7. Saya ingin beli rumah di dekat podomoro medan harga dibawah 1M ada?
8. Client saya lagi cari sewa dekat usu, anaknya mau kuliah disana
9. Carikan rumah di inti kota medan yang harganya dibawah 1M
10. apakah ada ruko yang disewakan di daerah krakatau?
11. saya lagi cari tanah yang dijual di marelan
12. apakah ada gudang yang dijual atau disewa di KIM?
13. Carikan rumah dijual daerah ringroad harga 1M an 3 kamar
14. Apakah masih ada pilihan lain? *(context-dependent)*
15. Berikan lagi pilihan lain *(context-dependent)*
16. kasih pilihan lain, lokasi dan harga masih sama, tapi yang 3 lantai? *(context-dependent)*
17. Berikan lagi pilihan lain *(context-dependent)*
18. Kalau pilihan lain, lokasi dan jumlah lantai masih sama, tapi yang dibawah 800 juta ada? *(context-dependent)*
19. carikan rumah dengan fasilitas cctv di medan
20. carikan rumah dengan fasilitas wifi di medan
21. cari rumah dalam komplek dengan fasilitas lapangan basket
22. cari rumah yang bisa parkir beberapa mobil
23. cari rumah yang sudah ada ac, lemari, dapur dan tangki air
24. cari rumah dekat mall
25. cari rumah dekat sekolah di medan
26. cari rumah dekat mall yang harganya dibawah 800 juta
27. cari rumah full furnished yang harganya dibawah 1 M dalam komplek dengan fasilitas lapangan basket
28. cari apartment di podomoro yang bisa harganya dibawah 1.5 M
29. cari rumah di citraland bagya city medan
30. cari rumah dijual di komplek givency one

**Catatan:** Query 14-18 adalah context-dependent (mengacu pada pencarian sebelumnya). Harus dijalankan secara sequential dalam satu session.

---

## 8. Workflow Evaluasi

### Step 1: Jalankan Test 30 Query

```bash
# Test dengan metode hybrid (default)
python scripts/test_sequential_chat.py --method hybrid

# Test dengan API only
python scripts/test_sequential_chat.py --method api_only

# Test dengan Vector only
python scripts/test_sequential_chat.py --method vector_only
```

Script akan:
- Menjalankan 30 query secara sequential (menjaga konteks untuk Q14-18)
- Menyimpan hasil ke `data/evaluation/test_results_[method]_YYYYMMDD_HHMMSS.json`

### Step 2: Generate HTML Interface

```bash
python scripts/generate_evaluation_html.py
```

Script akan menghasilkan:
- `data/evaluation/evaluation_YYYYMMDD_HHMMSS.html` - Interface untuk rating

### Step 3: Isi Rating Manual di HTML

Buka file HTML di browser, untuk setiap query:

1. **Klik ✓ atau ✗** pada setiap properti (relevan/tidak relevan)
2. **Isi Response Quality** (0-5)
3. **Isi Notes** jika diperlukan

**Tips Rating:**
- Untuk query dengan 0 hasil:
  - Jika memang tidak ada data → notes="no data exists"
  - Jika seharusnya ada → notes="should have results"

### Step 4: Export CSV

Klik tombol "Export to CSV" di HTML untuk download hasil rating.

### Step 5: Hitung Metrics

```bash
python scripts/calculate_evaluation_metrics.py --input data/evaluation/exported.csv
```

### Step 6: Generate Comparison Report (After All Methods Tested)

```bash
# Phase 1: Compare search methods
python scripts/compare_methods.py --phase 1 --output markdown

# Phase 2: Compare LLM models (after Phase 1)
python scripts/compare_methods.py --phase 2 --output markdown
```

---

## 9. Query Categories

Untuk analisis per kategori, setiap query diklasifikasikan:

| Category | Query IDs | Deskripsi |
|----------|-----------|-----------|
| location_simple | 1, 2, 3 | Pencarian lokasi sederhana |
| location_price | 4, 7, 9 | Lokasi + filter harga |
| location_price_spec | 5, 6, 13 | Lokasi + harga + spesifikasi |
| location_intent | 8 | Lokasi dengan konteks intent |
| property_type | 10, 11, 12 | Pencarian tipe properti spesifik |
| context_followup | 14, 15, 17 | Follow-up dari hasil sebelumnya |
| context_modify | 16, 18 | Modifikasi kriteria dari konteks |
| feature_search | 19-23 | Pencarian berdasarkan fasilitas |
| nearby_search | 24, 25 | Pencarian dekat landmark |
| nearby_price | 26 | Dekat landmark + filter harga |
| complex_query | 27, 28 | Query kompleks multi-kriteria |
| project_search | 29, 30 | Pencarian proyek/komplek spesifik |

---

## 10. Referensi

### Information Retrieval & Evaluation Metrics

- Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press. Chapter 8: Evaluation in Information Retrieval.

- Voorhees, E. M. (2002). The philosophy of information retrieval evaluation. *CLEF Workshop on Cross-Language Information Retrieval and Evaluation*. Springer.

### Mean Reciprocal Rank (MRR)

- Voorhees, E. M. (1999). The TREC-8 Question Answering Track Report. *Proceedings of the 8th Text REtrieval Conference (TREC-8)*. NIST Special Publication. pp. 77-82.

- Craswell, N. (2009). Mean Reciprocal Rank. In: *Encyclopedia of Database Systems*. Springer. https://doi.org/10.1007/978-0-387-39940-9_488

### RAG Evaluation

- Chen, D., & Yih, W. (2020). Open-Domain Question Answering. *ACL Tutorial*.

---

## 11. File Structure

```
data/evaluation/
├── hybrid/                                       # Hybrid method results
│   ├── test_results_YYYYMMDD_HHMMSS.json        # Raw test results
│   ├── test_results_latest.json                  # Latest reference
│   ├── evaluation_template_YYYYMMDD.csv          # CSV template for rating
│   ├── evaluation_YYYYMMDD.html                  # HTML interface for rating
│   ├── evaluation_rated_YYYYMMDD.csv             # Exported ratings
│   └── full_responses_YYYYMMDD.txt               # Full responses for review
│
├── api_only/                                     # API Only method results
│   ├── test_results_YYYYMMDD_HHMMSS.json
│   ├── test_results_latest.json
│   ├── evaluation_template_YYYYMMDD.csv
│   ├── evaluation_YYYYMMDD.html
│   └── evaluation_rated_YYYYMMDD.csv
│
├── vector_only/                                  # Vector Only method results
│   ├── test_results_YYYYMMDD_HHMMSS.json
│   ├── test_results_latest.json
│   ├── evaluation_template_YYYYMMDD.csv
│   ├── evaluation_YYYYMMDD.html
│   └── evaluation_rated_YYYYMMDD.csv
│
├── phase1_comparison_YYYYMMDD.md                 # Phase 1 comparison report
├── phase2_comparison_YYYYMMDD.md                 # Phase 2 comparison report
└── evaluation_report_YYYYMMDD.md                 # Final report (Markdown)

scripts/
├── test_sequential_chat.py               # Run 30-query test (--method parameter)
├── generate_evaluation_html.py           # Generate HTML interface
├── calculate_evaluation_metrics.py       # Calculate all metrics
└── compare_methods.py                    # Generate comparison reports
```

---

## 12. Summary of Metrics

| Metric | Formula | Interpretasi | Referensi |
|--------|---------|--------------|-----------|
| **Precision@5** | relevan top 5 / min(n, 5) | Kualitas ranking | Manning (2008) |
| **Overall Precision** | relevan / total | Kualitas keseluruhan | Manning (2008) |
| **MRR** | mean(1/rank_first) | Kecepatan menemukan | Voorhees (1999) |
| **Success Rate** | query sukses / total | Tingkat keberhasilan | Voorhees (2002) |
| **Coverage** | query dengan hasil / total | Kemampuan menjawab | Manning (2008) |
| **Response Quality** | mean(rating 0-5) | Evaluasi subjektif | - |

---

*Dokumen ini dibuat: 23 Januari 2026*
*Update terakhir: 25 Januari 2026 - Marked as V1 methodology*
*Status: Superseded by V2 (constraint-based evaluation)*
*Untuk: Thesis RAG Property Chatbot Evaluation*
