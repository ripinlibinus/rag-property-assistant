# Master Reference List for RAG Property Chatbot Thesis

## Overview

Dokumen ini berisi semua referensi yang digunakan dalam paper thesis RAG Property Chatbot. Referensi disusun berdasarkan kategori untuk memudahkan pencarian saat menulis.

**Total Referensi:** 28+

---

## Cara Penggunaan

Saat menulis paper, gunakan tag `[REF-XX]` untuk menandai sitasi yang perlu dimasukkan via Mendeley:
- Contoh: "RAG mitigates hallucination **[REF-01]**"
- Kemudian di Word, ganti `[REF-XX]` dengan citation dari Mendeley

---

## Category A: RAG Foundations

### [REF-01] RAG Original Paper
- **Title:** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- **Authors:** Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., et al.
- **Year:** 2020
- **Venue:** NeurIPS 2020
- **DOI:** 10.48550/arXiv.2005.11401
- **Tags:** `RAG`, `foundational`, `knowledge-intensive`
- **Use for:** Defining RAG, grounding LLM outputs, combining retrieval + generation

```bibtex
@inproceedings{lewis2020retrieval,
  title={Retrieval-augmented generation for knowledge-intensive NLP tasks},
  author={Lewis, Patrick and Perez, Ethan and Piktus, Aleksandra and Petroni, Fabio and Karpukhin, Vladimir and Goyal, Naman and others},
  booktitle={Advances in Neural Information Processing Systems},
  volume={33},
  pages={9459--9474},
  year={2020}
}
```

---

### [REF-02] Fusion-in-Decoder
- **Title:** Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering
- **Authors:** Izacard, G. and Grave, E.
- **Year:** 2021
- **Venue:** EACL 2021
- **DOI:** 10.18653/v1/2021.eacl-main.74
- **Tags:** `passage-retrieval`, `QA`, `evidence-aggregation`
- **Use for:** Aggregating evidence from multiple passages

```bibtex
@inproceedings{izacard2021leveraging,
  title={Leveraging passage retrieval with generative models for open domain question answering},
  author={Izacard, Gautier and Grave, Edouard},
  booktitle={Proceedings of the 16th Conference of the European Chapter of the ACL},
  pages={874--880},
  year={2021}
}
```

---

### [REF-03] DPR - Dense Passage Retrieval
- **Title:** Dense Passage Retrieval for Open-Domain Question Answering
- **Authors:** Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., Yih, W.
- **Year:** 2020
- **Venue:** EMNLP 2020
- **DOI:** 10.18653/v1/2020.emnlp-main.550
- **Tags:** `dense-retrieval`, `vector-search`, `embeddings`
- **Use for:** Dense/vector retrieval methods, semantic search

```bibtex
@inproceedings{karpukhin2020dense,
  title={Dense passage retrieval for open-domain question answering},
  author={Karpukhin, Vladimir and Oguz, Barlas and Min, Sewon and Lewis, Patrick and Wu, Ledell and Edunov, Sergey and Chen, Danqi and Yih, Wen-tau},
  booktitle={Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing},
  pages={6769--6781},
  year={2020}
}
```

---

### [REF-04] ColBERT
- **Title:** ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT
- **Authors:** Khattab, O. and Zaharia, M.
- **Year:** 2020
- **Venue:** SIGIR 2020
- **DOI:** 10.1145/3397271.3401075
- **Tags:** `late-interaction`, `efficient-retrieval`, `BERT`
- **Use for:** Efficient dense retrieval, late-interaction ranking

```bibtex
@inproceedings{khattab2020colbert,
  title={ColBERT: Efficient and effective passage search via contextualized late interaction over BERT},
  author={Khattab, Omar and Zaharia, Matei},
  booktitle={Proceedings of the 43rd International ACM SIGIR Conference},
  pages={39--48},
  year={2020}
}
```

---

### [REF-10] REALM
- **Title:** REALM: Retrieval-Augmented Language Model Pre-Training
- **Authors:** Guu, K., Lee, K., Tung, Z., Pasupat, P., Chang, M.W.
- **Year:** 2020
- **DOI:** 10.5555/3524938.3525306
- **Tags:** `pretraining`, `retrieval-augmented`
- **Use for:** Retrieval-augmented pretraining

```bibtex
@inproceedings{guu2020realm,
  title={REALM: Retrieval-augmented language model pre-training},
  author={Guu, Kelvin and Lee, Kenton and Tung, Zora and Pasupat, Panupong and Chang, Ming-Wei},
  booktitle={International Conference on Machine Learning},
  pages={3929--3938},
  year={2020}
}
```

---

### [REF-11] RAG + LLM Survey
- **Title:** A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models
- **Authors:** Fan, W., et al.
- **Year:** 2024
- **Venue:** KDD 2024
- **DOI:** 10.1145/3637528.3671470
- **Tags:** `survey`, `RAG`, `LLM`
- **Use for:** RAG landscape, trade-offs (recall vs latency)

```bibtex
@inproceedings{fan2024survey,
  title={A Survey on RAG Meeting LLMs: Towards Retrieval-Augmented Large Language Models},
  author={Fan, Wenqi and others},
  booktitle={Proceedings of the 30th ACM SIGKDD Conference},
  pages={6491--6501},
  year={2024}
}
```

---

## Category B: Chatbots & Conversational Systems

### [REF-05] AI Chatbot in Real Estate
- **Title:** Analyzing the Impact of AI-Enabled Chatbot on Service Quality in the Real Estate Sector: An Empirical Study in NCR
- **Authors:** Sao, A., Pathak, D., Vijh, G., Saxena, S., Deogaonkar, A.
- **Year:** 2025
- **Venue:** Procedia Computer Science
- **DOI:** 10.1016/j.procs.2025.04.075
- **Tags:** `real-estate`, `chatbot`, `service-quality`
- **Use for:** AI chatbot benefits in real estate, agent productivity

```bibtex
@inproceedings{sao2025analyzing,
  title={Analyzing the Impact of AI-Enabled Chatbot on Service Quality in the Real Estate Sector},
  author={Sao, Anurag and Pathak, Divya and Vijh, Gaurav and Saxena, Shivam and Deogaonkar, Ankit},
  booktitle={Procedia Computer Science},
  pages={1198--1207},
  year={2025},
  publisher={Elsevier}
}
```

---

### [REF-06] Conversational Recommender Systems Survey
- **Title:** A Survey on Conversational Recommender Systems
- **Authors:** Jannach, D., Manzoor, A., Cai, W., Chen, L.
- **Year:** 2022
- **Venue:** ACM Computing Surveys
- **DOI:** 10.1145/3453154
- **Tags:** `CRS`, `survey`, `dialogue`
- **Use for:** Multi-turn preference elicitation, dialogue strategies

```bibtex
@article{jannach2022survey,
  title={A Survey on Conversational Recommender Systems},
  author={Jannach, Dietmar and Manzoor, Ahtsham and Cai, Wanling and Chen, Li},
  journal={ACM Computing Surveys},
  volume={54},
  number={5},
  year={2022}
}
```

---

### [REF-07] CRS Advances and Challenges
- **Title:** Advances and Challenges in Conversational Recommender Systems: A Survey
- **Authors:** Gao, C., Lei, W., He, X., de Rijke, M., Chua, T.S.
- **Year:** 2021
- **Venue:** AI Open
- **DOI:** 10.1016/j.aiopen.2021.06.002
- **Tags:** `CRS`, `challenges`, `survey`
- **Use for:** CRS challenges, interaction friction

```bibtex
@article{gao2021advances,
  title={Advances and challenges in conversational recommender systems: A survey},
  author={Gao, Chongming and Lei, Wenqiang and He, Xiangnan and de Rijke, Maarten and Chua, Tat-Seng},
  journal={AI Open},
  volume={2},
  pages={100--126},
  year={2021}
}
```

---

## Category C: Conversational IR & Search

### [REF-08] Conversational Search Framework
- **Title:** A Theoretical Framework for Conversational Search
- **Authors:** Radlinski, F. and Craswell, N.
- **Year:** 2017
- **Venue:** CHIIR 2017
- **DOI:** 10.1145/3020165.3020183
- **Tags:** `conversational-IR`, `framework`, `dialogue`
- **Use for:** Conversational search properties, iterative refinement

```bibtex
@inproceedings{radlinski2017theoretical,
  title={A theoretical framework for conversational search},
  author={Radlinski, Filip and Craswell, Nick},
  booktitle={Proceedings of the 2017 Conference on Human Information Interaction and Retrieval},
  pages={117--126},
  year={2017}
}
```

---

### [REF-09] TREC CAsT
- **Title:** CAsT 2020: The Conversational Assistance Track Overview
- **Authors:** Dalton, J., Xiong, C., Callan, J.
- **Year:** 2021
- **URL:** https://trec.nist.gov/pubs/trec29/papers/OVERVIEW.C.pdf
- **Tags:** `benchmark`, `conversational-assistance`, `TREC`
- **Use for:** Conversational assistance methodology, query rewriting

```bibtex
@inproceedings{dalton2021cast,
  title={CAsT 2020: The Conversational Assistance Track Overview},
  author={Dalton, Jeffrey and Xiong, Chenyan and Callan, Jamie},
  booktitle={TREC},
  year={2021}
}
```

---

### [REF-12] Search User Interfaces
- **Title:** Search User Interfaces
- **Authors:** Hearst, M.A.
- **Year:** 2009
- **Publisher:** Cambridge University Press
- **URL:** https://searchuserinterfaces.com/
- **Tags:** `HCI`, `faceted-search`, `UI`
- **Use for:** Faceted filtering limitations, form-based search friction

```bibtex
@book{hearst2009search,
  title={Search User Interfaces},
  author={Hearst, Marti A.},
  year={2009},
  publisher={Cambridge University Press}
}
```

---

## Category D: Vector Search & Infrastructure

### [REF-13] FAISS
- **Title:** FAISS: A Library for Efficient Similarity Search
- **Authors:** Facebook AI Research
- **Year:** 2017
- **URL:** https://faiss.ai/
- **Tags:** `vector-search`, `ANN`, `infrastructure`
- **Use for:** Billion-scale similarity search

```bibtex
@misc{faiss2017,
  title={FAISS: A Library for Efficient Similarity Search and Clustering of Dense Vectors},
  author={Facebook AI Research},
  year={2017},
  url={https://faiss.ai/}
}
```

---

### [REF-14] Product Quantization
- **Title:** Product Quantization for Nearest Neighbor Search
- **Authors:** Jegou, H., Douze, M., Schmid, C.
- **Year:** 2011
- **Venue:** IEEE TPAMI
- **DOI:** 10.1109/TPAMI.2010.57
- **Tags:** `quantization`, `ANN`, `efficiency`
- **Use for:** Efficient ANN search techniques

```bibtex
@article{jegou2011product,
  title={Product quantization for nearest neighbor search},
  author={J{\'e}gou, Herv{\'e} and Douze, Matthijs and Schmid, Cordelia},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  volume={33},
  number={1},
  pages={117--128},
  year={2011}
}
```

---

### [REF-15] ChromaDB
- **Title:** Chroma: The AI-native Open-source Embedding Database
- **Authors:** Chroma Team
- **Year:** 2023
- **URL:** https://docs.trychroma.com/
- **Tags:** `vector-store`, `embeddings`, `infrastructure`
- **Use for:** Vector storage, semantic search implementation

```bibtex
@misc{chroma2023,
  title={Chroma: The AI-native Open-source Embedding Database},
  author={Chroma},
  year={2023},
  url={https://docs.trychroma.com/}
}
```

---

### [REF-16] LangChain
- **Title:** LangChain: Building Applications with LLMs
- **Authors:** LangChain Team
- **Year:** 2023
- **URL:** https://docs.langchain.com/
- **Tags:** `orchestration`, `framework`, `tools`
- **Use for:** LLM orchestration, tool-augmented prompting

```bibtex
@misc{langchain2023,
  title={LangChain: Building Applications with LLMs},
  author={LangChain},
  year={2023},
  url={https://docs.langchain.com/}
}
```

---

## Category E: Evaluation & Metrics

### [REF-17] Selective Classification
- **Title:** Selective Classification for Deep Neural Networks
- **Authors:** Geifman, Y. and El-Yaniv, R.
- **Year:** 2017
- **Venue:** NeurIPS 2017
- **Tags:** `abstention`, `selective-prediction`, `confidence`
- **Use for:** Correct abstention, no-result handling

```bibtex
@inproceedings{geifman2017selective,
  title={Selective Classification for Deep Neural Networks},
  author={Geifman, Yonatan and El-Yaniv, Ran},
  booktitle={Advances in Neural Information Processing Systems},
  volume={30},
  year={2017}
}
```

---

### [REF-18] Natural Language to Database
- **Title:** Natural Language Interface to Database for Data Retrieval and Processing
- **Authors:** Tapsai, C., Meesad, P., Haruechaiyasak, C.
- **Year:** 2021
- **Venue:** Applied Science and Engineering Progress
- **DOI:** 10.14416/j.asep.2020.05.003
- **Tags:** `text-to-SQL`, `NL-interface`, `database`
- **Use for:** Text-to-JSON conversion, structured query generation

```bibtex
@article{tapsai2021natural,
  title={Natural language interface to database for data retrieval and processing},
  author={Tapsai, Chaloemphon and Meesad, Phayung and Haruechaiyasak, Choochart},
  journal={Applied Science and Engineering Progress},
  volume={14},
  number={3},
  pages={435--446},
  year={2021}
}
```

---

### [REF-19] BM25 Framework
- **Title:** The Probabilistic Relevance Framework: BM25 and Beyond
- **Authors:** Robertson, S. and Zaragoza, H.
- **Year:** 2009
- **Venue:** Foundations and Trends in IR
- **DOI:** 10.1561/1500000019
- **Tags:** `BM25`, `probabilistic-IR`, `ranking`
- **Use for:** Sparse retrieval baseline, probabilistic ranking

```bibtex
@article{robertson2009probabilistic,
  title={The probabilistic relevance framework: BM25 and beyond},
  author={Robertson, Stephen and Zaragoza, Hugo},
  journal={Foundations and Trends in Information Retrieval},
  volume={3},
  number={4},
  pages={333--389},
  year={2009}
}
```

---

### [REF-20] NDCG Optimization
- **Title:** Learning to Rank by Optimizing NDCG Measure
- **Authors:** Valizadegan, H., Jin, R., Zhang, R., Mao, J.
- **Year:** 2009
- **Venue:** NeurIPS 2009
- **Tags:** `learning-to-rank`, `NDCG`, `metrics`
- **Use for:** Ranking metrics, NDCG explanation

```bibtex
@inproceedings{valizadegan2009learning,
  title={Learning to Rank by Optimizing NDCG Measure},
  author={Valizadegan, Hamed and Jin, Rong and Zhang, Ruofei and Mao, Jianchang},
  booktitle={Advances in Neural Information Processing Systems},
  volume={22},
  year={2009}
}
```

---

## Category F: Additional Hybrid RAG Research

### [REF-21] Comparing Retrieval Approaches
- **Title:** From Retrieval to Generation: Comparing Different Approaches
- **Authors:** Abdallah, A., Mozafari, J., Piryani, B., Ali, M., Jatowt, A.
- **Year:** 2025
- **arXiv:** 2502.20245
- **Tags:** `comparison`, `BM25`, `DPR`, `hybrid`
- **Use for:** Comparing sparse vs dense vs hybrid retrieval

```bibtex
@article{abdallah2025retrieval,
  title={From Retrieval to Generation: Comparing Different Approaches},
  author={Abdallah, Abdelrahman and Mozafari, Jamshid and Piryani, Bhawna and Ali, Mohammed and Jatowt, Adam},
  journal={arXiv preprint arXiv:2502.20245},
  year={2025}
}
```

---

### [REF-22] Rethinking Hybrid Retrieval
- **Title:** Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models
- **Authors:** Rao, A., Alipour, H., Pendar, N.
- **Year:** 2025
- **arXiv:** 2506.00049
- **Tags:** `hybrid`, `re-ranking`, `small-models`
- **Use for:** Hybrid + re-ranking effectiveness

```bibtex
@article{rao2025rethinking,
  title={Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models},
  author={Rao, Arjun and Alipour, Hanieh and Pendar, Nick},
  journal={arXiv preprint arXiv:2506.00049},
  year={2025}
}
```

---

### [REF-23] RAG Survey (Gao et al.)
- **Title:** Retrieval-Augmented Generation for Large Language Models: A Survey
- **Authors:** Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., et al.
- **Year:** 2024
- **arXiv:** 2312.10997
- **Citations:** 2000+
- **Tags:** `survey`, `RAG`, `comprehensive`
- **Use for:** RAG taxonomy (Naive, Advanced, Modular)

```bibtex
@article{gao2024rag,
  title={Retrieval-Augmented Generation for Large Language Models: A Survey},
  author={Gao, Yunfan and Xiong, Yun and Gao, Xinyu and Jia, Kangxiang and Pan, Jinliu and Bi, Yuxi and Dai, Yi and Sun, Jiawei and Wang, Meng and others},
  journal={arXiv preprint arXiv:2312.10997},
  year={2024}
}
```

---

### [REF-24] Hybrid RAG Approach (Doan et al.)
- **Title:** A Hybrid Retrieval Approach for Advancing Retrieval-Augmented Generation Systems
- **Authors:** Doan, N.N., Harma, A., Celebi, R.
- **Year:** 2024
- **Venue:** ICNLSP 2024
- **URL:** https://aclanthology.org/2024.icnlsp-1.41.pdf
- **Tags:** `hybrid`, `retrieve-then-rerank`
- **Use for:** Hybrid retriever + reranking

```bibtex
@inproceedings{doan2024hybrid,
  title={A Hybrid Retrieval Approach for Advancing RAG Systems},
  author={Doan, Ngoc Nhu and H{\"a}rm{\"a}, Aki and Celebi, Remzi},
  booktitle={Proceedings of ICNLSP 2024},
  year={2024}
}
```

---

### [REF-25] RAG Evaluation Survey
- **Title:** Evaluation of Retrieval-Augmented Generation: A Survey
- **Authors:** Yu, H., Gan, A., Zhang, K., Tong, S., Liu, Q., Liu, Z.
- **Year:** 2024
- **Venue:** CCF Big Data Conference
- **Citations:** 313
- **Tags:** `evaluation`, `RAG`, `benchmarks`
- **Use for:** RAG evaluation metrics and benchmarks

```bibtex
@inproceedings{yu2024evaluation,
  title={Evaluation of Retrieval-Augmented Generation: A Survey},
  author={Yu, Hao and Gan, An and Zhang, Kai and Tong, Shiwei and Liu, Qi and Liu, Zhenya},
  booktitle={CCF Conference on Big Data},
  pages={93--108},
  year={2024}
}
```

---

### [REF-26] Hybrid RAG for LLM Query Enhancement
- **Title:** Hybrid Retrieval-Augmented Generation Approach for LLMs Query Response Enhancement
- **Authors:** Omrani, P., Hosseini, A., Hooshanfar, K.
- **Year:** 2024
- **Venue:** IEEE ICWR 2024
- **Citations:** 38
- **Tags:** `hybrid`, `query-enhancement`
- **Use for:** Hybrid RAG performance comparison

```bibtex
@inproceedings{omrani2024hybrid,
  title={Hybrid RAG Approach for LLMs Query Response Enhancement},
  author={Omrani, Pouria and Hosseini, Amir and Hooshanfar, Kamran},
  booktitle={IEEE International Conference on Web Research},
  pages={1--6},
  year={2024}
}
```

---

### [REF-27] RAG vs Long-Context LLMs
- **Title:** Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach
- **Authors:** Li, Z., Li, C., Zhang, M., Mei, Q., Bendersky, M.
- **Year:** 2024
- **arXiv:** 2407.16833
- **Venue:** EMNLP 2024 Industry Track
- **Tags:** `RAG`, `long-context`, `self-route`
- **Use for:** RAG vs long context comparison

```bibtex
@inproceedings{li2024retrieval,
  title={RAG or Long-Context LLMs? A Comprehensive Study},
  author={Li, Zhuowan and Li, Cheng and Zhang, Mingyang and Mei, Qiaozhu and Bendersky, Michael},
  booktitle={EMNLP 2024 Industry Track},
  year={2024}
}
```

---

### [REF-28] RAG Text Generation Survey
- **Title:** A Survey on Retrieval-Augmented Text Generation for Large Language Models
- **Authors:** Huang, Y. and Huang, J.
- **Year:** 2024
- **arXiv:** 2404.10981
- **Tags:** `survey`, `text-generation`, `RAG-stages`
- **Use for:** RAG stages (pre-retrieval, retrieval, post-retrieval, generation)

```bibtex
@article{huang2024survey,
  title={A Survey on Retrieval-Augmented Text Generation for LLMs},
  author={Huang, Yizheng and Huang, Jimmy},
  journal={arXiv preprint arXiv:2404.10981},
  year={2024}
}
```

---

## Quick Reference Table

| REF ID | Short Name | Category | Primary Use |
|--------|------------|----------|-------------|
| REF-01 | Lewis RAG | RAG Foundations | RAG definition |
| REF-02 | Izacard FiD | RAG Foundations | Evidence aggregation |
| REF-03 | Karpukhin DPR | RAG Foundations | Dense retrieval |
| REF-04 | Khattab ColBERT | RAG Foundations | Late interaction |
| REF-05 | Sao Real Estate | Chatbots | Real estate AI chatbot |
| REF-06 | Jannach CRS | Chatbots | CRS survey |
| REF-07 | Gao CRS | Chatbots | CRS challenges |
| REF-08 | Radlinski Conv | Conversational IR | Conv search framework |
| REF-09 | Dalton CAsT | Conversational IR | TREC benchmark |
| REF-10 | Guu REALM | RAG Foundations | Retrieval pretraining |
| REF-11 | Fan RAG Survey | RAG Foundations | RAG + LLM landscape |
| REF-12 | Hearst UI | Search UI | Faceted search limits |
| REF-13 | FAISS | Infrastructure | Vector search |
| REF-14 | Jegou PQ | Infrastructure | ANN efficiency |
| REF-15 | ChromaDB | Infrastructure | Vector store |
| REF-16 | LangChain | Infrastructure | Orchestration |
| REF-17 | Geifman Selective | Evaluation | Abstention |
| REF-18 | Tapsai NL2DB | Evaluation | Text-to-SQL |
| REF-19 | Robertson BM25 | Evaluation | Sparse retrieval |
| REF-20 | Valizadegan NDCG | Evaluation | Ranking metrics |
| REF-21 | Abdallah Compare | Hybrid RAG | Method comparison |
| REF-22 | Rao Rethinking | Hybrid RAG | Re-ranking |
| REF-23 | Gao RAG Survey | Hybrid RAG | RAG taxonomy |
| REF-24 | Doan Hybrid | Hybrid RAG | Retrieve-rerank |
| REF-25 | Yu Eval Survey | Evaluation | RAG evaluation |
| REF-26 | Omrani Hybrid | Hybrid RAG | Query enhancement |
| REF-27 | Li RAG vs LC | Hybrid RAG | RAG vs long context |
| REF-28 | Huang Survey | Hybrid RAG | RAG stages |

---

## Usage Examples in Paper

### Introduction
```
"RAG mitigates hallucination by pairing generation with retrieval [REF-01]."
"Dense retrieval methods like DPR [REF-03] and ColBERT [REF-04] have shown..."
"Faceted search imposes overhead when intents are fuzzy [REF-12]."
```

### Related Work
```
"AI chatbots improve service quality in real estate [REF-05]."
"Conversational recommender systems emphasize multi-turn elicitation [REF-06], [REF-07]."
"Conversational search formalizes interactive IR properties [REF-08]."
```

### Methodology
```
"We use ChromaDB for vector storage [REF-15] with LangChain orchestration [REF-16]."
"Text-to-JSON conversion follows approaches from [REF-18]."
```

### Evaluation
```
"We derive metrics from confusion matrix analysis [REF-19], [REF-20]."
"Correct abstention follows selective classification principles [REF-17]."
```

---

## Paper Citation Mapping (REF-ID → Paper Number)

Mapping antara REF-ID di dokumen ini dengan nomor sitasi [X] di paper.docx:

| Paper [X] | REF-ID | Nama Singkat | Digunakan di Section |
|-----------|--------|--------------|----------------------|
| [1] | REF-01 | Lewis RAG 2020 | 1, 2.2 |
| [2] | REF-02 | Izacard FiD 2021 | 1, 2.2 |
| [3] | REF-03 | Karpukhin DPR 2020 | 1, 2.2 |
| [4] | REF-04 | Khattab ColBERT 2020 | 1, 2.2 |
| [5] | REF-05 | Sao Real Estate 2025 | 1, 2.1 |
| [6] | REF-06 | Jannach CRS 2022 | 1, 2.1 |
| [7] | REF-07 | Gao CRS 2021 | 1, 2.1 |
| [8] | REF-08 | Radlinski Conv 2017 | 1, 2.2, 2.3 |
| [9] | REF-09 | Dalton CAsT 2021 | 2.2 |
| [10] | REF-10 | Guu REALM 2020 | 2.2 |
| [11] | REF-11 | Fan RAG Survey 2024 | 1, 2.2 |
| [12] | REF-12 | Hearst UI 2009 | 1, 2.3 |
| [13] | REF-13 | FAISS 2017 | 2.4 |
| [14] | REF-14 | Jegou PQ 2011 | 2.4 |
| [15] | REF-15 | ChromaDB 2023 | 1, 2.4, 3.5 |
| [16] | REF-16 | LangChain 2023 | 1, 3.1, 3.5, 3.7 |
| [17] | REF-17 | Geifman Selective 2017 | 2.6, 3.7 |
| [18] | REF-18 | Tapsai NL2DB 2021 | 1, 2.5 |
| [19] | REF-19 | Robertson BM25 2009 | 3.6 |
| [20] | REF-20 | Valizadegan NDCG 2009 | 3.6 |

### Referensi Tambahan (Belum Dipakai di Paper)

| REF-ID | Nama Singkat | Potensi Penggunaan |
|--------|--------------|-------------------|
| REF-21 | Abdallah Compare | Perbandingan sparse vs dense |
| REF-22 | Rao Rethinking | Hybrid + re-ranking |
| REF-23 | Gao RAG Survey | RAG taxonomy |
| REF-24 | Doan Hybrid | Retrieve-rerank approach |
| REF-25 | Yu Eval Survey | RAG evaluation methods |
| REF-26 | Omrani Hybrid | Query enhancement |
| REF-27 | Li RAG vs LC | RAG vs long context |
| REF-28 | Huang Survey | RAG stages |

### Cara Penggunaan di Paper

Saat menulis di Word, gunakan format `[X]` sesuai mapping di atas:
- Contoh: "The ReAct agent uses LangGraph for orchestration [16]."
- Kemudian gunakan Mendeley untuk replace dengan proper citation

---

*Document created: 26 January 2026*
*Last updated: 26 January 2026*
*For: Thesis RAG Property Chatbot*
