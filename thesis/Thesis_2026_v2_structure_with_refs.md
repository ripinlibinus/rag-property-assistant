# STRUKTUR THESIS V2 - DENGAN REFERENSI CODE PATH

> **CATATAN**: File ini berisi path referensi ke source code di project RAG-Tesis untuk memudahkan pencarian ulang jika session terputus.

## Informasi Umum
- **Judul**: Perancangan dan Implementasi Chatbot AI Berbasis RAG untuk Asisten Virtual Agen Properti
- **Target**: 70 halaman (tidak termasuk lampiran)
- **Fokus Utama**: Perbandingan 3 strategi retrieval (Vector, API, Hybrid)

---

## PROJECT STRUCTURE OVERVIEW

```
d:\Project\Rag-Tesis\
├── src/                    # Main source code
│   ├── agents/             # ReAct Agent implementation
│   ├── adapters/           # API adapters (metaproperty.py)
│   ├── knowledge/          # Hybrid search, vector search
│   └── memory/             # Chat history management
├── frontend/               # Vue.js frontend
│   └── src/components/     # UI components
├── scripts/                # Evaluation & utility scripts
├── data/                   # Gold questions, results
├── docs/                   # Documentation
└── thesis/                 # Thesis documents
```

---

## BAGIAN AWAL (~9 halaman)

| No | Bagian | Estimasi Halaman |
|----|--------|------------------|
| 1 | Halaman Sampul | 1 |
| 2 | Halaman Judul | 1 |
| 3 | Halaman Pernyataan Keaslian Tesis | 1 |
| 4 | Halaman Pernyataan Hak Cipta | 1 |
| 5 | Halaman Pengesahan | 1 |
| 6 | Prakata | 1 |
| 7 | Abstrak (Indonesia & English) | 2 |
| 8 | Daftar Isi | 1 |
| 9 | Daftar Tabel | 0.5 |
| 10 | Daftar Gambar | 0.5 |

---

## BAB I: PENDAHULUAN (~6.5 halaman)

### 1.1 Latar Belakang (2 halaman)
- Perkembangan industri properti Indonesia
- Data AREBI tentang jumlah broker
- Tantangan pencarian informasi properti
- Gap antara filter tradisional vs natural language
- Potensi AI dan RAG untuk solusi
- Pentingnya perbandingan strategi retrieval

### 1.2 Perumusan Masalah (0.5 halaman)
1. Bagaimana merancang chatbot RAG yang dapat memahami query natural language?
2. Bagaimana membandingkan efektivitas strategi Vector-only, API-only, dan Hybrid?
3. Bagaimana mengukur akurasi sistem dengan metrik constraint-based?
4. Strategi retrieval mana yang paling optimal untuk domain properti?

### 1.3 Tujuan Penelitian (0.5 halaman)
1. Merancang dan mengimplementasikan chatbot RAG dengan arsitektur ReAct Agent
2. Membandingkan 3 strategi retrieval pada dataset yang sama
3. Mengembangkan framework evaluasi constraint-based
4. Mengidentifikasi strategi optimal untuk berbagai jenis query

### 1.4 Manfaat Penelitian (1 halaman)
- Bagi tenaga pemasaran properti
- Bagi perusahaan broker
- Bagi industri properti Indonesia
- Bagi pengembangan ilmu pengetahuan

### 1.5 Hipotesis Penelitian (0.5 halaman)
- H1: Strategi Hybrid retrieval menghasilkan akurasi yang lebih tinggi dibandingkan strategi Vector-only dan API-only
- H2: Sistem chatbot RAG mampu memahami query natural language dengan akurasi > 80%
- H3: Terdapat perbedaan signifikan dalam Per-Constraint Accuracy antar strategi

### 1.6 Ruang Lingkup Penelitian (0.5 halaman)
- Fokus pada pasar properti Medan, Indonesia
- Dataset ~2.800 listing properti
- Evaluasi menggunakan 30 gold-labeled questions
- Model LLM: GPT-4o-mini

### 1.7 Sistematika Penulisan (1.5 halaman)

---

## BAB II: TINJAUAN PUSTAKA (~14 halaman)

### 2.1 Artificial Intelligence (1 halaman)
### 2.2 Machine Learning (1 halaman)
### 2.3 Natural Language Processing (1.5 halaman)
### 2.4 Large Language Models (2 halaman)
### 2.5 Retrieval-Augmented Generation (RAG) (2 halaman)
### 2.6 Vector Database dan Semantic Search (1.5 halaman)
### 2.7 Conversational Search dan Information Retrieval (1.5 halaman)
### 2.8 Hybrid Retrieval Approaches (1.5 halaman)
### 2.9 Evaluasi Sistem RAG (1.5 halaman)
### 2.10 Penelitian Terdahulu (2 halaman)

---

## BAB III: METODOLOGI PENELITIAN (~16 halaman)

### 3.1 Kerangka Pemikiran (1 halaman)
- Diagram alur penelitian
- Mapping tujuan ke metodologi

### 3.2 Arsitektur Sistem (3 halaman)

#### 3.2.1 High-Level Architecture
> **CODE REF**: `frontend/src/components/DocumentationPage.vue:82-104` - Architecture diagram

#### 3.2.2 ReAct Agent Design
> **CODE REF**:
> - `src/agents/react_agent.py` - Main ReAct agent
> - `src/agents/property_agent.py` - Property-specific agent
> - `src/agents/orchestrator.py` - Agent orchestration

#### 3.2.3 Tool Layer (9 Tools)
> **CODE REF**: `frontend/src/components/DocumentationPage.vue:211-244` - Tool list

| Tool | Fungsi |
|------|--------|
| search_properties | Pencarian dengan filter |
| search_nearby | Pencarian radius |
| geocode_location | Konversi alamat ke koordinat |
| search_knowledge | Vector search di ChromaDB |
| rerank_results | Cross-encoder reranking |
| get_property_details | Detail properti by ID |
| get_property_types | Daftar tipe properti |
| get_locations | Daftar lokasi |
| no_properties_found | Handler tidak ada hasil |

#### 3.2.4 Data Sources
> **CODE REF**:
> - `src/adapters/metaproperty.py` - Property API adapter
> - `src/knowledge/hybrid_search.py` - ChromaDB integration

### 3.3 Persiapan Data (2 halaman)

#### 3.3.1 Pengumpulan Data
> **CODE REF**: `scripts/sync_properties.py` - Sync dari API ke ChromaDB

#### 3.3.2 Data Cleaning dan Normalisasi
> **CODE REF**: `scripts/ingest_knowledge.py` - ETL pipeline

#### 3.3.3 Vector Index Preparation
> **CODE REF**:
> - `src/knowledge/hybrid_search.py` - Embedding & indexing
> - `config/settings.py` - Embedding model config

#### 3.3.4 Gold Standard Questions
> **DATA REF**:
> - `data/gold_questions.xlsx` atau `data/gold_questions.json`
> - 30 pertanyaan dalam 12 kategori

### 3.4 Implementasi Tiga Strategi Retrieval (4 halaman)

#### 3.4.1 Vector-Only Pipeline
> **CODE REF**: `src/knowledge/hybrid_search.py` - method: `search_vector_only()`

#### 3.4.2 API-Only Pipeline
> **CODE REF**: `src/adapters/metaproperty.py` - method: `search_properties()`

#### 3.4.3 Hybrid Pipeline
> **CODE REF**:
> - `src/knowledge/hybrid_search.py` - method: `hybrid_search()`
> - Score fusion formula: `score = 0.6 × semantic + 0.4 × api_position`

### 3.5 Framework Evaluasi (3 halaman)

#### 3.5.1 Constraint-Based Metrics
> **CODE REF**: `scripts/evaluate_v2.py` - Evaluation logic

#### 3.5.2 Question-Level Evaluation
> **RESULT REF**: `data/evaluation_results/` - Hasil evaluasi

#### 3.5.3 Evaluation Protocol
> **CODE REF**: `scripts/run_evaluation.py` - Evaluation runner

### 3.6 Implementasi Teknis (2 halaman)

#### 3.6.1 Hardware Specifications
> **CONFIG REF**: `docker-compose.yml` - Container specs

#### 3.6.2 Software Stack
> **CONFIG REF**:
> - `requirements.txt` - Python dependencies
> - `pyproject.toml` - Project config
> - `frontend/package.json` - Frontend dependencies

#### 3.6.3 Hyperparameters
> **CONFIG REF**: `config/settings.py` - All hyperparameters

### 3.7 Keterbatasan Metodologi (1 halaman)

---

## BAB IV: HASIL DAN PEMBAHASAN (~20 halaman)

### 4.1 Hasil Implementasi Sistem (4 halaman)

#### 4.1.1 API Contract dan Data Source Integration
> **CODE REF**: `frontend/src/components/DocumentationPage.vue:443-522` - Property API Guide
>
> **API Contract:**
> ```
> GET /api/properties
> Query Parameters: listing_type, property_type, min_price, max_price,
>                   bedrooms, bathrooms, location, lat, lng, radius
>
> Response Format:
> {
>   "success": true,
>   "data": [{id, title, description, price, listing_type, property_type,
>             bedrooms, bathrooms, land_area, building_area,
>             location: {address, city, district, lat, lng},
>             images: [], url}],
>   "meta": {total, page, per_page}
> }
> ```

#### 4.1.2 Frontend Implementation
> **CODE REF**:
> - `frontend/src/App.vue` - Main app
> - `frontend/src/components/ChatInterface.vue` - Chat UI
> - `frontend/src/components/DocumentationPage.vue` - Documentation

#### 4.1.3 Vector Database Implementation
> **CODE REF**:
> - `src/knowledge/hybrid_search.py` - ChromaDB operations
> - `data/chromadb/` - Persisted vector store

#### 4.1.4 Agent Implementation
> **CODE REF**:
> - `src/agents/react_agent.py` - ReAct agent with prompt template
> - `src/memory/` - Memory management (sqlite_memory.py, summarizer.py)

### 4.2 Hasil Evaluasi Kuantitatif (8 halaman)

#### 4.2.1 Summary Metrics Comparison
> **RESULT REF**: `data/evaluation_results/summary_metrics.json`
> **UI REF**: `frontend/src/components/DocumentationPage.vue:248-380` - Evaluation display

| Method | Query Success | Mean CPR | Strict Success |
|--------|--------------|----------|----------------|
| Hybrid | 100% | 97.61% | 96.62% |
| API Only | 73.33% | 73.35% | 72.62% |
| Vector Only | 50% | 55.33% | 33.04% |

#### 4.2.2 Per-Constraint Accuracy Analysis
> **RESULT REF**: `data/evaluation_results/per_constraint_accuracy.json`

#### 4.2.3 Confusion Matrix Analysis
> **UI REF**: `frontend/src/components/DocumentationPage.vue:335-364` - Confusion matrix

**Hybrid Confusion Matrix:**
- TN: 2, FP: 0
- FN: 0, TP: 28

#### 4.2.4 Per-Category Performance
> **RESULT REF**: `data/evaluation_results/per_category_performance.json`

#### 4.2.5 Response Time Analysis
> **RESULT REF**: `data/evaluation_results/response_times.json`

### 4.3 Pembahasan (6 halaman)

#### 4.3.1 Analisis Keunggulan Vector-Only
#### 4.3.2 Analisis Keunggulan API-Only
#### 4.3.3 Mengapa Hybrid Unggul
> **CODE REF**: `src/knowledge/hybrid_search.py` - Score fusion logic

#### 4.3.4 Perbandingan dengan Penelitian Terdahulu
#### 4.3.5 Implikasi Praktis

### 4.4 Evaluasi User Experience (2 halaman)
> **DATA REF**: `data/ux_survey_results.xlsx`

---

## BAB V: SIMPULAN DAN SARAN (~4 halaman)

### 5.1 Simpulan (2.5 halaman)
1. Keberhasilan implementasi sistem RAG
2. Perbandingan 3 strategi retrieval
3. Hybrid sebagai strategi optimal (100% accuracy)
4. Kontribusi framework evaluasi constraint-based
5. Validasi user satisfaction
6. Keterbatasan sistem

### 5.2 Saran Pengembangan (1.5 halaman)
1. Dynamic routing berdasarkan query characteristics
2. Expanded evaluation (100-200 questions)
3. User study dengan SUS metrics
4. Multi-turn dialogue sophistication
5. Integration dengan WhatsApp/Telegram
6. Multi-market expansion

---

## DAFTAR PUSTAKA (~2 halaman)
> **REF**: `thesis/references.bib` (jika ada)

---

## LAMPIRAN

### Lampiran 1: Daftar 30 Pertanyaan Gold Standard
> **DATA REF**: `data/gold_questions.xlsx`

### Lampiran 2: Hasil Evaluasi Detail per Pertanyaan
> **DATA REF**: `data/evaluation_results/detailed_results.json`

### Lampiran 3: Source Code Utama
> **CODE REF**:
> - Agent: `src/agents/react_agent.py`
> - Evaluation: `scripts/evaluate_v2.py`
> - Hybrid Search: `src/knowledge/hybrid_search.py`

### Lampiran 4: Kuesioner User Experience
> **DATA REF**: `data/ux_survey_form.pdf`

### Lampiran 5: API Contract Documentation
> **CODE REF**: `frontend/src/components/DocumentationPage.vue:443-522`

---

## QUICK REFERENCE - IMPORTANT FILES

### Core Implementation
| Component | Path |
|-----------|------|
| ReAct Agent | `src/agents/react_agent.py` |
| Property Agent | `src/agents/property_agent.py` |
| Hybrid Search | `src/knowledge/hybrid_search.py` |
| MetaProperty Adapter | `src/adapters/metaproperty.py` |
| Settings | `config/settings.py` |

### Frontend
| Component | Path |
|-----------|------|
| Main App | `frontend/src/App.vue` |
| Chat Interface | `frontend/src/components/ChatInterface.vue` |
| Documentation | `frontend/src/components/DocumentationPage.vue` |

### Evaluation
| Component | Path |
|-----------|------|
| Evaluation Script | `scripts/evaluate_v2.py` |
| Run Evaluation | `scripts/run_evaluation.py` |
| Gold Questions | `data/gold_questions.xlsx` |

### Configuration
| Component | Path |
|-----------|------|
| Docker Compose | `docker-compose.yml` |
| Requirements | `requirements.txt` |
| Environment | `.env.example` |

---

## CATATAN PENTING

1. **Konsistensi Data**: Semua angka harus konsisten antara paper_full.md dan thesis
2. **Bahasa**: Indonesia formal akademis
3. **Referensi**: Minimal 25 sumber, prioritas jurnal Q1-Q2
4. **Novelty**: Fokus pada perbandingan 3 strategi dan constraint-based evaluation
5. **Reproducibility**: Sertakan semua hyperparameters dan metodologi detail
