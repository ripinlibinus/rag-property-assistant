#!/usr/bin/env python
"""
Multi-Model Embedding Comparison Script

Compares retrieval quality across different embedding models.
Creates separate ChromaDB stores for each model.

Usage:
    python scripts/compare_models.py --sync          # Sync all models
    python scripts/compare_models.py --test          # Run comparison tests
    python scripts/compare_models.py --sync --test   # Both
    python scripts/compare_models.py --stats         # Show model stats

Models compared:
    - text-embedding-3-small (default, fastest)
    - text-embedding-3-large (better quality)
"""

import asyncio
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os

from src.knowledge.property_store import PropertyStore, EMBEDDING_MODELS, create_property_store
from src.adapters.metaproperty import MetaPropertyAPIAdapter


# Test queries for comparison
TEST_QUERIES = [
    # Location-based queries
    {"query": "rumah di cemara asri", "type": "location"},
    {"query": "ruko sunggal", "type": "location"},
    {"query": "apartemen medan kota", "type": "location"},

    # Feature-based queries
    {"query": "rumah dengan kolam renang", "type": "feature"},
    {"query": "rumah full furnished", "type": "feature"},
    {"query": "properti security 24 jam", "type": "feature"},

    # Specification queries
    {"query": "rumah 3 kamar tidur", "type": "spec"},
    {"query": "tanah luas 500 meter", "type": "spec"},
    {"query": "ruko 3 lantai", "type": "spec"},

    # Intent queries
    {"query": "rumah murah dijual", "type": "intent"},
    {"query": "properti disewakan", "type": "intent"},
    {"query": "proyek baru developer", "type": "intent"},

    # Combined queries
    {"query": "rumah 3 kamar di cemara asri dengan kolam renang", "type": "combined"},
    {"query": "apartemen furnished dekat USU", "type": "combined"},
    {"query": "ruko dijual di sunggal security 24 jam", "type": "combined"},
]


def get_model_store(model: str, base_dir: str = "data/chromadb/properties") -> PropertyStore:
    """Create PropertyStore for a specific model."""
    return create_property_store(
        persist_dir=base_dir,
        embedding_model=model,
        use_model_suffix=True,
    )


async def sync_model(
    model: str,
    adapter: MetaPropertyAPIAdapter,
    limit: int = 500,
) -> Dict[str, Any]:
    """Sync properties for a specific model."""
    print(f"\n{'='*60}")
    print(f"Syncing: {model}")
    print(f"{'='*60}")

    store = get_model_store(model)
    stats_before = store.get_stats()

    print(f"Directory: {store.persist_dir}")
    print(f"Current count: {stats_before['total_properties']}")

    # Get pending properties
    try:
        pending = await adapter.get_pending_ingest(limit=limit)
    except Exception as e:
        print(f"Error fetching pending: {e}")
        return {"model": model, "error": str(e)}

    if not pending:
        print("No pending properties")
        return {
            "model": model,
            "synced": 0,
            "total": stats_before["total_properties"],
        }

    print(f"Found {len(pending)} properties to sync...")

    # Ingest
    synced = 0
    for prop in pending:
        try:
            store.upsert_property(prop)
            synced += 1
            if synced % 50 == 0:
                print(f"  Progress: {synced}/{len(pending)}")
        except Exception as e:
            print(f"  Error: {prop.get('id')} - {e}")

    stats_after = store.get_stats()

    return {
        "model": model,
        "synced": synced,
        "total": stats_after["total_properties"],
        "persist_dir": stats_after["persist_dir"],
    }


def compare_search_results(
    query: str,
    models: List[str],
    k: int = 10,
) -> Dict[str, Any]:
    """Compare search results across models."""
    results = {}

    for model in models:
        store = get_model_store(model)
        try:
            search_results = store.search_with_scores(query, k=k)
            results[model] = {
                "property_ids": [pid for pid, _ in search_results],
                "scores": [score for _, score in search_results],
                "count": len(search_results),
            }
        except Exception as e:
            results[model] = {"error": str(e)}

    return results


def calculate_overlap(results_a: List[str], results_b: List[str]) -> Dict[str, float]:
    """Calculate overlap between two result sets."""
    set_a = set(results_a)
    set_b = set(results_b)

    intersection = set_a & set_b
    union = set_a | set_b

    return {
        "intersection": len(intersection),
        "jaccard": len(intersection) / len(union) if union else 0,
        "overlap_in_a": len(intersection) / len(set_a) if set_a else 0,
        "overlap_in_b": len(intersection) / len(set_b) if set_b else 0,
    }


def run_comparison_tests(models: List[str]) -> List[Dict[str, Any]]:
    """Run comparison tests across models."""
    print("\n" + "="*60)
    print("MULTI-MODEL COMPARISON TEST")
    print("="*60)
    print(f"Models: {', '.join(models)}")
    print(f"Queries: {len(TEST_QUERIES)}")
    print("-"*60)

    all_results = []

    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        query_type = test["type"]

        print(f"\n[{i}] Query: \"{query}\" (type: {query_type})")

        results = compare_search_results(query, models, k=10)

        comparison = {
            "query": query,
            "type": query_type,
            "results": results,
        }

        # Calculate overlaps between models
        if len(models) >= 2:
            model_a, model_b = models[0], models[1]
            if "property_ids" in results.get(model_a, {}) and "property_ids" in results.get(model_b, {}):
                overlap = calculate_overlap(
                    results[model_a]["property_ids"],
                    results[model_b]["property_ids"],
                )
                comparison["overlap"] = overlap
                print(f"    Overlap: {overlap['intersection']}/10 "
                      f"(Jaccard: {overlap['jaccard']:.2f})")

        for model in models:
            if "count" in results.get(model, {}):
                print(f"    {model}: {results[model]['count']} results")
            elif "error" in results.get(model, {}):
                print(f"    {model}: ERROR - {results[model]['error']}")

        all_results.append(comparison)

    return all_results


def show_stats(models: List[str]):
    """Show statistics for all model stores."""
    print("\n" + "="*60)
    print("MODEL STATISTICS")
    print("="*60)

    for model in models:
        store = get_model_store(model)
        try:
            stats = store.get_stats()
            print(f"\n{model}:")
            print(f"  Directory: {stats['persist_dir']}")
            print(f"  Documents: {stats['total_properties']}")
        except Exception as e:
            print(f"\n{model}: ERROR - {e}")


def save_results(results: List[Dict], filename: str = None):
    """Save comparison results to JSON."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"model_comparison_{timestamp}.json"

    output_dir = project_root / "data" / "metrics"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "models": EMBEDDING_MODELS[:2],  # Compare top 2 models
            "queries": len(results),
            "results": results,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_path}")
    return output_path


async def main():
    parser = argparse.ArgumentParser(description="Multi-model embedding comparison")
    parser.add_argument("--sync", action="store_true", help="Sync properties for all models")
    parser.add_argument("--test", action="store_true", help="Run comparison tests")
    parser.add_argument("--stats", action="store_true", help="Show model statistics")
    parser.add_argument("--limit", type=int, default=500, help="Sync limit per batch")
    parser.add_argument("--models", type=str, default="small,large",
                        help="Models to compare (small,large or small,large,ada)")
    args = parser.parse_args()

    # Parse models
    model_map = {
        "small": "text-embedding-3-small",
        "large": "text-embedding-3-large",
        "ada": "text-embedding-ada-002",
    }
    model_names = [m.strip() for m in args.models.split(",")]
    models = [model_map.get(m, m) for m in model_names]

    print("="*60)
    print("MULTI-MODEL EMBEDDING COMPARISON")
    print("="*60)
    print(f"Models: {models}")

    # Stats
    if args.stats:
        show_stats(models)
        return

    # Sync
    if args.sync:
        api_url = os.getenv("METAPROPERTY_API_URL")
        api_token = os.getenv("METAPROPERTY_API_TOKEN")

        if not api_url:
            print("ERROR: METAPROPERTY_API_URL not set")
            return

        adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)

        try:
            for model in models:
                result = await sync_model(model, adapter, limit=args.limit)
                print(f"Result: {result}")
        finally:
            await adapter.close()

    # Test
    if args.test:
        results = run_comparison_tests(models)

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)

        total_overlap = 0
        count = 0
        for r in results:
            if "overlap" in r:
                total_overlap += r["overlap"]["jaccard"]
                count += 1

        if count > 0:
            avg_overlap = total_overlap / count
            print(f"Average Jaccard overlap: {avg_overlap:.2f}")
            print(f"(Higher = more similar results between models)")

        # Save results
        save_results(results)

    if not args.sync and not args.test and not args.stats:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
