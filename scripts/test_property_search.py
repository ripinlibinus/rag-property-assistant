"""Quick test for property semantic search."""
import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv()

from src.knowledge import PropertyStore

store = PropertyStore()

# Get count from collection
count = len(store.vector_store.get()['ids'])
print(f"ChromaDB Properties: {count} items\n")

# Test search - returns property IDs
query = "rumah taman luas"
print(f"Test Search: '{query}'")
print("-" * 50)

property_ids = store.search(query, k=5)
print(f"Property IDs found: {property_ids}")

# Test search with scores
print(f"\nTest Search with scores:")
print("-" * 50)
results_with_scores = store.search_with_scores(query, k=5)
for prop_id, score in results_with_scores:
    print(f"  ID: {prop_id}, Score: {score:.4f}")
