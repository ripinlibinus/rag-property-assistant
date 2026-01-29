# BAB I PENDAHULUAN

## 1.1 Latar Belakang

Kalau kita lihat, industri properti di Indonesia ini mengalami kemajuan yang cukup signifikan dalam beberapa tahun belakangan. Data dari AREBI (Asosiasi Real Estate Broker Indonesia) menunjukan bahwa ada lebih dari 1.400 kantor properti yang tersebar di seluruh wilayah Indonesia, dengan jumlah tenaga pemasaran yang mencapai lebih dari 50.000 orang. Nah, pertumbuhan ini tentunya juga diiringi dengan ekspektasi konsumen yang makin tinggi terhadap profesionalisme layanan - baik itu soal kecepatan respon maupun kualitas informasi yang dikasih.

Sehari-hari, tenaga pemasaran properti itu sering banget menghadapi tantangan dalam hal menyediakan informasi yang cepat dan akurat ke calon pembeli. Mereka harus bisa jawab macem-macem pertanyaan yang sifatnya natural dan variatif lah, misalnya kayak "carikan rumah 3 kamar di sekitar Cemara dengan harga sekitar 1 miliar" atau "ada rumah yang deket sama mall gak?". Pertanyaan-pertanyaan model begini butuh pemahaman kontekstual yang susah dijawab sama sistem pencarian filter tradisional yang ada sekarang.

Platform pencarian properti yang konvensional umumnya masih pakai pendekatan faceted search - yaitu dropdown filter untuk parameter kayak lokasi, rentang harga, jumlah kamar, tipe properti, dan sebagainya [12]. Walaupun pendekatan ini lumayan robust buat query yang udah terdefinisi dengan jelas, tapi tetep aja ada gap yang cukup besar antara cara pikir pengguna sama antarmuka sistemnya. Pengguna itu cenderung mikir pakai istilah-istilah fuzzy kayak "harga terjangkau", "deket sekolah", atau "rumah luas ada tamannya", yang mana hal-hal ini gak bisa langsung ditranslate ke parameter filter diskrit [8].

Gap ini bikin beberapa masalah praktis di lapangan. Pertama, pengguna butuh waktu lebih lama buat menerjemahkan kebutuhan mereka ke format filter yang ada. Kedua, hasil pencarian sering gak sesuai ekspektasi soalnya parameter yang dimasukin gak bener-bener mencerminkan intent sebenernya si pengguna. Terus yang ketiga, fitur-fitur properti yang gak terstruktur di database (contohnya "ada CCTV", "deket mall", "view bagus") itu gak bisa sama sekali dicari lewat filter konvensional.

Nah, perkembangan teknologi AI (Artificial Intelligence), khususnya Large Language Models atau LLM, ini membuka peluang baru buat menjembatani gap tadi [24]. LLM kayak GPT-4 punya kemampuan buat memahami bahasa natural dengan tingkat akurasi yang lumayan tinggi [21], jadi pengguna bisa mengekspresikan kebutuhannya pakai bahasa sehari-hari tanpa perlu ngerti terminologi teknis atau struktur filter tertentu. Tapi ya, LLM murni juga ada kelemahannya yang cukup fundamental - yaitu hallucination. Maksudnya, dia bisa menghasilkan informasi yang kelihatannya bener tapi sebenernya gak punya basis faktual [1].

Retrieval-Augmented Generation (RAG) hadir sebagai solusi buat mengatasi keterbatasan LLM ini [1]. Jadi RAG itu menggabungkan kemampuan pemahaman bahasa dari LLM dengan retrieval dari sumber data yang otoritatif, sehingga respons yang dihasilkan itu grounded pada fakta yang bisa diverifikasi [11]. Dalam konteks properti, RAG bikin chatbot bisa memahami query bahasa natural sambil tetep ngambil data dari database properti yang akurat dan up-to-date [5].

Implementasi RAG buat pencarian properti sendiri bisa pakai macem-macem strategi retrieval [3]. Ada yang namanya strategi Vector-Only - ini pakai semantic search berbasis embedding buat nemuin properti yang relevan secara semantik [4]. Ada juga API-Only yang mengkonversi query jadi parameter filter terstruktur buat query langsung ke database [18]. Dan ada Hybrid yang ngekombinasiin kedua pendekatan itu supaya dapet keuntungan dari masing-masing [33], [34].

Kenapa penelitian ini penting? Soalnya sejauh ini belum ada studi yang secara sistematis ngebandingin efektivitas berbagai strategi retrieval dalam konteks RAG khususnya buat domain properti. Perbandingan ini perlu dilakukan buat ngidentifikasi pendekatan mana yang paling optimal - yang bisa kasih akurasi tinggi sekaligus coverage yang komprehensif buat berbagai jenis query.

Jadi berdasarkan latar belakang yang udah dipaparkan tadi, penelitian ini bakal mengembangkan chatbot AI berbasis RAG sebagai asisten virtual agen properti. Nanti bakal dibandingin tiga strategi retrieval: Vector-Only, API-Only, sama Hybrid. Evaluasinya pakai framework constraint-based yang ngukur sejauh mana hasil pencarian bisa memenuhi kriteria yang dispesifikasikan di query pengguna.

## 1.2 Perumusan Masalah

Dari latar belakang yang udah diuraikan di atas, penelitian ini merumuskan masalah-masalah berikut:

1. Gimana cara merancang sistem chatbot berbasis RAG yang bisa memahami query natural language buat pencarian properti?

2. Gimana cara ngebandingin efektivitas strategi retrieval Vector-Only, API-Only, sama Hybrid dalam konteks pencarian properti?

3. Gimana cara ngukur akurasi sistem pakai pendekatan constraint-based yang bisa mencerminkan kepuasan terhadap kriteria pencarian?

4. Strategi retrieval mana sih yang paling optimal buat berbagai jenis query properti (transaksional, berbasis fitur, berbasis lokasi)?

## 1.3 Tujuan Penelitian

Tujuan dari penelitian ini adalah:

1. Merancang dan mengimplementasikan sistem chatbot berbasis RAG dengan arsitektur ReAct Agent yang bisa memahami query bahasa natural buat pencarian properti.

2. Ngebandingin tiga strategi retrieval (Vector-Only, API-Only, Hybrid) pakai dataset gold-labeled questions yang sama biar perbandingannya fair.

3. Mengembangkan framework evaluasi constraint-based dengan metrik Per-Constraint Accuracy (PCA), Constraint Pass Ratio (CPR), sama Strict Success Ratio.

4. Ngidentifikasi strategi retrieval yang optimal buat berbagai kategori query dan kasih rekomendasi praktis buat implementasi sistem pencarian properti.

## 1.4 Manfaat Penelitian

### 1.4.1 Manfaat Bagi Tenaga Pemasaran Properti

Chatbot AI yang dikembangkan di penelitian ini diharapkan bisa kasih manfaat langsung buat tenaga pemasaran properti:

1. **Efisiensi Meningkat**: Tenaga pemasaran bisa respon pertanyaan pelanggan lebih cepet tanpa harus cari-cari manual di database.

2. **Info Akurat**: Sistem menjamin informasi yang dikasih (harga, ketersediaan, spesifikasi) selalu akurat dan terkini karena konek langsung sama data live.

3. **Bisa Handle Query Kompleks**: Mampu jawab pertanyaan yang involve kombinasi kriteria dan bahasa informal.

4. **Support Konteks Percakapan**: Bisa paham pertanyaan lanjutan yang nyambung sama konteks sebelumnya.

### 1.4.2 Manfaat Bagi Perusahaan Broker

Implementasi sistem ini juga kasih nilai strategis buat perusahaan broker properti:

1. **Skalabilitas**: Bisa layanin banyak inquiry barengan tanpa harus nambah SDM secara proporsional.

2. **Konsistensi**: Respons chatbot selalu konsisten, gak dipengaruhi faktor kayak capek atau mood.

3. **Available 24/7**: Sistem bisa jalan di luar jam kerja, jadi bisa tangkep leads yang mungkin kelewat.

4. **Data Insights**: Bisa analisis pola pertanyaan pelanggan buat lebih paham preferensi pasar.

### 1.4.3 Manfaat Bagi Industri Properti Indonesia

Secara lebih luas, penelitian ini berkontribusi buat:

1. **Modernisasi Industri**: Dorong adopsi teknologi AI di industri properti Indonesia.

2. **Standar Evaluasi**: Sediain framework evaluasi yang bisa dipake buat ngukur sistem-sistem serupa.

3. **Best Practices**: Identifikasi pendekatan optimal yang bisa diadopsi pelaku industri lain.

### 1.4.4 Manfaat Bagi Pengembangan Ilmu Pengetahuan

Dari sisi akademis, penelitian ini kontribusi:

1. **Perbandingan Empiris**: Sediain data perbandingan sistematis antar strategi retrieval yang belum ada di literatur.

2. **Framework Evaluasi Baru**: Kembangkan constraint-based evaluation metrics yang bisa diaplikasiin ke domain lain.

3. **Domain-Specific RAG**: Demonstrasiin penerapan RAG buat domain properti Indonesia dengan karakteristik bahasa lokal.

## 1.5 Hipotesis Penelitian

Berdasarkan rumusan masalah dan tujuan penelitian, diajukan hipotesis-hipotesis ini:

**H1**: Strategi Hybrid retrieval bakal menghasilkan akurasi lebih tinggi dibanding Vector-Only dan API-Only pada sistem chatbot RAG buat domain properti.

*Alasannya*: Hybrid gabungin keunggulan structured query (akurasi constraint) sama semantic search (coverage semantik), jadi diharapkan kasih performa yang lebih bagus.

**H2**: Sistem chatbot RAG yang dikembangkan mampu memahami query natural language dengan akurasi di atas 80%.

*Alasannya*: Kombinasi LLM buat pemahaman bahasa plus retrieval dari data otoritatif harusnya bisa hasilin akurasi tinggi.

**H3**: Ada perbedaan signifikan dalam Per-Constraint Accuracy antara ketiga strategi retrieval buat berbagai jenis constraint.

*Alasannya*: Tiap strategi punya kekuatan dan kelemahan di jenis constraint yang beda-beda, jadi bakal hasilin profil performa yang distinct.

## 1.6 Ruang Lingkup Penelitian

Ruang lingkup penelitian ini adalah:

### 1.6.1 Batasan Geografis

Penelitian fokus di pasar properti wilayah Medan, Indonesia. Kenapa Medan? Karena ketersediaan data dari kantor properti mitra dan karakteristik pasarnya cukup representatif.

### 1.6.2 Batasan Dataset

Dataset yang dipake terdiri dari:
- Kurang lebih 2.800 listing properti aktif
- 30 gold-labeled questions dalam 12 kategori
- Tipe properti: rumah, apartemen, ruko, tanah, gudang

### 1.6.3 Batasan Teknologi

Komponen teknologi yang dipake:
- Model LLM: GPT-4o-mini dari OpenAI
- Model Embedding: text-embedding-3-small dari OpenAI
- Vector Database: ChromaDB
- Backend: FastAPI pakai Python
- Frontend: Vue.js

### 1.6.4 Batasan Evaluasi

Evaluasi difokuskan pada:
- Metrik constraint-based (PCA, CPR, Strict Success)
- Confusion matrix analysis (Precision, Recall, F1, Accuracy)
- User experience survey (10 responden)

Yang gak termasuk lingkup penelitian:
- Evaluasi biaya operasional jangka panjang
- A/B testing di production environment
- Perbandingan sama sistem chatbot properti komersial lain

## 1.7 Sistematika Penulisan

Tesis ini disusun dalam lima bab:

### BAB I: PENDAHULUAN

Bab ini uraikan latar belakang penelitian - soal gap antara pencarian properti tradisional sama kebutuhan pemahaman bahasa natural. Juga dipaparkan rumusan masalah, tujuan, manfaat buat berbagai stakeholder, hipotesis, ruang lingkup, dan sistematika penulisan.

### BAB II: TINJAUAN PUSTAKA

Bab ini sajikan landasan teori yang mendasari penelitian. Meliputi konsep AI, Machine Learning, NLP, Large Language Models, RAG, Vector Database dan Semantic Search, Conversational Search, Hybrid Retrieval, evaluasi sistem RAG, plus tinjauan penelitian terdahulu yang relevan.

### BAB III: METODOLOGI PENELITIAN

Bab ini jelasin metodologi secara komprehensif - kerangka pemikiran, arsitektur sistem (high-level architecture, ReAct agent design, tool layer, data sources), persiapan data (pengumpulan, cleaning, vector index, gold standard questions), implementasi tiga strategi retrieval, framework evaluasi, implementasi teknis, dan keterbatasan metodologi.

### BAB IV: HASIL DAN PEMBAHASAN

Bab ini sajikan hasil implementasi sistem dan evaluasi kuantitatif. Ada pembahasan mendalam soal keunggulan masing-masing strategi, analisis kenapa Hybrid unggul, perbandingan sama penelitian terdahulu, dan implikasi praktis. User experience evaluation juga disajikan.

### BAB V: SIMPULAN DAN SARAN

Bab ini simpulkan temuan utama, jawab pertanyaan penelitian, dan validasi/tolak hipotesis. Ada juga saran pengembangan ke depan - dynamic routing, expanded evaluation, user study, multi-turn dialogue, integrasi platform messaging, multi-market expansion.

---

**Ringkasan BAB I:**

Bab ini udah paparkan:

1. **Latar Belakang**: Gap pencarian properti tradisional vs kebutuhan bahasa natural, potensi RAG sebagai solusi.

2. **Rumusan Masalah**: 4 pertanyaan soal perancangan, perbandingan strategi, pengukuran akurasi, identifikasi strategi optimal.

3. **Tujuan**: Implementasi chatbot RAG, bandingin 3 strategi, kembangkan framework evaluasi, kasih rekomendasi praktis.

4. **Manfaat**: Buat tenaga pemasaran, perusahaan broker, industri properti, ilmu pengetahuan.

5. **Hipotesis**: 3 hipotesis soal keunggulan Hybrid, akurasi >80%, perbedaan per-constraint accuracy.

6. **Ruang Lingkup**: Fokus Medan, ~2.800 listings, 30 gold questions, teknologi OpenAI + ChromaDB.

7. **Sistematika**: 5 bab dari Pendahuluan sampe Simpulan.
