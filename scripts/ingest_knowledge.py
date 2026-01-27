#!/usr/bin/env python
"""
Knowledge Base Ingestion Script

Ingests markdown files from data/knowledge-base into ChromaDB.
Run this when knowledge base files are added or updated.

Usage:
    python scripts/ingest_knowledge.py           # Ingest all
    python scripts/ingest_knowledge.py --stats   # Show stats only
    python scripts/ingest_knowledge.py --test    # Test search

Examples:
    # First time / after adding new files:
    python scripts/ingest_knowledge.py
    
    # Check what's in the database:
    python scripts/ingest_knowledge.py --stats
    
    # Test search:
    python scripts/ingest_knowledge.py --test "cara closing"
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.knowledge import KnowledgeStore


def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge base to ChromaDB")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    parser.add_argument("--test", type=str, help="Test search query")
    parser.add_argument("--category", type=str, help="Filter by category (sales, knowledge, motivation)")
    parser.add_argument("--docs-dir", type=str, default="data/knowledge-base", help="Knowledge base directory")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Knowledge Base Ingestion")
    print("=" * 60)
    
    # Initialize store
    store = KnowledgeStore()
    
    # Stats only mode
    if args.stats:
        stats = store.get_stats()
        print(f"\nTotal chunks: {stats['total_chunks']}")
        print(f"Persist directory: {stats['persist_dir']}")
        print("\nBy category:")
        for cat, count in stats.get("by_category", {}).items():
            print(f"  - {cat}: {count} chunks")
        return
    
    # Test search mode
    if args.test:
        print(f"\nSearching for: '{args.test}'")
        if args.category:
            print(f"Category filter: {args.category}")
        
        results = store.search(args.test, category=args.category, k=3)
        
        if not results:
            print("No results found.")
        else:
            print(f"\nFound {len(results)} results:\n")
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get("source", "Unknown")
                category = doc.metadata.get("category", "Unknown")
                content = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                print(f"{i}. [{category}] {source}")
                print(f"   {content}\n")
        return
    
    # Full ingestion mode
    docs_dir = args.docs_dir
    if not Path(docs_dir).exists():
        print(f"ERROR: Directory not found: {docs_dir}")
        sys.exit(1)
    
    print(f"\nIngesting from: {docs_dir}")
    
    # Show current stats
    try:
        current_stats = store.get_stats()
        print(f"Current chunks in DB: {current_stats['total_chunks']}")
    except Exception:
        print("No existing data (new database)")
    
    # Ingest
    print("\n" + "-" * 40)
    count = store.ingest_directory(docs_dir)
    print("-" * 40)
    
    # Show new stats
    new_stats = store.get_stats()
    print(f"\n✅ Ingestion complete!")
    print(f"Total chunks now: {new_stats['total_chunks']}")
    print("\nBy category:")
    for cat, cnt in new_stats.get("by_category", {}).items():
        print(f"  - {cat}: {cnt} chunks")
    
    print("\n" + "=" * 60)
    print("Test with: python scripts/ingest_knowledge.py --test 'your query'")
    print("=" * 60)


if __name__ == "__main__":
    main()
