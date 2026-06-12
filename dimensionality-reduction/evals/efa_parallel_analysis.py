"""
EFA with Parallel Analysis for determining optimal number of factors.
"""

import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
import matplotlib.pyplot as plt
from typing import Tuple, Optional


def parallel_analysis(data: pd.DataFrame, n_factors_max: int = 10, n_resamples: int = 100) -> int:
    """
    Perform parallel analysis to determine the number of factors.

    Parallel analysis generates random data with the same structure as the real data,
    extracts eigenvalues from the random correlation matrix, and compares them to
    eigenvalues from the real data. Retain factors where real eigenvalues exceed
    the mean eigenvalues from random data (typically 95th percentile).

    Args:
        data: DataFrame of survey items (n_observations × n_items)
        n_factors_max: Maximum number of factors to test
        n_resamples: Number of random samples to generate

    Returns:
        Optimal number of factors
    """
    n_obs, n_vars = data.shape

    # Compute eigenvalues from real data
    corr_matrix = data.corr()
    real_eigenvalues = np.linalg.eigvalsh(corr_matrix)[::-1]

    # Simulate eigenvalues from random data
    random_eigenvalues = np.zeros((n_resamples, n_vars))
    for i in range(n_resamples):
        random_data = np.random.normal(0, 1, (n_obs, n_vars))
        random_corr = np.corrcoef(random_data.T)
        random_eigenvalues[i, :] = np.linalg.eigvalsh(random_corr)[::-1]

    # 95th percentile of random eigenvalues (threshold for retention)
    percentile_95 = np.percentile(random_eigenvalues, 95, axis=0)

    # Determine number of factors: where real > 95th percentile
    n_factors = np.sum(real_eigenvalues > percentile_95)

    # Plot the scree plot with parallel analysis overlay
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(real_eigenvalues) + 1), real_eigenvalues, 'bo-',
             label='Real Data', linewidth=2, markersize=8)
    plt.plot(range(1, len(percentile_95) + 1), percentile_95, 'r--',
             label='95th Percentile (Random)', linewidth=2)

    # Shade the area where factors are retained
    retained_range = min(n_factors, len(real_eigenvalues))
    if retained_range > 0:
        plt.axvline(x=retained_range + 0.5, color='green', linestyle=':', alpha=0.7,
                   label=f'Suggested cutoff: {n_factors} factors')

    plt.xlabel('Factor Number', fontsize=12)
    plt.ylabel('Eigenvalue', fontsize=12)
    plt.title('Parallel Analysis Scree Plot', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('parallel_analysis_scree.png', dpi=300)
    plt.show()

    print(f"\n=== Parallel Analysis Results ===")
    print(f"Optimal number of factors: {n_factors}")
    print(f"Real eigenvalues (first 10): {real_eigenvalues[:10].round(3)}")
    print(f"95th percentile (first 10): {percentile_95[:10].round(3)}")

    return n_factors


def fit_efa_with_parallel_analysis(data: pd.DataFrame,
                                   rotation: str = 'promax',
                                   n_factors: Optional[int] = None) -> Tuple[FactorAnalyzer, pd.DataFrame]:
    """
    Fit EFA on survey items with automatic factor determination via parallel analysis.

    Rotation choice explanation:
    - Promax (oblique): Assumes factors are correlated; more realistic for most
      psychological/behavioral constructs. Provides both pattern and structure loadings.
    - Varimax (orthogonal): Assumes factors are uncorrelated; easier interpretation
      but often unrealistic. Use only when constructs are truly independent.

    Args:
        data: DataFrame of survey items (observations × items)
        rotation: 'promax' (default, oblique) or 'varimax' (orthogonal)
        n_factors: If None, uses parallel analysis; otherwise uses specified number

    Returns:
        Tuple of (fitted FactorAnalyzer, DataFrame of loadings)
    """

    # Test assumptions
    print("\n=== Factorability Tests ===")

    # Bartlett's test (should be significant, p < 0.05)
    chi_square, p_value = calculate_bartlett_sphericity(data)
    print(f"Bartlett's Sphericity Test:")
    print(f"  χ² = {chi_square:.3f}, p = {p_value:.2e}")
    if p_value < 0.05:
        print("  ✓ Correlations significantly differ from identity matrix")
    else:
        print("  ✗ WARNING: Correlations may not be suitable for EFA")

    # KMO test (should be > 0.6, ideally > 0.7)
    kmo_overall, kmo_per_var = calculate_kmo(data)
    print(f"\nKaiser-Meyer-Olkin (KMO) Test:")
    print(f"  Overall KMO = {kmo_overall:.3f}")
    if kmo_overall >= 0.9:
        print("  ✓ Marvelous sampling adequacy")
    elif kmo_overall >= 0.8:
        print("  ✓ Meritorious sampling adequacy")
    elif kmo_overall >= 0.7:
        print("  ✓ Middling sampling adequacy")
    elif kmo_overall >= 0.6:
        print("  ✓ Mediocre sampling adequacy")
    else:
        print("  ✗ WARNING: Sampling adequacy is low")

    # Determine number of factors
    if n_factors is None:
        n_factors = parallel_analysis(data)
    else:
        print(f"\nUsing specified n_factors = {n_factors}")

    # Fit EFA with the determined number of factors
    print(f"\n=== Fitting EFA (n_factors={n_factors}, rotation='{rotation}') ===")

    fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method='minres')
    fa.fit(data)

    # Extract loadings
    loadings = fa.loadings_
    item_names = data.columns.tolist()

    loadings_df = pd.DataFrame(
        loadings,
        index=item_names,
        columns=[f'Factor {i+1}' for i in range(n_factors)]
    )

    print(f"\nVariance explained: {fa.get_factor_variance()[1].sum():.1%}")
    print(f"Per-factor variance: {fa.get_factor_variance()[1].round(3)}")

    return fa, loadings_df


def display_loadings(loadings_df: pd.DataFrame,
                     loading_threshold: float = 0.4,
                     sort_by_loading: bool = True) -> None:
    """
    Display and interpret factor loadings.

    Args:
        loadings_df: DataFrame of factor loadings
        loading_threshold: Highlight loadings above this threshold
        sort_by_loading: Sort items by highest loading per factor
    """
    print("\n=== Factor Loadings ===")
    print("(Loadings |exceeding threshold are bolded)")

    # Display raw loadings with formatting
    print("\nRaw Loadings:")
    display_loadings = loadings_df.copy()
    print(display_loadings.round(3).to_string())

    # Identify primary loadings (highest per item, exceeding threshold)
    print("\n\nPrimary Factor Assignments:")
    primary_factor = loadings_df.abs().idxmax(axis=1)
    primary_loading = loadings_df.abs().max(axis=1)

    assignment_df = pd.DataFrame({
        'Item': loadings_df.index,
        'Primary Factor': primary_factor,
        'Loading': [loadings_df.loc[item, primary_factor[item]]
                   for item in loadings_df.index],
        'Strength': primary_loading
    })

    # Filter to items with loadings above threshold
    strong_items = assignment_df[assignment_df['Strength'] >= loading_threshold]
    print(strong_items.to_string(index=False))

    # Flag items with weak loadings or cross-loading
    weak_items = assignment_df[assignment_df['Strength'] < loading_threshold]
    if len(weak_items) > 0:
        print(f"\n⚠ Weak Items (loading < {loading_threshold}):")
        print(weak_items[['Item', 'Strength']].to_string(index=False))

    # Check for cross-loading (>2 factors with substantial loading)
    print("\n\nCross-Loading Check:")
    cross_loads = (loadings_df.abs() >= loading_threshold).sum(axis=1)
    cross_loaded_items = cross_loads[cross_loads > 1]

    if len(cross_loaded_items) > 0:
        print(f"Items loading on {loading_threshold} or more factors:")
        for item in cross_loaded_items.index:
            factors = loadings_df.columns[loadings_df.loc[item].abs() >= loading_threshold].tolist()
            print(f"  {item}: {factors}")
    else:
        print(f"✓ No items with cross-loading above {loading_threshold} threshold")

    return assignment_df


def rotation_comparison(data: pd.DataFrame, n_factors: int) -> None:
    """
    Compare orthogonal (Varimax) and oblique (Promax) rotations.
    """
    print("\n" + "="*70)
    print("ROTATION CHOICE: PROMAX vs VARIMAX")
    print("="*70)

    print("""
PROMAX (Oblique Rotation) — RECOMMENDED
  • Assumes factors ARE correlated
  • Produces pattern & structure loadings (pattern is for interpretation)
  • Better reflects real-world psychological/behavioral constructs
  • More complex interpretation but more realistic

VARIMAX (Orthogonal Rotation)
  • Assumes factors are UNCORRELATED
  • Simpler interpretation (one set of loadings)
  • Unrealistic for most behavioral data
  • Use only when constructs are truly independent

DEFAULT CHOICE: Promax
  Most survey/psychological data have correlated factors. Use Promax unless
  you have strong theoretical reasons to believe factors are independent.
""")

    print("\nComparing both on your data:")

    for rot in ['varimax', 'promax']:
        fa = FactorAnalyzer(n_factors=n_factors, rotation=rot, method='minres')
        fa.fit(data)
        variance = fa.get_factor_variance()[1].sum()
        print(f"  {rot.capitalize():8} → Cumulative variance: {variance:.1%}")


# Example usage
if __name__ == "__main__":
    # Create synthetic survey data (20 items, 500 respondents)
    np.random.seed(42)
    n_respondents = 500

    # Generate latent factors
    factor1 = np.random.normal(0, 1, n_respondents)
    factor2 = np.random.normal(0, 1, n_respondents)

    # Create items loading on these factors
    items = pd.DataFrame({
        'item_1': 0.8 * factor1 + 0.2 * np.random.normal(0, 1, n_respondents),
        'item_2': 0.75 * factor1 + 0.25 * np.random.normal(0, 1, n_respondents),
        'item_3': 0.82 * factor1 + 0.18 * np.random.normal(0, 1, n_respondents),
        'item_4': 0.9 * factor2 + 0.1 * np.random.normal(0, 1, n_respondents),
        'item_5': 0.85 * factor2 + 0.15 * np.random.normal(0, 1, n_respondents),
        'item_6': 0.88 * factor2 + 0.12 * np.random.normal(0, 1, n_respondents),
        'item_7': 0.7 * factor1 + 0.3 * np.random.normal(0, 1, n_respondents),
        'item_8': 0.72 * factor2 + 0.28 * np.random.normal(0, 1, n_respondents),
    })

    # Standardize
    items = (items - items.mean()) / items.std()

    # Run the analysis
    fa, loadings = fit_efa_with_parallel_analysis(items, rotation='promax')
    assignment_df = display_loadings(loadings, loading_threshold=0.4)
    rotation_comparison(items, n_factors=2)

    print("\n✓ Analysis complete. Scree plot saved as 'parallel_analysis_scree.png'")
