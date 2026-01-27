# Thesis Rewriting Prompts

## Document Information
- **Purpose:** Prompts for rewriting thesis paper with updated methodology and results
- **Target:** Applied Science and Engineering Progress Journal
- **Language:** Formal Academic English
- **Status:** Metrics with `[PENDING]` or `[X.XX]` to be filled after evaluation complete

---

## Master Prompt (Use This First)

```
You are an academic writing assistant helping to revise a research paper for the
"Applied Science and Engineering Progress" journal. The paper is about a RAG-based
AI chatbot for real estate property search.

WRITING GUIDELINES:
1. Use formal academic English throughout
2. Write in third person (avoid "we" excessively, prefer "this study", "the system")
3. Use active voice where appropriate for clarity
4. Keep sentences concise but complete
5. Each paragraph should have a clear topic sentence
6. Use transition words between paragraphs
7. Define acronyms on first use
8. Be precise with technical terms

STRUCTURE REQUIREMENTS:
- Maintain the original paper structure
- Keep all existing references [1]-[20]
- New references should be added at the end [21], [22], etc.
- Use the same metrics: PCA, Strict Success, CPR, Confusion Matrix (P/R/F1/Accuracy)

METRICS PLACEHOLDERS:
- Numbers marked as [PENDING] or [X.XX] will be filled with actual data later
- Keep the placeholder format exactly as shown

TONE:
- Objective and evidence-based
- Avoid overclaiming (use "suggests", "indicates" rather than "proves")
- Acknowledge limitations honestly
- Be specific with numbers and percentages
```

---

## Section 1: Abstract Prompt

```
Rewrite the abstract for a research paper about a RAG-based property search chatbot.

CURRENT ABSTRACT ISSUES:
- Needs clearer problem statement upfront
- Should mention statistical significance
- Results should be more specific

KEY POINTS TO INCLUDE:
1. Problem: Rigid form-based filters fail for fuzzy user intents
2. Solution: RAG assistant with three retrieval pipelines (Vector, API, Hybrid)
3. Evaluation: 30 gold-labeled questions with constraint-based metrics
4. Main Results (use these placeholders):
   - Hybrid PCA: [HYBRID_PCA]%
   - Hybrid Accuracy: [HYBRID_ACC]%
   - Improvement over baselines: statistically significant (p < 0.05)
5. Conclusion: Hybrid approach balances semantic flexibility with transactional correctness

METRICS TO INCLUDE:
- Per-Constraint Accuracy (PCA)
- Question-level Accuracy
- F1 Score
- Statistical significance mention

FORMAT:
- Maximum 250 words
- Single paragraph
- No citations in abstract

EXAMPLE STRUCTURE:
"[Problem statement - 2 sentences]. [Solution approach - 2 sentences].
[Methodology - 1 sentence]. [Key results with numbers - 2-3 sentences].
[Conclusion - 1 sentence]."

PLACEHOLDER DATA:
| Metric | Vector | API | Hybrid |
|--------|--------|-----|--------|
| PCA | [VEC_PCA]% | [API_PCA]% | [HYBRID_PCA]% |
| Accuracy | [VEC_ACC]% | [API_ACC]% | [HYBRID_ACC]% |
| F1 | [VEC_F1]% | [API_F1]% | [HYBRID_F1]% |
```

---

## Section 2: Introduction Prompt

```
Rewrite the Introduction section with better motivation and clearer problem statement.

CURRENT ISSUES:
- Jumps too quickly into solution without establishing problem
- Lacks concrete examples of user pain points
- Contribution list is buried

STRUCTURE (4-5 paragraphs):

PARAGRAPH 1 - Problem Context:
- Start with the limitation of current real estate search systems
- Give concrete examples of fuzzy intents: "near landmark X", "under IDR 1B", "spacious 3-bedroom"
- Mention the gap between natural language and rigid filters

PARAGRAPH 2 - Why Existing Solutions Fail:
- Form-based filters require exact input
- Users must translate preferences into filter combinations
- Results in query reformulation loops and missed opportunities

PARAGRAPH 3 - Proposed Solution:
- Introduce RAG (Retrieval-Augmented Generation) as solution
- Explain channel-agnostic design (API endpoint)
- Mention three retrieval pipelines briefly

PARAGRAPH 4 - Evaluation Approach:
- Constraint-based evaluation on 30 gold-labeled questions
- Metrics: PCA, CPR, Confusion Matrix
- Statistical significance testing

PARAGRAPH 5 - Contributions:
List 3-4 clear contributions:
1. Channel-agnostic RAG assistant design
2. Tri-path retrieval comparison (Vector, API, Hybrid)
3. Constraint-grounded evaluation protocol
4. Empirical evidence with statistical significance

OPENING SENTENCE EXAMPLE:
"Current real estate search systems rely predominantly on rigid, form-based
filters that require users to specify exact values for location, price range,
and property attributes—a paradigm that fails when buyers express fuzzy or
evolving intents."

DO NOT:
- Use "In this paper" as the first sentence
- Make claims without later backing them up
- Use vague language like "novel" or "state-of-the-art" without evidence
```

---

## Section 3: Related Works Prompt

```
Condense the Related Works section to approximately 1 page (from current ~2 pages).

CURRENT ISSUES:
- Too verbose, can be condensed
- Missing comparison table
- Gap statement could be stronger

TARGET STRUCTURE (4-5 paragraphs max):

PARAGRAPH 1 - Chatbots in Real Estate (~3-4 sentences):
- AI chatbots improve service quality [5]
- Conversational recommender systems capture intent better than forms [6][7]
- Keep references [5], [6], [7]

PARAGRAPH 2 - RAG and Conversational IR (~4-5 sentences):
- Conversational search foundations [8], [9]
- RAG combines parametric and non-parametric memory [1]
- Dense retrievers like DPR [3], FiD [2]
- Keep references [1], [2], [3], [8], [9], [10], [11]

PARAGRAPH 3 - Vector Search Technology (~3-4 sentences):
- FAISS for efficient similarity search [13], [14]
- ColBERT for late interaction [4]
- Practical tools: Chroma, LangChain [15], [16]
- Keep references [4], [13], [14], [15], [16]

PARAGRAPH 4 - Gap and Positioning (~4-5 sentences):
- Prior work binds to single channel and retrieval mode
- Limited head-to-head comparison across pipelines
- No constraint-grounded evaluation metrics
- Our contribution fills this gap

ADD THIS COMPARISON TABLE:

Table 1: Comparison with Prior Approaches
| Aspect | Prior Real Estate Chatbots | Our Approach |
|--------|---------------------------|--------------|
| Channel | Single (web or mobile) | Channel-agnostic API |
| Retrieval | Single mode (semantic OR SQL) | Tri-path (Vector, API, Hybrid) |
| Data Freshness | Static index | Live API as source of truth |
| Evaluation | Subjective or MRR-based | Constraint-grounded + CM |
| Statistical Testing | Rarely reported | Wilcoxon, McNemar, Bootstrap CI |

KEEP ALL EXISTING REFERENCES [1]-[20]
```

---

## Section 4: Methodology Prompt

```
Rewrite the Methodology section with updated evaluation approach (V2).

SECTIONS TO INCLUDE:

4.1 SYSTEM OVERVIEW AND ARCHITECTURE
- Keep existing content about channel-agnostic design
- Response API endpoint concept
- LangChain controller with two data substrates
- Update Figure 1 description if needed

4.2 DATA AND PREPARATION
- MySQL as source of truth
- Vector index with OpenAI text-embedding-3-small
- 30 gold-labeled questions with constraint annotations
- Keep Table 1 (example gold dataset)

4.3 INFERENCE PIPELINES
- Vector Retrieval: similarity_score_threshold, k=1500, threshold=0.35
- MySQL/API Retrieval: Text→JSON filter
- Hybrid Retrieval: API→Vector with re-ranking
- Keep Figures 3a, 3b, 3c

4.4 EXPERIMENTAL SETUP
- Same 30 questions across all pipelines
- max_items = 5 per query
- Fixed retrieval parameters

4.5 IMPLEMENTATION DETAILS
- Hardware: VPS specs
- Software: Python 3.12.9, LangChain v1.0.5, etc.
- Hyperparameters: temperature=0, etc.

4.6 METRICS AND EVALUATION (UPDATE THIS SECTION)

Replace old metrics section with:

"This study employs constraint-based evaluation where each query has
explicit gold constraints (property_type, listing_type, location, price,
bedrooms, floors). For each returned property, we check constraint satisfaction."

METRICS DEFINITIONS:

1. Per-Constraint Accuracy (PCA):
   PCA_i = (1/|C|) × Σ 1_{i,c} for each constraint c ∈ C

2. Strict Success:
   Strict_i = 1 if PCA_i = 1 (all constraints satisfied), else 0

3. Constraint Pass Ratio (CPR):
   CPR = (1/K) × Σ Strict_i for K returned listings

4. Query Success:
   A query is successful if:
   - expected=has_data: has_results AND mean_CPR ≥ T (default T=0.60)
   - expected=no_data: no results returned

5. Confusion Matrix (Question-level):
   - TP: Expected has_data, system returns results with CPR ≥ T
   - FN: Expected has_data, system fails threshold or returns nothing
   - TN: Expected no_data, system correctly returns nothing
   - FP: Expected no_data, system incorrectly returns results

   Precision = TP / (TP + FP)
   Recall = TP / (TP + FN)
   F1 = 2 × Precision × Recall / (Precision + Recall)
   Accuracy = (TP + TN) / (TP + TN + FP + FN)

ADD NEW SUBSECTION:

4.7 STATISTICAL ANALYSIS

"To assess statistical significance, we employ:
- Wilcoxon signed-rank test for paired comparison of accuracy across methods
- McNemar's test for comparing confusion matrices
- Bootstrap resampling (n=1000) for 95% confidence intervals

All tests use α = 0.05 significance level."

4.8 THRESHOLD SENSITIVITY

"The CPR threshold T=0.60 was selected based on domain requirements:
with typical K=5 results, this means at least 3 of 5 listings must
satisfy all constraints. We validate this choice through sensitivity
analysis across T ∈ {0.50, 0.60, 0.70, 0.80}."
```

---

## Section 5: Results Prompt

```
Rewrite the Results section with statistical significance claims.

STRUCTURE:

5.1 MAIN RESULTS

Create Table 3 with placeholders:

Table 3: Summary of Evaluation Results
| Metric | Vector | API | Hybrid | Δ Hybrid vs Best Baseline |
|--------|--------|-----|--------|---------------------------|
| PCA | [VEC_PCA] | [API_PCA] | [HYBRID_PCA] | [DELTA_PCA]% |
| Strict Success | [VEC_SS] | [API_SS] | [HYBRID_SS] | [DELTA_SS]% |
| CPR | [VEC_CPR] | [API_CPR] | [HYBRID_CPR] | [DELTA_CPR]% |
| Precision | [VEC_PREC] | [API_PREC] | [HYBRID_PREC] | [DELTA_PREC]% |
| Recall | [VEC_REC] | [API_REC] | [HYBRID_REC] | [DELTA_REC]% |
| F1 | [VEC_F1] | [API_F1] | [HYBRID_F1] | [DELTA_F1]% |
| Accuracy | [VEC_ACC] | [API_ACC] | [HYBRID_ACC] | [DELTA_ACC]% |

NARRATIVE FOR RESULTS:

"Table 3 summarizes the evaluation results across three pipelines.
Hybrid retrieval achieved the highest PCA ([HYBRID_PCA]%) and Accuracy
([HYBRID_ACC]%), representing improvements of [DELTA_PCA]% and [DELTA_ACC]%
over the best baseline respectively."

5.2 STATISTICAL SIGNIFICANCE

Add statistical claims:

Table 4: Statistical Comparison (Hybrid vs Baselines)
| Comparison | Metric | Difference | 95% CI | p-value | Significant? |
|------------|--------|------------|--------|---------|--------------|
| Hybrid vs API | Accuracy | [DIFF]% | [[CI_LOW], [CI_HIGH]] | [P_VAL] | [YES/NO] |
| Hybrid vs Vector | Accuracy | [DIFF]% | [[CI_LOW], [CI_HIGH]] | [P_VAL] | [YES/NO] |
| Hybrid vs API | F1 | [DIFF]% | [[CI_LOW], [CI_HIGH]] | [P_VAL] | [YES/NO] |
| Hybrid vs Vector | F1 | [DIFF]% | [[CI_LOW], [CI_HIGH]] | [P_VAL] | [YES/NO] |

EXAMPLE SENTENCE WITH STATISTICS:
"Hybrid achieved [HYBRID_ACC]% accuracy compared to [API_ACC]% for API
(Wilcoxon p=[P_VAL], 95% CI [[CI_LOW], [CI_HIGH]]), demonstrating
statistically significant improvement at α=0.05."

5.3 CONFUSION MATRIX ANALYSIS

Include confusion matrix for each method:

"Figure 4 presents the confusion matrices for each pipeline. Hybrid
shows [HYBRID_TP] true positives and [HYBRID_TN] true negatives,
with only [HYBRID_FN] false negatives—indicating strong recall for
queries where results should exist."

Vector CM: TP=[VEC_TP], FP=[VEC_FP], TN=[VEC_TN], FN=[VEC_FN]
API CM: TP=[API_TP], FP=[API_FP], TN=[API_TN], FN=[API_FN]
Hybrid CM: TP=[HYB_TP], FP=[HYB_FP], TN=[HYB_TN], FN=[HYB_FN]

5.4 THRESHOLD SENSITIVITY ANALYSIS

Table 5: Metrics Across Different Threshold Values (Hybrid)
| Threshold T | Precision | Recall | F1 | Accuracy |
|-------------|-----------|--------|-----|----------|
| 0.50 | [T50_PREC] | [T50_REC] | [T50_F1] | [T50_ACC] |
| 0.60 | [T60_PREC] | [T60_REC] | [T60_F1] | [T60_ACC] |
| 0.70 | [T70_PREC] | [T70_REC] | [T70_F1] | [T70_ACC] |
| 0.80 | [T80_PREC] | [T80_REC] | [T80_F1] | [T80_ACC] |

"Table 5 shows metrics remain stable across T ∈ [0.50, 0.70], with
decline at T=0.80 due to stricter success criteria. This validates
our choice of T=0.60 as a balanced threshold."

5.5 PER-CONSTRAINT ACCURACY BREAKDOWN (OPTIONAL)

Table 6: PCA by Constraint Type (Hybrid)
| Constraint | Accuracy | Notes |
|------------|----------|-------|
| property_type | [PCA_PROPTYPE]% | |
| listing_type | [PCA_LISTTYPE]% | |
| location | [PCA_LOC]% | Most challenging |
| price | [PCA_PRICE]% | |
| bedrooms | [PCA_BEDS]% | |
```

---

## Section 6: Discussion Prompt

```
Rewrite the Discussion section analyzing why Hybrid performs best.

STRUCTURE (4-5 paragraphs):

PARAGRAPH 1 - Vector Strengths and Weaknesses:
"Vector retrieval excels at handling fuzzy intent—synonyms, spelling
variants, and informal location names—enabling semantic matching when
users provide vague descriptions. However, its reliance on pre-computed
embeddings leads to staleness issues, and it cannot guarantee numeric
accuracy for price or availability fields. This is reflected in its
lower PCA ([VEC_PCA]%) and Accuracy ([VEC_ACC]%)."

PARAGRAPH 2 - API Strengths and Weaknesses:
"API retrieval (Text→JSON) provides transactional correctness by
querying live database records, achieving high Strict Success ([API_SS])
when constraints are explicit. However, it struggles with underspecified
or informally phrased queries, resulting in lower Recall ([API_REC]%)
as relevant items are missed due to failed filter translation."

PARAGRAPH 3 - Why Hybrid Works Best:
"Hybrid retrieval combines both advantages: numeric fields (price,
bedrooms, availability) are validated against the live API as source
of truth, while the vector layer expands recall and re-ranks candidates
for fuzzy location or keyword matches. This design achieves the highest
PCA ([HYBRID_PCA]%) and balanced Precision-Recall (F1=[HYBRID_F1]%),
with statistical significance confirmed by Wilcoxon test (p=[P_VAL])."

PARAGRAPH 4 - Error Analysis:
"Analysis of failed queries reveals three primary patterns:
1. Location ambiguity: [X]% of failures involved non-standard location names
2. Price interpretation: [Y]% involved colloquial price expressions ('harga 1M-an')
3. Compound constraints: [Z]% involved multiple constraints with implicit logic

These patterns suggest opportunities for improved query understanding
and user clarification mechanisms."

PARAGRAPH 5 - Practical Implications:
"For practitioners deploying property search assistants, our findings
suggest that hybrid approaches offer the best balance of flexibility
and correctness. The API should remain the source of truth for
transactional fields, while semantic search can safely enhance
recall for descriptive attributes."
```

---

## Section 7: Conclusion & Future Work Prompt

```
Rewrite Conclusion and Future Work sections.

7.1 CONCLUSION (1 paragraph, ~150 words)

"This study presented a channel-agnostic RAG assistant for property
search, comparing three retrieval pipelines—Vector, API, and Hybrid—on
30 gold-labeled questions using constraint-based evaluation. The Hybrid
approach achieved [HYBRID_PCA]% constraint accuracy and [HYBRID_ACC]%
question-level accuracy, significantly outperforming the API baseline
(p=[P_VAL]) and Vector baseline (p=[P_VAL2]). Statistical analysis
confirmed these improvements with 95% confidence intervals of
[[CI_LOW], [CI_HIGH]] for accuracy difference versus API. The key
design insight is that transactional fields (price, availability)
should be grounded in live API data, while vector search expands
coverage for fuzzy intents. Our constraint-grounded evaluation
protocol, including PCA, CPR, and confusion matrix metrics, provides
a reproducible framework for assessing property search systems."

7.2 LIMITATIONS (bullet points)

Acknowledge honestly:
• Gold set size (30 questions) limits statistical power
• Single market dataset (Medan, Indonesia) may not generalize
• Vector index staleness not quantified under high churn
• No user study for perceived usefulness

7.3 FUTURE WORK (bullet points)

1. Dynamic routing: Learn policy to select Vector/API/Hybrid per query type
2. Adaptive thresholding: Calibrate CPR threshold T based on query category
3. Multi-turn dialogue: Handle clarification and follow-up questions
4. Scale evaluation: Expand to 100-200 questions with inter-annotator agreement
5. User study: Measure perceived usefulness with SUS and task completion time
```

---

## Reference Guidelines

```
EXISTING REFERENCES TO KEEP [1]-[20]:
All references in the original paper must be preserved.

SUGGESTED NEW REFERENCES TO ADD:

[21] For Wilcoxon test justification:
     Wilcoxon, F. (1945). Individual comparisons by ranking methods.
     Biometrics Bulletin, 1(6), 80-83.

[22] For McNemar's test:
     McNemar, Q. (1947). Note on the sampling error of the difference
     between correlated proportions or percentages. Psychometrika, 12(2), 153-157.

[23] For Bootstrap CI:
     Efron, B., & Tibshirani, R. J. (1994). An introduction to the bootstrap.
     CRC press.

[24] For constraint-based evaluation (if needed):
     Dalvi, N., et al. (2022). Towards trustworthy entity alignment using
     constraint-based evaluation.

FORMAT:
Use the same citation format as existing references (IEEE style for this journal).
```

---

## Placeholder Reference Table

Use this table to fill in actual values after evaluation:

```
=== METRICS PLACEHOLDERS ===

VECTOR:
VEC_PCA = [PENDING]
VEC_SS = [PENDING]
VEC_CPR = [PENDING]
VEC_PREC = [PENDING]
VEC_REC = [PENDING]
VEC_F1 = [PENDING]
VEC_ACC = [PENDING]
VEC_TP = [PENDING]
VEC_FP = [PENDING]
VEC_TN = [PENDING]
VEC_FN = [PENDING]

API:
API_PCA = [PENDING]
API_SS = [PENDING]
API_CPR = [PENDING]
API_PREC = [PENDING]
API_REC = [PENDING]
API_F1 = [PENDING]
API_ACC = [PENDING]
API_TP = [PENDING]
API_FP = [PENDING]
API_TN = [PENDING]
API_FN = [PENDING]

HYBRID:
HYBRID_PCA = [PENDING]
HYBRID_SS = [PENDING]
HYBRID_CPR = [PENDING]
HYBRID_PREC = [PENDING]
HYBRID_REC = [PENDING]
HYBRID_F1 = [PENDING]
HYBRID_ACC = [PENDING]
HYB_TP = [PENDING]
HYB_FP = [PENDING]
HYB_TN = [PENDING]
HYB_FN = [PENDING]

STATISTICAL:
P_VAL_HYB_VS_API = [PENDING]
P_VAL_HYB_VS_VEC = [PENDING]
CI_LOW_ACC = [PENDING]
CI_HIGH_ACC = [PENDING]

THRESHOLD SENSITIVITY (T=0.50, 0.60, 0.70, 0.80):
T50_PREC, T50_REC, T50_F1, T50_ACC = [PENDING]
T60_PREC, T60_REC, T60_F1, T60_ACC = [PENDING]
T70_PREC, T70_REC, T70_F1, T70_ACC = [PENDING]
T80_PREC, T80_REC, T80_F1, T80_ACC = [PENDING]
```

---

## Usage Instructions

1. **Start with Master Prompt** - Copy to Claude/ChatGPT to set context
2. **Process section by section** - Use each section prompt separately
3. **Fill placeholders** - Replace [PENDING] with actual values from evaluation
4. **Review consistency** - Ensure numbers match across sections
5. **Final proofread** - Check grammar, flow, and citation format

---

*Document created: 26 January 2026*
*For: Thesis RAG Property Chatbot - Paper Revision*
