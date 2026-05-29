# Response: Temporal Aggregation for Email SNA

Your plan is a reasonable starting point, but it has one significant methodological gap that can produce misleading conclusions — and a few execution details worth getting right before you run anything. Let me go through both.

---

## What your plan gets right

You have a directed, weighted, one-mode network (employees → employees, weight = email count). That's correct framing. Computing standard SNA metrics on it is appropriate for many questions about communication volume and structural position.

Your network dimensions: 450 nodes, potentially hundreds of thousands of edges (after aggregating 2.3M emails). At that scale, NetworkX is fine for most computations; igraph is a faster alternative if centrality calculations feel slow.

---

## The core problem: aggregating over 3 years destroys temporal ordering

This is not a minor nuance — it fundamentally changes what your metrics measure.

When you aggregate 3 years of email into a single weighted matrix, you lose **causal ordering**. An email chain where Alice emails Bob on day 1 and Bob emails Carol on day 2 is a genuine information path: Alice → Bob → Carol. But a chain where Alice emails Bob on day 400 and Bob emailed Carol on day 2 is *not* — Carol couldn't have received information that Alice hadn't sent yet. The static graph treats both as equivalent, because both show edges A→B and B→C with nonzero weight.

This matters for centrality. **Static betweenness centrality counts shortest paths that don't exist as actual communication sequences.** The ranking it produces is not the ranking of real information brokers — it's the ranking of people who sit on paths that *would* exist if time were ignored.

The empirical evidence on this (Holme & Saramäki 2012; Karsai et al. 2011) consistently shows that **temporal betweenness and static betweenness can rank nodes in qualitatively different — not just quantitatively rescaled — orders**. A node ranked #1 by static betweenness may rank near the bottom by temporal betweenness if those aggregate paths don't exist as time-respecting sequences. A node that looks peripheral statically may be a consistent temporal bridge at exactly the right moments and rank highly temporally. This is rank inversion, not scaling.

You also lose:

- **Burstiness and inter-event times**: if two people exchange 100 emails in one intense week and then nothing for 2.9 years, versus 100 emails spread evenly over the period, the static graph gives them identical edge weights. But the patterns of who relays information to whom are completely different. Bursty interaction patterns are known to *slow down* spreading relative to uniform-frequency equivalents.
- **Tie persistence vs. intermittent contact**: an edge weight of 50 could mean a steady relationship or sporadic contact.
- **Changes over time**: did communication patterns shift? Did key communicators change roles, leave, or emerge? The static aggregate buries this.

---

## What to do instead (or in addition)

### Option A: Temporal snapshots (recommended first step)

If you want to preserve your current workflow but partially address the temporal problem, aggregate into time windows — monthly or quarterly is natural for organizational communication — and compute your metrics on each snapshot. Then:

1. Track centrality rankings over time for each individual
2. Check whether your "key communicators" are consistently central or artifacts of one unusual period
3. Use multi-scale analysis: compute metrics at weekly, monthly, and quarterly resolution and look for stable features

This is not as rigorous as full temporal analysis, but it's far better than a single 3-year aggregate, and it directly reveals temporal dynamics that will be substantively meaningful to the organization.

### Option B: Time-respecting paths (proper temporal SNA)

For a principled treatment, keep the timestamps and work with **time-respecting paths**: a path i → x₁ → x₂ → j is only valid if the edges are traversed in chronological order (contact at t₁ < t₂ < t₃). Reachability, latency, and centrality computed on time-respecting paths answer the right questions about who can actually relay information to whom.

Python libraries for this:
- `pathpy` (Scholtes): higher-order temporal networks, time-respecting path computation
- `teneto` (Thompson): temporal centrality measures, fluctuation analysis
- `Raphtory`: streaming/incremental analysis, scales well

In Python, if you want to start simpler, you can compute temporal betweenness by enumerating time-ordered paths on slices of the event sequence. `pathpy` has built-in support for this.

### Option C: Relational Event Models (if you want to model *why* people email whom)

If your goal goes beyond description to inference — what predicts each email event? — Relational Event Models (Butts 2008; `relevent` or `goldfish` in R) treat each (sender, recipient, timestamp) triple as a discrete-choice realization. This is to temporal networks what ERGMs are to static networks, but defined on event sequences.

---

## Execution details for your static analysis (if you proceed with aggregation)

Even if you proceed with the static aggregate as a starting point, a few things to get right:

**1. Treat this as a directed network.** Person A sending 100 emails to B and B never replying is structurally different from 100 emails in both directions. Keep directionality; it affects betweenness, PageRank, and all centrality measures.

**2. Choose the right centrality for "key communicators."**

There is no single "key communicator" metric. What does "key" mean for your question?

| Meaning of "key" | Metric to use |
|---|---|
| Highest email volume | Out-degree (emails sent) or total degree |
| Reaches others most quickly | Closeness centrality (on the LWCC only — see below) |
| Information broker between groups | Betweenness centrality |
| Connected to other high-senders | PageRank (better than eigenvector on directed networks) |
| Reciprocal relationships | Reciprocity per node |

Do not use eigenvector centrality on a directed network without strong components — it is undefined or gives nonsensical results. Use PageRank instead.

**3. Handle disconnected components.** With 450 employees, your graph almost certainly has some isolates and possibly small weakly connected components. Closeness centrality is undefined for nodes not reachable from/to others. Either restrict closeness to the largest weakly connected component (and say so explicitly) or use harmonic centrality, which handles unreachable pairs gracefully.

**4. Compare to a null model.** Raw centrality scores are uninterpretable without a reference distribution. Use the configuration model (same degree sequence, randomized edges) to establish what betweenness or clustering coefficient you'd expect by chance. A node's betweenness is "high" only relative to the null.

**5. Inspect before computing.** Print these numbers before running any centrality:

```python
import networkx as nx
import pandas as pd

# Build the graph from your (sender, recipient, timestamp) dataframe
df = pd.read_csv("emails.csv")
edge_counts = df.groupby(["sender", "recipient"]).size().reset_index(name="weight")
G = nx.from_pandas_edgelist(edge_counts, "sender", "recipient", edge_attr="weight",
                             create_using=nx.DiGraph())

print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}")
print(f"density={nx.density(G):.4f}")
print(f"weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"strongly connected components: {nx.number_strongly_connected_components(G)}")
print(f"reciprocity: {nx.reciprocity(G):.3f}")

# Largest weakly connected component
lwcc = max(nx.weakly_connected_components(G), key=len)
G_lwcc = G.subgraph(lwcc).copy()
print(f"LWCC size: {G_lwcc.number_of_nodes()} nodes")
```

A reciprocity value near 1 means most emails get replies (typical in organizational communication); near 0 means directional broadcasting. This framing shapes everything about how to interpret centrality.

---

## Summary recommendation

Your aggregation plan will give you a serviceable first-pass picture of volume-based communication patterns. But if you're making decisions based on who the "key communicators" are — HR decisions, change management, information security — you should be aware that static betweenness rankings may not reflect who actually bridges information across the organization, because timing determines whether those paths are real.

A practical path forward:
1. Run the static analysis as a baseline — it's fast and gives context
2. Immediately follow it with monthly/quarterly snapshots and check whether rankings are stable
3. For any specific claim about information flow or influence, compute temporal betweenness on time-respecting paths using `pathpy` or `teneto`

The 3-year temporal scope and 2.3M event scale are actually well within the range where temporal analysis is tractable and where temporal-vs-static discrepancies are well-documented in the literature (Karsai et al. 2011 on email datasets specifically found meaningful differences). Don't leave that data on the floor.
