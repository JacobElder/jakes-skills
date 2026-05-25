#!/usr/bin/env python3
"""
centrality_battery.py — Compute multiple centralities and surface where they
disagree.

The point: centrality is plural. Different measures rank nodes differently;
that disagreement is the substantive information, not noise. Run this BEFORE
picking a single centrality to report, to know how robust the ranking is.

Usage:
    python centrality_battery.py <path> [--directed] [--top K] [--out csv_path]

Computes:
    degree (in/out for directed), strength (if weighted), betweenness,
    closeness (harmonic for robustness), eigenvector or PageRank,
    Katz, Burt's constraint (structural holes).

Reports:
    - top-K list under each measure
    - Spearman rank correlation matrix between measures
    - flag pairs of measures with rank correlation < 0.5 (they disagree
      substantially; pick based on substantive question)
"""
import argparse
import sys

import networkx as nx
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def compute_centralities(G):
    """Compute a battery of centrality measures, with sensible fallbacks."""
    centralities = {}
    n = G.number_of_nodes()
    directed = G.is_directed()
    weighted = any("weight" in d for _, _, d in G.edges(data=True))

    # degree (and in/out if directed)
    if directed:
        centralities["in_degree"]  = dict(G.in_degree())
        centralities["out_degree"] = dict(G.out_degree())
    else:
        centralities["degree"] = dict(G.degree())

    # strength (weighted degree)
    if weighted:
        if directed:
            centralities["in_strength"]  = dict(G.in_degree(weight="weight"))
            centralities["out_strength"] = dict(G.out_degree(weight="weight"))
        else:
            centralities["strength"] = dict(G.degree(weight="weight"))

    # betweenness — sample for large graphs
    print("  computing betweenness...", file=sys.stderr)
    if n > 5000:
        k = max(100, n // 50)
        centralities["betweenness"] = nx.betweenness_centrality(G, k=k, seed=42)
        print(f"  (approximated with k={k} samples)", file=sys.stderr)
    else:
        centralities["betweenness"] = nx.betweenness_centrality(G)

    # closeness — use harmonic for robustness to disconnection
    print("  computing harmonic closeness...", file=sys.stderr)
    try:
        centralities["harmonic_closeness"] = nx.harmonic_centrality(G)
    except Exception as e:
        print(f"  harmonic closeness failed: {e}", file=sys.stderr)

    # PageRank works for directed and undirected; eigenvector fails for many cases
    print("  computing PageRank...", file=sys.stderr)
    try:
        centralities["pagerank"] = nx.pagerank(G, alpha=0.85)
    except Exception as e:
        print(f"  pagerank failed: {e}", file=sys.stderr)

    # eigenvector (often fails; warn rather than abort)
    print("  computing eigenvector centrality...", file=sys.stderr)
    try:
        if directed:
            centralities["eigenvector"] = nx.eigenvector_centrality_numpy(G)
        else:
            centralities["eigenvector"] = nx.eigenvector_centrality_numpy(G)
    except Exception as e:
        print(f"  eigenvector failed (this is common — use Katz/PageRank instead): {e}", file=sys.stderr)

    # Katz — works on directed graphs where eigenvector fails
    print("  computing Katz centrality...", file=sys.stderr)
    try:
        # alpha must be < 1/lambda_max; use 0.005 as a safe default
        # for larger networks scale alpha down
        alpha = min(0.005, 0.9 / max(dict(G.degree()).values()))
        centralities["katz"] = nx.katz_centrality_numpy(G, alpha=alpha)
    except Exception as e:
        print(f"  katz failed: {e}", file=sys.stderr)

    # Burt's constraint — structural holes
    print("  computing Burt's constraint (structural holes)...", file=sys.stderr)
    try:
        constraint = nx.constraint(G)
        # lower constraint = more brokerage opportunity; invert sign for "centrality"-like ranking
        centralities["broker_score"] = {n: -v if not np.isnan(v) else 0.0 for n, v in constraint.items()}
    except Exception as e:
        print(f"  constraint failed: {e}", file=sys.stderr)

    return centralities


def build_dataframe(centralities):
    df = pd.DataFrame(centralities)
    df = df.fillna(0)
    return df


def rank_correlations(df):
    """Spearman rank correlation between centralities."""
    cols = df.columns
    corr = pd.DataFrame(index=cols, columns=cols, dtype=float)
    for a in cols:
        for b in cols:
            if a == b:
                corr.loc[a, b] = 1.0
            else:
                rho, _ = spearmanr(df[a], df[b])
                corr.loc[a, b] = rho
    return corr


def top_k(df, k=10):
    """For each centrality, list the top-K nodes."""
    for col in df.columns:
        ranked = df[col].sort_values(ascending=False).head(k)
        print(f"\n[top {k} by {col}]")
        for node, value in ranked.items():
            print(f"  {str(node):30s} {value:.4f}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", help="Path to graph file (edgelist)")
    p.add_argument("--directed", action="store_true")
    p.add_argument("--weighted", action="store_true")
    p.add_argument("--delimiter", default=None)
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--out", default=None, help="Save full centrality dataframe to CSV")
    args = p.parse_args()

    create_using = nx.DiGraph() if args.directed else nx.Graph()
    if args.weighted:
        G = nx.read_weighted_edgelist(args.path, create_using=create_using, delimiter=args.delimiter)
    else:
        G = nx.read_edgelist(args.path, create_using=create_using, delimiter=args.delimiter)

    print(f"\nLoaded graph: n={G.number_of_nodes()}, m={G.number_of_edges()}, "
          f"directed={G.is_directed()}", file=sys.stderr)

    # for connected components: most centralities only sensible on LCC
    if args.directed:
        components = list(nx.weakly_connected_components(G))
    else:
        components = list(nx.connected_components(G))

    if len(components) > 1:
        largest = max(components, key=len)
        print(f"WARNING: graph is disconnected ({len(components)} components). "
              f"Restricting to largest component (n={len(largest)}).", file=sys.stderr)
        G = G.subgraph(largest).copy()

    print("\nComputing centralities...", file=sys.stderr)
    centralities = compute_centralities(G)

    df = build_dataframe(centralities)
    top_k(df, k=args.top)

    print("\n[rank correlations between centralities (Spearman ρ)]")
    corr = rank_correlations(df)
    print(corr.round(3).to_string())

    # flag substantial disagreements
    print("\n[centrality DISAGREEMENTS (|ρ| < 0.5) — these are substantive choices]")
    disagreements = []
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            if abs(corr.loc[a, b]) < 0.5:
                disagreements.append((a, b, corr.loc[a, b]))
    if disagreements:
        for a, b, r in disagreements:
            print(f"  {a} vs {b}: ρ = {r:.3f}")
        print("\n  → these measures rank nodes differently. The choice between them ")
        print("    is substantive (different definitions of 'important'). See SKILL.md ")
        print("    or references/centrality.md for which to pick based on the question.")
    else:
        print("  (all centralities are highly correlated for this network — robust ranking)")

    if args.out:
        df.to_csv(args.out)
        print(f"\nSaved full centrality dataframe to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
