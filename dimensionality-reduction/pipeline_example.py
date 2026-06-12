"""
Complete dimensionality reduction pipeline with trustworthiness validation.
Loads data → standardizes → PCA → UMAP → validates embedding quality.
"""

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.neighbors import NearestNeighbors
import umap
import matplotlib.pyplot as plt


def load_dataset(dataset_name="iris", n_samples=300, n_features=20):
    """Load or generate a numeric dataset."""
    if dataset_name == "iris":
        data = load_iris()
        X = data.data
        y = data.target
        print(f"Loaded Iris dataset: {X.shape}")
    elif dataset_name == "synthetic":
        X, y = make_blobs(
            n_samples=n_samples,
            n_features=n_features,
            centers=5,
            random_state=42,
            cluster_std=2.0
        )
        print(f"Generated synthetic dataset: {X.shape}")
    else:
        raise ValueError("dataset_name must be 'iris' or 'synthetic'")

    return X, y


def standardize(X):
    """Standardize features to zero mean and unit variance."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print(f"Standardized data: mean={X_scaled.mean():.4f}, std={X_scaled.std():.4f}")
    return X_scaled, scaler


def apply_pca(X, n_components=50):
    """Apply PCA for preprocessing before UMAP."""
    pca = PCA(n_components=min(n_components, X.shape[1]))
    X_pca = pca.fit_transform(X)
    explained_var = pca.explained_variance_ratio_.sum()
    print(f"PCA: {X.shape[1]} → {X_pca.shape[1]} dims, "
          f"explained variance={explained_var:.4f}")
    return X_pca, pca


def apply_umap(X, n_components=2, n_neighbors=15, min_dist=0.1):
    """Apply UMAP for 2D/3D visualization or further reduction."""
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=42,
        metric='euclidean'
    )
    X_umap = reducer.fit_transform(X)
    print(f"UMAP: {X.shape[1]} → {X_umap.shape[1]} dims")
    return X_umap, reducer


def trustworthiness_score(X_high, X_low, k=15):
    """
    Quantify whether local structure is preserved (0-1, higher is better).
    If k neighbors in high-dim space match k neighbors in low-dim space,
    trustworthiness is high. Measures preservation of nearest neighbors.
    """
    n = X_high.shape[0]

    # Find k nearest neighbors in high-dimensional space
    nbrs_high = NearestNeighbors(n_neighbors=k + 1).fit(X_high)
    indices_high = nbrs_high.kneighbors(X_high, return_distance=False)[:, 1:]

    # Find k nearest neighbors in low-dimensional space
    nbrs_low = NearestNeighbors(n_neighbors=k + 1).fit(X_low)
    indices_low = nbrs_low.kneighbors(X_low, return_distance=False)[:, 1:]

    # Count matches: how many of the k nearest neighbors in low-dim
    # were also in the k nearest in high-dim
    trust = 0
    for i in range(n):
        matches = len(set(indices_high[i]) & set(indices_low[i]))
        trust += matches / k

    return trust / n


def continuity_score(X_high, X_low, k=15):
    """
    Quantify whether new neighbors are not introduced (0-1, higher is better).
    Complement of trustworthiness. Measures absence of false neighbors.
    """
    n = X_high.shape[0]

    nbrs_high = NearestNeighbors(n_neighbors=k + 1).fit(X_high)
    indices_high = nbrs_high.kneighbors(X_high, return_distance=False)[:, 1:]

    nbrs_low = NearestNeighbors(n_neighbors=k + 1).fit(X_low)
    indices_low = nbrs_low.kneighbors(X_low, return_distance=False)[:, 1:]

    cont = 0
    for i in range(n):
        matches = len(set(indices_high[i]) & set(indices_low[i]))
        cont += matches / k

    return cont / n


def distance_preservation(X_high, X_low, sample_size=None):
    """
    Measure correlation of pairwise distances: high-dim vs low-dim.
    Higher correlation (→1) means distances are better preserved.
    """
    if sample_size is None:
        sample_size = min(500, X_high.shape[0])

    idx = np.random.choice(X_high.shape[0], size=sample_size, replace=False)
    X_h = X_high[idx]
    X_l = X_low[idx]

    # Pairwise distances
    D_high = euclidean_distances(X_h)
    D_low = euclidean_distances(X_l)

    # Flatten and compute Pearson correlation
    d_high = D_high[np.triu_indices_from(D_high, k=1)]
    d_low = D_low[np.triu_indices_from(D_low, k=1)]

    correlation = np.corrcoef(d_high, d_low)[0, 1]
    return correlation


def validate_embedding(X_high, X_low, k=15, verbose=True):
    """
    Comprehensive validation of embedding trustworthiness.
    Returns dict with multiple metrics.
    """
    results = {
        'trustworthiness': trustworthiness_score(X_high, X_low, k=k),
        'continuity': continuity_score(X_high, X_low, k=k),
        'distance_correlation': distance_preservation(X_high, X_low),
    }

    if verbose:
        print("\n" + "="*60)
        print("EMBEDDING VALIDATION RESULTS")
        print("="*60)
        print(f"Trustworthiness (k={k}):     {results['trustworthiness']:.4f}  [0-1, higher=better]")
        print(f"Continuity (k={k}):          {results['continuity']:.4f}  [0-1, higher=better]")
        print(f"Distance Correlation:       {results['distance_correlation']:.4f}  [-1-1, |·|→1=better]")

        if results['trustworthiness'] > 0.9:
            print("\n✓ Embedding is HIGHLY TRUSTWORTHY")
        elif results['trustworthiness'] > 0.7:
            print("\n✓ Embedding is REASONABLY TRUSTWORTHY")
        else:
            print("\n⚠ Embedding may not preserve structure well")

        print("="*60 + "\n")

    return results


def plot_embedding(X_low, y, title="UMAP Embedding"):
    """Visualize 2D embedding colored by labels."""
    if X_low.shape[1] < 2:
        print("Cannot plot: embedding has fewer than 2 dimensions")
        return

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_low[:, 0], X_low[:, 1], c=y, cmap='tab10', alpha=0.7, s=30)
    plt.colorbar(scatter, label='Class')
    plt.title(title)
    plt.xlabel('UMAP 1')
    plt.ylabel('UMAP 2')
    plt.tight_layout()
    plt.show()


def main():
    """Run the complete pipeline."""
    print("Dimensionality Reduction Pipeline with Trustworthiness Validation\n")

    # 1. Load data
    X, y = load_dataset(dataset_name="iris")

    # 2. Standardize
    X_scaled, scaler = standardize(X)

    # 3. PCA preprocessing (optional, helps UMAP)
    X_pca, pca = apply_pca(X_scaled, n_components=50)

    # 4. UMAP for visualization
    X_umap, umap_model = apply_umap(X_pca, n_components=2, n_neighbors=15, min_dist=0.1)

    # 5. Validate embedding quality
    metrics = validate_embedding(X_pca, X_umap, k=15, verbose=True)

    # 6. Plot (optional)
    plot_embedding(X_umap, y, title="UMAP Embedding of Iris Dataset")

    return {
        'X_original': X,
        'X_scaled': X_scaled,
        'X_pca': X_pca,
        'X_umap': X_umap,
        'y': y,
        'scaler': scaler,
        'pca': pca,
        'umap': umap_model,
        'metrics': metrics
    }


if __name__ == "__main__":
    results = main()
