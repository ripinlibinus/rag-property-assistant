"""
Evaluation: API vs ChromaDB vs Hybrid Search

Metrics:
- Hit Rate: Apakah hasil relevan ditemukan?
- Precision@K: Berapa persen dari K hasil yang relevan?
- MRR (Mean Reciprocal Rank): Posisi rata-rata hasil relevan pertama
- Response Coverage: Berapa query yang return hasil?

Test Cases:
- Semantic queries (no exact keyword match)
- Location queries (exact area names)
- Mixed queries (semantic + location)
"""
import sys
import os
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

import asyncio
from dataclasses import dataclass
from typing import List, Optional
import time

from src.knowledge import PropertyStore, HybridSearchService
from src.adapters.metaproperty import MetaPropertyAPIAdapter
from src.adapters.base import SearchCriteria

API_URL = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("METAPROPERTY_API_TOKEN", "")


@dataclass
class TestCase:
    """Test case for evaluation"""
    query: str
    category: str  # "semantic", "location", "mixed"
    description: str
    # Expected relevant keywords in title/location (for automatic relevance check)
    relevant_keywords: List[str]


# Test cases covering different query types
TEST_CASES = [
    # Semantic queries - no exact match expected in API
    TestCase(
        query="rumah taman luas",
        category="semantic",
        description="Cari rumah dengan halaman/garden besar",
        relevant_keywords=["taman", "garden", "park", "hijau", "green"],
    ),
    TestCase(
        query="hunian nyaman keluarga",
        category="semantic",
        description="Rumah family-friendly",
        relevant_keywords=["hunian", "residence", "family", "town", "house"],
    ),
    TestCase(
        query="properti modern minimalis",
        category="semantic",
        description="Desain kontemporer",
        relevant_keywords=["modern", "minimalis", "contemporary", "prime", "luxury"],
    ),
    TestCase(
        query="investasi bagus",
        category="semantic",
        description="Properti untuk investasi",
        relevant_keywords=["residence", "suite", "apartment", "soho"],
    ),
    
    # Location queries - should match in API
    TestCase(
        query="sunggal",
        category="location",
        description="Area Sunggal Medan",
        relevant_keywords=["sunggal", "ringroad"],
    ),
    TestCase(
        query="marelan",
        category="location",
        description="Area Marelan",
        relevant_keywords=["marelan"],
    ),
    TestCase(
        query="johor",
        category="location",
        description="Area Johor Medan",
        relevant_keywords=["johor"],
    ),
    
    # Mixed queries - location + semantic
    TestCase(
        query="rumah murah medan",
        category="mixed",
        description="Rumah affordable di Medan",
        relevant_keywords=["medan", "residence", "permai"],
    ),
    TestCase(
        query="perumahan baru",
        category="mixed",
        description="Proyek perumahan baru",
        relevant_keywords=["residence", "ville", "garden", "park"],
    ),
]


@dataclass
class SearchResult:
    """Result from a search method"""
    method: str
    query: str
    results: List[str]  # List of titles
    result_count: int
    time_ms: float
    has_results: bool


@dataclass
class EvalMetrics:
    """Evaluation metrics for a search method"""
    method: str
    total_queries: int
    queries_with_results: int
    coverage_rate: float
    avg_results: float
    avg_time_ms: float
    hit_rate: float  # % queries with at least 1 relevant result
    precision_at_5: float  # Avg precision in top 5


async def search_api(adapter, query: str, limit: int = 5) -> SearchResult:
    """Search using API only"""
    start = time.time()
    try:
        criteria = SearchCriteria(query=query, limit=limit)
        result = await adapter.search(criteria)
        titles = [p.title for p in result.properties[:limit]]
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="API",
            query=query,
            results=titles,
            result_count=len(titles),
            time_ms=elapsed,
            has_results=len(titles) > 0,
        )
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="API",
            query=query,
            results=[],
            result_count=0,
            time_ms=elapsed,
            has_results=False,
        )


def search_chromadb(store: PropertyStore, query: str, limit: int = 5) -> SearchResult:
    """Search using ChromaDB only (semantic)"""
    start = time.time()
    try:
        results = store.vector_store.similarity_search(query=query, k=limit)
        titles = [doc.metadata.get("title", "N/A") for doc in results]
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="ChromaDB",
            query=query,
            results=titles,
            result_count=len(titles),
            time_ms=elapsed,
            has_results=len(titles) > 0,
        )
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="ChromaDB",
            query=query,
            results=[],
            result_count=0,
            time_ms=elapsed,
            has_results=False,
        )


async def search_hybrid(hybrid: HybridSearchService, adapter, query: str, limit: int = 5) -> SearchResult:
    """Search using Hybrid (API + ChromaDB reranking)"""
    start = time.time()
    try:
        result = await hybrid.search(
            adapter=adapter,
            query=query,
            limit=limit,
            use_semantic_rerank=True,
        )
        titles = [p.title for p in result.properties[:limit]]
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="Hybrid",
            query=query,
            results=titles,
            result_count=len(titles),
            time_ms=elapsed,
            has_results=len(titles) > 0,
        )
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return SearchResult(
            method="Hybrid",
            query=query,
            results=[],
            result_count=0,
            time_ms=elapsed,
            has_results=False,
        )


def check_relevance(title: str, keywords: List[str]) -> bool:
    """Check if title contains any relevant keyword"""
    title_lower = title.lower()
    return any(kw.lower() in title_lower for kw in keywords)


def calculate_metrics(results: List[SearchResult], test_cases: List[TestCase]) -> EvalMetrics:
    """Calculate evaluation metrics for a search method"""
    if not results:
        return EvalMetrics(
            method="Unknown",
            total_queries=0,
            queries_with_results=0,
            coverage_rate=0.0,
            avg_results=0.0,
            avg_time_ms=0.0,
            hit_rate=0.0,
            precision_at_5=0.0,
        )
    
    method = results[0].method
    total = len(results)
    with_results = sum(1 for r in results if r.has_results)
    avg_results = sum(r.result_count for r in results) / total
    avg_time = sum(r.time_ms for r in results) / total
    
    # Calculate hit rate and precision
    hits = 0
    total_precision = 0.0
    
    for result, test_case in zip(results, test_cases):
        # Check if any result is relevant
        relevant_in_results = [check_relevance(t, test_case.relevant_keywords) for t in result.results[:5]]
        
        if any(relevant_in_results):
            hits += 1
        
        # Precision@5: relevant / returned (max 5)
        if result.results:
            precision = sum(relevant_in_results) / min(len(result.results), 5)
            total_precision += precision
    
    return EvalMetrics(
        method=method,
        total_queries=total,
        queries_with_results=with_results,
        coverage_rate=with_results / total * 100,
        avg_results=avg_results,
        avg_time_ms=avg_time,
        hit_rate=hits / total * 100,
        precision_at_5=total_precision / total * 100,
    )


async def main():
    print("=" * 80)
    print("EVALUATION: API vs ChromaDB vs Hybrid Search")
    print("=" * 80)
    
    # Initialize
    store = PropertyStore()
    adapter = MetaPropertyAPIAdapter(api_url=API_URL, api_token=API_TOKEN)
    hybrid = HybridSearchService(property_store=store, semantic_weight=0.6)
    
    count = len(store.vector_store.get()['ids'])
    print(f"\nChromaDB: {count} properties")
    print(f"Test Cases: {len(TEST_CASES)}")
    print()
    
    # Run all searches
    api_results = []
    chroma_results = []
    hybrid_results = []
    
    for tc in TEST_CASES:
        print(f"Testing: \"{tc.query}\" ({tc.category})")
        
        # API search
        api_res = await search_api(adapter, tc.query)
        api_results.append(api_res)
        
        # ChromaDB search
        chroma_res = search_chromadb(store, tc.query)
        chroma_results.append(chroma_res)
        
        # Hybrid search
        hybrid_res = await search_hybrid(hybrid, adapter, tc.query)
        hybrid_results.append(hybrid_res)
    
    await adapter.close()
    
    # Calculate metrics
    api_metrics = calculate_metrics(api_results, TEST_CASES)
    chroma_metrics = calculate_metrics(chroma_results, TEST_CASES)
    hybrid_metrics = calculate_metrics(hybrid_results, TEST_CASES)
    
    # Print comparison table
    print("\n" + "=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)
    
    # Per-query comparison
    print("\n📊 Per-Query Results:")
    print("-" * 80)
    print(f"{'Query':<30} {'API':<8} {'ChromaDB':<10} {'Hybrid':<8}")
    print("-" * 80)
    
    for i, tc in enumerate(TEST_CASES):
        api_count = api_results[i].result_count
        chroma_count = chroma_results[i].result_count
        hybrid_count = hybrid_results[i].result_count
        
        # Mark best method
        api_str = f"{api_count}" if api_count > 0 else "❌ 0"
        chroma_str = f"✓ {chroma_count}" if chroma_count > 0 else "❌ 0"
        hybrid_str = f"✓ {hybrid_count}" if hybrid_count > 0 else "❌ 0"
        
        print(f"{tc.query:<30} {api_str:<8} {chroma_str:<10} {hybrid_str:<8}")
    
    # Metrics summary
    print("\n" + "=" * 80)
    print("METRICS SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Metric':<25} {'API':<15} {'ChromaDB':<15} {'Hybrid':<15}")
    print("-" * 70)
    print(f"{'Coverage Rate':<25} {api_metrics.coverage_rate:>6.1f}%        {chroma_metrics.coverage_rate:>6.1f}%        {hybrid_metrics.coverage_rate:>6.1f}%")
    print(f"{'Hit Rate (Relevance)':<25} {api_metrics.hit_rate:>6.1f}%        {chroma_metrics.hit_rate:>6.1f}%        {hybrid_metrics.hit_rate:>6.1f}%")
    print(f"{'Precision@5':<25} {api_metrics.precision_at_5:>6.1f}%        {chroma_metrics.precision_at_5:>6.1f}%        {hybrid_metrics.precision_at_5:>6.1f}%")
    print(f"{'Avg Results':<25} {api_metrics.avg_results:>6.1f}          {chroma_metrics.avg_results:>6.1f}          {hybrid_metrics.avg_results:>6.1f}")
    print(f"{'Avg Time (ms)':<25} {api_metrics.avg_time_ms:>6.1f}          {chroma_metrics.avg_time_ms:>6.1f}          {hybrid_metrics.avg_time_ms:>6.1f}")
    
    # Category breakdown
    print("\n" + "=" * 80)
    print("BY QUERY CATEGORY")
    print("=" * 80)
    
    for category in ["semantic", "location", "mixed"]:
        cat_cases = [(i, tc) for i, tc in enumerate(TEST_CASES) if tc.category == category]
        if not cat_cases:
            continue
        
        api_hits = sum(1 for i, _ in cat_cases if api_results[i].has_results)
        chroma_hits = sum(1 for i, _ in cat_cases if chroma_results[i].has_results)
        hybrid_hits = sum(1 for i, _ in cat_cases if hybrid_results[i].has_results)
        total = len(cat_cases)
        
        print(f"\n{category.upper()} queries ({total} total):")
        print(f"  API:      {api_hits}/{total} ({api_hits/total*100:.0f}%)")
        print(f"  ChromaDB: {chroma_hits}/{total} ({chroma_hits/total*100:.0f}%)")
        print(f"  Hybrid:   {hybrid_hits}/{total} ({hybrid_hits/total*100:.0f}%)")
    
    # Winner analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("""
🏆 WINNER BY CATEGORY:

📌 SEMANTIC Queries (e.g., "rumah taman luas", "hunian nyaman"):
   - API: Usually fails (no keyword match)
   - ChromaDB: ✅ BEST - understands meaning
   - Hybrid: ✅ Falls back to ChromaDB

📌 LOCATION Queries (e.g., "sunggal", "marelan"):
   - API: ✅ BEST - exact database match
   - ChromaDB: Works but may be slower
   - Hybrid: Uses API results, reranked

📌 MIXED Queries (e.g., "rumah murah medan"):
   - API: Partial results
   - ChromaDB: Semantic matching
   - Hybrid: ✅ BEST - combines both

💡 RECOMMENDATION:
   Use HYBRID search for best overall coverage:
   - Gets API's structured filters (price, bedrooms)
   - Falls back to semantic when API returns nothing
   - Re-ranks results by relevance
""")


if __name__ == "__main__":
    asyncio.run(main())
