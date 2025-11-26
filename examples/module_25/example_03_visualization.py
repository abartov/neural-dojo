#!/usr/bin/env python3
"""
Module 25 Example 3: Data Visualization

Demonstrates matplotlib and seaborn for creating
publication-quality visualizations for ML analysis.

Visualization is how you understand your data before training models.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Create output directory for saved plots
OUTPUT_DIR = Path(__file__).parent / "plots"
OUTPUT_DIR.mkdir(exist_ok=True)


# =============================================================================
# Part 1: matplotlib Basics
# =============================================================================

def demo_matplotlib_basics():
    """Demonstrate basic matplotlib plotting."""
    print("\n" + "="*60)
    print("Part 1: matplotlib Basics")
    print("="*60)

    # Simple line plot
    print("\n--- Line Plot ---")
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x, y1, 'b-', label='sin(x)', linewidth=2)
    ax.plot(x, y2, 'r--', label='cos(x)', linewidth=2)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title('Trigonometric Functions', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '01_line_plot.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/01_line_plot.png")

    # Scatter plot
    print("\n--- Scatter Plot ---")
    np.random.seed(42)
    n = 100
    x = np.random.randn(n)
    y = x + np.random.randn(n) * 0.5
    colors = np.random.rand(n)
    sizes = np.abs(np.random.randn(n)) * 200

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(x, y, c=colors, s=sizes, alpha=0.6, cmap='viridis')
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    ax.set_title('Scatter Plot with Color and Size', fontsize=14)
    plt.colorbar(scatter, label='Color Value')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '02_scatter_plot.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/02_scatter_plot.png")

    # Bar chart
    print("\n--- Bar Chart ---")
    categories = ['Category A', 'Category B', 'Category C', 'Category D', 'Category E']
    values = [23, 45, 56, 78, 32]
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(categories)))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, values, color=colors, edgecolor='black')
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title('Bar Chart', fontsize=14)

    # Add value labels on bars
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                str(value), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '03_bar_chart.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/03_bar_chart.png")

    # Histogram
    print("\n--- Histogram ---")
    data = np.random.randn(1000)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(data, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.2f}')
    ax.axvline(np.median(data), color='green', linestyle=':', linewidth=2, label=f'Median: {np.median(data):.2f}')
    ax.set_xlabel('Value', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Histogram of Normal Distribution', fontsize=14)
    ax.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '04_histogram.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/04_histogram.png")


# =============================================================================
# Part 2: Subplots and Multiple Plots
# =============================================================================

def demo_subplots():
    """Demonstrate creating multiple subplots."""
    print("\n" + "="*60)
    print("Part 2: Subplots and Multiple Plots")
    print("="*60)

    np.random.seed(42)

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Top-left: Line plot
    x = np.linspace(0, 10, 100)
    axes[0, 0].plot(x, np.sin(x), 'b-', label='sin(x)')
    axes[0, 0].plot(x, np.cos(x), 'r--', label='cos(x)')
    axes[0, 0].set_title('Line Plot')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Top-right: Scatter plot
    axes[0, 1].scatter(np.random.rand(50), np.random.rand(50),
                       c=np.random.rand(50), s=np.random.rand(50)*500,
                       alpha=0.6, cmap='viridis')
    axes[0, 1].set_title('Scatter Plot')

    # Bottom-left: Bar plot
    categories = ['A', 'B', 'C', 'D', 'E']
    values = np.random.randint(10, 50, 5)
    axes[1, 0].bar(categories, values, color='steelblue', edgecolor='black')
    axes[1, 0].set_title('Bar Chart')

    # Bottom-right: Histogram
    data = np.random.randn(1000)
    axes[1, 1].hist(data, bins=30, edgecolor='black', alpha=0.7)
    axes[1, 1].set_title('Histogram')

    plt.suptitle('Multiple Subplots Example', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '05_subplots.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/05_subplots.png")


# =============================================================================
# Part 3: seaborn Statistical Visualizations
# =============================================================================

def demo_seaborn_basics():
    """Demonstrate seaborn's statistical visualization capabilities."""
    print("\n" + "="*60)
    print("Part 3: seaborn Statistical Visualizations")
    print("="*60)

    # Set seaborn style
    sns.set_theme(style='whitegrid')

    # Create sample dataset
    np.random.seed(42)
    n = 200
    df = pd.DataFrame({
        'feature_1': np.random.randn(n),
        'feature_2': np.random.randn(n) * 2 + 1,
        'category': np.random.choice(['A', 'B', 'C'], n),
        'target': np.random.choice([0, 1], n)
    })
    df['feature_2'] = df['feature_2'] + df['feature_1'] * 0.5  # Add correlation

    # Distribution plot
    print("\n--- Distribution Plot ---")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.histplot(df['feature_1'], kde=True, ax=axes[0], color='steelblue')
    axes[0].set_title('Distribution with KDE')

    sns.kdeplot(data=df, x='feature_1', hue='category', ax=axes[1])
    axes[1].set_title('KDE by Category')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '06_distribution.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/06_distribution.png")

    # Box and Violin plots
    print("\n--- Box and Violin Plots ---")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.boxplot(x='category', y='feature_1', data=df, ax=axes[0], palette='Set2')
    axes[0].set_title('Box Plot by Category')

    sns.violinplot(x='category', y='feature_1', data=df, ax=axes[1], palette='Set2')
    axes[1].set_title('Violin Plot by Category')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '07_box_violin.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/07_box_violin.png")

    # Scatter with regression
    print("\n--- Scatter with Regression ---")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.scatterplot(x='feature_1', y='feature_2', hue='category', data=df, ax=axes[0])
    axes[0].set_title('Scatter by Category')

    sns.regplot(x='feature_1', y='feature_2', data=df, ax=axes[1],
                scatter_kws={'alpha': 0.5}, line_kws={'color': 'red'})
    axes[1].set_title('Scatter with Regression Line')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '08_scatter_regression.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/08_scatter_regression.png")


# =============================================================================
# Part 4: Correlation Heatmaps
# =============================================================================

def demo_heatmaps():
    """Demonstrate heatmaps for correlation analysis."""
    print("\n" + "="*60)
    print("Part 4: Correlation Heatmaps")
    print("="*60)

    # Create dataset with correlations
    np.random.seed(42)
    n = 500

    df = pd.DataFrame({
        'feature_1': np.random.randn(n),
        'feature_2': np.random.randn(n),
        'feature_3': np.random.randn(n),
    })

    # Add correlations
    df['feature_4'] = df['feature_1'] * 0.8 + np.random.randn(n) * 0.2
    df['feature_5'] = -df['feature_2'] * 0.6 + np.random.randn(n) * 0.4
    df['feature_6'] = df['feature_3'] + df['feature_1'] * 0.3 + np.random.randn(n) * 0.5
    df['target'] = (df['feature_1'] + df['feature_4'] > 0).astype(int)

    # Calculate correlation matrix
    corr = df.corr()

    # Heatmap
    print("\n--- Correlation Heatmap ---")
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, ax=ax,
                cbar_kws={'shrink': 0.8})
    ax.set_title('Feature Correlation Matrix', fontsize=14)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '09_correlation_heatmap.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/09_correlation_heatmap.png")

    # Masked heatmap (show only lower triangle)
    print("\n--- Masked Correlation Heatmap ---")
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, square=True, linewidths=0.5, ax=ax)
    ax.set_title('Correlation Matrix (Lower Triangle)', fontsize=14)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '10_correlation_masked.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/10_correlation_masked.png")


# =============================================================================
# Part 5: Pair Plots for Feature Exploration
# =============================================================================

def demo_pair_plots():
    """Demonstrate pair plots for exploratory data analysis."""
    print("\n" + "="*60)
    print("Part 5: Pair Plots for Feature Exploration")
    print("="*60)

    # Create sample classification dataset
    np.random.seed(42)
    n = 150

    # Class 0
    class0 = pd.DataFrame({
        'feature_1': np.random.normal(0, 1, n // 2),
        'feature_2': np.random.normal(0, 1, n // 2),
        'feature_3': np.random.normal(2, 1, n // 2),
        'class': 0
    })

    # Class 1
    class1 = pd.DataFrame({
        'feature_1': np.random.normal(2, 1, n // 2),
        'feature_2': np.random.normal(2, 1, n // 2),
        'feature_3': np.random.normal(0, 1, n // 2),
        'class': 1
    })

    df = pd.concat([class0, class1], ignore_index=True)
    df['class'] = df['class'].astype('category')

    # Pair plot
    print("\n--- Pair Plot ---")
    g = sns.pairplot(df, hue='class', diag_kind='kde',
                     plot_kws={'alpha': 0.6},
                     palette='Set1')
    g.fig.suptitle('Pair Plot: Feature Relationships by Class', y=1.02)

    plt.savefig(OUTPUT_DIR / '11_pair_plot.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/11_pair_plot.png")


# =============================================================================
# Part 6: ML-Specific Visualizations
# =============================================================================

def demo_ml_visualizations():
    """Demonstrate visualizations commonly used in ML."""
    print("\n" + "="*60)
    print("Part 6: ML-Specific Visualizations")
    print("="*60)

    np.random.seed(42)

    # Create training history data (simulated)
    epochs = np.arange(1, 51)
    train_loss = 2.5 * np.exp(-epochs/15) + 0.2 + np.random.randn(50) * 0.05
    val_loss = 2.5 * np.exp(-epochs/15) + 0.3 + np.random.randn(50) * 0.1
    train_acc = 1 - train_loss / 3
    val_acc = 1 - val_loss / 3

    # Training curves
    print("\n--- Training Curves ---")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Loss curves
    axes[0].plot(epochs, train_loss, 'b-', label='Training Loss', linewidth=2)
    axes[0].plot(epochs, val_loss, 'r-', label='Validation Loss', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Loss', fontsize=12)
    axes[0].set_title('Training and Validation Loss', fontsize=14)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Accuracy curves
    axes[1].plot(epochs, train_acc, 'b-', label='Training Accuracy', linewidth=2)
    axes[1].plot(epochs, val_acc, 'r-', label='Validation Accuracy', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Accuracy', fontsize=12)
    axes[1].set_title('Training and Validation Accuracy', fontsize=14)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '12_training_curves.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/12_training_curves.png")

    # Confusion matrix
    print("\n--- Confusion Matrix ---")
    from sklearn.metrics import confusion_matrix

    # Simulated predictions
    y_true = np.random.choice([0, 1, 2], 100)
    y_pred = y_true.copy()
    # Add some errors
    noise_idx = np.random.choice(100, 20, replace=False)
    y_pred[noise_idx] = np.random.choice([0, 1, 2], 20)

    cm = confusion_matrix(y_true, y_pred)
    labels = ['Class 0', 'Class 1', 'Class 2']

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=labels, yticklabels=labels)
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('True', fontsize=12)
    ax.set_title('Confusion Matrix', fontsize=14)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '13_confusion_matrix.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/13_confusion_matrix.png")

    # Feature importance
    print("\n--- Feature Importance ---")
    features = ['feature_1', 'feature_2', 'feature_3', 'feature_4',
                'feature_5', 'feature_6', 'feature_7', 'feature_8']
    importances = np.random.rand(8)
    importances = importances / importances.sum()  # Normalize
    importances.sort()

    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(features))
    ax.barh(y_pos, importances, color='steelblue', edgecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features)
    ax.set_xlabel('Importance', fontsize=12)
    ax.set_title('Feature Importance', fontsize=14)

    # Add value labels
    for i, v in enumerate(importances):
        ax.text(v + 0.01, i, f'{v:.2%}', va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '14_feature_importance.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/14_feature_importance.png")

    # ROC Curve
    print("\n--- ROC Curve ---")
    from sklearn.metrics import roc_curve, auc

    # Simulated probabilities
    y_true_binary = np.random.choice([0, 1], 200)
    y_prob = np.random.beta(2, 5, 200)  # Skewed probabilities
    y_prob[y_true_binary == 1] += 0.3
    y_prob = np.clip(y_prob, 0, 1)

    fpr, tpr, _ = roc_curve(y_true_binary, y_prob)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, 'b-', linewidth=2, label=f'ROC (AUC = {roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
    ax.fill_between(fpr, tpr, alpha=0.2)
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=14)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '15_roc_curve.png', dpi=150)
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/15_roc_curve.png")


# =============================================================================
# Part 7: EDA Dashboard
# =============================================================================

def demo_eda_dashboard():
    """Create a comprehensive EDA dashboard."""
    print("\n" + "="*60)
    print("Part 7: EDA Dashboard")
    print("="*60)

    # Create realistic dataset
    np.random.seed(42)
    n = 500

    df = pd.DataFrame({
        'age': np.random.normal(35, 10, n).clip(18, 70).astype(int),
        'income': np.random.lognormal(10.5, 0.5, n),
        'credit_score': np.random.normal(650, 100, n).clip(300, 850).astype(int),
        'num_products': np.random.poisson(2, n),
        'tenure_months': np.random.exponential(30, n).clip(1, 120).astype(int),
        'is_active': np.random.choice([0, 1], n, p=[0.3, 0.7]),
        'churned': np.random.choice([0, 1], n, p=[0.8, 0.2])
    })

    # Make churned correlate with some features
    churn_prob = 0.1 + 0.2 * (df['age'] < 25) + 0.1 * (df['credit_score'] < 600)
    df['churned'] = (np.random.rand(n) < churn_prob).astype(int)

    print(f"Dataset shape: {df.shape}")
    print(f"Target distribution: {df['churned'].value_counts().to_dict()}")

    # Create dashboard
    fig = plt.figure(figsize=(16, 12))

    # 1. Target distribution
    ax1 = fig.add_subplot(2, 3, 1)
    df['churned'].value_counts().plot(kind='pie', ax=ax1, autopct='%1.1f%%',
                                       colors=['#2ecc71', '#e74c3c'],
                                       labels=['Retained', 'Churned'])
    ax1.set_title('Target Distribution', fontsize=12, fontweight='bold')
    ax1.set_ylabel('')

    # 2. Age distribution by churn
    ax2 = fig.add_subplot(2, 3, 2)
    sns.boxplot(x='churned', y='age', data=df, ax=ax2, palette=['#2ecc71', '#e74c3c'])
    ax2.set_xticklabels(['Retained', 'Churned'])
    ax2.set_title('Age by Churn Status', fontsize=12, fontweight='bold')

    # 3. Credit score distribution
    ax3 = fig.add_subplot(2, 3, 3)
    sns.histplot(data=df, x='credit_score', hue='churned', kde=True, ax=ax3,
                 palette=['#2ecc71', '#e74c3c'])
    ax3.set_title('Credit Score Distribution', fontsize=12, fontweight='bold')
    ax3.legend(['Retained', 'Churned'])

    # 4. Correlation heatmap
    ax4 = fig.add_subplot(2, 3, 4)
    corr = df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, ax=ax4, cbar_kws={'shrink': 0.8})
    ax4.set_title('Feature Correlations', fontsize=12, fontweight='bold')

    # 5. Income vs Credit Score
    ax5 = fig.add_subplot(2, 3, 5)
    sns.scatterplot(data=df, x='income', y='credit_score', hue='churned',
                    ax=ax5, palette=['#2ecc71', '#e74c3c'], alpha=0.6)
    ax5.set_title('Income vs Credit Score', fontsize=12, fontweight='bold')

    # 6. Feature distributions
    ax6 = fig.add_subplot(2, 3, 6)
    df_numeric = df.select_dtypes(include=[np.number]).drop(columns=['churned'])
    df_scaled = (df_numeric - df_numeric.mean()) / df_numeric.std()
    df_scaled.boxplot(ax=ax6)
    ax6.set_title('Feature Distributions (Z-scores)', fontsize=12, fontweight='bold')
    ax6.tick_params(axis='x', rotation=45)

    plt.suptitle('Exploratory Data Analysis Dashboard', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '16_eda_dashboard.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR}/16_eda_dashboard.png")


# =============================================================================
# Main Execution
# =============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Module 25: Data Visualization")
    print("matplotlib and seaborn for ML Analysis")
    print("="*60)

    # Check for required packages
    try:
        from sklearn.metrics import confusion_matrix, roc_curve, auc
    except ImportError:
        print("\nNote: sklearn not found. Some visualizations will be skipped.")
        print("Install with: pip install scikit-learn")

    # Run all demonstrations
    demo_matplotlib_basics()
    demo_subplots()
    demo_seaborn_basics()
    demo_heatmaps()
    demo_pair_plots()
    demo_ml_visualizations()
    demo_eda_dashboard()

    print("\n" + "="*60)
    print("Visualization Examples Complete!")
    print("="*60)
    print(f"""
All plots saved to: {OUTPUT_DIR.absolute()}

Generated plots:
1. Line plot (trigonometric functions)
2. Scatter plot with color and size
3. Bar chart with labels
4. Histogram with statistics
5. Subplots (2x2 grid)
6. Distribution plots with KDE
7. Box and violin plots
8. Scatter with regression
9. Correlation heatmap
10. Masked correlation heatmap
11. Pair plot for EDA
12. Training curves (loss and accuracy)
13. Confusion matrix
14. Feature importance
15. ROC curve
16. EDA dashboard

Key Takeaways:
1. matplotlib provides low-level control
2. seaborn simplifies statistical visualizations
3. Always visualize before modeling
4. Use appropriate plots for different data types
5. Color-blind friendly palettes matter!

Next: Build the ML Data Toolkit deliverable!
    """)
