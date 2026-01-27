# RAG-Tesis Improvement Roadmap

Dokumen ini merekap semua temuan dan rekomendasi improvement dari analisis codebase.
Setiap item dapat diselesaikan secara incremental.

---

## Status Legend

- [ ] Belum dikerjakan
- [x] Selesai
- [~] In Progress

---

## 1. Quick Wins (High Impact, Low Effort)

### 1.1 Embedding Cache
- **Status:** [x]
- **Priority:** HIGH
- **Effort:** 1-2 jam
- **Impact:** Reduce OpenAI API calls ~80%, reduce latency

**Problem:**
Setiap search query di-embed ulang via OpenAI API, meskipun query sama/mirip.

**Location:**
- `src/agents/tools.py` line 214 (search_properties tool)
- `src/knowledge/hybrid_search.py` (semantic search)

**Solution:**
```python
# Tambahkan LRU cache dengan TTL
from functools import lru_cache
from cachetools import TTLCache

# Cache embeddings for 1 hour
_embedding_cache = TTLCache(maxsize=1000, ttl=3600)

def get_cached_embedding(query: str, embeddings: OpenAIEmbeddings) -> list:
    if query not in _embedding_cache:
        _embedding_cache[query] = embeddings.embed_query(query)
    return _embedding_cache[query]
```

**Files to modify:**
- [x] `src/knowledge/hybrid_search.py`
- [x] `src/agents/tools.py` (uses HybridSearchService which now has cache)
- [x] `requirements.txt` (add cachetools)

---

### 1.2 Optimize ChromaDB Re-ranking
- **Status:** [x]
- **Priority:** HIGH
- **Effort:** 30 menit
- **Impact:** Reduce re-ranking latency ~70%

**Problem:**
Request k=50 documents dari ChromaDB untuk re-ranking padahal hanya butuh top 10-15.

**Location:**
- `src/knowledge/hybrid_search.py` line 288-291

**Current Code:**
```python
# Current - inefficient
results = self.property_store.vector_store.similarity_search_with_score(
    query=query,
    k=50  # Too many!
)
```

**Solution:**
```python
# Optimized - only fetch what we need
k_rerank = min(len(api_results) + 5, 20)  # Dynamic based on API results
results = self.property_store.vector_store.similarity_search_with_score(
    query=query,
    k=k_rerank
)
```

**Files to modify:**
- [ ] `src/knowledge/hybrid_search.py`

---

### 1.3 Structured Logging
- **Status:** [x]
- **Priority:** MEDIUM
- **Effort:** 2-3 jam
- **Impact:** Better debugging, performance monitoring

**Problem:**
Menggunakan `print()` untuk logging, sulit untuk debug dan monitor di production.

**Locations:**
- `src/adapters/metaproperty.py` line 180 (connection errors)
- `src/knowledge/hybrid_search.py` (search results)
- `src/agents/react_agent.py` (agent decisions)

**Solution:**
```python
import structlog

logger = structlog.get_logger()

# Instead of print()
logger.info("search_completed",
    query=query,
    results_count=len(results),
    latency_ms=elapsed_ms
)
```

**Files to modify:**
- [x] `src/adapters/metaproperty.py`
- [x] `src/knowledge/hybrid_search.py`
- [x] `src/agents/react_agent.py`
- [x] `src/agents/tools.py`
- [x] `requirements.txt` (structlog already present)
- [x] Create `src/utils/logging.py`

---

## 2. Memory & Context Management

### 2.1 Conversation Summarization
- **Status:** [x]
- **Priority:** HIGH
- **Effort:** 1 hari
- **Impact:** Prevent context explosion, support long conversations

**Problem:**
Conversation dengan 100+ messages akan melebihi context limit.
Field `summary` di schema sudah ada tapi tidak digunakan.

**Location:**
- `src/memory/sqlite_memory.py` line 86-100 (schema has summary field)
- `src/memory/sqlite_memory.py` line 442-536 (SlidingWindowMemory)

**Solution:**
1. Trigger summarization ketika message count > 50
2. Gunakan LLM untuk summarize older messages
3. Simpan summary ke database
4. Load summary + recent 20 messages

```python
class SlidingWindowMemory:
    def maybe_summarize(self, thread_id: str):
        """Summarize if conversation too long"""
        stats = self.storage.get_conversation_stats(thread_id)
        if stats and stats.get("message_count", 0) > 50:
            # Get older messages (beyond sliding window)
            older = self.storage.get_older_messages(thread_id, offset=20)
            if older:
                summary = self._generate_summary(older)
                self.storage.update_summary(thread_id, summary)
                # Optionally delete old messages to save space
```

**Files to modify:**
- [x] `src/memory/sqlite_memory.py` - Already implemented with:
  - `SlidingWindowMemory` class with `SUMMARIZE_THRESHOLD = 50`
  - `maybe_summarize()` for auto-trigger
  - `_generate_summary()` using LLM
  - `force_summarize()` for manual trigger
  - `get_older_messages()` and `delete_older_messages()` support

---

### 2.2 Optimize Message Validation
- **Status:** [ ]
- **Priority:** LOW
- **Effort:** 1 jam
- **Impact:** Minor latency improvement

**Problem:**
Two-pass validation setiap kali retrieve context messages.

**Location:**
- `src/memory/sqlite_memory.py` line 206-265

**Solution:**
Validate sekali saat save, bukan saat retrieve.

**Files to modify:**
- [ ] `src/memory/sqlite_memory.py`

---

### 2.3 Accurate Token Counting
- **Status:** [x]
- **Priority:** LOW
- **Effort:** 2 jam
- **Impact:** Accurate cost tracking

**Problem:**
Token estimation menggunakan `char/4` heuristic, tidak akurat.

**Location:**
- `scripts/chat.py` line 174-175, 259

**Solution:**
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

**Files to modify:**
- [x] `scripts/chat.py` - Updated to use `count_tokens()` from utils
- [x] `src/utils/tokens.py` - Created with:
  - `count_tokens()` - Accurate token counting
  - `count_message_tokens()` - For LangChain messages
  - `estimate_cost()` - Cost calculation
  - `truncate_to_token_limit()` - Safe truncation
  - `get_context_window_limit()` - Model limits
- [x] `requirements.txt` (added tiktoken>=0.7.0)

---

## 3. Search & Retrieval Improvements

### 3.1 Query Expansion / Synonyms
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 3-4 jam
- **Impact:** Reduce missed matches

**Problem:**
"Rumah" dan "Perumahan" tidak match padahal maksudnya sama.

**Solution:**
```python
SYNONYMS = {
    "rumah": ["rumah", "perumahan", "hunian", "residence"],
    "apartemen": ["apartemen", "apartment", "flat", "unit"],
    "ruko": ["ruko", "shophouse", "toko"],
    "murah": ["murah", "terjangkau", "ekonomis", "budget"],
    "mewah": ["mewah", "luxury", "premium", "elite"],
}

def expand_query(query: str) -> str:
    """Expand query with synonyms"""
    words = query.lower().split()
    expanded = []
    for word in words:
        if word in SYNONYMS:
            expanded.append(f"({' OR '.join(SYNONYMS[word])})")
        else:
            expanded.append(word)
    return " ".join(expanded)
```

**Files to modify:**
- [ ] Create `src/utils/query_expansion.py`
- [ ] `src/agents/tools.py`
- [ ] `src/knowledge/hybrid_search.py`

---

### 3.2 Post-Reranking Filters
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 2-3 jam
- **Impact:** Better user control over results

**Problem:**
User tidak bisa narrow results setelah search pertama.
Contoh: "dari hasil tadi, tampilkan hanya yang 3KT"

**Solution:**
Cache full results, allow post-filtering without re-search.

```python
# In tools.py
_full_search_results = {}  # Store all results, not just top 10

def filter_cached_results(filters: dict) -> list:
    """Filter cached results without re-searching"""
    results = _full_search_results.get("last_results", [])
    if "min_bedrooms" in filters:
        results = [r for r in results if r.bedrooms >= filters["min_bedrooms"]]
    if "max_price" in filters:
        results = [r for r in results if r.price <= filters["max_price"]]
    return results
```

**Files to modify:**
- [ ] `src/agents/tools.py`
- [ ] Add new tool `filter_results`

---

### 3.3 ChromaDB Fallback Pagination
- **Status:** [ ]
- **Priority:** LOW
- **Effort:** 1 jam
- **Impact:** Consistent result limits

**Problem:**
Fallback search (when API returns 0) tidak ada limit control.

**Location:**
- `src/knowledge/hybrid_search.py` line 162-262

**Solution:**
Add limit parameter to fallback search.

**Files to modify:**
- [ ] `src/knowledge/hybrid_search.py`

---

## 4. Thread Safety & Concurrency

### 4.1 Thread-Safe Tool Caching
- **Status:** [ ]
- **Priority:** HIGH (jika ada concurrent users)
- **Effort:** 2 jam
- **Impact:** Prevent race conditions

**Problem:**
`_last_search_results` adalah global dict, tidak thread-safe.

**Location:**
- `src/agents/tools.py` line 151-152

**Solution:**
```python
import threading
from contextvars import ContextVar

# Thread-local storage
_search_results_var: ContextVar[dict] = ContextVar('search_results', default={})

def get_cached_results() -> dict:
    return _search_results_var.get()

def set_cached_results(results: dict):
    _search_results_var.set(results)
```

**Files to modify:**
- [ ] `src/agents/tools.py`

---

### 4.2 Checkpointer Thread ID Cleanup
- **Status:** [ ]
- **Priority:** LOW
- **Effort:** 30 menit
- **Impact:** Memory management

**Problem:**
Setiap chat() call creates new UUID, grows thread_id namespace.

**Location:**
- `src/agents/react_agent.py` line 298-301

**Solution:**
Use consistent thread_id atau cleanup old checkpoints.

**Files to modify:**
- [ ] `src/agents/react_agent.py`

---

## 5. Thesis-Specific Features

### 5.1 Metrics Collection
- **Status:** [x]
- **Priority:** HIGH untuk thesis
- **Effort:** 1 hari
- **Impact:** Data untuk analisis thesis

**Metrics to track:**
- Search latency (API vs Hybrid vs ChromaDB-only)
- Re-ranking effectiveness (position changes)
- Tool execution counts
- Token usage per query type
- User satisfaction (if applicable)

**Solution:**
```python
# src/utils/metrics.py
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class SearchMetrics:
    timestamp: datetime
    query: str
    method: str  # "api", "hybrid", "chromadb"
    api_results: int
    final_results: int
    reranking_changes: int  # How many positions changed
    latency_ms: float
    tokens_used: int

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "query": self.query,
            "method": self.method,
            "api_results": self.api_results,
            "final_results": self.final_results,
            "reranking_changes": self.reranking_changes,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
        }

class MetricsCollector:
    def __init__(self, output_path: str = "data/metrics.jsonl"):
        self.output_path = output_path

    def log(self, metric: SearchMetrics):
        with open(self.output_path, "a") as f:
            f.write(json.dumps(metric.to_dict()) + "\n")
```

**Files to create/modify:**
- [x] Create `src/utils/metrics.py` - SearchMetrics, ToolMetrics, ConversationMetrics, MetricsCollector, Timer
- [x] `src/knowledge/hybrid_search.py` - Integrated SearchMetrics with Timer for latency tracking
- [x] `src/agents/tools.py` - Integrated ToolMetrics for search_properties, get_property_detail

---

### 5.2 A/B Testing Framework
- **Status:** [x]
- **Priority:** HIGH untuk thesis
- **Effort:** 1-2 hari
- **Impact:** Compare methods dengan data

**Purpose:**
Compare search methods:
- API only
- ChromaDB only
- Hybrid (berbagai weight configurations)

**Solution:**
```python
# src/utils/ab_testing.py
import random
from enum import Enum

class SearchMethod(Enum):
    API_ONLY = "api_only"
    CHROMADB_ONLY = "chromadb_only"
    HYBRID_60_40 = "hybrid_60_40"
    HYBRID_70_30 = "hybrid_70_30"
    HYBRID_80_20 = "hybrid_80_20"

class ABTestManager:
    def __init__(self, weights: dict = None):
        self.weights = weights or {
            SearchMethod.API_ONLY: 0.2,
            SearchMethod.HYBRID_60_40: 0.6,
            SearchMethod.CHROMADB_ONLY: 0.2,
        }

    def get_method(self, user_id: str = None) -> SearchMethod:
        """Get search method for this request"""
        # Consistent assignment per user, or random
        if user_id:
            # Hash user_id for consistent assignment
            hash_val = hash(user_id) % 100
            # ... assign based on hash
        return random.choices(
            list(self.weights.keys()),
            weights=list(self.weights.values())
        )[0]
```

**Files to create/modify:**
- [x] Create `src/utils/ab_testing.py` - SearchMethod enum, ABTestConfig, ABTestManager with presets
- [x] `src/knowledge/hybrid_search.py` - Integrated A/B method selection with semantic_weight override

---

### 5.3 Metrics Export for Analysis
- **Status:** [x]
- **Priority:** HIGH untuk thesis
- **Effort:** 3-4 jam
- **Impact:** Easy thesis data analysis

**Solution:**
```python
# scripts/export_metrics.py
import pandas as pd
import json

def export_to_csv(jsonl_path: str, csv_path: str):
    """Export metrics to CSV for analysis"""
    records = []
    with open(jsonl_path) as f:
        for line in f:
            records.append(json.loads(line))

    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)

    # Also generate summary stats
    summary = df.groupby("method").agg({
        "latency_ms": ["mean", "std", "min", "max"],
        "reranking_changes": "mean",
        "final_results": "mean",
    })
    summary.to_csv(csv_path.replace(".csv", "_summary.csv"))
```

**Files to create:**
- [x] `scripts/export_metrics.py` - Export JSONL to CSV with summaries
- [x] `scripts/analyze_metrics.py` - Generate charts, statistics, and markdown report

---

## 6. Error Handling & Resilience

### 6.1 Retry Logic for API Calls
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 2 jam
- **Impact:** Better reliability

**Problem:**
API calls fail tanpa retry, langsung error.

**Location:**
- `src/adapters/metaproperty.py`

**Solution:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def _make_request(self, method: str, url: str, **kwargs):
    async with self.client as client:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
```

**Files to modify:**
- [ ] `src/adapters/metaproperty.py`
- [ ] `requirements.txt` (add tenacity)

---

### 6.2 Graceful Degradation
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 2 jam
- **Impact:** Better UX when components fail

**Problem:**
Jika ChromaDB down, entire hybrid search fails.

**Solution:**
Fallback chain: Hybrid → API-only → Error message

**Files to modify:**
- [ ] `src/knowledge/hybrid_search.py`
- [ ] `src/agents/tools.py`

---

## 7. Batch Operations

### 7.1 Batch Property Sync with Retry
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 3-4 jam
- **Impact:** Reliable large-scale sync

**Problem:**
`sync_properties.py` tidak handle failures well untuk large batches.

**Solution:**
```python
async def batch_sync_with_retry(
    adapter: MetaPropertyAPIAdapter,
    store: PropertyStore,
    batch_size: int = 100,
    max_retries: int = 3
):
    """Sync properties in batches with retry logic"""
    pending = await adapter.get_pending_ingest()

    for i in range(0, len(pending), batch_size):
        batch = pending[i:i+batch_size]
        failed = []

        for prop in batch:
            for attempt in range(max_retries):
                try:
                    store.upsert_property(prop)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed.append((prop.id, str(e)))
                    await asyncio.sleep(2 ** attempt)

        # Mark successful ones
        successful_ids = [p.id for p in batch if p.id not in [f[0] for f in failed]]
        await adapter.mark_ingested(successful_ids)

        logger.info(f"Batch {i//batch_size + 1}: {len(successful_ids)} success, {len(failed)} failed")
```

**Files to modify:**
- [ ] `scripts/sync_properties.py`

---

## Implementation Order (Recommended)

### Phase 1: Quick Wins (Week 1)
1. [ ] 1.2 Optimize ChromaDB Re-ranking (30 min)
2. [ ] 1.1 Embedding Cache (2 jam)
3. [ ] 1.3 Structured Logging (3 jam)

### Phase 2: Thesis Features (Week 2)
4. [ ] 5.1 Metrics Collection (1 hari)
5. [ ] 5.2 A/B Testing Framework (1 hari)
6. [ ] 5.3 Metrics Export (3 jam)

### Phase 3: Memory & Context (Week 3)
7. [ ] 2.1 Conversation Summarization (1 hari)
8. [ ] 2.3 Accurate Token Counting (2 jam)

### Phase 4: Search Improvements (Week 4)
9. [ ] 3.1 Query Expansion (3 jam)
10. [ ] 4.1 Thread-Safe Caching (2 jam)
11. [ ] 6.1 Retry Logic (2 jam)

### Phase 5: Polish (Week 5)
12. [ ] 3.2 Post-Reranking Filters (3 jam)
13. [ ] 6.2 Graceful Degradation (2 jam)
14. [ ] 7.1 Batch Sync (4 jam)

---

## 8. Security & Multi-User Support

### 8.1 User Isolation for Chat History
- **Status:** [x]
- **Priority:** 🔴 CRITICAL (untuk production)
- **Effort:** 2-3 jam
- **Impact:** Privacy & security - mencegah data bocor antar user

**Problem:**
Saat ini chat history **TIDAK dipisahkan per user** dengan benar.

**Current State:**
```python
# scripts/chat_api_only.py
thread_id = "api_only_chat"  # ❌ SAMA untuk semua user!

# scripts/chat_hybrid.py
thread_id = "hybrid_chat"    # ❌ SAMA untuk semua user!

# scripts/chat.py
thread_id = "interactive"    # ❌ SAMA untuk semua user!
```

**Database Schema (sudah ada user_id tapi tidak dipakai):**
```sql
conversations (
    thread_id TEXT UNIQUE,  -- Primary identifier
    user_id TEXT,           -- Ada tapi OPTIONAL dan sering NULL!
)
```

**Risiko:**
- User A bisa lihat chat history User B
- Data properti yang dicari bocor ke user lain
- Tidak comply dengan privacy standards

**Solution:**

**Step 1: Update thread_id pattern**
```python
# Format: {user_id}_{context}_{optional_session}
thread_id = f"{user_id}_api_only"

# Atau dengan session untuk multiple conversations
thread_id = f"{user_id}_api_only_{session_id}"
```

**Step 2: Enforce user_id di memory**
```python
# src/memory/sqlite_memory.py

def get_or_create_conversation(
    self,
    thread_id: str,
    user_id: str,  # Make REQUIRED, not optional!
) -> int:
    """Get existing conversation or create new one"""
    with self._get_connection() as conn:
        cursor = conn.cursor()

        # Include user_id in lookup for proper isolation
        cursor.execute(
            "SELECT id FROM conversations WHERE thread_id = ? AND user_id = ?",
            (thread_id, user_id)
        )
        row = cursor.fetchone()

        if row:
            return row["id"]

        # Create new - user_id is required
        cursor.execute(
            """INSERT INTO conversations (thread_id, user_id, created_at, updated_at)
               VALUES (?, ?, ?, ?)""",
            (thread_id, user_id, datetime.now(), datetime.now())
        )
        return cursor.lastrowid
```

**Step 3: Update chat scripts**
```python
# scripts/chat_api_only.py

def main():
    # Get user ID at start
    print("Enter your user ID (or press Enter for 'guest'):")
    user_id = input().strip() or "guest"

    thread_id = f"{user_id}_api_only"

    # Pass user_id to agent
    agent = ReActPropertyAgent(...)

    while True:
        # ...
        result = agent.chat(user_input, thread_id=thread_id, user_id=user_id)
```

**Step 4: Add user_id to all chat interfaces**
```python
# src/agents/react_agent.py

def chat(
    self,
    message: str,
    thread_id: str = "default",
    user_id: str = "anonymous",  # Add default, but encourage explicit
    user_role: str = "user",
) -> str:
    # Validate user_id is not empty
    if not user_id or user_id == "anonymous":
        logger.warning("chat_without_user_id", thread_id=thread_id)

    # ... rest of implementation
```

**Step 5: Add query filter for list_conversations**
```python
# Already exists but ensure it's used:
def list_conversations(
    self,
    user_id: str,  # Make required, not optional
    limit: int = 20,
    offset: int = 0,
) -> List[Dict]:
    """List conversations for a specific user only"""
```

**Files to modify:**
- [x] `src/memory/sqlite_memory.py` - Enforce user_id
- [x] `src/agents/react_agent.py` - Add user_id validation
- [x] `scripts/chat_api_only.py` - Ask for user_id
- [x] `scripts/chat_hybrid.py` - Ask for user_id
- [x] `scripts/chat.py` - Ask for user_id
- [ ] Add database migration to add NOT NULL constraint (optional)

**Testing:**
```bash
# Test isolation
# Terminal 1: user_id = "alice"
python scripts/chat_api_only.py
> alice
> cari rumah di cemara

# Terminal 2: user_id = "bob"
python scripts/chat_api_only.py
> bob
> clear  # Should NOT see Alice's history
```

---

### 8.2 Tool Result Cache per User
- **Status:** [x]
- **Priority:** HIGH (terkait dengan 8.1)
- **Effort:** 1 jam
- **Impact:** Prevent cross-user data leakage

**Problem:**
`_last_search_results` adalah global dict yang shared antar semua users.

```python
# src/agents/tools.py line 151-152
_last_search_results: dict[int, "Property"] = {}  # ❌ GLOBAL!
```

**Risiko:**
- User A search → cache filled
- User B says "detail nomor 3" → Gets User A's result!

**Solution:**
```python
# Option 1: Thread-local storage
from contextvars import ContextVar

_search_results_var: ContextVar[dict] = ContextVar('search_results', default={})

def get_user_search_results() -> dict:
    return _search_results_var.get()

def set_user_search_results(results: dict):
    _search_results_var.set(results)


# Option 2: User-keyed cache (if user_id available)
_user_search_results: dict[str, dict[int, "Property"]] = {}

def get_user_results(user_id: str) -> dict:
    return _user_search_results.get(user_id, {})

def set_user_results(user_id: str, results: dict):
    _user_search_results[user_id] = results
```

**Files to modify:**
- [x] `src/agents/tools.py` - Change global cache to user-scoped
- [x] `src/agents/react_agent.py` - Set user context before tool execution

---

### 8.3 API Token Security
- **Status:** [ ]
- **Priority:** MEDIUM
- **Effort:** 1 jam
- **Impact:** Prevent credential exposure

**Problem:**
API tokens loaded via environment variables, but may be logged or exposed.

**Solution:**
```python
# Don't log tokens
logger.info("api_connected",
    url=api_url,
    has_token=bool(api_token)  # ✓ Don't log actual token
)

# Mask in error messages
def mask_token(token: str) -> str:
    if len(token) > 8:
        return token[:4] + "****" + token[-4:]
    return "****"
```

**Files to modify:**
- [ ] `src/adapters/metaproperty.py`
- [ ] `src/utils/logging.py`

---

## Implementation Order (Recommended)

### Phase 1: Quick Wins (Week 1)
1. [x] 1.2 Optimize ChromaDB Re-ranking (30 min)
2. [x] 1.1 Embedding Cache (2 jam)
3. [x] 1.3 Structured Logging (3 jam)

### Phase 2: Security (Week 1-2) ⚠️ PRIORITAS!
4. [x] 8.1 User Isolation for Chat History (2-3 jam) 🔴
5. [x] 8.2 Tool Result Cache per User (1 jam)

### Phase 3: Thesis Features (Week 2)
6. [x] 5.1 Metrics Collection (1 hari) ✅
7. [x] 5.2 A/B Testing Framework (1 hari) ✅
8. [x] 5.3 Metrics Export (3 jam) ✅

### Phase 4: Memory & Context (Week 3)
9. [x] 2.1 Conversation Summarization (1 hari) ✅
10. [x] 2.3 Accurate Token Counting (2 jam) ✅

### Phase 5: Search Improvements (Week 4)
11. [ ] 3.1 Query Expansion (3 jam)
12. [ ] 4.1 Thread-Safe Caching (2 jam)
13. [ ] 6.1 Retry Logic (2 jam)

### Phase 6: Polish (Week 5)
14. [ ] 3.2 Post-Reranking Filters (3 jam)
15. [ ] 6.2 Graceful Degradation (2 jam)
16. [ ] 7.1 Batch Sync (4 jam)

---

## Notes

- Setiap improvement harus di-test sebelum merge
- Update dokumentasi setelah implementasi
- Track metrics sebelum dan sesudah improvement untuk thesis
- **8.1 User Isolation adalah CRITICAL untuk production!**

---

*Last updated: 2026-01-23*
