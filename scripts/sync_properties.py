#!/usr/bin/env python
"""
Property Sync Script

Syncs properties from MetaProperty API to ChromaDB.
Uses flag-based incremental sync (need_ingest column).

Usage:
    python scripts/sync_properties.py           # Sync pending only
    python scripts/sync_properties.py --full    # Force full re-sync
    python scripts/sync_properties.py --stats   # Show stats only
    python scripts/sync_properties.py --test "taman luas"  # Test search

Note:
    Requires MetaProperty API to have sync endpoints:
    - GET /api/v1/sync/pending-ingest
    - POST /api/v1/sync/mark-ingested
    - POST /api/v1/sync/reset-ingest (for --full)
    
    See: metaproperty2026/docs/outstanding-session/chromadb-sync-api.md
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.knowledge import PropertyStore
from src.adapters.metaproperty import MetaPropertyAPIAdapter


async def sync_pending(adapter: MetaPropertyAPIAdapter, store: PropertyStore, limit: int = 100) -> int:
    """
    Sync only listings with need_ingest=true.
    
    Args:
        limit: Maximum number of properties to sync
    
    Returns:
        Number of properties synced
    """
    print(f"Fetching pending properties from API (limit: {limit})...")
    
    try:
        pending = await adapter.get_pending_ingest(limit=limit)
    except Exception as e:
        print(f"ERROR: Could not fetch pending properties: {e}")
        print("\nMake sure MetaProperty API has sync endpoints implemented.")
        print("See: metaproperty2026/docs/outstanding-session/chromadb-sync-api.md")
        return 0
    
    if not pending:
        print("No pending properties to sync.")
        return 0
    
    print(f"Found {len(pending)} properties to sync...")
    
    # Ingest to ChromaDB
    ingested_items = []  # Store source+id for mark_ingested
    for prop in pending:
        try:
            store.upsert_property(prop)
            # Store both source and id for marking as ingested
            ingested_items.append({
                "source": prop.get("source", "listing"),
                "id": prop["id"]
            })
            print(f"  [OK] Synced: {prop.get('title', prop.get('name', prop['id']))[:50]}")
        except Exception as e:
            print(f"  [ERR] Error syncing {prop['id']}: {e}")
    
    # Mark as ingested in API
    if ingested_items:
        try:
            await adapter.mark_ingested(ingested_items)
            print(f"\n[DONE] Marked {len(ingested_items)} properties as ingested in API")
        except Exception as e:
            print(f"\n[WARN] Could not mark as ingested: {e}")
    
    return len(ingested_items)


async def full_resync(adapter: MetaPropertyAPIAdapter, store: PropertyStore, limit: int = 100) -> int:
    """
    Force full re-sync by resetting all ingest flags.
    
    Args:
        adapter: API adapter
        store: Property store
        limit: Maximum properties to sync (default 100 for dev)
    
    Returns:
        Number of properties synced
    """
    print("Resetting ingest flags in API...")
    
    try:
        await adapter.reset_ingest_flags()
        print("[OK] All listings marked for re-ingest")
    except Exception as e:
        print(f"ERROR: Could not reset flags: {e}")
        return 0
    
    # Clear ChromaDB
    print("Clearing existing ChromaDB data...")
    store.clear()
    
    # Now sync with limit
    count = await sync_pending(adapter, store, limit=limit)
    print(f"Synced {count} properties (limit: {limit})")
    
    return count


async def main():
    parser = argparse.ArgumentParser(description="Sync properties to ChromaDB")
    parser.add_argument("--full", action="store_true", help="Force full re-sync")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    parser.add_argument("--test", type=str, help="Test semantic search")
    parser.add_argument("--limit", type=int, default=100, help="Max properties to sync (default: 100)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Property Sync to ChromaDB")
    print("=" * 60)
    
    # Initialize
    store = PropertyStore()
    
    # Stats only
    if args.stats:
        stats = store.get_stats()
        print(f"\nTotal properties in ChromaDB: {stats['total_properties']}")
        print(f"Persist directory: {stats['persist_dir']}")
        return
    
    # Test search
    if args.test:
        print(f"\nSemantic search for: '{args.test}'")
        results = store.search_with_scores(args.test, k=5)
        
        if not results:
            print("No results found.")
        else:
            print(f"\nFound {len(results)} results:\n")
            for property_id, score in results:
                print(f"  - ID: {property_id}, Score: {score:.4f}")
        return
    
    # Sync mode
    api_url = os.getenv("METAPROPERTY_API_URL")
    api_token = os.getenv("METAPROPERTY_API_TOKEN")
    
    if not api_url:
        print("ERROR: METAPROPERTY_API_URL not set in .env")
        sys.exit(1)
    
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    
    try:
        if args.full:
            print(f"\n[FULL] Starting FULL re-sync (limit: {args.limit})...")
            count = await full_resync(adapter, store, limit=args.limit)
        else:
            print(f"\n[SYNC] Syncing pending listings (limit: {args.limit})...")
            count = await sync_pending(adapter, store, limit=args.limit)
        
        print(f"\n{'=' * 60}")
        print(f"Sync complete: {count} properties processed")
        
        stats = store.get_stats()
        print(f"Total in ChromaDB: {stats['total_properties']}")
        print("=" * 60)
        
    finally:
        await adapter.close()


if __name__ == "__main__":
    asyncio.run(main())
