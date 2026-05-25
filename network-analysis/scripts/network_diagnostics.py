#!/usr/bin/env python3
"""
network_diagnostics.py — Print a one-page diagnostic report for any network.

Usage:
    python network_diagnostics.py <path> [--directed] [--weighted] [--delimiter ','] [--format edgelist|graphml|gml|pajek]

The point: run this BEFORE any analysis. Surface misreads of the data
(unexpected isolates, wrong direction, miscounted nodes) before you start
computing betweenness on a graph you think is one thing and is another.

Outputs:
  - basic counts (n, m, density, directedness, weightedness)
  - components: number, size of largest, isolates
  - degree distribution summary (mean, median, max, gini)
  - reciprocity (if directed), transitivity, clustering
  - assortativity (degree)
  - top-degree node IDs (visual sanity check)
  - warnings for common gotchas (self-loops, multi-edges, isolates, disconnected, very dense, very sparse)
"""
import argparse
import sys
from collections import Counter

import networkx as nx
import numpy as np


def gini(values):
    """Gini coefficient of a non-negative array (for degree inequality)."""
    v = np.sort(np.asarray(values, dtype=float))
    n = len(v)
    if n == 0 or v.sum() == 0:
        return 0.0
    return (2 * np.arange(1, n + 1) - n - 1).dot(v) / (n * v.sum())


def load_graph(path, fmt, directed, weighted, delimiter):
    if fmt == "graphml":
        return nx.read_graphml(path)
    if fmt == "gml":
        return nx.read_gml(path)
    if fmt == "pajek":
        return nx.read_pajek(path)
    # edgelist
    create_using = nx.DiGraph() if directed else nx.Graph()
    if weighted:
        return nx.read_weighted_edgelist(path, create_using=create_using, delimiter=delimiter)
    return nx.read_edgelist(path, create_using=create_using, delimiter=delimiter)


def report(G):
    print("=" * 60)
    print(" Network diagnostic report")
    print("=" * 60)

    n = G.number_of_nodes()
    m = G.number_of_edges()
    directed = G.is_directed()
    multi = G.is_multigraph()
    weighted = any("weight" in d for _, _, d in G.edges(data=True))

    print(f"\n[basics]")
    print(f"  nodes:       {n:,}")
    print(f"  edges:       {m:,}")
    print(f"  directed:    {directed}")
    print(f"  multigraph:  {multi}")
    print(f"  weighted:    {weighted}")
    print(f"  density:     {nx.density(G):.6f}")
    print(f"  self-loops:  {nx.number_of_selfloops(G):,}")

    # components
    if directed:
        n_wcc = nx.number_weakly_connected_components(G)
        n_scc = nx.number_strongly_connected_components(G)
        largest_wcc = max(nx.weakly_connected_components(G), key=len)
        largest_scc = max(nx.strongly_connected_components(G), key=len)
        print(f"\n[components]")
        print(f"  weakly connected components:   {n_wcc:,}")
        print(f"  largest WCC size:              {len(largest_wcc):,} ({100*len(largest_wcc)/n:.1f}%)")
        print(f"  strongly connected components: {n_scc:,}")
        print(f"  largest SCC size:              {len(largest_scc):,} ({100*len(largest_scc)/n:.1f}%)")
    else:
        n_cc = nx.number_connected_components(G)
        largest_cc = max(nx.connected_components(G), key=len)
        print(f"\n[components]")
        print(f"  connected components: {n_cc:,}")
        print(f"  largest CC size:      {len(largest_cc):,} ({100*len(largest_cc)/n:.1f}%)")

    # isolates
    isolates = list(nx.isolates(G))
    print(f"  isolates: {len(isolates):,}")

    # degree distribution
    if directed:
        in_deg = [d for _, d in G.in_degree()]
        out_deg = [d for _, d in G.out_degree()]
        print(f"\n[degree distribution — in-degree]")
        print(f"  mean: {np.mean(in_deg):.2f}, median: {np.median(in_deg):.0f}, "
              f"max: {np.max(in_deg)}, gini: {gini(in_deg):.3f}")
        print(f"[degree distribution — out-degree]")
        print(f"  mean: {np.mean(out_deg):.2f}, median: {np.median(out_deg):.0f}, "
              f"max: {np.max(out_deg)}, gini: {gini(out_deg):.3f}")
    else:
        deg = [d for _, d in G.degree()]
        print(f"\n[degree distribution]")
        print(f"  mean: {np.mean(deg):.2f}, median: {np.median(deg):.0f}, "
              f"max: {np.max(deg)}, gini: {gini(deg):.3f}")

    # structural measures
    print(f"\n[structure]")
    if directed:
        try:
            r = nx.reciprocity(G)
            print(f"  reciprocity:              {r:.4f}")
        except Exception as e:
            print(f"  reciprocity: ERROR — {e}")
    try:
        t = nx.transitivity(G)
        print(f"  transitivity (global C):  {t:.4f}")
    except Exception as e:
        print(f"  transitivity: ERROR — {e}")
    try:
        avg_clust = nx.average_clustering(G)
        print(f"  avg clustering coef:      {avg_clust:.4f}")
    except Exception as e:
        print(f"  avg clustering: ERROR — {e}")
    try:
        dassort = nx.degree_assortativity_coefficient(G)
        print(f"  degree assortativity:     {dassort:.4f}")
    except Exception as e:
        print(f"  degree assortativity: ERROR — {e}")

    # top-degree nodes
    print(f"\n[top-10 highest-degree nodes]")
    if directed:
        top = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
        for node, d in top:
            print(f"  {node!s:30s} total_degree={d}")
    else:
        top = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:10]
        for node, d in top:
            print(f"  {node!s:30s} degree={d}")

    # warnings
    print(f"\n[warnings]")
    warnings = []
    if nx.number_of_selfloops(G) > 0:
        warnings.append(f"  ! {nx.number_of_selfloops(G)} self-loops present — some algorithms (clustering) handle these oddly")
    if multi:
        warnings.append(f"  ! multigraph (parallel edges) — many SNA algorithms assume simple graphs")
    if len(isolates) > 0:
        warnings.append(f"  ! {len(isolates)} isolated nodes — closeness, eigenvector centrality fail; consider restriction")
    if nx.density(G) > 0.5:
        warnings.append(f"  ! very dense (density>0.5) — visualization will be a hairball; consider matrix view or backbone")
    if nx.density(G) < 1e-5:
        warnings.append(f"  ! very sparse (density<1e-5) — many edges may be missing; consider whether observation is complete")
    if directed:
        if nx.number_weakly_connected_components(G) > 1:
            warnings.append(f"  ! disconnected — eigenvector/closeness need explicit handling; consider restricting to LWCC")
        if nx.number_strongly_connected_components(G) / n > 0.9:
            warnings.append(f"  ! most nodes are in their own SCC — many directed algorithms (PageRank, HITS) may give degenerate output")
    else:
        if nx.number_connected_components(G) > 1:
            warnings.append(f"  ! disconnected — eigenvector/closeness need explicit handling; consider restricting to LCC")
    deg_vals = [d for _, d in G.degree()]
    if max(deg_vals) > 0.5 * n:
        warnings.append(f"  ! a node has degree > 50% of network — possible hub artifact or data entry error")
    if not warnings:
        print("  (no warnings)")
    else:
        for w in warnings:
            print(w)

    print("\n" + "=" * 60)
    print(" Next steps suggestions:")
    print("=" * 60)
    if nx.density(G) < 1e-4 and n > 1000:
        print("  - Network is sparse and large: igraph or graph-tool will be much faster than NetworkX")
    if directed:
        print("  - Directed network: prefer Katz or PageRank over eigenvector centrality")
    if nx.number_of_selfloops(G) > 0:
        print("  - Consider G.remove_edges_from(nx.selfloop_edges(G)) before structural analysis")
    if len(isolates) > 0:
        print("  - Restrict to largest component for path-based centralities:")
        print("       G_lcc = G.subgraph(max(nx.connected_components(G), key=len)).copy()")
    if nx.density(G) > 0.3:
        print("  - Dense network: consider backbone extraction (disparity filter) before visualization")
    print()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("path", help="Path to graph file")
    p.add_argument("--directed", action="store_true", help="(edgelist) treat as directed")
    p.add_argument("--weighted", action="store_true", help="(edgelist) read edge weights")
    p.add_argument("--delimiter", default=None, help="(edgelist) field delimiter")
    p.add_argument("--format", choices=["edgelist", "graphml", "gml", "pajek"], default="edgelist")
    args = p.parse_args()

    try:
        G = load_graph(args.path, args.format, args.directed, args.weighted, args.delimiter)
    except Exception as e:
        print(f"Failed to load graph: {e}", file=sys.stderr)
        sys.exit(1)

    report(G)


if __name__ == "__main__":
    main()
