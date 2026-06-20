import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from factor_analyzer.factor_analyzer import calculate_kmo, calculate_bartlett_sphericity
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any, Optional


def run_parallel_analysis(
    data: pd.DataFrame,
    n_iterations: int = 100,
    percentile: float = 95.0,
) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Run parallel analysis to determine optimal number of factors.

    Compares observed eigenvalues against those from random data.
    Keep factors where observed eigenvalue > random percentile eigenvalue.

    Parameters
    ----------
    data : pd.DataFrame
        Standardized survey items (rows=subjects, cols=items).
    n_iterations : int
        Number of random permutations to generate (default 100).
    percentile : float
        Percentile of random eigenvalues to use (default 95.0).

    Returns
    -------
    observed_evals : np.ndarray
        Eigenvalues from the actual data.
    random_evals : np.ndarray
        Specified percentile of random eigenvalues.
    n_factors : int
        Number of factors to retain (last index where observed > random).
    """
    n_subjects, n_items = data.shape

    # Observed eigenvalues — must use correlation matrix, not covariance.
    # Covariance eigenvalues scale with variable variance; correlation eigenvalues
    # are bounded (max = n_items) and comparable to the random-data eigenvalues
    # generated below (which also use np.corrcoef). Mixing covariance and
    # correlation eigenvalues makes factor retention decisions wrong when
    # variables have different scales.
    cov_matrix = data.corr()
    observed_evals = np.linalg.eigvals(cov_matrix)
    observed_evals = np.sort(observed_evals)[::-1]

    # Random eigenvalues
    random_evals_list = []
    np.random.seed(42)
    for _ in range(n_iterations):
        random_data = np.random.randn(n_subjects, n_items)
        random_cov = np.corrcoef(random_data.T)
        random_evals = np.linalg.eigvals(random_cov)
        random_evals_list.append(np.sort(random_evals)[::-1])

    random_evals = np.percentile(random_evals_list, percentile, axis=0)

    # Find the number of factors: last index where observed > random
    n_factors = np.sum(observed_evals > random_evals)

    return observed_evals, random_evals, n_factors


def fit_efa(
    data: pd.DataFrame,
    n_factors: Optional[int] = None,
    method: str = "ml",
    rotation: str = "oblimin",
    check_factorability: bool = True,
    parallel_analysis: bool = True,
) -> Tuple[FactorAnalyzer, Dict[str, Any]]:
    """
    Fit EFA on survey items with optional parallel analysis and factorability checks.

    This function implements best-practice exploratory factor analysis:
    1. Checks whether the data is suitable for factor analysis (KMO, Bartlett's)
    2. Determines the number of factors using parallel analysis or user specification
    3. Extracts factors using ML or principal-axis factoring
    4. Rotates to simple structure (oblique by default)

    Parameters
    ----------
    data : pd.DataFrame
        Survey items (rows=subjects, cols=items). Should be numeric item responses.
    n_factors : int, optional
        Number of factors to extract. If None and parallel_analysis=True,
        determined via parallel analysis. If None and parallel_analysis=False,
        defaults to 3.
    method : str, default="ml"
        Extraction method: "ml" (maximum likelihood) or "pa" (principal-axis factoring).
        - ML: Preferred if data ~normally distributed; enables fit statistics/tests
        - PA (PAF): More robust to non-normality; requires fewer assumptions
    rotation : str, default="oblimin"
        Rotation type. Affects interpretability and reported factor correlations:
        - "oblimin" (oblique): DEFAULT, assumes factors may correlate. Use in most
          cases; social/behavioral constructs typically covary. Reports factor
          correlation matrix φ.
        - "varimax" (orthogonal): Only if theory requires independent factors. Gives
          cleaner but usually less realistic structure. Correlation matrix is identity.
    check_factorability : bool, default=True
        If True, compute KMO and Bartlett's test and warn if data is unsuitable.
    parallel_analysis : bool, default=True
        If True and n_factors is None, use parallel analysis to determine n_factors
        (compare observed to random eigenvalues at the 95th percentile).

    Returns
    -------
    fa : FactorAnalyzer
        Fitted EFA model with loadings, communalities, and fit info.
    diagnostics : Dict[str, Any]
        Dictionary with keys:
        - "kmo_overall" : float, Kaiser–Meyer–Olkin statistic (want ≥ 0.6)
        - "bartlett_p" : float, p-value from Bartlett's test (want p < 0.05)
        - "n_factors" : int, number of factors extracted
        - "parallel_analysis" : dict with observed/random eigenvalues (if enabled)
        - "variance_explained" : float, total variance explained by factors
        - "communalities" : pd.Series, communality h² for each item (0–1 range)

    Notes
    -----
    - Always standardize data first (done automatically if not already done).
    - The number of factors is often the most consequential choice; parallel
      analysis is the most defensible approach.
    - Oblique rotation is the realistic default; orthogonal is a special case.
    - Communalities near 1.0 (Heywood cases) suggest model misspecification.
    - Low communalities (< 0.3) suggest an item measures something not common
      to the other items (consider removing or revising).
    """
    # Standardize if not already
    if not np.allclose(data.std(), 1.0):
        data = (data - data.mean()) / data.std()

    diagnostics = {}

    # Check factorability
    if check_factorability:
        kmo_per_item, kmo_overall = calculate_kmo(data.values)
        chi_square, p_value = calculate_bartlett_sphericity(data.values)

        diagnostics["kmo_overall"] = kmo_overall
        diagnostics["kmo_per_item"] = kmo_per_item
        diagnostics["bartlett_chi2"] = chi_square
        diagnostics["bartlett_p"] = p_value

        if kmo_overall < 0.6:
            print(f"⚠️  Warning: KMO = {kmo_overall:.3f} (want > 0.6). Data may not be suitable for FA.")
        if p_value > 0.05:
            print(f"⚠️  Warning: Bartlett p = {p_value:.4f} (want < 0.05). Correlation matrix near identity.")

    # Determine number of factors
    if n_factors is None:
        if parallel_analysis:
            obs_evals, rand_evals, n_factors = run_parallel_analysis(data)
            diagnostics["parallel_analysis"] = {
                "observed_eigenvalues": obs_evals,
                "random_eigenvalues": rand_evals,
                "n_factors": n_factors,
            }
            print(f"Parallel analysis suggests {n_factors} factor(s).")
        else:
            n_factors = 3
            print(f"No n_factors specified and parallel_analysis=False; defaulting to {n_factors}.")

    diagnostics["n_factors"] = n_factors

    # Fit EFA
    fa = FactorAnalyzer(
        n_factors=n_factors,
        method=method,
        rotation=rotation,
        use_smc=True,  # Use squared multiple correlations for initial communality estimates
    )
    fa.fit(data.values)

    # Extract diagnostics
    diagnostics["variance_explained"] = np.sum(fa.get_factor_variance()[0])
    diagnostics["communalities"] = pd.Series(
        fa.get_communalities(),
        index=data.columns,
    )

    return fa, diagnostics


def summary_efa(
    fa: FactorAnalyzer,
    data: pd.DataFrame,
    loading_threshold: float = 0.30,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Generate a formatted summary of EFA results with interpretation guidance.

    This function extracts and visualizes factor loadings, communalities, inter-factor
    correlations, and flags interpretability issues (cross-loadings, weak factors,
    Heywood cases).

    Parameters
    ----------
    fa : FactorAnalyzer
        Fitted EFA model.
    data : pd.DataFrame
        Original data (for column names and diagnostics).
    loading_threshold : float, default=0.30
        Magnitude threshold for defining "strong" loadings.
        - |λ| ≥ 0.40: substantive (primary interpretation)
        - 0.30 ≤ |λ| < 0.40: weak-moderate (secondary)
        - |λ| < 0.30: negligible (not usually interpreted)
    verbose : bool, default=True
        If True, print a formatted summary with interpretation guidance.

    Returns
    -------
    summary : Dict[str, Any]
        Dictionary with keys:
        - "loadings" : DataFrame (items × factors) of factor loadings λ
        - "communalities" : Series of item communalities h² (0–1, variance explained)
        - "factor_correlations" : DataFrame of φ (phi) matrix correlations (if oblique)
        - "flags" : list of interpretability warnings/errors
        - "rotation_type" : str, "oblique" or "orthogonal"

    Notes
    -----
    Interpretation rules (subject to field convention):
    - Communality h² < 0.30: item may not belong; measure different construct
    - Communality h² > 0.95: possible Heywood case; model may be misfit
    - Cross-loadings (|λ| > threshold on 2+ factors): item is ambiguous
    - Factor r > 0.80 (oblique): factors may be measuring the same thing; consider merging
    """
    summary = {}

    # Loadings
    loadings_df = pd.DataFrame(
        fa.loadings_,
        columns=[f"Factor_{i+1}" for i in range(fa.n_factors)],
        index=data.columns,
    )
    summary["loadings"] = loadings_df

    # Communalities
    communalities = pd.Series(fa.get_communalities(), index=data.columns, name="Communality")
    summary["communalities"] = communalities

    # Factor correlations (if rotation is oblique)
    if hasattr(fa, 'phi_') and fa.phi_ is not None:
        factor_corr = pd.DataFrame(
            fa.phi_,
            columns=[f"Factor_{i+1}" for i in range(fa.n_factors)],
            index=[f"Factor_{i+1}" for i in range(fa.n_factors)],
        )
        summary["factor_correlations"] = factor_corr

    # Flags
    flags = []

    # Flag cross-loadings
    abs_loadings = np.abs(loadings_df.values)
    above_threshold = abs_loadings >= loading_threshold
    cross_loaders = np.sum(above_threshold, axis=1) > 1
    if np.any(cross_loaders):
        cross_items = data.columns[cross_loaders]
        flags.append(f"Cross-loadings detected on: {', '.join(cross_items)}")

    # Flag weak factors (no items with |loading| >= threshold)
    strong_per_factor = np.sum(above_threshold, axis=0)
    if np.any(strong_per_factor == 0):
        weak_factors = np.where(strong_per_factor == 0)[0]
        flags.append(f"No strong loadings on Factor(s): {weak_factors + 1}")

    # Flag Heywood cases (communalities > 1, impossible)
    if np.any(communalities > 1.0):
        heywood_items = communalities[communalities > 1.0].index
        flags.append(f"Heywood cases (communality > 1.0): {', '.join(heywood_items)}")

    # Flag low communalities (< 0.3)
    if np.any(communalities < 0.3):
        low_comm_items = communalities[communalities < 0.3].index
        flags.append(f"Low communalities (< 0.30): {', '.join(low_comm_items)}")

    summary["flags"] = flags
    summary["rotation_type"] = "oblique" if hasattr(fa, 'phi_') and fa.phi_ is not None else "orthogonal"

    if verbose:
        _print_efa_summary(summary, loadings_df, communalities)

    return summary


def _print_efa_summary(summary: Dict, loadings_df: pd.DataFrame, communalities: pd.Series) -> None:
    """Print a formatted EFA summary with interpretation guidance."""

    print("\n" + "=" * 80)
    print("EXPLORATORY FACTOR ANALYSIS SUMMARY")
    print("=" * 80)

    # Factor loadings
    print("\nFACTOR LOADINGS (λ)")
    print("-" * 80)
    print("(Items with |λ| ≥ 0.40 are substantive; 0.30–0.40 are weak-moderate)")
    print()
    print(loadings_df.round(3).to_string())

    # Communalities
    print("\n\nCOMMUNALITIES (h²)")
    print("-" * 80)
    print("Proportion of each item's variance explained by the factors (0–1 scale).")
    print()
    comm_display = communalities.round(3).to_frame("h²")
    print(comm_display.to_string())

    # Highlight low communalities
    low_comm = communalities[communalities < 0.30]
    if len(low_comm) > 0:
        print("\n  ⚠️  Low communalities (< 0.30):")
        for item, val in low_comm.items():
            print(f"    {item:30s} h² = {val:.3f}  (item may measure unique variance not shared with others)")

    # Highlight Heywood cases
    high_comm = communalities[communalities > 0.98]
    if len(high_comm) > 0:
        print("\n  ⚠️  Heywood cases (h² > 0.98, impossible variance):")
        for item, val in high_comm.items():
            print(f"    {item:30s} h² = {val:.3f}  (model misspecification)")

    # Factor correlations
    if "factor_correlations" in summary:
        print("\n\nFACTOR CORRELATIONS (φ matrix, oblique rotation)")
        print("-" * 80)
        print("Correlations between latent factors. A substantive finding (r > |0.5|)")
        print("suggests factors may measure related constructs.")
        print()
        print(summary["factor_correlations"].round(3).to_string())

        # Highlight high correlations
        corr_matrix = summary["factor_correlations"].values
        for i in range(len(corr_matrix)):
            for j in range(i+1, len(corr_matrix)):
                if abs(corr_matrix[i, j]) > 0.70:
                    print(f"\n  ⚠️  High factor correlation: Factor {i+1} ↔ Factor {j+1} (r = {corr_matrix[i, j]:.3f})")
                    print(f"     → Consider whether factors measure distinct constructs")

    # Flags
    if summary["flags"]:
        print("\n\nINTERPRETABILITY FLAGS")
        print("-" * 80)
        for i, flag in enumerate(summary["flags"], 1):
            print(f"  {i}. {flag}")
    else:
        print("\n\n✓ No major interpretability issues detected")

    print("\n" + "=" * 80)


ROTATION_EXPLANATION = """
╔════════════════════════════════════════════════════════════════════════════════╗
║                     ROTATION CHOICE: OBLIQUE vs. ORTHOGONAL                     ║
╚════════════════════════════════════════════════════════════════════════════════╝

1. OBLIQUE ROTATION (oblimin, promax) — USE BY DEFAULT
   ─────────────────────────────────────────────────────

   Assumption: Factors MAY correlate (realistic in social science).

   Pros:
   ✓ Recovers inter-factor correlations (substantive information)
   ✓ Simpler structure (items load strongly on one factor)
   ✓ More interpretable (clearer factor definitions)
   ✓ Factors in psychology, education, business typically covary

   Cons:
   ✗ Slightly more complex output (need φ matrix)

   When to use:
   • Default choice for psychology, education, organizational behavior
   • When you don't know if factors correlate
   • When you want to know the factor relationships

   Example:
       fa, diag = fit_efa(df, rotation='oblimin')
       # Reports factor correlations φ; probably some r > 0.30


2. ORTHOGONAL ROTATION (varimax, equamax) — SPECIAL CASE ONLY
   ──────────────────────────────────────────────────────────

   Assumption: Factors are UNCORRELATED (independence).

   Pros:
   ✓ Simpler interpretation (no correlation matrix needed)
   ✓ Better for specific applications (some ML preprocessing tasks)
   ✓ Cleaner factor score computation

   Cons:
   ✗ Unrealistic for most social science data
   ✗ Forces independence where none may exist
   ✗ Usually produces messier item-to-factor mappings

   When to use:
   • Theory explicitly requires independent constructs
   • Downstream model (e.g., regression) expects uncorrelated predictors
   • Historical convention in your field (rare)

   Example:
       fa, diag = fit_efa(df, rotation='varimax')
       # All inter-factor correlations set to 0


BOTTOM LINE:
───────────
• Oblique (oblimin) is the realistic default. Use it unless you have
  a specific reason not to.
• The factor correlations from oblique rotation are data, not a flaw.
  They tell you whether factors are related.
• Orthogonal is a special-case constraint, not a general choice.
"""


# Example usage
if __name__ == "__main__":
    print(ROTATION_EXPLANATION)

    # Create sample survey data (200 subjects, 9 items from 3 factors)
    np.random.seed(42)
    n_subjects = 200

    # 3 latent factors (with some correlation)
    f1 = np.random.randn(n_subjects)
    f2 = np.random.randn(n_subjects)
    f3 = 0.3*f1 + 0.7*np.random.randn(n_subjects)  # f3 slightly correlated with f1

    # Generate items with loadings + noise
    data_matrix = np.column_stack([
        # Factor 1 items
        0.8*f1 + 0.3*np.random.randn(n_subjects),
        0.75*f1 + 0.3*np.random.randn(n_subjects),
        0.7*f1 + 0.3*np.random.randn(n_subjects),
        # Factor 2 items
        0.8*f2 + 0.3*np.random.randn(n_subjects),
        0.75*f2 + 0.3*np.random.randn(n_subjects),
        0.7*f2 + 0.3*np.random.randn(n_subjects),
        # Factor 3 items
        0.8*f3 + 0.3*np.random.randn(n_subjects),
        0.75*f3 + 0.3*np.random.randn(n_subjects),
        0.7*f3 + 0.3*np.random.randn(n_subjects),
    ])

    # Scale to Likert-like (1-5)
    df = pd.DataFrame(
        data_matrix,
        columns=[f"Item_{i+1}" for i in range(9)]
    )
    df = ((df + 2.5) * 0.8).round().clip(1, 5)

    # Standardize
    df = (df - df.mean()) / df.std()

    print("\n" + "="*80)
    print("EXAMPLE: EFA with Parallel Analysis and Oblique Rotation")
    print("="*80)

    # Fit EFA with parallel analysis (default: oblimin rotation)
    fa, diag = fit_efa(df, method="ml", rotation="oblimin")

    print(f"\nFactorability Check:")
    print(f"  KMO: {diag['kmo_overall']:.3f}")
    print(f"  Bartlett's p: {diag['bartlett_p']:.2e}")

    if "parallel_analysis" in diag:
        pa = diag["parallel_analysis"]
        print(f"\nParallel Analysis Result:")
        print(f"  Suggested n_factors: {pa['n_factors']}")

    summary = summary_efa(fa, df, verbose=True)

    print(f"\nModel Summary:")
    print(f"  Rotation: {summary['rotation_type'].upper()}")
    print(f"  Variance Explained: {diag['variance_explained']:.1%}")

    # Demonstrate difference with orthogonal rotation
    print("\n" + "="*80)
    print("COMPARISON: Same EFA with Orthogonal Rotation (varimax)")
    print("="*80)
    print("(Note: varimax forces independence; oblimin is usually preferred)\n")

    fa_ortho, diag_ortho = fit_efa(df, n_factors=3, method="ml", rotation="varimax")
    summary_ortho = summary_efa(fa_ortho, df, verbose=True)
