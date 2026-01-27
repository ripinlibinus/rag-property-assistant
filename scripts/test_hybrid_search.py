"""
Test Hybrid Search - API + ChromaDB Semantic Re-ranking

Shows how hybrid search re-ranks API results using semantic relevance.
"""
import sys
import os
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.knowledge import PropertyStore, HybridSearchService
from src.adapters.metaproperty import MetaPropertyAPIAdapter

API_URL = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("METAPROPERTY_API_TOKEN", "")

# Test queries with semantic meaning
TEST_QUERIES = [
    "rumah taman luas",
    "hunian nyaman keluarga", 
    "properti modern minimalis",
    "rumah dekat sekolah",
]


async def main():
    print("=" * 70)
    print("Hybrid Search Test: API Filter + ChromaDB Re-ranking")
    print("=" * 70)
    
    # Initialize
    store = PropertyStore()
    adapter = MetaPropertyAPIAdapter(api_url=API_URL, api_token=API_TOKEN)
    
    hybrid = HybridSearchService(
        property_store=store,
        semantic_weight=0.6,  # 60% semantic, 40% API order
    )
    
    count = len(store.vector_store.get()['ids'])
    print(f"\nChromaDB contains: {count} properties")
    print(f"Semantic weight: 60% (semantic) vs 40% (API order)\n")
    
    for query in TEST_QUERIES:
        print(f"\n{'='*70}")
        print(f"Query: \"{query}\"")
        print("-" * 70)
        
        # Hybrid search
        result = await hybrid.search(
            adapter=adapter,
            query=query,
            limit=5,
            use_semantic_rerank=True,
        )
        
        print(f"\n📊 API found: {result.api_count} | Reranked: {result.reranked}")
        print(f"\n🔀 Hybrid Results (re-ranked by semantic relevance):")
        
        for i, prop in enumerate(result.properties, 1):
            score = result.semantic_scores.get(str(prop.id), 0)
            score_bar = "█" * int(score * 20) if score > 0 else "░"
            print(f"   {i}. {prop.title[:40]:<40} [score: {score:.3f}] {score_bar}")
        
        if not result.properties:
            print("   (No results)")
    
    await adapter.close()
    
    print("\n" + "=" * 70)
    print("HOW HYBRID SEARCH WORKS")
    print("=" * 70)
    print("""
1. API Search: Fetches properties matching location/filters
2. ChromaDB: Gets semantic similarity scores for each property
3. Combine Scores:
   - API position score (earlier = higher)
   - Semantic score (from vector similarity)
   - Combined = 0.6 * semantic + 0.4 * API
4. Re-rank: Sort by combined score

Benefits:
✅ Filters work (price, bedrooms, location from API)
✅ Semantic concepts understood ("taman luas" → finds gardens)
✅ Results sorted by RELEVANCE, not just database order
""")


if __name__ == "__main__":
    asyncio.run(main())
