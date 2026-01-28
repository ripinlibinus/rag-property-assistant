#!/usr/bin/env python
"""
ChromaDB Sync Scheduler

Periodically syncs properties from MetaProperty API to ChromaDB.
Designed to run as a Docker container alongside the main API.

Environment Variables:
    - SYNC_INTERVAL_MINUTES: Interval between syncs (default: 60)
    - SYNC_LIMIT: Max properties per sync (default: 200)
    - METAPROPERTY_API_URL: MetaProperty API base URL
    - METAPROPERTY_API_TOKEN: API token for authentication
    - CHROMA_PERSIST_DIRECTORY: ChromaDB storage path

Usage:
    python scripts/scheduler.py

    # Or with custom settings:
    SYNC_INTERVAL_MINUTES=30 SYNC_LIMIT=100 python scripts/scheduler.py
"""

import os
import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def get_logger():
    """Simple logger for scheduler"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('scheduler')


logger = get_logger()


async def run_sync(limit: int = 200) -> dict:
    """
    Run a single sync cycle.

    Returns:
        dict with sync results: synced, total, errors
    """
    from src.knowledge.property_store import create_property_store
    from src.adapters.metaproperty import MetaPropertyAPIAdapter

    api_url = os.getenv("METAPROPERTY_API_URL")
    api_token = os.getenv("METAPROPERTY_API_TOKEN")

    if not api_url:
        logger.error("METAPROPERTY_API_URL not set")
        return {"synced": 0, "total": 0, "errors": ["METAPROPERTY_API_URL not set"]}

    store = create_property_store()
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)

    result = {
        "synced": 0,
        "total": 0,
        "errors": [],
        "skipped": 0,
    }

    try:
        # Get pending properties from MetaProperty API
        logger.info(f"Fetching pending properties (limit={limit})...")
        pending = await adapter.get_pending_ingest(limit=limit)

        if not pending:
            logger.info("No pending properties to sync")
            stats = store.get_stats()
            result["total"] = stats["total_properties"]
            return result

        logger.info(f"Found {len(pending)} properties to sync")

        # Ingest to ChromaDB
        ingested_items = []
        for prop in pending:
            prop_id = prop.get("id", "unknown")
            prop_source = prop.get("source", "listing")

            try:
                store.upsert_property(prop)
                ingested_items.append({
                    "source": prop_source,
                    "id": prop_id
                })
                result["synced"] += 1
            except Exception as e:
                error_msg = f"{prop_source}/{prop_id}: {str(e)}"
                logger.error(f"Failed to ingest: {error_msg}")
                result["errors"].append(error_msg)

        # Mark as ingested in MetaProperty
        if ingested_items:
            try:
                await adapter.mark_ingested(ingested_items)
                logger.info(f"Marked {len(ingested_items)} properties as ingested")
            except Exception as e:
                logger.error(f"Failed to mark ingested: {e}")
                result["errors"].append(f"mark_ingested: {str(e)}")

        # Get final stats
        stats = store.get_stats()
        result["total"] = stats["total_properties"]

        logger.info(f"Sync complete: {result['synced']} synced, {len(result['errors'])} errors, total: {result['total']}")

        return result

    except Exception as e:
        logger.error(f"Sync failed: {e}")
        result["errors"].append(str(e))
        return result

    finally:
        await adapter.close()


async def run_cleanup() -> dict:
    """
    Remove deleted properties from ChromaDB.

    Returns:
        dict with cleanup results
    """
    from src.knowledge.property_store import create_property_store
    from src.adapters.metaproperty import MetaPropertyAPIAdapter

    api_url = os.getenv("METAPROPERTY_API_URL")
    api_token = os.getenv("METAPROPERTY_API_TOKEN")

    if not api_url:
        return {"deleted": 0, "errors": ["METAPROPERTY_API_URL not set"]}

    store = create_property_store()
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)

    result = {"deleted": 0, "errors": []}

    try:
        # Get deleted properties from API
        response = await adapter._get_client()
        resp = await response.get("/api/v1/sync/deleted")

        if resp.status_code == 200:
            data = resp.json()
            deleted_items = data.get("deleted", [])

            for item in deleted_items:
                try:
                    prop_id = str(item.get("id"))
                    store.delete_property(prop_id)
                    result["deleted"] += 1
                except Exception as e:
                    result["errors"].append(f"delete {item}: {e}")

            if result["deleted"] > 0:
                logger.info(f"Cleaned up {result['deleted']} deleted properties")

    except Exception as e:
        logger.warning(f"Cleanup skipped: {e}")

    finally:
        await adapter.close()

    return result


def main():
    """Main scheduler loop"""
    interval_minutes = int(os.getenv("SYNC_INTERVAL_MINUTES", "60"))
    limit = int(os.getenv("SYNC_LIMIT", "200"))
    interval_seconds = interval_minutes * 60

    logger.info("=" * 60)
    logger.info("ChromaDB Sync Scheduler Started")
    logger.info(f"  Interval: {interval_minutes} minutes")
    logger.info(f"  Limit per sync: {limit}")
    logger.info(f"  MetaProperty API: {os.getenv('METAPROPERTY_API_URL', 'NOT SET')}")
    logger.info("=" * 60)

    # Run initial sync on startup
    logger.info("Running initial sync...")
    try:
        result = asyncio.run(run_sync(limit=limit))
        logger.info(f"Initial sync complete: {result['synced']} properties synced")
    except Exception as e:
        logger.error(f"Initial sync failed: {e}")

    # Main loop
    while True:
        logger.info(f"Next sync in {interval_minutes} minutes...")
        time.sleep(interval_seconds)

        try:
            # Run sync
            result = asyncio.run(run_sync(limit=limit))

            # Run cleanup (remove deleted properties)
            cleanup = asyncio.run(run_cleanup())

            logger.info(
                f"Cycle complete: synced={result['synced']}, "
                f"deleted={cleanup['deleted']}, "
                f"total={result['total']}"
            )

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Sync cycle error: {e}")
            # Continue running, don't crash on errors


if __name__ == "__main__":
    main()
