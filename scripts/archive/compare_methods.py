"""
Compare Methods Script for RAG Evaluation

Generates comparison reports for:
- Phase 1: Search method comparison (API vs Vector vs Hybrid)
- Phase 2: LLM model comparison (GPT vs Claude vs Gemini)

Usage:
    python scripts/compare_methods.py --phase 1
    python scripts/compare_methods.py --phase 2
    python scripts/compare_methods.py --phase 1 --output markdown
"""

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_evaluation_results(eval_dir: Path, method: str) -> Optional[Dict]:
    """
    Load evaluation results for a specific method.

    Looks for completed evaluation CSV files with calculated metrics.
    Now looks in method-specific subfolders: eval_dir/method/
    """
    method_dir = eval_dir / method

    # Look for rated CSV file (after manual evaluation)
    csv_files = []
    if method_dir.exists():
        csv_files = list(method_dir.glob("evaluation_rated_*.csv"))
        if not csv_files:
            csv_files = list(method_dir.glob("*rated*.csv"))

    # Fallback to old location
    if not csv_files:
        csv_files = list(eval_dir.glob(f"evaluation_rated_{method}_*.csv"))
        if not csv_files:
            csv_files = list(eval_dir.glob(f"*{method}*rated*.csv"))

    if not csv_files:
        return None

    # Use most recent file
    csv_file = sorted(csv_files)[-1]

    results = {
        "method": method,
        "file": str(csv_file),
        "queries": [],
        "metrics": {},
    }

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results["queries"].append(row)

    return results


def load_json_results(eval_dir: Path, method: str) -> Optional[Dict]:
    """
    Load raw JSON test results for a specific method.

    Now looks in method-specific subfolders: eval_dir/method/
    """
    method_dir = eval_dir / method

    # Try method-specific folder first
    json_file = method_dir / "test_results_latest.json"
    if not json_file.exists():
        # Try to find any matching file in method folder
        if method_dir.exists():
            json_files = list(method_dir.glob("test_results_*.json"))
            if json_files:
                json_file = sorted(json_files)[-1]

    # Fallback to old location
    if not json_file.exists():
        json_file = eval_dir / f"test_results_{method}_latest.json"
        if not json_file.exists():
            json_files = list(eval_dir.glob(f"test_results_{method}_*.json"))
            if json_files:
                json_file = sorted(json_files)[-1]
            else:
                return None

    if not json_file.exists():
        return None

    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics_from_csv(queries: List[Dict]) -> Dict:
    """
    Calculate aggregate metrics from evaluated CSV data.
    """
    total = len(queries)
    if total == 0:
        return {}

    # Initialize counters
    precision_at_5_sum = 0.0
    overall_precision_sum = 0.0
    mrr_sum = 0.0
    success_count = 0
    coverage_count = 0

    valid_p5 = 0
    valid_op = 0
    valid_mrr = 0

    for q in queries:
        # Precision@5
        p5 = q.get("precision_at_5", "")
        if p5 and p5 != "":
            try:
                precision_at_5_sum += float(p5)
                valid_p5 += 1
            except ValueError:
                pass

        # Overall Precision
        op = q.get("overall_precision", "")
        if op and op != "":
            try:
                overall_precision_sum += float(op)
                valid_op += 1
            except ValueError:
                pass

        # MRR
        mrr = q.get("mrr", "")
        if mrr and mrr != "":
            try:
                mrr_sum += float(mrr)
                valid_mrr += 1
            except ValueError:
                pass

        # Success (binary)
        success = q.get("success", "")
        if success == "1" or success == 1:
            success_count += 1

        # Coverage (has results)
        results_count = q.get("results_count", "0")
        try:
            if int(results_count) > 0:
                coverage_count += 1
        except ValueError:
            pass

    return {
        "total_queries": total,
        "precision_at_5": precision_at_5_sum / valid_p5 if valid_p5 > 0 else 0,
        "overall_precision": overall_precision_sum / valid_op if valid_op > 0 else 0,
        "mrr": mrr_sum / valid_mrr if valid_mrr > 0 else 0,
        "success_rate": success_count / total if total > 0 else 0,
        "coverage": coverage_count / total if total > 0 else 0,
        "valid_counts": {
            "p5": valid_p5,
            "op": valid_op,
            "mrr": valid_mrr,
        }
    }


def generate_phase1_report(eval_dir: Path, output_format: str = "console") -> str:
    """
    Generate Phase 1 comparison report: Search Method Comparison.
    """
    methods = ["hybrid", "api_only", "vector_only"]
    method_labels = {
        "hybrid": "Hybrid (60/40)",
        "api_only": "API Only",
        "vector_only": "Vector Only",
    }

    results = {}
    for method in methods:
        csv_data = load_evaluation_results(eval_dir, method)
        json_data = load_json_results(eval_dir, method)

        if csv_data and csv_data.get("queries"):
            results[method] = {
                "data": csv_data,
                "metrics": calculate_metrics_from_csv(csv_data["queries"]),
                "raw": json_data,
            }
        elif json_data:
            results[method] = {
                "data": None,
                "metrics": {},
                "raw": json_data,
                "status": "pending_evaluation",
            }

    # Generate report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("PHASE 1: SEARCH METHOD COMPARISON REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    # Summary table
    report_lines.append("## Summary Table")
    report_lines.append("")
    report_lines.append("| Metric | " + " | ".join([method_labels[m] for m in methods]) + " |")
    report_lines.append("|--------|" + "|".join(["----------" for _ in methods]) + "|")

    metrics_to_show = [
        ("Precision@5", "precision_at_5", "{:.2%}"),
        ("Overall Precision", "overall_precision", "{:.2%}"),
        ("MRR", "mrr", "{:.3f}"),
        ("Success Rate", "success_rate", "{:.2%}"),
        ("Coverage", "coverage", "{:.2%}"),
    ]

    for label, key, fmt in metrics_to_show:
        values = []
        for method in methods:
            if method in results and results[method].get("metrics"):
                val = results[method]["metrics"].get(key, 0)
                values.append(fmt.format(val))
            else:
                values.append("N/A")
        report_lines.append(f"| {label} | " + " | ".join(values) + " |")

    report_lines.append("")

    # Status per method
    report_lines.append("## Method Status")
    report_lines.append("")
    for method in methods:
        status = "Not tested"
        if method in results:
            if results[method].get("metrics"):
                status = f"Evaluated ({results[method]['metrics'].get('total_queries', 0)} queries)"
            elif results[method].get("status") == "pending_evaluation":
                status = "Tested, pending manual evaluation"
        report_lines.append(f"- **{method_labels[method]}**: {status}")

    report_lines.append("")

    # Determine winner (if all evaluated)
    all_evaluated = all(
        method in results and results[method].get("metrics")
        for method in methods
    )

    if all_evaluated:
        report_lines.append("## Winner Analysis")
        report_lines.append("")

        # Find best for each metric
        for label, key, fmt in metrics_to_show:
            best_method = max(methods, key=lambda m: results[m]["metrics"].get(key, 0))
            best_val = results[best_method]["metrics"].get(key, 0)
            report_lines.append(f"- Best {label}: **{method_labels[best_method]}** ({fmt.format(best_val)})")

        report_lines.append("")

        # Overall recommendation (weighted by P@5 and MRR)
        scores = {}
        for method in methods:
            m = results[method]["metrics"]
            # Weight: P@5 (40%) + MRR (30%) + Success (20%) + Coverage (10%)
            scores[method] = (
                m.get("precision_at_5", 0) * 0.4 +
                m.get("mrr", 0) * 0.3 +
                m.get("success_rate", 0) * 0.2 +
                m.get("coverage", 0) * 0.1
            )

        winner = max(scores, key=scores.get)
        report_lines.append(f"### Recommendation")
        report_lines.append(f"**Winner: {method_labels[winner]}** (Composite Score: {scores[winner]:.3f})")
        report_lines.append("")
        report_lines.append("Use this method for Phase 2 LLM comparison.")

    report_lines.append("")
    report_lines.append("=" * 70)

    report = "\n".join(report_lines)

    # Output
    if output_format == "markdown":
        output_file = eval_dir / f"phase1_comparison_{datetime.now().strftime('%Y%m%d')}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {output_file}")

    return report


def generate_phase2_report(eval_dir: Path, output_format: str = "console") -> str:
    """
    Generate Phase 2 comparison report: LLM Model Comparison.
    """
    # LLM models to compare
    llms = ["openai", "anthropic", "google"]
    llm_labels = {
        "openai": "GPT-4o-mini",
        "anthropic": "Claude 3 Haiku",
        "google": "Gemini 1.5 Flash",
    }

    results = {}
    for llm in llms:
        # Look for LLM-specific results
        csv_files = list(eval_dir.glob(f"*{llm}*rated*.csv"))
        json_files = list(eval_dir.glob(f"*{llm}*.json"))

        if csv_files:
            csv_file = sorted(csv_files)[-1]
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                queries = list(reader)
            results[llm] = {
                "metrics": calculate_metrics_from_csv(queries),
                "queries": queries,
            }

    # Generate report
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("PHASE 2: LLM MODEL COMPARISON REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    if not results:
        report_lines.append("No LLM comparison data found.")
        report_lines.append("Run tests with: python scripts/test_sequential_chat.py --llm [model]")
    else:
        # Summary table
        report_lines.append("## Summary Table")
        report_lines.append("")
        headers = ["Metric"] + [llm_labels.get(llm, llm) for llm in llms if llm in results]
        report_lines.append("| " + " | ".join(headers) + " |")
        report_lines.append("|" + "|".join(["----------" for _ in headers]) + "|")

        metrics_to_show = [
            ("Response Quality", "response_quality", "{:.2f}/5"),
            ("Precision@5", "precision_at_5", "{:.2%}"),
            ("Success Rate", "success_rate", "{:.2%}"),
        ]

        for label, key, fmt in metrics_to_show:
            values = [label]
            for llm in llms:
                if llm in results and results[llm].get("metrics"):
                    val = results[llm]["metrics"].get(key, 0)
                    values.append(fmt.format(val))
            report_lines.append("| " + " | ".join(values) + " |")

    report_lines.append("")
    report_lines.append("=" * 70)

    report = "\n".join(report_lines)

    if output_format == "markdown":
        output_file = eval_dir / f"phase2_comparison_{datetime.now().strftime('%Y%m%d')}.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {output_file}")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison reports for RAG evaluation"
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        choices=[1, 2],
        help="Phase to generate report for: 1 (Search Methods) or 2 (LLM Models)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="console",
        choices=["console", "markdown"],
        help="Output format: console (default) or markdown file",
    )

    args = parser.parse_args()

    eval_dir = project_root / "data" / "evaluation"

    if args.phase == 1:
        report = generate_phase1_report(eval_dir, args.output)
    else:
        report = generate_phase2_report(eval_dir, args.output)

    print(report)


if __name__ == "__main__":
    main()
