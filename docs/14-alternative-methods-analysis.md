# Alternative RAG/IR Methods Analysis

## Overview

Dokumen ini menganalisis metode-metode alternatif untuk RAG dan Information Retrieval yang bisa digunakan untuk property search seperti MetaProperty.

---

## 1. Metode yang Sudah Diimplementasikan

### 1.1 API-based Search (Structured Query)
- **Deskripsi:** Query langsung ke API dengan parameter terstruktur
- **Kelebihan:** Exact match, cepat, reliable
- **Kekurangan:** Tidak bisa semantic search
- **Status:** ✅ Implemented

### 1.2 Vector Search (ChromaDB)
- **Deskripsi:** Semantic search menggunakan embeddings
- **Kelebihan:** Bisa memahami makna, flexible
- **Kekurangan:** Butuh banyak data training, bisa miss exact matches
- **Status:** ✅ Implemented

### 1.3 Hybrid Search (API + Vector + Reranking)
- **Deskripsi:** Kombinasi API dan Vector dengan reranking
- **Kelebihan:** Best of both worlds
- **Kekurangan:** Lebih kompleks, latency lebih tinggi
- **Status:** ✅ Implemented

---

## 2. Metode Alternatif yang Dipertimbangkan

### 2.1 Text-to-SQL ❌ (Tidak Direkomendasikan)

**Deskripsi:**
LLM generate SQL query dari natural language, lalu execute ke database.

**Contoh:**
```
User: "cari rumah di cemara harga dibawah 1M"

Generated SQL:
SELECT * FROM properties 
WHERE lokasi LIKE '%cemara%' 
AND harga < 1000000000
```

**Kelebihan:**
- Sangat flexible untuk query kompleks
- Direct database access

**Kekurangan:**
- **Security risk tinggi** (SQL injection)
- LLM bisa generate SQL yang salah
- Error handling kompleks
- Butuh schema awareness

**Kesimpulan:** Tidak cocok untuk MetaProperty karena:
1. Sudah ada API yang lengkap
2. Risk > benefit
3. Effort implementasi tinggi

---

### 2.2 Query Expansion / RAG Fusion ⭐⭐ (Bisa Ditambahkan)

**Deskripsi:**
Generate multiple queries dari 1 input user, lalu gabungkan hasil dengan Reciprocal Rank Fusion.

**Contoh:**
```
User: "cari rumah cemara harga 1M"

Generated queries:
1. "rumah dijual cemara"
2. "properti cemara harga 800juta-1.2M"
3. "rumah murah daerah cemara medan"

→ Search each query
→ Combine with RRF
→ Return top results
```

**Kelebihan:**
- Menangani query yang ambiguous
- Meningkatkan recall
- Improvement terukur

**Kekurangan:**
- Menambah latency (multiple searches)
- Butuh LLM call untuk generate queries

**Effort:** Medium
**Value:** Tinggi untuk query ambiguous

**Referensi:**
- RAG Fusion paper
- Pinecone Advanced RAG Techniques

---

### 2.3 HyDE (Hypothetical Document Embeddings) ⭐ (Opsional)

**Deskripsi:**
Generate hypothetical answer/document dulu, lalu cari yang mirip di vector store.

**Contoh:**
```
User: "rumah 3 kamar di cemara"

LLM generates hypothetical listing:
"Rumah 3 kamar tidur di Jl. Cemara No. 123, Medan. 
Luas tanah 200m2, luas bangunan 150m2. 
Harga 800 juta rupiah..."

→ Embed hypothetical document
→ Search similar in ChromaDB
→ Return real matches
```

**Kelebihan:**
- Meningkatkan semantic matching
- Bagus untuk query yang tidak jelas

**Kekurangan:**
- Butuh LLM call tambahan
- Hypothetical document bisa misleading

**Effort:** Medium
**Value:** Medium

---

### 2.4 Self-RAG / Corrective RAG ⭐ (Advanced)

**Deskripsi:**
LLM mengevaluasi sendiri apakah hasil retrieval sudah bagus. Jika tidak, lakukan retrieval ulang dengan query yang berbeda.

**Flow:**
```
1. Initial retrieval
2. LLM evaluates: "Apakah hasil ini relevan?"
3. If score < threshold:
   - Generate new query
   - Retry retrieval
4. Return best results
```

**Kelebihan:**
- Self-correcting
- Adaptif

**Kekurangan:**
- Kompleksitas tinggi
- Multiple LLM calls
- Latency tinggi

**Effort:** High
**Value:** Untuk kasus kompleks

---

### 2.5 Knowledge Graph RAG ⭐ (Future Work)

**Deskripsi:**
Membangun knowledge graph dari data properti, lalu traverse graph untuk retrieval.

**Contoh Graph:**
```
[Properti A] --located_in--> [Cemara]
[Cemara] --near--> [USU]
[Properti A] --has_feature--> [3 Kamar]
```

**Kelebihan:**
- Relationship-aware search
- Bagus untuk "dekat dengan X"

**Kekurangan:**
- Butuh effort besar untuk build graph
- Maintenance kompleks

**Effort:** Very High
**Value:** Untuk fitur lokasi/nearby

---

## 3. Perbandingan Metode

| Metode | Complexity | Accuracy | Latency | Effort | Recommended |
|--------|------------|----------|---------|--------|-------------|
| API-only | Low | High (exact) | Low | Done | ✅ |
| Vector-only | Medium | Medium | Medium | Done | ✅ |
| Hybrid | Medium | High | Medium | Done | ✅ |
| Query Expansion | Medium-High | Higher | High | Medium | ⭐ Consider |
| HyDE | Medium | Medium-High | High | Medium | Optional |
| Text-to-SQL | High | Variable | Low | High | ❌ No |
| Self-RAG | Very High | High | Very High | High | Future |
| Knowledge Graph | Very High | High | Medium | Very High | Future |

---

## 4. Rekomendasi untuk Thesis

### Scope Thesis (3 Metode):
1. **API-only** - Baseline structured search
2. **Vector-only (ChromaDB)** - Semantic search
3. **Hybrid** - Best of both

### Alasan:
- Sudah cukup untuk menunjukkan perbandingan yang bermakna
- Sesuai dengan literatur (Abdallah et al. 2025)
- Effort manageable
- Hasil terukur

### Future Work (Setelah Thesis):
- Query Expansion untuk handling ambiguous queries
- Knowledge Graph untuk fitur nearby/lokasi

---

## 5. Advanced RAG Techniques (Dari Literatur)

### 5.1 Pre-Retrieval Optimization
- Query rewriting
- Query expansion
- Query decomposition

### 5.2 Retrieval Optimization
- Chunk size optimization
- Embedding model selection
- Hybrid retrieval (sparse + dense)

### 5.3 Post-Retrieval Optimization
- Re-ranking (Cohere, Cross-encoder)
- Information compression
- Contextual filtering

### 5.4 Generation Optimization
- Prompt engineering
- Chain-of-thought
- Self-consistency

**Referensi:**
- Pinecone: Advanced RAG Techniques
- LlamaIndex: Building Advanced RAG

---

*Dokumen ini dibuat: 23 Januari 2026*
*Untuk: Thesis RAG Property Chatbot*
