# BAB II TINJAUAN PUSTAKA

Bab ini menyajikan landasan teori yang mendasari penelitian, meliputi konsep Artificial Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Retrieval-Augmented Generation, Vector Database, Conversational Search, Hybrid Retrieval, evaluasi sistem RAG, dan penelitian terdahulu yang relevan.

## 2.1 Artificial Intelligence

### 2.1.1 Definisi dan Konsep Dasar

Artificial Intelligence (AI) atau Kecerdasan Buatan adalah cabang ilmu komputer yang berfokus pada pengembangan sistem yang dapat melakukan tugas-tugas yang biasanya memerlukan kecerdasan manusia [24]. Tugas-tugas tersebut mencakup pemahaman bahasa natural, pengenalan pola, pengambilan keputusan, dan pembelajaran dari pengalaman.

AI dapat diklasifikasikan berdasarkan kapabilitasnya:

1. **Narrow AI (AI Sempit)**: Sistem yang dirancang untuk tugas spesifik, seperti pengenalan wajah, rekomendasi produk, atau asisten virtual. Mayoritas aplikasi AI saat ini termasuk dalam kategori ini.

2. **General AI (AI Umum)**: Sistem hipotetis yang dapat melakukan tugas intelektual apapun yang dapat dilakukan manusia. Belum terealisasi hingga saat ini.

3. **Super AI**: Konsep teoretis tentang AI yang melampaui kecerdasan manusia di semua aspek.

### 2.1.2 Relevansi dengan Industri Properti

Dalam konteks industri properti, AI berperan dalam berbagai aplikasi:

- **Chatbot dan Virtual Assistant**: Membantu calon pembeli menemukan properti yang sesuai kebutuhan melalui interaksi natural
- **Property Valuation**: Estimasi harga properti berbasis data historis dan karakteristik
- **Image Recognition**: Klasifikasi dan tagging otomatis foto properti
- **Recommendation Systems**: Menyarankan properti berdasarkan preferensi pengguna

Penelitian ini menggunakan pendekatan AI untuk mengembangkan chatbot yang dapat memahami query bahasa natural dan menghasilkan respons yang relevan dengan konteks properti.

## 2.2 Machine Learning

### 2.2.1 Paradigma Pembelajaran

Machine Learning (ML) adalah subdomain AI yang memungkinkan komputer belajar dari data tanpa pemrograman eksplisit [22]. Terdapat tiga paradigma utama:

**1. Supervised Learning (Pembelajaran Terawasi)**

Algoritma belajar dari data berlabel untuk memprediksi output pada data baru. Contoh:
- Klasifikasi: Mengkategorikan email sebagai spam atau bukan
- Regresi: Memprediksi harga properti berdasarkan fitur

**2. Unsupervised Learning (Pembelajaran Tak Terawasi)**

Algoritma menemukan pola tersembunyi dalam data tanpa label. Contoh:
- Clustering: Mengelompokkan properti berdasarkan karakteristik serupa
- Dimensionality Reduction: Mereduksi fitur untuk visualisasi

**3. Reinforcement Learning (Pembelajaran Penguatan)**

Agent belajar melalui interaksi dengan environment dan feedback berupa reward/punishment. Digunakan dalam:
- Game playing
- Robotika
- Optimasi dialog agent

### 2.2.2 Deep Learning

Deep Learning adalah subset ML yang menggunakan neural network dengan banyak layer (deep neural networks). Arsitektur deep learning telah merevolusi kemampuan pemrosesan:

- **Computer Vision**: Convolutional Neural Networks (CNN)
- **Sequence Processing**: Recurrent Neural Networks (RNN), LSTM
- **Language Understanding**: Transformer architecture

Transformer architecture menjadi fondasi bagi perkembangan Large Language Models yang digunakan dalam penelitian ini.

## 2.3 Natural Language Processing

### 2.3.1 Definisi dan Ruang Lingkup

Natural Language Processing (NLP) adalah bidang yang menggabungkan linguistik, ilmu komputer, dan AI untuk memungkinkan komputer memahami, menginterpretasi, dan menghasilkan bahasa manusia [23].

### 2.3.2 Tahapan Pemrosesan NLP

**1. Tokenization**

Proses memecah teks menjadi unit-unit kecil (token). Contoh:
- Word tokenization: "Rumah dijual di Medan" → ["Rumah", "dijual", "di", "Medan"]
- Subword tokenization: Memecah kata langka menjadi subword units

**2. Part-of-Speech (POS) Tagging**

Mengidentifikasi kategori gramatikal setiap kata:
- "Rumah" (Noun)
- "dijual" (Verb)
- "di" (Preposition)
- "Medan" (Proper Noun)

**3. Named Entity Recognition (NER)**

Mengidentifikasi dan mengklasifikasi entitas dalam teks:
- Location: "Medan", "Cemara Asri"
- Price: "1 Miliar", "500 juta"
- Property Type: "rumah", "apartemen"

**4. Semantic Analysis**

Memahami makna di balik teks, termasuk:
- Word Sense Disambiguation
- Semantic Role Labeling
- Sentiment Analysis

### 2.3.3 Aplikasi dalam Chatbot

Dalam konteks chatbot properti, NLP digunakan untuk:
- Memahami intent pengguna (mencari, membandingkan, bertanya detail)
- Mengekstrak parameter pencarian (lokasi, harga, spesifikasi)
- Menghasilkan respons yang natural dan informatif
- Menangani variasi bahasa dan typo

## 2.4 Large Language Models

### 2.4.1 Arsitektur Transformer

Transformer adalah arsitektur neural network yang diperkenalkan oleh Vaswani et al. (2017) dalam paper "Attention Is All You Need" [25]. Komponen kunci Transformer meliputi:

**Self-Attention Mechanism**

Memungkinkan model untuk mempertimbangkan konteks dari seluruh input sequence saat memproses setiap token. Berbeda dengan RNN yang memproses sequential, Transformer memproses parallel.

**Multi-Head Attention**

Menggunakan beberapa attention head secara paralel untuk menangkap berbagai aspek hubungan antar token.

**Positional Encoding**

Menambahkan informasi posisi karena Transformer tidak memiliki konsep urutan bawaan.

**Feed-Forward Networks**

Layer fully-connected yang memproses representasi dari attention layer.

### 2.4.2 Evolusi GPT Series

**GPT (Generative Pre-trained Transformer)**

- GPT-1 (2018): Memperkenalkan pre-training + fine-tuning paradigm
- GPT-2 (2019): 1.5B parameters, menunjukkan kemampuan zero-shot
- GPT-3 (2020): 175B parameters, breakthrough dalam few-shot learning [21]
- GPT-4 (2023): Multimodal, significantly improved reasoning
- GPT-4o (2024): Optimized for speed and cost efficiency

### 2.4.3 Few-Shot dan Zero-Shot Learning

**Zero-Shot Learning**: Model dapat melakukan tugas tanpa contoh spesifik, hanya dengan instruksi natural language.

**Few-Shot Learning**: Model diberikan beberapa contoh dalam prompt untuk memandu output.

**In-Context Learning**: Model belajar dari contoh yang diberikan dalam prompt tanpa update parameter.

Kemampuan ini memungkinkan LLM digunakan untuk berbagai tugas NLP tanpa fine-tuning khusus.

### 2.4.4 Hallucination Problem

LLM dapat menghasilkan informasi yang tampak benar tetapi sebenarnya salah atau tidak memiliki basis faktual. Masalah ini disebut hallucination dan merupakan tantangan utama dalam aplikasi LLM untuk domain yang memerlukan akurasi tinggi.

Penyebab hallucination:
- Training data yang tidak akurat atau outdated
- Over-generalization dari pola dalam data
- Lack of grounding pada sumber faktual

Mitigasi hallucination menjadi motivasi utama pengembangan Retrieval-Augmented Generation (RAG).

## 2.5 Retrieval-Augmented Generation (RAG)

### 2.5.1 Konsep Dasar RAG

Retrieval-Augmented Generation (RAG) adalah paradigma yang menggabungkan retrieval (pengambilan informasi) dengan generation (pembangkitan teks) untuk menghasilkan respons yang grounded pada sumber faktual [1].

Komponen utama RAG:

**1. Retriever**
Bertanggung jawab untuk mengambil dokumen atau informasi relevan dari knowledge base berdasarkan query pengguna.

**2. Generator**
Menggunakan dokumen yang di-retrieve sebagai konteks untuk menghasilkan respons yang informatif dan akurat.

### 2.5.2 Arsitektur RAG

```
Query → Retriever → Relevant Documents → Generator (LLM) → Response
                          ↑
                    Knowledge Base
                    (Vector Store / Database)
```

**Retrieval Phase:**
1. Query dikonversi ke representasi (embedding atau keywords)
2. Similarity search dilakukan terhadap knowledge base
3. Top-K dokumen relevan diambil

**Generation Phase:**
1. Query + retrieved documents digabung dalam prompt
2. LLM memproses prompt dan menghasilkan respons
3. Respons ideally grounded pada dokumen yang di-retrieve

### 2.5.3 Keunggulan RAG vs Pure LLM

| Aspek | Pure LLM | RAG |
|-------|----------|-----|
| Knowledge Currency | Terbatas pada training cutoff | Dapat mengakses data terkini |
| Hallucination | Rentan | Berkurang (grounded) |
| Domain Specificity | General | Dapat di-customize |
| Transparency | Black box | Dapat trace sumber |
| Update | Requires retraining | Update knowledge base saja |

### 2.5.4 RAG untuk Domain-Specific Applications

RAG sangat cocok untuk aplikasi domain-specific seperti properti karena:
- Data properti berubah frequently (listing baru, update harga)
- Memerlukan akurasi tinggi (harga, ketersediaan)
- Domain-specific knowledge (terminologi properti, lokasi)
- User queries sering spesifik dan constraint-based

## 2.6 Vector Database dan Semantic Search

### 2.6.1 Embedding Representations

Embedding adalah representasi numerik (vektor) dari objek seperti teks, gambar, atau audio dalam ruang berdimensi tinggi. Untuk teks, embedding menangkap makna semantik sehingga teks dengan makna serupa memiliki vektor yang berdekatan.

**Text Embedding Models:**
- Word2Vec, GloVe: Word-level embeddings
- BERT, RoBERTa: Contextual embeddings
- Sentence-BERT: Sentence-level embeddings
- OpenAI text-embedding-3-small: State-of-the-art general embeddings

### 2.6.2 Similarity Metrics

**Cosine Similarity**

Mengukur sudut antara dua vektor, independen terhadap magnitude:
```
cos(A,B) = (A · B) / (||A|| × ||B||)
```
Nilai berkisar -1 (berlawanan) hingga 1 (identik).

**Euclidean Distance**

Mengukur jarak geometris antara dua titik dalam ruang vektor:
```
d(A,B) = √(Σ(Ai - Bi)²)
```

**Dot Product**

Kombinasi magnitude dan angle, sering digunakan ketika magnitude bermakna:
```
A · B = Σ(Ai × Bi)
```

### 2.6.3 Perbandingan Vector Databases

**Tabel 2.1. Perbandingan Vector Database**

| Aspek | ChromaDB | FAISS | Pinecone |
|-------|----------|-------|----------|
| Type | Embedded | Library | Managed Service |
| Scalability | Medium | High | High |
| Setup Complexity | Low | Medium | Low |
| Persistence | SQLite/Parquet | In-memory/disk | Cloud |
| Metadata Filtering | Yes | Limited | Yes |
| Cost | Free | Free | Pay-per-use |
| Best For | Prototyping, Small-medium scale | Large-scale, On-premise | Production, Managed |

Penelitian ini menggunakan ChromaDB [15] karena kemudahan setup, dukungan metadata filtering, dan kesesuaian untuk skala dataset ~2.800 dokumen. FAISS [13] menyediakan kemampuan pencarian skala besar, sementara Product Quantization [14] memungkinkan efisiensi penyimpanan.

### 2.6.4 Indexing Strategies

**Flat Index**
Brute-force search, akurat tapi lambat untuk dataset besar.

**IVF (Inverted File Index)**
Partisi ruang vektor ke cluster, search hanya di cluster terdekat.

**HNSW (Hierarchical Navigable Small World)**
Graph-based index, balance antara speed dan accuracy.

## 2.7 Conversational Search dan Information Retrieval

### 2.7.1 Keterbatasan Faceted Search

Faceted search (filter dropdown) memiliki keterbatasan fundamental [12]:
- Memerlukan pengguna menerjemahkan intent ke parameter diskrit
- Tidak dapat menangani query fuzzy ("sekitar 1 miliar")
- Tidak memahami konteks ("dekat sekolah anak")
- Workflow rigid, memerlukan banyak klik

### 2.7.2 Conversational IR Principles

Conversational Information Retrieval (CIR) menawarkan paradigma alternatif [8]. TREC CAsT [9] telah menetapkan metodologi untuk penelitian conversational assistance:

**1. Natural Language Interface**
Pengguna mengekspresikan kebutuhan dalam bahasa natural tanpa perlu memahami struktur filter.

**2. Iterative Refinement**
Dialog memungkinkan klarifikasi dan penyempurnaan kriteria secara incremental.

**3. Context Awareness**
Sistem memahami referensi ke percakapan sebelumnya ("yang tadi", "lebih murah lagi").

**4. Mixed-Initiative**
Baik pengguna maupun sistem dapat mengambil inisiatif dalam dialog.

### 2.7.3 Multi-turn Dialogue

Dalam konteks pencarian properti, multi-turn dialogue memungkinkan:

```
User: Carikan rumah di Medan
Bot: Ada 150 rumah di Medan. Apakah ada preferensi harga?
User: Sekitar 1 miliar
Bot: Ditemukan 45 rumah. Berapa kamar tidur yang diinginkan?
User: Minimal 3
Bot: Berikut 12 rumah 3+ kamar di Medan sekitar 1M...
```

Pendekatan ini mengurangi cognitive load pengguna dan menghasilkan hasil yang lebih sesuai kebutuhan.

## 2.8 Hybrid Retrieval Approaches

### 2.8.1 Sparse vs Dense Retrieval

**Sparse Retrieval (Lexical)** [19]
- Berbasis keyword matching (TF-IDF, BM25)
- Representasi sparse (high-dimensional, mostly zeros)
- Kekuatan: Exact match, interpretable
- Kelemahan: Vocabulary mismatch, no semantic understanding

**Dense Retrieval (Semantic)** [3], [4]
- Berbasis embedding similarity
- Representasi dense (low-dimensional, semua non-zero)
- Kekuatan: Semantic matching, synonym handling
- Kelemahan: Costly inference, less interpretable

### 2.8.2 Fusion Strategies

**Early Fusion**
Menggabungkan representasi sparse dan dense sebelum retrieval.

**Late Fusion**
Menjalankan kedua retriever secara terpisah, kemudian menggabungkan hasil:
- Reciprocal Rank Fusion (RRF)
- Score interpolation
- Weighted combination

**Hybrid/Sequential**
Menggunakan satu retriever untuk filter awal, lainnya untuk re-ranking.

Penelitian ini menggunakan pendekatan sequential dengan score fusion:
```
score = 0.6 × semantic_score + 0.4 × api_position_score
```

### 2.8.3 Re-ranking Methods

**Cross-Encoder Re-ranking**
Menggunakan model yang melihat query dan dokumen bersama untuk scoring lebih akurat, tetapi costly.

**Embedding Re-ranking**
Menggunakan embedding similarity untuk re-order hasil dari retriever pertama.

**LLM-based Re-ranking**
Menggunakan LLM untuk menilai relevansi dokumen terhadap query.

## 2.9 Evaluasi Sistem RAG

### 2.9.1 Traditional IR Metrics

**Precision**
Proporsi retrieved documents yang relevan:
```
Precision = Relevant Retrieved / Total Retrieved
```

**Recall**
Proporsi relevant documents yang berhasil di-retrieve:
```
Recall = Relevant Retrieved / Total Relevant
```

**Mean Reciprocal Rank (MRR)**
Rata-rata reciprocal rank dari dokumen relevan pertama:
```
MRR = (1/|Q|) × Σ(1/rank_i)
```

**Normalized Discounted Cumulative Gain (NDCG)** [20]
Mengukur kualitas ranking dengan mempertimbangkan posisi dan graded relevance.

### 2.9.2 Constraint-Based Evaluation

Untuk domain seperti properti di mana hasil harus memenuhi kriteria spesifik, constraint-based evaluation lebih sesuai:

**Per-Constraint Accuracy**
Mengukur seberapa banyak constraint yang dipenuhi oleh setiap hasil.

**Constraint Pass Ratio**
Proporsi hasil yang memenuhi semua constraint.

**Strict Success**
Binary indicator apakah semua constraint terpenuhi.

### 2.9.3 Selective Classification dan Abstention

Selective classification adalah konsep di mana sistem dapat memilih untuk tidak memberikan jawaban (abstain) ketika confidence rendah [17]. Dalam konteks RAG:

**Correct Abstention**
Sistem tidak mengembalikan hasil ketika memang tidak ada properti yang sesuai (True Negative).

**Missed Opportunity**
Sistem abstain padahal ada properti yang sesuai (False Negative).

**False Alarm**
Sistem mengembalikan hasil padahal tidak ada yang sesuai (False Positive).

Kemampuan correct abstention penting untuk menjaga kepercayaan pengguna.

## 2.10 Penelitian Terdahulu

### 2.10.1 Tabel Penelitian Relevan

**Tabel 2.2. Ringkasan Penelitian Terdahulu**

| No | Peneliti (Tahun) | Judul | Metode | Hasil | Ref |
|----|------------------|-------|--------|-------|-----|
| 1 | Febrianto & Putri (2023) | Implementasi Chatbot Sebagai Agen Perumahan Menggunakan Einstein Bot | Rule-based chatbot dengan Einstein Bot | User satisfaction 85%, efisiensi meningkat | [26] |
| 2 | Salem & Mazzara (2020) | ML-based Telegram Bot for Real Estate Price Prediction | Machine learning untuk prediksi harga | Akurasi prediksi 78% | [27] |
| 3 | Ratnawati et al. (2021) | Sistem Informasi Pemasaran Perumahan dengan Fitur Chatbot | Chatbot berbasis Telegram | Mempercepat respons informasi | [28] |
| 4 | Febriansyah & Nirmala (2023) | Perancangan Sistem Jual Beli Properti dengan Chat Bot Telegram | Integrasi Telegram + Web | Aksesibilitas meningkat | [29] |
| 5 | Mali et al. (2023) | Web and Android Application for Real Estate Business Management | Full-stack application | Manajemen properti terintegrasi | [30] |
| 6 | Lewis et al. (2020) | Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks | RAG framework | Peningkatan signifikan vs pure LLM | [1] |
| 7 | Karpukhin et al. (2020) | Dense Passage Retrieval for Open-Domain QA | Dense retrieval (DPR) | Outperform BM25 pada QA tasks | [3] |
| 8 | Izacard & Grave (2021) | Fusion-in-Decoder | Multi-passage evidence aggregation | State-of-the-art pada QA benchmarks | [2] |
| 9 | Khattab & Zaharia (2020) | ColBERT: Efficient and Effective Passage Search | Late-interaction ranking | Balance speed dan accuracy | [4] |
| 10 | Doan et al. (2024) | A Hybrid Retrieval Approach for Advancing RAG Systems | Hybrid retrieve-rerank | Hybrid outperform single strategy | [33] |

### 2.10.2 Gap Analysis

Berdasarkan tinjauan penelitian terdahulu, teridentifikasi beberapa gap:

**1. Single Retrieval Strategy**
Mayoritas penelitian chatbot properti menggunakan satu strategi retrieval (rule-based atau keyword-based) tanpa perbandingan sistematis antar pendekatan.

**2. Kurangnya Evaluasi Objektif**
Evaluasi cenderung fokus pada user satisfaction tanpa metrik objektif untuk mengukur akurasi constraint.

**3. Tidak Ada Constraint-Based Metrics**
Belum ada penelitian yang mengembangkan framework evaluasi berbasis constraint untuk domain properti.

**4. Limited RAG Application**
Penerapan RAG untuk domain properti Indonesia masih sangat terbatas.

### 2.10.3 Posisi Penelitian Ini

Penelitian ini berkontribusi dengan:

1. **Perbandingan Sistematis**: Membandingkan tiga strategi retrieval (Vector-Only, API-Only, Hybrid) pada dataset gold-labeled yang sama.

2. **Constraint-Based Evaluation**: Mengembangkan framework evaluasi yang mengukur kepuasan constraint secara objektif (PCA, CPR, Strict Success).

3. **Hybrid Architecture**: Mendemonstrasikan arsitektur yang menggabungkan structured query dengan semantic search.

4. **Domain Properti Indonesia**: Menerapkan RAG untuk konteks properti Indonesia dengan karakteristik bahasa dan pasar lokal.

5. **Reproducible Methodology**: Menyediakan metrik terukur dan metodologi yang dapat direplikasi.

---

**Ringkasan BAB II:**

Bab ini telah menyajikan tinjauan pustaka yang komprehensif meliputi:

1. **Artificial Intelligence**: Fondasi dan relevansi dengan industri properti
2. **Machine Learning**: Paradigma pembelajaran dan deep learning
3. **Natural Language Processing**: Teknik pemahaman bahasa natural
4. **Large Language Models**: Arsitektur Transformer dan evolusi GPT
5. **RAG**: Paradigma retrieval-augmented generation
6. **Vector Database**: Embedding dan semantic search
7. **Conversational Search**: Paradigma pencarian berbasis dialog
8. **Hybrid Retrieval**: Kombinasi sparse dan dense retrieval
9. **Evaluasi RAG**: Metrik tradisional dan constraint-based
10. **Penelitian Terdahulu**: Gap analysis dan positioning

Tinjauan ini memberikan landasan teoretis untuk pengembangan sistem chatbot RAG dengan tiga strategi retrieval yang dievaluasi menggunakan framework constraint-based.
