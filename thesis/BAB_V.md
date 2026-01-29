# BAB V SIMPULAN DAN SARAN

Bab ini menyajikan simpulan dari penelitian berdasarkan temuan yang telah dipaparkan pada bab sebelumnya, serta saran untuk pengembangan sistem di masa depan.

## 5.1 Simpulan

Berdasarkan hasil penelitian yang telah dilakukan, dapat disimpulkan beberapa hal sebagai berikut:

### 5.1.1 Keberhasilan Implementasi Sistem RAG

Penelitian ini berhasil merancang dan mengimplementasikan sistem chatbot berbasis Retrieval-Augmented Generation (RAG) [1] untuk asisten virtual agen properti. Sistem yang dikembangkan memiliki karakteristik:

1. **Arsitektur ReAct Agent**: Menggunakan paradigma Reason-Act-Observe yang memungkinkan penalaran eksplisit dalam pemilihan strategi dan tools.

2. **9 Tools Spesialisasi**: Menyediakan fungsi-fungsi khusus untuk pencarian properti (search_properties, search_nearby, search_knowledge, dll.) yang menangani berbagai jenis query.

3. **Dual Data Sources**: Mengintegrasikan Property API sebagai source of truth untuk data transaksional dan ChromaDB [15] sebagai vector store untuk pencarian semantik.

4. **API Contract Architecture**: Mengadopsi arsitektur database-agnostic yang memungkinkan integrasi dengan berbagai sumber data selama mengikuti format respons standar.

### 5.1.2 Perbandingan Tiga Strategi Retrieval

Penelitian ini berhasil membandingkan tiga strategi retrieval secara sistematis menggunakan 30 gold-labeled questions. Hasil evaluasi menunjukkan hierarki performa yang jelas:

| Strategi | Accuracy | Mean CPR | F1-Score |
|----------|----------|----------|----------|
| **Hybrid** | **100%** | **97,61%** | **100%** |
| API-Only | 73,33% | 73,35% | 83,33% |
| Vector-Only | 56,67% | 55,33% | 66,77% |

**Temuan kunci perbandingan:**

- **Vector-Only** unggul pada pemahaman lokasi (PCA 94,02%) namun lemah pada constraint transaksional (price PCA 43,75%)
- **API-Only** sempurna pada constraint terstruktur (100%) namun gagal total pada feature_search dan nearby_search (0%)
- **Hybrid** mewarisi keunggulan kedua strategi dengan akurasi 100% di semua kategori query

### 5.1.3 Validasi Hipotesis

**H1: Strategi Hybrid retrieval menghasilkan akurasi yang lebih tinggi** - **TERBUKTI**

Hybrid mencapai 100% accuracy, mengungguli API-Only (73,33%) dan Vector-Only (56,67%) dengan margin signifikan 26,67% dan 43,33%.

**H2: Sistem mampu memahami query natural language dengan akurasi >80%** - **TERBUKTI**

Strategi Hybrid mencapai 100% accuracy, jauh melampaui threshold 80% yang dihipotesiskan. Bahkan API-Only (73,33%) mendekati threshold ini.

**H3: Terdapat perbedaan signifikan dalam Per-Constraint Accuracy antar strategi** - **TERBUKTI**

Tabel per-constraint menunjukkan perbedaan dramatis:
- Price: Vector 43,75% vs API/Hybrid 100%
- Property_type: Vector 52,17% vs API/Hybrid 100%
- Feature-based queries: API 0% vs Hybrid 100%

### 5.1.4 Kontribusi Framework Evaluasi Constraint-Based

Penelitian ini mengembangkan framework evaluasi yang mengukur kepuasan constraint secara objektif:

1. **Per-Constraint Accuracy (PCA)**: Mengukur proporsi constraint yang terpenuhi per listing
2. **Constraint Pass Ratio (CPR)**: Mengukur proporsi listing yang memenuhi semua constraint
3. **Strict Success**: Binary indicator untuk listing dengan PCA = 100%
4. **Confusion Matrix Analysis**: Mengukur performa klasifikasi pada tingkat pertanyaan

Framework ini memberikan insight yang lebih mendalam dibandingkan metrik tradisional (Precision, Recall, MRR) karena langsung mengukur kepuasan terhadap kriteria pencarian.

### 5.1.5 Validasi User Experience

Survei terhadap 10 tenaga pemasaran properti menunjukkan tingkat kepuasan tinggi:

- **Rata-rata keseluruhan**: 4,76 dari 5,00 (95,2%)
- **Waktu respons**: 4,90/5,00 (sangat memuaskan)
- **Kepuasan keseluruhan**: 4,90/5,00
- **Kesediaan menggunakan**: 4,90/5,00

Hasil ini memvalidasi bahwa sistem tidak hanya akurat secara teknis, tetapi juga diterima dengan baik oleh pengguna akhir.

### 5.1.6 Keterbatasan Sistem

Meskipun mencapai performa tinggi, sistem memiliki beberapa keterbatasan:

1. **Gold Set Size**: Evaluasi menggunakan 30 pertanyaan, membatasi statistical power untuk analisis subgroup
2. **Single Market**: Fokus pada pasar Medan, hasil mungkin berbeda di pasar lain
3. **Index Lag**: Vector index disinkronisasi periodik, dapat menyebabkan temporary stale data
4. **LLM Dependency**: Bergantung pada OpenAI API untuk inference dan embedding

## 5.2 Saran Pengembangan

Berdasarkan temuan dan keterbatasan yang teridentifikasi, berikut saran untuk pengembangan sistem di masa depan:

### 5.2.1 Dynamic Routing

**Deskripsi**: Mengembangkan learned policy untuk secara otomatis memilih strategi retrieval (Vector, API, atau Hybrid) berdasarkan karakteristik query.

**Rasional**: Meskipun Hybrid unggul secara keseluruhan, terdapat kasus di mana single strategy lebih efisien. Query dengan constraint jelas ("rumah 3 kamar max 1M") dapat langsung menggunakan API tanpa semantic overhead.

**Implementasi yang Disarankan**:
- Classifier untuk mengkategorikan query
- Routing rules berbasis kategori
- A/B testing untuk optimasi threshold

### 5.2.2 Expanded Evaluation

**Deskripsi**: Memperluas dataset evaluasi ke 100-200 pertanyaan dengan multiple annotators.

**Rasional**: Dataset lebih besar memungkinkan:
- Statistical power untuk analisis subgroup
- Inter-annotator agreement metrics (Cohen's κ)
- Identifikasi edge cases yang lebih komprehensif

**Implementasi yang Disarankan**:
- Crowdsourcing annotation dengan training
- Stratified sampling untuk coverage kategori
- Periodic refresh untuk data currency

### 5.2.3 User Study dengan SUS Metrics

**Deskripsi**: Melakukan studi usability formal menggunakan System Usability Scale (SUS) dan task completion metrics.

**Rasional**: Survei saat ini mengukur satisfaction, namun tidak mengukur:
- Task completion time
- Error rate dalam pencarian
- Learnability curve

**Implementasi yang Disarankan**:
- Controlled experiment dengan 30+ pengguna
- Pre-defined task scenarios
- Think-aloud protocol untuk qualitative insights

### 5.2.4 Multi-turn Dialogue Sophistication

**Deskripsi**: Meningkatkan kemampuan sistem dalam menangani percakapan multi-turn yang kompleks.

**Rasional**: Evaluasi menunjukkan pemahaman konteks (4,45/5,00) adalah dimensi dengan skor terendah.

**Implementasi yang Disarankan**:
- Enhanced memory management dengan summarization
- Explicit slot filling untuk preference tracking
- Clarification request generation
- Preference refinement across turns

### 5.2.5 Integrasi Platform Messaging

**Deskripsi**: Mengintegrasikan chatbot dengan platform messaging populer seperti WhatsApp dan Telegram.

**Rasional**: Tenaga pemasaran sering berkomunikasi dengan calon pembeli melalui platform ini. Integrasi akan meningkatkan aksesibilitas.

**Implementasi yang Disarankan**:
- WhatsApp Business API integration
- Telegram Bot API integration
- Unified backend dengan multi-channel frontend
- Rich message formatting (cards, carousels)

### 5.2.6 Multi-Market Expansion

**Deskripsi**: Memperluas coverage ke pasar properti di kota-kota lain di Indonesia.

**Rasional**: Arsitektur API Contract memungkinkan ekspansi tanpa perubahan signifikan pada sistem core.

**Implementasi yang Disarankan**:
- Onboarding flow untuk partner properti baru
- Regional terminology mapping
- Price normalization across markets
- Distributed vector indices per region

### 5.2.7 Optimasi Performa

**Deskripsi**: Meningkatkan kecepatan respons dan mengurangi latency.

**Rasional**: Hybrid memiliki latency tertinggi (rata-rata 2,2 detik). Optimasi dapat meningkatkan user experience.

**Implementasi yang Disarankan**:
- Response caching untuk query frequent
- Parallel execution untuk API dan semantic search
- Model distillation untuk inference lebih cepat
- Edge deployment untuk reduced network latency

### 5.2.8 Monitoring dan Analytics

**Deskripsi**: Mengembangkan dashboard monitoring untuk tracking performa sistem di production.

**Rasional**: Performa dapat berubah seiring waktu akibat data drift atau perubahan pola query.

**Implementasi yang Disarankan**:
- Real-time metrics dashboard
- Query pattern analysis
- Automatic alert untuk anomali performa
- A/B testing infrastructure

---

**Penutup:**

Penelitian ini telah berhasil mencapai seluruh tujuan yang ditetapkan. Sistem chatbot RAG yang dikembangkan mendemonstrasikan bahwa kombinasi structured query dan semantic search (Hybrid) adalah pendekatan optimal untuk pencarian properti berbasis natural language, mencapai 100% accuracy yang mengungguli strategi tunggal manapun.

Framework evaluasi constraint-based yang dikembangkan memberikan metodologi yang reproducible untuk menilai sistem serupa. Temuan ini memiliki implikasi praktis yang signifikan bagi pengembangan asisten virtual di industri properti Indonesia dan dapat diadaptasi untuk domain transaksional lainnya yang memerlukan kombinasi pemahaman semantik dan akurasi constraint.

Dengan saran pengembangan yang dipaparkan, sistem ini berpotensi menjadi solusi enterprise-ready yang dapat meningkatkan efisiensi tenaga pemasaran properti dan pengalaman calon pembeli dalam mencari properti idaman mereka.
