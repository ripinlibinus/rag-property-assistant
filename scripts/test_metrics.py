"""
Test Chat for Metrics Collection

Run a few test searches to generate metrics, then display the results.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os


async def run_test_searches():
    """Run test searches to generate metrics."""
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.knowledge import PropertyStore
    from src.knowledge.hybrid_search import HybridSearchService
    from src.utils.ab_testing import configure_ab_test, SearchMethod
    from src.utils.metrics import get_metrics_collector
    
    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")
    
    print("=" * 60)
    print("TEST CHAT FOR METRICS COLLECTION")
    print("=" * 60)
    
    # Initialize
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    
    # Try to load property store
    property_store = None
    chroma_path = project_root / "data" / "chromadb"
    if chroma_path.exists():
        try:
            property_store = PropertyStore(persist_dir=str(chroma_path / "properties"))
            print(f"[OK] ChromaDB loaded from {chroma_path}")
        except Exception as e:
            print(f"[WARN] ChromaDB not available: {e}")
    
    # Initialize hybrid search
    hybrid_service = HybridSearchService(
        property_store=property_store,
        semantic_weight=0.6,
    )
    
    # Configure A/B test for comparison
    print("\nConfiguring A/B test: comparison mode")
    configure_ab_test("comparison")
    
    # Test queries
    test_queries = [
        {"query": "rumah di cemara asri", "property_type": "house", "user_id": "test_user_1"},
        {"query": "ruko di sunggal", "property_type": "shophouse", "user_id": "test_user_2"},
        {"query": "rumah murah 3 kamar", "min_bedrooms": 3, "max_price": 1000000000, "user_id": "test_user_3"},
        {"query": "apartemen medan", "property_type": "apartment", "user_id": "test_user_1"},
        {"query": "tanah luas", "property_type": "land", "user_id": "test_user_2"},
    ]
    
    print(f"\nRunning {len(test_queries)} test searches...")
    print("-" * 60)
    
    results_summary = []
    
    for i, params in enumerate(test_queries, 1):
        query = params.pop("query")
        user_id = params.pop("user_id", "anonymous")
        
        print(f"\n[{i}] Query: \"{query}\"")
        print(f"    Params: {params}")
        print(f"    User: {user_id}")
        
        try:
            result = await hybrid_service.search(
                adapter=adapter,
                query=query,
                user_id=user_id,
                limit=5,
                **params,
            )
            
            print(f"    [OK] Found {len(result.properties)} properties (total: {result.total})")
            print(f"    [OK] Reranked: {result.reranked}")
            
            results_summary.append({
                "query": query,
                "results": len(result.properties),
                "total": result.total,
                "reranked": result.reranked,
            })
            
            # Show first result
            if result.properties:
                prop = result.properties[0]
                print(f"    -> Top result: {prop.title[:50]}... - Rp {prop.price:,.0f}")
                
        except Exception as e:
            print(f"    [ERR] Error: {e}")
            results_summary.append({
                "query": query,
                "error": str(e),
            })
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    return results_summary


def show_metrics():
    """Display collected metrics."""
    import json
    from datetime import datetime
    
    metrics_dir = project_root / "data" / "metrics"
    
    print("\n" + "=" * 60)
    print("COLLECTED METRICS")
    print("=" * 60)
    
    if not metrics_dir.exists():
        print("No metrics directory found.")
        return
    
    # Find today's metrics files
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Search metrics
    search_file = metrics_dir / f"search_{today}.jsonl"
    if search_file.exists():
        print(f"\n[STATS] Search Metrics ({search_file.name}):")
        print("-" * 50)
        
        with open(search_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        print(f"Total records: {len(lines)}")
        
        # Parse and summarize
        methods = {}
        latencies = []
        
        for line in lines:
            try:
                record = json.loads(line)
                method = record.get("method", "unknown")
                methods[method] = methods.get(method, 0) + 1
                if "total_latency_ms" in record:
                    latencies.append(record["total_latency_ms"])
            except:
                pass
        
        print(f"\nBy method:")
        for method, count in methods.items():
            print(f"  - {method}: {count} searches")
        
        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            print(f"\nLatency stats:")
            print(f"  - Average: {avg_latency:.2f} ms")
            print(f"  - Min: {min(latencies):.2f} ms")
            print(f"  - Max: {max(latencies):.2f} ms")
        
        # Show last 3 records
        print(f"\nLast 3 records:")
        for line in lines[-3:]:
            try:
                record = json.loads(line)
                print(f"  [{record.get('method')}] \"{record.get('query', '')[:30]}...\" "
                      f"-> {record.get('final_results_count', 0)} results "
                      f"({record.get('total_latency_ms', 0):.0f}ms)")
            except:
                pass
    else:
        print(f"\nNo search metrics file for today ({today})")
    
    # Tool metrics
    tool_file = metrics_dir / f"tool_{today}.jsonl"
    if tool_file.exists():
        print(f"\n[TOOLS] Tool Metrics ({tool_file.name}):")
        print("-" * 50)
        
        with open(tool_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        print(f"Total tool calls: {len(lines)}")
        
        # Count by tool
        tools = {}
        for line in lines:
            try:
                record = json.loads(line)
                tool = record.get("tool_name", "unknown")
                tools[tool] = tools.get(tool, 0) + 1
            except:
                pass
        
        for tool, count in tools.items():
            print(f"  - {tool}: {count} calls")
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("  1. python scripts/export_metrics.py    # Export to CSV")
    print("  2. python scripts/analyze_metrics.py   # Generate charts")
    print("=" * 60)


def main():
    print("\n[*] Starting test chat...")

    # Run searches
    results = asyncio.run(run_test_searches())

    # Show metrics
    show_metrics()


if __name__ == "__main__":
    main()
