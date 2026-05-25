# Temporal Networks

A temporal network is a sequence of interactions over time, not a static graph. Most "network" data in the modern world (emails, calls, citations, friendships with formation/dissolution dates) is fundamentally temporal, but it's almost always analyzed as if static — losing the information that the timing carries. This file covers what changes when you keep the time dimension.

## What you lose by aggregating

When you collapse a sequence of timestamped interactions into a single weighted graph (edge weight = number of interactions, or simply binary "ever interacted"), you lose at minimum:

- **Causal ordering**: in static analysis, A→B→C is the same as A→B and A→C; in reality, B can only relay information from A to C if the AB interaction happened before BC.
- **Burstiness and inter-event times**: real interactions are heavy-tailed; long quiet periods followed by activity bursts. Static analysis assumes uniform mixing.
- **Recurrence vs. one-shot**: 10 interactions one day each is very different from 10 interactions in one day, but both look the same on the aggregated graph (or only differ by an aggregated weight that doesn't preserve the temporal pattern).

Holme & Saramäki (2012) is the canonical reference; their 2019 book *Temporal Network Theory* extends it.

## Time-respecting paths (the core concept)

A **time-respecting path** from i to j is a sequence of contacts i→x₁ at t₁, x₁→x₂ at t₂, ..., x_{k-1}→j at t_k with t₁ < t₂ < ... < t_k (and typically with some additional delay constraint Δt between consecutive contacts).

This is the fundamental object of temporal network analysis. It is **not symmetric**: there may be a time-respecting path from A to B but not from B to A. It is **not transitive** in the static sense: A→B and B→C as time-respecting paths do not imply A→C unless they line up in time.

### Reachability

Two nodes i, j are **temporally reachable** (i → j) if there is a time-respecting path. The **reachability ratio** is the fraction of ordered pairs (i, j) for which i is temporally reachable to j. This is typically much smaller than the static reachability — Holme's studies show 30–70% reductions.

### Latency

The **latency** from i to j is the minimum elapsed time over any time-respecting path. This depends on the starting time; latency(i, j, t) = (arrival time at j of fastest path starting at i at or after time t) − t.

### Forward / backward / co-temporal cones

- **Forward set** of (i, t): all nodes reachable from i starting at time t
- **Backward set** of (j, t): all nodes that can reach j by time t
- **Influence set**: forward set, often plotted as it grows with time

## Temporal centrality

Static centrality computed on the aggregated network is *biased* because it counts paths that don't exist temporally. Two key temporal centralities:

### Temporal betweenness

For each node v and time window, count the fraction of *shortest time-respecting paths* (s, t) passing through v. Computing this is NP-hard in some path-definitions (Buß et al. 2020) but tractable for most practical definitions; the choice of "shortest" matters:

- **Shortest** (fewest hops)
- **Foremost** (earliest arrival)
- **Fastest** (smallest elapsed time)
- **Cheapest** (smallest sum of weights)

These give different rankings. State which you're using.

### Temporal closeness

Average inverse temporal distance from v to all others (with t = start of window or averaged over t). Handles unreachable pairs the way harmonic centrality does for static networks.

### Burstiness-aware centrality

Even within time-respecting paths, the *distribution* of inter-event times matters: bursty patterns slow down spreading more than the same number of events spread uniformly (Karsai et al. 2011). Centralities that incorporate inter-event-time distributions exist but are less standardized.

## Aggregation: window choice and its consequences

If you must aggregate temporal data into snapshots, the choice of window size is critical:

- **Too short**: each snapshot is sparse and uninformative; structural measures are noisy
- **Too long**: temporal ordering is lost within windows; you approach the static case
- **Multi-scale**: compute structural measures across several window sizes and look for stable features

Selection criteria:
- Match the **natural rhythm** of the process (daily for human contact, monthly for collaboration, etc.)
- Use the **mean inter-event time** as a guide
- For inference (SAOM, STERGM), the window between waves *should be the same scale as the dynamics* — waves a year apart on a network that changes daily lose too much

## Temporal motifs

Static motifs (small subgraphs, e.g., triangles) generalize to temporal motifs: small subgraphs with timestamped edges in a specific order. Kovanen et al. (2011) and Paranjape et al. (2017) classified these for k=3 nodes, l=3 edges.

Examples:
- "Triangle-closing motif": A→B, A→C, then B→C within Δt
- "Reciprocation motif": A→B, then B→A within Δt
- "Forwarding motif": A→B, then B→C within Δt

Counts of these motifs (compared to randomized references that preserve some properties but destroy others — see next section) reveal the temporal mechanisms shaping the network.

## Null models for temporal networks

You cannot use the standard configuration model — it ignores time. Temporal null models randomize one feature at a time:

- **Time-shuffled**: keep the static graph, randomize timestamps. Tests effects of timing given topology.
- **Sequence-shuffled**: shuffle the order of contacts but keep their durations. Tests effects of order.
- **Inter-event randomized**: shuffle the gaps between events for each edge. Tests burstiness.
- **Link-permuted**: randomly relabel the contacts so that each "i→j at t" becomes "i'→j' at t" preserving degree-sequence. Tests topology.
- **Activity-driven model** (Perra et al. 2012): generative model where each node has a baseline activity rate; contacts are random.

The choice tells you what hypothesis you're testing. "Is the observed structure due to timing or topology?" requires a different null than "is it due to burstiness or to uniformity?"

## Inference on temporal networks

### Higher-order models (Scholtes et al. 2014; pathpy)

When temporal correlations matter, a first-order Markov model on nodes is wrong. **Higher-order networks** represent paths-of-length-k as nodes and capture k-step memory. Implementation: `pathpy` (Scholtes).

This matters when "B usually relays from A to C, but C usually relays from B to D" — first-order treats these symmetrically; higher-order captures the routing pattern.

### Relational Event Models (REM; Butts 2008; DyNAM)

Continuous-time model where each event (i, j, t) is treated as a discrete-choice realization: actor i selects the most attractive partner j according to a rate function. REM is to temporal networks as ERGMs are to static networks — but defined on event sequences rather than graph configurations.

R package: `relevent`; `goldfish` (Stadtfeld et al.) is the modern alternative with DyNAM.

When to use REM: you have event-level data (every interaction with timestamp), you want to model what drives each interaction, and you have enough data per actor for individual-level estimation.

### STERGM (Krivitsky & Handcock 2014)

Discrete-time temporal ERGM with separate formation/dissolution models. Useful when:
- You have panel data (regular snapshots)
- Tie persistence is meaningful (the same tie either exists or doesn't at each wave)
- Different processes drive formation and dissolution

See `references/ergm_saom.md` for setup.

### SAOM with continuous time

SAOM (RSiena) is technically continuous-time even though it's fit on panel data — it treats waves as snapshots of a continuous process. This makes it preferable to STERGM when actors have agency and ties evolve smoothly.

## Spreading and contagion on temporal networks

A key result from temporal network research: **the same SIR/SI process unfolds slower on the empirical temporal network than on its time-randomized counterpart**. The reasons (Karsai et al. 2011):
- **Burstiness**: long gaps between contacts slow down spreading
- **Community structure**: spreading bottlenecks at community boundaries
- **Weak ties**: occasional bridges between communities matter more than expected from frequency

Implications: a static network analysis predicts faster, more uniform spread than actually occurs. Temporal vaccination strategies that target high-temporal-degree at the right time outperform static degree-based strategies.

## Libraries

| Library | Language | Strengths |
|---|---|---|
| `pathpy` (Scholtes) | Python | Higher-order temporal networks, time-respecting paths |
| `teneto` (Thompson) | Python | Temporal centrality, fluctuation analysis |
| `Raphtory` | Python/Rust | Streaming/incremental, scales |
| `tnet` (Opsahl) | R | Older but widely cited; weighted temporal |
| `igraph` | Python/R/C | Has some temporal support via edge attributes |
| `relevent`, `goldfish` | R | REM / DyNAM models |
| `RSiena` | R | SAOM (panel) |
| `tergm`, `statnet` | R | STERGM |
| `tidygraph + ggraph` | R | Tidy temporal pipelines |

## Common temporal mistakes

- Aggregating to static and proceeding as if temporal information didn't exist (the modal mistake)
- Computing static centrality on aggregated network and calling it "temporal centrality"
- Using a single window size without checking sensitivity
- Confusing **temporal degree** (number of contacts) with **temporal strength** (frequency or duration) — they measure different things
- Forgetting that **time-respecting paths are not symmetric** even on undirected interaction data
- Comparing temporal-network metrics on raw data to time-randomized data without preserving relevant features (the null model choice matters)
- For SAOM/STERGM, treating waves too far apart as if they were close (or vice versa) — wave spacing affects parameter estimates in STERGM, less so in SAOM but it affects what "rate" means

## Canonical references

- Holme, P. & Saramäki, J. (2012). "Temporal networks." *Physics Reports* 519: 97–125.
- Holme, P. & Saramäki, J. (Eds.) (2019). *Temporal Network Theory*. Springer.
- Masuda, N. & Lambiotte, R. (2020). *A Guide to Temporal Networks* (2nd ed.). World Scientific.
- Karsai, M., Kivelä, M., Pan, R. K., Kaski, K., Kertész, J., Barabási, A.-L., & Saramäki, J. (2011). "Small but slow world: How network topology and burstiness slow down spreading." *Physical Review E* 83: 025102.
- Kovanen, L., Karsai, M., Kaski, K., Kertész, J., & Saramäki, J. (2011). "Temporal motifs in time-dependent networks." *Journal of Statistical Mechanics* 2011: P11005.
- Scholtes, I., Wider, N., Pfitzner, R., Garas, A., Tessone, C. J., & Schweitzer, F. (2014). "Causality-driven slow-down and speed-up of diffusion in non-Markovian temporal networks." *Nature Communications* 5: 5024.
- Butts, C. T. (2008). "A relational event framework for social action." *Sociological Methodology* 38: 155–200.
- Stadtfeld, C., Hollway, J., & Block, P. (2017). "Dynamic network actor models: Investigating coordination ties through time." *Sociological Methodology* 47: 1–40.
