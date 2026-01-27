"""
Chat with ChromaDB Only - Testing semantic search without API

Usage:
    python scripts/chat_chromadb_only.py

This script tests ChromaDB semantic search directly without going through the API.
Useful for understanding what ChromaDB can and cannot find.
"""

import os
import sys

# Disable ChromaDB telemetry BEFORE any imports
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import logging
from pathlib import Path

# Suppress noisy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("chromadb.telemetry").setLevel(logging.ERROR)
logging.getLogger("chromadb.config").setLevel(logging.ERROR)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Constants - must match property_store.py
PERSIST_DIR = str(project_root / "data" / "chromadb" / "properties")
COLLECTION_NAME = "properties"
EMBEDDING_MODEL = "text-embedding-3-small"


def load_chromadb():
    """Load ChromaDB property store with correct settings"""
    print("Loading ChromaDB...")
    print(f"  Directory: {PERSIST_DIR}")
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Embedding: {EMBEDDING_MODEL}")

    store = Chroma(
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(model=EMBEDDING_MODEL)
    )
    count = len(store.get()['ids'])
    print(f"Loaded {count} properties from ChromaDB\n")
    return store


def search_chromadb(store, query: str, k: int = 5, property_type: str = None):
    """Search ChromaDB with optional property_type filter"""

    # Build filter if property_type specified
    filter_dict = None
    if property_type:
        filter_dict = {"property_type": property_type}

    # Search with relevance scores
    results = store.similarity_search_with_relevance_scores(
        query,
        k=k,
        filter=filter_dict
    )

    return results


def format_results(results):
    """Format search results for display"""
    if not results:
        return "No results found."

    output = []
    for i, (doc, score) in enumerate(results, 1):
        meta = doc.metadata
        output.append(f"\n{i}. [{score:.4f}] {meta.get('title', 'N/A')}")
        output.append(f"   Type: {meta.get('property_type', 'N/A')} | City: {meta.get('city', 'N/A')}")

        price = meta.get('price', 0)
        if price:
            output.append(f"   Price: Rp {int(price):,}")

        # Show bedrooms/floors if available
        bedrooms = meta.get('bedrooms', 0)
        floors = meta.get('floors', 0)
        if bedrooms or floors:
            specs = []
            if bedrooms:
                specs.append(f"{int(bedrooms)} BR")
            if floors:
                specs.append(f"{int(floors)} lantai")
            output.append(f"   Specs: {', '.join(specs)}")

        # Show content preview
        content = doc.page_content[:150].replace('\n', ' ')
        output.append(f"   Content: {content}...")

    return "\n".join(output)


def main():
    print("=" * 60)
    print("ChromaDB-Only Chat - Semantic Search Testing")
    print("=" * 60)
    print("\nCommands:")
    print("  /type <property_type> - Set filter (house/apartment/warehouse/etc)")
    print("  /clear - Clear property_type filter")
    print("  /count - Show total documents in ChromaDB")
    print("  /stats - Show collection statistics")
    print("  /quit - Exit")
    print("-" * 60)

    store = load_chromadb()
    property_type_filter = None

    while True:
        try:
            # Show current filter
            filter_info = f" [filter: {property_type_filter}]" if property_type_filter else ""
            query = input(f"\nYou{filter_info}: ").strip()

            if not query:
                continue

            # Handle commands
            if query.lower() == "/quit":
                print("Goodbye!")
                break

            if query.lower() == "/clear":
                property_type_filter = None
                print("Filter cleared.")
                continue

            if query.lower() == "/count":
                count = len(store.get()['ids'])
                print(f"ChromaDB contains {count} documents.")
                continue

            if query.lower() == "/stats":
                collection = store._collection
                print(f"Collection: {COLLECTION_NAME}")
                print(f"Documents: {collection.count()}")
                print(f"Embedding: {EMBEDDING_MODEL}")
                print(f"Directory: {PERSIST_DIR}")
                continue

            if query.lower().startswith("/type "):
                property_type_filter = query[6:].strip()
                print(f"Filter set to: {property_type_filter}")
                continue

            # Perform search
            print(f"\nSearching ChromaDB for: '{query}'")
            if property_type_filter:
                print(f"With filter: property_type={property_type_filter}")

            results = search_chromadb(
                store,
                query,
                k=5,
                property_type=property_type_filter
            )

            print(format_results(results))

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
