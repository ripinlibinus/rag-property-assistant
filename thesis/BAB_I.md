# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Industri properti Indonesia mengalami pertumbuhan yang signifikan dalam beberapa tahun terakhir. Berdasarkan data Asosiasi Real Estate Broker Indonesia (AREBI), terdapat lebih dari 50.000 tenaga pemasaran properti yang aktif melayani kebutuhan masyarakat dalam transaksi jual beli dan sewa properti. Pertumbuhan ini diiringi dengan meningkatnya ekspektasi konsumen terhadap kecepatan dan kualitas layanan informasi.

Tenaga pemasaran properti menghadapi tantangan dalam menyediakan informasi secara cepat dan akurat kepada calon pembeli. Dalam praktik sehari-hari, tenaga pemasaran harus menjawab berbagai pertanyaan yang bersifat natural dan variatif, seperti "carikan rumah 3 kamar di sekitar Cemara dengan harga sekitar 1 miliar" atau "ada rumah yang dekat dengan mall tidak?". Pertanyaan-pertanyaan semacam ini memerlukan pemahaman kontekstual yang tidak dapat dijawab oleh sistem pencarian berbasis filter tradisional.

Platform pencarian properti konvensional umumnya menggunakan pendekatan faceted search dengan dropdown filter untuk parameter seperti lokasi, rentang harga, jumlah kamar, dan tipe properti [12]. Meskipun pendekatan ini robust untuk query yang terdefinisi dengan baik, terdapat gap signifikan antara cara berpikir pengguna dan antarmuka sistem. Pengguna cenderung berpikir dalam istilah fuzzy seperti "harga terjangkau", "dekat sekolah", atau "rumah luas dengan taman", yang tidak dapat langsung diterjemahkan ke parameter filter diskrit [8].

Gap ini menimbulkan beberapa permasalahan praktis. Pertama, pengguna memerlukan waktu lebih lama untuk menerjemahkan kebutuhan mereka ke dalam format filter yang tersedia. Kedua, hasil pencarian sering tidak sesuai ekspektasi karena parameter tidak mencerminkan intent sebenarnya. Ketiga, fitur-fitur properti yang tidak terstruktur dalam database (seperti "ada CCTV", "dekat mall", atau "view bagus") tidak dapat dicari melalui filter konvensional.

Perkembangan teknologi Artificial Intelligence (AI), khususnya Large Language Models (LLM), membuka peluang untuk menjembatani gap ini [24]. LLM seperti GPT-4 memiliki kemampuan memahami bahasa natural dengan tingkat akurasi yang tinggi [21], memungkinkan pengguna mengekspresikan kebutuhan dalam bahasa sehari-hari tanpa perlu menguasai terminologi teknis atau struktur filter. Namun, LLM murni memiliki kelemahan fundamental berupa hallucination—menghasilkan informasi yang tampak benar tetapi tidak memiliki basis faktual [1].

Retrieval-Augmented Generation (RAG) hadir sebagai solusi untuk mengatasi keterbatasan LLM [1]. RAG menggabungkan kemampuan pemahaman bahasa LLM dengan retrieval dari sumber data otoritatif, memastikan respons yang dihasilkan grounded pada fakta yang dapat diverifikasi [11]. Dalam konteks properti, RAG memungkinkan chatbot untuk memahami query natural language sambil mengambil data dari database properti yang akurat dan terkini [5].

Implementasi RAG untuk pencarian properti dapat menggunakan berbagai strategi retrieval [3]. Strategi Vector-Only menggunakan semantic search berbasis embedding untuk menemukan properti yang relevan secara semantik [4]. Strategi API-Only mengkonversi query menjadi parameter filter terstruktur untuk query langsung ke database [18]. Strategi Hybrid mengkombinasikan kedua pendekatan untuk mendapatkan keuntungan dari masing-masing [33], [34].

Penelitian ini penting untuk dilakukan karena belum ada studi yang secara sistematis membandingkan efektivitas berbagai strategi retrieval dalam konteks RAG untuk domain properti. Perbandingan ini diperlukan untuk mengidentifikasi pendekatan optimal yang dapat memberikan akurasi tinggi sekaligus coverage yang komprehensif terhadap berbagai jenis query.

Berdasarkan latar belakang tersebut, penelitian ini mengembangkan chatbot AI berbasis RAG untuk asisten virtual agen properti dengan membandingkan tiga strategi retrieval: Vector-Only, API-Only, dan Hybrid. Evaluasi dilakukan menggunakan framework constraint-based yang mengukur sejauh mana hasil pencarian memenuhi kriteria yang dispesifikasikan dalam query pengguna.

## 1.2 Perumusan Masalah

Berdasarkan latar belakang yang telah diuraikan, penelitian ini merumuskan masalah sebagai berikut:

1. Bagaimana merancang sistem chatbot berbasis RAG yang dapat memahami query natural language untuk pencarian properti?

2. Bagaimana membandingkan efektivitas strategi retrieval Vector-Only, API-Only, dan Hybrid dalam konteks pencarian properti?

3. Bagaimana mengukur akurasi sistem dengan pendekatan constraint-based yang mencerminkan kepuasan terhadap kriteria pencarian?

4. Strategi retrieval mana yang paling optimal untuk berbagai jenis query properti (transaksional, berbasis fitur, berbasis lokasi)?

## 1.3 Tujuan Penelitian

Penelitian ini memiliki tujuan sebagai berikut:

1. Merancang dan mengimplementasikan sistem chatbot berbasis RAG dengan arsitektur ReAct Agent yang dapat memahami query bahasa natural untuk pencarian properti.

2. Membandingkan tiga strategi retrieval (Vector-Only, API-Only, dan Hybrid) menggunakan dataset gold-labeled questions yang sama untuk memastikan perbandingan yang adil.

3. Mengembangkan framework evaluasi constraint-based dengan metrik Per-Constraint Accuracy (PCA), Constraint Pass Ratio (CPR), dan Strict Success Ratio.

4. Mengidentifikasi strategi retrieval optimal untuk berbagai kategori query dan memberikan rekomendasi praktis untuk implementasi sistem pencarian properti.

## 1.4 Manfaat Penelitian

### 1.4.1 Manfaat Bagi Tenaga Pemasaran Properti

Chatbot AI yang dikembangkan dalam penelitian ini memberikan manfaat langsung bagi tenaga pemasaran properti:

1. **Peningkatan Efisiensi**: Tenaga pemasaran dapat merespons pertanyaan pelanggan dengan lebih cepat tanpa perlu mencari manual dalam database.

2. **Akurasi Informasi**: Sistem menjamin informasi yang diberikan (harga, ketersediaan, spesifikasi) selalu akurat dan terkini karena terhubung dengan data live.

3. **Penanganan Query Kompleks**: Mampu menjawab pertanyaan yang melibatkan kombinasi kriteria dan bahasa informal.

4. **Dukungan Konteks Percakapan**: Memahami pertanyaan lanjutan yang merujuk pada konteks sebelumnya.

### 1.4.2 Manfaat Bagi Perusahaan Broker

Implementasi sistem ini memberikan nilai strategis bagi perusahaan broker properti:

1. **Skalabilitas Layanan**: Dapat melayani banyak inquiry secara simultan tanpa peningkatan proporsional sumber daya manusia.

2. **Konsistensi Layanan**: Respons chatbot konsisten dan tidak dipengaruhi faktor seperti kelelahan atau mood.

3. **Ketersediaan 24/7**: Sistem dapat beroperasi di luar jam kerja normal, menangkap leads yang mungkin terlewat.

4. **Data Insights**: Dapat menganalisis pola pertanyaan pelanggan untuk memahami preferensi pasar.

### 1.4.3 Manfaat Bagi Industri Properti Indonesia

Secara lebih luas, penelitian ini berkontribusi pada:

1. **Modernisasi Industri**: Mendorong adopsi teknologi AI dalam industri properti Indonesia.

2. **Standar Evaluasi**: Menyediakan framework evaluasi yang dapat digunakan untuk mengukur sistem serupa.

3. **Best Practices**: Mengidentifikasi pendekatan optimal yang dapat diadopsi oleh pelaku industri lain.

### 1.4.4 Manfaat Bagi Pengembangan Ilmu Pengetahuan

Dari perspektif akademis, penelitian ini memberikan kontribusi:

1. **Perbandingan Empiris**: Menyediakan data perbandingan sistematis antar strategi retrieval yang belum tersedia dalam literatur.

2. **Framework Evaluasi Baru**: Mengembangkan constraint-based evaluation metrics yang dapat diaplikasikan ke domain lain.

3. **Domain-Specific RAG**: Mendemonstrasikan penerapan RAG untuk domain properti Indonesia dengan karakteristik bahasa lokal.

## 1.5 Hipotesis Penelitian

Berdasarkan rumusan masalah dan tujuan penelitian, diajukan hipotesis sebagai berikut:

**H1**: Strategi Hybrid retrieval menghasilkan akurasi yang lebih tinggi dibandingkan strategi Vector-Only dan API-Only pada sistem chatbot RAG untuk domain properti.

*Rasional*: Hybrid menggabungkan keunggulan structured query (akurasi constraint) dan semantic search (coverage semantik), sehingga diharapkan memberikan performa superior.

**H2**: Sistem chatbot RAG yang dikembangkan mampu memahami query natural language dengan tingkat akurasi di atas 80%.

*Rasional*: Kombinasi LLM untuk pemahaman bahasa dan retrieval dari data otoritatif diharapkan menghasilkan akurasi tinggi.

**H3**: Terdapat perbedaan signifikan dalam Per-Constraint Accuracy antara ketiga strategi retrieval untuk berbagai jenis constraint.

*Rasional*: Setiap strategi memiliki kekuatan dan kelemahan pada jenis constraint yang berbeda, menghasilkan profil performa yang distinct.

## 1.6 Ruang Lingkup Penelitian

Penelitian ini memiliki ruang lingkup sebagai berikut:

### 1.6.1 Batasan Geografis

Penelitian fokus pada pasar properti di wilayah Medan, Indonesia. Pemilihan ini didasarkan pada ketersediaan data dari kantor properti mitra dan karakteristik pasar yang representatif.

### 1.6.2 Batasan Dataset

Dataset yang digunakan terdiri dari:
- Sekitar 2.800 listing properti aktif
- 30 gold-labeled questions dalam 12 kategori
- Tipe properti mencakup rumah, apartemen, ruko, tanah, dan gudang

### 1.6.3 Batasan Teknologi

Komponen teknologi yang digunakan:
- Model LLM: GPT-4o-mini dari OpenAI
- Model Embedding: text-embedding-3-small dari OpenAI
- Vector Database: ChromaDB
- Backend: FastAPI dengan Python
- Frontend: Vue.js

### 1.6.4 Batasan Evaluasi

Evaluasi difokuskan pada:
- Metrik constraint-based (PCA, CPR, Strict Success)
- Confusion matrix analysis (Precision, Recall, F1, Accuracy)
- User experience survey (10 responden)

Tidak termasuk dalam lingkup:
- Evaluasi biaya operasional jangka panjang
- A/B testing pada production environment
- Perbandingan dengan sistem chatbot properti komersial lain

## 1.7 Sistematika Penulisan

Tesis ini disusun dalam lima bab dengan sistematika sebagai berikut:

### BAB I: PENDAHULUAN

Bab ini menguraikan latar belakang penelitian yang menjelaskan gap antara pencarian properti tradisional dan kebutuhan pemahaman bahasa natural. Dipaparkan pula rumusan masalah, tujuan penelitian, manfaat penelitian bagi berbagai stakeholder, hipotesis yang diajukan, ruang lingkup penelitian, dan sistematika penulisan.

### BAB II: TINJAUAN PUSTAKA

Bab ini menyajikan landasan teori yang mendasari penelitian, meliputi konsep Artificial Intelligence, Machine Learning, Natural Language Processing, Large Language Models, Retrieval-Augmented Generation, Vector Database dan Semantic Search, Conversational Search, Hybrid Retrieval Approaches, evaluasi sistem RAG, serta tinjauan penelitian terdahulu yang relevan dengan gap analysis dan positioning penelitian ini.

### BAB III: METODOLOGI PENELITIAN

Bab ini menjelaskan metodologi penelitian secara komprehensif, mencakup kerangka pemikiran, arsitektur sistem (high-level architecture, ReAct agent design, tool layer, data sources), persiapan data (pengumpulan, cleaning, vector index, gold standard questions), implementasi tiga strategi retrieval (Vector-Only, API-Only, Hybrid), framework evaluasi (constraint-based metrics, question-level evaluation, evaluation protocol), implementasi teknis (hardware, software, hyperparameters), dan keterbatasan metodologi.

### BAB IV: HASIL DAN PEMBAHASAN

Bab ini menyajikan hasil implementasi sistem (API Contract integration, frontend, vector database, agent implementation) dan hasil evaluasi kuantitatif (summary metrics comparison, per-constraint accuracy analysis, confusion matrix analysis, per-category performance, response time analysis). Disertakan pula pembahasan mendalam tentang keunggulan masing-masing strategi, analisis mengapa Hybrid unggul, perbandingan dengan penelitian terdahulu, dan implikasi praktis. Evaluasi user experience juga disajikan untuk validasi penerimaan pengguna.

### BAB V: SIMPULAN DAN SARAN

Bab ini menyimpulkan temuan utama penelitian, menjawab pertanyaan penelitian yang dirumuskan, dan memvalidasi atau menolak hipotesis yang diajukan. Disertakan pula saran untuk pengembangan sistem di masa depan, termasuk dynamic routing, expanded evaluation, user study, multi-turn dialogue sophistication, integrasi dengan platform messaging, dan multi-market expansion.

---

**Ringkasan BAB I:**

Bab ini telah memaparkan landasan penelitian yang meliputi:

1. **Latar Belakang**: Gap antara pencarian properti tradisional dan kebutuhan pemahaman bahasa natural, serta potensi RAG sebagai solusi.

2. **Rumusan Masalah**: Empat pertanyaan penelitian tentang perancangan, perbandingan strategi, pengukuran akurasi, dan identifikasi strategi optimal.

3. **Tujuan Penelitian**: Implementasi chatbot RAG, perbandingan tiga strategi, pengembangan framework evaluasi, dan rekomendasi praktis.

4. **Manfaat Penelitian**: Bagi tenaga pemasaran, perusahaan broker, industri properti, dan pengembangan ilmu pengetahuan.

5. **Hipotesis**: Tiga hipotesis tentang keunggulan Hybrid, akurasi >80%, dan perbedaan per-constraint accuracy.

6. **Ruang Lingkup**: Fokus Medan, ~2.800 listings, 30 gold questions, teknologi OpenAI + ChromaDB.

7. **Sistematika**: Struktur lima bab dari Pendahuluan hingga Simpulan.
