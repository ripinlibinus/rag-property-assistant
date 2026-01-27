"""
Metrics Analysis and Visualization for Thesis

Generate charts and statistical analysis from collected metrics.
Useful for thesis report and presentation.

Usage:
    python scripts/analyze_metrics.py                      # Full analysis
    python scripts/analyze_metrics.py --no-plots           # Stats only
    python scripts/analyze_metrics.py --output report/     # Custom output
"""

import argparse
import json
import sys
from datetime import datetime
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

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend for server use
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def load_evaluation_report(data_dir: Path) -> Optional[Dict]:
    """Load evaluation report JSON."""
    report_path = data_dir / "evaluation_report.json"
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_confusion_matrix(evaluation_report: Dict, output_dir: Path) -> Dict:
    """
    Generate confusion matrix from evaluation report.
    
    For RAG systems, we create:
    1. Intent Classification Confusion Matrix
    2. Search Method Effectiveness Matrix
    """
    if not HAS_MATPLOTLIB or not HAS_NUMPY:
        return {"error": "matplotlib and numpy required"}
    
    stats = {}
    test_results = evaluation_report.get("test_results", [])
    
    if not test_results:
        return {"error": "No test results found"}
    
    # 1. Intent Classification Confusion Matrix
    intents = set()
    for result in test_results:
        intents.add(result.get("actual_intent", "unknown"))
        intents.add(result.get("predicted_intent", "unknown"))
    
    intent_list = sorted(list(intents))
    n_intents = len(intent_list)
    intent_to_idx = {intent: i for i, intent in enumerate(intent_list)}
    
    # Build confusion matrix
    cm = np.zeros((n_intents, n_intents), dtype=int)
    for result in test_results:
        actual = result.get("actual_intent", "unknown")
        predicted = result.get("predicted_intent", "unknown")
        if actual in intent_to_idx and predicted in intent_to_idx:
            cm[intent_to_idx[actual], intent_to_idx[predicted]] += 1
    
    # Plot confusion matrix
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    ax.set(xticks=np.arange(n_intents),
           yticks=np.arange(n_intents),
           xticklabels=intent_list,
           yticklabels=intent_list,
           title='Intent Classification Confusion Matrix',
           ylabel='Actual Intent',
           xlabel='Predicted Intent')
    
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations
    thresh = cm.max() / 2.
    for i in range(n_intents):
        for j in range(n_intents):
            ax.text(j, i, format(cm[i, j], 'd'),
                   ha="center", va="center",
                   color="white" if cm[i, j] > thresh else "black")
    
    fig.tight_layout()
    cm_path = output_dir / "confusion_matrix_intent.png"
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"Intent confusion matrix saved to {cm_path}")
    
    # Calculate metrics from confusion matrix
    total = cm.sum()
    correct = np.diag(cm).sum()
    accuracy = correct / total if total > 0 else 0
    
    # Per-class metrics
    per_class = {}
    for i, intent in enumerate(intent_list):
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        per_class[intent] = {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "support": int(cm[i, :].sum()),
        }
    
    stats["intent_classification"] = {
        "accuracy": round(accuracy, 3),
        "total_samples": int(total),
        "correct_predictions": int(correct),
        "per_class": per_class,
        "confusion_matrix": cm.tolist(),
        "labels": intent_list,
    }
    
    # 2. Search Relevance Analysis
    relevance_scores = [r.get("relevance_score", 0) for r in test_results if r.get("relevance_score")]
    if relevance_scores:
        stats["search_relevance"] = {
            "mean_score": round(np.mean(relevance_scores), 3),
            "median_score": round(np.median(relevance_scores), 3),
            "std_score": round(np.std(relevance_scores), 3),
            "min_score": round(min(relevance_scores), 3),
            "max_score": round(max(relevance_scores), 3),
        }
        
        # Plot relevance distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(relevance_scores, bins=10, edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(relevance_scores), color='red', linestyle='--', label=f'Mean: {np.mean(relevance_scores):.2f}')
        ax.set_title('Search Relevance Score Distribution')
        ax.set_xlabel('Relevance Score')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        relevance_path = output_dir / "relevance_distribution.png"
        plt.savefig(relevance_path, dpi=150)
        plt.close()
        print(f"Relevance distribution saved to {relevance_path}")
    
    # 3. Category Performance
    category_results = evaluation_report.get("category_results", {})
    if category_results:
        categories = list(category_results.keys())
        accuracies = [category_results[c].get("intent_accuracy", 0) * 100 for c in categories]
        pass_rates = [category_results[c].get("passed", 0) / category_results[c].get("total", 1) * 100 for c in categories]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, accuracies, width, label='Intent Accuracy %', color='steelblue')
        bars2 = ax.bar(x + width/2, pass_rates, width, label='Pass Rate %', color='forestgreen')
        
        ax.set_ylabel('Percentage')
        ax.set_title('Performance by Category')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim(0, 105)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}%', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
        
        fig.tight_layout()
        category_path = output_dir / "category_performance.png"
        plt.savefig(category_path, dpi=150)
        plt.close()
        print(f"Category performance saved to {category_path}")
        
        stats["category_performance"] = category_results
    
    return stats


def generate_reranking_analysis(df: pd.DataFrame, output_dir: Path) -> Dict:
    """
    Analyze reranking effectiveness.
    
    Compares searches with and without reranking.
    """
    stats = {}
    
    if "reranking_applied" not in df.columns:
        return stats
    
    reranked = df[df["reranking_applied"] == True]
    not_reranked = df[df["reranking_applied"] == False]
    
    if len(reranked) == 0 or len(not_reranked) == 0:
        return {"note": "Need both reranked and non-reranked samples for comparison"}
    
    stats["reranking"] = {
        "total_with_reranking": len(reranked),
        "total_without_reranking": len(not_reranked),
        "avg_latency_with": round(reranked["total_latency_ms"].mean(), 2),
        "avg_latency_without": round(not_reranked["total_latency_ms"].mean(), 2),
        "avg_results_with": round(reranked["final_results_count"].mean(), 2),
        "avg_results_without": round(not_reranked["final_results_count"].mean(), 2),
    }
    
    if "reranking_changes" in reranked.columns:
        changes = reranked["reranking_changes"]
        stats["reranking"]["position_changes"] = {
            "mean": round(changes.mean(), 2),
            "max": int(changes.max()),
            "searches_with_changes": int((changes > 0).sum()),
            "pct_with_changes": round((changes > 0).mean() * 100, 2),
        }
    
    return stats


def load_metrics_csv(metrics_dir: Path, metric_type: str = "search") -> Optional[pd.DataFrame]:
    """Load metrics from CSV export."""
    csv_path = metrics_dir / f"{metric_type}_metrics_raw.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    
    # Try loading from JSONL if CSV not available
    jsonl_files = list(metrics_dir.parent.glob(f"{metric_type}_*.jsonl"))
    if jsonl_files:
        records = []
        for f in jsonl_files:
            with open(f, "r", encoding="utf-8") as fp:
                for line in fp:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        if records:
            return pd.DataFrame(records)
    
    return None


def analyze_search_performance(df: pd.DataFrame, output_dir: Path) -> Dict:
    """
    Analyze search performance metrics.
    
    Returns dict with analysis results.
    """
    stats = {}
    
    # Overall statistics
    stats["total_searches"] = len(df)
    stats["date_range"] = {
        "start": df["timestamp"].min() if "timestamp" in df.columns else None,
        "end": df["timestamp"].max() if "timestamp" in df.columns else None,
    }
    
    # Latency analysis
    if "total_latency_ms" in df.columns:
        latency = df["total_latency_ms"]
        stats["latency"] = {
            "mean_ms": round(latency.mean(), 2),
            "median_ms": round(latency.median(), 2),
            "std_ms": round(latency.std(), 2),
            "p95_ms": round(latency.quantile(0.95), 2),
            "p99_ms": round(latency.quantile(0.99), 2),
            "min_ms": round(latency.min(), 2),
            "max_ms": round(latency.max(), 2),
        }
    
    # Method comparison
    if "method" in df.columns:
        method_stats = df.groupby("method").agg({
            "total_latency_ms": ["count", "mean", "median", "std"],
            "final_results_count": "mean",
            "reranking_changes": "mean" if "reranking_changes" in df.columns else "count",
        }).round(2)
        
        stats["by_method"] = method_stats.to_dict()
        
        # Save method comparison
        method_path = output_dir / "method_comparison.csv"
        method_stats.to_csv(method_path)
        print(f"Method comparison saved to {method_path}")
    
    # Cache effectiveness
    if "embedding_cache_hit" in df.columns:
        cache_hits = df["embedding_cache_hit"].sum()
        cache_rate = df["embedding_cache_hit"].mean() * 100
        stats["cache"] = {
            "hits": int(cache_hits),
            "hit_rate_pct": round(cache_rate, 2),
        }
    
    # Re-ranking effectiveness
    if "reranking_changes" in df.columns and "reranking_applied" in df.columns:
        reranked = df[df["reranking_applied"] == True]
        if len(reranked) > 0:
            stats["reranking"] = {
                "total_reranked": len(reranked),
                "avg_position_changes": round(reranked["reranking_changes"].mean(), 2),
                "max_position_changes": int(reranked["reranking_changes"].max()),
                "searches_with_changes": int((reranked["reranking_changes"] > 0).sum()),
            }
    
    return stats


def analyze_tool_performance(df: pd.DataFrame, output_dir: Path) -> Dict:
    """Analyze tool execution metrics."""
    stats = {
        "total_calls": len(df),
    }
    
    if "tool_name" in df.columns:
        tool_counts = df["tool_name"].value_counts().to_dict()
        stats["calls_by_tool"] = tool_counts
        
        # Success rate by tool
        if "success" in df.columns:
            success_rate = df.groupby("tool_name")["success"].mean() * 100
            stats["success_rate_by_tool"] = success_rate.round(2).to_dict()
        
        # Latency by tool
        if "latency_ms" in df.columns:
            latency_by_tool = df.groupby("tool_name")["latency_ms"].agg(["mean", "median", "max"])
            stats["latency_by_tool"] = latency_by_tool.round(2).to_dict()
    
    return stats


def plot_latency_distribution(df: pd.DataFrame, output_dir: Path):
    """Plot latency distribution by method."""
    if not HAS_MATPLOTLIB:
        print("matplotlib not installed, skipping plots")
        return
    
    if "method" not in df.columns or "total_latency_ms" not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Box plot by method
    methods = df["method"].unique()
    data = [df[df["method"] == m]["total_latency_ms"].dropna() for m in methods]
    
    axes[0].boxplot(data, labels=methods)
    axes[0].set_title("Latency Distribution by Search Method")
    axes[0].set_ylabel("Latency (ms)")
    axes[0].set_xlabel("Method")
    axes[0].tick_params(axis='x', rotation=45)
    
    # Histogram
    for method in methods:
        method_data = df[df["method"] == method]["total_latency_ms"]
        axes[1].hist(method_data, bins=30, alpha=0.5, label=method)
    
    axes[1].set_title("Latency Histogram by Method")
    axes[1].set_xlabel("Latency (ms)")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()
    
    plt.tight_layout()
    plot_path = output_dir / "latency_distribution.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Latency distribution plot saved to {plot_path}")


def plot_method_comparison(df: pd.DataFrame, output_dir: Path):
    """Plot method comparison bar charts."""
    if not HAS_MATPLOTLIB:
        return
    
    if "method" not in df.columns:
        return
    
    method_stats = df.groupby("method").agg({
        "total_latency_ms": "mean",
        "final_results_count": "mean",
        "reranking_changes": "mean" if "reranking_changes" in df.columns else "count",
    }).round(2)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Average latency
    method_stats["total_latency_ms"].plot(kind="bar", ax=axes[0], color="steelblue")
    axes[0].set_title("Average Latency by Method")
    axes[0].set_ylabel("Latency (ms)")
    axes[0].tick_params(axis='x', rotation=45)
    
    # Average results
    method_stats["final_results_count"].plot(kind="bar", ax=axes[1], color="forestgreen")
    axes[1].set_title("Average Results Count by Method")
    axes[1].set_ylabel("Results")
    axes[1].tick_params(axis='x', rotation=45)
    
    # Reranking changes
    if "reranking_changes" in method_stats.columns:
        method_stats["reranking_changes"].plot(kind="bar", ax=axes[2], color="coral")
        axes[2].set_title("Average Reranking Changes by Method")
        axes[2].set_ylabel("Position Changes")
        axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plot_path = output_dir / "method_comparison.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Method comparison plot saved to {plot_path}")


def plot_daily_trends(df: pd.DataFrame, output_dir: Path):
    """Plot daily trends."""
    if not HAS_MATPLOTLIB or "timestamp" not in df.columns:
        return
    
    df = df.copy()
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    
    daily = df.groupby("date").agg({
        "total_latency_ms": ["count", "mean"],
    })
    daily.columns = ["search_count", "avg_latency"]
    
    if len(daily) < 2:
        return
    
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # Search count
    daily["search_count"].plot(ax=axes[0], marker="o", color="steelblue")
    axes[0].set_title("Daily Search Volume")
    axes[0].set_ylabel("Searches")
    axes[0].grid(True, alpha=0.3)
    
    # Average latency
    daily["avg_latency"].plot(ax=axes[1], marker="o", color="coral")
    axes[1].set_title("Daily Average Latency")
    axes[1].set_ylabel("Latency (ms)")
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = output_dir / "daily_trends.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Daily trends plot saved to {plot_path}")


def generate_report(stats: Dict, output_dir: Path):
    """Generate markdown report."""
    report_lines = [
        "# RAG Search Metrics Analysis Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "\n## Overview",
        f"\n- **Total Searches:** {stats.get('total_searches', 'N/A')}",
    ]
    
    if "date_range" in stats:
        report_lines.append(f"- **Date Range:** {stats['date_range'].get('start')} to {stats['date_range'].get('end')}")
    
    if "latency" in stats:
        report_lines.extend([
            "\n## Latency Statistics",
            f"\n| Metric | Value |",
            f"|--------|-------|",
            f"| Mean | {stats['latency']['mean_ms']} ms |",
            f"| Median | {stats['latency']['median_ms']} ms |",
            f"| Std Dev | {stats['latency']['std_ms']} ms |",
            f"| P95 | {stats['latency']['p95_ms']} ms |",
            f"| P99 | {stats['latency']['p99_ms']} ms |",
        ])
    
    if "cache" in stats:
        report_lines.extend([
            "\n## Cache Performance",
            f"\n- **Cache Hits:** {stats['cache']['hits']}",
            f"- **Hit Rate:** {stats['cache']['hit_rate_pct']}%",
        ])
    
    if "reranking" in stats:
        report_lines.extend([
            "\n## Re-ranking Effectiveness",
            f"\n- **Searches with Re-ranking:** {stats['reranking']['total_reranked']}",
            f"- **Avg Position Changes:** {stats['reranking']['avg_position_changes']}",
            f"- **Searches with Changes:** {stats['reranking']['searches_with_changes']}",
        ])
    
    report_lines.extend([
        "\n## Generated Files",
        "\n- `search_metrics_raw.csv` - Raw search data",
        "- `method_comparison.csv` - Stats by search method",
        "- `latency_distribution.png` - Latency box plots",
        "- `method_comparison.png` - Method comparison charts",
        "- `daily_trends.png` - Daily trends",
    ])
    
    report_path = output_dir / "analysis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Report saved to {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze RAG metrics for thesis"
    )
    parser.add_argument(
        "--metrics-dir",
        type=str,
        default="data/metrics/exports",
        help="Directory containing metrics CSV files",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/metrics/analysis",
        help="Output directory for analysis results",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip generating plots",
    )
    
    args = parser.parse_args()
    
    if not HAS_PANDAS:
        print("Error: pandas is required. Install with: pip install pandas")
        return
    
    metrics_dir = Path(args.metrics_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("RAG METRICS ANALYSIS")
    print("=" * 50)
    
    # Load and analyze search metrics
    search_df = load_metrics_csv(metrics_dir, "search")
    if search_df is not None and len(search_df) > 0:
        print(f"\nLoaded {len(search_df)} search records")
        
        stats = analyze_search_performance(search_df, output_dir)
        
        # Print summary
        print("\n--- Search Performance ---")
        print(f"Total searches: {stats.get('total_searches', 0)}")
        if "latency" in stats:
            print(f"Mean latency: {stats['latency']['mean_ms']} ms")
            print(f"Median latency: {stats['latency']['median_ms']} ms")
            print(f"P95 latency: {stats['latency']['p95_ms']} ms")
        if "cache" in stats:
            print(f"Cache hit rate: {stats['cache']['hit_rate_pct']}%")
        
        # Generate plots
        if not args.no_plots and HAS_MATPLOTLIB:
            print("\nGenerating plots...")
            plot_latency_distribution(search_df, output_dir)
            plot_method_comparison(search_df, output_dir)
            plot_daily_trends(search_df, output_dir)
            
            # Reranking analysis
            rerank_stats = generate_reranking_analysis(search_df, output_dir)
            if rerank_stats:
                stats.update(rerank_stats)
        
        # Generate report
        generate_report(stats, output_dir)
        
        # Save stats as JSON (convert tuple keys to strings)
        stats_path = output_dir / "analysis_stats.json"
        
        def convert_keys(obj):
            """Convert tuple keys to strings for JSON serialization."""
            if isinstance(obj, dict):
                return {str(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(i) for i in obj]
            else:
                return obj
        
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(convert_keys(stats), f, indent=2, default=str)
        print(f"Stats saved to {stats_path}")
    else:
        print("\nNo search metrics found. Run some searches first.")
        print("Then run: python scripts/export_metrics.py")
    
    # Load and analyze tool metrics
    tool_df = load_metrics_csv(metrics_dir, "tool")
    if tool_df is not None and len(tool_df) > 0:
        print(f"\n--- Tool Performance ---")
        print(f"Total tool calls: {len(tool_df)}")
        
        tool_stats = analyze_tool_performance(tool_df, output_dir)
        if "calls_by_tool" in tool_stats:
            print("Calls by tool:", tool_stats["calls_by_tool"])
    
    # Load and analyze evaluation report (for confusion matrix)
    data_dir = Path(args.metrics_dir).parent.parent / "data"
    if not data_dir.exists():
        data_dir = project_root / "data"
    
    eval_report = load_evaluation_report(data_dir)
    if eval_report and not args.no_plots:
        print("\n--- Intent Classification Analysis ---")
        cm_stats = generate_confusion_matrix(eval_report, output_dir)
        if "intent_classification" in cm_stats:
            ic = cm_stats["intent_classification"]
            print(f"Intent Accuracy: {ic['accuracy']*100:.1f}%")
            print(f"Total samples: {ic['total_samples']}")
            print(f"Correct predictions: {ic['correct_predictions']}")
        if "search_relevance" in cm_stats:
            sr = cm_stats["search_relevance"]
            print(f"\nSearch Relevance - Mean: {sr['mean_score']}, Median: {sr['median_score']}")
        
        # Save confusion matrix stats
        cm_stats_path = output_dir / "confusion_matrix_stats.json"
        with open(cm_stats_path, "w", encoding="utf-8") as f:
            json.dump(cm_stats, f, indent=2, default=str)
        print(f"Confusion matrix stats saved to {cm_stats_path}")
    
    print("\n" + "=" * 50)
    print(f"Analysis complete. Results in: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    main()
