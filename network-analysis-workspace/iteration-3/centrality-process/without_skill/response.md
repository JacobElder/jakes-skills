# Identifying Influential People in Your Advice Network

Great use case. An advice network survey maps informal influence that org charts miss entirely. Here is a practical walkthrough — what centrality measures to compute, what each means for your situation, and how to turn numbers into decisions.

---

## Step 1: Structure your data

Your survey gave you directed edges: person A said they go to person B for advice. That means your network is a **directed graph** where edges point from advice-seeker to advice-giver.

Represent it as an **edge list** (two columns: `from`, `to`) or an **adjacency matrix** (200x200, cell[i][j] = 1 if i goes to j). Either format works with standard tools.

**Recommended tools:**
- Python: `networkx` (free, most flexible)
- R: `igraph` or `tidygraph` + `ggraph`
- No-code: Gephi (GUI, good for visual exploration)

---

## Step 2: The four centrality measures that matter most for your goals

### 1. In-Degree Centrality
**What it is:** Count of how many people named this person as a go-to advisor.

**Formula:** `in-degree(v) / (n - 1)` where n = 200

**What it tells you:** Raw popularity as an advice-giver. High in-degree = many people already trust this person's judgment. This is your simplest and most interpretable signal.

**Best for:** Identifying existing knowledge champions — people the organization has already self-selected.

```python
import networkx as nx
G = nx.DiGraph()
# Add edges from your edge list
in_deg = nx.in_degree_centrality(G)
```

---

### 2. Betweenness Centrality
**What it is:** How often a person sits on the shortest path between two other people in the network.

**Formula:** For each pair (s, t), what fraction of shortest paths between s and t pass through v? Sum over all pairs, normalize.

**What it tells you:** Identifies **brokers** — people who bridge otherwise disconnected groups (e.g., someone who connects the finance team to the product team). These are often not the most popular advisors, but they are the most critical for information flow across the org.

**Best for:** Rolling out a new initiative where you need cross-functional buy-in. A high-betweenness person carries information across silos more efficiently than anyone else. Losing them creates a bottleneck.

```python
betweenness = nx.betweenness_centrality(G, normalized=True)
```

---

### 3. Eigenvector Centrality (or PageRank)
**What it is:** Not just how many people consult you, but whether the people who consult you are themselves influential. Being advised by other high-status advisors multiplies your score.

**PageRank** is the directed-graph variant (what Google originally used) and handles directed networks more robustly than plain eigenvector centrality.

**What it tells you:** Identifies **high-leverage influencers** whose reach is amplified through the people they influence. A person consulted by five VPs has more eigenvector/PageRank centrality than one consulted by twenty junior analysts — even if in-degree favors the latter.

**Best for:** Deciding who to brief first on a new initiative. If you convince a high-PageRank person, their endorsement propagates through the high-influence tier of the network.

```python
pagerank = nx.pagerank(G, alpha=0.85)
```

---

### 4. Closeness Centrality
**What it is:** Average shortest path distance from a node to all others, inverted. High closeness = can reach (or be reached by) everyone quickly.

**What it tells you:** Identifies people who can **diffuse information quickly** across the whole org, not just their immediate cluster.

**Best for:** Identifying who to use as communication hubs if you need a message to propagate broadly and fast.

```python
# Note: for directed graphs, use in-closeness (how quickly others can reach v)
closeness = nx.closeness_centrality(G.reverse())
```

---

## Step 3: Which measure to use for each decision

| Goal | Primary metric | Secondary metric |
|---|---|---|
| Knowledge champions (deep expertise, already trusted) | In-degree | PageRank |
| Cross-functional initiative rollout (reach across silos) | Betweenness | Closeness |
| Early briefing list (influence multiplier) | PageRank | In-degree |
| Identifying single points of failure / key dependencies | Betweenness | — |
| Fast org-wide message diffusion | Closeness | Betweenness |

For your two stated goals specifically:

- **Internal knowledge champions:** Start with in-degree. These are people the org has already organically identified as go-to experts. Combine with PageRank to up-weight those whose advice-seekers are themselves advice-givers — that gives you people with genuine depth of influence, not just volume.

- **Who to loop in early on a new initiative:** Betweenness is your primary signal. You want brokers who span teams. A high-betweenness person in the middle of your org can carry your message to clusters that would otherwise be hard to reach. Supplement with PageRank to ensure the people you loop in are respected by other respected people.

---

## Step 4: A practical workflow

1. **Build the graph.** Load your edge list into networkx or igraph.

2. **Compute all four metrics.** It takes under a second for 200 nodes.

3. **Normalize and rank.** Sort each metric descending, keep the top 10-15% (roughly top 20-30 people) for each.

4. **Look for overlap.** People who appear in the top tier on multiple measures are your highest-priority targets. A person in the top 10% on in-degree, betweenness, and PageRank simultaneously is extremely valuable.

5. **Visualize.** Even a simple force-directed layout (Gephi, or `matplotlib` + `networkx`) colored by betweenness will make the broker structure immediately obvious. Clusters = teams or functions. Narrow bridges = your high-betweenness people.

6. **Sanity-check against org chart.** High-centrality people are often (but not always) senior. If you find a mid-level analyst in the top 5 on betweenness, that is a genuine insight — they are a hidden connector worth engaging.

---

## Step 5: Things to watch out for

**Reciprocity vs. direction.** Make sure you are using the directed graph. If you accidentally treat it as undirected you lose the distinction between givers and seekers.

**Self-nomination bias.** People may over-report prestigious advisors (the CEO) or under-report peers. Betweenness is more robust to this than in-degree because it is structural, not just vote-counting.

**Isolates.** Some employees may not appear in anyone's answers (no one goes to them) or may not have named anyone. Check your degree distribution. A person with in-degree 0 is not an advice-giver at all; a person with out-degree 0 either did not respond or claims not to seek advice.

**Community structure.** Before finalizing your knowledge champion list, check whether high-in-degree people are clustered within a single team. If all your top-in-degree nodes are in the finance function, you have good coverage there but a gap everywhere else. Use community detection (Louvain algorithm: `python-louvain` or `igraph::cluster_louvain`) to find natural clusters, then ensure you have a champion candidate from each.

---

## Minimal working code (Python/networkx)

```python
import networkx as nx
import pandas as pd

# Load edge list: columns 'from_id', 'to_id'
df = pd.read_csv("advice_network.csv")

G = nx.DiGraph()
G.add_edges_from(zip(df["from_id"], df["to_id"]))

results = pd.DataFrame({
    "in_degree":    nx.in_degree_centrality(G),
    "betweenness":  nx.betweenness_centrality(G, normalized=True),
    "pagerank":     nx.pagerank(G, alpha=0.85),
    "closeness":    nx.closeness_centrality(G.reverse()),  # in-closeness
}).sort_values("pagerank", ascending=False)

print(results.head(20))
```

This gives you a ranked table of the top 20 people across all four metrics. From there, the people at the top of multiple columns are your knowledge champion and early-briefing targets.
