# ChromaDB Ingestion Guide

## Overview

This guide explains how to manage the knowledge base and ChromaDB vector stores.

---

## Knowledge Base Structure

```
data/
├── chromadb/
│   ├── knowledge/     # Knowledge base embeddings
│   └── properties/    # Property embeddings (synced from API)
└── knowledge-base/
    ├── sales-techniques/
    │   ├── closing-strategies.md
    │   ├── handle-objection.md
    │   └── marketing-digital.md
    ├── real-estate-knowledge/
    │   ├── sertifikat-types.md
    │   ├── proses-jual-beli.md
    │   ├── kpr-guide.md
    │   └── pajak-properti.md
    └── motivational/
        └── mindset-tips.md
```

---

## Category Mapping

| Folder Name | Category | Tool That Uses It |
|-------------|----------|-------------------|
| `sales-techniques/` | `sales` | `get_sales_tips`, `search_knowledge` |
| `real-estate-knowledge/` | `knowledge` | `search_knowledge` |
| `motivational/` | `motivation` | `get_motivation`, `search_knowledge` |

---

## How to Add New Knowledge

### Step 1: Create Markdown File

Create a new `.md` file in the appropriate folder:

```markdown
# Title of Your Topic

## Section 1
Content here...

## Section 2
More content...
```

**Best Practices:**
- Use clear headers (##, ###)
- Use bullet points for lists
- Include practical examples
- Keep each section focused (will be chunked)

### Step 2: Run Ingestion

```bash
cd D:\Project\Rag-Tesis
.\venv\Scripts\Activate.ps1
python scripts/ingest_knowledge.py
```

This will:
1. Clear existing data
2. Re-read all markdown files
3. Split into chunks (~500 tokens each)
4. Embed and store in ChromaDB

### Step 3: Verify

```bash
# Check stats
python scripts/ingest_knowledge.py --stats

# Test search
python scripts/ingest_knowledge.py --test "your query"
```

---

## Knowledge Topics to Add

### Sales Techniques (sales-techniques/)

| Topic | Filename | Priority |
|-------|----------|----------|
| Cold calling scripts | `cold-calling.md` | Medium |
| First meeting tips | `first-meeting.md` | High |
| Presentation techniques | `presentation.md` | Medium |
| Negotiation tactics | `negotiation.md` | High |
| Referral strategies | `referral.md` | Medium |

### Real Estate Knowledge (real-estate-knowledge/)

| Topic | Filename | Priority |
|-------|----------|----------|
| ~~Sertifikat types~~ | `sertifikat-types.md` | ✅ Done |
| ~~KPR guide~~ | `kpr-guide.md` | ✅ Done |
| ~~Pajak properti~~ | `pajak-properti.md` | ✅ Done |
| ~~Proses jual beli~~ | `proses-jual-beli.md` | ✅ Done |
| Area guide Medan | `area-guide-medan.md` | High |
| Developer profiles | `developer-profiles.md` | Medium |
| Property inspection checklist | `inspection-checklist.md` | Medium |
| Legal documents checklist | `legal-documents.md` | High |

### Motivational (motivational/)

| Topic | Filename | Priority |
|-------|----------|----------|
| ~~Mindset tips~~ | `mindset-tips.md` | ✅ Done |
| Success stories | `success-stories.md` | Low |
| Weekly inspiration | `weekly-inspiration.md` | Low |

---

## Content Guidelines

### Good Content Structure

```markdown
# Main Topic Title

## Overview
Brief introduction to the topic.

## Key Concepts

### Concept 1
Explanation with:
- Bullet points
- Clear examples
- Practical tips

### Concept 2
...

## FAQ
Common questions and answers.

## Tips for Agents
Practical application for real estate agents.
```

### Chunk-Friendly Writing

- Each section should be self-contained
- Aim for 300-600 words per major section
- Use headers to separate topics
- Include context in each section

### Language

- Primary: Indonesian (Bahasa Indonesia)
- Mixed Indonesian-English terms OK (common in industry)
- Use formal but accessible tone
- Include industry jargon with explanations

---

## Property Vector Store

### How It Works

Properties from MetaProperty API are synced to ChromaDB for semantic search.

**What Gets Embedded (Document Text):**
- Title + listing type context (dijual/disewa)
- Source type (Proyek baru vs Secondary market)
- Unit types, bedroom/floor ranges for projects
- Building/land area ranges
- Description (HTML stripped)
- Location info (area, complex, district, city, address)
- Property type in Indonesian (Rumah, Ruko, Tanah, dll)
- Certificate type (SHM, SHGB, HGB, dll)
- Amenities/facilities in Indonesian (kolam renang, jogging track, cctv, dll)

**Metadata Stored (for filtering):**

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | str | Unique property ID |
| `slug` | str | URL slug for property link |
| `url_view` | str | Full property URL |
| `title` | str | Property title |
| `property_type` | str | house, shophouse, land, apartment |
| `listing_type` | str | sale or rent |
| `source` | str | project or listing |
| `city` | str | City name |
| `district` | str | District name |
| `area_listing` | str | Area listing (comma-separated) |
| `price` | float | Property price |
| `bedrooms` / `bedrooms_max` | int | Bedroom range |
| `bathrooms` / `bathrooms_max` | int | Bathroom range |
| `floors` / `floors_max` | float | Floor range |
| `land_area` / `land_area_max` | float | Land area range |
| `building_area` / `building_area_max` | float | Building area range |
| `certificate_type` | str | SHM, SHGB, HGB, etc. |
| `status` | str | active, sold, upcoming |
| `complex_name` | str | Complex/cluster name (if any) |
| `in_complex` | int | 1 if in complex, 0 if standalone |
| `facing` | str | Facing direction (utara, selatan, etc.) |
| `synced_at` | str | ISO timestamp of last sync |

**Sync Script:**
```bash
python scripts/sync_properties.py           # Sync pending
python scripts/sync_properties.py --stats   # Check stats
python scripts/sync_properties.py --full    # Force full resync
python scripts/sync_properties.py --test "taman luas"  # Test search
```

**Note:** Requires MetaProperty API to have sync endpoints. See:
- [MetaProperty ChromaDB Sync API](../../metaproperty2026/docs/outstanding-session/chromadb-sync-api.md)

### URL Enrichment

Jika ChromaDB tidak memiliki `slug` atau `url_view` (belum re-sync), sistem akan **enrich URL dari API** saat search:

```
ChromaDB search → property IDs
      ↓
API call: GET /api/v1/properties?ids=1,2,3
      ↓
Enrich properties with url_view
      ↓
Return dengan URL lengkap
```

Untuk menghindari ini, re-sync properties setelah update kode:
```bash
python scripts/sync_properties.py --full --limit 3000
```

---

## Troubleshooting

### "No documents found"
- Check if files are in correct folder
- Files must have `.md` extension
- Check file encoding (UTF-8)

### "Search returns no results"
- Run ingestion first
- Check if query matches content
- Try broader search terms

### "ChromaDB error"
- Delete `data/chromadb/` folder and re-ingest
- Check disk space
- Ensure OPENAI_API_KEY is set

---

## Scheduled Updates

### Weekly Tasks
- [ ] Add new knowledge based on agent feedback
- [ ] Review search performance

### Monthly Tasks
- [ ] Full knowledge base review
- [ ] Update outdated information (tax rates, bank rates)
- [ ] Add new FAQ based on common questions

---

*Last updated: 2026-01-25*
*Added: Complete metadata field list, URL enrichment documentation*
