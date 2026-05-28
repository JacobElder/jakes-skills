# Response: Temporal Email Network Analysis

## Short answer

The aggregation-first plan is a reasonable starting point but has a critical flaw for several of the questions you likely care about: **collapsing 3 years of timestamped interactions into a single weighted adjacency matrix destroys the temporal structure that carries most of the substantive information in an email dataset**. For some descriptive purposes the aggregate is fine; for identifying "key communicators" it may give you the wrong answer. Here is a full breakdown.

---

## Step 1: Classify your network

Before any analysis, establish what kind of network you have:

| Axis | This dataset |
|---|---|
| Mode | One-mode (employee → employee) |
| Directionality | **Directed** — sender ≠ recipient; email volume asymmetries are meaningful |
| Weight | Weighted (count of emails per ordered pair) |
| Multiplicity | Single relation (email), but you could split by thread/topic to get multiplex |
| Time | **Continuous-time event sequence** — this is the critical one |
| Boundary | Complete (you have all 450 employees) |
| Scale | Medium (450 nodes); the 2.3M edges in the aggregate are still tractable with igraph or even NetworkX |

The time axis is the problem. Your data is a **temporal network** — a sequence of (sender, recipient, timestamp) events. It is not a static weighted graph with noise; the timing is load-bearing information.

---

## What you lose by aggregating

Collapsing to a weighted adjacency matrix loses at least three things:

**1. Causal ordering (time-respecting paths)**
In a temporal network, information can flow from A to C through B only if the A→B email happens *before* the B→C email. The aggregated graph treats all paths as valid regardless of order. This means your static centrality measures will count paths that cannot actually carry information — betweenness and closeness centralities computed on the aggregate will be **systematically inflated** for nodes that happen to receive early and send late, but not vice versa.

Formally: a time-respecting path from i to j is a sequence of contacts at times t₁ < t₂ < ... < tₖ. Static analysis ignores this ordering. Studies of email and call networks (Holme & Saramäki 2012) show that temporal reachability is typically **30–70% lower** than static reachability — many pairs that appear connected in the aggregate graph cannot actually relay information to each other.

**2. Burstiness and inter-event times**
Real email communication is heavy-tailed: long silent periods followed by bursts. A sender who exchanges 200 emails with a colleague in a single crisis week looks the same in your aggregate as someone who sends 200 emails spread evenly over 3 years. These are very different communication relationships. Bursty patterns also **slow down spreading** through the network compared to what static models predict (Karsai et al. 2011).

**3. Recurrence vs. one-shot**
Consistent daily contact vs. a single dense thread both collapse to the same edge weight (or near it). These have completely different structural implications for who is a reliable communication bridge.

---

## Where the aggregate *is* fine

The static weighted graph is a reasonable approximation when you want:

- **Descriptive volume statistics**: who sends the most email, which dyads communicate most frequently. This is just degree / strength and the aggregate is correct for it.
- **Stable structural features that don't depend on path timing**: broad community structure among employees who communicate, overall density of communication, rough clustering patterns.
- **A baseline** before doing temporal analysis — it's always worth computing the aggregate as a reference.

---

## The "key communicators" problem

"Key communicators" is ambiguous — it maps to at least three different network concepts, and the right choice depends on your substantive question:

| What you mean by "key" | Metric | Works on aggregate? |
|---|---|---|
| Sends/receives the most email (volume) | Weighted in-degree / out-degree | Yes |
| Bridges between otherwise disconnected groups | Betweenness centrality | Partially — see caveat below |
| Information reaches them early and they relay it fast | Temporal betweenness / foremost-path centrality | No — requires timestamps |
| Well-connected to other well-connected people (status) | PageRank or eigenvector centrality | Partially |

**The betweenness caveat**: static betweenness on the aggregate counts all paths. Temporal betweenness counts only *time-respecting* shortest paths. These can produce **qualitatively different rankings**. A person who sits between two groups but always emails group A before group B (never the other direction) will look like a broker statically but may not be a temporal bridge at all.

If your goal is to identify people whose removal would disrupt information flow, or people who could seed a message that would spread fastest, you need temporal betweenness, not static betweenness.

---

## Recommended approach

### Option A: Aggregate + acknowledge limitations (fast, defensible)

If your question is primarily about communication volume and stable structural position:

1. Build the directed, weighted aggregate graph (weight = total emails sent, or optionally log(1 + count) to dampen outliers).
2. Compute baseline structure first:
   - n nodes, m directed edges, density, weakly connected components
   - In-degree and out-degree distributions (expect heavy tails)
   - Reciprocity (what fraction of pairs email both ways?)
   - Transitivity / clustering coefficient
3. For centrality: use **weighted in-degree** for "who is most contacted" (volume), **PageRank** for "who is reached by the most information" (works on directed networks, unlike eigenvector centrality which can fail on directed graphs with weak components), and **betweenness** for brokerage — but explicitly caveat that betweenness on the aggregate overestimates brokerage for nodes that serve as temporal relays.
4. State explicitly: "This analysis treats the 3-year email record as a static snapshot. Conclusions about information flow and brokerage are upper bounds; actual temporal reachability is likely 30–70% lower."

```python
import networkx as nx
import pandas as pd

# df has columns: sender, recipient, timestamp
edges = df.groupby(['sender', 'recipient']).size().reset_index(name='weight')
G = nx.from_pandas_edgelist(edges, 'sender', 'recipient', 
                             edge_attr='weight', create_using=nx.DiGraph())

print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}")
print(f"density={nx.density(G):.4f}")
print(f"weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"reciprocity: {nx.reciprocity(G):.3f}")

G_lwcc = G.subgraph(max(nx.weakly_connected_components(G), key=len)).copy()

# Centrality
in_deg = dict(G.in_degree(weight='weight'))
pr = nx.pagerank(G, alpha=0.85, weight='weight')
btw = nx.betweenness_centrality(G_lwcc, normalized=True, weight='weight')
```

### Option B: Temporal snapshot panel (better, moderate effort)

Aggregate into time windows (e.g., monthly or quarterly for a 3-year dataset) and analyze as a panel. This lets you:

- Track how the communication network evolves: who becomes central, when do communities form or dissolve?
- Use STERGM or SAOM to model tie formation and dissolution statistically
- Compare centrality measures across periods to find consistently vs. transiently central employees

Window choice: use **monthly** windows for a 3-year dataset (36 snapshots). Check sensitivity against weekly and quarterly.

### Option C: Full temporal analysis (best, most effort)

Use the raw event sequence. This is appropriate if your question is about information propagation, influence, or real-time communication dynamics.

- Compute **temporal betweenness** and **temporal closeness** using `teneto` (Python) or `pathpy`
- Compute **temporal motifs** (e.g., forwarding: A→B then B→C within Δt; reciprocation: A→B then B→A within Δt) to characterize communication patterns — these reveal whether email culture is hierarchical, reciprocal, or broadcast-style
- Compare metrics to a **time-shuffled null model** (keep the static graph, randomize timestamps) to identify what is due to *who* communicates vs. *when*

```python
import teneto

# Build TemporalNetwork from event list
# teneto expects (i, j, t) tuples
tn = teneto.TemporalNetwork(from_df=df, 
                             columns=['sender', 'recipient', 'timestamp'])
tc = teneto.networkmeasures.temporal_closeness_centrality(tn)
tb = teneto.networkmeasures.temporal_betweenness_centrality(tn)
```

---

## The one mistake to avoid right now

Do not compute static betweenness on the aggregate and report it as measuring "information brokerage" without the temporal caveat. This is the most common error in email network analysis. The aggregate betweenness tells you about structural position in the communication volume graph; it does not tell you who controls the flow of *timely* information. These can differ substantially.

---

## Recommended starting workflow

1. Build the aggregate directed weighted graph. Run baseline stats (n, m, density, reciprocity, degree distribution).
2. Check if the degree distribution is heavy-tailed (log-log plot). If so, note that a small number of employees dominate by volume — this shapes all downstream centrality results.
3. For centrality, compute weighted in-degree (volume received), PageRank (weighted), and betweenness — report all three with explicit interpretation of what each measures.
4. Build monthly snapshots and track centrality rank stability over time. Employees who are consistently high-centrality are different from those with a single active period.
5. If the core question is about real-time influence or information speed, invest in temporal betweenness via `teneto` or `pathpy`.

---

## References

- Holme, P. & Saramäki, J. (2012). "Temporal networks." *Physics Reports* 519: 97–125.
- Karsai, M. et al. (2011). "Small but slow world." *Physical Review E* 83: 025102.
- Kovanen, L. et al. (2011). "Temporal motifs in time-dependent networks." *J. Statistical Mechanics* P11005.
- Masuda, N. & Lambiotte, R. (2020). *A Guide to Temporal Networks* (2nd ed.). World Scientific.
