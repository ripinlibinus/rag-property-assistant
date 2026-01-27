# Auto-Evaluation Implementation Plan (V1 - LLM-based)

> **Note:** Dokumen ini menjelaskan metodologi evaluasi V1 yang menggunakan LLM untuk menilai relevansi. Metodologi ini telah digantikan oleh **V2 (Constraint-based Evaluation)** yang lebih objektif dan reproducible. Lihat [docs/18-evaluation-v2-confusion-matrix.md](18-evaluation-v2-confusion-matrix.md) untuk metodologi terbaru.

Dokumen ini menjelaskan implementasi sistem evaluasi otomatis menggunakan LLM untuk menilai relevansi hasil pencarian.

## 1. Overview

### Tujuan
Membuat sistem evaluasi otomatis yang dapat:
1. Menilai relevansi setiap properti hasil pencarian terhadap query user
2. Mendukung multiple LLM evaluators (GPT-4o-mini, Claude 3.5 Sonnet)
3. Menghasilkan output yang kompatibel dengan HTML evaluation interface
4. Menyimpan hasil di folder terpisah untuk perbandingan

### Manfaat
- **Konsistensi**: LLM memberikan penilaian yang lebih konsisten daripada evaluator manusia yang berbeda
- **Skalabilitas**: Dapat mengevaluasi ribuan query tanpa kelelahan
- **Perbandingan**: Memungkinkan perbandingan antar model evaluator
- **Verifikasi**: Hasil tetap dapat diverifikasi manual melalui HTML interface

---

## 2. Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUTO-EVALUATION FLOW                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  INPUT: test_results.json                                        │
│  - query_id, question, response, results_count                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROPERTY PARSER                                                 │
│  - Extract individual properties from response                   │
│  - Parse: title, price, location, specs                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LLM EVALUATOR (GPT-4o-mini / Claude 3.5 Sonnet)                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ For each property:                                         │  │
│  │ - Input: user_query + property_details                     │  │
│  │ - Output: relevant (true/false) + confidence + reasoning   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  METRICS CALCULATOR                                              │
│  - Precision@5, Overall Precision, MRR, Success Rate            │
│  - Per-category breakdown                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                          │
│  ├── evaluation_rated.csv (compatible with HTML viewer)          │
│  ├── evaluation.html (auto-generated)                            │
│  ├── evaluation_report.json (metrics)                            │
│  └── llm_judgments.json (detailed LLM responses)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Folder Structure

```
data/evaluation/
├── hybrid/
│   └── 20260124_140507/              # Test timestamp
│       ├── test_results.json         # Original test results
│       ├── evaluation.html           # HTML interface (manual)
│       │
│       ├── auto_gpt4o_mini/          # GPT-4o-mini evaluation
│       │   ├── evaluation_rated.csv  # Ratings CSV
│       │   ├── evaluation.html       # HTML with pre-filled ratings
│       │   ├── evaluation_report.json
│       │   ├── evaluation_report.md
│       │   └── llm_judgments.json    # Detailed LLM responses
│       │
│       └── auto_claude_sonnet/       # Claude 3.5 Sonnet evaluation
│           ├── evaluation_rated.csv
│           ├── evaluation.html
│           ├── evaluation_report.json
│           ├── evaluation_report.md
│           └── llm_judgments.json
```

---

## 4. LLM Prompt Design

### Relevance Evaluation Prompt

```python
EVALUATION_PROMPT = """You are evaluating search results for a real estate chatbot.

USER QUERY: {query}

PROPERTY DETAILS:
- Title: {title}
- Price: {price}
- Location: {location}
- Specs: {specs}
- Property Type: {property_type}
- Listing Type: {listing_type}

TASK: Determine if this property is RELEVANT to the user's query.

RELEVANCE CRITERIA:
1. Location Match: Does the property location match or is near the requested area?
2. Price Match: Is the price within the requested range (if specified)?
3. Property Type Match: Is it the right type (rumah, ruko, tanah, etc.)?
4. Specification Match: Does it meet bedroom/floor/size requirements?
5. Listing Type Match: Is it sale/rent as requested?
6. Feature Match: Does it have requested features/amenities?

IMPORTANT:
- A property is RELEVANT if it reasonably matches the main criteria
- Minor mismatches (e.g., 10% price difference) are acceptable
- If query is vague, be more lenient in judging relevance

Respond in JSON format:
{
    "relevant": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}
"""
```

### Response Quality Prompt

```python
QUALITY_PROMPT = """Rate the overall quality of this search response.

USER QUERY: {query}
SEARCH RESULTS: {results_summary}
RELEVANT COUNT: {relevant_count} / {total_count}

Rate from 0-5:
5 = All results highly relevant
4 = Most results relevant (>70%)
3 = Half relevant (50-70%)
2 = Few relevant (<50%)
1 = Almost no relevant results
0 = No results or error

Respond in JSON:
{
    "quality": 0-5,
    "reasoning": "Brief explanation"
}
"""
```

---

## 5. Implementation Steps

### Step 1: Create auto_evaluate.py

```python
# scripts/auto_evaluate.py

class LLMEvaluator:
    """Base class for LLM-based evaluation."""

    def __init__(self, model_name: str):
        self.model_name = model_name

    def evaluate_relevance(self, query: str, property_details: dict) -> dict:
        """Evaluate if a property is relevant to the query."""
        raise NotImplementedError

    def evaluate_quality(self, query: str, results: list) -> int:
        """Rate overall response quality (0-5)."""
        raise NotImplementedError


class GPT4oMiniEvaluator(LLMEvaluator):
    """OpenAI GPT-4o-mini evaluator."""

    def __init__(self):
        super().__init__("gpt-4o-mini")
        self.client = OpenAI()


class ClaudeSonnetEvaluator(LLMEvaluator):
    """Anthropic Claude 3.5 Sonnet evaluator."""

    def __init__(self):
        super().__init__("claude-3-5-sonnet-20241022")
        self.client = Anthropic()
```

### Step 2: Property Parser (Reuse from HTML generator)

```python
def parse_properties_from_response(response: str) -> List[dict]:
    """Extract property details from agent response."""
    # Reuse logic from generate_evaluation_html.py
    pass
```

### Step 3: Batch Evaluation

```python
def evaluate_test_results(
    input_file: Path,
    evaluator: LLMEvaluator,
    output_dir: Path
) -> dict:
    """
    Evaluate all test results using the specified LLM evaluator.

    Returns metrics dict with Precision@5, MRR, etc.
    """
    pass
```

### Step 4: Output Generation

```python
def generate_rated_csv(results: list, output_path: Path):
    """Generate CSV in the same format as manual evaluation."""
    pass

def generate_html_with_ratings(results: list, ratings: dict, output_path: Path):
    """Generate HTML with pre-filled ratings from LLM."""
    pass
```

---

## 6. CLI Interface

```bash
# Evaluate with GPT-4o-mini
python scripts/auto_evaluate.py --evaluator gpt4o-mini

# Evaluate with Claude 3.5 Sonnet
python scripts/auto_evaluate.py --evaluator claude-sonnet

# Evaluate specific test results
python scripts/auto_evaluate.py --input data/evaluation/hybrid/20260124_140507/test_results.json

# Compare evaluators
python scripts/auto_evaluate.py --compare

# Specify search method
python scripts/auto_evaluate.py --method hybrid --evaluator gpt4o-mini
```

---

## 7. Comparison Report

### Evaluator Agreement Analysis

```
┌────────────────────────────────────────────────────────────────┐
│                 EVALUATOR COMPARISON REPORT                     │
├────────────────────────────────────────────────────────────────┤
│ Test: hybrid/20260124_140507                                   │
│ Total Queries: 30                                               │
│ Total Properties Evaluated: 285                                 │
└────────────────────────────────────────────────────────────────┘

┌──────────────────┬─────────────┬─────────────────┐
│ Metric           │ GPT-4o-mini │ Claude Sonnet   │
├──────────────────┼─────────────┼─────────────────┤
│ Precision@5      │ 45.2%       │ 48.7%           │
│ Overall Precision│ 42.1%       │ 44.3%           │
│ MRR              │ 0.512       │ 0.534           │
│ Success Rate     │ 63.3%       │ 66.7%           │
│ Mean Quality     │ 3.1/5       │ 3.4/5           │
├──────────────────┼─────────────┼─────────────────┤
│ Agreement Rate   │         87.4% (249/285)       │
│ Cohen's Kappa    │         0.72 (substantial)    │
└──────────────────┴─────────────────────────────────┘

Disagreement Analysis:
- Query #19 (feature_search): GPT marked 2/5 relevant, Claude marked 4/5
- Query #24 (nearby_search): GPT marked 1/5 relevant, Claude marked 3/5
...
```

---

## 8. Error Handling

### Rate Limiting
```python
# Implement exponential backoff
MAX_RETRIES = 3
RETRY_DELAY = [1, 2, 4]  # seconds

def call_llm_with_retry(prompt: str) -> dict:
    for attempt in range(MAX_RETRIES):
        try:
            return call_llm(prompt)
        except RateLimitError:
            time.sleep(RETRY_DELAY[attempt])
    raise Exception("Max retries exceeded")
```

### Malformed Responses
```python
def parse_llm_response(response: str) -> dict:
    """Parse LLM response with fallback."""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block
        match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Default fallback
        return {"relevant": False, "confidence": 0, "reasoning": "Parse error"}
```

---

## 9. Cost Estimation

### GPT-4o-mini
- Input: ~500 tokens per property evaluation
- Output: ~50 tokens per evaluation
- Cost: $0.15/1M input, $0.60/1M output
- Per property: ~$0.0001
- Per test (30 queries × 10 props): ~$0.03

### Claude 3.5 Sonnet
- Input: ~500 tokens per property evaluation
- Output: ~50 tokens per evaluation
- Cost: $3/1M input, $15/1M output
- Per property: ~$0.002
- Per test (30 queries × 10 props): ~$0.60

### Total for Full Comparison
- GPT-4o-mini: ~$0.03
- Claude 3.5 Sonnet: ~$0.60
- **Total: ~$0.63 per test run**

---

## 10. Execution Plan

| # | Task | Status |
|---|------|--------|
| 1 | Create `scripts/auto_evaluate.py` | Done |
| 2 | Implement GPT-4o-mini evaluator | Done |
| 3 | Implement Claude Sonnet 4 evaluator | Done |
| 4 | Run evaluation with GPT-4o-mini | Done |
| 5 | Run evaluation with Claude Sonnet 4 | Done |
| 6 | Generate comparison report | Done |
| 7 | Verify results via HTML interface | Pending |

---

## 10.1 Evaluation Results (20260124_212941)

### Summary Comparison

| Metric | GPT-4o-mini | Claude Sonnet 4 |
|--------|-------------|-----------------|
| **Precision@5** | 69.3% | 39.3% |
| **Overall Precision** | 67.0% | 38.9% |
| **MRR** | 0.833 | 0.501 |
| **Success Rate** | 80.0% | 56.7% |

### Key Findings

1. **GPT-4o-mini** cenderung lebih lenient dalam menilai relevansi
2. **Claude Sonnet 4** lebih strict, terutama pada:
   - Context/follow-up queries: menilai 0% karena properti duplikat
   - Feature search (CCTV, WiFi): tidak bisa verifikasi fasilitas
   - Nearby search: lebih ketat soal proximity

### Category Breakdown (GPT-4o-mini)

| Category | P@5 | MRR | Success |
|----------|-----|-----|---------|
| location_simple | 96.7% | 1.0 | 100% |
| location_price | 16.7% | 0.33 | 33.3% |
| location_price_spec | 73.3% | 1.0 | 100% |
| property_type | 76.7% | 1.0 | 100% |
| context_followup | 100% | 1.0 | 100% |
| feature_search | 56.0% | 0.8 | 60% |
| nearby_search | 16.7% | 0.5 | 50% |

### Output Files Location
```
data/evaluation/hybrid/20260124_212941/
├── auto_gpt4o_mini/
│   ├── llm_judgments.json
│   ├── evaluation_rated.csv
│   ├── evaluation_report.json
│   └── evaluation_report.md
└── auto_claude_sonnet/
    └── (same files)
```

---

## 11. Dependencies

```python
# requirements.txt additions
openai>=1.0.0      # For GPT-4o-mini
anthropic>=0.18.0  # For Claude 3.5 Sonnet
```

---

## 12. References

- Manning et al. (2008). Introduction to Information Retrieval - Precision/Recall
- Voorhees (1999). TREC-8 QA Track - MRR
- Cohen (1960). A coefficient of agreement - Inter-rater reliability

---

## 13. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `scripts/auto_evaluate.py` | Create | Main auto-evaluation script |
| `scripts/compare_evaluators.py` | Create | Compare GPT vs Claude results |
| `requirements.txt` | Modify | Add anthropic package |

---

*Last updated: 2026-01-25*
*Status: Superseded by V2 (constraint-based evaluation)*

