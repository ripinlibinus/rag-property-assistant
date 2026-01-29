# BAB III METODOLOGI PENELITIAN

Bab ini menjelaskan metodologi yang digunakan dalam penelitian, meliputi kerangka pemikiran, arsitektur sistem, persiapan data, implementasi tiga strategi retrieval, framework evaluasi, implementasi teknis, dan keterbatasan metodologi.

## 3.1 Kerangka Pemikiran

Penelitian ini bertujuan untuk mengembangkan dan mengevaluasi sistem chatbot AI berbasis RAG (Retrieval-Augmented Generation) untuk membantu tenaga pemasaran properti dalam menjawab query pelanggan menggunakan bahasa natural. Kerangka pemikiran penelitian diilustrasikan pada Gambar 3.1.

**Gambar 3.1. Kerangka Pemikiran Penelitian**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MASALAH PENELITIAN                           │
│  - Filter tradisional tidak memahami bahasa natural                 │
│  - Gap antara cara berpikir pengguna dan interface sistem           │
│  - Kebutuhan perbandingan strategi retrieval untuk domain properti  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SOLUSI YANG DIAJUKAN                           │
│  Chatbot RAG dengan 3 Strategi Retrieval:                           │
│  1. Vector-Only (Semantic Search)                                   │
│  2. API-Only (Structured Query)                                     │
│  3. Hybrid (Kombinasi keduanya)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         IMPLEMENTASI                                │
│  - Arsitektur ReAct Agent dengan 9 Tools                            │
│  - API Contract untuk integrasi data                                │
│  - ChromaDB untuk vector storage                                    │
│  - Score Fusion untuk hybrid ranking                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          EVALUASI                                   │
│  - 30 Gold-Labeled Questions                                        │
│  - Constraint-Based Metrics (CPR, Strict Success)                   │
│  - Confusion Matrix Analysis                                        │
│  - User Experience Survey                                           │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       OUTPUT PENELITIAN                             │
│  - Identifikasi strategi retrieval optimal                          │
│  - Framework evaluasi constraint-based                              │
│  - Sistem chatbot yang dapat diimplementasikan                      │
└─────────────────────────────────────────────────────────────────────┘
```

Alur penelitian dimulai dari identifikasi masalah pencarian properti menggunakan filter tradisional, dilanjutkan dengan perancangan solusi berbasis RAG, implementasi tiga strategi retrieval, evaluasi menggunakan metrik constraint-based, dan analisis untuk mengidentifikasi strategi optimal.

---

## 3.2 Arsitektur Sistem

### 3.2.1 High-Level Architecture

Sistem chatbot RAG yang dikembangkan terdiri dari beberapa lapisan komponen yang saling terintegrasi. Gambar 3.2 menunjukkan arsitektur tingkat tinggi sistem.

**Gambar 3.2. High-Level System Architecture**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │
│                    (Vue.js Chat Interface)                          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                              │
│                    (HTTP/JSON API Endpoint)                         │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         REACT AGENT                                 │
│              (LangGraph-based Reason-Act-Observe Loop)              │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐                   │
│  │  Reason   │ -> │    Act    │ -> │  Observe  │ -> (iterate)      │
│  └───────────┘    └───────────┘    └───────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         TOOL LAYER                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │search_properties│  │ search_nearby  │  │search_knowledge│        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │geocode_location│  │ rerank_results │  │get_prop_details│        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │get_prop_types  │  │ get_locations  │  │no_props_found  │        │
│  └────────────────┘  └────────────────┘  └────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
┌─────────────────────────────┐   ┌─────────────────────────────────┐
│      PROPERTY API           │   │         CHROMADB                │
│   (REST API - MySQL)        │   │    (Vector Database)            │
│   Source of Truth           │   │    Semantic Search              │
│   ~2,800 listings           │   │    ~2,800 embeddings            │
└─────────────────────────────┘   └─────────────────────────────────┘
```

Arsitektur ini terdiri dari lima lapisan utama:

1. **User Interface Layer**: Antarmuka pengguna berbasis Vue.js yang menyediakan tampilan chat interaktif.

2. **API Layer**: FastAPI backend yang mengekspos endpoint HTTP/JSON untuk menerima query dan mengembalikan respons.

3. **Agent Layer**: ReAct Agent berbasis LangGraph yang melakukan penalaran dan pemilihan tool.

4. **Tool Layer**: Sembilan tools spesialisasi yang menangani berbagai jenis operasi pencarian dan retrieval.

5. **Data Layer**: Dua sumber data—Property API untuk data terstruktur dan ChromaDB untuk pencarian semantik.

### 3.2.2 ReAct Agent Design

Agent diimplementasikan menggunakan paradigma ReAct (Reasoning and Acting) [16] yang memungkinkan penalaran eksplisit sebelum mengambil tindakan. Gambar 3.3 menunjukkan alur kerja ReAct Agent.

**Gambar 3.3. ReAct Agent Flow**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUERY                                  │
│         "Carikan rumah 3 kamar di Cemara harga 1M-an"              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      THOUGHT (Reasoning)                            │
│  "User mencari rumah dengan spesifikasi:                            │
│   - Bedrooms: 3                                                     │
│   - Location: Cemara                                                │
│   - Price range: sekitar 1 miliar                                   │
│   Saya perlu menggunakan search_properties dengan filter ini"       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ACTION (Tool Call)                           │
│  Tool: search_properties                                            │
│  Parameters: {                                                      │
│    "location": "cemara",                                            │
│    "bedrooms": 3,                                                   │
│    "min_price": 800000000,                                          │
│    "max_price": 1200000000,                                         │
│    "listing_type": "sale"                                           │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     OBSERVATION (Tool Result)                       │
│  [Property 1: Rumah Cemara Asri Tipe 120, 3KT, Rp 1.05M]           │
│  [Property 2: Rumah Cemara Indah Tipe 100, 3KT, Rp 980jt]          │
│  [Property 3: ...]                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      THOUGHT (Evaluation)                           │
│  "Saya mendapatkan hasil yang sesuai dengan kriteria user.          │
│   Ada beberapa opsi yang dapat saya presentasikan."                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FINAL ANSWER                                  │
│  "Berikut rumah 3 kamar di area Cemara dengan harga sekitar 1M:     │
│   1. Rumah Cemara Asri Tipe 120 - Rp 1,05 Miliar                   │
│   2. Rumah Cemara Indah Tipe 100 - Rp 980 Juta                     │
│   ..."                                                              │
└─────────────────────────────────────────────────────────────────────┘
```

Implementasi menggunakan LangGraph yang menyediakan:
- **State Management**: Menyimpan konteks percakapan dan hasil intermediate
- **Graph-based Flow**: Mengelola transisi antar state (reason, act, observe)
- **Tool Binding**: Menghubungkan agent dengan tools yang tersedia
- **Memory Integration**: Mengintegrasikan dengan sistem memori untuk konteks multi-turn

### 3.2.3 Tool Layer (9 Tools)

Agent memiliki akses ke sembilan tools yang dirancang khusus untuk domain pencarian properti:

**Tabel 3.1. Daftar Agent Tools**

| No | Tool Name | Fungsi | Parameter Utama |
|----|-----------|--------|-----------------|
| 1 | search_properties | Pencarian properti dengan filter terstruktur | location, price_range, bedrooms, property_type, listing_type |
| 2 | search_nearby | Pencarian dalam radius dari titik koordinat | lat, lng, radius_km, property_type |
| 3 | geocode_location | Konversi nama lokasi ke koordinat geografis | location_name |
| 4 | search_knowledge | Pencarian semantik di ChromaDB | query_text, top_k |
| 5 | rerank_results | Re-ranking hasil menggunakan semantic scores | results, query |
| 6 | get_property_details | Mengambil detail lengkap properti | property_id |
| 7 | get_property_types | Daftar tipe properti yang tersedia | - |
| 8 | get_locations | Daftar lokasi/area yang tersedia | - |
| 9 | no_properties_found | Handler untuk kondisi tidak ada hasil | reason |

**Strategi Pemilihan Tool:**

Agent mengikuti strategi routing berdasarkan karakteristik query:

1. **Constraint-heavy queries** (harga, kamar, tipe) → `search_properties`
2. **Proximity queries** ("dekat mall", "sekitar sekolah") → `geocode_location` + `search_nearby`
3. **Feature queries** ("dengan CCTV", "ada kolam renang") → `search_knowledge`
4. **Detail queries** ("info lengkap properti X") → `get_property_details`
5. **Exploratory queries** ("tipe properti apa saja?") → `get_property_types` atau `get_locations`

### 3.2.4 Data Sources

Sistem menggunakan dua sumber data yang saling melengkapi:

**Tabel 3.2. Spesifikasi Data Sources**

| Aspek | Property API (MySQL via REST) | ChromaDB (Vector Store) |
|-------|-------------------------------|-------------------------|
| Fungsi | Source of truth untuk data transaksional | Pencarian semantik |
| Jumlah Data | ~2.800 listings aktif | ~2.800 embeddings |
| Update | Real-time | Periodik (setiap 60 menit) |
| Query Type | Structured filters | Semantic similarity |
| Keunggulan | Akurasi constraint 100% | Pemahaman natural language |
| Keterbatasan | Tidak memahami semantik | Data mungkin tidak terkini |

**Property API** berfungsi sebagai source of truth untuk semua data transaksional:
- Harga dan ketersediaan yang selalu akurat
- Filter terstruktur untuk constraint numerik
- Pagination dan sorting hasil

**ChromaDB** [15] menyediakan kemampuan pencarian semantik:
- Matching berdasarkan similarity vektor
- Pemahaman sinonim dan variasi bahasa
- Pencarian berdasarkan deskripsi dan fitur

---

## 3.3 Persiapan Data

### 3.3.1 Pengumpulan Data

Data properti diperoleh melalui integrasi dengan MetaProperty API yang menyediakan akses ke listing properti dari kantor-kantor properti mitra di wilayah Medan, Indonesia. Proses pengumpulan data dilakukan secara otomatis melalui API endpoint yang telah disediakan.

**Karakteristik Dataset:**

| Atribut | Nilai |
|---------|-------|
| Jumlah Total Listing | ~2.800 |
| Wilayah Coverage | Medan dan sekitarnya |
| Tipe Properti | Rumah, Apartemen, Ruko, Tanah, Gudang |
| Listing Type | Dijual (Sale), Disewa (Rent) |
| Periode Data | Aktif (tersedia untuk transaksi) |

**Atribut Data yang Dikumpulkan:**

- **Identifikasi**: ID unik, judul, URL listing
- **Harga**: Harga jual/sewa, periode sewa (jika applicable)
- **Spesifikasi**: Kamar tidur, kamar mandi, lantai, luas tanah, luas bangunan
- **Lokasi**: Alamat lengkap, kota, kecamatan, koordinat GPS
- **Deskripsi**: Teks deskripsi, fasilitas, keunggulan
- **Media**: URL gambar properti
- **Metadata**: Tanggal listing, status ketersediaan

### 3.3.2 Data Cleaning dan Normalisasi

Data yang diperoleh dari API melewati proses ETL (Extract, Transform, Load) untuk memastikan konsistensi:

**Proses Cleaning:**

1. **Normalisasi Harga**: Mengkonversi format harga yang bervariasi ("1M", "1 Miliar", "1.000.000.000") ke format numerik standar

2. **Standardisasi Lokasi**: Menyeragamkan penamaan lokasi (case normalization, penghapusan karakter khusus)

3. **Validasi Koordinat**: Memverifikasi bahwa koordinat GPS berada dalam batas geografis yang valid

4. **Penanganan Missing Values**:
   - Numerik: Default ke 0 atau null yang teridentifikasi
   - Teks: Default ke string kosong
   - Koordinat: Geocoding dari alamat jika tidak tersedia

5. **Deduplikasi**: Identifikasi dan penanganan listing duplikat berdasarkan kombinasi judul + lokasi + harga

### 3.3.3 Vector Index Preparation

Proses persiapan vector index melibatkan konversi data properti menjadi representasi vektor yang dapat dicari secara semantik.

**Gambar 3.4. Data Preparation Workflow**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Property Data  │ --> │ Text Conversion │ --> │   Embedding     │
│   (from API)    │     │   (Template)    │     │  (OpenAI API)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │    ChromaDB     │
                                                │   Vector Store  │
                                                └─────────────────┘
```

**Template Konversi Teks:**

Setiap properti dikonversi ke format teks menggunakan template berikut:

```
{property_type} {listing_type} di {location}
Harga: Rp {price}
Spesifikasi: {bedrooms} kamar tidur, {bathrooms} kamar mandi, {floors} lantai
Luas: Tanah {land_area} m², Bangunan {building_area} m²
Fasilitas: {facilities}
{description}
```

**Parameter Embedding:**

| Parameter | Nilai |
|-----------|-------|
| Model | text-embedding-3-small (OpenAI) |
| Dimensi | 1.536 |
| Batch Size | 100 dokumen per request |
| Total Embeddings | ~2.800 |

**Konfigurasi ChromaDB:**

| Parameter | Nilai |
|-----------|-------|
| Collection Name | properties |
| Distance Function | Cosine Similarity |
| Persistence | SQLite + Parquet files |
| Metadata Fields | property_type, listing_type, location, price, id |

### 3.3.4 Gold Standard Questions

Untuk evaluasi yang objektif, dikembangkan set 30 pertanyaan gold-standard yang mencakup berbagai jenis query properti.

**Tabel 3.3. Kategori Gold Standard Questions**

| Kategori | Jumlah | Contoh Pertanyaan |
|----------|--------|-------------------|
| location_simple | 3 | "Carikan rumah dijual di daerah Cemara" |
| location_price | 3 | "Carikan rumah di Cemara harga 1M-an" |
| location_price_spec | 3 | "Rumah dijual Ringroad dibawah 800jt 3 kamar" |
| property_type | 3 | "Apakah ada ruko disewakan di Krakatau?" |
| context_followup | 3 | "Apakah masih ada pilihan lain?" |
| context_modify | 2 | "Pilihan lain, tapi yang 3 lantai?" |
| project_search | 2 | "Cari rumah di Citraland Bagya City" |
| feature_search | 5 | "Carikan rumah dengan fasilitas CCTV" |
| nearby_search | 4 | "Cari rumah dekat mall di Medan" |
| no_data | 2 | "Apakah ada gudang di KIM?" |
| **Total** | **30** | |

**Annotation Protocol:**

Setiap pertanyaan dilengkapi dengan anotasi:
1. **Expected Constraints**: Daftar constraint yang harus dipenuhi (location, price, bedrooms, dll.)
2. **Expected Result Status**: has_data atau no_data
3. **Ground Truth Verification**: Verifikasi melalui API untuk memastikan kebenaran expected result

---

## 3.4 Implementasi Tiga Strategi Retrieval

### 3.4.1 Vector-Only Pipeline

Strategi Vector-Only melakukan pencarian murni menggunakan semantic similarity di ChromaDB tanpa melibatkan API terstruktur.

**Gambar 3.5. Vector-Only Pipeline**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Query    │ --> │    Embedding    │ --> │  ChromaDB       │
│  (Natural Text) │     │   Generation    │     │ Similarity      │
└─────────────────┘     └─────────────────┘     │    Search       │
                                                └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Post-Filtering │
                                                │  (Metadata)     │
                                                └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │   Top-K         │
                                                │   Results       │
                                                └─────────────────┘
```

**Alur Proses:**

1. **Query Embedding**: Query pengguna dikonversi menjadi vektor menggunakan model embedding yang sama (text-embedding-3-small)

2. **Similarity Search**: ChromaDB mencari K dokumen terdekat berdasarkan cosine similarity

3. **Post-Filtering**: Filter opsional berdasarkan metadata (property_type, listing_type) jika teridentifikasi dari query

4. **Result Ranking**: Hasil diurutkan berdasarkan similarity score

**Konfigurasi:**

| Parameter | Nilai |
|-----------|-------|
| Top-K | 20 (pre-filter) |
| Final Results | 10 |
| Similarity Threshold | 0.35 |
| Post-Filter Fields | property_type, listing_type |

**Kekuatan:**
- Memahami variasi bahasa dan sinonim
- Toleran terhadap typo dan informal language
- Dapat matching berdasarkan deskripsi dan fitur

**Kelemahan:**
- Tidak menjamin akurasi constraint numerik
- Data mungkin tidak terkini (index lag)
- Tidak dapat melakukan exact match pada filter

### 3.4.2 API-Only Pipeline

Strategi API-Only mengkonversi query natural language menjadi parameter filter terstruktur untuk query ke Property API [18].

**Gambar 3.6. API-Only Pipeline**

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Query    │ --> │    LLM Parse    │ --> │   JSON Filter   │
│  (Natural Text) │     │   (Extract      │     │   Generation    │
│                 │     │   Parameters)   │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  Property API   │
                                                │    Query        │
                                                └─────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │   Structured    │
                                                │    Results      │
                                                └─────────────────┘
```

**Alur Proses:**

1. **Parameter Extraction**: LLM mengekstrak parameter pencarian dari query natural language:
   - Location: nama area/lokasi
   - Price Range: min_price, max_price
   - Specifications: bedrooms, bathrooms, floors
   - Type: property_type, listing_type

2. **JSON Filter Construction**: Parameter dikompilasi menjadi JSON filter object

3. **API Query**: Filter dikirim ke Property API

4. **Result Processing**: Hasil dari API langsung dikembalikan dengan urutan dari API

**Contoh Konversi:**

Query: "Carikan rumah 3 kamar di Cemara harga di bawah 1 Miliar"

```json
{
  "location": "cemara",
  "bedrooms": 3,
  "max_price": 1000000000,
  "listing_type": "sale",
  "property_type": "house"
}
```

**Kekuatan:**
- Akurasi 100% pada constraint terstruktur
- Data selalu terkini (live database)
- Performa query cepat

**Kelemahan:**
- Tidak memahami query berbasis fitur (CCTV, kolam renang)
- Tidak memahami konsep proximity (dekat mall)
- Memerlukan mapping exact untuk parameter

### 3.4.3 Hybrid Pipeline

Strategi Hybrid mengkombinasikan kedua pendekatan dengan strategi sequential dan fallback.

**Gambar 3.7. Hybrid Pipeline (Sequential with Fallback)**

```
┌─────────────────┐
│   User Query    │
└─────────────────┘
        │
        ▼
┌─────────────────┐
│  API Search     │ ──────────────────────────────┐
│  (Structured)   │                               │
└─────────────────┘                               │
        │                                         │
        ▼                                         │
   ┌─────────┐                                    │
   │ Results │                                    │
   │   > 0?  │                                    │
   └─────────┘                                    │
    │       │                                     │
   Yes      No                                    │
    │       │                                     │
    ▼       ▼                                     │
┌───────┐ ┌─────────────────┐                    │
│Semantic│ │ChromaDB Semantic│                    │
│Rerank  │ │   Fallback      │                    │
└───────┘ └─────────────────┘                    │
    │             │                               │
    ▼             ▼                               │
┌─────────────────────────────────────────────────┘
│              Score Fusion                       │
│   score = 0.6 × semantic + 0.4 × api_position   │
└─────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────┐
│  Final Ranked   │
│    Results      │
└─────────────────┘
```

**Alur Proses:**

1. **API Search First**: Sistem selalu memulai dengan pencarian API terstruktur untuk constraint yang dapat diidentifikasi

2. **Conditional Branching**:
   - Jika API mengembalikan hasil → lanjut ke semantic re-ranking
   - Jika API tidak mengembalikan hasil → fallback ke ChromaDB semantic search

3. **Semantic Re-ranking**: Untuk hasil dari API, semantic scores dihitung dan digabungkan dengan posisi API

4. **Score Fusion**: Skor final dihitung dengan formula:

```
score = α × semantic_score + β × api_position_score
```

Di mana:
- α = 0.6 (bobot semantic relevance)
- β = 0.4 (bobot API position)
- api_position_score = 1 - (position / total_results)

**Rasional Pemilihan Bobot:**

Bobot 60:40 dipilih berdasarkan eksperimen yang menunjukkan:
- Semantic relevance lebih penting untuk user satisfaction
- API position menjamin hasil memenuhi constraint terstruktur
- Kombinasi ini memberikan keseimbangan optimal

**Keunggulan Hybrid:**

1. **Transactional Accuracy**: Constraint numerik dijamin akurat dari API
2. **Semantic Coverage**: Feature dan proximity queries ditangani oleh semantic search
3. **Relevance Ranking**: Re-ranking meningkatkan kualitas urutan hasil
4. **Fallback Safety**: Tidak mengembalikan hasil kosong jika salah satu strategi gagal

---

## 3.5 Framework Evaluasi

### 3.5.1 Constraint-Based Metrics

Evaluasi menggunakan metrik berbasis constraint yang mengukur sejauh mana hasil memenuhi kriteria yang dispesifikasikan dalam query.

**Per-Constraint Accuracy (PCA)**

Untuk setiap listing yang dikembalikan, PCA mengukur proporsi constraint yang terpenuhi:

```
PCA_i = (Jumlah constraint terpenuhi) / (Jumlah total constraint yang applicable)
```

Contoh:
- Query: "rumah 3 kamar harga max 1M di Cemara"
- Constraints: {bedrooms ≥ 3, price ≤ 1M, location = Cemara, property_type = house}
- Listing hasil: {bedrooms: 3, price: 950jt, location: Cemara Asri, type: house}
- PCA = 4/4 = 100%

**Strict Success**

Binary indicator apakah listing memenuhi SEMUA constraint:

```
Strict_Success_i = 1 jika PCA_i = 100%, else 0
```

**Constraint Pass Ratio (CPR)**

Rasio listing yang memenuhi semua constraint dari total listing yang dikembalikan:

```
CPR = (Σ Strict_Success_i) / K
```

Di mana K = jumlah listing yang dikembalikan

**Tabel 3.4. Definisi Metrik Evaluasi**

| Metrik | Definisi |
|--------|----------|
| PCA | Rasio constraint terpenuhi untuk satu listing |
| Strict Success | Listing dengan PCA = 100% |
| Strict Success Ratio | Proporsi Strict Success dari semua hasil |
| CPR | Rata-rata Strict Success per query |
| Mean CPR | Rata-rata CPR across all queries |
| Query Success Rate | Persentase query dengan CPR ≥ threshold (T=0.60) |

### 3.5.2 Question-Level Evaluation

Evaluasi tingkat pertanyaan menggunakan confusion matrix untuk mengukur performa klasifikasi.

**Ground Truth (GT):**
- Positive: API mengembalikan hasil untuk gold constraints
- Negative: API tidak mengembalikan hasil (no matching properties)

**Prediction (Pred):**
- Positive: Bot mengembalikan listings DAN CPR ≥ T
- Negative: Bot menyatakan "no result" ATAU CPR < T

**Confusion Matrix Components:**

| | Predicted Negative | Predicted Positive |
|--|-------------------|-------------------|
| **Actual Negative** | TN (Correct Abstention) | FP (False Alarm) |
| **Actual Positive** | FN (Missed Opportunity) | TP (Correct Answer) |

**Derived Metrics:**

```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2 × (Precision × Recall) / (Precision + Recall)
Accuracy = (TP + TN) / (TP + TN + FP + FN)
```

### 3.5.3 Evaluation Protocol

**Sequential Conversation Protocol:**

Evaluasi dilakukan menggunakan protokol percakapan sekuensial:

1. Setiap pipeline diinisialisasi dengan thread_id unik
2. Pertanyaan diproses secara berurutan (1-30)
3. Konteks percakapan dipertahankan untuk kategori context_followup dan context_modify
4. Hasil dicatat per pertanyaan

**Ground Truth Verification:**

Untuk setiap properti yang dikembalikan:
1. Ekstrak property_id dari hasil
2. Query API untuk mendapatkan data aktual
3. Bandingkan atribut dengan gold constraints
4. Hitung PCA berdasarkan data API (bukan hasil parsing teks)

**Reproducibility Measures:**

| Aspek | Implementasi |
|-------|--------------|
| LLM Temperature | 0 (deterministic) |
| Random Seed | Fixed per experiment |
| Evaluation Script | Versioned di repository |
| Gold Questions | Stored di data/gold_questions.xlsx |

---

## 3.6 Implementasi Teknis

### 3.6.1 Hardware Specifications

Sistem di-deploy pada infrastruktur cloud dengan spesifikasi:

**Tabel 3.5. Spesifikasi Hardware**

| Komponen | Spesifikasi |
|----------|-------------|
| Platform | Cloud Virtual Private Server (VPS) |
| CPU | 4 vCPU cores |
| RAM | 8 GB |
| Storage | 100 GB SSD |
| Network | 1 Gbps |
| OS | Ubuntu 22.04 LTS |

### 3.6.2 Software Stack

**Tabel 3.6. Software Dependencies**

| Komponen | Versi | Fungsi |
|----------|-------|--------|
| Python | 3.11 | Runtime environment |
| FastAPI | 0.110.x | HTTP/JSON API endpoint |
| LangChain | 0.3.x | Agent orchestration |
| LangGraph | 0.2.x | ReAct agent state management |
| ChromaDB | 0.5.x | Vector storage |
| OpenAI API | - | LLM (GPT-4o-mini) & embeddings |
| SQLAlchemy | 2.0.x | Database ORM |
| Vue.js | 3.x | Frontend framework |
| Docker | 24.x | Containerization |

### 3.6.3 Hyperparameters

**Tabel 3.7. System Hyperparameters**

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| LLM Model | GPT-4o-mini | Model inference |
| Temperature | 0 | Output deterministik |
| Embedding Model | text-embedding-3-small | 1536 dimensi |
| Vector Search k | limit × 2 | Pre-fetch untuk re-ranking |
| Similarity Threshold | 0.35 | Minimum cosine similarity |
| Max Results | 10 | Properti per query |
| CPR Threshold (T) | 0.60 | Threshold query success |
| Semantic Weight (α) | 0.60 | Hybrid score fusion |
| API Position Weight (β) | 0.40 | Hybrid score fusion |
| Sync Interval | 60 menit | ChromaDB sync period |
| Memory Window | 20 messages | Konteks percakapan |

**Justifikasi Pemilihan Nilai:**

1. **Temperature = 0**: Memastikan reproducibility dan konsistensi hasil
2. **Similarity Threshold = 0.35**: Dipilih untuk balance antara precision dan recall pada semantic search
3. **CPR Threshold = 0.60**: Dengan max 10 hasil, minimal 6 harus correct untuk dianggap successful
4. **Score Fusion 60:40**: Eksperimen menunjukkan bobot ini optimal untuk kombinasi relevance dan constraint satisfaction

---

## 3.7 Keterbatasan Metodologi

Penelitian ini memiliki beberapa keterbatasan metodologis yang perlu diakui:

### 3.7.1 Gold Set Size

Dataset evaluasi terdiri dari 30 pertanyaan yang mencakup 12 kategori. Meskipun dirancang untuk representatif, ukuran ini membatasi:
- Statistical power untuk analisis subgroup yang detail
- Generalisasi ke variasi query yang lebih luas
- Identifikasi edge cases yang jarang

**Mitigasi:** Pertanyaan dipilih secara purposive untuk mencakup spektrum query yang umum dalam konteks properti Indonesia.

### 3.7.2 Single Market Focus

Evaluasi dilakukan pada data properti dari wilayah Medan, Indonesia. Hasil mungkin tidak sepenuhnya transferable ke:
- Pasar properti dengan karakteristik berbeda
- Bahasa dan terminologi regional lain
- Range harga dan spesifikasi yang berbeda

**Mitigasi:** Arsitektur API Contract memungkinkan adaptasi ke market lain dengan konfigurasi minimal.

### 3.7.3 Index Freshness

Vector index disinkronisasi setiap 60 menit, menimbulkan potensi lag antara:
- Data live di API
- Data di ChromaDB

**Mitigasi:** Verifikasi final selalu menggunakan API sebagai source of truth. Vector search digunakan untuk discovery, bukan sebagai final arbiter.

### 3.7.4 No User Study for Comparison

Evaluasi fokus pada metrik objektif (constraint satisfaction) tanpa:
- Studi usability dengan pengguna akhir untuk perbandingan antar strategi
- Pengukuran SUS (System Usability Scale) per strategi
- Task completion time comparison

**Mitigasi:** Survei UX dilakukan untuk sistem final (Hybrid), memberikan validasi penerimaan pengguna.

### 3.7.5 LLM Dependency

Sistem bergantung pada OpenAI API untuk:
- Inference (GPT-4o-mini)
- Embedding generation (text-embedding-3-small)

Hal ini menimbulkan:
- Ketergantungan pada layanan eksternal
- Variabilitas biaya operasional
- Potensi perubahan behavior model di masa depan

**Mitigasi:** Arsitektur modular memungkinkan penggantian provider LLM jika diperlukan.

---

**Ringkasan BAB III:**

Bab ini telah menjelaskan metodologi penelitian secara komprehensif, meliputi:

1. **Kerangka Pemikiran**: Alur dari identifikasi masalah hingga output penelitian
2. **Arsitektur Sistem**: Desain berlapis dengan ReAct Agent, 9 tools, dan dual data sources
3. **Persiapan Data**: ETL pipeline dan gold standard questions
4. **Tiga Strategi Retrieval**: Vector-Only, API-Only, dan Hybrid dengan score fusion
5. **Framework Evaluasi**: Metrik constraint-based dan confusion matrix analysis
6. **Implementasi Teknis**: Hardware, software stack, dan hyperparameters
7. **Keterbatasan**: Acknowledged limitations dan mitigasi yang dilakukan

Metodologi ini dirancang untuk memungkinkan perbandingan yang adil antar strategi dan menghasilkan temuan yang reproducible.
