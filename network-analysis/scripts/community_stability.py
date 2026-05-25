#!/usr/bin/env python3
"""
community_stability.py — Run Leiden many times, report partition stability.

The point: a single Louvain/Leiden run gives ONE high-modularity partition
from a degenerate landscape with many similar partitions. Reporting that
single partition as "the communities" is overclaim. Use this to quantify
how stable the community structure actually is.

Outputs:
  - mean and SD of number of communities across runs
  - mean and SD of modularity
  - pairwise NMI / ARI across runs (consensus stability)
  - the consensus partition (each pair clustered together iff they were
    together in >= 50% of runs)

Usage:
    python community_stability.py <path> [--directed] [--runs 100] [--resolution 1.0]

Requires: python-igraph, leidenalg, scikit-learn
"""
import argparse
import sys
from collections import Counter

import numpy as np
import igraph as ig
import leidenalg as la
from sklearn.metrics import (
    normalized_mutual_info_score,
    adjusted_mutual_info_score,
    adjusted_rand_score,
)


def load_graph_ig(path, directed, delimiter):
    """Load an edgelist into igraph."""
    with open(path) as f:
        edges = []
        for line in f:
            parts = line.strip().split(delimiter) if delimiter else line.strip().split()
            if len(parts) >= 2:
                edges.append((parts[0], parts[1]))
    # build vocabulary
    vocab = {}
    for s, t in edges:
        for v in (s, t):
            if v not in vocab:
                vocab[v] = len(vocab)
    eindex = [(vocab[s], vocab[t]) for s, t in edges]
    g = ig.Graph(n=len(vocab), edges=eindex, directed=directed)
    g.vs["name"] = [n for n, _ in sorted(vocab.items(), key=lambda x: x[1])]
    return g


def leiden_runs(g, n_runs, resolution, seed_start=0):
    partitions = []
    qualities = []
    sizes = []
    for r in range(n_runs):
        part = la.find_partition(
            g,
            la.RBConfigurationVertexPartition,
            resolution_parameter=resolution,
            seed=seed_start + r,
        )
        partitions.append(part.membership)
        qualities.append(part.quality())
        sizes.append(len(part))
        if (r + 1) % 10 == 0:
            print(f"  completed {r+1}/{n_runs} runs", file=sys.stderr)
    return partitions, qualities, sizes


def pairwise_ari(partitions, max_pairs=200):
    """Mean pairwise ARI; sample if there are many partitions."""
    n = len(partitions)
    pairs = []
    if n * (n - 1) // 2 <= max_pairs:
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((i, j))
    else:
        rng = np.random.default_rng(42)
        while len(pairs) < max_pairs:
            i, j = rng.integers(0, n, 2)
            if i != j:
                pairs.append((min(i, j), max(i, j)))
        pairs = list(set(pairs))
    aris = [adjusted_rand_score(partitions[i], partitions[j]) for i, j in pairs]
    amis = [adjusted_mutual_info_score(partitions[i], partitions[j]) for i, j in pairs]
    return np.mean(aris), np.std(aris), np.mean(amis), np.std(amis)


def consensus_partition(partitions, threshold=0.5):
    """Build a consensus partition: cluster i with j iff they were in the same
    cluster in >= threshold fraction of runs.

    Implemented as a graph clustering on the consensus graph (nodes = original
    nodes, edges weighted by co-clustering frequency).
    """
    n_runs = len(partitions)
    n_nodes = len(partitions[0])

    # build co-occurrence matrix (sparse representation for efficiency)
    co_count = np.zeros((n_nodes, n_nodes), dtype=np.float32)
    for p in partitions:
        p_arr = np.asarray(p)
        # for each cluster, add 1 to every pair in that cluster
        for c in np.unique(p_arr):
            members = np.where(p_arr == c)[0]
            for i in members:
                co_count[i, members] += 1

    co_freq = co_count / n_runs
    # build consensus graph
    adj = (co_freq >= threshold).astype(int)
    np.fill_diagonal(adj, 0)
    g_cons = ig.Graph.Adjacency(adj.tolist(), mode="undirected")
    cons_part = la.find_partition(g_cons, la.ModularityVertexPartition, seed=42)
    return cons_part.membership, co_freq


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("--directed", action="store_true")
    p.add_argument("--delimiter", default=None)
    p.add_argument("--runs", type=int, default=50)
    p.add_argument("--resolution", type=float, default=1.0,
                   help="RB configuration resolution parameter; scan to find structure")
    p.add_argument("--threshold", type=float, default=0.5,
                   help="Consensus threshold (fraction of runs requiring co-membership)")
    args = p.parse_args()

    g = load_graph_ig(args.path, args.directed, args.delimiter)
    print(f"Loaded graph: n={g.vcount()}, m={g.ecount()}, directed={g.is_directed()}",
          file=sys.stderr)

    if not g.is_connected(mode="weak"):
        comps = g.components(mode="weak")
        largest_idx = max(range(len(comps)), key=lambda i: len(comps[i]))
        print(f"WARNING: disconnected; restricting to largest component "
              f"(n={len(comps[largest_idx])})", file=sys.stderr)
        g = g.subgraph(comps[largest_idx])

    print(f"\nRunning Leiden {args.runs} times at resolution={args.resolution}...",
          file=sys.stderr)
    partitions, qualities, sizes = leiden_runs(g, args.runs, args.resolution)

    print("\n[per-run summaries]")
    print(f"  number of communities:  mean={np.mean(sizes):.1f} sd={np.std(sizes):.1f} "
          f"min={min(sizes)} max={max(sizes)}")
    print(f"  modularity-like quality: mean={np.mean(qualities):.4f} sd={np.std(qualities):.4f}")

    # distribution of community counts
    size_counter = Counter(sizes)
    print("  distribution of community counts: " +
          ", ".join(f"{k}:{v}" for k, v in sorted(size_counter.items())))

    print("\n[pairwise partition similarity across runs]")
    ari_m, ari_s, ami_m, ami_s = pairwise_ari(partitions)
    print(f"  mean ARI: {ari_m:.3f} ± {ari_s:.3f}")
    print(f"  mean AMI: {ami_m:.3f} ± {ami_s:.3f}")
    if ari_m < 0.5:
        print("  → LOW stability: partition is not robust. Consider larger resolution "
              "scan or use a different algorithm (nested SBM in graph-tool).")
    elif ari_m < 0.8:
        print("  → moderate stability: report consensus partition rather than single run.")
    else:
        print("  → high stability: a single-run partition is reasonably representative.")

    print(f"\n[consensus partition (co-membership >= {args.threshold} of runs)]")
    cons, _ = consensus_partition(partitions, threshold=args.threshold)
    cons_sizes = Counter(cons)
    print(f"  consensus has {len(cons_sizes)} communities")
    print(f"  size distribution: {sorted(cons_sizes.values(), reverse=True)}")

    # null comparison: shuffle the graph and rerun
    print("\n[null comparison — shuffled (configuration-model) modularity]")
    g_null = g.copy()
    g_null.rewire(n=10 * g.ecount(), mode="simple")
    null_part = la.find_partition(g_null, la.RBConfigurationVertexPartition,
                                    resolution_parameter=args.resolution, seed=0)
    print(f"  configuration-null modularity:  {null_part.quality():.4f}")
    print(f"  observed modularity (mean):     {np.mean(qualities):.4f}")
    if np.mean(qualities) - null_part.quality() < 0.05:
        print("  → modularity is barely better than null. Community structure may be SPURIOUS.")
    else:
        print(f"  → modularity exceeds null by {np.mean(qualities) - null_part.quality():.3f}; "
              "structure is real.")


if __name__ == "__main__":
    main()
