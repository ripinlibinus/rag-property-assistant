"""Debug ChromaDB metadata and API fetch"""
import sys
import os
import asyncio
sys.path.insert(0, ".")
from dotenv import load_dotenv
load_dotenv()

from src.knowledge import PropertyStore
from src.adapters.metaproperty import MetaPropertyAPIAdapter

API_URL = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
API_TOKEN = os.getenv("METAPROPERTY_API_TOKEN", "")

async def main():
    store = PropertyStore()
    adapter = MetaPropertyAPIAdapter(api_url=API_URL, api_token=API_TOKEN)
    
    print("1. Checking ChromaDB metadata...")
    results = store.vector_store.similarity_search_with_score("rumah taman luas", k=3)
    
    for doc, score in results:
        prop_id = doc.metadata.get("property_id")
        title = doc.metadata.get("title")
        print(f"\n  ChromaDB: ID={prop_id}, Title={title}, Score={score:.3f}")
        
        # Try to fetch from API
        print(f"  Fetching from API...")
        try:
            prop = await adapter.get_by_id(prop_id)
            if prop:
                print(f"  ✅ API returned: {prop.title}")
            else:
                print(f"  ❌ API returned None")
        except Exception as e:
            print(f"  ❌ API error: {e}")
    
    await adapter.close()

asyncio.run(main())
