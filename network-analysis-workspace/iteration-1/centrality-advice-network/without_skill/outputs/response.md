# Identifying Influential People in Your Advice Network

Great use case — advice network data is one of the richest sources of organizational intelligence you can get. Here's how to approach this systematically.

---

## Step 1: Structure Your Data

Your survey responses should be structured as a directed edge list: each row represents "Person A goes to Person B for advice," meaning B is the advice-giver (the influential party).

```
from_id, to_id
employee_001, employee_045
employee_002, employee_012
...
```

If you collected this in a spreadsheet, you can export it as CSV and load it into Python (NetworkX), R (igraph), or a tool like Gephi or NodeXL.

---

## Step 2: Understand What Centrality Measures Actually Mean

There are four key centrality measures, each answering a different question:

### 1. In-Degree Centrality
**Question answered:** Who gets nominated most often as a go-to advisor?

- Simply the count (or proportion) of incoming nominations each person receives.
- Highest in-degree = most frequently sought out for advice.
- **Best for:** Identifying the obvious knowledge hubs — the people everyone already knows to call.

```python
import networkx as nx
G = nx.from_pandas_edgelist(df, source='from_id', target='to_id', create_using=nx.DiGraph())
in_degree = dict(G.in_degree())
```

### 2. Betweenness Centrality
**Question answered:** Who sits on the shortest paths between many pairs of people?

- High betweenness = a person who acts as a bridge connecting otherwise disconnected parts of the organization.
- These are **critical information brokers** — remove them and knowledge flow breaks down.
- **Best for:** Finding the "connectors" who bridge departments, levels, or cliques. These are your highest-leverage early targets for a rollout because they carry information across silos.

```python
betweenness = nx.betweenness_centrality(G, normalized=True)
```

### 3. Closeness Centrality
**Question answered:** How quickly can a person reach (or be reached by) everyone else in the network?

- High closeness = can disseminate information to the whole organization quickly.
- **Best for:** Identifying people who would be efficient messengers — if you tell them something, news travels fast.

```python
closeness = nx.closeness_centrality(G)
```

### 4. PageRank (Eigenvector-family)
**Question answered:** Who is nominated by other well-connected people?

- Not just about raw nominations — it weights nominations by the prestige of the nominator. Being sought by high-centrality colleagues counts more than being sought by peripheral employees.
- PageRank is the directed-graph version of eigenvector centrality, and it's usually the most robust for advice networks.
- **Best for:** Finding the "hidden heavyweights" — people who may not have the highest raw nomination count, but whose advice-seekers are themselves influential.

```python
pagerank = nx.pagerank(G, alpha=0.85)
```

---

## Step 3: Compute and Rank

Run all four and build a combined table. Here's a minimal working example in Python:

```python
import pandas as pd
import networkx as nx

# Load your edge list
df = pd.read_csv('advice_network.csv')  # columns: from_id, to_id

G = nx.from_pandas_edgelist(df, source='from_id', target='to_id', create_using=nx.DiGraph())

# Compute centrality measures
results = pd.DataFrame({
    'in_degree':    pd.Series(dict(G.in_degree())),
    'betweenness':  pd.Series(nx.betweenness_centrality(G, normalized=True)),
    'closeness':    pd.Series(nx.closeness_centrality(G)),
    'pagerank':     pd.Series(nx.pagerank(G, alpha=0.85))
})

# Normalize each column to 0-1 and sum for a composite score
results_norm = (results - results.min()) / (results.max() - results.min())
results['composite_score'] = results_norm.sum(axis=1)

results_sorted = results.sort_values('composite_score', ascending=False)
print(results_sorted.head(20))
```

---

## Step 4: Interpret the Results for Your Use Case

### For "Knowledge Champions" (internal expertise ambassadors):

Target people who are **high on in-degree AND PageRank**. These are the people employees genuinely trust and already route their questions through. They have:
- Demonstrated expertise (people seek them out)
- Peer credibility (the nomination comes organically, not from org chart position)

Look especially for people who rank high on these measures but are **not** in senior leadership — these are often your most effective grassroots champions because they have influence without the authority bias.

### For "Early Initiative Rollout" targets:

Target people who are **high on betweenness centrality**. These are your cross-silo bridges. When you brief them early:
- Information flows across departmental boundaries faster
- You reduce the chance that a whole pocket of the org is left out of the loop
- They often surface concerns from underrepresented clusters that leadership wouldn't otherwise hear

A practical heuristic: brief your **top 10-15% on betweenness** before any company-wide announcement. This is your seeding strategy.

### Watch for: Isolates and Peripheral Clusters

Also look at the other end — employees with low in-degree who are also not connected to high-centrality people. These are your **change-adoption risk areas**: pockets of people who are underserved by the informal knowledge network and may be last to hear about and adapt to new initiatives.

---

## Step 5: Validate and Add Context

Raw centrality scores can mislead if interpreted without context:

- **Control for org-chart position:** A VP may have high in-degree simply because of authority. Compare within-level — who has unusually high centrality for their seniority?
- **Check for recency/tenure effects:** Long-tenured employees often have high centrality by default. Is their centrality "earned" or legacy?
- **Look at ego networks:** For your top candidates, visualize their immediate neighborhood (1-2 hops) to understand what part of the org they're really central to — a person may be central globally but only because they're a super-hub in one department.

---

## Recommended Tools

| Tool | Best for | Notes |
|------|----------|-------|
| **Python + NetworkX** | Full analysis, reproducibility | Most flexible; add pandas for data wrangling |
| **R + igraph** | Statisticians already in R | Excellent centrality functions and visualization |
| **Gephi** | Visual exploration, non-programmers | Free, drag-and-drop graph visualization |
| **NodeXL** | Excel-native workflow | Good for quick exploration if team lives in Excel |

---

## Summary: Priority Targeting Logic

| Goal | Primary Metric | Secondary Check |
|------|---------------|-----------------|
| Knowledge Champions | PageRank + In-Degree | Non-leadership, broad reach |
| Rollout early-briefing targets | Betweenness Centrality | Cross-departmental bridges |
| Fast information spread | Closeness Centrality | Message dissemination speed |
| Adoption risk monitoring | Low in-degree + peripheral | Underserved clusters |

Start with the composite score to get a ranked list, then apply the above lenses to pick the right people for the right role. In a 200-person network, you're probably looking at a shortlist of 15-25 people across these categories.
