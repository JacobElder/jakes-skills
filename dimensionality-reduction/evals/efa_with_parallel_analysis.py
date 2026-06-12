"""
EFA with Parallel Analysis for determining the number of factors.

Key principles:
  - Factorability checks (KMO & Bartlett's test) before analysis
  - Parallel analysis (not Kaiser eigenvalue > 1) to retain factors
  - Maximum likelihood or PAF extraction (not PCA)
  - Oblique rotation by default (factors usually correlate in practice)
  - Interpretation with communality & cross-loading flags
"""

import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity, calculate_kmo
from typing import Dict, Tuple, Any


def fit_efa_with_parallel_analysis(
    df: pd.DataFrame,
    n_factors: int = None,
    extraction: str = "ml",
    rotation: str = "oblimin",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Fit EFA on survey items with parallel analysis to determine optimal n_factors.

    Args:
        df: DataFrame of survey items (rows=respondents, cols=items).
        n_factors: Number of factors to extract. If None, determined by parallel analysis.
        extraction: 'ml' (maximum likelihood, default) or 'minres' (minimum residual/PAF).
                   Use ML if data ~normal and you want fit statistics; minres if non-normal.
        rotation: 'oblimin' (default, oblique) or 'varimax'/'quartimin' (orthogonal).
                 Use oblique when factors are expected to correlate (typical in social science).
        verbose: Print diagnostics and interpretation.

    Returns:
        Dictionary with:
            - 'kmo': KMO sampling adequacy
            - 'bartlett_pval': Bartlett's sphericity test p-value
            - 'n_factors': Number of factors extracted
            - 'loadings': DataFrame of factor loadings (rows=items, cols=factors)
            - 'communalities': Item communalities (variance explained by factors)
            - 'variance_explained': Proportion of total variance by each factor
            - 'factor_correlations': Correlation matrix of factors (if oblique rotation)
            - 'eigenvalues': Eigenvalues from the correlation matrix
    """

    # Step 1: Check factorability
    if verbose:
        print("=" * 75)
        print("STEP 1: FACTORABILITY CHECKS")
        print("=" * 75)

    corr_matrix = df.corr()

    # Kaiser-Meyer-Olkin (KMO) sampling adequacy
    kmo_all, kmo_model = calculate_kmo(df)
    if verbose:
        print(f"\nKaiser-Meyer-Olkin (KMO) Overall: {kmo_model:.3f}")
        print("  Benchmarks: ≥0.9 Marvelous | 0.8–0.9 Meritorious | 0.7–0.8 Middling")
        print("              0.6–0.7 Mediocre | 0.5–0.6 Miserable | <0.5 Unacceptable")

    # Bartlett's test of sphericity
    chi_sq, bartlett_pval = calculate_bartlett_sphericity(df)
    if verbose:
        print(f"\nBartlett's Test of Sphericity: χ² = {chi_sq:.2f}, p = {bartlett_pval:.2e}")
        if bartlett_pval < 0.05:
            print("  ✓ Significant (p < 0.05): correlations differ from identity → good")
        else:
            print("  ✗ Not significant: items may be too independent to factor")

    # Step 2: Determine number of factors via parallel analysis
    if n_factors is None:
        if verbose:
            print("\n" + "=" * 75)
            print("STEP 2: PARALLEL ANALYSIS (determining optimal n_factors)")
            print("=" * 75)
        n_factors, pa_info = _parallel_analysis(corr_matrix, df.shape[0], verbose=verbose)
    else:
        pa_info = {"method": "manual"}

    # Step 3: Fit EFA
    if verbose:
        print("\n" + "=" * 75)
        print(f"STEP 3: FITTING EFA ({extraction.upper()}, {rotation} rotation)")
        print("=" * 75)

    fa = FactorAnalyzer(
        n_factors=n_factors,
        rotation=rotation,
        method=extraction,
        use_smc=True,
    )
    fa.fit(df)

    # Extract results
    loadings_raw = fa.loadings_
    communalities = fa.get_communalities()
    variance_list = fa.get_factor_variance()

    loadings_df = pd.DataFrame(
        loadings_raw,
        index=df.columns,
        columns=[f"F{i+1}" for i in range(n_factors)],
    )

    results = {
        "kmo": kmo_model,
        "bartlett_pval": bartlett_pval,
        "n_factors": n_factors,
        "loadings": loadings_df,
        "communalities": pd.Series(communalities, index=df.columns),
        "variance_explained": variance_list[1],
        "eigenvalues": variance_list[0],
        "parallel_analysis": pa_info,
        "rotation": rotation,
        "extraction": extraction,
        "fa_object": fa,
    }

    # Factor correlations if oblique rotation
    if rotation in ["oblimin", "promax", "quartimin"]:
        try:
            results["factor_correlations"] = pd.DataFrame(
                fa.factor_correlations(),
                index=[f"F{i+1}" for i in range(n_factors)],
                columns=[f"F{i+1}" for i in range(n_factors)],
            )
        except Exception:
            results["factor_correlations"] = None

    # Step 4: Display results
    if verbose:
        print("\nFACTOR LOADINGS (rotated):")
        print("-" * 75)
        print(loadings_df.round(3).to_string())

        print("\n\nCOMMUNALITIES (variance in each item explained by the factors):")
        print("-" * 75)
        comm_df = pd.DataFrame({
            "Item": df.columns,
            "Communality": communalities,
        }).set_index("Item")
        print(comm_df.round(3).to_string())
        print("  Note: <0.20 indicates weak items; >0.40 is typical")

        print(f"\n\nVARIANCE EXPLAINED BY EACH FACTOR:")
        print("-" * 75)
        for i, var in enumerate(results["variance_explained"]):
            print(f"  F{i+1}: {var*100:.1f}%")
        print(f"  Total: {results['variance_explained'].sum()*100:.1f}%")

        if results["factor_correlations"] is not None:
            print(f"\n\nFACTOR INTER-CORRELATIONS ({rotation.upper()} rotation):")
            print("-" * 75)
            print(results["factor_correlations"].round(3).to_string())

        _print_interpretation(results)

    return results


def _parallel_analysis(
    corr_matrix: pd.DataFrame, n_obs: int, verbose: bool = True
) -> Tuple[int, Dict]:
    """Parallel analysis: compare observed eigenvalues to random-data eigenvalues."""
    n_vars = corr_matrix.shape[0]

    # Observed eigenvalues
    eigenvalues_obs, _ = np.linalg.eig(corr_matrix)
    eigenvalues_obs = np.sort(eigenvalues_obs)[::-1]

    # Random eigenvalues (100 permutations)
    n_perm = 100
    random_eigs = []
    np.random.seed(42)

    for _ in range(n_perm):
        random_data = np.random.randn(n_obs, n_vars)
        random_corr = np.corrcoef(random_data.T)
        eigs, _ = np.linalg.eig(random_corr)
        random_eigs.append(np.sort(eigs)[::-1])

    random_eigs = np.array(random_eigs)
    mean_random = random_eigs.mean(axis=0)
    ci_95_random = np.percentile(random_eigs, 95, axis=0)

    # Keep factors where observed > 95% CI of random
    n_factors = np.sum(eigenvalues_obs > ci_95_random)
    n_factors = max(1, n_factors)

    if verbose:
        print("\nParallel Analysis Results (first 10 factors):")
        print("-" * 75)
        print(f"{'#':<3} {'Observed':<12} {'Random Mean':<15} {'95% CI':<12} {'Keep?':<10}")
        print("-" * 75)
        for i in range(min(10, len(eigenvalues_obs))):
            keep = "✓" if eigenvalues_obs[i] > ci_95_random[i] else "✗"
            print(f"{i+1:<3} {eigenvalues_obs[i]:<12.3f} {mean_random[i]:<15.3f} "
                  f"{ci_95_random[i]:<12.3f} {keep:<10}")
        print("-" * 75)
        print(f"\n→ Retain {n_factors} factor(s) (observed > 95% CI of random)\n")

    pa_info = {
        "method": "parallel_analysis",
        "n_factors": n_factors,
        "eigenvalues_observed": eigenvalues_obs,
        "eigenvalues_random_mean": mean_random,
    }

    return n_factors, pa_info


def _print_interpretation(results: Dict) -> None:
    """Print interpretation guidance."""
    print("\n" + "=" * 75)
    print("INTERPRETATION & NEXT STEPS")
    print("=" * 75)

    print(f"\n1. ROTATION CHOICE: {results['rotation'].upper()}")
    if results["rotation"] in ["oblimin", "promax"]:
        print("   Oblique rotation — assumes factors MAY correlate")
        print("   → Realistic in social science (constructs often covary)")
        print("   → Reports factor inter-correlations as additional information")
        if results["factor_correlations"] is not None:
            max_corr = np.abs(
                results["factor_correlations"].values[
                    np.triu_indices_from(results["factor_correlations"].values, k=1)
                ]
            ).max()
            print(f"   → Observed max inter-factor correlation: {max_corr:.2f}")
            if max_corr < 0.3:
                print("      (Weak; consider orthogonal/varimax if independence is assumed)")
    else:
        print("   Orthogonal rotation — assumes factors are independent")
        print("   → Only use if theory strongly supports independence")

    print(f"\n2. READING THE LOADINGS")
    print("   • Loadings > |0.40| = strong item-factor association")
    print("   • Flag cross-loadings (item loads >0.30 on multiple factors)")
    print("   • Name factors from high-loading items (theory-informed)")
    print("   • Weak items (communality <0.20) may need revision")

    print(f"\n3. VALIDATION")
    print("   • NEVER run CFA on this same sample (circular confirmation)")
    print("   • Collect new data, then specify model structure and fit CFA")
    print("   • Report CFI ≥0.95, RMSEA ≤0.06, SRMR ≤0.08 for good fit")

    print()


if __name__ == "__main__":
    # Example: Simulate 3-factor survey structure (40 respondents, 12 Likert items)
    np.random.seed(42)

    f1 = np.random.normal(0, 1, 40)
    f2 = np.random.normal(0, 1, 40)
    f3 = np.random.normal(0, 1, 40)

    # Items loading on factors with noise
    noise = np.random.normal(0, 0.3, (40, 12))
    items = np.column_stack([
        0.9*f1 + 0.1*f2 + noise[:, 0],  # Items 1-4 load on F1
        0.85*f1 + 0.15*f2 + noise[:, 1],
        0.8*f1 + 0.2*f2 + noise[:, 2],
        0.75*f1 + 0.25*f3 + noise[:, 3],
        0.9*f2 + 0.1*f1 + noise[:, 4],  # Items 5-8 load on F2
        0.85*f2 + 0.15*f3 + noise[:, 5],
        0.8*f2 + 0.2*f3 + noise[:, 6],
        0.75*f2 + 0.25*f1 + noise[:, 7],
        0.9*f3 + 0.1*f1 + noise[:, 8],  # Items 9-12 load on F3
        0.85*f3 + 0.15*f2 + noise[:, 9],
        0.8*f3 + 0.2*f1 + noise[:, 10],
        0.75*f3 + 0.25*f2 + noise[:, 11],
    ])

    # Scale to Likert 1-5
    items = (items - items.min(axis=0)) / (items.max(axis=0) - items.min(axis=0)) * 4 + 1
    items = np.round(items).astype(int)
    items = np.clip(items, 1, 5)

    df = pd.DataFrame(
        items,
        columns=[f"Item_{i+1}" for i in range(12)]
    )

    # Run EFA with parallel analysis
    results = fit_efa_with_parallel_analysis(
        df,
        extraction="ml",
        rotation="oblimin",
        verbose=True,
    )

    print("\n" + "=" * 75)
    print("SUMMARY")
    print("=" * 75)
    print(f"Detected {results['n_factors']} factors")
    print(f"Total variance explained: {results['variance_explained'].sum()*100:.1f}%")
    print(f"KMO adequacy: {results['kmo']:.3f}")
