"""
Test ChromaDB Semantic Search Effectiveness

Compares:
1. ChromaDB semantic search (vector similarity)
2. API keyword search (traditional filter)

To see if semantic search finds relevant properties that keyword search misses.
"""
import sys
import os
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

import asyncio
from src.knowledge import PropertyStore
from src.adapters.metaproperty import MetaPropertyAPIAdapter

# Get API config from env
API_URL = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("METAPROPERTY_API_TOKEN", "")

# Test queries - semantic meaning vs exact keywords
TEST_QUERIES = [
    # Query yang pakai istilah umum/sinonim
    ("rumah taman luas", "Cari rumah dengan halaman/taman besar"),
    ("properti dekat kampus", "Cari properti dekat universitas/sekolah"),
    ("hunian nyaman keluarga", "Cari rumah family-friendly"),
    ("rumah modern minimalis", "Cari desain kontemporer"),
    ("investasi properti bagus", "Cari properti untuk investasi"),
]


async def test_api_search(adapter, query: str):
    """Search via API (keyword-based)"""
    from src.adapters.base import SearchCriteria
    
    criteria = SearchCriteria(
        query=query,
        limit=5
    )
    result = await adapter.search(criteria)
    return [p.title for p in result.properties]


def test_chromadb_search(store, query: str):
    """Search via ChromaDB (semantic)"""
    # Get IDs first
    property_ids = store.search(query, k=5)
    
    # Get titles from metadata
    results = store.vector_store.similarity_search(query, k=5)
    return [doc.metadata.get('title', 'N/A') for doc in results]


async def main():
    print("=" * 70)
    print("ChromaDB Semantic Search vs API Keyword Search")
    print("=" * 70)
    
    # Initialize
    store = PropertyStore()
    adapter = MetaPropertyAPIAdapter(
        api_url=API_URL,
        api_token=API_TOKEN
    )
    
    count = len(store.vector_store.get()['ids'])
    print(f"\nChromaDB contains: {count} properties\n")
    
    for query, description in TEST_QUERIES:
        print(f"\n{'='*70}")
        print(f"Query: \"{query}\"")
        print(f"Intent: {description}")
        print("-" * 70)
        
        # ChromaDB semantic search
        print("\n🔍 ChromaDB (Semantic):")
        chromadb_results = test_chromadb_search(store, query)
        for i, title in enumerate(chromadb_results, 1):
            print(f"   {i}. {title}")
        
        # API keyword search
        print("\n🔎 API (Keyword):")
        try:
            api_results = await test_api_search(adapter, query)
            if api_results:
                for i, title in enumerate(api_results, 1):
                    print(f"   {i}. {title}")
            else:
                print("   (No results)")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
    
    await adapter.close()
    
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    print("""
ChromaDB semantic search works by understanding MEANING, not just keywords.

✅ Advantages of ChromaDB:
   - "taman luas" can find properties with "garden", "halaman besar", "area hijau"
   - "dekat kampus" can find "area universitas", "USU", "UNIMED"
   - Finds synonyms and related concepts

❌ Limitations:
   - Requires embedding (costs tokens)
   - May find semantically similar but not exactly matching
   - Needs good property descriptions

Best Practice:
   Use ChromaDB for RE-RANKING API results, not replacing API search.
   1. API search with filters (price, bedrooms, location)
   2. ChromaDB re-ranks by semantic relevance to query
""")


if __name__ == "__main__":
    asyncio.run(main())
