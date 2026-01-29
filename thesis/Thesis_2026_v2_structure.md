# STRUKTUR THESIS V2 - RENCANA 70 HALAMAN

## Informasi Umum
- **Judul**: Perancangan dan Implementasi Chatbot AI Berbasis RAG untuk Asisten Virtual Agen Properti
- **Target**: 70 halaman (tidak termasuk lampiran)
- **Fokus Utama**: Perbandingan 3 strategi retrieval (Vector, API, Hybrid)

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
- H1: Strategi Hybrid retrieval menghasilkan akurasi yang lebih tinggi dibandingkan strategi Vector-only dan API-only pada sistem chatbot RAG untuk domain properti
- H2: Sistem chatbot RAG yang dikembangkan mampu memahami query natural language dengan tingkat akurasi di atas 80%
- H3: Terdapat perbedaan signifikan dalam Per-Constraint Accuracy antara ketiga strategi retrieval untuk berbagai jenis constraint

### 1.6 Ruang Lingkup Penelitian (0.5 halaman)
- Fokus pada pasar properti Medan, Indonesia
- Dataset ~2.800 listing properti
- Evaluasi menggunakan 30 gold-labeled questions
- Model LLM: GPT-4o-mini

### 1.7 Sistematika Penulisan (1.5 halaman)
- Ringkasan isi setiap bab

---

## BAB II: TINJAUAN PUSTAKA (~14 halaman)

### 2.1 Artificial Intelligence (1 halaman)
- Definisi dan sejarah singkat
- Relevansi dengan industri properti

### 2.2 Machine Learning (1 halaman)
- Supervised, unsupervised, reinforcement learning
- Aplikasi dalam NLP

### 2.3 Natural Language Processing (1.5 halaman)
- Tokenization, POS tagging, NER
- Semantic analysis
- Aplikasi dalam chatbot

### 2.4 Large Language Models (2 halaman)
- Arsitektur Transformer
- GPT series evolution
- Few-shot learning
- Hallucination problem

### 2.5 Retrieval-Augmented Generation (RAG) (2 halaman)
- Konsep dasar RAG
- Komponen: Retriever + Generator
- Keunggulan vs pure LLM
- RAG untuk domain-specific applications

### 2.6 Vector Database dan Semantic Search (1.5 halaman)
- Embedding representations
- Similarity metrics (cosine, euclidean)
- ChromaDB, FAISS, Pinecone comparison
- Indexing strategies

### 2.7 Conversational Search dan Information Retrieval (1.5 halaman)
- Faceted search limitations
- Conversational IR principles
- Multi-turn dialogue

### 2.8 Hybrid Retrieval Approaches (1.5 halaman)
- Sparse vs Dense retrieval
- Fusion strategies
- Re-ranking methods

### 2.9 Evaluasi Sistem RAG (1.5 halaman)
- Traditional IR metrics (Precision, Recall, MRR, NDCG)
- Constraint-based evaluation
- Selective classification dan abstention

### 2.10 Penelitian Terdahulu (2 halaman)
- Tabel 10+ penelitian relevan
- Gap analysis
- Posisi penelitian ini

---

## BAB III: METODOLOGI PENELITIAN (~16 halaman)

### 3.1 Kerangka Pemikiran (1 halaman)
- Diagram alur penelitian
- Mapping tujuan ke metodologi

### 3.2 Arsitektur Sistem (3 halaman)

#### 3.2.1 High-Level Architecture
- Diagram arsitektur keseluruhan
- Komponen utama: ReAct Agent, Tool Layer, Data Sources

#### 3.2.2 ReAct Agent Design
- Reason-Act-Observe loop
- LangGraph implementation
- State management

#### 3.2.3 Tool Layer
- Tabel 9 tools dengan deskripsi
- Tool selection strategy

#### 3.2.4 Data Sources
- External Property API (REST)
- ChromaDB vector store

### 3.3 Persiapan Data (2 halaman)

#### 3.3.1 Pengumpulan Data
- Sumber data (kantor properti AREBI via API)
- Jumlah dan karakteristik data

#### 3.3.2 Data Cleaning dan Normalisasi
- ETL pipeline
- Standarisasi format

#### 3.3.3 Vector Index Preparation
- Text snippet generation
- Embedding model (text-embedding-3-small)
- ChromaDB indexing

#### 3.3.4 Gold Standard Questions
- 30 pertanyaan dalam 12 kategori
- Tabel kategori dengan contoh
- Annotation protocol

### 3.4 Implementasi Tiga Strategi Retrieval (4 halaman)

#### 3.4.1 Vector-Only Pipeline
- Diagram alur
- Semantic search process
- Post-filtering mechanism
- Strengths dan weaknesses

#### 3.4.2 API-Only Pipeline
- Diagram alur
- Text-to-JSON conversion
- Structured query execution
- Strengths dan weaknesses

#### 3.4.3 Hybrid Pipeline
- Diagram alur
- Sequential strategy dengan fallback
- Score fusion formula: score = 0.6 × semantic + 0.4 × api_position
- Re-ranking process

### 3.5 Framework Evaluasi (3 halaman)

#### 3.5.1 Constraint-Based Metrics
- Per-Constraint Accuracy (PCA) dengan formula
- Strict Success definition
- Constraint Pass Ratio (CPR) dengan formula

#### 3.5.2 Question-Level Evaluation
- Confusion matrix components (TP, FP, TN, FN)
- Precision, Recall, F1, Accuracy formulas
- No-result handling dan correct abstention

#### 3.5.3 Evaluation Protocol
- Sequential conversation protocol
- Ground truth verification via API
- Reproducibility measures

### 3.6 Implementasi Teknis (2 halaman)

#### 3.6.1 Hardware Specifications
- VPS specifications

#### 3.6.2 Software Stack
- Tabel dependencies dengan versi

#### 3.6.3 Hyperparameters
- Tabel semua hyperparameters
- Justifikasi pemilihan nilai

### 3.7 Keterbatasan Metodologi (1 halaman)
- Gold set size
- Single market focus
- Index freshness
- No user study

---

## BAB IV: HASIL DAN PEMBAHASAN (~20 halaman)

### 4.1 Hasil Implementasi Sistem (4 halaman)

#### 4.1.1 API Contract dan Data Source Integration
- Spesifikasi API Contract
- Required endpoints dan parameters
- Response format yang diharapkan
- Keuntungan arsitektur berbasis API (database-agnostic)

#### 4.1.2 Frontend Implementation
- Screenshot UI chatbot
- Chat bubble design
- Responsive design
- Documentation page

#### 4.1.3 Vector Database Implementation
- Text conversion examples
- Embedding statistics
- Index size dan performance

#### 4.1.4 Agent Implementation
- Prompt template
- Tool integration
- Memory management

### 4.2 Hasil Evaluasi Kuantitatif (8 halaman)

#### 4.2.1 Summary Metrics Comparison
- Tabel utama: Vector vs API vs Hybrid
- Mean CPR, Strict Success Ratio, Query Success Ratio
- Precision, Recall, F1, Accuracy
- Bar chart visualization

#### 4.2.2 Per-Constraint Accuracy Analysis
- Tabel breakdown 6 constraints
- Analysis per constraint type
- Visualization

#### 4.2.3 Confusion Matrix Analysis
- Matrix untuk Vector (dengan diagram)
- Matrix untuk API (dengan diagram)
- Matrix untuk Hybrid (dengan diagram)
- Comparative analysis

#### 4.2.4 Per-Category Performance
- Tabel performance per 12 kategori
- Identification of strong/weak areas
- Feature search analysis
- Nearby search analysis

#### 4.2.5 Response Time Analysis
- Average response time per pipeline
- Latency breakdown

### 4.3 Pembahasan (6 halaman)

#### 4.3.1 Analisis Keunggulan Vector-Only
- Semantic understanding capability
- Location matching strength
- Weakness pada transactional constraints

#### 4.3.2 Analisis Keunggulan API-Only
- Exact constraint matching
- Transactional accuracy
- Weakness pada feature/nearby queries

#### 4.3.3 Mengapa Hybrid Unggul
- API-First untuk accuracy
- Semantic fallback untuk coverage
- Score fusion untuk ranking
- Handling feature_search dan nearby_search

#### 4.3.4 Perbandingan dengan Penelitian Terdahulu
- Tabel perbandingan dengan studi lain
- Kontribusi unik penelitian ini

#### 4.3.5 Implikasi Praktis
- Rekomendasi untuk praktisi
- Deployment considerations
- Cost-benefit analysis

### 4.4 Evaluasi User Experience (2 halaman)

#### 4.4.1 Metodologi Survey
- 10 responden tenaga pemasaran
- 10 dimensi evaluasi
- Skala Likert 1-5

#### 4.4.2 Hasil Survey
- Tabel hasil per pertanyaan
- Rata-rata keseluruhan
- Analisis per dimensi

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
- ~25-30 referensi
- Format APA 7th edition

---

## LAMPIRAN (~10+ halaman, tidak dihitung dalam 70 halaman)

### Lampiran 1: Daftar 30 Pertanyaan Gold Standard
- Tabel lengkap dengan kategori dan expected results

### Lampiran 2: Hasil Evaluasi Detail per Pertanyaan
- Tabel lengkap hasil Vector
- Tabel lengkap hasil API
- Tabel lengkap hasil Hybrid

### Lampiran 3: Source Code Utama
- Agent implementation
- Evaluation script
- Score fusion algorithm

### Lampiran 4: Kuesioner User Experience
- Form kuesioner lengkap
- Raw data responses

### Lampiran 5: API Contract Documentation
- Property API endpoint specifications
- Request/response format examples
- Required parameters

---

## DAFTAR RIWAYAT HIDUP
- Biodata penulis
- Riwayat pendidikan
- Riwayat pekerjaan (jika ada)

---

## RINGKASAN ESTIMASI HALAMAN

| Bagian | Halaman |
|--------|---------|
| Bagian Awal | 9 |
| BAB I: Pendahuluan | 6.5 |
| BAB II: Tinjauan Pustaka | 14 |
| BAB III: Metodologi | 16 |
| BAB IV: Hasil dan Pembahasan | 20 |
| BAB V: Simpulan | 4 |
| Daftar Pustaka | 2 |
| **TOTAL** | **71.5** |

---

## DAFTAR TABEL YANG AKAN DIBUAT

1. Tabel 2.1: Perbandingan Vector Database
2. Tabel 2.2: Penelitian Terdahulu
3. Tabel 3.1: Agent Tools
4. Tabel 3.2: API Contract Parameters
5. Tabel 3.3: Gold Standard Question Categories
6. Tabel 3.4: Software Dependencies
7. Tabel 3.5: System Hyperparameters
8. Tabel 3.6: Metric Definitions
9. Tabel 4.1: API Response Format
10. Tabel 4.2: Summary Evaluation Results
11. Tabel 4.3: Per-Constraint Accuracy
12. Tabel 4.4: Per-Category Performance
13. Tabel 4.5: User Experience Survey Results

---

## DAFTAR GAMBAR YANG AKAN DIBUAT

1. Gambar 1.1: Perbandingan Filter Tradisional vs Conversational Search
2. Gambar 2.1: Arsitektur RAG
3. Gambar 2.2: Transformer Architecture
4. Gambar 3.1: Tahapan Penelitian
5. Gambar 3.2: High-Level System Architecture
6. Gambar 3.3: ReAct Agent Flow
7. Gambar 3.4: Data Preparation Workflow
8. Gambar 3.5: Vector-Only Pipeline
9. Gambar 3.6: API-Only Pipeline
10. Gambar 3.7: Hybrid Pipeline
11. Gambar 4.1: API Contract Architecture
12. Gambar 4.2: Frontend Chatbot Design
13. Gambar 4.3: Summary Metrics Bar Chart
14. Gambar 4.4: Confusion Matrix - Vector
15. Gambar 4.5: Confusion Matrix - API
16. Gambar 4.6: Confusion Matrix - Hybrid
17. Gambar 4.7: Per-Constraint Accuracy Chart

---

## CATATAN PENTING

1. **Konsistensi Data**: Semua angka harus konsisten antara paper_full.md dan thesis
2. **Bahasa**: Indonesia formal akademis
3. **Referensi**: Minimal 25 sumber, prioritas jurnal Q1-Q2
4. **Novelty**: Fokus pada perbandingan 3 strategi dan constraint-based evaluation
5. **Reproducibility**: Sertakan semua hyperparameters dan metodologi detail
