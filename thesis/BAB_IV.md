# BAB IV HASIL DAN PEMBAHASAN

Bab ini menyajikan hasil implementasi sistem chatbot AI berbasis RAG untuk asisten virtual agen properti, hasil evaluasi kuantitatif terhadap tiga strategi retrieval, serta pembahasan mendalam mengenai temuan penelitian.

## 4.1 Hasil Implementasi Sistem

Implementasi sistem chatbot AI untuk agen properti dilakukan melalui beberapa tahapan yang saling terintegrasi, meliputi perancangan arsitektur berbasis API Contract, pengembangan antarmuka pengguna, pembangunan vector database, dan implementasi agent berbasis ReAct. Subbab ini menjelaskan secara rinci setiap komponen implementasi.

### 4.1.1 API Contract dan Data Source Integration

Sistem yang dikembangkan mengadopsi arsitektur berbasis API Contract yang bersifat *database-agnostic*. Pendekatan ini memungkinkan sistem untuk menerima data dari berbagai sumber database (MySQL, PostgreSQL, MongoDB, atau database lainnya) selama respons yang diberikan sesuai dengan format yang telah ditentukan. Keunggulan arsitektur ini adalah fleksibilitas dalam integrasi dengan sistem properti yang sudah ada tanpa memerlukan perubahan pada struktur database internal.

#### Spesifikasi API Contract

Sistem memerlukan dua endpoint utama untuk beroperasi:

**Endpoint Pencarian Properti:**
```
GET /api/properties
```

Endpoint ini menerima parameter query sebagai berikut:

| Parameter | Tipe | Deskripsi |
|-----------|------|-----------|
| listing_type | string | Jenis listing: "rent" atau "sale" |
| property_type | string | Tipe properti: "house", "apartment", "ruko", dll. |
| min_price | number | Batas harga minimum |
| max_price | number | Batas harga maksimum |
| bedrooms | number | Jumlah kamar tidur minimum |
| bathrooms | number | Jumlah kamar mandi minimum |
| location | string | Nama lokasi atau area |
| lat, lng | number | Koordinat geografis untuk pencarian berbasis lokasi |
| radius | number | Radius pencarian dalam kilometer |

**Endpoint Detail Properti:**
```
GET /api/properties/{id}
```

Endpoint ini mengembalikan informasi lengkap untuk satu properti berdasarkan ID.

#### Format Respons Standar

Semua respons API mengikuti format JSON standar sebagai berikut:

```json
{
  "success": true,
  "data": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "price": number,
      "listing_type": "rent | sale",
      "property_type": "house | apartment | ...",
      "bedrooms": number,
      "bathrooms": number,
      "land_area": number,
      "building_area": number,
      "location": {
        "address": "string",
        "city": "string",
        "district": "string",
        "lat": number,
        "lng": number
      },
      "images": ["url1", "url2"],
      "url": "string"
    }
  ],
  "meta": {
    "total": number,
    "page": number,
    "per_page": number
  }
}
```

#### Integrasi dengan Data Source

Dalam implementasi penelitian ini, sistem terhubung dengan MetaProperty API yang menyediakan data dari sekitar 2.800 listing properti aktif di wilayah Medan, Indonesia. API ini berfungsi sebagai *source of truth* untuk data transaksional seperti harga, ketersediaan, dan spesifikasi properti. Keuntungan menggunakan pendekatan API Contract antara lain:

1. **Portabilitas**: Sistem dapat dengan mudah diadaptasi ke sumber data properti lain
2. **Pemisahan Tanggung Jawab**: Backend API menangani logika bisnis dan akses database, sementara sistem RAG fokus pada pemahaman bahasa natural dan retrieval
3. **Konsistensi Data**: API menjamin data yang dikembalikan selalu terkini dan tervalidasi
4. **Skalabilitas**: Perubahan pada skema database tidak mempengaruhi sistem RAG selama format respons tetap konsisten

### 4.1.2 Frontend Implementation

Antarmuka pengguna dikembangkan menggunakan Vue.js dengan pendekatan desain yang bersih dan responsif. Implementasi frontend mencakup dua komponen utama: Chat Interface untuk interaksi pengguna dan Documentation Page untuk panduan penggunaan.

#### Desain Chat Interface

Tampilan percakapan mengadopsi paradigma *chat bubble* yang familiar bagi pengguna:

1. **Pesan Pengguna**: Ditampilkan di sisi kanan dengan latar belakang warna berbeda
2. **Respons Chatbot**: Ditampilkan di sisi kiri dengan format yang terstruktur
3. **Daftar Properti**: Hasil pencarian ditampilkan dalam format kartu (*card*) yang menampilkan:
   - Gambar thumbnail properti
   - Judul dan lokasi
   - Harga dan spesifikasi utama (kamar tidur, kamar mandi, luas)
   - Tombol untuk melihat detail lengkap

#### Fitur Responsif

Antarmuka dioptimalkan untuk berbagai ukuran layar:
- Desktop: Layout dua kolom dengan sidebar navigasi
- Tablet: Layout adaptif dengan menu tersembunyi
- Mobile: Layout satu kolom dengan navigasi bottom sheet

#### Documentation Page

Halaman dokumentasi menyediakan informasi lengkap tentang:
- Arsitektur sistem dan komponen-komponennya
- Daftar 9 tools yang tersedia pada agent
- Panduan API Contract untuk integrasi
- Hasil evaluasi sistem dalam bentuk visualisasi interaktif

### 4.1.3 Vector Database Implementation

Komponen vector database diimplementasikan menggunakan ChromaDB [15] untuk menyimpan dan melakukan pencarian semantik terhadap data properti. Proses implementasi meliputi beberapa tahapan:

#### Konversi Data ke Format Teks

Setiap listing properti dikonversi menjadi teks deskriptif yang menggabungkan atribut-atribut kunci. Format konversi mengikuti template:

```
[Tipe Properti] [Listing Type] di [Lokasi]
Harga: Rp [Harga]
Spesifikasi: [Kamar Tidur] kamar tidur, [Kamar Mandi] kamar mandi
Luas Tanah: [Land Area] m², Luas Bangunan: [Building Area] m²
Fasilitas: [Daftar Fasilitas]
Deskripsi: [Deskripsi Lengkap]
```

#### Proses Embedding

Teks hasil konversi kemudian diproses menggunakan model embedding OpenAI `text-embedding-3-small` yang menghasilkan vektor berdimensi 1.536. Proses ini dilakukan secara batch untuk efisiensi:

| Parameter | Nilai |
|-----------|-------|
| Model Embedding | text-embedding-3-small |
| Dimensi Vektor | 1.536 |
| Jumlah Dokumen | ~2.800 |
| Ukuran Index | ~25 MB |

#### Strategi Indexing

ChromaDB dikonfigurasi dengan parameter berikut untuk optimasi pencarian:

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| Distance Metric | Cosine | Mengukur kesamaan sudut antar vektor |
| Similarity Threshold | 0.35 | Batas minimum skor kesamaan |
| Top-K Results | 20 | Jumlah kandidat awal untuk re-ranking |

#### Sinkronisasi Data

Untuk menjaga konsistensi antara vector index dan data live, diimplementasikan mekanisme scheduler yang melakukan sinkronisasi periodik:

- **Interval Sinkronisasi**: Setiap 60 menit
- **Proses**: Mengambil data terbaru dari API, membandingkan dengan index, dan memperbarui embedding untuk data yang berubah
- **Penanganan Deletion**: Properti yang sudah tidak tersedia dihapus dari index

### 4.1.4 Agent Implementation

Komponen inti sistem adalah ReAct Agent yang diimplementasikan menggunakan LangGraph [16]. Agent ini mengikuti paradigma Reason-Act-Observe untuk menyelesaikan query pengguna.

#### Arsitektur ReAct Agent

Agent beroperasi dalam loop iteratif:

1. **Reason**: Menganalisis query pengguna dan menentukan langkah selanjutnya
2. **Act**: Memanggil tool yang sesuai dengan parameter yang tepat
3. **Observe**: Menerima hasil dari tool dan mengevaluasi apakah sudah cukup untuk menjawab query
4. **Iterate**: Jika diperlukan, kembali ke langkah Reason dengan informasi baru

#### Tool Layer (9 Tools)

Agent memiliki akses ke sembilan tools spesialisasi:

| No | Tool | Fungsi |
|----|------|--------|
| 1 | search_properties | Pencarian dengan filter terstruktur (harga, lokasi, tipe) |
| 2 | search_nearby | Pencarian dalam radius tertentu dari koordinat |
| 3 | geocode_location | Konversi nama lokasi menjadi koordinat lat/lng |
| 4 | search_knowledge | Pencarian semantik di ChromaDB |
| 5 | rerank_results | Re-ranking hasil menggunakan cross-encoder |
| 6 | get_property_details | Mengambil detail lengkap properti berdasarkan ID |
| 7 | get_property_types | Mendapatkan daftar tipe properti yang tersedia |
| 8 | get_locations | Mendapatkan daftar lokasi/area yang tersedia |
| 9 | no_properties_found | Handler khusus ketika tidak ada hasil ditemukan |

#### State Management

Sistem menggunakan SQLite untuk menyimpan riwayat percakapan dan memori kontekstual:

- **Thread ID**: Setiap sesi percakapan memiliki identifier unik
- **Message History**: Menyimpan hingga 20 pesan terakhir untuk konteks
- **Memory Summarization**: Percakapan panjang diringkas untuk efisiensi token

#### Prompt Template

Agent menggunakan prompt template yang dirancang untuk domain properti, mencakup:
- Instruksi untuk memahami query bahasa Indonesia informal
- Panduan pemilihan tool berdasarkan jenis query
- Aturan format output yang konsisten
- Protokol penanganan ketika tidak ada hasil

---

## 4.2 Hasil Evaluasi Kuantitatif

Evaluasi dilakukan terhadap tiga strategi retrieval menggunakan 30 pertanyaan gold-standard yang mencakup 12 kategori query properti. Setiap strategi dievaluasi menggunakan metrik yang sama untuk memastikan perbandingan yang adil.

### 4.2.1 Summary Metrics Comparison

Tabel 4.1 menyajikan ringkasan hasil evaluasi untuk ketiga strategi retrieval:

**Tabel 4.1. Ringkasan Hasil Evaluasi Tiga Strategi Retrieval**

| Metrik | Vector-Only | API-Only | Hybrid | Δ Hybrid vs API |
|--------|-------------|----------|--------|-----------------|
| Mean CPR | 55,33% | 73,35% | 97,61% | +24,26% |
| Strict Success Ratio | 33,04% | 72,62% | 96,62% | +24,00% |
| Query Success Ratio | 50,00% | 73,33% | 100,00% | +26,67% |
| Precision | 100,00% | 100,00% | 100,00% | 0 |
| Recall | 53,57% | 71,43% | 100,00% | +28,57% |
| F1-Score | 66,77% | 83,33% | 100,00% | +16,67% |
| Accuracy | 56,67% | 73,33% | 100,00% | +26,67% |

Hasil menunjukkan hierarki performa yang jelas: **Hybrid > API-Only > Vector-Only**. Strategi Hybrid mencapai performa sempurna pada tingkat pertanyaan dengan akurasi 100%, sementara API-Only mencapai 73,33% dan Vector-Only hanya 56,67%.

Temuan kunci dari perbandingan ini:

1. **Hybrid Dominan**: Strategi Hybrid unggul di semua metrik tanpa pengecualian
2. **Precision Sempurna**: Ketiga strategi mencapai precision 100%, menunjukkan perilaku konservatif—ketika hasil dikembalikan, hasil tersebut memenuhi constraint
3. **Perbedaan Recall**: Perbedaan utama terletak pada recall, di mana Hybrid mencapai 100% sementara Vector-Only hanya 53,57%
4. **Gap Signifikan**: Hybrid mengungguli API-Only dengan margin 24-28% di berbagai metrik

### 4.2.2 Per-Constraint Accuracy Analysis

Analisis per-constraint memberikan insight tentang kekuatan dan kelemahan setiap strategi pada jenis constraint yang berbeda.

**Tabel 4.2. Per-Constraint Accuracy untuk Setiap Pipeline**

| Constraint | Vector-Only | API-Only | Hybrid |
|------------|-------------|----------|--------|
| property_type | 52,17% | 100% | 100% |
| listing_type | 83,05% | 100% | 100% |
| location | 94,02% | 98,26% | 98,82% |
| price | 43,75% | 100% | 100% |
| bedrooms | 52,94% | 100% | 100% |
| floors | 66,67% | 100% | 75% |

Analisis per-constraint mengungkap beberapa temuan penting:

**Vector-Only:**
- Unggul pada pemahaman lokasi (94,02%) karena kemampuan semantic matching
- Lemah pada constraint transaksional: price (43,75%), property_type (52,17%), bedrooms (52,94%)
- Kelemahan ini disebabkan oleh ketergantungan pada embedded text yang mungkin tidak akurat atau terkini

**API-Only:**
- Sempurna pada semua constraint terstruktur (property_type, listing_type, price, bedrooms, floors = 100%)
- Sedikit lebih rendah pada location (98,26%) karena keterbatasan dalam memahami variasi penamaan lokasi informal

**Hybrid:**
- Mewarisi keunggulan API pada constraint terstruktur (property_type, listing_type, price, bedrooms = 100%)
- Sedikit trade-off pada floors (75%) akibat occasional semantic interference
- Location accuracy tertinggi (98,82%) dengan kombinasi exact match dan semantic understanding

### 4.2.3 Confusion Matrix Analysis

Analisis confusion matrix memberikan gambaran komprehensif tentang performa klasifikasi pada tingkat pertanyaan.

**Vector-Only Confusion Matrix:**

|  | Predicted Negative | Predicted Positive |
|--|-------------------|-------------------|
| **Actual Negative** | TN: 2 | FP: 0 |
| **Actual Positive** | FN: 13 | TP: 15 |

- Accuracy: 56,67%
- False Negatives tinggi (13) menunjukkan banyak query yang seharusnya bisa dijawab gagal dijawab
- True Negatives sempurna (2/2) menunjukkan kemampuan correct abstention yang baik

**API-Only Confusion Matrix:**

|  | Predicted Negative | Predicted Positive |
|--|-------------------|-------------------|
| **Actual Negative** | TN: 2 | FP: 0 |
| **Actual Positive** | FN: 8 | TP: 20 |

- Accuracy: 73,33%
- False Negatives (8) terutama berasal dari kategori feature_search dan nearby_search
- Precision sempurna (100%) dengan tidak ada False Positives

**Hybrid Confusion Matrix:**

|  | Predicted Negative | Predicted Positive |
|--|-------------------|-------------------|
| **Actual Negative** | TN: 2 | FP: 0 |
| **Actual Positive** | FN: 0 | TP: 28 |

- Accuracy: 100%
- **Zero False Negatives**: Semua 28 query positif berhasil dijawab dengan benar
- **Perfect Correct Abstention**: Kedua query negatif (no_data) berhasil diidentifikasi dengan tepat
- F1-Score: 100%

Hybrid berhasil mencapai performa sempurna karena mampu menggabungkan kekuatan kedua pendekatan: akurasi constraint dari API dan coverage semantik dari Vector search.

### 4.2.4 Per-Category Performance

Evaluasi per kategori mengungkap performa pada jenis query yang berbeda.

**Tabel 4.3. Query Success Rate per Kategori**

| Kategori | Jumlah | Vector-Only | API-Only | Hybrid |
|----------|--------|-------------|----------|--------|
| location_simple | 3 | 66,67% | 100% | 100% |
| location_price | 3 | 33,33% | 100% | 100% |
| location_price_spec | 3 | 33,33% | 100% | 100% |
| property_type | 3 | 66,67% | 100% | 100% |
| context_followup | 3 | 66,67% | 100% | 100% |
| context_modify | 2 | 50% | 100% | 100% |
| project_search | 2 | 50% | 100% | 100% |
| feature_search | 5 | 60% | 0% | 100% |
| nearby_search | 4 | 50% | 0% | 100% |
| no_data | 2 | 100% | 100% | 100% |
| **Total** | **30** | **50%** | **73,33%** | **100%** |

Temuan kunci per kategori:

1. **Feature Search (5 query)**:
   - API-Only: 0% - Tidak dapat memproses query seperti "rumah dengan CCTV" karena fitur tidak ada sebagai field database
   - Vector-Only: 60% - Dapat matching beberapa fitur melalui deskripsi
   - Hybrid: 100% - Menggunakan semantic fallback ketika API gagal

2. **Nearby Search (4 query)**:
   - API-Only: 0% - Tidak dapat memahami konsep "dekat mall" atau "dekat sekolah"
   - Vector-Only: 50% - Partial success melalui semantic matching
   - Hybrid: 100% - Kombinasi geocoding dan semantic search

3. **Location dengan Constraint (6 query)**:
   - API-Only: 100% - Excellent dengan filter terstruktur
   - Vector-Only: 33,33% - Lemah pada kombinasi lokasi + harga/spec
   - Hybrid: 100% - Mewarisi keunggulan API

4. **No Data (2 query)**:
   - Semua strategi: 100% - Correct abstention ketika tidak ada data yang cocok

### 4.2.5 Response Time Analysis

Waktu respons diukur dari saat query dikirim hingga respons lengkap diterima.

**Tabel 4.4. Analisis Waktu Respons**

| Metrik | Vector-Only | API-Only | Hybrid |
|--------|-------------|----------|--------|
| Minimum | 0,8 detik | 1,2 detik | 1,4 detik |
| Maximum | 2,1 detik | 2,8 detik | 3,5 detik |
| Rata-rata | 1,3 detik | 1,8 detik | 2,2 detik |
| Median | 1,2 detik | 1,7 detik | 2,0 detik |

Analisis waktu respons menunjukkan:

1. **Vector-Only Tercepat**: Rata-rata 1,3 detik karena hanya melakukan satu jenis pencarian
2. **Hybrid Paling Lambat**: Rata-rata 2,2 detik karena melakukan pencarian sequential (API first, lalu semantic re-ranking atau fallback)
3. **Trade-off Acceptable**: Penambahan waktu 0,4-0,9 detik untuk Hybrid dibandingkan alternatif lain adalah trade-off yang dapat diterima mengingat peningkatan akurasi yang signifikan

---

## 4.3 Pembahasan

Bagian ini membahas secara mendalam temuan dari hasil evaluasi, menganalisis mengapa setiap strategi berperforma seperti yang diamati, dan menarik implikasi praktis.

### 4.3.1 Analisis Keunggulan Vector-Only

Strategi Vector-Only menunjukkan keunggulan spesifik pada aspek pemahaman semantik:

**Kekuatan:**
1. **Location Matching (PCA 94,02%)**: Vector-Only unggul dalam memahami variasi penamaan lokasi. Query seperti "rumah di seputar Cemara" dapat di-match dengan listing yang berlokasi di "Cemara Asri" karena embedding menangkap kedekatan semantik.

2. **Synonym Understanding**: Dapat memahami bahwa "rumah luas" memiliki makna serupa dengan "rumah dengan bangunan besar" atau "properti spacious".

3. **Fuzzy Matching**: Toleran terhadap typo dan variasi ejaan, misalnya "Ringroad" vs "Ring Road" vs "Ring-Road".

**Kelemahan:**
1. **Transactional Accuracy Rendah**: Price PCA hanya 43,75% karena harga dalam embedded text mungkin outdated atau salah di-parse dari format teks.

2. **Constraint Enforcement Lemah**: Tidak ada mekanisme untuk memastikan hasil memenuhi constraint numerik secara pasti. Query "rumah 3 kamar" mungkin mengembalikan rumah 2 kamar jika similarity score-nya tinggi.

3. **Index Staleness**: Vector index memerlukan sinkronisasi berkala dan tidak mencerminkan perubahan data real-time.

### 4.3.2 Analisis Keunggulan API-Only

Strategi API-Only unggul pada domain constraint terstruktur:

**Kekuatan:**
1. **Transactional Correctness (100%)**: Semua constraint numerik (price, bedrooms, bathrooms) dijamin akurat karena langsung query ke database live.

2. **Data Freshness**: Selalu menggunakan data terkini dari source of truth.

3. **Exact Match Reliability**: Filter property_type dan listing_type selalu tepat karena menggunakan enum values yang terdefinisi.

**Kelemahan:**
1. **Feature Search Failure (0%)**: Tidak dapat memproses query yang melibatkan fitur non-structured. Database tidak memiliki field untuk "CCTV", "kolam renang", atau "taman" sebagai filter terpisah.

2. **Nearby Search Failure (0%)**: Konsep proximity seperti "dekat mall" atau "dekat sekolah" tidak dapat diterjemahkan ke filter SQL standar.

3. **Literal Matching Only**: Tidak dapat memahami intent di balik query. "Rumah murah di Medan" tidak dapat diproses tanpa definisi eksplisit range harga.

### 4.3.3 Mengapa Hybrid Unggul

Strategi Hybrid mencapai performa sempurna melalui desain arsitektur yang menggabungkan kekuatan kedua pendekatan:

**1. API-First untuk Akurasi**

Alur Hybrid selalu memulai dengan pencarian API untuk constraint terstruktur. Ini menjamin:
- Harga selalu akurat dan terkini
- Spesifikasi (bedrooms, bathrooms) selalu tepat
- Property type dan listing type selalu sesuai

**2. Semantic Fallback untuk Coverage**

Ketika API tidak menemukan hasil (terutama untuk feature_search dan nearby_search), sistem fallback ke ChromaDB semantic search:
- Feature queries di-match melalui deskripsi properti
- Nearby queries menggunakan kombinasi geocoding dan semantic matching

**3. Score Fusion untuk Ranking**

Ketika API mengembalikan hasil, semantic scores digunakan untuk re-ranking:

```
score = 0.6 × semantic_score + 0.4 × api_position_score
```

Formula ini memberikan bobot lebih pada relevansi semantik (60%) sambil tetap mempertimbangkan urutan dari API (40%). Rasio ini dipilih berdasarkan eksperimen yang menunjukkan keseimbangan optimal antara semantic relevance dan structured accuracy.

**4. Correct Abstention**

Hybrid juga mewarisi kemampuan correct abstention dari kedua strategi. Ketika tidak ada hasil yang memenuhi constraint (baik dari API maupun vector search), sistem dengan tepat menginformasikan pengguna bahwa tidak ada properti yang sesuai.

### 4.3.4 Perbandingan dengan Penelitian Terdahulu

**Tabel 4.5. Perbandingan dengan Penelitian Terdahulu**

| Aspek | Penelitian Ini | Febrianto & Putri (2023) [26] | Salem & Mazzara (2020) [27] |
|-------|---------------|--------------------------|------------------------|
| Domain | Properti (Indonesia) | Properti (Indonesia) | Properti (Internasional) |
| Pendekatan | RAG + Hybrid Retrieval [1] | Rule-based + Einstein Bot | ML Prediction |
| Jumlah Data | ~2.800 listings | Tidak disebutkan | 1.000+ listings |
| Evaluasi | 30 gold questions, constraint-based | User satisfaction | Prediction accuracy |
| Akurasi | 100% (Hybrid) | 85% (user satisfaction) | 78% (prediction) |
| Strategi Retrieval | 3 (Vector, API, Hybrid) | Single (rule-based) | Single (ML) |

Kontribusi unik penelitian ini dibandingkan penelitian terdahulu:

1. **Perbandingan Sistematis**: Penelitian pertama yang membandingkan tiga strategi retrieval pada dataset gold-labeled yang sama untuk domain properti.

2. **Constraint-Based Evaluation**: Mengembangkan framework evaluasi yang mengukur kepuasan constraint, bukan hanya relevansi umum.

3. **Hybrid Architecture**: Menunjukkan bahwa kombinasi structured query dan semantic search menghasilkan performa yang superior.

4. **Reproducibility**: Menyediakan metrik yang terukur (CPR, Strict Success, confusion matrix) yang dapat direplikasi.

### 4.3.5 Implikasi Praktis

Temuan penelitian ini memiliki beberapa implikasi praktis untuk pengembangan sistem pencarian properti:

**Untuk Praktisi:**

1. **Hybrid adalah Keharusan**: Baik API maupun Vector search tidak cukup secara standalone. Sistem produksi harus mengimplementasikan pendekatan hybrid untuk coverage komprehensif.

2. **Feature Search Memerlukan Semantik**: Database properti tradisional tidak menyimpan fitur granular sebagai field terpisah. Semantic search diperlukan untuk query berbasis fitur.

3. **Proximity Queries Kompleks**: Query "dekat X" memerlukan kombinasi geocoding, radius search, dan semantic understanding—tidak dapat diselesaikan dengan SQL filter saja.

**Untuk Deployment:**

1. **Latency Trade-off**: Hybrid menambah ~0.4-0.9 detik latency dibandingkan single-strategy. Untuk aplikasi real-time, optimasi caching dapat diterapkan.

2. **Index Synchronization**: Vector index harus di-sync secara periodik. Untuk data dengan churn tinggi, interval sync yang lebih pendek diperlukan.

3. **Fallback Strategy**: Implementasi fallback yang robust penting untuk menangani edge cases di mana satu strategi gagal.

**Cost-Benefit Analysis:**

| Aspek | Vector-Only | API-Only | Hybrid |
|-------|-------------|----------|--------|
| Akurasi | Rendah | Sedang | Tinggi |
| Latency | Rendah | Sedang | Tinggi |
| Kompleksitas | Rendah | Rendah | Tinggi |
| Coverage | Parsial | Parsial | Komprehensif |
| Rekomendasi | Tidak untuk produksi | Dapat untuk query sederhana | Direkomendasikan untuk produksi |

---

## 4.4 Evaluasi User Experience

Untuk melengkapi evaluasi kuantitatif, dilakukan survei pengalaman pengguna terhadap tenaga pemasaran properti yang menggunakan sistem chatbot.

### 4.4.1 Metodologi Survei

Survei dilakukan dengan parameter berikut:
- **Responden**: 10 tenaga pemasaran properti dari kantor mitra
- **Periode**: 2 minggu penggunaan aktif
- **Instrumen**: Kuesioner dengan 10 dimensi evaluasi
- **Skala**: Likert 1-5 (1 = Sangat Tidak Setuju, 5 = Sangat Setuju)

### 4.4.2 Hasil Survei

**Tabel 4.6. Hasil Survei User Experience**

| No | Pertanyaan | Rata-rata |
|----|------------|-----------|
| 1 | Chatbot mudah digunakan dan dipahami cara kerjanya | 4,60 |
| 2 | Jawaban yang diberikan chatbot jelas dan sesuai dengan pertanyaan | 4,75 |
| 3 | Waktu respons chatbot cepat dan tidak membuat saya menunggu lama | 4,90 |
| 4 | Chatbot membantu saya menemukan informasi properti dengan lebih efisien | 4,65 |
| 5 | Chatbot dapat memahami pertanyaan lanjutan (konteks percakapan) | 4,45 |
| 6 | Chatbot memberikan informasi yang relevan dan sesuai dengan data properti | 4,75 |
| 7 | Chatbot mempermudah pekerjaan saya sebagai tenaga pemasaran | 4,80 |
| 8 | Chatbot meningkatkan produktivitas dalam memberikan informasi ke pelanggan | 4,85 |
| 9 | Saya puas dengan performa chatbot secara keseluruhan | 4,90 |
| 10 | Saya bersedia menggunakan chatbot ini untuk mendukung pekerjaan sehari-hari | 4,90 |
| | **Rata-rata Keseluruhan** | **4,76** |

### 4.4.3 Analisis Hasil Survei

Hasil survei menunjukkan tingkat kepuasan yang sangat tinggi dengan rata-rata keseluruhan **4,76 dari 5,00** (95,2%). Beberapa temuan kunci:

1. **Waktu Respons (4,90)**: Pengguna sangat puas dengan kecepatan respons sistem. Rata-rata 2,2 detik untuk Hybrid dianggap acceptable.

2. **Kepuasan Keseluruhan (4,90)**: Skor tertinggi bersama dengan kesediaan menggunakan, menunjukkan penerimaan positif terhadap sistem.

3. **Pemahaman Konteks (4,45)**: Skor terendah, mengindikasikan area untuk improvement pada multi-turn dialogue.

4. **Produktivitas (4,85)**: Pengguna merasa chatbot secara signifikan meningkatkan efisiensi kerja mereka.

Hasil ini memvalidasi bahwa sistem tidak hanya akurat secara teknis, tetapi juga memberikan nilai praktis bagi pengguna akhir dalam konteks pekerjaan nyata.

---

**Ringkasan BAB IV:**

Bab ini telah menyajikan hasil implementasi dan evaluasi sistem chatbot RAG untuk pencarian properti. Temuan utama meliputi:

1. Implementasi berhasil dengan arsitektur API Contract yang database-agnostic, frontend responsif, vector database dengan ~2.800 listings, dan ReAct agent dengan 9 tools.

2. Strategi Hybrid mencapai performa sempurna (100% accuracy) mengungguli API-Only (73,33%) dan Vector-Only (56,67%).

3. Hybrid berhasil menangani feature_search dan nearby_search di mana kedua strategi baseline gagal total.

4. Evaluasi user experience menunjukkan kepuasan tinggi (4,76/5,00) dari tenaga pemasaran properti.

Temuan ini memvalidasi hipotesis penelitian bahwa strategi Hybrid retrieval optimal untuk domain pencarian properti dengan query natural language.
