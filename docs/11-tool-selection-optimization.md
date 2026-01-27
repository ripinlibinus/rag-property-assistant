# Tool Selection Optimization Guide

Strategi untuk meningkatkan ketepatan agent dalam memilih tools yang tepat.

**Last Updated:** 2026-01-23

---

## 📋 Table of Contents

1. [Current Challenges](#current-challenges)
2. [Optimization Strategies](#optimization-strategies)
3. [Implementation Guide](#implementation-guide)
4. [Metrics & Evaluation](#metrics--evaluation)
5. [Advanced Techniques](#advanced-techniques)

---

## 🎯 Current Challenges

### 1. Ambiguous Queries

**Problem:**
```
User: "cari rumah cemara"
Could mean:
- search_properties(query="cemara") ✓ Correct
- search_nearby(location_name="cemara") ✗ Less appropriate
```

**Why it happens:**
- "cemara" could be area name OR landmark
- No explicit radius mentioned
- LLM must infer intent

### 2. Tool Overlap

**Problem:**
```
User: "detail properti nomor 3"
Could use:
- get_property_by_number(number=3) ✓ Correct
- get_property_detail(property_id=???) ✗ Needs ID first
```

**Why it happens:**
- Both tools get property details
- get_property_by_number is more convenient
- LLM might not know about cached results

### 3. Missing Context

**Problem:**
```
User: "yang paling murah?"
Should:
- NO tool call, analyze previous results ✓
But might:
- Call search_properties again ✗ Unnecessary
```

**Why it happens:**
- LLM doesn't remember what tools were called before
- No explicit instruction about comparative questions

### 4. Over-calling Tools

**Problem:**
```
User: "halo"
Might call:
- get_motivation() ✗ Unnecessary
Should:
- Just respond "Halo! Ada yang bisa saya bantu?" ✓
```

---

## 🚀 Optimization Strategies

### Strategy 1: Enhanced System Prompt

**Current Issue:**
System prompt terlalu general, tidak cukup specific examples.

**Solution:**
Add more concrete decision rules dan examples.

#### Implementation

**File:** `src/agents/react_agent.py`

```python
REACT_SYSTEM_PROMPT = """You are a helpful real estate assistant for property agents in Indonesia.

# ============================================================================
# TOOL SELECTION DECISION TREE
# ============================================================================

## Step 1: Determine Query Type

1. **Greeting/Small talk** → NO TOOL, just respond
   - "halo", "hi", "terima kasih", "thanks"
   - Response: Friendly greeting

2. **Comparative/Analysis** → NO TOOL, analyze previous results
   - "yang paling murah?", "mana yang terbesar?", "bandingkan nomor 1 dan 3"
   - Requires: Previous search results in context
   - Response: Analyze and compare from chat history

3. **Property Search (New)** → Use search tool
   - "cari rumah...", "ada ruko...", "properti di..."
   - Decision: search_properties OR search_nearby

4. **Property Detail (Specific)** → Use detail tool
   - "detail nomor X" → get_property_by_number
   - "detail id XXX" → get_property_detail
   - "info properti X" → Determine which based on X format

5. **Knowledge/Tips** → Use knowledge tools
   - "apa itu SHM?" → search_knowledge
   - "tips closing" → get_sales_tips
   - "butuh motivasi" → get_motivation

## Step 2: Choose Between search_properties vs search_nearby

**Use search_properties when:**
- ✓ User mentions AREA NAME directly: "cemara asri", "sunggal", "johor"
- ✓ NO radius mentioned
- ✓ General search: "cari rumah di medan"

**Use search_nearby when:**
- ✓ User mentions LANDMARK: "USU", "Sun Plaza", "Kualanamu Airport"
- ✓ User mentions RADIUS/DISTANCE: "radius 3km", "jarak 5km", "dekat USU"
- ✓ Keywords: "dekat", "sekitar", "nearby"

**Examples:**
```
"cari rumah di cemara asri" → search_properties (area name)
"cari rumah dekat USU" → search_nearby (landmark + "dekat")
"rumah sekitar Sun Plaza radius 5km" → search_nearby (landmark + radius)
"ada ruko di sunggal?" → search_properties (area name)
```

## Step 3: Choose Between get_property_by_number vs get_property_detail

**Use get_property_by_number when:**
- ✓ User refers by NUMBER: "nomor 3", "yang ke-5", "no 8"
- ✓ There are cached search results (check context)

**Use get_property_detail when:**
- ✓ User provides explicit ID: "detail id prop-12345"
- ✓ No cached results available

## Step 4: Validate Before Calling

Before calling any tool, ask yourself:
1. Is this really necessary? Can I answer from context?
2. Do I have all required parameters?
3. Is there a more appropriate tool?

# ============================================================================
# TOOL DESCRIPTIONS
# ============================================================================

1. **search_properties** - General property search
   - When: Area name, city, general criteria
   - Examples: "rumah di cemara", "ruko sunggal", "apartemen medan"

2. **search_nearby** - Radius-based search near landmark
   - When: Landmark + radius OR "dekat/sekitar" keyword
   - Examples: "dekat USU 3km", "sekitar Sun Plaza"

3. **get_property_by_number** - Get cached result by number
   - When: "nomor X" from previous search
   - Requirement: Previous search must exist

4. **get_property_detail** - Get by property ID
   - When: User provides explicit ID
   - Format: Usually "prop-XXXXX" or similar

5. **geocode_location** - Convert location to coordinates
   - When: User asks "koordinat X" or needs lat/lng
   - Usually not needed (search_nearby does this automatically)

6. **search_knowledge** - Search knowledge base
   - When: Questions about real estate, laws, procedures
   - Examples: "apa itu SHM?", "prosedur KPR?"

7. **get_sales_tips** - Get sales techniques
   - When: Asking for tips, techniques, how-to
   - Examples: "tips closing", "cara follow up"

8. **get_motivation** - Get motivational message
   - When: User feels down or asks for motivation
   - Keywords: "motivasi", "semangat", "down"

# ============================================================================
# COMMON MISTAKES TO AVOID
# ============================================================================

❌ **Mistake 1:** Calling tool for greetings
```
User: "halo"
Wrong: get_motivation()
Right: "Halo! Ada yang bisa saya bantu mencari properti?"
```

❌ **Mistake 2:** Calling search again for comparison
```
User: "yang paling murah?"
Wrong: search_properties(...)
Right: Analyze previous search results from context
```

❌ **Mistake 3:** Using wrong search tool
```
User: "cari rumah di cemara asri"
Wrong: search_nearby(location_name="cemara asri")
Right: search_properties(query="cemara asri")
Reason: Cemara Asri is an AREA NAME, not a landmark
```

❌ **Mistake 4:** Calling get_property_detail with number
```
User: "detail nomor 3"
Wrong: get_property_detail(property_id="3")
Right: get_property_by_number(number=3)
```

# ============================================================================
# LANGUAGE & STYLE
# ============================================================================

- Mirror user's language (Indonesian/English)
- Mirror formality level (formal/casual)
- Default to polite Indonesian if unclear

Today's date: {date}
"""
```

**Key Improvements:**
- Decision tree for systematic tool selection
- Clear "when to use" rules
- Common mistakes section
- More examples

---

### Strategy 2: Better Tool Descriptions

**Current Issue:**
Tool descriptions dalam function docstring tidak cukup detail.

**Solution:**
Enhance `@tool` descriptions dengan decision criteria.

#### Implementation

**File:** `src/agents/tools.py`

```python
@tool(args_schema=SearchPropertiesInput)
def search_properties(...) -> str:
    """
    🏠 GENERAL PROPERTY SEARCH - Use for area/city-based searches

    PRIMARY USE CASES:
    ✓ User mentions area/district name: "cemara asri", "sunggal", "johor"
    ✓ General city search: "rumah di medan", "properti jakarta"
    ✓ NO radius/distance mentioned
    ✓ NOT a landmark-based search

    DO NOT USE WHEN:
    ✗ User mentions landmark + radius: "dekat USU 3km" → use search_nearby
    ✗ User mentions "dekat", "sekitar", "nearby" → use search_nearby

    FEATURES:
    - Hybrid search: API filtering + ChromaDB semantic re-ranking
    - Supports all filters: price, bedrooms, property_type, source
    - Caches top 10 results for later reference by number
    - Semantic matching for quality/style queries

    EXAMPLES:
    ✓ "cari rumah di cemara asri" → query="cemara asri", property_type="house"
    ✓ "ada ruko di sunggal harga 500 juta" → query="sunggal", property_type="shophouse", max_price=500000000
    ✓ "rumah taman luas nyaman" → query="rumah taman luas nyaman" (semantic search)
    ✓ "proyek baru di medan" → query="medan", source="project"

    RETURNS: Formatted list with property details, coordinates, relevance scores
    """
    # ... implementation ...


@tool(args_schema=SearchNearbyInput)
def search_nearby(...) -> str:
    """
    📍 RADIUS-BASED SEARCH - Use for landmark-based searches with distance

    PRIMARY USE CASES:
    ✓ User mentions LANDMARK: "USU", "Sun Plaza", "Kualanamu"
    ✓ User mentions RADIUS/DISTANCE: "radius 3km", "jarak 5km", "dalam 2km"
    ✓ Keywords present: "dekat", "sekitar", "nearby", "around"

    DO NOT USE WHEN:
    ✗ User mentions area NAME (not landmark): "cemara asri" → use search_properties
    ✗ No distance/radius context → use search_properties

    PROCESS:
    1. Geocode landmark → lat/lng (automatic)
    2. Search properties within radius
    3. Sort by distance (closest first)

    EXAMPLES:
    ✓ "cari rumah dekat USU radius 3km" → location_name="USU", radius_km=3
    ✓ "properti sekitar Sun Plaza" → location_name="Sun Plaza", radius_km=3 (default)
    ✓ "rumah dalam jarak 5km dari Kualanamu" → location_name="Kualanamu", radius_km=5

    RETURNS: Distance-sorted list with distance indicators (📏 1.2km)
    """
    # ... implementation ...


@tool(args_schema=GetPropertyByNumberInput)
def get_property_by_number(number: int) -> str:
    """
    🔢 GET CACHED RESULT BY NUMBER - Reference previous search by position

    PRIMARY USE CASES:
    ✓ User refers by number: "nomor 3", "yang ke-5", "no 8", "hasil ke-2"
    ✓ Previous search exists (check context for search_properties/search_nearby calls)

    DO NOT USE WHEN:
    ✗ No previous search in context
    ✗ User provides property ID (use get_property_detail instead)
    ✗ Comparative questions ("yang paling murah") → analyze without tool call

    REQUIREMENTS:
    - Previous search must have cached results (last 10 results)
    - Number must be 1-10

    EXAMPLES:
    ✓ "detail nomor 3" → number=3
    ✓ "yang ke-5 gimana?" → number=5
    ✓ "info lebih lanjut untuk hasil ke-2" → number=2

    RETURNS: Full property details + contact info
    """
    # ... implementation ...
```

**Key Improvements:**
- ✓/✗ notation untuk clear guidelines
- "DO NOT USE WHEN" section
- More specific examples
- Feature highlights

---

### Strategy 3: Few-Shot Examples in Prompt

**Current Issue:**
LLM learns better with concrete examples.

**Solution:**
Add few-shot examples di system prompt.

#### Implementation

```python
REACT_SYSTEM_PROMPT = """
...

# ============================================================================
# DECISION EXAMPLES (Few-Shot Learning)
# ============================================================================

## Example 1: Area Search
```
User: "cari rumah di cemara asri"

Reasoning:
- "cemara asri" is an AREA NAME (not landmark)
- No radius mentioned
- Property type: "rumah" = house

Decision: search_properties
Parameters: query="cemara asri", property_type="house"
```

## Example 2: Landmark Search
```
User: "properti dekat USU radius 3km"

Reasoning:
- "USU" is a LANDMARK (university)
- Keyword "dekat" present
- Explicit radius: 3km

Decision: search_nearby
Parameters: location_name="USU", radius_km=3
```

## Example 3: Reference by Number
```
User: "detail nomor 3"

Reasoning:
- User refers by NUMBER from previous search
- Previous search results exist in context
- Want full details

Decision: get_property_by_number
Parameters: number=3
```

## Example 4: Comparative Question
```
User: "yang paling murah?"

Reasoning:
- Comparative question about previous results
- Previous search results in context
- No new search needed

Decision: NO TOOL CALL
Action: Analyze previous search results and compare prices
```

## Example 5: Greeting
```
User: "halo kak"

Reasoning:
- Simple greeting
- No property-related question
- Casual style ("kak")

Decision: NO TOOL CALL
Response: "Halo! Ada yang bisa saya bantu mencari properti? 😊"
```

## Example 6: Source Type Detection
```
User: "ada proyek baru di medan?"

Reasoning:
- Keywords: "proyek baru" = new development
- Source type: project (primary market)
- Location: medan

Decision: search_properties
Parameters: query="medan", source="project"
```

...
"""
```

---

### Strategy 4: Input Validation & Error Messages

**Current Issue:**
Tools kadang dipanggil dengan parameter yang salah/kurang.

**Solution:**
Add validation layer dan helpful error messages.

#### Implementation

**File:** `src/agents/tools.py`

```python
@tool(args_schema=GetPropertyByNumberInput)
def get_property_by_number(number: int) -> str:
    """..."""

    # Validation 1: Check cache exists
    if not _last_search_results:
        return """❌ Tidak ada hasil pencarian sebelumnya.

Silakan lakukan pencarian terlebih dahulu dengan:
- search_properties (untuk area/kota)
- search_nearby (untuk landmark + radius)

Kemudian Anda bisa reference hasil dengan nomor."""

    # Validation 2: Check number range
    if number < 1 or number > 10:
        available = list(_last_search_results.keys())
        return f"""❌ Nomor {number} tidak valid.

Pilihan yang tersedia: {min(available)} sampai {max(available)}
Total hasil cache: {len(available)} properti"""

    # Validation 3: Check number exists
    prop = _last_search_results.get(number)
    if not prop:
        return f"""❌ Properti nomor {number} tidak ditemukan dalam cache.

Kemungkinan:
1. Nomor salah (cek hasil pencarian terakhir)
2. Cache sudah cleared (lakukan search ulang)"""

    # ... rest of implementation ...


@tool(args_schema=SearchNearbyInput)
def search_nearby(...) -> str:
    """..."""

    # Validation: Warn if location is likely an area name
    AREA_NAMES = [
        "cemara asri", "sunggal", "johor", "helvetia",
        "medan area", "medan kota", "setia budi"
    ]

    location_lower = location_name.lower()
    if any(area in location_lower for area in AREA_NAMES):
        # Still execute, but add note
        note = f"""
⚠️ Note: '{location_name}' terdeteksi sebagai nama area.
Untuk pencarian area, search_properties mungkin lebih tepat.
Tetap melanjutkan pencarian radius-based...\n"""
    else:
        note = ""

    # ... rest of implementation ...

    return note + result
```

**Benefits:**
- LLM learns from error messages
- Next time it will choose correct tool
- User gets better experience

---

### Strategy 5: Tool Result Quality Signals

**Current Issue:**
LLM tidak tahu apakah tool call berhasil/gagal.

**Solution:**
Add clear success/failure signals in tool output.

#### Implementation

```python
@tool(args_schema=SearchPropertiesInput)
def search_properties(...) -> str:
    """..."""
    try:
        # ... search logic ...

        if not properties:
            return f"""🔍 SEARCH RESULT: 0 properties found

Query: "{query}"
Filters: {filters_summary}

Suggestions:
1. Try broader area: expand to nearby districts
2. Relax filters: increase price range, reduce bedrooms requirement
3. Try search_nearby if looking near a landmark
4. Check spelling of location name"""

        # Success case
        output = f"""✅ SEARCH SUCCESSFUL: {total} properties found

Showing top {len(properties[:10])} results (sorted by relevance):
"""
        # ... format results ...

        return output

    except Exception as e:
        return f"""❌ SEARCH FAILED

Error: {str(e)}

Possible solutions:
1. Check if API is available
2. Simplify search criteria
3. Try again in a moment"""
```

**Benefits:**
- Clear status indicators (✅/❌/⚠️)
- Actionable suggestions
- LLM can handle failures gracefully

---

### Strategy 6: Context-Aware Tool Selection

**Current Issue:**
LLM tidak selalu aware tentang conversation history.

**Solution:**
Add context check in system prompt.

#### Implementation

```python
REACT_SYSTEM_PROMPT = """
...

# ============================================================================
# CONTEXT AWARENESS
# ============================================================================

Before calling ANY tool, check conversation history:

1. **Has a search been done recently?**
   - If YES and user asks comparative ("yang paling murah?"): ANALYZE, don't search again
   - If NO: Need to search first

2. **Are there cached results?**
   - If YES and user says "nomor 3": Use get_property_by_number
   - If NO: Need to search first, then can reference by number

3. **Is this a follow-up question?**
   - "Detail tentang itu?" → Refer to last mentioned property
   - "Bagaimana dengan yang lain?" → Refer to previous results

4. **What was the last tool called?**
   - If search_properties just called: Results are cached
   - If get_property_detail just called: User has full info
   - If get_sales_tips just called: Don't repeat same tips

EXAMPLE CONVERSATION:
```
User: "cari rumah di cemara"
You: [Call search_properties] → Shows 10 results
     [Cache results 1-10]

User: "yang paling murah?"
You: [NO TOOL] → Analyze cached results
     "Yang paling murah adalah nomor 5: Rp 650 juta"

User: "detail nomor 5"
You: [Call get_property_by_number(5)] → Shows full details
     [Remember: this is prop-12345]

User: "bisa nego harganya?"
You: [Call get_sales_tips("negotiation")] → Shows tips
```

...
"""
```

---

## 📊 Metrics & Evaluation

### Track Tool Selection Accuracy

**File:** `src/utils/tool_metrics.py` (NEW)

```python
"""Track tool selection accuracy for optimization"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
from typing import Optional, List


@dataclass
class ToolCallMetric:
    """Metric for a single tool call"""
    timestamp: str
    user_query: str
    tool_called: str
    parameters: dict
    result_status: str  # "success", "failure", "wrong_tool"
    result_summary: str
    conversation_id: str

    # Evaluation (manual or automatic)
    was_correct_tool: Optional[bool] = None  # True/False/None
    should_have_used: Optional[str] = None   # Alternative tool name
    notes: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class ToolMetricsCollector:
    """Collect and analyze tool selection metrics"""

    def __init__(self, output_path: Path = None):
        self.output_path = output_path or Path("data/metrics/tool_calls.jsonl")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def log_tool_call(
        self,
        user_query: str,
        tool_called: str,
        parameters: dict,
        result_status: str,
        result_summary: str,
        conversation_id: str,
    ):
        """Log a tool call"""
        metric = ToolCallMetric(
            timestamp=datetime.now().isoformat(),
            user_query=user_query,
            tool_called=tool_called,
            parameters=parameters,
            result_status=result_status,
            result_summary=result_summary,
            conversation_id=conversation_id,
        )

        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(metric.to_dict(), ensure_ascii=False) + "\n")

    def get_tool_accuracy(self) -> dict:
        """Calculate tool selection accuracy"""
        if not self.output_path.exists():
            return {}

        total = 0
        correct = 0
        wrong_tool_count = 0

        tool_usage = {}

        with open(self.output_path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                total += 1

                tool = data["tool_called"]
                tool_usage[tool] = tool_usage.get(tool, 0) + 1

                if data.get("was_correct_tool") is True:
                    correct += 1
                elif data.get("was_correct_tool") is False:
                    wrong_tool_count += 1

        evaluated = correct + wrong_tool_count

        return {
            "total_calls": total,
            "evaluated": evaluated,
            "correct": correct,
            "wrong": wrong_tool_count,
            "accuracy": correct / evaluated if evaluated > 0 else 0,
            "tool_usage": tool_usage,
        }

    def get_common_mistakes(self) -> List[dict]:
        """Get most common tool selection mistakes"""
        if not self.output_path.exists():
            return []

        mistakes = []

        with open(self.output_path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                if data.get("was_correct_tool") is False:
                    mistakes.append({
                        "query": data["user_query"],
                        "wrong_tool": data["tool_called"],
                        "should_use": data.get("should_have_used"),
                        "notes": data.get("notes"),
                    })

        return mistakes


# Global instance
_metrics_collector = None

def get_metrics_collector() -> ToolMetricsCollector:
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = ToolMetricsCollector()
    return _metrics_collector
```

**Usage in agent:**

```python
# In src/agents/react_agent.py

from ..utils.tool_metrics import get_metrics_collector

class ReActPropertyAgent:
    def chat(self, message: str, thread_id: str = "default", ...):
        # ... existing code ...

        # Track tool calls
        metrics = get_metrics_collector()

        result = self.graph.invoke(inputs, config)

        # Extract tool calls from result
        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    # Find corresponding ToolMessage
                    tool_result = self._find_tool_result(result["messages"], tc["id"])

                    metrics.log_tool_call(
                        user_query=message,
                        tool_called=tc["name"],
                        parameters=tc["args"],
                        result_status=self._determine_status(tool_result),
                        result_summary=tool_result[:200] if tool_result else "",
                        conversation_id=thread_id,
                    )

        # ... return response ...
```

---

### Evaluation Script

**File:** `scripts/evaluate_tool_selection.py` (NEW)

```python
"""Evaluate tool selection accuracy"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.tool_metrics import get_metrics_collector


def main():
    collector = get_metrics_collector()

    print("=" * 60)
    print("TOOL SELECTION ACCURACY REPORT")
    print("=" * 60)

    stats = collector.get_tool_accuracy()

    print(f"\nTotal tool calls: {stats['total_calls']}")
    print(f"Evaluated: {stats['evaluated']}")
    print(f"Accuracy: {stats['accuracy']:.1%}")

    print("\n📊 Tool Usage:")
    for tool, count in sorted(stats['tool_usage'].items(), key=lambda x: -x[1]):
        print(f"  {tool}: {count} calls")

    print("\n❌ Common Mistakes:")
    mistakes = collector.get_common_mistakes()
    for i, mistake in enumerate(mistakes[:10], 1):
        print(f"\n{i}. Query: \"{mistake['query']}\"")
        print(f"   Wrong tool: {mistake['wrong_tool']}")
        print(f"   Should use: {mistake['should_use']}")
        if mistake['notes']:
            print(f"   Notes: {mistake['notes']}")


if __name__ == "__main__":
    main()
```

---

## 🎓 Advanced Techniques

### 1. Tool Use Classifier (Pre-filter)

Add lightweight classifier before LLM to filter obvious cases.

```python
class ToolPreFilter:
    """Pre-filter to catch obvious tool selections before LLM"""

    GREETING_PATTERNS = ["halo", "hi", "hello", "terima kasih", "thanks", "bye"]
    COMPARATIVE_PATTERNS = ["yang paling", "mana yang", "bandingkan", "lebih murah", "lebih besar"]
    NEARBY_PATTERNS = ["dekat", "sekitar", "nearby", "radius", "jarak", "km dari"]

    @staticmethod
    def should_skip_llm(query: str) -> Optional[dict]:
        """Check if we can skip LLM for obvious cases"""
        query_lower = query.lower().strip()

        # Greeting - no tool needed
        if any(greeting in query_lower for greeting in ToolPreFilter.GREETING_PATTERNS):
            if len(query_lower) < 20:  # Short greeting
                return {"action": "respond", "message": "greeting"}

        # Comparative - analyze previous results
        if any(pattern in query_lower for pattern in ToolPreFilter.COMPARATIVE_PATTERNS):
            return {"action": "analyze", "message": "comparative_question"}

        return None  # Let LLM decide
```

### 2. Feedback Loop

Collect user feedback untuk improve tool selection.

```python
def ask_tool_feedback(tool_called: str, result: str) -> Optional[bool]:
    """Ask user if tool selection was correct"""
    print(f"\n[Feedback] Was '{tool_called}' the right tool for your question? (y/n/skip): ", end="")
    response = input().strip().lower()

    if response == 'y':
        return True
    elif response == 'n':
        print("What tool should have been used? ", end="")
        correct_tool = input().strip()
        return False, correct_tool
    else:
        return None
```

### 3. Fine-Tuning Dataset Generation

Generate training data untuk fine-tune LLM on tool selection.

```python
"""Generate fine-tuning dataset from successful interactions"""

def generate_finetuning_data():
    """Export successful tool calls as fine-tuning examples"""
    collector = get_metrics_collector()

    dataset = []

    # Read metrics
    with open(collector.output_path) as f:
        for line in f:
            data = json.loads(line)

            # Only include confirmed correct calls
            if data.get("was_correct_tool") is True:
                dataset.append({
                    "messages": [
                        {"role": "user", "content": data["user_query"]},
                        {
                            "role": "assistant",
                            "tool_calls": [{
                                "name": data["tool_called"],
                                "arguments": data["parameters"]
                            }]
                        }
                    ]
                })

    # Export for OpenAI fine-tuning format
    output_path = Path("data/finetuning/tool_selection.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for example in dataset:
            f.write(json.dumps(example) + "\n")

    print(f"Exported {len(dataset)} examples to {output_path}")
```

---

## 📝 Implementation Checklist

### Phase 1: Quick Wins (1-2 days)

- [ ] **1.1** Update REACT_SYSTEM_PROMPT dengan decision tree
- [ ] **1.2** Add "DO NOT USE WHEN" sections to tool descriptions
- [ ] **1.3** Add few-shot examples (5-10 examples)
- [ ] **1.4** Add input validation with helpful errors

### Phase 2: Metrics (2-3 days)

- [ ] **2.1** Create ToolMetricsCollector class
- [ ] **2.2** Integrate metrics logging in agent
- [ ] **2.3** Create evaluation script
- [ ] **2.4** Collect baseline data (50-100 queries)

### Phase 3: Optimization (1 week)

- [ ] **3.1** Analyze common mistakes from metrics
- [ ] **3.2** Update prompt based on findings
- [ ] **3.3** Add context-awareness checks
- [ ] **3.4** Implement tool pre-filter for obvious cases

### Phase 4: Advanced (2 weeks)

- [ ] **4.1** Add feedback collection mechanism
- [ ] **4.2** Generate fine-tuning dataset
- [ ] **4.3** A/B test different prompts
- [ ] **4.4** Consider fine-tuning GPT-4o-mini

---

## 🎯 Expected Improvements

### Before Optimization

```
Tool Selection Accuracy: ~70%

Common Mistakes:
- Using search_nearby for area names (20%)
- Calling tools for greetings (10%)
- Redundant searches for comparisons (15%)
- Wrong tool for number references (5%)
```

### After Optimization

```
Tool Selection Accuracy: ~90-95%

Remaining Issues:
- Edge cases with ambiguous landmarks/areas (5%)
- Novel query patterns not in examples (3%)
```

---

## 📚 Related Documentation

- [10-agents-and-tools-guide.md](./10-agents-and-tools-guide.md) - Full tools reference
- [09-improvement-roadmap.md](./09-improvement-roadmap.md) - Overall improvements

---

*Last updated: 2026-01-23*
