# Paper dengan Referensi yang Sudah Di-Map

**Panduan:** Setiap `[REF-XX]` sudah di-convert ke `[X]` sesuai references-master.md.
Copy teks di bawah ke Word, lalu gunakan Mendeley untuk insert citation.

---

## Mapping Referensi Lengkap

| [X] | REF-ID | Nama Lengkap |
|-----|--------|--------------|
| [1] | REF-01 | Lewis et al. 2020 - RAG Original Paper |
| [2] | REF-02 | Izacard & Grave 2021 - Fusion-in-Decoder |
| [3] | REF-03 | Karpukhin et al. 2020 - DPR |
| [4] | REF-04 | Khattab & Zaharia 2020 - ColBERT |
| [5] | REF-05 | Sao et al. 2025 - AI Chatbot in Real Estate |
| [6] | REF-06 | Jannach et al. 2022 - CRS Survey |
| [7] | REF-07 | Gao et al. 2021 - CRS Advances |
| [8] | REF-08 | Radlinski & Craswell 2017 - Conversational Search |
| [9] | REF-09 | Dalton et al. 2021 - TREC CAsT |
| [10] | REF-10 | Guu et al. 2020 - REALM |
| [11] | REF-11 | Fan et al. 2024 - RAG + LLM Survey |
| [12] | REF-12 | Hearst 2009 - Search User Interfaces |
| [13] | REF-13 | Facebook AI 2017 - FAISS |
| [14] | REF-14 | Jegou et al. 2011 - Product Quantization |
| [15] | REF-15 | Chroma 2023 - ChromaDB |
| [16] | REF-16 | LangChain 2023 |
| [17] | REF-17 | Geifman & El-Yaniv 2017 - Selective Classification |
| [18] | REF-18 | Tapsai et al. 2021 - NL to Database |
| [19] | REF-19 | Robertson & Zaragoza 2009 - BM25 |
| [20] | REF-20 | Valizadegan et al. 2009 - NDCG |
| [21] | REF-21 | Abdallah et al. 2025 - Comparing Retrieval |
| [22] | REF-22 | Rao et al. 2025 - Rethinking Hybrid |
| [23] | REF-23 | Gao et al. 2024 - RAG Survey |
| [24] | REF-24 | Doan et al. 2024 - Hybrid RAG |
| [25] | REF-25 | Yu et al. 2024 - RAG Evaluation Survey |

---

# SECTION 1: Introduction

**Paragraph 1:**
Most real estate systems still require users to pre-select rigid filters such as location, price range, bedrooms, and property type. This workflow performs well for narrow, well-defined queries but struggles when user intents are fuzzy, for example "near a named landmark," "budget around 1 billion," or "minimum 3 bedrooms" **[12]**. Real estate agents often spend multiple rounds tweaking filter inputs, delaying answers and risking user drop-off **[5]**. We address this gap with a conversational assistant that captures natural-language intent while preserving transactional correctness through live, structured data.

**Paragraph 2:**
Large Language Models (LLMs) enable fluent, multi-turn conversations but can drift from enterprise facts or hallucinate nonexistent listings. Retrieval-Augmented Generation (RAG) mitigates this problem by pairing text generation with targeted retrieval from authoritative data sources **[1]**. Dense passage retrieval methods **[3]** and late-interaction models **[4]** have demonstrated strong performance for open-domain question answering, while frameworks such as Fusion-in-Decoder aggregate evidence across multiple retrieved passages **[2]**. Recent surveys consolidate this landscape and highlight trade-offs between recall, latency, and provenance **[11]**. In property search, we make two key design choices: first, decouple the chat interface from inference by exposing a stateless HTTP/JSON API endpoint; second, compare three retrieval pipelines on the same gold-labeled questions using constraint-grounded metrics.

**Paragraph 3:**
Conversational search formalizes properties of interactive information retrieval in a chat setting, motivating dialogue-centric models that iteratively refine user information needs **[8]**. Surveys on conversational recommender systems emphasize multi-turn preference elicitation and dialogue strategies that reduce interaction friction compared to static filter forms **[6]**, **[7]**. Our work applies these principles to real estate by designing a domain-specific RAG assistant delivered as a response API endpoint that any front-end client can consume. Rather than building a dedicated chat UI, we expose a stateless endpoint that returns assistant replies along with optional diagnostics and metadata. A simple web interface accompanies the API for testing and demonstration purposes.

**Paragraph 4:**
The system implements three retrieval strategies: Vector-only using semantic search with ChromaDB **[15]**, API-only using structured MySQL queries following text-to-JSON conversion **[18]**, and Hybrid combining API filtering with semantic re-ranking. The Hybrid approach treats the live database API as the source of truth for transactional fields like price and availability, while using vector embeddings to expand recall for fuzzy location names and informal queries **[1]**, **[3]**. We orchestrate these pipelines using LangChain **[16]** with tool-augmented prompting. We evaluate all three pipelines using a constraint-based protocol with Per-Constraint Accuracy (PCA), Constraint Pass Ratio (CPR), Strict Success Ratio, and question-level Precision, Recall, F1, and Accuracy derived from confusion matrix analysis.

**Paragraph 5 (Paper Outline) - PERLU DIREVISI:**
The rest of the paper is organized as follows. Section 2 reviews related work on chatbots, conversational IR, and RAG foundations. Section 3 describes the system architecture, data preparation, pipeline implementations, experimental setup, and evaluation metrics. Section 4 reports results and discussion. Section 5 concludes the paper with limitations and future work.

---

# SECTION 2: Related Works

## 2.1 Chatbots Conversational Recommendation

Empirical studies report that AI-enabled chatbots can improve perceived service quality in real estate, suggesting practical benefits for high-inquiry tasks such as property search **[5]**. Surveys on conversational recommender systems (CRS) emphasize multi-turn preference elicitation and dialogue strategies that reduce interaction friction compared to static filter forms **[6]**, **[7]**. These findings motivate natural-language interfaces that handle fuzzy, evolving user preferences while maintaining factual correctness.

## 2.2 Conversational IR and RAG Foundations

Foundational work in conversational search formalizes interactive IR properties and motivates dialogue-centric models that iteratively refine information needs **[8]**. The TREC CAsT track established methodology for conversational assistance research **[9]**. Retrieval-Augmented Generation (RAG) addresses LLM hallucination by grounding outputs in retrieved content **[1]**. Related approaches include REALM for retrieval-augmented pretraining **[10]**, DPR for dense passage retrieval **[3]**, Fusion-in-Decoder for evidence aggregation **[2]**, and ColBERT for efficient late-interaction ranking **[4]**. Recent surveys discuss trade-offs between retrieval recall, latency, and provenance **[11]**, **[23]**.

## 2.3 Faceted Search and Its Limitations

Classic HCI literature documents both strengths and friction of faceted filtering **[12]**. While robust for well-specified queries, facets impose overhead when intents are vague. A user searching for "a house near the university for my child" must manually decompose this into location, type, and price filters. Conversational retrieval elicits constraints naturally while structured back-ends enforce correctness **[8]**.

## 2.4 Hybrid Retrieval and Vector Search

Efficient nearest-neighbor search underpins dense retrieval, with FAISS providing billion-scale similarity search **[13]**, **[14]**. Lightweight vector stores like ChromaDB and orchestration frameworks like LangChain ease RAG prototyping **[15]**, **[16]**. Recent work shows that combining sparse lexical methods with dense semantic methods outperforms either alone **[21]**, **[22]**, **[24]**. Small embedding models with LLM re-ranking can match larger models, suggesting retriever-reader alignment matters more than embedding size **[22]**.

## 2.5 Natural Language to Database

Converting natural language to structured queries has been studied extensively **[18]**. Our API-only pipeline generates JSON filter objects rather than raw SQL, reducing injection risks while maintaining interpretability.

## 2.6 RAG Evaluation

Evaluating RAG systems requires assessing both retrieval and generation quality **[25]**. Retrieval metrics include Precision, Recall, MRR, and NDCG **[19]**, **[20]**. For task-oriented systems, constraint satisfaction measures whether results match user requirements. Selective classification principles suggest systems should abstain when confidence is low **[17]**. Our evaluation adopts constraint-based metrics combined with confusion matrix analysis.

## 2.7 Research Gap

Prior real estate chatbots typically use single retrieval modes with limited systematic comparisons. Our work addresses this by: (1) designing a channel-agnostic RAG assistant with stateless API architecture, (2) comparing three retrieval strategies on identical gold-labeled questions, (3) proposing constraint-based evaluation measuring both listing-level and question-level correctness, and (4) demonstrating that Hybrid retrieval achieves superior performance.

---

# SECTION 3: Research Methodology

## 3.1 System Architecture

The system consists of three main layers: a ReAct agent for reasoning and tool selection, a tool layer with six specialized functions for property search, and data sources including a live API and a vector database.

**ReAct Agent.** We implement a ReAct (Reasoning and Acting) agent using LangGraph that follows a reason-act-observe loop **[16]**. Given a user query, the LLM first reasons about what information is needed, selects appropriate tools, observes the results, and iterates until it can formulate a final answer.

(Table 1, Table 2 - tidak perlu referensi)

## 3.2 Data Preparation

(Tidak ada referensi di section ini)

## 3.3 Retrieval Pipelines

(Tidak ada referensi di section ini)

## 3.4 Experimental Setup

(Tidak ada referensi di section ini)

## 3.5 Implementation Details

### 3.5.2 Software Stack
Table 4 lists the key software dependencies:
- LangChain 0.3.x - Agent orchestration **[16]**
- ChromaDB 0.5.x - Vector storage **[15]**

## 3.6 Metrics and Evaluation

### 3.6.1 Constraint checks per item
For listing i, define a per-constraint indicator **[19]**, **[20]**:
(formula)

### 3.6.3 Handling no result replies
We score the reply as correct abstention or missed opportunity **[17]**.

## 3.7 Agent Flow and Safety Rules

The system implements a ReAct (Reasoning and Acting) agent using LangGraph, which orchestrates tool selection through a reason-act-observe loop **[16]**.

**Safety Rules - Correct Abstention:** This follows selective classification principles where systems should decline when confidence is low **[17]**.

## 3.8 Reproducibility

(Tidak ada referensi di section ini)

## 3.9 Limitations

(Tidak ada referensi di section ini)

---

# SECTION 4: Results and Discussion

(Tidak ada referensi di section ini - murni hasil evaluasi)

---

# SECTION 5: Conclusion & Future Works

(Tidak ada referensi di section ini)

---

# REFERENCES (Untuk di-copy ke Word)

**Format:** Gunakan Mendeley untuk generate references. Berikut urutan yang dipakai di paper:

[1] Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.

[2] Izacard, G., & Grave, E. (2021). Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering. EACL 2021.

[3] Karpukhin, V., et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP 2020.

[4] Khattab, O., & Zaharia, M. (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. SIGIR 2020.

[5] Sao, A., et al. (2025). Analyzing the Impact of AI-Enabled Chatbot on Service Quality in the Real Estate Sector. Procedia Computer Science.

[6] Jannach, D., et al. (2022). A Survey on Conversational Recommender Systems. ACM Computing Surveys.

[7] Gao, C., et al. (2021). Advances and Challenges in Conversational Recommender Systems: A Survey. AI Open.

[8] Radlinski, F., & Craswell, N. (2017). A Theoretical Framework for Conversational Search. CHIIR 2017.

[9] Dalton, J., et al. (2021). CAsT 2020: The Conversational Assistance Track Overview. TREC.

[10] Guu, K., et al. (2020). REALM: Retrieval-Augmented Language Model Pre-Training. ICML 2020.

[11] Fan, W., et al. (2024). A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models. KDD 2024.

[12] Hearst, M.A. (2009). Search User Interfaces. Cambridge University Press.

[13] Facebook AI Research. (2017). FAISS: A Library for Efficient Similarity Search.

[14] Jegou, H., et al. (2011). Product Quantization for Nearest Neighbor Search. IEEE TPAMI.

[15] Chroma. (2023). Chroma: The AI-native Open-source Embedding Database.

[16] LangChain. (2023). LangChain: Building Applications with LLMs.

[17] Geifman, Y., & El-Yaniv, R. (2017). Selective Classification for Deep Neural Networks. NeurIPS 2017.

[18] Tapsai, C., et al. (2021). Natural Language Interface to Database for Data Retrieval and Processing. Applied Science and Engineering Progress.

[19] Robertson, S., & Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in IR.

[20] Valizadegan, H., et al. (2009). Learning to Rank by Optimizing NDCG Measure. NeurIPS 2009.

[21] Abdallah, A., et al. (2025). From Retrieval to Generation: Comparing Different Approaches. arXiv:2502.20245.

[22] Rao, A., et al. (2025). Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models. arXiv:2506.00049.

[23] Gao, Y., et al. (2024). Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv:2312.10997.

[24] Doan, N.N., et al. (2024). A Hybrid Retrieval Approach for Advancing Retrieval-Augmented Generation Systems. ICNLSP 2024.

[25] Yu, H., et al. (2024). Evaluation of Retrieval-Augmented Generation: A Survey. CCF Big Data Conference.

---

# RINGKASAN REFERENSI PER SECTION

| Section | Referensi yang Dipakai |
|---------|------------------------|
| 1. Introduction | [1], [2], [3], [4], [5], [6], [7], [8], [11], [12], [15], [16], [18] |
| 2.1 Chatbots | [5], [6], [7] |
| 2.2 Conv IR & RAG | [1], [2], [3], [4], [8], [9], [10], [11], [23] |
| 2.3 Faceted Search | [8], [12] |
| 2.4 Hybrid & Vector | [13], [14], [15], [16], [21], [22], [24] |
| 2.5 NL to DB | [18] |
| 2.6 RAG Evaluation | [17], [19], [20], [25] |
| 2.7 Research Gap | - |
| 3.1 System Architecture | [16] |
| 3.5.2 Software Stack | [15], [16] |
| 3.6.1 Constraints | [19], [20] |
| 3.6.3 No Result | [17] |
| 3.7 Agent Flow | [16], [17] |
| 4. Results | - |
| 5. Conclusion | - |

---

*File dibuat: 27 Januari 2026*
*Siap untuk insert referensi ke Word via Mendeley*
