"""
Generate Figure 4 for thesis paper with latest evaluation data.
Figure 4a: Summary Metrics per Pipeline (bar chart)
Figure 4b: Confusion Matrix - Vector
Figure 4c: Confusion Matrix - API
Figure 4d: Confusion Matrix - Hybrid
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

# Output directory
OUTPUT_DIR = Path("d:/Project/Rag-Tesis/docs/paper-html")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Data from latest evaluation (26 Jan 2026)
metrics_data = {
    'Mean CPR': [0.5533, 0.7335, 0.9761],
    'Strict Success': [0.3304, 0.7262, 0.9662],
    'CPR': [0.5533, 0.7335, 0.9761],
    'NR Score': [1.0, 1.0, 1.0],
    'Accuracy': [0.5667, 0.7333, 1.0],
}

# Confusion matrix data
cm_vector = np.array([[2, 0], [13, 15]])   # TN=2, FP=0, FN=13, TP=15
cm_api = np.array([[2, 0], [8, 20]])       # TN=2, FP=0, FN=8, TP=20
cm_hybrid = np.array([[2, 0], [0, 28]])    # TN=2, FP=0, FN=0, TP=28

pipelines = ['Vector', 'API', 'Hybrid']
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green

def generate_figure_4a():
    """Generate bar chart comparing metrics across pipelines."""
    fig, ax = plt.subplots(figsize=(10, 6))

    metrics = ['Mean CPR', 'Strict Success', 'NR Score', 'Accuracy']
    x = np.arange(len(metrics))
    width = 0.25

    values_vector = [metrics_data[m][0] for m in metrics]
    values_api = [metrics_data[m][1] for m in metrics]
    values_hybrid = [metrics_data[m][2] for m in metrics]

    bars1 = ax.bar(x - width, values_vector, width, label='Vector', color=colors[0])
    bars2 = ax.bar(x, values_api, width, label='API', color=colors[1])
    bars3 = ax.bar(x + width, values_hybrid, width, label='Hybrid', color=colors[2])

    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Summary Metrics per Pipeline', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11)
    ax.legend(loc='upper left', fontsize=11)
    ax.set_ylim(0, 1.15)
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_4a_summary_metrics.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / 'figure_4a_summary_metrics.png'}")

def generate_confusion_matrix(cm, title, filename, cmap='YlGnBu'):
    """Generate a single confusion matrix heatmap."""
    fig, ax = plt.subplots(figsize=(6, 5))

    # Calculate metrics
    tn, fp, fn, tp = cm[0,0], cm[0,1], cm[1,0], cm[1,1]
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    sns.heatmap(cm, annot=True, fmt='d', cmap=cmap,
                xticklabels=['Negative', 'Positive'],
                yticklabels=['Negative', 'Positive'],
                annot_kws={'size': 16},
                cbar=False, ax=ax)

    ax.set_xlabel('Predicted Label', fontsize=12)
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_title(f'{title}\nAcc={accuracy:.1%}, Prec={precision:.1%}, Rec={recall:.1%}', fontsize=12)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / filename}")

def generate_combined_figure():
    """Generate combined 2x2 figure with all confusion matrices."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Figure 4a - Summary metrics (top-left)
    ax = axes[0, 0]
    metrics = ['Mean CPR', 'Strict', 'NR', 'Acc']
    x = np.arange(len(metrics))
    width = 0.25

    values_vector = [0.5533, 0.3304, 1.0, 0.5667]
    values_api = [0.7335, 0.7262, 1.0, 0.7333]
    values_hybrid = [0.9761, 0.9662, 1.0, 1.0]

    ax.bar(x - width, values_vector, width, label='Vector', color=colors[0])
    ax.bar(x, values_api, width, label='API', color=colors[1])
    ax.bar(x + width, values_hybrid, width, label='Hybrid', color=colors[2])

    ax.set_ylabel('Score')
    ax.set_title('(a) Summary Metrics per Pipeline')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 1.15)
    ax.grid(axis='y', alpha=0.3)

    # Confusion matrices
    cms = [
        (cm_vector, '(b) Confusion Matrix - Vector', axes[0, 1]),
        (cm_api, '(c) Confusion Matrix - API', axes[1, 0]),
        (cm_hybrid, '(d) Confusion Matrix - Hybrid', axes[1, 1]),
    ]

    for cm, title, ax in cms:
        tn, fp, fn, tp = cm[0,0], cm[0,1], cm[1,0], cm[1,1]
        accuracy = (tp + tn) / (tp + tn + fp + fn)

        sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu',
                   xticklabels=['Neg', 'Pos'],
                   yticklabels=['Neg', 'Pos'],
                   annot_kws={'size': 14},
                   cbar=False, ax=ax)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title(f'{title} (Acc={accuracy:.1%})')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'figure_4_combined.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / 'figure_4_combined.png'}")

if __name__ == '__main__':
    print("Generating Figure 4 for thesis paper...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Generate individual figures
    generate_figure_4a()
    generate_confusion_matrix(cm_vector, 'Confusion Matrix - Vector', 'figure_4b_cm_vector.png')
    generate_confusion_matrix(cm_api, 'Confusion Matrix - API', 'figure_4c_cm_api.png')
    generate_confusion_matrix(cm_hybrid, 'Confusion Matrix - Hybrid', 'figure_4d_cm_hybrid.png')

    # Generate combined figure
    generate_combined_figure()

    print()
    print("All figures generated successfully!")
