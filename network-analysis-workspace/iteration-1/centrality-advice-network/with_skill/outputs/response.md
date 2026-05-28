# Identifying Central/Influential People in Your Advice Network

## First: classify your network before computing anything

Based on what you've described, your advice network has the following properties that drive every methodological choice:

- **Mode**: one-mode (people → people)
- **Directionality**: **directed** — employee A saying "I go to B for advice" is not the same as B saying "I go to A." This is asymmetric and meaningful. The direction tells you who is *sought out* (high in-degree = prestigious, trusted) versus who is *actively seeking* (high out-degree = engaged, possibly less confident).
- **Weight**: likely binary (tie/no tie) from a survey, unless you also captured frequency or you allowed multiple nominees per respondent
- **Scale**: small (n=200) — NetworkX is entirely sufficient
- **Boundary**: complete network (all 200 employees were surveyed) — this is good; it means centrality estimates are reliable within this population

**Critical implication of directionality**: several standard centrality algorithms behave incorrectly or deceptively on directed networks if you're not careful. I'll flag each one.

---

## Inspect the network before computing centrality

Before touching centrality, print these diagnostics:

```python
import networkx as nx

# Load: rows are "respondent → advisee" directed edges
G = nx.read_edgelist("advice_edges.csv", create_using=nx.DiGraph, delimiter=",")

print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}")
print(f"density={nx.density(G):.4f}")
print(f"weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"strongly connected components: {nx.number_strongly_connected_components(G)}")
print(f"reciprocity: {nx.reciprocity(G):.3f}")  # % of ties that are mutual
print(f"transitivity: {nx.transitivity(G):.3f}")

# Degree distribution summary (in vs out)
in_deg  = [d for _, d in G.in_degree()]
out_deg = [d for _, d in G.out_degree()]
import numpy as np
print(f"in-degree  — mean: {np.mean(in_deg):.1f}, max: {max(in_deg)}, median: {np.median(in_deg):.1f}")
print(f"out-degree — mean: {np.mean(out_deg):.1f}, max: {max(out_deg)}, median: {np.median(out_deg):.1f}")
```

**Reciprocity** tells you how often advice-seeking is mutual. If it's very low (say < 0.15), the network is genuinely asymmetric and directed measures matter a lot. If it's high (> 0.5), the network behaves more like an undirected friendship network and you may treat it as such for some measures — but state that assumption explicitly.

**Strongly connected components (SCCs)**: this matters for eigenvector centrality (see below). If the network has many SCCs rather than one giant one, eigenvector centrality is unreliable.

---

## Why "centrality" is plural: what does "important" mean for your use cases?

You named two distinct use cases:

1. **Knowledge champions** — people whose expertise and reputation the organization trusts and defers to; people who would be effective at spreading and legitimizing new ideas
2. **Early-loop targets for initiative rollout** — people who can broadcast information quickly and/or who serve as bridges between subgroups so the rollout doesn't get siloed

These are not the same process, and they do not point to the same centrality measure. Here is the decision:

| Your goal | Implicit flow process | Right centrality |
|---|---|---|
| Who is most respected / deferred to as an expert? | Prestige: who do the well-connected people consult? | **In-degree** (raw count) or **PageRank** |
| Who can broadcast information to the whole org fastest? | Speed of reach: geodesic broadcast | **Harmonic closeness** (on G, directed, with harmonic handling) |
| Who bridges subgroups and controls cross-silo flow? | Brokerage: parcels travel through specific chokepoints | **Betweenness centrality** (directed) |
| Who spans structural holes — non-redundant contacts? | Brokerage: access to diverse, non-overlapping information | **Burt's constraint / effective size** |

---

## The four measures to compute, and why each one

### 1. In-degree / PageRank → "Knowledge Prestige Champions"

**In-degree** is the count of colleagues who named this person as a go-to advisor. It is the rawest signal of perceived expertise and trust.

**PageRank** is the better version: it weights nominations from well-connected people more than nominations from peripheral employees. If the most trusted five people in the firm all name the same person, that person's PageRank is high even if their raw in-degree count is only five. PageRank handles directed graphs correctly (unlike eigenvector centrality).

```python
# In-degree (raw count of nominations)
in_deg_centrality = dict(G.in_degree())

# PageRank — works on the full directed graph
pr = nx.pagerank(G, alpha=0.85)

# Top 10 by PageRank
top_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 by PageRank (knowledge prestige):", top_pr)
```

**Recommendation for "knowledge champions"**: Use PageRank as the primary ranking, cross-checked with in-degree. People who rank highly on both are the clearest targets. People who rank high on PageRank but low in raw in-degree are sought out by a few highly central colleagues — potentially deep specialists worth surfacing.

**Why NOT eigenvector centrality here**: On a directed network that doesn't have a single giant strongly connected component — which most real advice networks don't — eigenvector centrality will assign zero to any node with no incoming paths from the main component. Use PageRank or Katz instead.

---

### 2. Betweenness centrality → "Initiative Rollout Brokers"

Betweenness measures what fraction of all shortest paths between every pair of employees passes through a given person. High betweenness = this person sits between subgroups and controls information flow across the firm.

For initiative rollout, these are the people you *must* loop in early. If information has to cross from the Finance cluster to the Strategy cluster to the Operations cluster, high-betweenness nodes are the bridges. Skipping them risks the initiative message getting distorted or delayed as it passes through them secondhand.

```python
# Betweenness on the directed graph, normalized
btw = nx.betweenness_centrality(G, normalized=True, weight=None)

top_btw = sorted(btw.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 by betweenness (brokers/bridges):", top_btw)
```

**What the result means in plain language**: "Alice has the highest betweenness" → Alice is the person whose removal (or whose failure to relay your message) would most disrupt information flow between subgroups in your firm.

**Note on the assumption**: betweenness assumes information travels on *shortest* paths. This is approximately true for explicit referrals ("who should I ask about X?") but less true for diffuse information spread. If your real concern is information diffusion rather than controlled referral flows, see the note on PageRank above — it's a better model for random-walk-style spread.

---

### 3. Harmonic closeness → "Fast Broadcasters"

Closeness centrality measures how quickly a person can reach everyone else. Standard closeness breaks on directed networks with multiple weakly connected components (if person A can't reach person B, the distance is infinite and closeness collapses to zero). **Harmonic centrality** handles this gracefully:

`C_H(i) = Σ_{j≠i} 1/d(i,j)`  (where 1/∞ = 0)

```python
# Harmonic centrality — handles unreachable nodes automatically
harm = nx.harmonic_centrality(G)  # NetworkX uses directed paths by default on DiGraph

top_harm = sorted(harm.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 by harmonic centrality (fast broadcasters):", top_harm)
```

High harmonic closeness = this person can reach everyone else in the fewest hops, on average. These are your most efficient messengers for time-sensitive rollouts.

---

### 4. Burt's constraint → "Structural Hole Brokers"

This is different from betweenness. Betweenness asks "are you on many shortest paths?" Burt's constraint asks "do your contacts also know each other?" Low constraint = your contacts come from distinct, non-overlapping clusters = you span structural holes = you have access to diverse, non-redundant information and serve as the bridge that connects silos.

```python
# Burt's constraint — lower score = more structural holes = more brokerage opportunity
constraint = nx.structuralholes.constraint(G)
eff_size   = nx.structuralholes.effective_size(G)

# Low constraint is what you want for brokers; sort ascending
top_brokers_burt = sorted(constraint.items(), key=lambda x: x[1])[:10]
print("Top 10 structural hole brokers (low constraint):", top_brokers_burt)
```

**Why this matters in addition to betweenness**: A person can have moderate betweenness but be the single bridge between two large clusters — they span a critical structural hole. Burt's measure catches this. Per Burt (2004), structural-hole spanners are disproportionately likely to generate and recognize good ideas because they see information from multiple otherwise-isolated groups.

---

## Practical targeting strategy

Given your two use cases, here is a concrete decision rule:

**Knowledge Champions** (people to designate as internal experts / credibility anchors for new initiatives):
- Rank by **PageRank** (primary) + **in-degree** (secondary)
- Top 10–15 on both lists are your clearest candidates
- These are the people others *already* trust and consult; formalizing this as a "knowledge champion" role leverages existing social capital

**Initiative Rollout Targets** (people to brief first to ensure org-wide reach):
- **Must-loop**: top 10 by **betweenness** — these are the chokepoints; if they're not aligned, your message fragments
- **High-value amplifiers**: top 10 by **harmonic closeness** — they reach others fastest
- **Cross-silo bridges**: top 10 by **low Burt constraint** — they span the structural holes between departments

In practice, look for people who appear on multiple lists. Someone in the top 10 for PageRank *and* betweenness *and* low constraint is a genuinely exceptional node — they are trusted, they bridge clusters, and they can broadcast broadly. In a 200-person network there are usually 3–8 such people. These are your highest-value early adopters.

---

## Full code skeleton

```python
import networkx as nx
import numpy as np
import pandas as pd

# 1. Load directed graph
G = nx.read_edgelist("advice_edges.csv", create_using=nx.DiGraph, delimiter=",")
# If your edge list has headers or a weight column, adjust accordingly

# 2. Inspect
print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}, density={nx.density(G):.4f}")
print(f"Weakly connected components: {nx.number_weakly_connected_components(G)}")
print(f"Strongly connected components: {nx.number_strongly_connected_components(G)}")
print(f"Reciprocity: {nx.reciprocity(G):.3f}")

# 3. Centralities
in_deg   = dict(G.in_degree())
pr       = nx.pagerank(G, alpha=0.85)
btw      = nx.betweenness_centrality(G, normalized=True)
harm     = nx.harmonic_centrality(G)
constr   = nx.structuralholes.constraint(G)
eff_size = nx.structuralholes.effective_size(G)

# 4. Combine into a DataFrame
df = pd.DataFrame({
    "in_degree":    in_deg,
    "pagerank":     pr,
    "betweenness":  btw,
    "harmonic":     harm,
    "constraint":   constr,
    "eff_size":     eff_size,
})

# 5. Rank within each column
df["rank_pr"]  = df["pagerank"].rank(ascending=False)
df["rank_btw"] = df["betweenness"].rank(ascending=False)
df["rank_harm"]= df["harmonic"].rank(ascending=False)
df["rank_constr"] = df["constraint"].rank(ascending=True)  # low = good for brokers

# 6. Composite score: mean rank across all four
df["composite_rank"] = df[["rank_pr","rank_btw","rank_harm","rank_constr"]].mean(axis=1)

print(df.sort_values("composite_rank").head(15))
```

---

## Two caveats to communicate to your leadership

**1. Measurement error matters.** Survey data has non-response artifacts (some people name more contacts than others; recency bias; etc.). A node's centrality rank in this network is an estimate, not a ground truth. When you pick "top 10 knowledge champions," treat the precise ranking within that group as noise — treat membership in the group as signal. Borgatti, Carley & Krackhardt (2006) showed that even 10% edge perturbation can substantially reorder centrality rankings; for a survey network, perturbation from non-response is likely higher.

**2. High centrality is a demand, not just a resource.** The most central people in advice networks are often already overloaded. Research on advice networks (Gibbons 2004; Cross & Parker 2004) consistently finds that the top advisors are consulted far more than they can sustainably handle. When you designate them as knowledge champions, pair that with explicit time allocation and recognition — otherwise you're formalizing an invisible tax they're already paying.

---

## References

- Freeman, L. C. (1979). Centrality in social networks: Conceptual clarification. *Social Networks* 1: 215–239.
- Borgatti, S. P. (2005). Centrality and network flow. *Social Networks* 27: 55–71.
- Burt, R. S. (2004). Structural holes and good ideas. *American Journal of Sociology* 110(2): 349–399.
- Borgatti, S. P., Carley, K., & Krackhardt, D. (2006). On the robustness of centrality measures under conditions of imperfect data. *Social Networks* 28: 124–136.
- Cross, R. & Parker, A. (2004). *The Hidden Power of Social Networks.* Harvard Business School Press.
