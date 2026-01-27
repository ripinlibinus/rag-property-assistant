# Prompts untuk Generate Knowledge Base

Copy-paste prompts ini di sesi AI lain untuk generate konten knowledge base.

---

## 1. First Meeting Tips (High Priority)

```
Buatkan konten markdown untuk knowledge base chatbot real estate dengan topik "Tips First Meeting dengan Client".

Format yang diharapkan:
- Judul utama dengan #
- Sub-sections dengan ## dan ###
- Bullet points untuk tips
- Contoh dialog/script jika relevan
- Tips praktis untuk agen properti Indonesia

Topik yang harus dicover:
1. Persiapan sebelum meeting
2. Cara memulai percakapan
3. Pertanyaan untuk gali kebutuhan client
4. Cara presentasi properti
5. Do's and Don'ts
6. Cara closing first meeting (next step)
7. Follow up setelah meeting

Target audience: Agen properti Indonesia
Bahasa: Indonesia (boleh campur istilah English yang umum)
Panjang: 800-1500 kata
```

---

## 2. Area Guide Medan (High Priority)

```
Buatkan konten markdown untuk knowledge base chatbot real estate dengan topik "Panduan Area Properti di Medan".

Format yang diharapkan:
- Judul utama dengan #
- Setiap area sebagai ## section
- Info: karakteristik, range harga, target market, plus minus
- Tips untuk agen

Area yang harus dicover:
1. Medan Selayang / Setia Budi (premium)
2. Medan Johor / Ring Road
3. Cemara Asri / Helvetia
4. Sunggal / Tanjung Sari
5. Medan Marelan / Belawan
6. Medan Timur / Krakatau
7. Medan Tembung / Menteng
8. Deli Serdang (Lubuk Pakam, Tanjung Morawa)

Untuk setiap area, jelaskan:
- Karakteristik area
- Range harga rata-rata (rumah, tanah)
- Target market (keluarga muda, investor, dll)
- Akses dan infrastruktur
- Potensi dan perkembangan

Target audience: Agen properti Medan
Bahasa: Indonesia
Panjang: 1500-2500 kata
```

---

## 3. Legal Documents Checklist (High Priority)

```
Buatkan konten markdown untuk knowledge base chatbot real estate dengan topik "Checklist Dokumen Legal Jual Beli Properti".

Format yang diharapkan:
- Judul utama dengan #
- Kategori dokumen dengan ##
- Checklist dengan bullet points
- Penjelasan fungsi tiap dokumen
- Red flags yang perlu diwaspadai

Topik yang harus dicover:
1. Dokumen Penjual
   - KTP, KK, Surat Nikah
   - Sertifikat (SHM/SHGB/HGB)
   - PBB 5 tahun terakhir
   - IMB (jika ada bangunan)
   
2. Dokumen Pembeli
   - KTP, KK
   - NPWP
   - Dokumen KPR (jika pakai KPR)

3. Dokumen Transaksi
   - Surat Tanda Terima DP
   - PPJB (Perjanjian Pengikatan Jual Beli)
   - AJB (Akta Jual Beli)
   - Kwitansi pelunasan

4. Red Flags / Warning Signs
   - Sertifikat ganda
   - Sengketa waris
   - Tanah dalam jaminan bank
   - PBB nunggak

5. Tips untuk Agen
   - Kapan perlu cek ke BPN
   - Cara verifikasi dokumen

Target audience: Agen properti Indonesia
Bahasa: Indonesia
Panjang: 1000-1500 kata
```

---

## 4. Negotiation Tactics (Medium Priority)

```
Buatkan konten markdown untuk knowledge base chatbot real estate dengan topik "Teknik Negosiasi Properti".

Format yang diharapkan:
- Judul utama dengan #
- Teknik-teknik dengan ## sections
- Contoh situasi dan dialog
- Tips praktis

Topik yang harus dicover:
1. Mindset Negosiasi
   - Win-win thinking
   - Posisi agen sebagai mediator

2. Teknik Negosiasi Harga
   - Anchor pricing
   - Bracketing
   - Nibbling
   - Good cop / bad cop (dengan pasangan)

3. Negosiasi Non-Harga
   - Waktu serah terima
   - Furniture/inventaris
   - Renovasi kecil
   - Jadwal pembayaran

4. Cara Handle Deadlock
   - Teknik break
   - Creative solutions
   - Kapan walk away

5. Negosiasi dengan Tipe Client Berbeda
   - Client analitis (butuh data)
   - Client emosional (butuh rapport)
   - Client assertive (butuh respect)

Target audience: Agen properti Indonesia
Bahasa: Indonesia (boleh campur istilah English)
Panjang: 1000-1500 kata
```

---

## 5. Property Inspection Checklist (Medium Priority)

```
Buatkan konten markdown untuk knowledge base chatbot real estate dengan topik "Checklist Inspeksi Properti Sebelum Beli".

Format yang diharapkan:
- Judul utama dengan #
- Kategori inspeksi dengan ##
- Checklist items dengan checkboxes
- Red flags untuk setiap kategori
- Tips untuk agen saat menemani buyer

Kategori yang harus dicover:
1. Struktur Bangunan
   - Fondasi
   - Dinding (retak, lembab)
   - Atap dan plafon
   - Lantai

2. Sistem Air
   - Sumber air (PDAM/sumur)
   - Tekanan air
   - Saluran pembuangan
   - Septik tank

3. Sistem Listrik
   - Kapasitas (watt)
   - Kondisi kabel
   - Grounding
   - MCB/panel

4. Eksterior
   - Pagar dan gerbang
   - Carport/garasi
   - Taman dan drainase
   - Akses jalan

5. Lingkungan
   - Keamanan
   - Akses banjir
   - Tetangga
   - Kebisingan

6. Legalitas
   - Cek IMB vs bangunan actual
   - Batas tanah
   - GSB (Garis Sempadan Bangunan)

Target audience: Agen properti dan calon pembeli
Bahasa: Indonesia
Panjang: 1000-1500 kata
```

---

## Cara Pakai

1. Copy salah satu prompt di atas
2. Paste ke sesi AI baru
3. AI akan generate konten markdown
4. Save sebagai file `.md` di folder yang sesuai:
   - `data/knowledge-base/sales-techniques/`
   - `data/knowledge-base/real-estate-knowledge/`
5. Jalankan ingestion:
   ```bash
   python scripts/ingest_knowledge.py
   ```

---

## Setelah Generate, Simpan Sebagai:

| Topic | Save As |
|-------|---------|
| First Meeting Tips | `data/knowledge-base/sales-techniques/first-meeting.md` |
| Area Guide Medan | `data/knowledge-base/real-estate-knowledge/area-guide-medan.md` |
| Legal Documents | `data/knowledge-base/real-estate-knowledge/legal-documents.md` |
| Negotiation Tactics | `data/knowledge-base/sales-techniques/negotiation.md` |
| Property Inspection | `data/knowledge-base/real-estate-knowledge/inspection-checklist.md` |
