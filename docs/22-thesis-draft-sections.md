# Rencana Penulisan Paper RAG Chatbot

**Tanggal Update:** 26 Januari 2026
**Status:** Section 3.4 - 5 perlu revisi/ditulis ulang
**Target:** Maksimal 12 halaman
**Referensi:** Menggunakan `[REF-XX]` dari `references-master.md`

---

## Daftar Isi Rencana

1. [Status Paper Saat Ini](#status-paper-saat-ini)
2. [Standarisasi Terminologi](#standarisasi-terminologi)
3. [Data Evaluasi Final](#data-evaluasi-final)
4. [Section 3.4 - Experimental Setup](#section-34---experimental-setup)
5. [Section 3.5 - Implementation Details](#section-35---implementation-details)
6. [Section 3.6 - Metrics and Evaluation](#section-36---metrics-and-evaluation)
7. [Section 3.7 - Agent Flow and Safety Rules](#section-37---agent-flow-and-safety-rules)
8. [Section 3.8 - Reproducibility](#section-38---reproducibility)
9. [Section 3.9 - Limitations](#section-39---limitations)
10. [Section 4 - Results and Discussion](#section-4---results-and-discussion)
11. [Section 5 - Conclusion](#section-5---conclusion)

---

## Standarisasi Terminologi

**PENTING: Gunakan istilah yang konsisten di seluruh paper!**

| Istilah Standar | Singkatan | Definisi | JANGAN Gunakan |
|-----------------|-----------|----------|----------------|
| Per-Constraint Accuracy | PCA | Rasio constraint terpenuhi per listing | constraint accuracy, per-listing accuracy |
| Strict Success | - | Listing dengan PCA=1 (semua constraint terpenuhi) | strict match, perfect match |
| Strict Success Ratio | - | Rasio listing dengan Strict Success | strict success rate |
| Constraint Pass Ratio | CPR | Rasio Strict Success per query (= Σ Strict / K) | pass rate, success ratio |
| Mean CPR | - | Rata-rata CPR across all queries | average CPR, CPR mean |
| Query Success Rate | - | Persentase query yang sukses (CPR ≥ T) | query success, success rate |
| True Positive | TP | Query dengan hasil benar (GT+, Pred+) | - |
| False Negative | FN | Query yang seharusnya ada hasil tapi gagal | - |
| True Negative | TN | Query yang benar tidak ada hasil | - |
| False Positive | FP | Query yang salah memberikan hasil | - |

### Contoh Penggunaan yang BENAR:
- "Hybrid achieves 97.61% Mean CPR" ✓
- "The Strict Success Ratio is 96.62%" ✓
- "Query Success Rate reaches 100%" ✓
- "CPR threshold T=0.60" ✓

### Contoh Penggunaan yang SALAH:
- "Hybrid achieves 97.61% CPR mean" ✗
- "The strict success rate is 96.62%" ✗
- "Query success reaches 100%" ✗

---

## Masalah di Section 1-3.3 (PERLU DIPERBAIKI)

### 1. FORMAT REFERENSI TIDAK KONSISTEN ❌
**Masalah:** Paper menggunakan format campuran:
- Section 1-2: `[REF-01]`, `[REF-05]`, `[REF-12]`, dll
- Section 3.6+: `[19]`, `[20]`, `[17]` (format benar)
- References: `[1]`, `[2]`, `[3]`, dll

**Solusi:** Ganti SEMUA `[REF-XX]` menjadi `[X]` di seluruh paper
- `[REF-01]` → `[1]`
- `[REF-05]` → `[5]`
- `[REF-12]` → `[12]`
- dst...

### 2. TABLE NUMBERING DUPLIKAT ❌
**Masalah:**
- Page 4: Table 1, Table 2, Table 3 ✓
- Page 6: "Table 2: Metric definitions" → **SALAH! Duplikat**
- Page 7: "Table 3: Summary of evaluation results" → **SALAH! Duplikat**

**Solusi:**
- Hapus "Table 2" di Section 3.6, ganti dengan bullet list
- "Table 3" di Section 4 → ganti jadi **Table 6**

### 3. FORMAT [REF-XX] PERLU DIKONVERSI ⚠️
**Catatan:** Referensi mengikuti `references-master.md`, BUKAN PDF yang lama.

**Mapping Format:**
- `[REF-01]` → `[1]`
- `[REF-05]` → `[5]`
- `[REF-21]` → Tambahkan ke References jika dipakai, atau ganti dengan referensi [1]-[20]
- dst...

**Referensi [21]-[28] tersedia di references-master.md** untuk digunakan jika diperlukan.

### 4. OUTLINE DI INTRODUCTION SALAH ❌
**Masalah (Page 2):**
> "Section 4 presents the experimental setup and evaluation metrics. Section 5 reports results... Section 6 discusses limitations... Section 7 concludes."

**Struktur Aktual:**
- Section 3: Methodology (termasuk experimental setup & metrics)
- Section 4: Results and Discussion
- Section 5: Conclusion (termasuk limitations)

**Solusi:** Revisi outline jadi:
> "Section 3 describes the system architecture, data preparation, pipeline implementations, experimental setup, and evaluation metrics. Section 4 reports results and discussion. Section 5 concludes the paper with limitations and future work."

### 5. TERMINOLOGI TIDAK KONSISTEN ❌
**Masalah:**
- "strict success" vs "Strict Success" vs "Strict Success Ratio"
- "No Result Score" vs "No-Result Score" vs "No-result score"
- "CPR" tanpa penjelasan di Abstract

**Solusi:** Standarisasi sesuai panduan terminologi di atas

### 6. TYPO ❌
- Page 6: "satified" → "satisfied"
- Page 7: "explicity" → "explicitly"

---

## Status Paper Saat Ini

| Section | Status | Action |
|---------|--------|--------|
| 1. Introduction | ✅ Selesai | - |
| 2. Related Works (2.1-2.7) | ✅ Selesai | - |
| 3.1 System Architecture | ✅ Selesai | - |
| 3.2 Data Preparation | ✅ Selesai | - |
| 3.3 Retrieval Pipelines | ✅ Selesai | - |
| **3.4 Experimental Setup** | ❌ Kosong | **TULIS BARU** |
| **3.5 Implementation Details** | ❌ Kosong | **TULIS BARU** |
| **3.6 Metrics and Evaluation** | ⚠️ Ada | **REVISI** |
| **3.7 LangChain Flow** | ⚠️ Ada | **REVISI** |
| **3.8 Reproducibility** | ⚠️ Ada | **REVISI** |
| **3.9 Limitations** | ⚠️ Ada | **REVISI** |
| **4.1 Results** | ⚠️ Data Lama | **UPDATE DATA** |
| **4.2 Discussion** | ⚠️ Data Lama | **UPDATE NARASI** |
| **5. Conclusion** | ⚠️ Ada | **REVISI** |

---

## Data Evaluasi Final

### Sumber Data
```
data/evaluation/v2/hybrid_openai_20260126_132734/final/metrics.json
data/evaluation/v2/api_only_openai_20260126_135949/final/metrics.json
data/evaluation/v2/vector_only_openai_20260126_143851/final/metrics.json
```

### Tabel 1: Question-Level Metrics (Confusion Matrix)

| Metric | Vector | API | Hybrid |
|--------|--------|-----|--------|
| **Accuracy** | 56.67% | 73.33% | **100%** |
| **Precision** | 100% | 100% | **100%** |
| **Recall** | 53.57% | 71.43% | **100%** |
| **F1 Score** | 69.77% | 83.33% | **100%** |
| TP | 15 | 20 | **28** |
| FP | 0 | 0 | 0 |
| TN | 2 | 2 | 2 |
| FN | 13 | 8 | **0** |

### Tabel 2: Constraint-Level Metrics

| Metric | Vector | API | Hybrid |
|--------|--------|-----|--------|
| **Mean CPR** | 55.33% | 73.35% | **97.61%** |
| **Strict Success Ratio** | 33.04% | 72.62% | **96.62%** |
| **Query Success Rate** | 50% | 73.33% | **100%** |

### Tabel 3: Per-Constraint Accuracy (PCA)

| Constraint | Vector | API | Hybrid |
|------------|--------|-----|--------|
| property_type | 52.17% | 100% | **100%** |
| listing_type | 83.05% | 100% | **100%** |
| location | 94.20% | 98.26% | **98.82%** |
| price | 43.75% | 100% | **100%** |
| bedrooms | 52.94% | 100% | **100%** |
| floors | 66.67% | 100% | 75% |

### Tabel 4: Category Success Rate

| Category | Queries | Vector | API | Hybrid |
|----------|---------|--------|-----|--------|
| location_simple | 3 | 100% | 100% | **100%** |
| location_price | 3 | 66.67% | 100% | **100%** |
| location_price_spec | 3 | 100% | 100% | **100%** |
| location_intent | 1 | 0% | 100% | **100%** |
| property_type | 3 | 33.33% | 100% | **100%** |
| context_followup | 3 | 66.67% | 100% | **100%** |
| context_modify | 2 | 0% | 100% | **100%** |
| complex_query | 2 | 50% | 100% | **100%** |
| project_search | 2 | 100% | 100% | **100%** |
| **feature_search** | 5 | 0% | 0% | **100%** |
| **nearby_search** | 2 | 0% | 0% | **100%** |
| nearby_price | 1 | 100% | 0% | **100%** |

**Temuan Kunci:** Hybrid berhasil 100% pada feature_search dan nearby_search dimana Vector dan API gagal total (0%).

---

## Section 3.4 - Experimental Setup

### Status: ❌ PERLU DITULIS BARU

### Draft Konten:

---

**3.4 Experimental Setup**

All three retrieval pipelines were evaluated on the same 30 gold-labeled questions under identical conditions to ensure fair comparison. The evaluation followed a sequential conversation protocol where questions were processed in order, maintaining conversation context for follow-up queries.

**Evaluation Protocol.** Each pipeline processed the complete question set independently using the same maximum result limit (max_items=10) and identical LLM parameters. The evaluation script executed queries sequentially, recorded all agent responses, extracted property listings from the output, and computed constraint-based metrics against the gold standard annotations.

**Conversation Context.** For context-dependent questions in the context_followup and context_modify categories, the system maintained conversation history from previous turns within the same evaluation session. This design reflects real-world usage patterns where users iteratively refine their search criteria based on initial results. Each evaluation session used a unique thread_id to isolate conversation state.

**Ground Truth Verification.** For each property returned by the agent, we verified constraint satisfaction against the live MySQL database via the Property Website API. This approach ensures that evaluation reflects actual data accuracy rather than potentially stale information from the vector index. The API serves as the authoritative source of truth for transactional fields including price, availability status, and property specifications.

---

### Catatan untuk Copy ke Word:
- Panjang: ~200 kata
- Tidak ada tabel/gambar
- Referensi: Tidak perlu

---

## Section 3.5 - Implementation Details

### Status: ❌ PERLU DITULIS BARU

### Draft Konten:

---

**3.5 Implementation Details**

**3.5.1 Hardware**

The system was deployed on a cloud Virtual Private Server (VPS) with 4 vCPU cores, 8GB RAM, and 100GB SSD storage. Both the MySQL database (via Property Website API) and ChromaDB vector store were hosted on the same infrastructure to minimize network latency during hybrid retrieval operations.

**3.5.2 Software Stack**

The implementation uses Python 3.11 as the primary runtime environment. Table 4 lists the key software dependencies and their versions.

**Table 4: Software Dependencies**

| Component | Version | Purpose |
|-----------|---------|---------|
| LangChain | 0.3.x | Agent orchestration [16] |
| LangGraph | 0.2.x | ReAct agent state management |
| ChromaDB | 0.5.x | Vector storage [15] |
| OpenAI API | - | LLM (GPT-4o-mini) & embeddings |
| FastAPI | 0.110.x | HTTP/JSON endpoint |
| SQLAlchemy | 2.0.x | Database ORM |

**3.5.3 Hyperparameters**

Table 5 summarizes the key hyperparameters used across all experiments.

**Table 5: System Hyperparameters**

| Parameter | Value | Description |
|-----------|-------|-------------|
| LLM Model | GPT-4o-mini | Inference model |
| Temperature | 0 | Deterministic output |
| Embedding Model | text-embedding-3-small | 1536 dimensions |
| Vector Search k | limit × 2 | Pre-fetch for re-ranking |
| Similarity Threshold | 0.35 | Minimum cosine similarity |
| Max Results | 10 | Properties per query |
| CPR Threshold (T) | 0.60 | Query success threshold |
| Semantic Weight (α) | 0.6 | Hybrid score fusion |
| API Position Weight (β) | 0.4 | Hybrid score fusion |
| Price Tolerance | 10% | For "X-an" pattern queries |

The LLM temperature of 0 ensures reproducible results across evaluation runs. The CPR threshold T=0.60 means that with K=10 results, at least 6 of 10 listings must satisfy all applicable constraints for a query to be considered successful. The hybrid score fusion formula combines semantic relevance with API ordering: score = α × semantic_score + β × api_position_score.

---

### Catatan untuk Copy ke Word:
- Panjang: ~250 kata + 2 tabel
- Referensi: [15], [16]
- **Table 4** = lanjutan dari Table 3 di paper
- **Table 5** = lanjutan dari Table 4

---

## Section 3.6 - Metrics and Evaluation

### Status: ⚠️ PERLU REVISI (sudah ada di paper, perlu disesuaikan)

### Revisi yang Diperlukan:
1. Tambahkan penjelasan price tolerance untuk pattern "X-an"
2. Sesuaikan formula dengan implementasi aktual
3. Perbaiki Table numbering (Table 6 di paper lama → seharusnya tidak perlu table baru, sudah ada)

### Catatan Penting:
- Di paper.pdf halaman 6 sudah ada "Table 2: Metric definitions" - INI SALAH NUMBERING
- Seharusnya tidak ada Table baru di Section 3.6 (definisi metric bisa dalam bentuk paragraf/list)
- Atau jika tetap mau pakai table, harus rename jadi **Table 6**

### Draft Konten (Revisi):

---

**3.6 Metrics and Evaluation**

This study evaluates each chatbot reply against a gold standard prepared per question. A reply falls into one of two paths: (1) a listing reply where the bot returns one or more property items, or (2) a no-result reply where the bot explicitly states no matching properties exist. We treat the live MySQL API as the arbiter of truth for availability, prices, and attributes. All metrics are computed per question and then aggregated.

**Key Metrics:**
- **PCA (Per-Constraint Accuracy)**: Ratio of satisfied constraints for one listing
- **Strict Success**: A listing where all constraints are satisfied (PCA=1)
- **Strict Success Ratio**: Ratio of Strict Success listings across all results
- **CPR (Constraint Pass Ratio)**: Fraction of Strict Success listings per query response
- **Mean CPR**: Average CPR across all queries
- **Query Success Rate**: Percentage of queries achieving CPR ≥ T
- **Confusion Matrix Metrics**: Question-level Precision, Recall, F1, Accuracy

**3.6.1 Constraint Checks per Item**

Each question has a set of gold constraints (e.g., location keywords, max_price, bedrooms ≥ k, listing_type). For every returned listing i, we extract attributes from the response and verify against the API. Let C be the subset of gold constraints applicable to the question. For listing i, define a per-constraint indicator [19], [20]:

$$\mathbf{1}_{i,c} = \begin{cases} 1 & \text{if listing } i \text{ satisfies constraint } c \\ 0 & \text{otherwise} \end{cases}$$

**Per-Constraint Accuracy (PCA) for listing i:**

$$PCA_i = \frac{1}{|C|} \sum_{c \in C} \mathbf{1}_{i,c}$$

**Strict Success (binary) for listing i:**

$$Strict_i = \begin{cases} 1 & \text{if } PCA_i = 1 \\ 0 & \text{otherwise} \end{cases}$$

**Price Constraint with Tolerance.** For queries using colloquial price expressions like "harga 1M an" (around 1 billion), we apply a 10% tolerance band. If the target price is P, the constraint passes when:

$$P \times 0.9 \leq price \leq P \times 1.1$$

**3.6.2 Answer-Level Correctness (CPR)**

If a reply returns K listings (i = 1..K), we summarize correctness with Constraint Pass Ratio:

$$CPR = \frac{1}{K} \sum_{i=1}^{K} Strict_i$$

We declare the prediction for the question as Positive (correct answer) when CPR ≥ T, where T is a tunable threshold (default T = 0.60). With K = 10, this means at least 6 of 10 listings must be strictly correct.

**3.6.3 Handling No-Result Replies**

If the bot claims "no result", we verify by querying the API with the gold constraints:
- If the API also returns empty → correct abstention (TN)
- If the API returns items → missed opportunity (FN)

**No Result Score:**

$$\text{No Result Score} = \begin{cases} 1 & \text{if bot says no result AND API returns empty} \\ 0 & \text{otherwise} \end{cases}$$

**3.6.4 Confusion Matrix over Questions**

To summarize question-level outcomes, we compare system prediction against API ground truth:
- **Ground Truth (GT)**: Positive if API has items for gold constraints, Negative if API is empty
- **Prediction (Pred)**: Positive if bot returned listings with CPR ≥ T, Negative if bot returned "no result"

This yields four cases:
- **TP**: GT+, Pred+ (API has items, bot meets threshold)
- **FN**: GT+, Pred− (API has items, bot abstains or fails threshold)
- **TN**: GT−, Pred− (API empty, bot correctly says "no result")
- **FP**: GT−, Pred+ (API empty, bot incorrectly returns listings)

Derived metrics:

$$\text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}$$

$$\text{F1} = \frac{2 \times Precision \times Recall}{Precision + Recall}, \quad \text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

---

### Catatan untuk Copy ke Word:
- Panjang: ~400 kata + formula
- Referensi: [19], [20]
- **HAPUS Table 2 yang duplikat di paper lama**, ganti dengan bullet list

---

## Section 3.7 - Agent Flow and Safety Rules

### Status: ⚠️ PERLU REVISI (sudah ada di paper, perlu update)

### Catatan: Judul section diganti dari "LangChain Flow" → "Agent Flow" karena kita pakai LangGraph

### Draft Konten (Revisi):

---

**3.7 Agent Flow and Safety Rules**

The system implements a ReAct (Reasoning and Acting) agent using LangGraph, which orchestrates tool selection through a reason-act-observe loop [16]. Given a user query, the LLM first reasons about required information, selects appropriate tools from the six available functions (Table 1), observes results, and iterates until formulating a final response. LangGraph manages the agent state and conversation flow through a directed graph structure, enabling complex multi-step interactions.

**Tool Selection Strategy.** The agent follows a routing strategy based on query characteristics:
1. Queries with explicit numeric constraints (price, bedrooms) prioritize the API search tool
2. Queries with vague locations or descriptive terms trigger vector search fallback
3. Complex queries may invoke multiple tools sequentially

**Safety Rules.** Three key safety principles govern system behavior:

1. **Source of Truth**: Price, availability, and property specifications must come from the live API. Vector snippets provide contextual information but cannot override API facts.

2. **Correct Abstention**: If constraints conflict or required data is missing, the system prefers to abstain rather than return incorrect results. This follows selective classification principles where systems should decline when confidence is low [17].

3. **User Isolation**: Each conversation session maintains isolated state through unique thread identifiers, preventing cross-user data leakage.

---

### Catatan untuk Copy ke Word:
- Panjang: ~200 kata
- Referensi: [16], [17]
- Ganti judul section jadi "Agent Flow and Safety Rules"

---

## Section 3.8 - Reproducibility

### Status: ⚠️ PERLU REVISI

### Draft Konten (Revisi):

---

**3.8 Reproducibility**

All configuration parameters are stored in version-controlled files including API endpoints, authentication keys, timeout values, ChromaDB collection names, embedding model specifications, and LLM parameters. Each evaluation run records:
- Runner version and timestamp
- Prompt template hash
- Vector index snapshot identifier
- Per-request logs with tool calls, latencies, and token counts

The evaluator produces structured output including per-query CSV records and aggregated metrics with confusion matrix analysis. We use LLM temperature 0 to ensure deterministic outputs across runs. The complete implementation, evaluation scripts, and gold-labeled questions are available in a public repository.

---

### Catatan untuk Copy ke Word:
- Panjang: ~100 kata
- Referensi: Tidak perlu

---

## Section 3.9 - Limitations

### Status: ⚠️ PERLU REVISI (sesuaikan dengan kondisi terbaru)

### Draft Konten (Revisi):

---

**3.9 Limitations**

This study acknowledges several methodological constraints:

1. **Gold Set Size**: The evaluation uses 30 questions spanning 12 categories. While carefully constructed to cover diverse query types, this limits statistical power for fine-grained subgroup analysis.

2. **Single Market**: Evaluation data comes from the Medan, Indonesia real estate market. Results may vary in other regions with different naming conventions, price ranges, or property characteristics.

3. **Index Freshness**: The vector index is refreshed periodically but may lag behind the live database. While final verification uses API data, temporary recall reduction can occur under high inventory churn.

4. **No User Study**: Evaluation focuses on objective constraint satisfaction metrics. Perceived usefulness, trust, and user satisfaction require separate usability studies with human participants.

---

### Catatan untuk Copy ke Word:
- Panjang: ~130 kata
- Referensi: Tidak perlu

---

## Section 4 - Results and Discussion

### Status: ⚠️ PERLU UPDATE DENGAN DATA BARU

### Catatan Table/Figure Numbering:
- Di paper lama ada "Table 3" di Section 4 → GANTI jadi **Table 6**
- Tambah table PCA → **Table 7**
- Figure 4a, 4b, 4c, 4d sudah ada → TETAP pakai numbering ini

### 4.1 Results

### Draft Konten (Update):

---

**4 Results and Discussion**

**4.1 Results**

Table 6 summarizes the evaluation results across three retrieval pipelines: Vector-only, API-only, and Hybrid.

**Table 6: Summary of Evaluation Results**

| Metric | Vector | API | Hybrid | Δ Hybrid vs API |
|--------|--------|-----|--------|-----------------|
| Mean CPR | 55.33% | 73.35% | **97.61%** | +24.26% |
| Strict Success Ratio | 33.04% | 72.62% | **96.62%** | +24.00% |
| Query Success Rate | 50.00% | 73.33% | **100%** | +26.67% |
| Precision | 100% | 100% | **100%** | 0% |
| Recall | 53.57% | 71.43% | **100%** | +28.57% |
| F1 Score | 69.77% | 83.33% | **100%** | +16.67% |
| Accuracy | 56.67% | 73.33% | **100%** | +26.67% |

Results reveal a clear performance hierarchy: **Hybrid >> API >> Vector**. Figure 4a visualizes this comparison across four key metrics: Mean CPR, Strict Success Ratio, No-Result Score, and Accuracy. The green bars (Hybrid) consistently reach or approach 1.0 across all metrics, while Vector (blue) shows the lowest performance, particularly on Mean CPR (0.55) and Accuracy (0.57).

**Per-Pipeline Analysis**

**Vector-only** achieves 56.67% accuracy with 13 false negatives (Figure 4b). The pipeline excels at location matching (PCA=94.20%) but fails on transactional constraints—price accuracy is only 43.75% and property_type only 52.17%. This confirms that semantic search alone cannot reliably enforce structured constraints.

**API-only** improves significantly over Vector with 73.33% accuracy and F1=83.33% (Figure 4c). The pipeline achieves perfect constraint accuracy on structured fields (property_type, listing_type, price, bedrooms at 100%). However, API-only fails entirely on feature_search (0% success) and nearby_search (0% success) categories, producing 8 false negatives.

**Hybrid** achieves perfect question-level performance with 100% accuracy, 100% recall, and F1=1.0 (Figure 4d). The pipeline successfully answers all 28 positive queries (TP=28, FN=0) and correctly rejects both negative queries (TN=2, FP=0). Critically, Hybrid succeeds on feature_search (100% Query Success Rate, 90% Mean CPR) and nearby_search (100% Query Success Rate, 95% Mean CPR) where both baselines fail completely.

**Per-Constraint Analysis**

Table 7 presents the Per-Constraint Accuracy (PCA) breakdown for each pipeline.

**Table 7: Per-Constraint Accuracy by Pipeline**

| Constraint | Vector | API | Hybrid |
|------------|--------|-----|--------|
| property_type | 52.17% | 100% | **100%** |
| listing_type | 83.05% | 100% | **100%** |
| location | 94.20% | 98.26% | **98.82%** |
| price | 43.75% | 100% | **100%** |
| bedrooms | 52.94% | 100% | **100%** |
| floors | 66.67% | **100%** | 75% |

The per-constraint breakdown reveals complementary strengths. Vector excels at location understanding (94.20%) through semantic matching of area names and landmarks. API guarantees transactional correctness for numeric fields. Hybrid inherits both advantages, with a minor trade-off on floors (75% vs API's 100%) due to occasional semantic interference.

**Confusion Matrix Analysis**

Figure 4 presents the evaluation visualizations: Figure 4a shows the summary metrics comparison as a bar chart, while Figures 4b-4d display the confusion matrices for Vector, API, and Hybrid respectively.

| Pipeline | TP | FP | TN | FN | Precision | Recall |
|----------|----|----|----|----|-----------|--------|
| Vector (4b) | 15 | 0 | 2 | 13 | 100% | 53.57% |
| API (4c) | 20 | 0 | 2 | 8 | 100% | 71.43% |
| Hybrid (4d) | 28 | 0 | 2 | 0 | 100% | 100% |

All three methods achieve 100% precision (no false positives), indicating conservative behavior—when results are returned, they satisfy constraints. The key differentiator is recall: Hybrid achieves perfect recall (100%) while Vector misses 13 and API misses 8 answerable queries. The false negatives in API primarily come from feature_search (5 queries) and nearby_search (3 queries) categories that require semantic understanding beyond structured filters.

---

### 4.2 Discussion

### Draft Konten (Update):

---

**4.2 Discussion**

**Vector Strengths and Weaknesses.** Vector retrieval excels at semantic understanding—matching synonyms, spelling variants, and informal location references. Its high location PCA (94.20%) demonstrates effective area name recognition. However, reliance on embedded snippets without database verification leads to poor transactional accuracy. Price constraints fail at 43.75% because embedded price strings may be outdated or incorrectly parsed.

**API Strengths and Weaknesses.** API retrieval guarantees transactional correctness by querying the live database with structured filters. The perfect PCA scores on property_type, listing_type, price, and bedrooms (all 100%) confirm this reliability. However, API cannot interpret semantic queries about features ("rumah dengan CCTV") or proximity ("dekat mall") because these concepts are not encoded as structured database fields.

**Why Hybrid Succeeds.** The Hybrid approach combines both retrieval paradigms through sequential execution with semantic re-ranking:

1. **API-First for Accuracy**: Structured constraints (price, bedrooms, property_type) are handled by API queries, ensuring transactional correctness.

2. **Semantic Fallback for Coverage**: When API returns empty results (e.g., feature queries), ChromaDB semantic search provides fallback coverage by matching descriptive terms in property listings.

3. **Score Fusion for Ranking**: When API returns results, semantic scores re-rank candidates to prioritize relevance: score = 0.6 × semantic + 0.4 × api_position.

This architecture enables Hybrid to handle feature_search queries (CCTV, WiFi, parking) by matching these terms in property descriptions, while API and Vector alone cannot address such queries.

**Practical Implications.** For practitioners deploying property search assistants:

1. **Hybrid is essential**: Neither API nor Vector alone provides comprehensive coverage. The 100% success rate demonstrates that combined semantic-structured retrieval is necessary for diverse query types.

2. **Feature and proximity queries require semantic components**: The 0% API success on these categories confirms that structured databases alone cannot address natural language queries about amenities and relative locations.

3. **Transactional fields need API grounding**: Vector-only systems should not be trusted for price-sensitive applications, as demonstrated by the 43.75% price accuracy.

---

### Catatan untuk Copy ke Word:
- Section 4.1: ~550 kata + 2 tabel (Table 6, Table 7) + 1 tabel CM summary + Figure 4
- Section 4.2: ~350 kata
- Referensi: Tidak perlu tambahan
- **Struktur 4.1:** Overview → Per-Pipeline Analysis → Per-Constraint Analysis → Confusion Matrix Analysis

### ✅ FIGURE 4 SUDAH DI-GENERATE

File tersimpan di `docs/paper-html/`:
- `figure_4_combined.png` - gabungan 2×2
- `figure_4a_summary_metrics.png` - bar chart metrics
- `figure_4b_cm_vector.png` - confusion matrix Vector
- `figure_4c_cm_api.png` - confusion matrix API
- `figure_4d_cm_hybrid.png` - confusion matrix Hybrid

---

## Section 5 - Conclusion

### Status: ⚠️ PERLU REVISI (sesuaikan dengan hasil terbaru)

### Draft Konten (Revisi):

---

**5 Conclusion and Future Work**

**5.1 Conclusion**

This study presented a channel-agnostic RAG assistant for real estate property search, comparing three retrieval pipelines—Vector-only (semantic search), API-only (structured query), and Hybrid (combined approach)—on 30 gold-labeled questions using constraint-based evaluation.

The key finding is that **Hybrid achieves perfect question-level performance** with 100% accuracy, 100% recall, and F1=1.0, significantly outperforming API-only (73.33% accuracy, F1=83.33%) and Vector-only (56.67% accuracy, F1=69.77%). At the constraint level, Hybrid maintains 97.61% Mean CPR compared to 73.35% for API and 55.33% for Vector.

Critically, Hybrid successfully handles feature-based queries (100% success, 90% CPR) and proximity-based queries (100% success, 95% CPR) where both API and Vector fail entirely (0% success). This demonstrates that combining semantic and structured retrieval provides comprehensive coverage that neither approach achieves alone.

The constraint-based evaluation protocol developed in this study—measuring Per-Constraint Accuracy, Constraint Pass Ratio, and confusion matrix metrics—provides a reproducible framework for assessing property search systems. Unlike traditional IR metrics (MRR, NDCG), this approach explicitly captures constraint satisfaction essential for transactional domains.

**5.2 Future Work**

Several directions merit future investigation:

1. **Dynamic Routing**: Develop a learned policy to automatically select Vector, API, or Hybrid retrieval based on query characteristics, optimizing for both accuracy and latency.

2. **Expanded Evaluation**: Scale the gold set to 100-200 questions with multiple annotators and inter-annotator agreement metrics (Cohen's κ) for robust statistical analysis.

3. **User Study**: Conduct usability evaluation measuring System Usability Scale (SUS), task completion time, and qualitative user feedback.

4. **Multi-turn Dialogue**: Extend the system to handle clarification requests and sophisticated preference refinement across conversation turns.

---

### Catatan untuk Copy ke Word:
- Panjang: ~350 kata
- Referensi: Tidak perlu tambahan

---

## Checklist Pengerjaan

### ✅ DRAFT SUDAH SELESAI - Siap Copy ke Word

| Section | Status | Table/Figure | Referensi |
|---------|--------|--------------|-----------|
| 3.4 Experimental Setup | ✅ Ready | - | - |
| 3.5 Implementation Details | ✅ Ready | Table 4, 5 | [15], [16] |
| 3.6 Metrics and Evaluation | ✅ Ready | - | [19], [20] |
| 3.7 Agent Flow | ✅ Ready | - | [16], [17] |
| 3.8 Reproducibility | ✅ Ready | - | - |
| 3.9 Limitations | ✅ Ready | - | - |
| 4.1 Results | ✅ Ready | Table 6, 7 | - |
| 4.2 Discussion | ✅ Ready | - | - |
| 5 Conclusion | ✅ Ready | - | - |

### Langkah Copy ke Word:
1. Buka paper.docx
2. Copy setiap section dari planning doc ini
3. Format ulang tabel di Word
4. Render formula dengan equation editor
5. Update Figure 4 (Confusion Matrix) dengan data baru
6. Cek ulang referensi format [X]

---

## Mapping Referensi

| Di Paper | REF-ID | Keterangan |
|----------|--------|------------|
| [15] | REF-15 | ChromaDB |
| [16] | REF-16 | LangChain |
| [17] | REF-17 | Geifman Selective Classification |
| [19] | REF-19 | Robertson BM25 |
| [20] | REF-20 | Valizadegan NDCG |

---

## 🔴 PERBAIKAN WAJIB SEBELUM SUBMIT

**Tanggal:** 27 Januari 2026

Berikut perbaikan yang HARUS dilakukan di paper.docx:

---

### PERBAIKAN 1: Outline di Introduction (Halaman 2)

**HAPUS teks ini:**
> "The rest of the paper is organized as follows. Section 2 reviews related work on chatbots, conversational IR, and RAG foundations. Section 3 describes the system architecture, data preparation, and pipeline implementations. Section 4 presents the experimental setup and evaluation metrics. Section 5 reports results with quantitative analysis. Section 6 discusses limitations and directions for future work. Section 7 concludes the paper."

**GANTI dengan:**
> "The rest of the paper is organized as follows. Section 2 reviews related work on chatbots, conversational IR, and RAG foundations. Section 3 describes the system architecture, data preparation, pipeline implementations, experimental setup, and evaluation metrics. Section 4 reports results and discussion. Section 5 concludes the paper with limitations and future work."

---

### PERBAIKAN 2: Referensi [23] dan [24] Duplikat (Halaman 13)

**Masalah:** Referensi [23] dan [24] keduanya merujuk paper yang sama:
- [23] Y. Geifman and R. El-Yaniv, "Selective Classification for Deep Neural Networks"
- [24] Y. Geifman and R. El-Yaniv, "Selective Classification for Deep Neural Networks"

**Solusi:**
1. **HAPUS** referensi [24] dari daftar References
2. Di **Section 3.7** (halaman 8), ganti `[24]` → `[23]`

**Teks yang perlu diubah di Section 3.7:**

CARI:
> "This follows selective classification principles where systems should decline when confidence is low [24]."

GANTI DENGAN:
> "This follows selective classification principles where systems should decline when confidence is low [23]."

---

### PERBAIKAN 3: MetaProperty API → Property Website API (Halaman 3-4)

**Masalah:** Inkonsistensi nama API di Table 2 dan Figure 1.

#### 3a. Table 2: Data Sources (Halaman 4)

**UBAH Table 2 dari:**

| Data Sources | Description |
|--------------|-------------|
| Meta Property API (MYSQL via REST) | Live property listings (~2,800 records), source of truth for price, availability, and attributes |
| ChromaDB (Vector Store) | Property embeddings using text-embedding-3-small (1536 dimensions) for semantic search and re-ranking |

**MENJADI:**

| Data Sources | Description |
|--------------|-------------|
| Property Website API (MySQL via REST) | Live property listings (~2,800 records), source of truth for price, availability, and attributes |
| ChromaDB (Vector Store) | Property embeddings using text-embedding-3-small (1536 dimensions) for semantic search and re-ranking |

#### 3b. Figure 1: High Level Architecture (Halaman 3)

**Perlu di-edit manual di diagram:**
- Ubah label "MetaProperty API" → "Property Website API"

---

### CHECKLIST PERBAIKAN

| # | Item | Lokasi | Status |
|---|------|--------|--------|
| 1 | Outline Introduction | Halaman 2, paragraf terakhir Section 1 | ⬜ Belum |
| 2 | Hapus [24] dari References | Halaman 13 | ⬜ Belum |
| 3 | Ganti [24] → [23] di Section 3.7 | Halaman 8 | ⬜ Belum |
| 4 | Table 2: MetaProperty → Property Website | Halaman 4 | ⬜ Belum |
| 5 | Figure 1: MetaProperty → Property Website | Halaman 3 | ⬜ Belum |

---

### TEKS SIAP COPY

#### Copy untuk Introduction Outline:
```
The rest of the paper is organized as follows. Section 2 reviews related work on chatbots, conversational IR, and RAG foundations. Section 3 describes the system architecture, data preparation, pipeline implementations, experimental setup, and evaluation metrics. Section 4 reports results and discussion. Section 5 concludes the paper with limitations and future work.
```

#### Copy untuk Table 2 Row 1:
```
Property Website API (MySQL via REST) | Live property listings (~2,800 records), source of truth for price, availability, and attributes
```

#### Copy untuk Section 3.7 Safety Rules:
```
This follows selective classification principles where systems should decline when confidence is low [23].
```

---

*Dokumen diperbarui: 27 Januari 2026*
*Perbaikan wajib sebelum submit paper*
