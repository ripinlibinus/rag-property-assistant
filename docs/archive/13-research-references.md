# Research References for RAG Property Chatbot

## Overview

Dokumen ini berisi referensi penelitian yang relevan untuk thesis RAG Property Chatbot, khususnya yang membandingkan metode retrieval (API, Vector Search, Hybrid).

---

## 1. Paper Utama yang Sangat Relevan

### 1.1 "From Retrieval to Generation: Comparing Different Approaches" ⭐⭐⭐

- **Authors:** Abdallah, Mozafari, Piryani, Ali, Jatowt
- **Year:** 2025
- **arXiv:** [2502.20245](https://arxiv.org/abs/2502.20245)
- **Status:** Work in progress

**Relevansi:** SANGAT MIRIP dengan penelitian MetaProperty!

**Yang Dibandingkan:**
- BM25 (sparse/lexical retrieval)
- DPR - Dense Passage Retrieval (vector)
- Hybrid models (kombinasi sparse + dense)

**Metrics yang Digunakan:**
- Top-1 accuracy
- nDCG@10
- Perplexity (untuk language modeling)

**Hasil Utama:**
- DPR: 50.17% top-1 accuracy pada Natural Questions
- Hybrid: nDCG@10 naik dari 43.42 (BM25) → 52.59
- BM25 lebih baik untuk perplexity pada WikiText-103

**BibTeX:**
```bibtex
@article{abdallah2025retrieval,
  title={From Retrieval to Generation: Comparing Different Approaches},
  author={Abdallah, Abdelrahman and Mozafari, Jamshid and Piryani, Bhawna and Ali, Mohammed and Jatowt, Adam},
  journal={arXiv preprint arXiv:2502.20245},
  year={2025}
}
```

---

### 1.2 "Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models" ⭐⭐⭐

- **Authors:** Rao, Alipour, Pendar
- **Year:** 2025
- **arXiv:** [2506.00049](https://arxiv.org/abs/2506.00049)

**Relevansi:** Tri-modal hybrid retrieval dengan re-ranking (mirip implementasi kita)

**Yang Dibandingkan:**
- Dense semantic embeddings
- Sparse lexical (BM25-style)
- Graph-based embeddings
- LLM-based re-ranking

**Datasets:** SciFact, FIQA, NFCorpus

**Temuan Utama:**
- Model embedding kecil (MiniLM-v6) + LLM re-ranking bisa mengalahkan model besar
- Hybrid approach dengan re-ranking memberikan improvement signifikan
- Alignment dengan LLM lebih penting dari ukuran model

**BibTeX:**
```bibtex
@article{rao2025rethinking,
  title={Rethinking Hybrid Retrieval: When Small Embeddings and LLM Re-ranking Beat Bigger Models},
  author={Rao, Arjun and Alipour, Hanieh and Pendar, Nick},
  journal={arXiv preprint arXiv:2506.00049},
  year={2025}
}
```

---

### 1.3 "Retrieval-Augmented Generation for Large Language Models: A Survey" ⭐⭐⭐

- **Authors:** Gao, Xiong, Gao, Jia, Pan, Bi, Dai, Sun, Wang, et al.
- **Year:** 2023-2024
- **arXiv:** [2312.10997](https://arxiv.org/abs/2312.10997)
- **Citations:** 2000+

**Relevansi:** Survey komprehensif tentang RAG, framework evaluasi

**Covers:**
- Naive RAG
- Advanced RAG  
- Modular RAG
- Evaluation frameworks dan benchmarks

**BibTeX:**
```bibtex
@article{gao2024rag,
  title={Retrieval-Augmented Generation for Large Language Models: A Survey},
  author={Gao, Yunfan and Xiong, Yun and Gao, Xinyu and Jia, Kangxiang and Pan, Jinliu and Bi, Yuxi and Dai, Yi and Sun, Jiawei and Wang, Meng and others},
  journal={arXiv preprint arXiv:2312.10997},
  year={2024}
}
```

---

## 2. Paper Pendukung

### 2.1 "A Hybrid Retrieval Approach for Advancing RAG Systems"

- **Authors:** Doan, Härmä, Celebi
- **Year:** 2024
- **Venue:** ICNLSP 2024
- **URL:** [ACL Anthology](https://aclanthology.org/2024.icnlsp-1.41.pdf)
- **Citations:** 7

**Relevansi:** Hybrid retriever + retrieve-then-rerank

**BibTeX:**
```bibtex
@inproceedings{doan2024hybrid,
  title={A Hybrid Retrieval Approach for Advancing Retrieval-Augmented Generation Systems},
  author={Doan, Ngoc Nhu and H{\"a}rm{\"a}, Aki and Celebi, Remzi},
  booktitle={Proceedings of the 7th International Conference on Natural Language and Speech Processing (ICNLSP 2024)},
  year={2024}
}
```

---

### 2.2 "Evaluation of Retrieval-Augmented Generation: A Survey"

- **Authors:** Yu, Gan, Zhang, Tong, Liu, Liu
- **Year:** 2024
- **Venue:** CCF Conference on Big Data
- **Citations:** 313

**Relevansi:** Evaluation metrics dan benchmarks untuk RAG systems

**BibTeX:**
```bibtex
@inproceedings{yu2024evaluation,
  title={Evaluation of Retrieval-Augmented Generation: A Survey},
  author={Yu, Hao and Gan, An and Zhang, Kai and Tong, Shiwei and Liu, Qi and Liu, Zhenya},
  booktitle={CCF Conference on Big Data},
  pages={93--108},
  year={2024},
  publisher={Springer}
}
```

---

### 2.3 "Hybrid Retrieval-Augmented Generation Approach for LLMs Query Response Enhancement"

- **Authors:** Omrani, Hosseini, Hooshanfar
- **Year:** 2024
- **Venue:** IEEE International Conference on Web Research
- **Citations:** 38

**Relevansi:** Hybrid RAG framework dengan performance comparison

**BibTeX:**
```bibtex
@inproceedings{omrani2024hybrid,
  title={Hybrid Retrieval-Augmented Generation Approach for LLMs Query Response Enhancement},
  author={Omrani, Pouria and Hosseini, Amir and Hooshanfar, Kamran},
  booktitle={2024 10th International Conference on Web Research (ICWR)},
  pages={1--6},
  year={2024},
  organization={IEEE}
}
```

---

### 2.4 "Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach"

- **Authors:** Li, Li, Zhang, Mei, Bendersky
- **Year:** 2024
- **arXiv:** [2407.16833](https://arxiv.org/abs/2407.16833)
- **Venue:** EMNLP 2024 Industry Track
- **Citations:** 112

**Relevansi:** Perbandingan RAG vs Long Context dengan hybrid approach (Self-Route)

**BibTeX:**
```bibtex
@inproceedings{li2024retrieval,
  title={Retrieval Augmented Generation or Long-Context LLMs? A Comprehensive Study and Hybrid Approach},
  author={Li, Zhuowan and Li, Cheng and Zhang, Mingyang and Mei, Qiaozhu and Bendersky, Michael},
  booktitle={Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing: Industry Track},
  year={2024}
}
```

---

### 2.5 "A Survey on Retrieval-Augmented Text Generation for Large Language Models"

- **Authors:** Huang, Huang
- **Year:** 2024
- **arXiv:** [2404.10981](https://arxiv.org/abs/2404.10981)

**Relevansi:** Kategorisasi RAG (pre-retrieval, retrieval, post-retrieval, generation)

**BibTeX:**
```bibtex
@article{huang2024survey,
  title={A Survey on Retrieval-Augmented Text Generation for Large Language Models},
  author={Huang, Yizheng and Huang, Jimmy},
  journal={arXiv preprint arXiv:2404.10981},
  year={2024}
}
```

---

## 3. Mapping Referensi ke Implementasi MetaProperty

| Aspek MetaProperty | Paper Referensi | Section |
|-------------------|-----------------|---------|
| API-based Search | Abdallah et al. (BM25 comparison) | 1.1 |
| Vector Search (ChromaDB) | Abdallah et al. (DPR), Rao et al. | 1.1, 1.2 |
| Hybrid Search | Semua paper di atas | 1.1-2.4 |
| Re-ranking | Rao et al., Doan et al. | 1.2, 2.1 |
| Evaluation Metrics | Yu et al., Abdallah et al. | 2.2, 1.1 |
| RAG Framework | Gao et al. Survey | 1.3 |

---

## 4. Metrics yang Digunakan di Literatur

| Metric | Deskripsi | Digunakan di |
|--------|-----------|--------------|
| **Precision@K** | Proporsi hasil relevan dalam K teratas | Umum di semua paper |
| **Recall@K** | Proporsi dokumen relevan yang ditemukan | STARK benchmark |
| **nDCG@10** | Normalized Discounted Cumulative Gain | Abdallah et al. |
| **MRR** | Mean Reciprocal Rank | STARK benchmark |
| **Hit@K** | Apakah ada hasil relevan dalam K teratas | STARK benchmark |
| **Top-1 Accuracy** | Akurasi hasil pertama | Abdallah et al. |
| **Perplexity** | Untuk language modeling tasks | Abdallah et al. |

---

## 5. Kesimpulan untuk Thesis

Berdasarkan literatur:

1. **Hybrid approach terbukti lebih baik** dari single-method (confirmed by Abdallah et al., Rao et al.)

2. **Re-ranking memberikan improvement signifikan** (Rao et al., Doan et al.)

3. **Perbandingan 3 metode sudah umum dilakukan:**
   - Sparse/Lexical (BM25, API-based)
   - Dense/Vector (DPR, ChromaDB)
   - Hybrid (kombinasi keduanya)

4. **Metrics yang disarankan untuk thesis:**
   - Precision@5 (mudah dihitung, umum digunakan)
   - Success Rate (custom, praktis)
   - Response Quality (manual rating)
   - Latency (performance)

---

*Dokumen ini dibuat: 23 Januari 2026*
*Untuk: Thesis RAG Property Chatbot*
