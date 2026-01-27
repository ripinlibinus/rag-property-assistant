"""
Sequential Chat Test with Questions from test_question.py

Runs questions in order (some have connected context) and generates metrics.
Exports results to CSV for manual evaluation per docs/12-evaluation-methodology.md

Usage:
    python scripts/test_sequential_chat.py              # Run test
    python scripts/test_sequential_chat.py --export     # Export to CSV for rating
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os

# Question categories for analysis
QUESTION_CATEGORIES = {
    1: "location_simple",
    2: "location_simple",
    3: "location_simple",
    4: "location_price",
    5: "location_price_spec",
    6: "location_price_spec",
    7: "location_price",
    8: "location_intent",
    9: "location_price",
    10: "property_type",
    11: "property_type",
    12: "property_type",
    13: "location_price_spec",
    14: "context_followup",
    15: "context_followup",
    16: "context_modify",
    17: "context_followup",
    18: "context_modify",
    19: "feature_search",
    20: "feature_search",
    21: "feature_search",
    22: "feature_search",
    23: "feature_search",
    24: "nearby_search",
    25: "nearby_search",
    26: "nearby_price",
    27: "complex_query",
    28: "complex_query",
    29: "project_search",
    30: "project_search",
}

# Questions from old-version test_question.py (only q values)
QUESTIONS = [
    "Carikan rumah dijual di daerah cemara",
    "Carikan rumah dijual di daerah ringroad",
    "Carikan rumah sewa di medan",
    "Carikan rumah dijual di daerah cemara harga 1M an",
    "Carikan rumah dijual daerah ringroad harga dibawah 800juta 3 kamar",
    "apakah ada rumah sewa di medan yang dibawah 50juta 3 kamar?",
    "Saya ingin beli rumah di dekat podomoro medan harga dibawah 1M ada?",
    "Client saya lagi cari sewa dekat usu, anaknya mau kuliah disana",
    "Carikan rumah di inti kota medan yang harganya dibawah 1M",
    "apakah ada ruko yang disewakan di daerah krakatau?",
    "saya lagi cari tanah yang dijual di marelan",
    "apakah ada gudang yang dijual atau disewa di KIM ?",
    "Carikan rumah dijual daerah ringroad harga 1M an 3 kamar",
    "Apakah masih ada pilihan lain?",  # Context: continues from previous
    "Berikan lagi pilihan lain",  # Context: continues
    "kasih pilihan lain, lokasi dan harga masih sama, tapi yang 3 lantai?",  # Context
    "Berikan lagi pilihan lain",  # Context
    "Kalau pilihan lain, lokasi dan jumlah lantai masih sama, tapi yang dibawah 800 juta ada?",  # Context
    "carikan rumah dengan fasilitas cctv di medan",
    "carikan rumah dengan fasilitas wifi di medan",
    "cari rumah dalam komplek dengan fasilitas lapangan basket",
    "cari rumah yang bisa parkir beberapa mobil",
    "cari rumah yang sudah ada ac, lemari, dapur dan tangki air",
    "cari rumah dekat mall",
    "cari rumah dekat sekolah di medan",
    "cari rumah dekat mall yang harganya dibawah 800 juta",
    "cari rumah full furnished yang harganya dibawah 1 M dalam komplek dengan fasilitas lapangan basket",
    "cari apartment di podomoro yang bisa harganya dibawah 1.5 M",
    "cari rumah di citraland bagya city medan",
    "cari rumah dijual di komplek givency one",
]


def count_results_from_response(response: str) -> int:
    """
    Extract results count from agent response.

    Looks for patterns like:
    - "Ditemukan 5 properti"
    - "5 hasil ditemukan"
    - Numbered list (1., 2., 3., etc.)
    """
    # Pattern: "Ditemukan X properti" or "X hasil"
    patterns = [
        r"[Dd]itemukan\s+(\d+)\s+(?:properti|hasil|rumah|ruko|tanah)",
        r"(\d+)\s+(?:properti|hasil|rumah|ruko|tanah)\s+ditemukan",
        r"[Mm]enampilkan\s+(\d+)\s+(?:properti|hasil)",
        r"[Aa]da\s+(\d+)\s+(?:properti|hasil|pilihan)",
    ]

    for pattern in patterns:
        match = re.search(pattern, response)
        if match:
            return int(match.group(1))

    # Count numbered list items (1., 2., 3., etc. or **1.**, **2.**)
    numbered_items = re.findall(r"(?:^|\n)\s*(?:\*\*)?(\d+)\.", response)
    if numbered_items:
        return len(numbered_items)

    # If response mentions "tidak ada" or "tidak ditemukan"
    if re.search(r"tidak\s+(?:ada|ditemukan|menemukan)", response, re.IGNORECASE):
        return 0

    # Default: assume some results if response is long enough
    return -1  # Unknown


def run_sequential_chat(save_results: bool = True, method: str = "hybrid"):
    """
    Run questions sequentially using the agent.

    Args:
        save_results: Whether to save results to JSON file
        method: Search method - "hybrid", "api_only", or "vector_only"

    Returns:
        List of result dictionaries with full responses
    """
    from src.adapters.metaproperty import MetaPropertyAPIAdapter
    from src.agents.react_agent import create_property_react_agent
    from src.utils.ab_testing import (
        configure_ab_test,
        get_ab_manager,
        SearchMethod,
    )

    api_url = os.getenv("METAPROPERTY_API_URL", "http://localhost:8000")
    api_token = os.getenv("METAPROPERTY_API_TOKEN", "")

    # Map method string to SearchMethod enum
    method_map = {
        "hybrid": SearchMethod.HYBRID_60_40,
        "api_only": SearchMethod.API_ONLY,
        "vector_only": SearchMethod.CHROMADB_ONLY,
    }

    if method not in method_map:
        print(f"[ERR] Invalid method: {method}")
        print(f"      Valid options: {list(method_map.keys())}")
        return []

    search_method = method_map[method]

    print("=" * 70)
    print(f"SEQUENTIAL CHAT TEST - 30 Questions")
    print(f"Search Method: {method.upper()} ({search_method.value})")
    print("=" * 70)

    # Configure A/B test and set override for consistent method
    configure_ab_test("baseline")
    ab_manager = get_ab_manager()
    ab_manager.set_override(search_method)

    # Initialize
    adapter = MetaPropertyAPIAdapter(api_url=api_url, api_token=api_token)
    agent = create_property_react_agent(property_adapter=adapter)

    # Single thread_id to maintain context across questions
    user_id = "test_sequential"
    thread_id = f"{user_id}_{method}_test"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"\nUser ID: {user_id}")
    print(f"Thread ID: {thread_id}")
    print(f"Search Method: {method}")
    print(f"Total questions: {len(QUESTIONS)}")
    print(f"Timestamp: {timestamp}")
    print("-" * 70)

    results = []

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n[{i:02d}/{len(QUESTIONS)}] Q: {question}")

        try:
            response = agent.chat(
                message=question,
                thread_id=thread_id,
                user_id=user_id,
            )

            # Count results from response
            results_count = count_results_from_response(response)

            # Truncate response for display (handle encoding for Windows)
            response_preview = response[:150] + "..." if len(response) > 150 else response
            # Remove problematic characters for Windows console
            safe_preview = response_preview.encode('ascii', 'replace').decode('ascii')
            print(f"    A: {safe_preview}")
            print(f"    [Results: {results_count if results_count >= 0 else 'unknown'}]")

            results.append({
                "query_id": i,
                "question": question,
                "category": QUESTION_CATEGORIES.get(i, "unknown"),
                "success": True,
                "response": response,
                "response_length": len(response),
                "results_count": results_count if results_count >= 0 else None,
            })

        except Exception as e:
            print(f"    [ERR] Error: {e}")
            results.append({
                "query_id": i,
                "question": question,
                "category": QUESTION_CATEGORIES.get(i, "unknown"),
                "success": False,
                "response": "",
                "response_length": 0,
                "results_count": 0,
                "error": str(e),
            })

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    successful = sum(1 for r in results if r["success"])
    print(f"Successful: {successful}/{len(QUESTIONS)}")
    print(f"Failed: {len(QUESTIONS) - successful}/{len(QUESTIONS)}")

    # Save results to JSON
    if save_results:
        # Create timestamped subfolder within method folder
        # Structure: data/evaluation/{method}/{timestamp}/
        output_dir = project_root / "data" / "evaluation" / method / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)

        result_data = {
            "timestamp": timestamp,
            "thread_id": thread_id,
            "user_id": user_id,
            "search_method": method,
            "total_questions": len(QUESTIONS),
            "successful": successful,
            "results": results,
        }

        # Save to timestamped folder
        output_file = output_dir / "test_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        print(f"\nResults saved to: {output_file}")

        # Also save to 'latest' folder (copy, not symlink for Windows compatibility)
        latest_dir = project_root / "data" / "evaluation" / method / "latest"
        latest_dir.mkdir(parents=True, exist_ok=True)
        latest_file = latest_dir / "test_results.json"
        with open(latest_file, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        # Save timestamp reference for tracking
        timestamp_ref = latest_dir / "timestamp.txt"
        with open(timestamp_ref, "w") as f:
            f.write(timestamp)

    return results


def export_for_evaluation(input_file: str = None, method: str = "hybrid"):
    """
    Export test results to CSV format for manual evaluation.

    Creates a CSV file with columns per docs/12-evaluation-methodology.md:
    - query_id, question, category, results_count
    - relevant_count (to fill manually)
    - precision_at_5 (calculated after manual rating)
    - success (to fill manually: 0 or 1)
    - response_quality (to fill manually: 0-5)
    - notes (for manual notes)
    - response (full response for reference)
    """
    base_eval_dir = project_root / "data" / "evaluation"

    # Find input file - use new folder structure
    if input_file:
        json_file = Path(input_file)
        # Determine eval_dir from input file path
        eval_dir = json_file.parent
    else:
        # Look in latest folder first (new structure)
        latest_dir = base_eval_dir / method / "latest"
        json_file = latest_dir / "test_results.json"
        if not json_file.exists():
            # Fallback to old structure
            json_file = base_eval_dir / method / "test_results_latest.json"
        eval_dir = latest_dir if latest_dir.exists() else base_eval_dir / method

    if not json_file.exists():
        print(f"[ERR] Results file not found: {json_file}")
        print("Run the test first: python scripts/test_sequential_chat.py")
        return None

    # Load results
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    timestamp = data.get("timestamp", datetime.now().strftime("%Y%m%d_%H%M%S"))
    method = data.get("search_method", method)

    # Use timestamped folder (new structure)
    eval_dir = base_eval_dir / method / timestamp
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Create CSV for manual rating
    csv_file = eval_dir / "evaluation_template.csv"

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "query_id",
            "question",
            "category",
            "results_count",
            "relevant_count",
            "precision_at_5",
            "success",
            "response_quality",
            "notes",
            "response_preview",
        ])

        # Data rows
        for r in results:
            response_preview = r.get("response", "")[:500]  # First 500 chars
            writer.writerow([
                r.get("query_id", ""),
                r.get("question", ""),
                r.get("category", ""),
                r.get("results_count", ""),
                "",  # relevant_count - to fill manually
                "",  # precision_at_5 - calculated later
                "",  # success - to fill manually (0 or 1)
                "",  # response_quality - to fill manually (0-5)
                "",  # notes
                response_preview.replace("\n", " "),  # response preview
            ])

    print(f"\n[OK] CSV template created: {csv_file}")
    print(f"    Folder: {eval_dir}")
    print("\nManual evaluation steps:")
    print("  1. Open CSV in Excel/LibreOffice")
    print("  2. For each row, fill in:")
    print("     - relevant_count: How many results are relevant (0 to results_count)")
    print("     - success: 1 if query successful, 0 if failed")
    print("     - response_quality: 0-5 rating")
    print("     - notes: Any observations")
    print("  3. Save the CSV")
    print("  4. Run: python scripts/calculate_evaluation_metrics.py")

    # Also create a full responses file for detailed review
    responses_file = eval_dir / "full_responses.txt"
    with open(responses_file, "w", encoding="utf-8") as f:
        for r in results:
            f.write("=" * 70 + "\n")
            f.write(f"Query {r.get('query_id')}: {r.get('question')}\n")
            f.write(f"Category: {r.get('category')}\n")
            f.write(f"Results Count: {r.get('results_count')}\n")
            f.write("-" * 70 + "\n")
            f.write(r.get("response", "(no response)") + "\n")
            f.write("\n")

    print(f"[OK] Full responses saved: {responses_file}")

    return csv_file


def show_metrics():
    """Display collected metrics."""
    metrics_dir = project_root / "data" / "metrics"
    today = datetime.now().strftime("%Y-%m-%d")

    print("\n" + "=" * 70)
    print("COLLECTED METRICS")
    print("=" * 70)

    # Search metrics
    search_file = metrics_dir / f"search_{today}.jsonl"
    if search_file.exists():
        with open(search_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        print(f"\n[*] Search Metrics: {len(lines)} records")

        # Parse stats
        methods = {}
        latencies = []
        results_counts = []
        reranking_counts = 0

        for line in lines:
            try:
                record = json.loads(line)
                method = record.get("method", "unknown")
                methods[method] = methods.get(method, 0) + 1
                if "total_latency_ms" in record:
                    latencies.append(record["total_latency_ms"])
                if "final_results_count" in record:
                    results_counts.append(record["final_results_count"])
                if record.get("reranking_applied"):
                    reranking_counts += 1
            except:
                pass

        print(f"\nBy method:")
        for method, count in methods.items():
            print(f"  - {method}: {count}")

        if latencies:
            print(f"\nLatency:")
            print(f"  - Average: {sum(latencies)/len(latencies):.2f} ms")
            print(f"  - Min: {min(latencies):.2f} ms")
            print(f"  - Max: {max(latencies):.2f} ms")

        if results_counts:
            print(f"\nResults:")
            print(f"  - Average results per query: {sum(results_counts)/len(results_counts):.1f}")
            print(f"  - Queries with 0 results: {results_counts.count(0)}")
            print(f"  - Queries with results: {len([r for r in results_counts if r > 0])}")

        print(f"\nReranking applied: {reranking_counts}/{len(lines)}")

    # Tool metrics
    tool_file = metrics_dir / f"tool_{today}.jsonl"
    if tool_file.exists():
        with open(tool_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        print(f"\n[*] Tool Metrics: {len(lines)} calls")

        tools = {}
        for line in lines:
            try:
                record = json.loads(line)
                tool = record.get("tool_name", "unknown")
                tools[tool] = tools.get(tool, 0) + 1
            except:
                pass

        for tool, count in tools.items():
            print(f"  - {tool}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Run 30-question sequential chat test for RAG evaluation"
    )
    parser.add_argument(
        "--method",
        type=str,
        default="hybrid",
        choices=["hybrid", "api_only", "vector_only"],
        help="Search method: hybrid (default), api_only, or vector_only",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export latest results to CSV for manual evaluation",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input JSON file for export (default: latest results for method)",
    )
    parser.add_argument(
        "--skip-test",
        action="store_true",
        help="Skip running test, only show metrics",
    )

    args = parser.parse_args()

    if args.export:
        # Export mode - use new folder structure
        input_file = args.input
        if not input_file:
            # Try new structure first: method/latest/test_results.json
            latest_dir = project_root / "data" / "evaluation" / args.method / "latest"
            input_file = latest_dir / "test_results.json"
            if not input_file.exists():
                # Fallback to old structure
                eval_dir = project_root / "data" / "evaluation" / args.method
                input_file = eval_dir / "test_results_latest.json"
            input_file = str(input_file) if input_file.exists() else None
        export_for_evaluation(input_file, method=args.method)
        return

    if args.skip_test:
        show_metrics()
        return

    print("\n[*] Starting sequential chat test...")
    print(f"Search Method: {args.method.upper()}")
    print("This will run 30 questions in sequence (with context maintained)")
    print()

    # Run test with specified method
    results = run_sequential_chat(method=args.method)

    # Show metrics summary
    show_metrics()

    print("\n" + "=" * 70)
    print("Next steps:")
    print(f"  1. Export to CSV: python scripts/test_sequential_chat.py --method {args.method} --export")
    print("  2. Manual rating: Fill in the CSV file")
    print("  3. Calculate metrics: python scripts/calculate_evaluation_metrics.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
