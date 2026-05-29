# Response: Temporal Aggregation in Email SNA

Your plan — collapse all 2.3M emails into a single weighted adjacency matrix and run standard SNA metrics — is a reasonable starting point, but it has a specific and well-documented flaw that you should understand before committing to it. Whether it "works" depends on what questions you want to answer.

---

## First, classify the network you have

Before any method choice, be explicit about what you have:

- **Mode**: one-mode (employees → employees) — ✓ standard SNA applies
- **Directionality**: directed. Emails are inherently asymmetric: A sending 100 emails to B is not the same as B sending 100 emails to A. Do not symmetrize unless you have a specific reason.
- **Weight**: frequency counts (number of emails sent) — use as weighted edges; treat with caution (see below)
- **Time**: you have continuous-time event sequences — this is where the plan needs scrutiny
- **Boundary**: complete network of 450 employees — well-defined, good
- **Scale**: medium (~450 nodes, potentially tens of thousands of edges after aggregation). NetworkX handles this fine.

---

## The core problem with full aggregation

When you collapse all 2.3M emails across 3 years into a single matrix, you lose at minimum three things:

1. **Causal ordering.** In reality, B can only relay information from A to C if A→B happened *before* B→C. In your aggregated graph, A→B and B→C exist as edges regardless of when they occurred, so the graph implies reachability that doesn't exist temporally. Holme & Saramäki (2012) show that reachability on the empirical temporal network is typically 30–70% *lower* than on the aggregated static version. Your betweenness and closeness centralities will systematically overestimate how well-connected brokers and bridges actually are.

2. **Burstiness and inter-event times.** Communication is not uniform over time. An employee who sends 50 emails to a colleague in one intense week followed by 10 months of silence looks identical in the aggregate to one who sends 1 email per week for the whole year. These represent very different communication relationships. Karsai et al. (2011) show that bursty contact patterns actually *slow down* spreading processes compared to what the aggregate graph predicts — which directly affects how you interpret centrality as influence.

3. **Temporal change.** A 3-year window is long. Organizations restructure, teams form and dissolve, employees join and leave. The "communication network" at month 1 may be meaningfully different from month 36. Aggregating treats the network as if it were static throughout, which may obscure the very patterns you care about (e.g., a key communicator who left 18 months ago will still look central).

---

## What the approach does and doesn't give you

**The aggregate-then-analyze approach is appropriate for:**
- Describing the overall relational structure of the organization across the full period
- Identifying employees with persistently high communication activity (high weighted degree)
- Detecting stable community structure (teams/departments) if they persisted throughout the 3 years
- A fast first pass to understand the data shape before committing to more complex methods

**It is misleading for:**
- Claims about information flow, influence, or who would be a good target for spreading a message — these require time-respecting paths
- Identifying brokers or bridges (betweenness) — aggregate betweenness counts paths that don't exist temporally
- Understanding how communication patterns evolved — the aggregate erases this entirely
- Any causal interpretation ("this person connects these groups") — see note on brokerage below

---

## Concrete recommendations

### Step 1: Inspect the data before building the matrix

Before aggregating anything, run basic diagnostics on the raw event data:

```python
import pandas as pd
import networkx as nx

df = pd.read_csv("emails.csv", parse_dates=["timestamp"])

# Basic checks
print(df.shape)                          # should be ~2.3M rows
print(df.dtypes)                         # confirm timestamp is datetime
print(df[["sender", "recipient"]].nunique())  # should be ~450 unique senders/recipients
print(df.groupby("sender")["recipient"].nunique().describe())  # degree distribution preview
print(df["timestamp"].min(), df["timestamp"].max())  # confirm 3-year span
print((df["sender"] == df["recipient"]).sum())  # self-loops — common in email data, usually drop
```

Especially check for self-loops (CC-to-self, automated notifications). These are common in email data and will inflate self-weights.

### Step 2: Build the directed weighted aggregate graph

```python
# Drop self-loops
df = df[df["sender"] != df["recipient"]]

# Build directed weighted edge list
edges = (df.groupby(["sender", "recipient"])
           .size()
           .reset_index(name="weight"))

G = nx.from_pandas_edgelist(
    edges,
    source="sender",
    target="recipient",
    edge_attr="weight",
    create_using=nx.DiGraph()
)

print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}, density={nx.density(G):.4f}")
print(f"weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"reciprocity: {nx.reciprocity(G):.3f}")

G_lwcc = G.subgraph(max(nx.weakly_connected_components(G), key=len)).copy()
```

### Step 3: Compute baseline structure before any centrality

```python
print(f"transitivity: {nx.transitivity(G):.3f}")
print(f"degree assortativity: {nx.degree_assortativity_coefficient(G):.3f}")

# In-degree distribution — who receives the most email? (proxies for status/workload)
in_deg = dict(G.in_degree(weight="weight"))
out_deg = dict(G.out_degree(weight="weight"))
```

### Step 4: Pick centralities that match your substantive question

"Key communicators" is ambiguous. What do you mean?

| What "key" means | Centrality to use | Caution |
|---|---|---|
| Who sends/receives the most email overall | Weighted in/out-degree | Straightforward; no approximation issues |
| Who bridges disconnected groups (broker) | Betweenness centrality | *Overestimates* on aggregate; treat as screening, not ground truth |
| Who is reachable fastest for spreading news | PageRank or temporal analysis | Aggregate PageRank ignores timing |
| Who is connected to other well-connected people | Katz or PageRank (not eigenvector) | Use Katz/PageRank on directed; eigenvector is undefined for directed networks without strong components |

```python
# Weighted degree — safe and interpretable
in_degree_centrality = {n: G.in_degree(n, weight="weight") for n in G.nodes()}

# Betweenness — restrict to LWCC; note this assumes time-respecting paths
btw = nx.betweenness_centrality(G_lwcc, weight=None, normalized=True)  # unweighted paths

# PageRank — handles directed graph cleanly
pr = nx.pagerank(G, alpha=0.85, weight="weight")

top_10_by_pagerank = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]
```

**Do not use eigenvector centrality on this directed graph.** It is undefined in the presence of nodes outside the strongly connected component, which is almost certainly the case here. Use PageRank instead.

---

## What you should do beyond static aggregation

Given that you have continuous-time event data over 3 years, you have the raw material for much richer analysis. Two paths forward:

### Option A: Snapshot sequence (if you want to track change without full temporal modeling)

Divide the 3 years into monthly or quarterly snapshots. For each snapshot:

```python
snapshots = {}
for period, group in df.groupby(df["timestamp"].dt.to_period("M")):
    edges_p = (group.groupby(["sender", "recipient"]).size().reset_index(name="weight"))
    G_p = nx.from_pandas_edgelist(edges_p, source="sender", target="recipient",
                                   edge_attr="weight", create_using=nx.DiGraph())
    snapshots[period] = G_p
```

Then track centrality rankings, community structure, or density over time. This reveals whether a person's centrality is persistent or episodic — an important distinction that the 3-year aggregate hides entirely.

The critical warning here: choose the window size deliberately. For human communication, monthly windows are often natural (match project cycles, reporting periods). Check that the mean inter-event time between a given pair is much shorter than your window — if two employees email each other once a quarter, a monthly window will show most windows as empty.

### Option B: True temporal network analysis (if information flow / influence is your goal)

If your core question is "who would be most effective for spreading information?" or "how quickly does a message propagate through this organization?", the aggregate approach is structurally wrong and temporal analysis is warranted.

Use `pathpy` or `teneto`:

```python
# pathpy example
import pathpy as pp

t = pp.TemporalNetwork()
for _, row in df.iterrows():
    t.add_edge(row["sender"], row["recipient"], row["timestamp"].timestamp())

# Compute temporal betweenness (time-respecting paths only)
# pathpy will only count paths where contact timestamps are increasing
```

This correctly measures brokerage: an employee who happens to be in a communication chain at the right time (when information is actually flowing) vs. one who communicates frequently but never in a relay-enabling sequence.

### Option C: Relational Event Modeling (if you want to model *why* each email happened)

If your goal is explanatory — what organizational factors predict communication? — then Relational Event Models (Butts 2008) are the right framework. Each email is modeled as a discrete choice: given that employee i sent an email at time t, why did they choose recipient j? The rate function can include recency of prior contact, organizational hierarchy, team membership, and so on.

R package: `relevent` or `goldfish` (DyNAM). This is more involved but gives you interpretable, causally-framed estimates rather than descriptive centrality rankings.

---

## On community detection (if you plan to find teams/departments)

If you plan to detect communities in the aggregated graph:

- **Do not use a single Louvain run and call it "the" communities.** Modularity is degenerate — many qualitatively different partitions have near-identical modularity scores (Good et al. 2010). Run at least 100 times, compute pairwise NMI/ARI across runs to measure stability, then build a consensus partition.
- **Compare to a null model.** A modularity of Q = 0.45 means nothing unless you compare it to what a configuration model with the same degree sequence would produce.
- **Preferred alternative**: use Leiden with the Constant Potts Model, or a Stochastic Block Model (graph-tool's nested SBM), which is generative and principled. For an organizational email network, the SBM is particularly useful because it can find hierarchical community structure (teams within departments).

---

## Summary: Does your plan work?

The plan is a defensible first pass for descriptive questions about who communicates frequently with whom and what the broad community structure looks like. For those purposes, it is fine.

It is insufficient or misleading for:

1. **Claims about information flow or influence** — these require temporal analysis, because aggregate centrality counts paths that don't exist in time
2. **Understanding how communication evolved over 3 years** — the aggregate is silent on this
3. **Identifying brokers** — aggregate betweenness overstates brokerage; a temporal betweenness on time-respecting paths is more honest

The minimum viable improvement is to segment the 3 years into monthly or quarterly snapshots and track how the network changes, rather than treating it as a single static entity. If the question is specifically about information propagation or "who should I email to reach the whole company fastest," shift to temporal path analysis using pathpy or teneto.

---

## References

- Holme, P. & Saramäki, J. (2012). Temporal networks. *Physics Reports* 519: 97–125.
- Karsai, M. et al. (2011). Small but slow world: How network topology and burstiness slow down spreading. *Physical Review E* 83: 025102.
- Butts, C. T. (2008). A relational event framework for social action. *Sociological Methodology* 38: 155–200.
- Good, B. H., de Montjoye, Y.-A., & Clauset, A. (2010). Performance of modularity maximization in practical contexts. *Physical Review E* 81: 046106.
