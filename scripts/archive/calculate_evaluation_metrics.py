"""
Calculate Evaluation Metrics from Manually-Rated CSV

Reads the evaluation CSV with manual ratings and calculates:
- Precision@5: relevant_count / min(results_count, 5)
- Overall Precision: relevant_count / results_count
- MRR (Mean Reciprocal Rank): 1 / first_relevant_rank
- Success Rate: queries with success=1 / total queries
- Coverage: queries with results > 0 / total queries
- Mean Response Quality: average of response_quality ratings

References:
- Voorhees, E. M. (1999). TREC-8 Question Answering Track Report. (MRR)
- Manning et al. (2008). Introduction to Information Retrieval. (Precision)

Usage:
    python scripts/calculate_evaluation_metrics.py
    python scripts/calculate_evaluation_metrics.py --input data/evaluation/rated.csv
    python scripts/calculate_evaluation_metrics.py --output report.json
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_rated_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """
    Load manually-rated evaluation CSV.

    Expected columns:
    - query_id, question, category, results_count
    - relevant_count (from HTML rating)
    - relevant_in_top5 (from HTML rating)
    - first_relevant_rank (from HTML rating, for MRR)
    - overall_precision, precision_at_5, mrr (auto-calculated)
    - success (auto-calculated: 1 if relevant_count >= 1)
    - response_quality (manually filled: 0-5)
    - notes
    """
    results = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                result = {
                    "query_id": int(row.get("query_id", 0)),
                    "question": row.get("question", ""),
                    "category": row.get("category", ""),
                    "results_count": parse_int(row.get("results_count")),
                    "relevant_count": parse_int(row.get("relevant_count")),
                    "relevant_in_top5": parse_int(row.get("relevant_in_top5")),
                    "first_relevant_rank": parse_int(row.get("first_relevant_rank")),
                    "overall_precision": parse_float(row.get("overall_precision")),
                    "precision_at_5": parse_float(row.get("precision_at_5")),
                    "mrr": parse_float(row.get("mrr")),
                    "success": parse_int(row.get("success")),
                    "response_quality": parse_float(row.get("response_quality")),
                    "notes": row.get("notes", ""),
                }
                results.append(result)
            except Exception as e:
                print(f"[WARN] Error parsing row: {e}")
                continue

    return results


def parse_int(value: str) -> Optional[int]:
    """Parse integer from string, return None if empty or invalid."""
    if value is None or value.strip() == "" or value.upper() == "N/A":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def parse_float(value: str) -> Optional[float]:
    """Parse float from string, return None if empty or invalid."""
    if value is None or value.strip() == "" or value.upper() == "N/A":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def calculate_precision_at_k(relevant_count: int, results_count: int, k: int = 5) -> float:
    """
    Calculate Precision@K.

    Formula: relevant_count / min(results_count, K)
    """
    if results_count is None or results_count == 0:
        return None  # N/A for queries with no results

    denominator = min(results_count, k)
    if denominator == 0:
        return None

    return relevant_count / denominator


def calculate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate all evaluation metrics.

    Returns dict with:
    - overall_precision: Mean Overall Precision (relevant/total for all results)
    - precision_at_5: Mean Precision@5 (only top 5 results)
    - mrr: Mean Reciprocal Rank (1/first_relevant_rank)
    - success_rate: Overall success rate
    - coverage: % of queries with results
    - mean_response_quality: Mean response quality rating
    - category_breakdown: Metrics by query category
    """
    total_queries = len(results)

    if total_queries == 0:
        return {"error": "No data to analyze"}

    # Calculate metrics for each query
    overall_precisions = []
    precision_at_5_list = []
    mrr_list = []

    for r in results:
        if r["results_count"] is not None and r["results_count"] > 0:
            if r["relevant_count"] is not None:
                # Overall Precision = relevant_count / results_count
                overall_p = r["relevant_count"] / r["results_count"]
                overall_precisions.append(overall_p)
                r["overall_precision"] = round(overall_p, 4)

                # Precision@5 = relevant_in_top5 / min(results_count, 5)
                relevant_for_p5 = r.get("relevant_in_top5", r["relevant_count"])
                if relevant_for_p5 is None:
                    relevant_for_p5 = r["relevant_count"]
                p5 = calculate_precision_at_k(relevant_for_p5, r["results_count"], k=5)
                if p5 is not None:
                    precision_at_5_list.append(p5)
                    r["precision_at_5"] = round(p5, 4)
                else:
                    r["precision_at_5"] = None

                # MRR = 1 / first_relevant_rank (or from CSV if already calculated)
                if r.get("mrr") is not None:
                    mrr_list.append(r["mrr"])
                elif r.get("first_relevant_rank") is not None and r["first_relevant_rank"] > 0:
                    mrr_val = 1 / r["first_relevant_rank"]
                    mrr_list.append(mrr_val)
                    r["mrr"] = round(mrr_val, 4)
                else:
                    # No relevant found, MRR = 0
                    mrr_list.append(0)
                    r["mrr"] = 0
            else:
                r["overall_precision"] = None
                r["precision_at_5"] = None
                r["mrr"] = None
        else:
            r["overall_precision"] = None
            r["precision_at_5"] = None
            r["mrr"] = None

    # Mean Overall Precision
    mean_overall_precision = sum(overall_precisions) / len(overall_precisions) if overall_precisions else None

    # Mean Precision@5
    mean_precision_at_5 = sum(precision_at_5_list) / len(precision_at_5_list) if precision_at_5_list else None

    # Mean Reciprocal Rank
    mean_mrr = sum(mrr_list) / len(mrr_list) if mrr_list else None

    # Success Rate
    successes = [r["success"] for r in results if r["success"] is not None]
    success_rate = sum(successes) / len(successes) if successes else None

    # Coverage
    queries_with_results = sum(
        1 for r in results
        if r["results_count"] is not None and r["results_count"] > 0
    )
    coverage = queries_with_results / total_queries

    # Mean Response Quality
    qualities = [r["response_quality"] for r in results if r["response_quality"] is not None]
    mean_quality = sum(qualities) / len(qualities) if qualities else None

    # Category breakdown
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = {
                "count": 0,
                "overall_precisions": [],
                "precisions_at_5": [],
                "mrr_values": [],
                "successes": [],
                "qualities": [],
            }

        categories[cat]["count"] += 1

        if r.get("overall_precision") is not None:
            categories[cat]["overall_precisions"].append(r["overall_precision"])
        if r.get("precision_at_5") is not None:
            categories[cat]["precisions_at_5"].append(r["precision_at_5"])
        if r.get("mrr") is not None:
            categories[cat]["mrr_values"].append(r["mrr"])
        if r["success"] is not None:
            categories[cat]["successes"].append(r["success"])
        if r["response_quality"] is not None:
            categories[cat]["qualities"].append(r["response_quality"])

    category_metrics = {}
    for cat, data in categories.items():
        category_metrics[cat] = {
            "count": data["count"],
            "mean_overall_precision": round(sum(data["overall_precisions"]) / len(data["overall_precisions"]), 4) if data["overall_precisions"] else None,
            "mean_precision_at_5": round(sum(data["precisions_at_5"]) / len(data["precisions_at_5"]), 4) if data["precisions_at_5"] else None,
            "mean_mrr": round(sum(data["mrr_values"]) / len(data["mrr_values"]), 4) if data["mrr_values"] else None,
            "success_rate": round(sum(data["successes"]) / len(data["successes"]), 4) if data["successes"] else None,
            "mean_quality": round(sum(data["qualities"]) / len(data["qualities"]), 2) if data["qualities"] else None,
        }

    return {
        "timestamp": datetime.now().isoformat(),
        "total_queries": total_queries,
        "queries_with_results": queries_with_results,
        "queries_rated": len([r for r in results if r["relevant_count"] is not None]),

        # Main metrics
        "mean_overall_precision": round(mean_overall_precision, 4) if mean_overall_precision else None,
        "mean_precision_at_5": round(mean_precision_at_5, 4) if mean_precision_at_5 else None,
        "mean_mrr": round(mean_mrr, 4) if mean_mrr else None,
        "success_rate": round(success_rate, 4) if success_rate else None,
        "coverage": round(coverage, 4),
        "mean_response_quality": round(mean_quality, 2) if mean_quality else None,

        # Detailed
        "category_breakdown": category_metrics,
        "detailed_results": results,
    }


def generate_markdown_report(metrics: Dict[str, Any]) -> str:
    """Generate markdown report for thesis."""
    lines = [
        "# RAG Property Chatbot - Evaluation Report",
        "",
        f"**Generated:** {metrics.get('timestamp', 'N/A')}",
        "",
        "## Summary",
        "",
        f"- **Total Queries:** {metrics.get('total_queries', 0)}",
        f"- **Queries with Results:** {metrics.get('queries_with_results', 0)}",
        f"- **Queries Rated:** {metrics.get('queries_rated', 0)}",
        "",
        "## Main Metrics",
        "",
        "| Metric | Value | Description |",
        "|--------|-------|-------------|",
    ]

    # Main metrics table
    op = metrics.get("mean_overall_precision")
    p5 = metrics.get("mean_precision_at_5")
    mrr = metrics.get("mean_mrr")
    sr = metrics.get("success_rate")
    cov = metrics.get("coverage")
    mrq = metrics.get("mean_response_quality")

    lines.append(f"| Overall Precision | {op:.2%} | Relevant / Total results |" if op else "| Overall Precision | N/A | |")
    lines.append(f"| Precision@5 | {p5:.2%} | Relevant in top 5 |" if p5 else "| Precision@5 | N/A | |")
    lines.append(f"| MRR | {mrr:.3f} | Position of first relevant |" if mrr else "| MRR | N/A | |")
    lines.append(f"| Success Rate | {sr:.2%} | Queries with ≥1 relevant |" if sr else "| Success Rate | N/A | |")
    lines.append(f"| Coverage | {cov:.2%} | Queries with results |" if cov else "| Coverage | N/A | |")
    lines.append(f"| Response Quality | {mrq:.2f}/5 | Subjective rating |" if mrq else "| Response Quality | N/A | |")

    # Category breakdown
    lines.extend([
        "",
        "## Performance by Category",
        "",
        "| Category | Count | P@5 | MRR | Success | Quality |",
        "|----------|-------|-----|-----|---------|---------|",
    ])

    category_breakdown = metrics.get("category_breakdown", {})
    for cat, data in sorted(category_breakdown.items()):
        p = data.get("mean_precision_at_5")
        m = data.get("mean_mrr")
        s = data.get("success_rate")
        q = data.get("mean_quality")

        p_str = f"{p:.2%}" if p else "N/A"
        m_str = f"{m:.3f}" if m else "N/A"
        s_str = f"{s:.2%}" if s else "N/A"
        q_str = f"{q:.2f}" if q else "N/A"

        lines.append(f"| {cat} | {data['count']} | {p_str} | {m_str} | {s_str} | {q_str} |")

    # Interpretation
    lines.extend([
        "",
        "## Metric Interpretation",
        "",
        "### Precision@5 (Manning et al., 2008)",
        "- Proportion of relevant results in top 5",
        "- Range: 0.0 - 1.0 (higher is better)",
        "",
        "### MRR - Mean Reciprocal Rank (Voorhees, 1999)",
        "- Measures how quickly the first relevant result appears",
        "- MRR = 1.0: First result always relevant",
        "- MRR = 0.5: First relevant typically at position 2",
        "- MRR → 0: Relevant results far down or missing",
        "",
        "### Success Rate (Binary, Voorhees 2002)",
        "- Query is successful if it returns ≥1 relevant result",
        "- Standard TREC evaluation approach",
        "",
        "### Coverage",
        "- Percentage of queries that returned any results",
        "- Lower coverage indicates data gaps",
        "",
        "### Response Quality (0-5)",
        "| Score | Meaning |",
        "|-------|---------|",
        "| 5 | All results very relevant |",
        "| 4 | Most relevant (>70%) |",
        "| 3 | Half relevant (50-70%) |",
        "| 2 | Few relevant (<50%) |",
        "| 1 | No relevant results |",
        "| 0 | Error or no results |",
        "",
        "## References",
        "",
        "- Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*.",
        "- Voorhees, E. M. (1999). The TREC-8 Question Answering Track Report. NIST.",
        "- Voorhees, E. M. (2002). The philosophy of information retrieval evaluation. CLEF Workshop.",
        "",
        "---",
        "",
        "*Report generated for RAG Property Chatbot Thesis*",
    ])

    return "\n".join(lines)


def print_summary(metrics: Dict[str, Any]):
    """Print metrics summary to console."""
    print("\n" + "=" * 60)
    print("EVALUATION METRICS SUMMARY")
    print("=" * 60)

    print(f"\nTotal Queries: {metrics.get('total_queries', 0)}")
    print(f"Queries with Results: {metrics.get('queries_with_results', 0)}")
    print(f"Queries Rated: {metrics.get('queries_rated', 0)}")

    print("\n--- Main Metrics ---")

    op = metrics.get("mean_overall_precision")
    p5 = metrics.get("mean_precision_at_5")
    mrr = metrics.get("mean_mrr")
    sr = metrics.get("success_rate")
    cov = metrics.get("coverage")
    mrq = metrics.get("mean_response_quality")

    if op is not None:
        print(f"Mean Overall Precision: {op:.2%}")
    else:
        print("Mean Overall Precision: N/A")

    if p5 is not None:
        print(f"Mean Precision@5: {p5:.2%}")
    else:
        print("Mean Precision@5: N/A")

    if mrr is not None:
        print(f"Mean Reciprocal Rank (MRR): {mrr:.3f}")
    else:
        print("Mean Reciprocal Rank: N/A")

    if sr is not None:
        print(f"Success Rate: {sr:.2%}")
    else:
        print("Success Rate: N/A")

    if cov is not None:
        print(f"Coverage: {cov:.2%}")

    if mrq is not None:
        print(f"Mean Response Quality: {mrq:.2f}/5")
    else:
        print("Mean Response Quality: N/A")

    print("\n--- By Category ---")
    category_breakdown = metrics.get("category_breakdown", {})
    for cat, data in sorted(category_breakdown.items()):
        p = data.get("mean_precision_at_5")
        m = data.get("mean_mrr")
        s = data.get("success_rate")
        p_str = f"{p:.2%}" if p else "N/A"
        m_str = f"{m:.3f}" if m else "N/A"
        s_str = f"{s:.2%}" if s else "N/A"
        print(f"  {cat}: n={data['count']}, P@5={p_str}, MRR={m_str}, Success={s_str}")


def find_latest_csv(eval_dir: Path, method: str = None) -> Optional[Path]:
    """Find the most recent evaluation CSV file (template or rated)."""
    # New structure: method/{timestamp}/evaluation_template.csv or evaluation_rated.csv
    # Old structure: method/evaluation_template_{timestamp}.csv

    if method:
        method_dir = eval_dir / method

        # Try new structure first: look in latest folder
        latest_dir = method_dir / "latest"
        if latest_dir.exists():
            # Check for rated first, then template
            for name in ["evaluation_rated.csv", "evaluation_template.csv"]:
                csv_file = latest_dir / name
                if csv_file.exists():
                    return csv_file

        # Try new structure: find any timestamped folder
        if method_dir.exists():
            timestamp_dirs = [d for d in method_dir.iterdir() if d.is_dir() and d.name != "latest"]
            if timestamp_dirs:
                # Sort by name (timestamp) descending
                timestamp_dirs.sort(key=lambda d: d.name, reverse=True)
                for ts_dir in timestamp_dirs:
                    for name in ["evaluation_rated.csv", "evaluation_template.csv"]:
                        csv_file = ts_dir / name
                        if csv_file.exists():
                            return csv_file

        # Fallback to old structure
        patterns = ["evaluation_rated_*.csv", "evaluation_template_*.csv"]
        if method_dir.exists():
            for pattern in patterns:
                csv_files = list(method_dir.glob(pattern))
                if csv_files:
                    return max(csv_files, key=lambda f: f.stat().st_mtime)

    # Fallback to base directory
    patterns = ["evaluation_rated_*.csv", "evaluation_template_*.csv"]
    for pattern in patterns:
        csv_files = list(eval_dir.glob(pattern))
        if csv_files:
            return max(csv_files, key=lambda f: f.stat().st_mtime)

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Calculate evaluation metrics from rated CSV"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Input CSV file with manual ratings (default: latest in data/evaluation/)",
    )
    parser.add_argument(
        "--method",
        type=str,
        default=None,
        choices=["hybrid", "api_only", "vector_only"],
        help="Search method to find results for (looks in data/evaluation/[method]/)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON file for metrics (default: auto-generated)",
    )
    parser.add_argument(
        "--no-markdown",
        action="store_true",
        help="Skip generating markdown report",
    )

    args = parser.parse_args()

    base_eval_dir = project_root / "data" / "evaluation"

    # Find input file
    if args.input:
        csv_path = Path(args.input)
        # Determine method from path if possible
        method = args.method
        for m in ["hybrid", "api_only", "vector_only"]:
            if m in str(csv_path):
                method = m
                break
        eval_dir = csv_path.parent
    else:
        csv_path = find_latest_csv(base_eval_dir, args.method)
        method = args.method
        if csv_path:
            eval_dir = csv_path.parent
        else:
            eval_dir = base_eval_dir

    if csv_path is None or not csv_path.exists():
        print("[ERR] No evaluation CSV found.")
        print("Run first:")
        print("  1. python scripts/test_sequential_chat.py")
        print("  2. python scripts/test_sequential_chat.py --export")
        print("  3. Fill in the CSV manually")
        return

    print(f"[*] Loading: {csv_path}")

    # Load and calculate
    results = load_rated_csv(csv_path)

    if not results:
        print("[ERR] No data found in CSV")
        return

    print(f"[OK] Loaded {len(results)} results")

    # Check if any manual ratings exist
    rated_count = sum(1 for r in results if r["relevant_count"] is not None)
    if rated_count == 0:
        print("\n[WARN] No manual ratings found in CSV!")
        print("Please fill in the 'relevant_count', 'success', and 'response_quality' columns")
        print("Then run this script again.")
        return

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Print summary
    print_summary(metrics)

    # Save JSON report - save to same folder as input CSV
    if args.output:
        json_path = Path(args.output)
    else:
        # Save to same folder as the CSV (new structure: timestamped folder)
        json_path = eval_dir / "evaluation_report.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(f"\n[OK] JSON report saved: {json_path}")
    print(f"    Folder: {eval_dir}")

    # Generate markdown report
    if not args.no_markdown:
        md_content = generate_markdown_report(metrics)
        md_path = json_path.with_suffix(".md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[OK] Markdown report saved: {md_path}")

    print("\n" + "=" * 60)
    print("Evaluation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
