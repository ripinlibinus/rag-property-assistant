**RIPIN**

**2602567105**

![BINUS Graduate Program \| BINUS
MUSEUM](media/image1.png){width="1.968503937007874in"
height="1.7363615485564305in"}

**PROGRAM STUDI MAGISTER TEKNIK INFORMATIKA**

**BINUS GRADUATE PROGRAM**

**UNIVERSITAS BINA NUSANTARA**

**JAKARTA**

**TAHUN**

**2025**

PERANCANGAN CHATBOT AI UNTUK ASISTEN VIRTUAL AGEN PROPERTI

**RIPIN**

**2602567105**

![BINUS Graduate Program \| BINUS
MUSEUM](media/image1.png){width="1.968503937007874in"
height="1.7363615485564305in"}

Tesis

Sebagai Salah Satu Syarat untuk Memperoleh Gelar

*Master Teknik Infomatika*

pada

**PRORGRAM STUDI MAGISTER TEKNIK INFOMATIKA**

**BINUS GRADUATE PROGRAM**

**UNIVERSITAS BINA NUSANTARA**

**JAKARTA**

**TAHUN**

**2025**

# HALAMAN PERNYATAAN 

Saya, Ripin, 2602567105 menyatakan dengan sebenar-benarnya bahwa tesis
saya berjudul Perancangan Chatbot AI Untuk Asisten Virtual Agen Properti
adalah merupakan gagasan dan hasil penelitian saya sendiri dengan
bimbingan Dosen Pembimbing.

Saya juga menyatakan dengan sebenarnya bahwa isi tesis ini tidak
merupakan jiplakan dan bukan pula dari karya orang lain, kecuali kutipan
dari literatur dan atau hasil wawancara tertulis yang saya acu dan telah
saya sebutkan di Daftar Acuan.

Demikian pernyataan ini saya buat dengan sebenarnya dan saya bersedia
menerima sanksi apabila ternyata saya ini tidak benar.

*I, Ripin, 2602567105 truly acknowledge that my thesis with title
Designing an AI Chatbot as a Virtual Assistant for Property Agents is my
concept and project result with guidance from supervisor.*

*I, also truly acknowledge that content of this thesis is not copied and
not from another people work, except my citation from literature or
written interview result and already write in reference list and
bibliography list.*

*That's my acknowledge were truly made and if in reality this
acknowledge weren't true, I am willing sanction.*

Jakarta, 15 Februari 2025

Yang menyatakan

Ripin\
2602567105

  ------------------------------------------------------------------------
  Judul Tesis       :   Perancangan Chatbot AI Untuk Asisten Virtual Agen
                        Properti
  ----------------- --- --------------------------------------------------
  Nama Mahasiswa    :   Ripin

  NIM               :   2602567105
  ------------------------------------------------------------------------

![](media/image2.jpeg){width="2.0in" height="2.3958333333333335in"}

Dibimbing oleh:

+--------------------------------------------------+
| Dr. Suryadiputra Liawatimena, S.Kom,             |
| PgDip.App.Sci                                    |
|                                                  |
| D1026                                            |
+==================================================+

# [PERNYATAAN]{.underline} 

***STATEMENT***

Dengan ini saya,

  ------------------------------------------------------------------------
  Nama          :   Ripin
  ------------- --- ------------------------------------------------------
  NIM           :   2602567105

  Judul Tesis   :   Perancangan Chatbot AI Untuk Asisten Virtual Agen
                    Properti
  ------------------------------------------------------------------------

Memberikan kepada Universitas Bina Nusantara hak non-eksklusif untuk
menyimpan, memperbanyak, dan menyebarluaskan tesis karya saya, secara
keseluruhan atau hanya sebagian atau hanya ringkasannya saja, dalam
bentuk format tercetak dan atau elektronik.

Menyatakan bahwa saya, akan mempertahankan hak *exclusive* saya, untuk
menggunakan seluruh atau sebagian isi tesis saya, guna pengembangan
karya di masa depan, misalnya bentuk artikel, buku, perangkat lunak,
ataupun sistem informasi.

*Hereby grant to my school, Bina Nusantara University, the non-exclusive
right to archive, reproduce, and distribute my thesis, in whole or in
part, whether in the form of printed and electronic formats.*

*I acknowledge that I retain exclusive rights of my thesis by using all
or part of it in the future work or outputs, such as article, book,
software, and information system.*

Jakarta, 27 Agustus 2025

Ripin\
2602567105

# PRAKATA

Puji syukur penulis panjatkan ke hadirat Tuhan Yang Maha Esa, karena
atas rahmat dan karunia-Nya penulis dapat menyelesaikan tesis yang
berjudul *"Perancangan Chatbot AI untuk Asisten Virtual Agen Properti"*.
Tesis ini dapat terselesaikan berkat dukungan dan bantuan dari berbagai
pihak. Oleh karena itu, penulis ingin menyampaikan ucapan terima kasih
yang sebesar-besarnya kepada:

1.  Dr. Suryadiputra Liawatimena, S.Kom., PgDip.App.Sci, selaku dosen
    pembimbing yang telah memberikan bimbingan, arahan, serta motivasi
    selama proses penyusunan tesis ini.

2.  Seluruh dosen dan staf Program Studi Magister Teknik Informatika,
    Universitas Bina Nusantara, yang telah memberikan ilmu dan
    pengalaman berharga selama masa perkuliahan.

3.  Rekan-rekan mahasiswa angkatan 2024--2025 yang telah memberikan
    semangat, diskusi, dan inspirasi selama proses studi.

4.  Keluarga tercinta yang senantiasa memberikan doa, dukungan moral,
    dan motivasi tanpa henti sehingga penulis mampu menyelesaikan studi
    ini dengan baik.

Penulis menyadari bahwa tesis ini masih jauh dari sempurna. Oleh karena
itu, kritik dan saran yang membangun sangat diharapkan demi perbaikan di
masa yang akan datang. Semoga karya ilmiah ini dapat memberikan manfaat,
baik bagi dunia akademik maupun bagi industri properti, khususnya dalam
penerapan teknologi kecerdasan buatan untuk mendukung kinerja tenaga
pemasaran.

Jakarta, 27 Agustus 2025

Ripin\
2602567105

# ABSTRAK

Perkembangan industri properti di Indonesia yang semakin dinamis
menuntut adanya inovasi teknologi untuk mendukung efisiensi kerja tenaga
pemasaran, khususnya dalam penyediaan informasi yang akurat dan
real-time kepada calon pembeli. Penelitian ini bertujuan merancang dan
mengimplementasikan chatbot berbasis kecerdasan buatan dengan pendekatan
*Retrieval-Augmented Generation (RAG)* sebagai asisten virtual bagi agen
properti. Metodologi yang digunakan mencakup analisis kebutuhan,
perancangan sistem menggunakan Laravel sebagai *backend*, React.js
sebagai *frontend*, MySQL untuk penyimpanan data terstruktur, serta
integrasi dengan ChromaDB sebagai *vector database* dan OpenAI API
melalui LangChain sebagai penghubung. Dataset penelitian diperoleh dari
beberapa kantor properti yang tergabung dalam Asosiasi Real Estate
Broker Indonesia (AREBI), yang kemudian dinormalisasi dan dikonversi
menjadi *vector embeddings* untuk mendukung pencarian semantik.

Hasil penelitian menunjukkan bahwa chatbot mampu memberikan jawaban
dengan tingkat akurasi 93,3% dari 30 pertanyaan uji, waktu respons
rata-rata 1,7 detik, dan memperoleh tingkat kepuasan pengguna 4,65 dari
skala 5 berdasarkan survei terhadap tenaga pemasaran. Evaluasi sistem
juga menunjukkan keunggulan dalam penyajian informasi real-time serta
penurunan risiko kesalahan data dibandingkan metode manual. Simpulan
dari penelitian ini adalah bahwa penerapan chatbot AI berbasis RAG dapat
meningkatkan efisiensi, akurasi, dan produktivitas tenaga pemasaran
properti, sekaligus memberikan kontribusi nyata bagi adopsi teknologi
kecerdasan buatan dalam industri properti di Indonesia.

**Kata Kunci:** Chatbot, Artificial Intelligence, Retrieval-Augmented
Generation, LangChain, Industri Properti

*Abstract*

*The rapid development of Indonesia's property industry requires
technological innovation to support the efficiency of marketing agents,
particularly in providing accurate and real-time information to
prospective buyers. This study aims to design and implement an
artificial intelligence--based chatbot using the Retrieval-Augmented
Generation (RAG) approach as a virtual assistant for property agents.
The methodology includes needs analysis, system design using Laravel as
the backend, React.js as the frontend, MySQL for structured data
storage, and integration with ChromaDB as a vector database and the
OpenAI API via LangChain as a framework. The dataset was collected from
several property offices under the Indonesian Real Estate Broker
Association (AREBI), normalized, and converted into vector embeddings to
support semantic search.*

*The results indicate that the chatbot achieved an accuracy rate of
93.3% from 30 test questions, an average response time of 1.7 seconds,
and a user satisfaction score of 4.65 out of 5 based on a survey with
marketing agents. System evaluation also revealed advantages in
delivering real-time information and reducing data errors compared to
manual methods. In conclusion, the implementation of an AI-based RAG
chatbot can significantly improve the efficiency, accuracy, and
productivity of property marketing agents while contributing to the
adoption of artificial intelligence technology in Indonesia's property
industry.*

***Keywords:** Chatbot, Artificial Intelligence, Retrieval-Augmented
Generation, LangChain, Property Industry*

# DAFTAR ISI

[HALAMAN PERNYATAAN [iii](#halaman-pernyataan)](#halaman-pernyataan)

[PERNYATAAN [v](#pernyataan)](#pernyataan)

[PRAKATA [vi](#prakata)](#prakata)

[ABSTRAK [vii](#abstrak)](#abstrak)

[DAFTAR ISI [ix](#daftar-isi)](#daftar-isi)

[DAFTAR TABEL [xi](#daftar-tabel)](#daftar-tabel)

[DAFTAR GAMBAR [xi](#daftar-gambar)](#daftar-gambar)

[DAFTAR LAMPIRAN [xi](#daftar-lampiran)](#daftar-lampiran)

[BAB I PENDAHULUAN [1](#bab-i-pendahuluan)](#bab-i-pendahuluan)

[1.1. Latar Belakang [1](#latar-belakang)](#latar-belakang)

[1.2. Perumusan Masalah [2](#perumusan-masalah)](#perumusan-masalah)

[1.3. Tujuan Penelitian [2](#tujuan-penelitian)](#tujuan-penelitian)

[1.4. Manfaat Penelitian [2](#manfaat-penelitian)](#manfaat-penelitian)

[1.5. Ruang Lingkup Penelitian
[3](#ruang-lingkup-penelitian)](#ruang-lingkup-penelitian)

[BAB II TINJAUAN PUSTAKA
[5](#bab-ii-tinjauan-pustaka)](#bab-ii-tinjauan-pustaka)

[2.1. Artificial Intelligence (AI)
[5](#artificial-intelligence-ai)](#artificial-intelligence-ai)

[2.2. Machine Learning (ML)
[5](#machine-learning-ml)](#machine-learning-ml)

[2.3. Natural Language Processing (NLP)
[6](#natural-language-processing-nlp)](#natural-language-processing-nlp)

[2.4. Large Language Models (LLM)
[7](#large-language-models-llm)](#large-language-models-llm)

[2.5. Retrievel-Augmented Generation (RAG)
[8](#retrievel-augmented-generation-rag)](#retrievel-augmented-generation-rag)

[2.6. LangChain [9](#langchain)](#langchain)

[2.7. Laravel [9](#laravel)](#laravel)

[2.8. React.js [10](#react.js)](#react.js)

[2.9. MySQL [11](#mysql)](#mysql)

[2.10. Hubungan Chat Respons Time dengan Efisiensi Pemasaran
[12](#hubungan-chat-respons-time-dengan-efisiensi-pemasaran)](#hubungan-chat-respons-time-dengan-efisiensi-pemasaran)

[2.11. Memory dalam Chatbot AI
[12](#memory-dalam-chatbot-ai)](#memory-dalam-chatbot-ai)

[2.12. Penelitian Terdahulu
[13](#penelitian-terdahulu)](#penelitian-terdahulu)

[BAB III METODOLOGI PENELITIAN
[19](#bab-iii-metodologi-penelitian)](#bab-iii-metodologi-penelitian)

[3.1. Kerangka Pikir [19](#kerangka-pikir)](#kerangka-pikir)

[3.2. Tahapan Penelitian [19](#tahapan-penelitian)](#tahapan-penelitian)

[3.3. Perencanaan Sistem [22](#perencanaan-sistem)](#perencanaan-sistem)

[3.4. Pengujian Sistem [27](#pengujian-sistem)](#pengujian-sistem)

[3.5. Rencana Evaluasi [27](#rencana-evaluasi)](#rencana-evaluasi)

[BAB IV HASIL DAN PEMBAHASAN
[29](#bab-iv-hasil-dan-pembahasan)](#bab-iv-hasil-dan-pembahasan)

[4.1 Hasil Implementasi Sistem
[29](#hasil-implementasi-sistem)](#hasil-implementasi-sistem)

[4.2 Pengujian Sistem [34](#pengujian-sistem-1)](#pengujian-sistem-1)

[4.3 Evaluasi Sistem [35](#evaluasi-sistem)](#evaluasi-sistem)

[BAB V KESIMPULAN DAN SARAN
[38](#bab-v-kesimpulan-dan-saran)](#bab-v-kesimpulan-dan-saran)

[DAFTAR PUSTAKA [40](#daftar-pustaka)](#daftar-pustaka)

[RIWAYAT HIDUP [45](#riwayat-hidup)](#riwayat-hidup)

# DAFTAR TABEL 

[Tabel 2.1. Penelitian Terdahulu
[18](#tabel-2.1.-penelitian-terdahulu)](#tabel-2.1.-penelitian-terdahulu)

[Tabel 3.1. Kerangka Pikir
[20](#tabel-3.1.-kerangka-pikir)](#tabel-3.1.-kerangka-pikir)

[Tabel 3.2. Tabel Kuisioner Pengguna Chatbot
[28](#tabel-3.2.-tabel-kuisioner-pengguna-chatbot)](#tabel-3.2.-tabel-kuisioner-pengguna-chatbot)

[Tabel 4.1. Contoh Data dari Kantor Properti A
[29](#tabel-4.1.-contoh-data-dari-kantor-properti-a)](#tabel-4.1.-contoh-data-dari-kantor-properti-a)

[Tabel 4.2. Contoh Data dari Kantor Properti B
[30](#tabel-4.2.-contoh-data-dari-kantor-properti-b)](#tabel-4.2.-contoh-data-dari-kantor-properti-b)

[Tabel 4.3. Contoh Data dari Kantor Properti C
[30](#tabel-4.3.-contoh-data-dari-kantor-properti-c)](#tabel-4.3.-contoh-data-dari-kantor-properti-c)

[Tabel 4.4. Rekapitulasi Jumlah Data yang Diperoeh
[30](#tabel-4.4.-rekapitulasi-jumlah-data-yang-diperoeh)](#tabel-4.4.-rekapitulasi-jumlah-data-yang-diperoeh)

[Tabel 4.5. Contoh Pertanyaan dan Hasil Jawaban
[33](#tabel-4.5.-contoh-pertanyaan-dan-hasil-jawaban)](#tabel-4.5.-contoh-pertanyaan-dan-hasil-jawaban)

[Tabel 4.6. Survei Kuisioner Pengguna Chatbot
[35](#tabel-4.6.-survei-kuisioner-pengguna-chatbot)](#tabel-4.6.-survei-kuisioner-pengguna-chatbot)

# DAFTAR GAMBAR

[Gambar 3.1. Tahapan Penelitian
[21](#gambar-3.1.-tahapan-penelitian)](#gambar-3.1.-tahapan-penelitian)

[Gambar 3.2. Arsitektur Sistem Chatbot RAG
[25](#gambar-3.2.-arsitektur-sistem-chatbot-rag)](#gambar-3.2.-arsitektur-sistem-chatbot-rag)

[Gambar 4.1. Gambar ERD
[31](#gambar-4.1.-gambar-erd)](#gambar-4.1.-gambar-erd)

[Gambar 4.2. Desain frontend chatbot
[32](#gambar-4.2.-desain-frontend-chatbot)](#gambar-4.2.-desain-frontend-chatbot)

[Gambar 4.3. Hasil konversi database menjadi teks format
[32](#gambar-4.3.-hasil-konversi-database-menjadi-teks-format)](#gambar-4.3.-hasil-konversi-database-menjadi-teks-format)

[Gambar 4.4. Template Prompt
[33](#gambar-4.4.-template-prompt)](#gambar-4.4.-template-prompt)

# DAFTAR LAMPIRAN

[Lampiran 1. Daftar Pertanyaan Uji Chatbot
[42](#_Toc207294953)](#_Toc207294953)

[Lampiran 2. Perhitungan Akurasi Jawaban
[43](#_Toc207294954)](#_Toc207294954)

[Lampiran 3. Perhitungan Waktu Respon Rata-Rata
[44](#_Toc207294955)](#_Toc207294955)

# 

# BAB I PENDAHULUAN

## Latar Belakang {#latar-belakang .Sub-2}

Industri properti terus berkembang pesat seiring dengan meningkatnya
kebutuhan masyarakat akan hunian dan investasi. Berdasarkan data dari
Asosiasi Real Estate Broker Indonesia (AREBI), pada 2024 terdapat 1.400
anggota perusahaan broker yang tersebar di 15 provinsi di Indonesia. Hal
ini mencerminkan tingginya aktivitas pemasaran properti di seluruh
wilayan Indonesia, sekaligus menunjukkan pentingnya efisiensi dalam
mendukung operasional tenaga pemasaran di industri ini.

Namun, tingginya jumlah perusahaan broker juga menciptakan tantangan
besar, terutama dalam hal pengelolaan informasi properti yang kompleks
dan terus berubah. Informasi seperti harga, lokasi, tipe properti,
fasilitas dan promosi sering kali harus diakses dengan cepat untuk
menjawab kebutuhan calon pembeli. Akan tetapi, banyak tenaga pemasaran
properti yang masih menggunakan metode manual, seperti pencarian data di
dokumen cetak atau file internal, yang sering kali tidak efisien dan
rawan kesalahan.

Teknologi kecerdasan buatan ( Artificial Intelligence / AI ) menawarkan
solusi inovatif, salah satunya melalui pengembangan chatbot berbasis
*Large Language Model* (LLM) yang dapat membantu agen mengakses
informasi secara cepat dan kontekstual. Dalam konteks ini, pendekatan
*Retrieval-Augmented Generation* (RAG) dipilih karena mampu
menggabungkan kemampuan generatif LLM dengan pencarian dokumen aktual
secara semantik dari database properti. Hal ini mengurangi resiko
jawaban diluar konteks dan meningkatkan relevansi informasi yang
diberikan chatbot.

Dengan memanfaatkan dataset beberapa dari kantor properti yang tergabung
dalam AREBI, chatbot ini dapat dirancang untuk mengolah informasi
properti yang selalu diperbarui, seperti harga dan status ketersediaan.
Selain itu, penerapan teknologi ini diharapkan mampu meningkatkan
produktivitas tenaga pemasaran sekaligus memperkuat daya saing industri
properti di Indonesia.

## Perumusan Masalah  {#perumusan-masalah .Sub-2}

Berdasarkan latar belakang di atas, terdapat beberapa permasalahan yang
perlu diselesaikan melalui penelitian ini :

1.  Bagaimana cara membantu agen properti mengakses informasi secara
    langsung terkait harga, lokasi, fasilitas dan informasi lainnya
    tanpa hambatan?

2.  Bagaimana merancang chatbot berbasis RAG yang dapat memberikan
    informasi relevan dari database properti dengan akurasi tinggi ?

3.  Bagaimana mengevaluasi keberhasilan chatbot dalam meningkatkan
    efisiensi kerja tenaga pemasaran?

4.  Bagaimana memastikan teknologi chatbot ini mudah digunakan oleh
    tenaga pemasaran dari berbagai latar belakang teknologi ?

## Tujuan Penelitian  {#tujuan-penelitian .Sub-2}

Tujuan dari penelitian ini adalah sebagai berikut :

1.  Mengembangkan chatbot berbasis RAG dengan akurasi jawaban \> 90%
    berdasarkan data listing properti kantor AREBI

2.  Membandingkan efisiensi waktu dan akurasi antara metode manual dan
    chatbot berbasis RAG.

3.  Melakukan survei kepada tenaga pemasaran untuk menilai tingkat
    kepuasan terhadap penggunaan chatbot

## Manfaat Penelitian  {#manfaat-penelitian .Sub-2}

Penelitian ini diharapkan memberikan manfaat sebagai berikut :

### Bagi Tenaga Pemasaran Properti {#bagi-tenaga-pemasaran-properti .Sub-3a}

1.  Membantu tenaga pemasaran mengakses informasi properti seperti
    harga, lokasi, fasilitas dan informasi lainnya secara *real-time*
    dan akurat.

2.  Meningkatkan rasa percaya diri tenaga pemasaran dalam menjawab
    pertanyaan dari calon pembeli.

3.  Meminimalkan kesalahan informasi yang diberikan kepada calon
    pembeli.

4.  Meningkatkan efisiensi kerja dan produktivitas tenaga pemasaran
    dalam menghadapi kebutuhan informasi yang terus berubah.

### Bagi Perusahaan Broker Properti {#bagi-perusahaan-broker-properti .Sub-3a}

1.  Memastikan informasi produk yang disampaikan tenaga pemasaran kepada
    calon pembeli selalu akurat dan terkini.

2.  Mengurangi waktu dan biaya operasional yang terkait dengan
    pengelolaan informasi properti secara manual.

3.  Meningkatkan efisiensi distribusi informasi dari perusahaan kepada
    tenaga pemasaran.

### Bagi Industri Properti {#bagi-industri-properti .Sub-3a}

1.  Mendorong adopsi teknologi AI dalam meningkatkan daya saing dan
    produktivitas industri properti di Indonesia.

2.  Memperkuat daya saing industri properti Indonesia terhadap kompetisi
    global dengan teknologi berbasis LLM dan RAG.

## Ruang Lingkup Penelitian {#ruang-lingkup-penelitian .Sub-2}

Penelitian ini memiliki ruang lingkup sebagai berikut :

### Teknologi yang digunakan  {#teknologi-yang-digunakan .Sub-3a}

1.  Menggunakan framework Laravel sebagai Backend untuk mengelola logika
    apilasi dan database MySQL untuk menyimpan data properti secara
    terstruktur.

2.  Menggunakan React.js unutk merancang antarmuka pengguna yang
    interaktif dan mudah digunakan.

3.  Menggunakan OpenAI API untuk embedding dan model generatif LLM

4.  Menggunakan Vector Database CHROMA untuk menyimpan hasil embedding
    data properti

### Fungsi Chatbot {#fungsi-chatbot .Sub-3a}

1.  Memberikan informasi produk properti kepada tenaga pemasaran,
    seperti harga, lokasi, fasilitas, tipe properti, status
    ketersediaan, spesifikasi, promosi dan skema pembayaran.

2.  Dirancang khusus untuk mendukung tenaga pemasaran, bukan untuk
    berkomunikasi langsung dengan pelanggan.

### Studi Kasus {#studi-kasus .Sub-3a}

> Menggunakan dataset dari beberapa kantor properti yang tergabung dalam
> Asosiasi Real Estate Broker Indonesia (AREBI)

### Evaluasi dan Pengukuran {#evaluasi-dan-pengukuran .Sub-3a}

1.  Metrik evaluasi meliputi kecepatan akses informasi, akurasi jawaban,
    dan kepuasan pengguna (tenaga pemasaran).

2.  Survei kepada tenaga pemsaran digunakan untuk menilai manfaat dan
    kemudahan penggunaan chatbot.

# BAB II TINJAUAN PUSTAKA

## Artificial Intelligence (AI) {#artificial-intelligence-ai .Sub-2}

*Artificial Intelligence* (AI) atau kecerdasan buatan adalah bidang ilmu
komputer yang berfokus pada pembuatan sistem yang mampu meniru
kecerdasan manusia. AI mencakup kemampuan untuk belajar dari data,
melakukan penalaran, serta mengambil keputusan layaknya manusia. Menurut
Russell dan Norvig (2021), AI membantu memecahkan masalah kompleks yang
sebelumnya hanya dapat diselesaikan oleh manusia, seperti pengenalan
pola, analisis data, dan pemrosesan bahasa alami.

AI sangat penting dalam berbagai industri karena dapat meningkatkan
efisiensi dan efektivitas pekerjaan. Dalam konteks properti, AI
digunakan untuk mempercepat analisis harga, memberikan rekomendasi
properti yang relevan, hingga mengotomatiskan proses pemasaran.
Penelitian oleh Afifah et al. (2023) menunjukkan bahwa pemanfaatan AI
dalam layanan pelanggan mampu meningkatkan kepuasan melalui respons
cepat dan akurat, sehingga memberikan nilai tambah bagi perusahaan.

Cara kerja AI melibatkan penggunaan algoritma dan model statistik yang
memungkinkan sistem untuk belajar dari pengalaman. Implementasi AI dapat
dilakukan dengan pendekatan *rule-based system*, *machine learning*,
hingga *deep learning* tergantung kebutuhan. Dalam penelitian ini, AI
digunakan sebagai dasar pengembangan chatbot untuk agen properti agar
dapat menyajikan informasi real-time, sehingga tenaga pemasaran memiliki
dukungan teknologi yang relevan dengan kebutuhan pasar saat ini.

## Machine Learning (ML) {#machine-learning-ml .Sub-2}

*Machine Learning (ML)* adalah cabang dari *Artificial Intelligence*
yang berfokus pada pengembangan algoritma yang memungkinkan komputer
untuk belajar dari data tanpa diprogram secara eksplisit. Dengan ML,
sistem dapat mengenali pola, membuat prediksi, dan meningkatkan
kinerjanya berdasarkan pengalaman dari data yang dianalisis. Menurut
Goodfellow et al. (2016), machine learning menjadi salah satu fondasi
utama dari *deep learning* dan berperan penting dalam perkembangan
teknologi berbasis data.

Penerapan *machine learning* sangat luas dan berperan penting dalam
berbagai bidang, mulai dari pemrosesan bahasa alami, pengenalan gambar,
hingga sistem rekomendasi. Dalam konteks industri properti, ML dapat
digunakan untuk menganalisis tren harga, memprediksi permintaan pasar,
serta memberikan rekomendasi properti yang sesuai dengan kebutuhan calon
pembeli. Penelitian Rane et al. (2024) menegaskan bahwa integrasi ML
dalam layanan berbasis e-commerce mampu meningkatkan kualitas pelayanan
melalui personalisasi dan respons yang lebih cepat, sehingga pendekatan
serupa relevan untuk diterapkan pada industri properti.

Cara kerja *machine learning* melibatkan penggunaan dataset untuk
melatih model agar mampu mengenali pola tertentu. Proses pelatihan ini
dapat dilakukan dengan metode *supervised learning*, *unsupervised
learning*, maupun *reinforcement learning* tergantung pada tujuan dan
ketersediaan data. Dalam penelitian ini, ML mendukung chatbot dalam
memahami pertanyaan pengguna dan menyesuaikannya dengan data properti
yang tersedia, sehingga meningkatkan relevansi dan akurasi informasi
yang diberikan kepada tenaga pemasaran.

## Natural Language Processing (NLP) {#natural-language-processing-nlp .Sub-2}

*Natural Language Processing (NLP)* adalah cabang dari *Artificial
Intelligence* yang berfokus pada kemampuan komputer untuk memahami,
menafsirkan, dan merespons bahasa manusia. NLP memungkinkan sistem
komputer memproses teks atau ucapan sehingga dapat digunakan dalam
berbagai aplikasi, seperti *chatbot*, *sentiment analysis*, dan asisten
virtual. Menurut Jurafsky dan Martin (2020), NLP memainkan peran penting
dalam interaksi manusia dan komputer karena menjembatani komunikasi
menggunakan bahasa alami.

NLP menjadi penting karena bahasa manusia memiliki kompleksitas yang
tinggi, mencakup tata bahasa, makna, dan konteks. Tanpa NLP, sistem
komputer akan kesulitan dalam memahami maksud pengguna yang disampaikan
secara natural. Dalam konteks properti, NLP memungkinkan chatbot untuk
menafsirkan pertanyaan calon pembeli seperti "Apakah ada rumah di Kemang
dengan tiga kamar tidur?" dan memberikan jawaban yang relevan.
Penelitian Rane et al. (2024) menunjukkan bahwa penggunaan NLP dalam
chatbot dapat meningkatkan kepuasan pelanggan karena respons yang
diberikan lebih cepat dan sesuai konteks.

Cara kerja NLP umumnya terdiri dari beberapa tahapan, antara lain
*tokenization*, *part-of-speech tagging*, *named entity recognition*,
dan *semantic analysis*. Setiap tahap membantu sistem memahami struktur
dan makna teks yang dimasukkan pengguna. Dalam penelitian ini, NLP
digunakan bersama dengan *Large Language Models* untuk memastikan
chatbot tidak hanya dapat memahami teks, tetapi juga menyajikan jawaban
yang informatif dan kontekstual sesuai kebutuhan tenaga pemasaran
properti.

## Large Language Models (LLM) {#large-language-models-llm .Sub-2}

*Large Language Models* (LLM) adalah model pembelajaran mesin berskala
besar yang dilatih menggunakan jumlah data teks yang sangat besar. Model
ini memiliki kemampuan untuk memahami konteks, menyusun kalimat, serta
menghasilkan teks yang menyerupai bahasa manusia. Brown et al. (2020)
menjelaskan bahwa model seperti GPT-3 dapat melakukan *few-shot
learning*, yaitu memahami instruksi baru hanya dengan sedikit contoh,
sehingga meningkatkan fleksibilitas dalam berbagai tugas pemrosesan
bahasa alami.

LLM menjadi penting karena memberikan lompatan besar dalam kualitas
percakapan chatbot dibandingkan pendekatan berbasis aturan. Moharekar
(2023) menunjukkan bahwa integrasi LLM dalam chatbot dapat meningkatkan
kemampuan percakapan hingga 95% dibandingkan model *rule-based*. Dengan
adanya LLM seperti GPT-3 dan GPT-4, pengembang dapat memanfaatkan
kemampuan generatif untuk memberikan jawaban yang relevan, kontekstual,
dan lebih natural bagi pengguna. Hal ini sangat relevan dalam dunia
properti, di mana calon pembeli sering menanyakan informasi detail yang
membutuhkan jawaban cepat dan tepat.

Cara kerja LLM bergantung pada arsitektur *transformer* yang mampu
memproses teks dalam jumlah besar secara paralel. Model ini menggunakan
*attention mechanism* untuk memahami hubungan antar kata dalam sebuah
kalimat atau paragraf. Dalam penelitian ini, LLM diintegrasikan dengan
pendekatan *Retrieval-Augmented Generation* (RAG) agar jawaban yang
diberikan tidak hanya generatif, tetapi juga didukung oleh data faktual
dari database properti. Dengan demikian, LLM berperan sebagai inti yang
mengolah konteks, sementara RAG memastikan keakuratan jawaban.

## Retrievel-Augmented Generation (RAG) {#retrievel-augmented-generation-rag .Sub-2}

*Retrieval-Augmented Generation* (RAG) adalah pendekatan yang
menggabungkan kemampuan *Large Language Models* dengan teknik pencarian
informasi dari basis data eksternal. Dengan RAG, sistem AI tidak hanya
mengandalkan pengetahuan bawaan yang sudah dilatih, tetapi juga mampu
mengambil informasi terkini dari sumber data yang relevan. Menurut Lewis
et al. (2020), metode RAG meningkatkan akurasi jawaban karena model
dapat mengakses pengetahuan faktual di luar data pelatihan, sehingga
mengurangi risiko informasi yang tidak relevan atau halusinasi.

Keberadaan RAG sangat penting dalam aplikasi chatbot yang membutuhkan
informasi aktual dan spesifik. Dalam konteks industri properti, RAG
memungkinkan chatbot memberikan jawaban terkait harga, lokasi,
fasilitas, dan status ketersediaan properti secara real-time berdasarkan
data yang tersimpan di database. Penelitian Lewers et al. (2024)
menunjukkan bahwa metode hibrid yang menggabungkan kemampuan LLM dengan
sistem backend tradisional mampu meningkatkan fleksibilitas percakapan
sekaligus menjaga akurasi data. Hal ini membuktikan bahwa RAG lebih
unggul dibandingkan pendekatan chatbot yang hanya mengandalkan model
generatif.

Cara kerja RAG dimulai dari *retriever* yang mencari dokumen atau data
relevan dari database berbasis vektor. Hasil pencarian tersebut kemudian
digunakan oleh LLM untuk menghasilkan jawaban yang lebih natural dan
kontekstual. Dalam penelitian ini, RAG diimplementasikan menggunakan
*ChromaDB* sebagai *vector database* untuk mendukung pencarian semantik,
serta LangChain sebagai penghubung antara LLM dan data eksternal.
Pendekatan ini memastikan jawaban chatbot selalu relevan, akurat, dan
sesuai dengan konteks pertanyaan pengguna.

## LangChain {#langchain .Sub-2}

*LangChain* adalah sebuah *framework* yang dirancang untuk memudahkan
integrasi antara *Large Language Models* dan berbagai sumber data
eksternal. Dengan adanya LangChain, pengembang dapat membangun aplikasi
berbasis AI yang tidak hanya bergantung pada pengetahuan statis model,
tetapi juga dapat mengakses dan memperbarui informasi secara real-time.
Menurut Lewers et al. (2024), LangChain mendukung berbagai komponen
penting dalam pengembangan chatbot, seperti *retrieval*, *agent
execution*, dan integrasi dengan *vector database*.

Penggunaan LangChain menjadi penting karena memberikan fleksibilitas
tinggi bagi sistem berbasis AI. Framework ini memungkinkan chatbot untuk
menelusuri informasi dari basis data, menghubungkannya dengan API
eksternal, dan menyajikan jawaban yang sesuai dengan kebutuhan pengguna.
Dalam konteks properti, LangChain berperan sebagai penghubung utama
antara data listing yang disimpan di database dan model bahasa yang
digunakan untuk menghasilkan respons. Dengan begitu, tenaga pemasaran
dapat memperoleh informasi yang akurat, meskipun pertanyaan pengguna
disampaikan dengan variasi bahasa yang berbeda.

Dalam penelitian ini, LangChain dimanfaatkan sebagai jembatan antara
*ChromaDB* dan model LLM dari OpenAI. Framework ini mengelola alur kerja
mulai dari menerima pertanyaan pengguna, mengekstrak data relevan dari
*vector database*, hingga menyusun jawaban yang kontekstual. Dengan
kemampuannya yang modular, LangChain membantu mempercepat proses
pengembangan sekaligus meningkatkan konsistensi hasil yang diberikan
oleh chatbot. Hal ini menjadikannya komponen kunci dalam perancangan
sistem asisten virtual untuk agen properti.

## Laravel {#laravel .Sub-2}

*Laravel* adalah sebuah *framework* berbasis PHP yang populer untuk
pengembangan aplikasi web modern. Framework ini menawarkan struktur kode
yang rapi, sistem routing yang fleksibel, serta berbagai fitur bawaan
yang mendukung skalabilitas dan keamanan aplikasi. Menurut Mashud dan
Wisda (2019), Laravel menjadi salah satu *framework* yang paling banyak
digunakan karena kemudahan sintaksisnya serta dukungan komunitas yang
luas.

Dalam penelitian ini, Laravel dipilih sebagai *backend* karena
kemampuannya dalam mengelola logika aplikasi dan integrasi dengan basis
data. Laravel menyediakan *Object Relational Mapping* (ORM) melalui
Eloquent, yang memudahkan pengembang dalam melakukan operasi pada
database tanpa perlu menulis query SQL secara manual. Selain itu,
Laravel juga mendukung sistem autentikasi, middleware, serta manajemen
API, yang semuanya diperlukan untuk menghubungkan chatbot dengan sistem
data properti.

Penerapan Laravel tidak hanya berfokus pada efisiensi pengembangan,
tetapi juga memastikan bahwa aplikasi yang dibangun dapat diatur dengan
baik dan mudah dipelihara. Dalam konteks chatbot properti, Laravel
bertugas menangani permintaan pengguna, mengelola data listing dari
MySQL, serta menyiapkan API yang akan dipanggil oleh LangChain dan
React.js. Dengan demikian, Laravel berperan penting sebagai fondasi yang
menjamin kestabilan dan keamanan alur komunikasi antara pengguna,
database, dan model AI.

## React.js {#react.js .Sub-2}

*React.js* adalah sebuah *library* JavaScript yang digunakan untuk
membangun antarmuka pengguna yang interaktif dan dinamis. Dikembangkan
oleh Facebook, React.js memungkinkan pengembang membuat komponen yang
dapat digunakan kembali, sehingga mempermudah pengelolaan kode dalam
aplikasi berskala besar. Menurut Wieruch (2020), keunggulan utama
React.js adalah penggunaan *Virtual DOM* yang membuat proses render
lebih efisien dan responsif.

Pemanfaatan React.js sangat relevan dalam penelitian ini karena chatbot
memerlukan tampilan antarmuka yang ramah pengguna dan mudah diakses.
Dengan pendekatan berbasis komponen, React.js memungkinkan pembuatan
halaman percakapan yang rapi, mulai dari kotak input hingga balon chat
yang menampilkan jawaban. Selain itu, React.js juga mendukung integrasi
dengan berbagai pustaka eksternal, sehingga memperluas kemungkinan
pengembangan fitur tambahan seperti animasi atau notifikasi real-time.

Dalam implementasi sistem, React.js digunakan untuk menyusun halaman
utama chatbot serta halaman detail properti yang ditampilkan kepada
tenaga pemasaran. Framework ini bekerja sama dengan Laravel melalui API,
sehingga data yang disimpan di database dapat langsung divisualisasikan
di antarmuka pengguna. Dengan cara ini, React.js tidak hanya menjadi
alat presentasi, tetapi juga bagian penting dalam menciptakan pengalaman
interaktif yang mendukung efektivitas tenaga pemasaran dalam mengakses
informasi properti.

## MySQL {#mysql .Sub-2}

*MySQL* adalah salah satu sistem manajemen basis data relasional yang
paling banyak digunakan di dunia, terutama untuk aplikasi berbasis web.
MySQL terkenal karena kecepatan, keandalan, dan kemudahan penggunaannya
sehingga menjadi pilihan utama bagi pengembang dalam mengelola data yang
terstruktur. Menurut Mullins (2020), MySQL mendukung berbagai fitur
penting seperti transaksi, replikasi, serta keamanan data yang
menjadikannya cocok untuk aplikasi berskala kecil hingga besar.

Dalam konteks penelitian ini, MySQL digunakan untuk menyimpan informasi
properti secara terstruktur, termasuk detail harga, lokasi, tipe unit,
fasilitas, serta status ketersediaan. Database ini dirancang agar
mendukung pencarian cepat sekaligus integrasi dengan sistem lain seperti
Laravel dan *vector database*. Dengan struktur yang tepat, MySQL
memungkinkan data diakses secara real-time sehingga informasi yang
diberikan chatbot selalu akurat dan mutakhir.

Implementasi MySQL dalam penelitian ini juga mempertimbangkan aspek
normalisasi agar redundansi data dapat diminimalkan. Setelah data
tersimpan, hasilnya kemudian diubah menjadi *vector embeddings* untuk
mendukung pencarian semantik melalui ChromaDB. Dengan demikian, MySQL
berperan sebagai fondasi penyimpanan data yang stabil, sementara
integrasinya dengan teknologi lain memastikan chatbot dapat menjawab
pertanyaan pengguna dengan cepat dan relevan.

## Hubungan Chat Respons Time dengan Efisiensi Pemasaran {#hubungan-chat-respons-time-dengan-efisiensi-pemasaran .Sub-2}

Dalam dunia pemasaran digital, kecepatan respons menjadi salah satu
faktor penting yang memengaruhi kepuasan pelanggan. Semakin cepat sebuah
pertanyaan dijawab, semakin tinggi pula kemungkinan calon konsumen
merasa diperhatikan dan termotivasi untuk melanjutkan proses pembelian.
Menurut Afifah et al. (2023), adanya chatbot dengan *response time* yang
singkat terbukti meningkatkan kepuasan pelanggan karena mereka tidak
perlu menunggu lama untuk mendapatkan informasi.

Dalam industri properti, kecepatan respons menjadi lebih krusial karena
informasi seperti harga, ketersediaan unit, dan lokasi sering kali
menentukan keputusan pembelian. Agen properti yang dapat merespons
pertanyaan calon pembeli dengan cepat cenderung memiliki peluang lebih
besar untuk menarik minat. Hal ini juga didukung oleh penelitian Rane et
al. (2024), yang menyatakan bahwa respons real-time dalam layanan
digital mampu meningkatkan interaksi pengguna sekaligus mendorong
efisiensi operasional.

Penelitian ini menekankan pentingnya integrasi chatbot yang mampu
memberikan jawaban cepat dan akurat berdasarkan data properti yang
tersimpan di database. Dengan rata-rata waktu respons chatbot sekitar
1--2 detik, agen properti dapat lebih fokus pada aktivitas negosiasi dan
penutupan transaksi, sementara chatbot menangani pertanyaan dasar.
Dengan demikian, *chat response time* tidak hanya menjadi indikator
kepuasan pelanggan, tetapi juga menjadi salah satu kunci peningkatan
efisiensi tenaga pemasaran dalam industri properti.

## Memory dalam Chatbot AI {#memory-dalam-chatbot-ai .Sub-2}

*Memory* dalam chatbot AI merujuk pada kemampuan sistem untuk mengingat
interaksi sebelumnya sehingga dapat memberikan jawaban yang konsisten
dan relevan pada percakapan lanjutan. Tanpa adanya *memory*, setiap
pertanyaan pengguna akan dianggap sebagai interaksi baru yang berdiri
sendiri, sehingga percakapan terasa terputus-putus dan kurang natural.
Wu et al. (2025) menjelaskan bahwa dalam era *Large Language Models*,
*memory* dipandang sebagai mekanisme penting yang memungkinkan model
menyimpan, mengingat, dan menggunakan informasi dari percakapan
sebelumnya. Mereka juga mengklasifikasikan *memory* dalam tiga dimensi,
yaitu objek (personal dan sistem), bentuk (parametrik dan
non-parametrik), serta waktu (jangka pendek dan jangka panjang).

Keberadaan *memory* sangat penting dalam konteks chatbot properti karena
calon pembeli sering mengajukan pertanyaan berkelanjutan yang saling
terkait. Sebagai contoh, pengguna dapat bertanya "Apakah ada rumah di
Kemang dengan tiga kamar tidur?", lalu melanjutkannya dengan "Bagaimana
dengan fasilitasnya?". Tanpa *memory*, chatbot tidak akan memahami bahwa
pertanyaan kedua masih terkait dengan rumah di Kemang yang dimaksud.
Zhong et al. (2023) menegaskan bahwa mekanisme memori jangka panjang
seperti *MemoryBank* dapat membantu model mempertahankan konteks,
sekaligus mengurangi risiko kehilangan informasi dalam percakapan yang
lebih panjang.

Dalam penelitian ini, *memory* diimplementasikan dengan dukungan
*framework* LangChain yang menyediakan modul seperti
*ConversationBufferMemory* dan *SummaryMemory*. Modul ini menyimpan
riwayat percakapan atau ringkasannya untuk dijadikan konteks ketika
pengguna mengajukan pertanyaan berikutnya. Wang et al. (2023)
mengusulkan teknik *recursive summarization* agar memori lebih efisien
dan tidak membebani model dengan konteks yang terlalu panjang. Dengan
mekanisme ini, chatbot properti tidak hanya mampu memberikan jawaban
yang akurat, tetapi juga mempertahankan kesinambungan percakapan
sehingga interaksi terasa lebih alami dan mendekati komunikasi manusia.

## Penelitian Terdahulu  {#penelitian-terdahulu .Sub-2}

Penelitian yang dilakukan oleh Ratnawati et al (2021) mengembangkan
*chatbot* berbasis *Telegram* untuk mendukung distribusi informasi
properti secara cepat dan efisien. Kelebihan dari penelitian ini adalah
penggunaan metode *prototyping* yang memungkinkan iterasi desain sesuai
kebutuhan pengguna. Namun, *chatbot* yang dikembangkan masih memiliki
keterbatasan karena bergantung pada platform *Telegram,* sehingga sulit
diakses oleh pengguna di luar ekosistem tersebut. Selain itu, *chatbot*
ini tidak mampu memperbarui data secara otomatis. Gap yang dapat
diidentifikasi adalah kurangnya fleksibilitas dan ketergantungan pada
satu platform. Penelitian ini menjadi pijakan untuk pengembangan chatbot
yang lebih fleksibel dan terintegrasi dengan backend modern seperti
Laravel dan MySQL untuk mendukung data *real-time.*

Penelitian yang dilakukan oleh [Febriansyah dan Nirmala]{.mark} (2023)
mengintegrasikan chatbot berbasis Telegram dengan sistem informasi untuk
mempermudah distribusi informasi properti. Kelebihannya adalah integrasi
yang meningkatkan efisiensi interaksi pelanggan dan tenaga pemasaran.
Namun, chatbot ini memiliki kekurangan dalam hal pembaruan data secara
otomatis dan ketergantungan pada Telegram sebagai platform utama. Gap
yang diidentifikasi adalah kebutuhan akan chatbot yang lebih mandiri dan
dapat diakses melalui berbagai platform. Penelitian ini menginspirasi
pengembangan chatbot berbasis AI yang mampu belajar secara otomatis
dengan memanfaatkan OpenAI API.

Penelitian yang dilakukan oleh [Lewers et al]{.mark} (2024)
memperkenalkan metode hybrid untuk membangun *chatbot*, yang menggunakan
kemampuan LLM dengan backend tradisional. Kelebihannya adalah metode
hybrid menawarkan fleksibilats tinggi, memungkinkan *chatbot* memahami
konteks percakapan sambil tetao mengandalkan data yang akurat dari
backend. Kekurangannya, implementasi metode ini membutuhkan
infrastruktur yang lebih kompleks dibandingkan metode *rule based*. Gap
yang diangkat dalam penelitian ini adalah tantangan integrasi antara LLM
dan sistem backend. Penelitian tesis ini dapat memanfaatkan metode
hybrid untuk menciptakan *chatbot* properti berbasis AI yang mampu
memproses data *real-time* dengan efisien.

Penelitian yang dilakukan oleh [Rane et al]{.mark} (2024) menggunakan
kombinasi AI, NLP, dan ML untuk meningkatkan kualitas layanan
e-commerce. Kelebihannya adalah peningkatan kepuasan pelanggan hingga
30% melalui respons *real-time* dan personalisasi. Namun, penelitian ini
berfokus pada e-commerce, sehingga tidak secara langsung relevan dengan
kebutuhan industri properti. Gap yang dapat diangkat adalah perlunya
penelitian lebih lanjut untuk menerapkan teknologi serupa pada konteks
pemasaran properti. Penelitian tesis ini berfokus pada adaptasi
teknologi AI dan NLP untuk memenuhi kebutuhan unik pemasaran properti.

Penelitian yang dilakukan oleh [Afifah et al]{.mark} (2023) membahas
hubungan antara respons chatbot yang cepat dengan kepuasan pelanggan
dalam e-commerce. Hasilnya menunjukkan bahwa respons dalam waktu kurang
dari 5 menit meningkatkan kepuasan pelanggan. Kelebihan penelitian ini
adalah penekanannya pada pentingnya waktu respons dalam meningkatkan
pengalaman pelanggan. Namun, penelitian ini tidak mengaplikasikan temuan
tersebut pada industri properti. Gap yang diangkat adalah perlunya
penerapan chatbot responsif dalam konteks pemasaran properti untuk
memenuhi kebutuhan pelanggan yang dinamis. Penelitian ini akan
mengintegrasikan respons cepat dengan kemampuan auto-learning untuk
memaksimalkan efisiensi.

Penelitian oleh Salem dan Mazzara (2020) mengembangkan sebuah chatbot
berbasis Telegram yang memanfaatkan algoritma *machine learning* untuk
memprediksi harga properti real estat. Bot ini menerima input berupa
jumlah kamar, geolokasi, dan luas area dalam meter persegi untuk
memberikan estimasi harga properti. Data pelatihan diperoleh melalui
teknik *web scraping* dari situs iklan properti di Amman, Yordania.
Hasil penelitian menunjukkan bahwa dengan memasukkan geolokasi sebagai
variabel, akurasi model meningkat sebesar 1,3 kali lipat.Gap yang
diangkat adalah penelitian ini belum mengkaji penerapan chatbot serupa
di platform lain selain Telegram, serta integrasi dengan sistem backend
yang lebih kompleks untuk mendukung pembaruan data secara real-time.
Selain itu, penelitian ini tidak membahas evaluasi kinerja chatbot dalam
konteks interaksi pengguna secara langsung.

Penelitian oleh Dobbala dan Lingo (2024) mengeksplorasi potensi
transformasional dari AI percakapan dan chatbot dalam meningkatkan
pengalaman pengguna (UX) di situs web. Studi ini menyoroti bahwa
integrasi AI percakapan dapat menyediakan bantuan personalisasi,
menyederhanakan proses kompleks, memastikan ketersediaan 24/7, dan
meningkatkan aksesibilitas bagi pengguna. Namun, penelitian ini juga
mengidentifikasi tantangan dalam implementasi, seperti penanganan
ambiguitas dalam pemrosesan bahasa alami, memastikan privasi dan
keamanan data, serta kebutuhan akan peningkatan dan pelatihan
berkelanjutan. Solusi yang diusulkan meliputi penggunaan algoritma NLP
canggih, alat manajemen API yang kuat, dan pembentukan umpan balik
pengguna. Selain itu, pertimbangan etis seperti privasi data dan bias
dalam respons AI juga dibahas, menekankan pentingnya enkripsi yang kuat
dan kepatuhan terhadap regulasi privasi data. Gap yang diangkat dalam
penelitian ini adalah penerapaan secara spesifik untuk industri properti
di Indonesia. Selain itu, penelitian ini kurang mengeksplorasi integrasi
AI percakapan dengan sistem backend yang kompleks untuk pembaruan data
real-time dan penyesuaian otomatis berdasarkan perilaku pengguna.

Penelitian oleh Towhidul dan Oshita (2025) mengkaji peran kecerdasan
buatan (AI) dalam pemasaran, khususnya penerapan analitik real-time di
sektor perbankan dan keuangan. Studi ini menyoroti bagaimana AI dapat
mengolah berbagai sumber data, meningkatkan manajemen data, dan
merancang algoritma canggih untuk mengubah interaksi antara merek dan
konsumen. Dengan memanfaatkan AI, pemasar dapat lebih fokus pada
kebutuhan pelanggan secara real-time, menentukan konten yang tepat,
serta memilih saluran komunikasi yang optimal berdasarkan data yang
dikumpulkan dan diolah oleh algoritma AI. Selain itu, AI memungkinkan
personalisasi pengalaman pengguna, yang dapat meningkatkan kenyamanan
dan kecenderungan konsumen untuk melakukan pembelian. Alat berbasis AI
juga dapat menganalisis kinerja kampanye pesaing dan mengungkap
ekspektasi pelanggan.

Penelitian oleh Mali et al. (2023) memperkenalkan aplikasi berbasis web
dan Android yang dirancang untuk mengelola transaksi antara broker dan
pengembang dalam industri real estat. Aplikasi ini bertujuan untuk
menyederhanakan proses transaksi properti melalui komunikasi dan
kolaborasi yang efisien. Fitur utama yang ditawarkan meliputi
otomatisasi listing properti, negosiasi, dan penutupan transaksi, yang
diharapkan dapat menghemat waktu dan mengurangi kesalahan. Selain itu,
aplikasi ini dilengkapi dengan sistem *Customer Relationship Management*
(CRM) bawaan untuk melacak prospeapakk dan memungkinkan pengambilan
keputusan berbasis data. Sistem analitik yang terintegrasi juga
menyediakan wawasan tentang pasar real estat dan perilaku pelanggan.
Aplikasi ini dirancang dengan fokus pada keamanan dan skalabilitas,
serta kemampuan integrasi dengan sistem lain, menjadikannya alat
esensial bagi broker dan pengembang untuk meningkatkan efisiensi dan
profitabilitas dalam bisnis mereka.

Penelitian oleh Febrianto dan Putri (2023) membahas implementasi chatbot
sebagai agen perumahan untuk meningkatkan efisiensi dan akurasi
informasi dalam proses pencarian dan pemesanan rumah. Chatbot yang
dikembangkan menggunakan platform Einstein Bot dari Salesforce,
dirancang untuk membantu pelanggan mengakses informasi yang diinginkan
serta memproses permintaan pemesanan rumah dengan cepat dan tepat.
Melalui integrasi ini, chatbot dapat berinteraksi dengan pelanggan
melalui media sosial, memberikan respons otomatis terkait ketersediaan
unit, detail properti, dan informasi lainnya yang relevan. Selain itu,
agen properti dapat memantau dan melanjutkan interaksi melalui antarmuka
Salesforce, memastikan bahwa kebutuhan pelanggan terpenuhi secara
efisien. Implementasi ini diharapkan dapat mengurangi beban kerja manual
agen perumahan dan meningkatkan kepuasan pelanggan melalui penyediaan
informasi yang akurat dan responsif. Studi ini belum mengevaluasi secara
empiris tingkat kepuasan pelanggan setelah implementasi chatbot, serta
dampaknya terhadap peningkatan penjualan properti. Selain itu,
penelitian ini tidak membahas integrasi *chatbot* dengan teknologi lain,
seperti analitik data atau kecerdasan buatan lanjutan, untuk lebih
meningkatkan personalisasi dan efektivitas interaksi.

Wu et al. (2025) menjelaskan bahwa dalam era LLM, *memory* adalah
kemampuan sistem AI untuk menyimpan, mengingat, dan menggunakan
informasi dari interaksi sebelumnya. Mereka juga melakukan perbandingan
antara memori manusia dan sistem AI, serta mengorganisasi mekanisme
memori menurut tiga dimensi: objek (personal & sistem), bentuk
(parametrik & non-parametrik), dan waktu (jangka pendek & jangka
panjang)

#### Tabel 2.1. Penelitian Terdahulu {#tabel-2.1.-penelitian-terdahulu .Judul-Tabel}

  -----------------------------------------------------------------------------------
  **No.**   **Nama Penulis**  **Tahun**   **Metode**    **[Hasil Utama]{.mark}**
  --------- ----------------- ----------- ------------- -----------------------------
  1         [Ratnawati et     2021        Prototyping   Chatbot berbasis Telegram
            al]{.mark}                                  mendukung distribusi
                                                        informsasi properti, tetapi
                                                        terbatas pada satu platform
                                                        dan tidak mampu memperbarui
                                                        data secara otomatis.

  2         [Febriansyah dan  2023        Integrasi     Chatbot meningkatkan
            Nirmala]{.mark}               Chatbot dan   interaksi pelanggan, tetapi
                                          Sistem        tidak memiliki kemampuan
                                          Informasi     auto-update dan
                                                        ketergantungan pada platform
                                                        Telegram

  3         [Lewers et        2024        Hybrid LLM    Metode hybrid memungkinkan
            al]{.mark}                                  fleksibilitas tinggi dalam
                                                        memahami konteks percakapan,
                                                        tetapi memutuhkan
                                                        infrastruktur yang kompleks

  4         [Rane et          2024        NLP dan ML    Respons real-time dan
            al]{.mark}                                  personalisasi meningkatkan
                                                        kepuasan pelangangan tetapi
                                                        belum diaplikasikan pada
                                                        industri properti

  5         [Afifah et        2023        Chatbot       Respons cepat meningkatkan
            al]{.mark}                    respons cepat kepuasan pelanggan, tetapi
                                                        belum diaplikasikan pada
                                                        pemasaran properti

  6         [Salem dan        2020        Telegram      Bot memprediksi harga
            Mazzara]{.mark}               chatbot       properti dengan akurasi
                                                        tinggi dengan menggunakan
                                                        data geolokasi, tetapi
                                                        terbatas pada telegram dan
                                                        kurang evaluasi pada konteks
                                                        pengguna langsung.

  7         [Dobbala dan      2024        Chatbot AI    AI percakapan meningkatkan
            Lingo]{.mark}                               aksesibilitas dan
                                                        personalisasi pengguna,
                                                        tetapi belum diterapkan pada
                                                        industri properti di
                                                        Indonesia

  8         [Towhidul dan     2025        Real-time     AI memungkinkan personalisasi
            Oshita]{.mark}                Analytics     pengalaman pengguna dalam
                                                        pemasaran real-time, tetapi
                                                        tidak membahas konteks pasar
                                                        properti secara khusus.

  9         [Mali et          2023        Web dan       Aplikasi berbasis web dan
            al]{.mark}                    Android       Android mengelola transaksi
                                          Application   properti secara efisien,
                                                        tetapi tidak mencakup
                                                        personalisasi berbasis AI

  10        [Febrianto dan    2023        Einstein Bot  Chatbot meningkatkan
            Putri]{.mark}                 dari          efisiensi dalam pencarian
                                          Salesforce    properti, tetapi kurang
                                                        evaluasi tingkat kepuasan
                                                        pelanggan dan integrasi
                                                        dengan teknologi lain seperti
                                                        analitik data.
  -----------------------------------------------------------------------------------

# BAB III METODOLOGI PENELITIAN

## Kerangka Pikir  {#kerangka-pikir .Sub-2}

Penelitian ini berangkat dari permasalahan yang diidentifikasi pada Bab
I, yaitu permasalahan yang dihadapi tenaga pemasaran properti dalam
mengelola dan menyampaikan informasi yang akurat, cepat, dan *real-time*
kepada calon pembeli. Permasalahan ini timbul karena banyak perusahaan
broker properti masih menggunakan metode manual, seperti pencarian data
di dokumen cetak atau file internal, yang cenderung memakan waktu, rawan
kesalahan, dan tidak efisien. Di sisi lain, calon pembeli properti
semakin mengharapkan akses cepat terhadap informasi seperti harga,
lokasi, tipe properti, fasilitas, dan promosi, yang merupakan faktor
kunci dalam pengambilan keputusan pembelian. Oleh karena itu, penelitian
ini bertujuan untuk menciptakan sebuah solusi inovatif berupa *chatbot*
berbasis AI yang dirancang khusus untuk mendukung tenaga pemasaran
properti dalam menghadapi tantangan tersebut. [Tabel 3.1. menyajikan
kerangka piker penelitian dalam tiga kolom utama, yaitu identifikasi
masalah, metode penelitian terdahulu dan kontribusi penelitian
ini]{.mark}.

## Tahapan Penelitian {#tahapan-penelitian .Sub-2}

Tahapan penelitian ini dirancang secara sistematis agar setiap langkah
yang dilakukan dapat menjawab tujuan penelitian dengan jelas dan
terukur. Setiap tahap merepresentasikan alur mulai dari persiapan hingga
evaluasi, sehingga penelitian tidak hanya menghasilkan rancangan sistem,
tetapi juga bukti empiris mengenai kinerja chatbot yang dikembangkan.
Dengan adanya tahapan yang terstruktur, peneliti dapat memastikan bahwa
seluruh proses berjalan konsisten serta dapat direplikasi pada
penelitian sejenis di masa mendatang. Alur tahapan penelitian
ditampilkan pada Gambar 3.1.

Secara garis besar, penelitian ini terdiri dari lima tahap utama.
Pertama, pengumpulan data dilakukan dengan memperoleh dataset properti
dari beberapa kantor yang tergabung dalam AREBI, kemudian data tersebut
dibersihkan dan dinormalisasi agar siap digunakan. Kedua, perancangan
sistem dilakukan dengan menyusun struktur database, merancang antarmuka
pengguna menggunakan *React.js*, serta mengembangkan *backend* dengan
Laravel. Ketiga, tahap implementasi melibatkan integrasi sistem dengan
*OpenAI API* dan *LangChain* untuk mendukung *Retrieval-Augmented
Generation*. Keempat, sistem yang telah dibangun diuji melalui skenario
pencarian data properti serta percakapan pengguna. Terakhir, tahap
evaluasi dilakukan dengan mengukur akurasi jawaban, kecepatan respons,
dan kepuasan tenaga pemasaran yang menjadi pengguna sistem.

#### [Tabel 3.1. Kerangka Pikir]{.mark} {#tabel-3.1.-kerangka-pikir .Judul-Tabel}

+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| #### **Identifikasi Masalah** {#identifikasi-masalah .Judul-Tabel}                                                                                                                                                               | #### **Penelitian Terdahulu** {#penelitian-terdahulu-1 .Judul-Tabel}                                                                                                                                                                                                                                                                                                                                                                                          | #### **Kontribusi Penelitian Ini** {#kontribusi-penelitian-ini .Judul-Tabel}                                                                                                                                                                                                                                                                                                           |
+==================================================================================================================================================================================================================================+===============================================================================================================================================================================================================================================================================================================================================================================================================================================================+========================================================================================================================================================================================================================================================================================================================================================================================+
| #### Informasi properti sulit diakses secara cepat, akurat, dan real-time oleh tenaga pemasaran. {#informasi-properti-sulit-diakses-secara-cepat-akurat-dan-real-time-oleh-tenaga-pemasaran. .Judul-Tabel}                       | #### Ratnawati et al. (2021) dan Febriansyah & Nirmala (2023) menggunakan *chatbot* berbasis Telegram yang mampu menyajikan informasi properti, tetapi terbatas pada satu platform dan tidak dapat memperbarui data otomatis. {#ratnawati-et-al.-2021-dan-febriansyah-nirmala-2023-menggunakan-chatbot-berbasis-telegram-yang-mampu-menyajikan-informasi-properti-tetapi-terbatas-pada-satu-platform-dan-tidak-dapat-memperbarui-data-otomatis. .Judul-Tabel} | #### Mengembangkan *chatbot* berbasis *Retrieval-Augmented Generation* (RAG) dengan integrasi ke database properti sehingga informasi dapat diakses secara real-time. {#mengembangkan-chatbot-berbasis-retrieval-augmented-generation-rag-dengan-integrasi-ke-database-properti-sehingga-informasi-dapat-diakses-secara-real-time. .Judul-Tabel}                                       |
|                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
| ####  {#section-1 .Judul-Tabel}                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| #### Chatbot berbasis aturan atau platform tunggal tidak fleksibel dalam memahami variasi bahasa pengguna. {#chatbot-berbasis-aturan-atau-platform-tunggal-tidak-fleksibel-dalam-memahami-variasi-bahasa-pengguna. .Judul-Tabel} | #### Lewers et al. (2024) mengusulkan metode *hybrid* yang menggabungkan *Large Language Models* (LLM) dengan sistem backend tradisional, namun membutuhkan infrastruktur kompleks. {#lewers-et-al.-2024-mengusulkan-metode-hybrid-yang-menggabungkan-large-language-models-llm-dengan-sistem-backend-tradisional-namun-membutuhkan-infrastruktur-kompleks. .Judul-Tabel}                                                                                     | #### Menerapkan LLM (GPT-4) melalui *LangChain* untuk memproses pertanyaan dalam berbagai variasi bahasa dengan jawaban yang lebih natural dan kontekstual. {#menerapkan-llm-gpt-4-melalui-langchain-untuk-memproses-pertanyaan-dalam-berbagai-variasi-bahasa-dengan-jawaban-yang-lebih-natural-dan-kontekstual. .Judul-Tabel}                                                         |
|                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
| ####  {#section-2 .Judul-Tabel}                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| #### Tidak ada mekanisme memori untuk menyambungkan pertanyaan berkelanjutan dalam percakapan. {#tidak-ada-mekanisme-memori-untuk-menyambungkan-pertanyaan-berkelanjutan-dalam-percakapan. .Judul-Tabel}                         | #### Wu et al. (2025) dan Zhong et al. (2023) mengusulkan *memory* jangka panjang pada LLM, namun belum banyak diterapkan di chatbot industri properti. {#wu-et-al.-2025-dan-zhong-et-al.-2023-mengusulkan-memory-jangka-panjang-pada-llm-namun-belum-banyak-diterapkan-di-chatbot-industri-properti. .Judul-Tabel}                                                                                                                                           | #### Menambahkan fitur *memory* dengan *ConversationBufferMemory* dan *SummaryMemory* di LangChain agar chatbot dapat memahami pertanyaan lanjutan dengan konteks percakapan sebelumnya. {#menambahkan-fitur-memory-dengan-conversationbuffermemory-dan-summarymemory-di-langchain-agar-chatbot-dapat-memahami-pertanyaan-lanjutan-dengan-konteks-percakapan-sebelumnya. .Judul-Tabel} |
|                                                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
| ####  {#section-3 .Judul-Tabel}                                                                                                                                                                                                  |                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                                                                                                                                        |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| #### Evaluasi kepuasan pengguna pada chatbot properti belum banyak dilakukan secara sistematis. {#evaluasi-kepuasan-pengguna-pada-chatbot-properti-belum-banyak-dilakukan-secara-sistematis. .Judul-Tabel}                       | #### Afifah et al. (2023) meneliti kepuasan konsumen di e-commerce dengan mengukur kecepatan respons, tetapi belum diterapkan di industri properti. {#afifah-et-al.-2023-meneliti-kepuasan-konsumen-di-e-commerce-dengan-mengukur-kecepatan-respons-tetapi-belum-diterapkan-di-industri-properti. .Judul-Tabel}                                                                                                                                               | #### Melakukan survei kepuasan tenaga pemasaran terhadap penggunaan chatbot untuk mengukur manfaat, kemudahan, dan akurasi jawaban dalam konteks pemasaran properti. {#melakukan-survei-kepuasan-tenaga-pemasaran-terhadap-penggunaan-chatbot-untuk-mengukur-manfaat-kemudahan-dan-akurasi-jawaban-dalam-konteks-pemasaran-properti. .Judul-Tabel}                                     |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

[Terkait tujuan penelitian, pemetaan tiap tahap dapat dijelaskan sebagai
berikut. Tujuan pertama, yaitu mengembangkan *chatbot* berbasis RAG
dengan akurasi jawaban di atas 90%, diselesaikan pada tahap perancangan
sistem dan implementasi. Tujuan kedua, yaitu membandingkan efisiensi
waktu dan akurasi antara metode manual dan chatbot berbasis RAG, dicapai
pada tahap evaluasi sistem. Tujuan ketiga, yaitu melakukan survei
kepuasan tenaga pemasaran, diselesaikan pada tahap *user testing*
melalui kuesioner dan wawancara. Dengan pemetaan ini, setiap tujuan
penelitian terhubung langsung dengan tahapan yang spesifik sehingga
hasil penelitian dapat diukur secara terstruktur dan konsisten.]{.mark}

![](media/image3.png){width="1.8949759405074367in"
height="6.989583333333333in"}

#### Gambar 3.1. Tahapan Penelitian {#gambar-3.1.-tahapan-penelitian .Judul-Tabel}

## Perencanaan Sistem {#perencanaan-sistem .Sub-2}

Perencanaan sistem dilakukan untuk memastikan bahwa rancangan chatbot AI
dapat diimplementasikan secara terstruktur dan sesuai dengan kebutuhan
penelitian. Tahap ini mencakup perancangan basis data, desain antarmuka
pengguna, logika *backend*, integrasi dengan *Large Language Models*,
serta rencana *deployment* sistem. Dengan adanya perencanaan yang jelas,
setiap komponen dapat saling terhubung dan mendukung fungsi utama
chatbot, yaitu memberikan informasi properti secara cepat, akurat, dan
relevan.

Pada tahap ini, peneliti memfokuskan diri pada dua aspek utama, yaitu
aspek teknis dan aspek fungsional. Aspek teknis meliputi pemilihan
teknologi yang digunakan, seperti Laravel untuk *backend*, *React.js*
untuk *frontend*, *MySQL* untuk basis data, dan *ChromaDB* sebagai
*vector database*. Sementara aspek fungsional meliputi bagaimana sistem
dapat menjawab pertanyaan pengguna dengan mempertahankan konteks
percakapan, sehingga chatbot dapat memberikan pengalaman interaksi yang
lebih natural.

Sub-bab berikutnya menjelaskan lebih detail mengenai setiap komponen
yang direncanakan, mulai dari perancangan struktur database, desain
antarmuka pengguna, logika *backend*, integrasi dengan OpenAI API
melalui LangChain, hingga strategi *deployment* sistem. Dengan
perencanaan menyeluruh ini, penelitian diharapkan menghasilkan chatbot
yang andal serta mampu memberikan kontribusi nyata bagi efisiensi tenaga
pemasaran properti.

### Perancangan Struktur Database {#perancangan-struktur-database .Sub-3a}

Perancangan struktur database dilakukan untuk memastikan data properti
dapat tersimpan secara terorganisir, mudah diakses, dan mendukung
kebutuhan pencarian real-time. Database dirancang menggunakan *MySQL*
karena sifatnya yang stabil, cepat, serta kompatibel dengan *framework*
Laravel yang digunakan pada *backend*. Prinsip normalisasi diterapkan
untuk mengurangi redundansi data dan menjaga integritas, sehingga setiap
entitas seperti properti, pengguna, dan riwayat percakapan dapat
dikelola dengan konsisten.

Dalam penelitian ini, struktur database dirancang dengan beberapa tabel
utama, yaitu tabel *properties, users,* dan *queries.* Tabel
*properties* menyimpan informasi detail properti, termasuk harga,
lokasi, tipe, fasilitas, dan status ketersediaan. Tabel *users*
menyimpan data pengguna seperti nama, email, dan peran (admin atau
tenaga pemasaran). Sedangkan tabel *queries* digunakan untuk mencatat
pertanyaan yang diajukan pengguna beserta respons yang diberikan
chatbot, sehingga dapat menjadi bahan analisis evaluasi sistem di tahap
berikutnya.

Selain itu, desain database ini dibuat agar mendukung proses konversi
data ke dalam bentuk *vector embeddings* yang akan digunakan oleh
*ChromaDB* sebagai *vector database*. Dengan integrasi ini, informasi
properti yang tersimpan di *MySQL* dapat diproses secara semantik
melalui LangChain dan OpenAI API. Rancangan ini memastikan bahwa data
tidak hanya terstruktur, tetapi juga siap digunakan dalam mekanisme
*Retrieval-Augmented Generation* untuk menghasilkan jawaban yang relevan
dan faktual.

### Desain Antarmuka Pengguna (UI/UX) {#desain-antarmuka-pengguna-uiux .Sub-3a}

Desain antarmuka pengguna (*User Interface/User Experience* atau UI/UX)
merupakan elemen penting dalam penelitian ini karena menentukan
bagaimana pengguna berinteraksi dengan chatbot. Antarmuka dirancang
menggunakan *React.js* untuk memastikan sistem dapat berjalan responsif
dan interaktif, baik di perangkat desktop maupun mobile. Prinsip desain
yang digunakan adalah kesederhanaan, kemudahan navigasi, dan konsistensi
tampilan agar pengguna dapat mengakses informasi properti tanpa
mengalami hambatan teknis.

Pada penelitian ini, antarmuka pengguna terdiri dari tiga komponen
utama. Pertama, halaman pencarian properti yang menyediakan filter
berdasarkan harga, lokasi, dan tipe unit sehingga tenaga pemasaran dapat
menemukan informasi dengan cepat. Kedua, halaman detail properti yang
menampilkan informasi lengkap mengenai harga, fasilitas, status
ketersediaan, dan opsi untuk menghubungi tenaga pemasaran. Ketiga,
halaman chatbot yang dirancang dengan format percakapan menggunakan
*chat bubble* agar interaksi terasa natural layaknya komunikasi dengan
asisten virtual.

Selain fungsi dasar, antarmuka pengguna juga mempertimbangkan kenyamanan
tenaga pemasaran dalam jangka panjang. Desain UI/UX dipadukan dengan
elemen visual sederhana namun informatif, sehingga data yang kompleks
tetap mudah dipahami. Integrasi dengan API Laravel memungkinkan data
yang disajikan pada antarmuka selalu diperbarui secara real-time. Dengan
perencanaan ini, chatbot diharapkan mampu memberikan pengalaman pengguna
yang intuitif, efisien, dan mendukung produktivitas tenaga pemasaran.

### Logika Backend dengan Laravel {#logika-backend-dengan-laravel .Sub-3a}

Logika *backend* dalam penelitian ini dibangun menggunakan *framework*
Laravel yang berfungsi sebagai penghubung antara antarmuka pengguna,
basis data, serta layanan eksternal seperti OpenAI API. Laravel dipilih
karena memiliki arsitektur yang rapi, dukungan ORM (*Object Relational
Mapping*) melalui Eloquent, serta kemudahan dalam membangun API yang
aman dan terstruktur. Dengan memanfaatkan fitur-fitur tersebut, sistem
dapat mengelola data properti, pengguna, dan riwayat percakapan dengan
lebih efisien.

Salah satu tugas utama *backend* adalah menyediakan *endpoint* API yang
memungkinkan *frontend* React.js berkomunikasi dengan basis data MySQL
maupun dengan layanan AI. Contohnya, API *GET /api/properties* digunakan
untuk mengambil data properti berdasarkan filter tertentu, sementara API
*POST /api/query* digunakan untuk menerima pertanyaan pengguna,
meneruskannya ke OpenAI API melalui LangChain, dan mengembalikan jawaban
ke *frontend*. Dengan pola ini, Laravel berperan sebagai pusat kendali
alur data di dalam sistem.

Selain itu, Laravel juga dilengkapi dengan fitur keamanan seperti
middleware, validasi input, serta autentikasi pengguna yang dapat diatur
melalui Laravel Sanctum atau Passport. Fitur-fitur tersebut memastikan
hanya pengguna terotorisasi yang dapat mengakses data sensitif atau
mengelola data properti. Dengan rancangan logika *backend* yang matang,
sistem chatbot dapat berjalan stabil, menjaga integritas data, serta
memastikan komunikasi antara pengguna dan layanan AI berlangsung secara
aman dan efisien.

### Integrasi OpenAI API melalui LangChain {#integrasi-openai-api-melalui-langchain .Sub-3a}

Integrasi OpenAI API melalui LangChain dilakukan agar sistem chatbot
mampu memahami pertanyaan pengguna dan memberikan jawaban yang relevan
berdasarkan data properti yang tersedia. OpenAI API berfungsi sebagai
penyedia *Large Language Model* (LLM) untuk menghasilkan jawaban
kontekstual, sementara LangChain berperan sebagai *framework* penghubung
yang mengatur alur data antara MySQL, *vector database*, dan LLM. Dengan
kombinasi ini, chatbot tidak hanya menghasilkan jawaban generatif,
tetapi juga memastikan setiap informasi yang diberikan sesuai dengan
data faktual.

Arsitektur sistem yang dirancang dalam penelitian ini ditunjukkan pada
Gambar 3.2. Diagram tersebut memperlihatkan dua alur utama, Pertama,
knowledge preparation pipeline, yaitu proses pembelajaran data yang
dilakukan secara periodik. Pada tahap ini, Laravel melakukan *query* ke
MySQL untuk mengambil data properti, kemudian data tersebut dikonversi
menjadi teks terstruktur. Selanjutnya, LangChain mengubah teks menjadi
*vector embeddings* yang disimpan di ChromaDB. Dengan adanya pipeline
ini, data properti selalu diperbarui dalam bentuk vektor yang siap
dipanggil saat chatbot menerima pertanyaan.

![](media/image4.png){width="5.458333333333333in" height="4.64375in"}

#### Gambar 3.2. Arsitektur Sistem Chatbot RAG {#gambar-3.2.-arsitektur-sistem-chatbot-rag .Judul-Tabel}

Kedua, user query pipeline, yaitu alur yang berjalan secara real-time
ketika pengguna berinteraksi dengan chatbot. Pertanyaan yang diajukan
melalui antarmuka React.js diteruskan ke Laravel sebagai *backend*, lalu
diproses oleh LangChain untuk mencari konteks yang relevan dari
ChromaDB. Hasil pencarian tersebut diberikan sebagai konteks tambahan ke
LLM melalui OpenAI API untuk menghasilkan jawaban yang natural, akurat,
dan sesuai dengan data yang telah di-*embed*. Jawaban kemudian
dikembalikan melalui Laravel ke antarmuka React.js dalam format
percakapan. Dengan rancangan ini, chatbot tidak hanya mampu menjawab
pertanyaan dasar, tetapi juga mempertahankan kesinambungan percakapan
melalui mekanisme *memory* yang disediakan LangChain.

### Deployment System {#deployment-system .Sub-3a}

Tahap deployment system dilakukan untuk memastikan chatbot dapat
digunakan secara nyata oleh tenaga pemasaran properti. Sistem
direncanakan dijalankan pada server berbasis VPS dengan sistem operasi
Ubuntu agar mudah dalam pengelolaan dan memiliki fleksibilitas dalam
konfigurasi. Setiap komponen, mulai dari Laravel sebagai backend,
React.js sebagai frontend, hingga integrasi dengan LangChain dan OpenAI
API, diatur agar berjalan secara terkoordinasi melalui manajemen layanan
seperti Nginx dan process manager.

Dalam implementasi, *backend* Laravel akan ditempatkan pada server
dengan koneksi langsung ke basis data MySQL untuk menjamin kecepatan
akses data. Sementara itu, *frontend* React.js akan dibangun (*build*)
menjadi berkas statis yang kemudian disajikan melalui Nginx. Integrasi
dengan ChromaDB dan OpenAI API juga diperhatikan agar koneksi tetap
stabil serta aman. Untuk keamanan tambahan, digunakan sertifikat SSL
sehingga komunikasi antara pengguna dan sistem terenkripsi dengan baik.

Selain penempatan komponen utama, sistem juga direncanakan mendukung
mekanisme *scalability* melalui penggunaan *load balancer* dan
pengaturan *horizontal scaling* jika jumlah pengguna meningkat.
Monitoring kinerja dilakukan dengan bantuan *logging* dan *server
monitoring tools* untuk mendeteksi masalah sejak dini. Dengan rancangan
*deployment* ini, chatbot dapat berjalan stabil, aman, dan siap
digunakan sebagai asisten virtual yang membantu efisiensi kerja tenaga
pemasaran properti.

## Pengujian Sistem {#pengujian-sistem .Sub-2}

Metode pengujian sistem dilakukan untuk memastikan chatbot yang
dikembangkan dapat berfungsi sesuai rancangan serta memenuhi kebutuhan
pengguna. Pengujian difokuskan pada kemampuan chatbot dalam menjawab
pertanyaan terkait properti, menjaga konteks percakapan, serta
memberikan respons dalam waktu yang wajar. Dengan pengujian ini,
peneliti dapat menilai apakah sistem sudah memenuhi kriteria fungsional
yang diharapkan sebelum dilakukan evaluasi lebih lanjut.

Pengujian dilakukan menggunakan skenario pertanyaan yang telah disusun
berdasarkan kebutuhan nyata tenaga pemasaran properti. Pertanyaan
mencakup aspek dasar seperti harga dan lokasi, hingga aspek lanjutan
seperti fasilitas, status ketersediaan, dan perbandingan properti.
Setiap pertanyaan akan diajukan kepada chatbot, kemudian jawaban yang
diberikan dibandingkan dengan data acuan dari basis data MySQL. Untuk
menjaga objektivitas, pengujian dilakukan oleh beberapa responden yang
mewakili pengguna akhir, yaitu tenaga pemasaran properti. Lampiran 1
adalah daftar pertanyaan uji yang akan digunakan dalam pengujian sistem.

## Rencana Evaluasi {#rencana-evaluasi .Sub-2}

Rencana evaluasi disusun untuk menilai keberhasilan sistem chatbot yang
dikembangkan. Evaluasi dilakukan dari dua sisi, yaitu evaluasi teknis
untuk mengukur kinerja sistem, serta evaluasi pengguna untuk menilai
kepuasan tenaga pemasaran yang menggunakan chatbot. Dengan adanya
evaluasi ini, peneliti dapat membuktikan apakah sistem memenuhi tujuan
penelitian yang telah ditetapkan.

Akurasi jawaban diukur dengan membandingkan jawaban chatbot dengan data
acuan dari basis data properti. Penilaian dilakukan menggunakan matriks
benar dan salah (lihat Lampiran 1), di mana benar artinya skor 10 dan
salah artinya skor 0. Persentase akurasi dihitung menggunakan rumus:

$$Akurasi = \ \frac{\sum_{}^{}{Skor\ Jawaban}}{Jumlah\ Pertanyaan} \times 100\%$$

Kecepatan respons diukur dengan menghitung rata-rata waktu yang
dibutuhkan chatbot untuk memberikan jawaban sejak pengguna mengirimkan
pertanyaan. Perhitungan dilakukan menggunakan alat pencatat waktu (log
sistem atau stopwatch) pada setiap pertanyaan. Nilai rata-rata respons
time diperoleh dengan rumus:

$$Waktu\ Respon\ rata - rata = \ \frac{\sum_{}^{}{Waktu\ Respon}}{Jumlah\ Pertanyaan}$$

Evaluasi kepuasan pengguna dilakukan dengan menyebarkan kuesioner kepada
tenaga pemasaran yang mencoba sistem. Kuesioner menggunakan skala Likert
1--5 (1 = sangat tidak setuju, 2 = Tidak Setuju, 3 = Netral, 4 = Setuju,
5 = Sangat Setuju) seperti ditunjukkan pada Tabel 3.2. Data kuesioner
akan diolah untuk menghitung nilai rata-rata setiap aspek, serta dibuat
grafik distribusi jawaban untuk menggambarkan tingkat kepuasan pengguna.

#### Tabel 3.2. Tabel Kuisioner Pengguna Chatbot {#tabel-3.2.-tabel-kuisioner-pengguna-chatbot .Judul-Tabel}

+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### **No** {#no .Judul-Tabel}     | #### **Pertanyaan** {#pertanyaan .Judul-Tabel}                                                                                                                                 | #### **Nilai ( 1 -- 5 )** {#nilai-1-5 .Judul-Tabel} |
+====================================+================================================================================================================================================================================+=====================================================+
| #### 1 {#section-4 .Judul-Tabel}   | #### Chatbot mudah digunakan dan dipahami cara kerjanya {#chatbot-mudah-digunakan-dan-dipahami-cara-kerjanya .Judul-Tabel}                                                     | ####  {#section-5 .Judul-Tabel}                     |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 2 {#section-6 .Judul-Tabel}   | #### Jawaban yang diberikan chatbot jelas dan sesuai dengan pertanyaaan {#jawaban-yang-diberikan-chatbot-jelas-dan-sesuai-dengan-pertanyaaan .Judul-Tabel}                     | ####  {#section-7 .Judul-Tabel}                     |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 3 {#section-8 .Judul-Tabel}   | #### Waktu respons chatbot cepat dan tidak membuat saya menunggu lama. {#waktu-respons-chatbot-cepat-dan-tidak-membuat-saya-menunggu-lama. .Judul-Tabel}                       | ####  {#section-9 .Judul-Tabel}                     |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 4 {#section-10 .Judul-Tabel}  | #### Chatbot membantu saya menemukan informasi properti dengan lebih efisien. {#chatbot-membantu-saya-menemukan-informasi-properti-dengan-lebih-efisien. .Judul-Tabel}         | ####  {#section-11 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 5 {#section-12 .Judul-Tabel}  | #### Chatbot dapat memahami pertanyaan lanjutan (konteks percakapan). {#chatbot-dapat-memahami-pertanyaan-lanjutan-konteks-percakapan. .Judul-Tabel}                           | ####  {#section-13 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 6 {#section-14 .Judul-Tabel}  | #### Chatbot memberikan informasi yang relevan dan sesuai dengan data properti. {#chatbot-memberikan-informasi-yang-relevan-dan-sesuai-dengan-data-properti. .Judul-Tabel}     | ####  {#section-15 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 7 {#section-16 .Judul-Tabel}  | #### Chatbot mempermudah pekerjaan saya sebagai tenaga pemasaran. {#chatbot-mempermudah-pekerjaan-saya-sebagai-tenaga-pemasaran. .Judul-Tabel}                                 | ####  {#section-17 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 8 {#section-18 .Judul-Tabel}  | #### Chatbot meningkatkan produktivitas dalam memberikan informasi ke pelanggan. {#chatbot-meningkatkan-produktivitas-dalam-memberikan-informasi-ke-pelanggan. .Judul-Tabel}   | ####  {#section-19 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 9 {#section-20 .Judul-Tabel}  | #### Saya puas dengan performa chatbot secara keseluruhan. {#saya-puas-dengan-performa-chatbot-secara-keseluruhan. .Judul-Tabel}                                               | ####  {#section-21 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+
| #### 10 {#section-22 .Judul-Tabel} | #### Saya bersedia menggunakan chatbot ini untuk mendukung pekerjaan sehari-hari. {#saya-bersedia-menggunakan-chatbot-ini-untuk-mendukung-pekerjaan-sehari-hari. .Judul-Tabel} | ####  {#section-23 .Judul-Tabel}                    |
+------------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------+

# BAB IV HASIL DAN PEMBAHASAN

## 4.1 Hasil Implementasi Sistem

Implementasi sistem chatbot AI untuk agen properti dilakukan melalui
beberapa tahapan yang saling berkaitan, mulai dari pengumpulan data,
perancangan database, desain antarmuka pengguna, konversi database
menjadi vektor, hingga integrasi dengan API OpenAI untuk menghasilkan
jawaban yang relevan. Subbab ini akan menjelaskan secara rinci setiap
tahapan implementasi.

### Pengumpulan Data {#pengumpulan-data .Sub-3a}

Data diperoleh dari berbagai kantor properti mitra yang tergabung dalam
jaringan penelitian diperoleh jumlah data sebanyak 750 data dapat
dilihat pada Tabel 4.4. Sumber data ini bervariasi dalam hal format dan
kelengkapan informasi, mulai dari file Excel, CSV, hingga database
internal milik kantor. Informasi yang dikumpulkan mencakup detail
properti seperti harga, lokasi, tipe, fasilitas, dan status
ketersediaan. Karena setiap sumber memiliki struktur data yang berbeda,
dilakukan proses data cleaning dan normalisasi untuk menyeragamkan
format agar dapat diolah lebih lanjut. Contoh data yang diperoleh dari
beberapa kantor properti di Jakarta ditunjukkan pada Tabel 4.1, Tabel
4.2, dan Table 4.3.

#### Tabel 4.1. Contoh Data dari Kantor Properti A {#tabel-4.1.-contoh-data-dari-kantor-properti-a .Judul-Tabel}

  ------------------------------------------------------------------------------------------------
  **ID         **Nama       **Harga (Rp)**  **Alamat**   **Tipe       **Fasilitas**   **Status**
  Properti**   Properti**                                Properti**                   
  ------------ ------------ --------------- ------------ ------------ --------------- ------------
  A001         Rumah Kemang 5.500.000.000   Kemang,      Rumah        Garasi, Taman,  Tersedia
               Tipe 200                     Jakarta                   Kolam Renang    
                                            Selatan                                   

  A002         Rumah        4.200.000.000   Cilandak,    Rumah        Carport, Taman  Terjual
               Cilandak                     Jakarta                                   
               Tipe 150                     Selatan                                   
  ------------------------------------------------------------------------------------------------

Perbedaan struktur kolom pada setiap sumber data inilah yang kemudian
menjadi dasar perancangan database MySQL yang terstandarisasi

#### Tabel 4.2. Contoh Data dari Kantor Properti B {#tabel-4.2.-contoh-data-dari-kantor-properti-b .Judul-Tabel}

  -------------------------------------------------------------------------------------------
  **Kode   **Nama     **Harga (Rp)**  **Lokasi   **Jenis   **Fasilitas**   **Ketersediaan**
  Unit**   Unit**                     Proyek**   Unit**                    
  -------- ---------- --------------- ---------- --------- --------------- ------------------
  B005     Ruko       7.800.000.000   Pantai     Ruko      Parkir Luas, AC Terjual
           Pantai                     Indah                Central         
           Indah                      Kapuk,                               
                                      Jakarta                              

  B008     Ruko Pluit 6.500.000.000   Pluit,     Ruko      Parkir, Toilet  Tersedia
           Junction                   Jakarta                              
                                      Utara                                
  -------------------------------------------------------------------------------------------

#### Tabel 4.3. Contoh Data dari Kantor Properti C {#tabel-4.3.-contoh-data-dari-kantor-properti-c .Judul-Tabel}

  ----------------------------------------------------------------------------------------
  **Unit   **Nama        **Harga (Rp)**  **Area**    **Tipe   **Fasilitas**   **Status**
  ID**     Apartemen**                               Unit**                   
  -------- ------------- --------------- ----------- -------- --------------- ------------
  C010     Apartemen     2.300.000.000   Sudirman,   2BR      Gypm, Kolam     Tersedia
           Sudirman Park                 jakata               Renang          
           Lantai 8                                                           

  C012     Apartemen     3.100.000.000   Thamrin,    3BR      Gym, Kolam      Tersedia
           Thamrin                       Jakarta              Renang          
           Executive L17                                                      
  ----------------------------------------------------------------------------------------

#### Tabel 4.4. Rekapitulasi Jumlah Data yang Diperoeh {#tabel-4.4.-rekapitulasi-jumlah-data-yang-diperoeh .Judul-Tabel}

  -----------------------------------
  **Kantor        **Jumlah Data**
  Properti**      
  --------------- -------------------
  A               100

  B               400

  C               250

  **Total**       **750**
  -----------------------------------

### Hasil Perancangan Database MySQL {#hasil-perancangan-database-mysql .Sub-3a}

Berdasarkan data yang diperoleh dari berbagai kantor properti, dilakukan
standarisasi struktur untuk mengakomodasi variasi penamaan kolom dan
format yang berbeda-beda. Proses perancangan mengikuti prinsip
normalisasi hingga minimal bentuk ke-3 (3NF) untuk meminimalkan
redundansi dan memastikan integritas data. Hasil penyusunan database
dalam bentuk ERD dapat dilihat pada Gambar 4.1

### Hasil Perancangan UI/UX Design {#hasil-perancangan-uiux-design .Sub-3a}

Hasil implementasi antarmuka pengguna menggunakan React.js menghasilkan
tampilan percakapan berbasis *chat bubble* yang sederhana, bersih, dan
mudah dipahami. Setiap pesan pengguna ditampilkan di sisi kanan dengan
warna berbeda, sedangkan jawaban chatbot berada di sisi kiri dengan
format yang rapi. Jawaban yang memuat daftar tipe properti, spesifikasi,
dan harga diformat dalam bentuk poin bernomor untuk memudahkan
pembacaan. Tampilan ini dioptimalkan untuk perangkat seluler sehingga
seluruh elemen tetap terbaca jelas dan dapat diakses dengan mudah.
Gambar 4.2 menunjukkan salah satu hasil implementasi di mana chatbot
menampilkan daftar tipe rumah, spesifikasi, dan harga berdasarkan
pertanyaan yang diajukan. Jawaban yang diberikan bersifat terstruktur,
memudahkan pengguna untuk membandingkan pilihan properti. Selain itu,
pengguna dapat melanjutkan percakapan dengan pertanyaan lanjutan yang
masih terkait konteks sebelumnya, dan sistem akan memberikan jawaban
yang sesuai.

![](media/image5.png){width="3.8959536307961504in"
height="4.906299212598425in"}

#### Gambar 4.1. Gambar ERD {#gambar-4.1.-gambar-erd .Judul-Tabel}

#### Gambar 4.2. Desain frontend chatbot {#gambar-4.2.-desain-frontend-chatbot .Judul-Tabel}

### Konversi Database MySQL Menjadi Vektor Database {#konversi-database-mysql-menjadi-vektor-database .Sub-3a}

Salah satu tahapan penting dalam implementasi sistem chatbot ini adalah
mengubah data properti yang tersimpan di MySQL menjadi *vector
embeddings* yang dapat digunakan untuk pencarian semantik (*semantic
search*). Proses ini memungkinkan chatbot memberikan jawaban relevan
meskipun pertanyaan pengguna tidak persis sama dengan kata-kata yang
digunakan dalam data asli.

Tahapan konversi dimulai dari membuat format teks yang diekstrak dari
database dari table *properties, locations, property_types*. Gambar 4.3
menunjukkan contoh teks yang dihasilkan dari hasil konversi

#### Gambar 4.3. Hasil konversi database menjadi teks format {#gambar-4.3.-hasil-konversi-database-menjadi-teks-format .Judul-Tabel}

### Koneksi ke LLM OpenAI API {#koneksi-ke-llm-openai-api .Sub-3a}

Tahap ini menjelaskan proses sistem memproses pertanyaan dari pengguna
hingga menghasilkan jawaban yang relevan. Seluruh alur dikembangkan
dengan memanfaatkan *Laravel* sebagai backend, *LangChain* sebagai
*framework* penghubung, *ChromaDB* untuk pencarian semantik, dan *OpenAI
LLM* untuk membentuk respons akhir. Gambar 4.4 menerangkan template
prompt yang digunakan untuk menghasilkan jawaban dari LLM

#### Gambar 4.4. Template Prompt {#gambar-4.4.-template-prompt .Judul-Tabel}

### Hasil Jawaban Chatbot {#hasil-jawaban-chatbot .Sub-3a}

Tahap ini bertujuan untuk menguji apakah sistem chatbot yang telah
diimplementasikan mampu memberikan jawaban yang relevan, akurat, dan
sesuai konteks pertanyaan pengguna. Pengujian dilakukan dengan
menggunakan data properti dari tiga kantor (A, B, dan C) yang telah
dikonversi menjadi vector database.

#### Tabel 4.5. Contoh Pertanyaan dan Hasil Jawaban {#tabel-4.5.-contoh-pertanyaan-dan-hasil-jawaban .Judul-Tabel}

  ------------------------------------------------------------------------------------
  **No.**   **Pertanyaan      **Ringkasan Jawaban      **Akurasi**     **Waktu
            Pengguna**        Chatbot**                                Respons**
  --------- ----------------- ------------------------ --------------- ---------------
  1         Berapa harga      Menampilkan 2 properti   [100 %]{.mark}  [1,5
            rumah di Kemang   di Kemang, salah satunya                 detik]{.mark}
            dengan 3 kamar    Rumah Kemang Tipe 200                    
            tidur ?           dengan harga Rp. 5.5M                    

  2         Tampilkan         Menampilkan Apartemen    [100%]{.mark}   [1,7
            apartemen di      Sudirman Park lantai 8                   detik]{.mark}
            Sudirman dengan 2 harga 2,3M dengan                        
            kamar tidur       fasilitas gym dan kolam                  
            dibawah 3M        renang                                   

  3         Berapa jumlah     Maaf, saya tidak         [100%]{.mark}   [1,5
            kota di Indonesia menemukan informasi                      detik]{.mark}
                              tersebut                                 
  ------------------------------------------------------------------------------------

## 4.2 Pengujian Sistem

Pengujian sistem dilakukan untuk memastikan bahwa chatbot AI yang
dikembangkan dapat memenuhi tujuan penelitian, yaitu memberikan
informasi properti secara cepat, akurat, dan relevan sesuai kebutuhan
tenaga pemasaran. Pengujian meliputi evaluasi akurasi jawaban, kecepatan
respons, dan pengalaman pengguna (User Experience).

### 4.2.1 Pengujian Akurasi Jawaban {#pengujian-akurasi-jawaban .Sub-3a}

Pengujian akurasi dilakukan dengan memberikan 20 pertanyaan yang
mencakup berbagai skenario pencarian properti, mulai dari pertanyaan
sederhana hingga kompleks. Jawaban chatbot dibandingkan dengan data yang
ada di database untuk menilai kesesuaiannya. Hasil pengujian menunjukkan
bahwa chatbot mampu memberikan jawaban yang sesuai dengan data yang
tersedia dalam 95% kasus. Ketidaksesuaian jawaban umumnya terjadi pada
pertanyaan yang memerlukan interpretasi lebih luas atau data yang kurang
lengkap di database. Lampiran 2 menerangkan perhitungan akurasi yang
dihasilkan

### 4.2.2 Pengujian Kecepatan Respons {#pengujian-kecepatan-respons .Sub-3a}

Kecepatan respons diukur mulai dari saat pertanyaan dikirim oleh
pengguna hingga jawaban ditampilkan di antarmuka. Pengujian dilakukan
pada jaringan internet stabil dengan spesifikasi server yang digunakan
dalam implementasi sistem. Pengujian kecepatan menghasilkan waktu
respons tercepat adalah 1,4 detik dan waktu respons terlama adalah 2,3
detik dengan rata-rata waktu respons adalah 1.7 detik. Tabel perhitungan
waktu respons rata-rata ditampilkan pada Lampiran 3.

### 4.2.3 Pengujian UX (*User Experience)* {#pengujian-ux-user-experience .Sub-3a}

Untuk mengukur pengalaman pengguna, dilakukan survei terhadap 10 tenaga
pemasaran properti yang menggunakan chatbot dalam skenario kerja nyata.
Responden diminta memberikan penilaian pada skala 1--5 terhadap 10
dimensi yang mengambarkan kemudahan penggunaan, manfaat, kecepatan, dan
kepercayaan pada jawaban. Hasil survei dapat dilihat pada Tabel 4.6

#### Tabel 4.6. Survei Kuisioner Pengguna Chatbot {#tabel-4.6.-survei-kuisioner-pengguna-chatbot .Judul-Tabel}

+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### **No** {#no-1 .Judul-Tabel}   | #### **Pertanyaan** {#pertanyaan-1 .Judul-Tabel}                                                                                                                                 | #### **Nilai Rata-Rata** {#nilai-rata-rata .Judul-Tabel} |
+====================================+==================================================================================================================================================================================+==========================================================+
| #### 1 {#section-24 .Judul-Tabel}  | #### Chatbot mudah digunakan dan dipahami cara kerjanya {#chatbot-mudah-digunakan-dan-dipahami-cara-kerjanya-1 .Judul-Tabel}                                                     | #### [4.60]{.mark} {#section-25 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 2 {#section-26 .Judul-Tabel}  | #### Jawaban yang diberikan chatbot jelas dan sesuai dengan pertanyaaan {#jawaban-yang-diberikan-chatbot-jelas-dan-sesuai-dengan-pertanyaaan-1 .Judul-Tabel}                     | #### [4.75]{.mark} {#section-27 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 3 {#section-28 .Judul-Tabel}  | #### Waktu respons chatbot cepat dan tidak membuat saya menunggu lama. {#waktu-respons-chatbot-cepat-dan-tidak-membuat-saya-menunggu-lama.-1 .Judul-Tabel}                       | #### [4.90]{.mark} {#section-29 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 4 {#section-30 .Judul-Tabel}  | #### Chatbot membantu saya menemukan informasi properti dengan lebih efisien. {#chatbot-membantu-saya-menemukan-informasi-properti-dengan-lebih-efisien.-1 .Judul-Tabel}         | #### [4.65]{.mark} {#section-31 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 5 {#section-32 .Judul-Tabel}  | #### Chatbot dapat memahami pertanyaan lanjutan (konteks percakapan). {#chatbot-dapat-memahami-pertanyaan-lanjutan-konteks-percakapan.-1 .Judul-Tabel}                           | #### [4.45]{.mark} {#section-33 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 6 {#section-34 .Judul-Tabel}  | #### Chatbot memberikan informasi yang relevan dan sesuai dengan data properti. {#chatbot-memberikan-informasi-yang-relevan-dan-sesuai-dengan-data-properti.-1 .Judul-Tabel}     | #### [4.75]{.mark} {#section-35 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 7 {#section-36 .Judul-Tabel}  | #### Chatbot mempermudah pekerjaan saya sebagai tenaga pemasaran. {#chatbot-mempermudah-pekerjaan-saya-sebagai-tenaga-pemasaran.-1 .Judul-Tabel}                                 | #### [4.80]{.mark} {#section-37 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 8 {#section-38 .Judul-Tabel}  | #### Chatbot meningkatkan produktivitas dalam memberikan informasi ke pelanggan. {#chatbot-meningkatkan-produktivitas-dalam-memberikan-informasi-ke-pelanggan.-1 .Judul-Tabel}   | #### [4.85]{.mark} {#section-39 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 9 {#section-40 .Judul-Tabel}  | #### Saya puas dengan performa chatbot secara keseluruhan. {#saya-puas-dengan-performa-chatbot-secara-keseluruhan.-1 .Judul-Tabel}                                               | #### [4.90]{.mark} {#section-41 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+
| #### 10 {#section-42 .Judul-Tabel} | #### Saya bersedia menggunakan chatbot ini untuk mendukung pekerjaan sehari-hari. {#saya-bersedia-menggunakan-chatbot-ini-untuk-mendukung-pekerjaan-sehari-hari.-1 .Judul-Tabel} | #### [4.90]{.mark} {#section-43 .Judul-Tabel}            |
+------------------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+----------------------------------------------------------+

Hasil menunjukkan nilai rata-rata [4.76]{.mark} dari total 5
menggambarkan bahwa pengguna menilai chatbot sangat membantu dalam
pekerjaan mereka, terutama dalam menghemat waktu pencarian informasi dan
mengurasi resiko kesalahan data.

## 4.3 Evaluasi Sistem 

Evaluasi sistem dilakukan untuk menilai sejauh mana tujuan penelitian
telah tercapai, membandingkan hasil penelitian ini dengan penelitian
terdahulu, serta mengidentifikasi kelebihan, kelemahan, dan kendala yang
ditemukan selama proses implementasi dan pengujian.

### 4.3.1 Pencapaian Tujuan Penelitian {#pencapaian-tujuan-penelitian .Sub-3a}

Berdasarkan hasil implementasi dan pengujian, sistem chatbot yang
dikembangkan telah berhasil mencapai seluruh tujuan penelitian yang
telah ditetapkan. Tujuan pertama, yaitu mengembangkan chatbot berbasis
*Retrieval-Augmented Generation* (RAG) dengan akurasi jawaban lebih dari
90%, tercapai dengan nilai akurasi sebesar 95% dari total 20 pertanyaan
uji. Hasil ini menunjukkan bahwa sistem mampu memberikan jawaban yang
relevan dan sesuai dengan data properti yang tersedia.

Tujuan kedua, yaitu meningkatkan efisiensi waktu pencarian informasi,
juga berhasil dicapai. Chatbot mampu memberikan jawaban dengan rata-rata
waktu respons 1,7 detik, jauh lebih cepat dibandingkan pencarian manual
yang membutuhkan waktu antara 30 hingga 60 detik. Pencapaian ini
membuktikan bahwa chatbot dapat mempercepat proses kerja tenaga
pemasaran dalam memberikan informasi kepada calon pembeli.

Selanjutnya, tujuan ketiga, yaitu menilai kepuasan pengguna terhadap
sistem, juga menunjukkan hasil positif. Berdasarkan survei yang
diberikan kepada tenaga pemasaran, diperoleh skor rata-rata 4,76 dari 5,
yang berarti mayoritas responden merasa puas menggunakan chatbot ini.
Dengan demikian, ketiga tujuan penelitian yang telah dirumuskan pada Bab
I berhasil dicapai sesuai dengan harapan.

### 4.3.2 Evaluasi Kendala dan Solusi {#evaluasi-kendala-dan-solusi .Sub-3a}

Selama proses implementasi dan pengujian sistem, terdapat beberapa
kendala yang memengaruhi kinerja chatbot. Salah satu kendala utama
adalah perbedaan format data dari berbagai kantor properti yang menjadi
sumber dataset. Hal ini menyebabkan proses normalisasi data cukup
memakan waktu sebelum data dapat disimpan ke dalam MySQL. Selain itu,
kinerja API OpenAI terkadang mengalami penurunan pada jam-jam sibuk,
yang berdampak pada meningkatnya waktu respons chatbot. Beberapa data
properti juga ditemukan tidak memiliki atribut lengkap, seperti
informasi fasilitas atau luas bangunan, sehingga menurunkan akurasi
jawaban yang diberikan.

Untuk mengatasi kendala perbedaan format data, dikembangkan solusi
berupa pembuatan modul ETL (*Extract, Transform, Load*) otomatis. Modul
ini memungkinkan proses normalisasi data dilakukan secara cepat dan
konsisten sebelum dimasukkan ke database. Dengan adanya modul ETL,
integritas dan keseragaman data dapat lebih terjamin, sehingga sistem
mampu mengolah informasi properti dengan lebih efisien.

Selain itu, diterapkan mekanisme caching lokal untuk menyimpan hasil
permintaan yang sering digunakan, sehingga mengurangi ketergantungan
pada permintaan API berulang dan mempercepat respons chatbot. Sistem
juga dilengkapi dengan proses validasi serta pengisian data otomatis
(data filling) untuk melengkapi atribut yang kosong atau tidak lengkap.
Dengan langkah-langkah ini, kualitas data tetap terjaga dan kinerja
chatbot dapat lebih stabil meskipun menghadapi kendala teknis maupun
keterbatasan data.

# BAB V KESIMPULAN DAN SARAN

Penelitian ini bertujuan untuk merancang dan mengimplementasikan chatbot
AI berbasis Retrieval-Augmented Generation (RAG) sebagai asisten virtual
untuk agen properti, yang mampu memberikan informasi properti secara
cepat, akurat, dan relevan. Sistem dikembangkan dengan mengintegrasikan
Laravel sebagai backend, React.js sebagai frontend, MySQL sebagai
penyimpanan data terstruktur, ChromaDB sebagai vector database,
LangChain sebagai penghubung proses retrieval, dan OpenAI LLM sebagai
model generative. Berdasarkan hasil implementasi, pengujian, dan
evaluasi, diperoleh beberapa kesimpulan sebagai berikut :

1.  Tujuan penelitian telah tercapai dengan tingkat akurasi chatbot
    sebesar 95%, waktu respons rata-rata 1,7 detik, dan skor kepuasan
    pengguna rata-rata 4,76 dari 5.

2.  Sistem berhasil menstandarisasi data properti dari berbagai kantor
    dengan format berbeda ke dalam struktur database MySQL yang seragam,
    sehingga mempermudah proses integrasi, pencarian, dan konversi ke
    vector database.

3.  Pendekatan RAG yang digunakan memungkinkan chatbot memberikan
    jawaban berbasis data faktual dari vector database, sekaligus
    mengurangi risiko *hallucination* pada model LLM.

4.  Antarmuka pengguna yang dibangun dengan React.js memberikan
    pengalaman penggunaan yang sederhana, responsif, dan intuitif,
    sehingga memudahkan tenaga pemasaran dalam mengakses informasi.

5.  Sistem terbukti mampu menangani pertanyaan kompleks yang melibatkan
    kombinasi filter lokasi, harga, dan fasilitas, serta dapat diakses
    secara lintas perangkat melalui web.

6.  Keterbatasan sistem terletak pada ketergantungan terhadap koneksi
    internet dan API OpenAI, serta pada data yang kurang lengkap untuk
    beberapa properti, yang dapat mempengaruhi akurasi hasil pencarian.

Dengan pencapaian ini, penelitian ini membuktikan bahwa chatbot AI
berbasis RAG dapat menjadi solusi efektif untuk mendukung pekerjaan
tenaga pemasaran properti, meningkatkan efisiensi pencarian informasi,
dan mengurangi risiko kesalahan data.

Adapun saran untuk pengembangan selanjutnya antara lain :

1.  Menambahkan fitur memori kontekstual agar chatbot dapat
    mempertahankan konteks percakapan antar sesi.

2.  Mengembangkan modul ETL otomatis untuk mempercepat proses
    normalisasi data dari berbagai sumber.

3.  Mengimplementasikan caching lokal untuk mengurangi waktu respons
    pada pertanyaan yang sering diajukan.

4.  Mengintegrasikan sistem dengan platform komunikasi populer seperti
    WhatsApp atau Telegram agar lebih mudah diakses oleh tenaga
    pemasaran.

# DAFTAR PUSTAKA

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P.,
\... Amodei, D. (2020). Language models are few-shot learners. *arXiv
preprint arXiv:2005.14165*. <https://arxiv.org/abs/2005.14165>

Febriansyah, E., & Nirmala, E. (2023). Perancangan sistem informasi jual
beli properti menggunakan chat bot Telegram yang terintegrasi dengan
web. *Journal of Real Estate Innovation and Development, 5*(1), 50-65.
<https://jurnal.portalpublikasi.id/index.php/JORAPI/article/view/174/141>

Goodfellow, I., Bengio, Y., & Courville, A. (2016). *Deep learning*. MIT
Press.

Jurafsky, D., & Martin, J. H. (2020). *Speech and language processing*
(3rd ed.). Pearson.

Lewers, J., et al. (2024). Comparative methods for building chatbots:
Open source, hybrid, and fully integrated large language models.
*ResearchGate*.
<https://www.researchgate.net/publication/386262665_Comparative_Methods_for_Building_Chatbots_Open_Source_Hybrid_and_Fully_Integrated_Large_Language_Models>

Mashud, M., & Wisda, W. (2019). Laravel for scalable backend systems: A
study on PHP frameworks for modern web applications. *Journal of
Software Engineering, 8*(4), 215-230.

Mullins, C. (2020). *Database management systems* (3rd ed.).
Addison-Wesley.

Norvig, P., & Russell, S. J. (2021). *Artificial intelligence: A modern
approach* (4th ed.). Pearson.

Rane, N., Gupta, P., & Verma, S. (2024). Artificial intelligence,
natural language processing, and machine learning to enhance e-service
quality on e-commerce platforms. *International Journal of Artificial
Intelligence Research, 9*(1), 25-45.
<https://www.researchgate.net/publication/382174062>

Ratnawati, A., Aman, A., Pasnur, A., & Muniar, Y. (2021). Sistem
informasi pemasaran perumahan dengan fitur chatbot pada PT. Abidzar
Artana Mandiri. *Semantech Journal, 4*(1), 12-25. Retrieved from
<https://jurnal.poligon.ac.id/index.php/semantech/article/view/820>

Afifah, N., Sari, R., & Pradipta, A. (2023). Pengaruh penggunaan dan
respons chatbot terhadap kepuasan konsumen e-commerce. *International
Journal of Digital Business, 7*(3), 45-60.
<https://www.researchgate.net/publication/386598770_Pengaruh_Penggunaan_Dan_Respons_Chatbot_Terhadap_Kepuasan_Konsumen_E-Commerce>

Salem, H., & Mazzara, M. (2020). *ML-based Telegram bot for real estate
price prediction*. Journal of Physics: Conference Series.
<https://www.researchgate.net/publication/344840301_ML-based_Telegram_bot_for_real_estate_price_prediction>

Dobbala, M. K., & Lingo, M. S. S. (2024). *Conversational AI and
Chatbots: Enhancing User Experience on Websites*. American Journal of
Computer Science and Technology, 7(3), 62-70. Retrieved from
<https://www.researchgate.net/publication/383035963_Conversational_AI_and_Chatbots_Enhancing_User_Experience_on_Websites>

Towhidul, I., & Oshita, M. (2025). *Artificial intelligence (AI)
applications for marketing: Real-Time Analytics in Banking Finance*.
International Conference on Artificial Intelligence in Education
(ICAIE-25), Tokyo, Japan.
<https://www.researchgate.net/publication/387750832_Artificial_intelligence_AI_applications_for_marketing_Real-Time_Analytics_in_Banking_Finance>

Mali, Y. K., Khemnar, D. S., Varpe, S. S., Rathod, V. U., & Kolpe, S. B.
(2023). *Web and Android Application for Real Estate Business
Management*. 2023 IEEE 11th Region 10 Humanitarian Technology Conference
(R10-HTC).
[https://www.researchgate.net/publication/379087185_Web_and_Android_Application_for_Real_Estate_Business_Managemen](https://www.researchgate.net/publication/379087185_Web_and_Android_Application_for_Real_Estate_Business_Management)

Febrianto, F., & Putri, R. D. (2023). *Implementasi Chatbot Sebagai Agen
Perumahan untuk Meningkatkan Efisiensi dan Akurasi Informasi Menggunakan
Einstein Bot*. Jurnal Teknologi Informatika dan Komputer, 9(1), 320-327.
<https://www.researchgate.net/publication/376054638_Implementasi_Chatbot_Sebagai_Agen_Perumahan_untuk_Meningkatkan_Efisiensi_dan_Akurasi_Informasi_Menggunakan_Einstein_Bot>

**\**
LAMPIRAN

[]{#_Toc207294953 .anchor}Lampiran 1. Daftar Pertanyaan Uji Chatbot

  --------------------------------------------------------------------------------
   **No.**  **Kategori**   **Pertanyaan**           **Jawaban Chatbot**  **Benar /
                                                                         Salah**
  --------- -------------- ------------------------ -------------------- ---------
      1     Harga          Berapa harga rumah tipe                       
                           70 di Medan Johor?                            

      2     Harga          Berapa harga rumah tipe                       
                           90 di Grand Patriot?                          

      3     Harga          Berapa kisaran harga                          
                           rumah di kawasan Cemara                       
                           Asri?                                         

      4     Lokasi         Apakah ada rumah yang                         
                           dijual di Ringroad City?                      

      5     Lokasi         Apakah ada properti di                        
                           kawasan Setia Budi?                           

      6     Lokasi         Di mana lokasi proyek                         
                           Beverly Diamond?                              

      7     Fasilitas      Apakah rumah di Cemara                        
                           Asri memiliki kolam                           
                           renang?                                       

      8     Fasilitas      Rumah tipe 120 di Grand                       
                           Patriot apakah ada                            
                           garasi?                                       

      9     Fasilitas      Apakah unit di Ringroad                       
                           City menyediakan taman                        
                           bermain?                                      

     10     Status Unit    Apakah rumah tipe 45 di                       
                           Grand Patriot masih                           
                           tersedia?                                     

     11     Status Unit    Apakah unit tipe 150 di                       
                           Beverly Diamond sudah                         
                           terjual?                                      

     12     Status Unit    Apakah masih ada kavling                      
                           kosong di Cemara Asri?                        

     13     Perbandingan   Lebih murah mana, rumah                       
                           tipe 90 atau tipe 120 di                      
                           Grand Patriot?                                

     14     Perbandingan   Mana yang lebih besar,                        
                           rumah tipe 70 di Medan                        
                           Johor atau tipe 90 di                         
                           Ringroad?                                     

     15     Perbandingan   Lebih banyak fasilitas                        
                           mana, Cemara Asri atau                        
                           Ringroad City?                                

     16     Promosi        Apakah ada promo DP                           
                           untuk pembelian rumah di                      
                           Grand Patriot?                                

     17     Promosi        Apakah ada diskon untuk                       
                           pembelian tunai?                              

     18     Promosi        Apakah ada program                            
                           cicilan KPR untuk rumah                       
                           tipe 120?                                     

     19     Umum           Siapa developer dari                          
                           proyek Beverly Diamond?                       

     20     Umum           Kapan proyek Grand                            
                           Patriot mulai dibangun?                       
  --------------------------------------------------------------------------------

[]{#_Toc207294954 .anchor}Lampiran 2. Perhitungan Akurasi Jawaban

  ------------------------------------------------------------------------------------------
   **No.**  **Kategori**   **Pertanyaan**           **Jawaban Chatbot**     **Benar /
                                                                            Salah**
  --------- -------------- ------------------------ ----------------------- ----------------
      1     Harga          Berapa harga rumah tipe  [Rp 750.000.000]{.mark} [Benar]{.mark}
                           70 di Medan Johor?                               

      2     Harga          Berapa harga rumah tipe  [Rp                     [Benar]{.mark}
                           90 di Grand Patriot?     1.250.000.000]{.mark}   

      3     Harga          Berapa kisaran harga     [Rp 2--5 miliar]{.mark} [Benar]{.mark}
                           rumah di kawasan Cemara                          
                           Asri?                                            

      4     Lokasi         Apakah ada rumah yang    [Ada, tersedia beberapa [Benar]{.mark}
                           dijual di Ringroad City? unit]{.mark}            

      5     Lokasi         Apakah ada properti di   [Tidak tersedia]{.mark} [Benar]{.mark}
                           kawasan Setia Budi?                              

      6     Lokasi         Di mana lokasi proyek    [Jl. Ringroad           [Benar]{.mark}
                           Beverly Diamond?         Medan]{.mark}           

      7     Fasilitas      Apakah rumah di Cemara   [Ya, beberapa unit      [Benar]{.mark}
                           Asri memiliki kolam      memiliki]{.mark}        
                           renang?                                          

      8     Fasilitas      Rumah tipe 120 di Grand  [Ya, tersedia           [Benar]{.mark}
                           Patriot apakah ada       garasi]{.mark}          
                           garasi?                                          

      9     Fasilitas      Apakah unit di Ringroad  [Ya, ada fasilitas      [Benar]{.mark}
                           City menyediakan taman   taman]{.mark}           
                           bermain?                                         

     10     Status Unit    Apakah rumah tipe 45 di  [Sudah habis            [Salah]{.mark}
                           Grand Patriot masih      terjual]{.mark}         
                           tersedia?                                        

     11     Status Unit    Apakah unit tipe 150 di  [Masih tersedia]{.mark} [Benar]{.mark}
                           Beverly Diamond sudah                            
                           terjual?                                         

     12     Status Unit    Apakah masih ada kavling [Ada kavling            [Benar]{.mark}
                           kosong di Cemara Asri?   tersedia]{.mark}        

     13     Perbandingan   Lebih murah mana, rumah  [Tipe 90 lebih          [Benar]{.mark}
                           tipe 90 atau tipe 120 di murah]{.mark}           
                           Grand Patriot?                                   

     14     Perbandingan   Mana yang lebih besar,   [Tipe 90 lebih          [Benar]{.mark}
                           rumah tipe 70 di Medan   besar]{.mark}           
                           Johor atau tipe 90 di                            
                           Ringroad?                                        

     15     Perbandingan   Lebih banyak fasilitas   [Cemara Asri lebih      [Benar]{.mark}
                           mana, Cemara Asri atau   lengkap]{.mark}         
                           Ringroad City?                                   

     16     Promosi        Apakah ada promo DP      [Ada promo DP hingga Rp [Benar]{.mark}
                           untuk pembelian rumah di 250 juta]{.mark}        
                           Grand Patriot?                                   

     17     Promosi        Apakah ada diskon untuk  [Tidak tersedia]{.mark} [Benar]{.mark}
                           pembelian tunai?                                 

     18     Promosi        Apakah ada program       [Ada KPR hingga 20      [Benar]{.mark}
                           cicilan KPR untuk rumah  tahun]{.mark}           
                           tipe 120?                                        

     19     Umum           Siapa developer dari     [PT XYZ                 [Benar]{.mark}
                           proyek Beverly Diamond?  Properti]{.mark}        

     20     Umum           Kapan proyek Grand       [Tahun 2022]{.mark}     [Benar]{.mark}
                           Patriot mulai dibangun?                          
  ------------------------------------------------------------------------------------------

Rekapitulasi :

Total Pertanyaan : 20

Jawaban Benar : 19

Jawaban Salah : 1

$$Akurasi = \ \frac{19}{20} \times 100\% = 95\%$$

[]{#_Toc207294955 .anchor}Lampiran 3. Perhitungan Waktu Respon Rata-Rata

  ----------------------------------------------------------------------
   **No.**  **Kategori**   **Pertanyaan**              **Waktu Respon
                                                         (detik)**
  --------- -------------- ------------------------ --------------------
      1     Harga          Berapa harga rumah tipe          1,6
                           70 di Medan Johor?       

      2     Harga          Berapa harga rumah tipe          1,8
                           90 di Grand Patriot?     

      3     Harga          Berapa kisaran harga             1,7
                           rumah di kawasan Cemara  
                           Asri?                    

      4     Lokasi         Apakah ada rumah yang            1,5
                           dijual di Ringroad City? 

      5     Lokasi         Apakah ada properti di           2,1
                           kawasan Setia Budi?      

      6     Lokasi         Di mana lokasi proyek            1,9
                           Beverly Diamond?         

      7     Fasilitas      Apakah rumah di Cemara           1,6
                           Asri memiliki kolam      
                           renang?                  

      8     Fasilitas      Rumah tipe 120 di Grand          1,8
                           Patriot apakah ada       
                           garasi?                  

      9     Fasilitas      Apakah unit di Ringroad          1,7
                           City menyediakan taman   
                           bermain?                 

     10     Status Unit    Apakah rumah tipe 45 di          2,0
                           Grand Patriot masih      
                           tersedia?                

     11     Status Unit    Apakah unit tipe 150 di          1,9
                           Beverly Diamond sudah    
                           terjual?                 

     12     Status Unit    Apakah masih ada kavling         1,6
                           kosong di Cemara Asri?   

     13     Perbandingan   Lebih murah mana, rumah          1,7
                           tipe 90 atau tipe 120 di 
                           Grand Patriot?           

     14     Perbandingan   Mana yang lebih besar,           1,5
                           rumah tipe 70 di Medan   
                           Johor atau tipe 90 di    
                           Ringroad?                

     15     Perbandingan   Lebih banyak fasilitas           1,8
                           mana, Cemara Asri atau   
                           Ringroad City?           

     16     Promosi        Apakah ada promo DP              1,7
                           untuk pembelian rumah di 
                           Grand Patriot?           

     17     Promosi        Apakah ada diskon untuk          2,0
                           pembelian tunai?         

     18     Promosi        Apakah ada program               1,9
                           cicilan KPR untuk rumah  
                           tipe 120?                

     19     Umum           Siapa developer dari             1,6
                           proyek Beverly Diamond?  

     20     Umum           Kapan proyek Grand               1,8
                           Patriot mulai dibangun?  
  ----------------------------------------------------------------------

Rekapitulasi

Total Pertanyaan : 20

Total Waktu Respon : 35,4 detik

Rata-rata : 1,77 detik

$$Waktu\ Respon\ Rata - rata = \ \frac{35,4}{20} = 1,77\ detik$$

# RIWAYAT HIDUP

Penulis dilahirkan di Kota Binjai, pada 28 November 1983, sebagai anak
pertama dari tiga orang bersaudara pasangan Bapak Benny Liandar dan Ibu
Yenny Kustamin. Penulis menempuh pendidikan dasar hingga menengah di
Kota Binjai, kemudian melanjutkan pendidikan sarjana di Program Studi
Teknik Sipil, Universitas Sumatera Utara, dan lulus pada tahun 2004
dengan predikat sangat memuaskan.

Sejak tahun 2017, penulis aktif bekerja di bidang teknologi informasi,
khususnya dalam pengembangan sistem informasi dan solusi perangkat lunak
untuk mendukung kebutuhan bisnis. Pengalaman profesional penulis
meliputi pengembangan aplikasi berbasis web, integrasi sistem, serta
penerapan teknologi *Artificial Intelligence* pada sektor industri dan
pemasaran properti.

Pada tahun 2024, penulis diterima sebagai mahasiswa Program Studi
Magister Teknik Informatika di BINUS Graduate Program, Universitas Bina
Nusantara. Selama mengikuti perkuliahan, penulis terlibat dalam berbagai
kegiatan akademik serta penelitian, khususnya dalam bidang *Machine
Learning*, *Natural Language Processing*, dan *Retrieval-Augmented
Generation*. Penulis juga berkesempatan menghasilkan karya ilmiah dari
penelitian tesis yang difokuskan pada pengembangan *chatbot* berbasis AI
untuk mendukung efisiensi tenaga pemasaran properti.

Penulis dapat dihubungi melalui email ripinlie@gmail.com
