# Thesis Improvement Plan

## Overview

Dokumen ini berisi rencana perbaikan thesis berdasarkan feedback dosen pembimbing.
Semua improvement dikerjakan **setelah evaluasi 3 metode selesai**.

**Status:** Menunggu hasil evaluasi
**Target:** Melengkapi statistical analysis dan revisi paper

---

## 1. Statistical Testing

### 1.1 Masalah di Versi Sebelumnya

Paper mengklaim "outperforming by 11.6-13.0%" tanpa bukti statistik:
- ❌ Tidak ada p-value
- ❌ Tidak ada confidence interval
- ❌ Tidak ada significance test

### 1.2 Yang Perlu Ditambahkan

| Test | Kegunaan | Library Python |
|------|----------|----------------|
| **Wilcoxon signed-rank test** | Paired comparison non-parametric | `scipy.stats.wilcoxon` |
| **McNemar's test** | Membandingkan confusion matrix | `statsmodels.stats.contingency_tables.mcnemar` |
| **Bootstrap 95% CI** | Confidence interval | `scipy.stats.bootstrap` |

### 1.3 Output yang Diharapkan

**Contoh kalimat untuk paper:**
```
"Hybrid achieved 86.7% accuracy vs 76.7% for API (Wilcoxon p=0.012,
95% CI [0.02, 0.18]), showing statistically significant improvement
at α=0.05 level."
```

### 1.4 Script yang Perlu Dibuat

```
scripts/statistical_comparison.py
├── Input: results dari 3 metode
├── Output: statistical_comparison.json, .csv, .html
└── Functions: wilcoxon_test(), mcnemar_test(), bootstrap_ci()
```

---

## 2. Threshold Sensitivity Analysis

### 2.1 Masalah

Threshold CPR T=0.60 tidak dijustifikasi.

### 2.2 Solusi

Sweep T ∈ {0.40, 0.50, 0.60, 0.70, 0.80} dan tunjukkan:
- Metrics tetap stabil di range tertentu
- Justifikasi pemilihan T=0.60

### 2.3 Script

```
scripts/threshold_sensitivity.py
├── Input: results.json dari setiap metode
├── Output: threshold_sensitivity.json, plot.png
└── Functions: recalculate_metrics(), sweep_thresholds(), plot_sensitivity()
```

---

## 3. Improved Visualizations

### 3.1 Figures yang Perlu Diperbaiki

| Figure | Improvement |
|--------|-------------|
| Confusion Matrix | Heatmap side-by-side (3 methods) |
| Metrics Comparison | Bar chart atau table |
| Threshold Sensitivity | Line plot |
| Error Analysis | NEW - failure patterns |

### 3.2 Script

```
scripts/generate_figures.py
├── plot_confusion_matrix_heatmap()
├── plot_threshold_sensitivity()
├── plot_metrics_comparison()
└── plot_error_analysis()
```

---

## 4. Writing Improvements

### 4.1 Introduction

**Sebelum:** Langsung masuk ke solusi
**Sesudah:** Mulai dengan problem statement yang jelas

### 4.2 Related Works

**Sebelum:** ~2 halaman verbose
**Sesudah:** ~1 halaman + comparison table

### 4.3 Results

**Sebelum:** Klaim tanpa statistik
**Sesudah:** Setiap klaim ada p-value dan CI

Lihat `docs/21-thesis-rewriting-prompts.md` untuk detail prompts.

---

## 5. Implementation Checklist

### Phase 1: Complete Evaluations ⏳

- [ ] Run `evaluate_v2.py --method api_only`
- [ ] Run `evaluate_v2.py --method vector_only`
- [ ] Verify hybrid results exist
- [ ] Collect all results

### Phase 2: Statistical Analysis 📊

- [ ] Create `scripts/statistical_comparison.py`
- [ ] Implement Wilcoxon test
- [ ] Implement McNemar's test
- [ ] Implement Bootstrap CI
- [ ] Generate comparison tables

### Phase 3: Threshold Sensitivity 📈

- [ ] Create `scripts/threshold_sensitivity.py`
- [ ] Sweep thresholds
- [ ] Generate table and plot
- [ ] Write justification

### Phase 4: Visualizations 🎨

- [ ] Create `scripts/generate_figures.py`
- [ ] Confusion matrix heatmaps
- [ ] Threshold sensitivity plot
- [ ] Error analysis figure

### Phase 5: Paper Revision ✍️

- [ ] Rewrite Introduction
- [ ] Condense Related Works
- [ ] Update Methodology
- [ ] Update Results with statistics
- [ ] Update Discussion
- [ ] Final proofread

---

## 6. File Structure After Completion

```
data/evaluation/v2/
├── hybrid_openai_{ts}/
├── api_only_openai_{ts}/
├── vector_only_openai_{ts}/
├── comparison/
│   ├── statistical_comparison.json
│   └── threshold_sensitivity.json
└── figures/
    ├── confusion_matrix_comparison.png
    ├── threshold_sensitivity.png
    └── metrics_comparison.png

scripts/
├── evaluate_v2.py (existing)
├── statistical_comparison.py (NEW)
├── threshold_sensitivity.py (NEW)
└── generate_figures.py (NEW)

docs/
├── 20-thesis-improvement-plan.md (this file)
└── 21-thesis-rewriting-prompts.md (prompts for rewriting)
```

---

*Document created: 26 January 2026*
