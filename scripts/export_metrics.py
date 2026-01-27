"""
Metrics Export for Thesis Analysis

Export collected metrics from JSONL to CSV format for analysis.
Generates summary statistics by search method, date, etc.

Usage:
    python scripts/export_metrics.py                    # Export all metrics
    python scripts/export_metrics.py --date 2026-01-23  # Export specific date
    python scripts/export_metrics.py --type search      # Export only search metrics
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    print("Warning: pandas not installed. Install with: pip install pandas")


def load_jsonl(file_path: Path) -> List[Dict]:
    """Load records from a JSONL file."""
    records = []
    if not file_path.exists():
        return records
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Warning: Skipping invalid JSON line: {e}")
    
    return records


def find_metrics_files(
    metrics_dir: Path,
    metric_type: str = "search",
    date: Optional[str] = None,
    days: int = 7,
) -> List[Path]:
    """
    Find metrics files matching criteria.
    
    Args:
        metrics_dir: Directory containing metrics files
        metric_type: Type of metrics (search, tool, conversation)
        date: Specific date (YYYY-MM-DD) or None for recent
        days: Number of days to look back if no specific date
        
    Returns:
        List of matching file paths
    """
    if date:
        # Specific date
        pattern = f"{metric_type}_{date}.jsonl"
        matches = list(metrics_dir.glob(pattern))
    else:
        # Recent files
        pattern = f"{metric_type}_*.jsonl"
        all_files = list(metrics_dir.glob(pattern))
        
        # Filter to recent days
        cutoff = datetime.now() - timedelta(days=days)
        matches = []
        for f in all_files:
            try:
                # Extract date from filename
                date_str = f.stem.split("_")[-1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date >= cutoff:
                    matches.append(f)
            except ValueError:
                # Include files with unparseable dates
                matches.append(f)
    
    return sorted(matches)


def export_search_metrics(
    input_files: List[Path],
    output_dir: Path,
    prefix: str = "search_metrics",
) -> Dict:
    """
    Export search metrics to CSV with summary statistics.
    
    Returns:
        Dict with export statistics
    """
    if not HAS_PANDAS:
        print("Error: pandas required for CSV export")
        return {"error": "pandas not installed"}
    
    # Load all records
    all_records = []
    for f in input_files:
        records = load_jsonl(f)
        all_records.extend(records)
    
    if not all_records:
        print("No search metrics found")
        return {"records": 0}
    
    # Convert to DataFrame
    df = pd.DataFrame(all_records)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export raw data
    raw_path = output_dir / f"{prefix}_raw.csv"
    df.to_csv(raw_path, index=False)
    print(f"Exported {len(df)} records to {raw_path}")
    
    # Generate summary by method
    if "method" in df.columns:
        summary = df.groupby("method").agg({
            "total_latency_ms": ["count", "mean", "std", "min", "max", "median"],
            "api_latency_ms": ["mean", "std"],
            "chromadb_latency_ms": ["mean", "std"],
            "reranking_latency_ms": ["mean", "std"],
            "api_results_count": ["mean", "sum"],
            "final_results_count": ["mean", "sum"],
            "reranking_changes": ["mean", "sum"],
            "embedding_cache_hit": ["sum", "mean"],
        }).round(2)
        
        summary_path = output_dir / f"{prefix}_by_method.csv"
        summary.to_csv(summary_path)
        print(f"Summary by method saved to {summary_path}")
    
    # Generate daily summary
    if "timestamp" in df.columns:
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        daily = df.groupby("date").agg({
            "total_latency_ms": ["count", "mean"],
            "final_results_count": "mean",
            "reranking_changes": "mean",
        }).round(2)
        
        daily_path = output_dir / f"{prefix}_daily.csv"
        daily.to_csv(daily_path)
        print(f"Daily summary saved to {daily_path}")
    
    return {
        "records": len(df),
        "files_processed": len(input_files),
        "output_dir": str(output_dir),
    }


def export_tool_metrics(
    input_files: List[Path],
    output_dir: Path,
    prefix: str = "tool_metrics",
) -> Dict:
    """Export tool metrics to CSV."""
    if not HAS_PANDAS:
        return {"error": "pandas not installed"}
    
    all_records = []
    for f in input_files:
        records = load_jsonl(f)
        all_records.extend(records)
    
    if not all_records:
        print("No tool metrics found")
        return {"records": 0}
    
    df = pd.DataFrame(all_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Raw data
    raw_path = output_dir / f"{prefix}_raw.csv"
    df.to_csv(raw_path, index=False)
    print(f"Exported {len(df)} tool records to {raw_path}")
    
    # Summary by tool
    if "tool_name" in df.columns:
        summary = df.groupby("tool_name").agg({
            "latency_ms": ["count", "mean", "std", "min", "max"],
            "success": ["sum", "mean"],
            "result_count": ["mean"],
            "result_size_chars": ["mean"],
        }).round(2)
        
        summary_path = output_dir / f"{prefix}_by_tool.csv"
        summary.to_csv(summary_path)
        print(f"Tool summary saved to {summary_path}")
    
    return {"records": len(df), "files_processed": len(input_files)}


def export_conversation_metrics(
    input_files: List[Path],
    output_dir: Path,
    prefix: str = "conversation_metrics",
) -> Dict:
    """Export conversation metrics to CSV."""
    if not HAS_PANDAS:
        return {"error": "pandas not installed"}
    
    all_records = []
    for f in input_files:
        records = load_jsonl(f)
        all_records.extend(records)
    
    if not all_records:
        print("No conversation metrics found")
        return {"records": 0}
    
    df = pd.DataFrame(all_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    raw_path = output_dir / f"{prefix}_raw.csv"
    df.to_csv(raw_path, index=False)
    print(f"Exported {len(df)} conversation records to {raw_path}")
    
    return {"records": len(df), "files_processed": len(input_files)}


def main():
    parser = argparse.ArgumentParser(
        description="Export RAG metrics to CSV for thesis analysis"
    )
    parser.add_argument(
        "--metrics-dir",
        type=str,
        default="data/metrics",
        help="Directory containing metrics JSONL files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/metrics/exports",
        help="Directory for CSV output files",
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["search", "tool", "conversation", "all"],
        default="all",
        help="Type of metrics to export",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Specific date to export (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to look back (default: 30)",
    )
    
    args = parser.parse_args()
    
    metrics_dir = Path(args.metrics_dir)
    output_dir = Path(args.output_dir)
    
    if not metrics_dir.exists():
        print(f"Metrics directory not found: {metrics_dir}")
        print("Run some searches first to generate metrics.")
        return
    
    print(f"Exporting metrics from {metrics_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    results = {}
    
    # Export search metrics
    if args.type in ["search", "all"]:
        files = find_metrics_files(metrics_dir, "search", args.date, args.days)
        if files:
            print(f"\nFound {len(files)} search metrics files")
            results["search"] = export_search_metrics(files, output_dir)
        else:
            print("\nNo search metrics files found")
    
    # Export tool metrics
    if args.type in ["tool", "all"]:
        files = find_metrics_files(metrics_dir, "tool", args.date, args.days)
        if files:
            print(f"\nFound {len(files)} tool metrics files")
            results["tool"] = export_tool_metrics(files, output_dir)
        else:
            print("\nNo tool metrics files found")
    
    # Export conversation metrics
    if args.type in ["conversation", "all"]:
        files = find_metrics_files(metrics_dir, "conversation", args.date, args.days)
        if files:
            print(f"\nFound {len(files)} conversation metrics files")
            results["conversation"] = export_conversation_metrics(files, output_dir)
        else:
            print("\nNo conversation metrics files found")
    
    print("\n" + "=" * 50)
    print("EXPORT COMPLETE")
    print("=" * 50)
    for metric_type, stats in results.items():
        print(f"  {metric_type}: {stats.get('records', 0)} records")


if __name__ == "__main__":
    main()
