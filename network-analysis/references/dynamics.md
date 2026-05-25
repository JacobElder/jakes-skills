# Network Dynamics: Spreading, Diffusion, and Influence

This file covers processes that *run on* networks: epidemic spreading, opinion diffusion, cascades, synchronization, influence maximization. Network structure and dynamics are deeply coupled — the same dynamics on different structures produce qualitatively different outcomes, and the topology that matters for diffusion is often different from the topology that matters for, say, community structure.

## Compartmental models

The simplest spreading models partition nodes into compartments (Susceptible, Infected, Recovered, etc.) and define transition rates. Adapted from epidemiology to networks:

### SI (Susceptible-Infected)

Each infected node infects each susceptible neighbor at rate β per unit time. Once infected, stay infected. Models permanent adoption (e.g., learning a piece of information).

### SIS

Infected nodes recover at rate γ and return to susceptible. Models recurring states (e.g., flu).

The **epidemic threshold** for SIS on a network with adjacency matrix A: outbreak occurs if β/γ > 1/λ_max(A). On scale-free networks (heavy-tailed degree), λ_max is large, so the threshold is *zero* in the infinite-size limit — any infection can cause an epidemic. This is the famous Pastor-Satorras & Vespignani (2001) result.

### SIR

Infected nodes recover with permanent immunity (rate γ). Models lasting immunity (most viral epidemics).

Threshold conditions are more nuanced; depends on degree distribution moments. On uncorrelated networks, threshold ∝ ⟨k⟩/⟨k²⟩.

### SEIR, SIRS, etc.

Extensions for incubation period, waning immunity. Same modeling framework.

### Implementation

```python
import networkx as nx
import EoN  # epidemics on networks (Kiss, Miller & Simon's book package)

t, S, I, R = EoN.fast_SIR(G, tau=0.3, gamma=0.1, initial_infecteds=[seed])
```

`EoN` (Joel Miller) is the reference Python library. `NDlib` is a more general dynamics library with many models. For stochastic simulation of SIR/SIS, Gillespie's algorithm is standard.

### Beyond mean-field

The "mean-field" approximation assumes nodes of the same degree behave identically. This is wrong when:
- Degree-degree correlations exist (assortativity)
- Community structure matters
- The network is small enough for finite-size effects

**Pair approximations**, **moment closure**, and **message-passing equations** improve the mean-field; for serious work, simulate.

## Threshold models

The classic alternative to compartmental models. Each node has a **threshold** φ_i; node i adopts if at least φ_i fraction (or count) of its neighbors have adopted. Granovetter (1978) for the social science version; Watts (2002) for the network version.

Key result (Watts 2002): cascades are possible only in a specific region of the (mean degree, threshold) parameter space — the **cascade window**. Below it, the seed dies out; above it, the network is too dense for the threshold to be exceeded by chance. The window has a tent shape.

Complex contagions (Centola & Macy 2007): when adoption requires *multiple* exposures (high threshold), wide bridges (multiple connections to the same cluster) matter more than long bridges. This contrasts with simple contagion where weak ties (Granovetter) carry information.

Implication: **for behaviors with high thresholds (joining a protest, adopting a costly technology), targeting high-betweenness nodes does NOT necessarily help spread**. The structure that aids complex contagion is dense local clustering, not bridges.

## Influence maximization

The optimization problem: select k seed nodes to maximize the expected number of influenced nodes under a chosen dynamics.

NP-hard in general. The classic results:

### Kempe, Kleinberg & Tardos (2003)

For Independent Cascade (IC) and Linear Threshold (LT) models, the influence function is **submodular and monotone**. Therefore, the **greedy algorithm** (at each step, add the node that maximizes marginal influence) gives a (1 − 1/e) ≈ 0.63 approximation.

The catch: estimating marginal influence requires Monte Carlo simulation of the cascade many times for each candidate. CELF (Leskovec et al. 2007) uses lazy evaluation to make this much faster.

### CELF, CELF++, TIM, IMM

A sequence of papers reduced complexity by orders of magnitude:
- **CELF** (Cost-Effective Lazy Forward): use submodularity to skip recomputing marginal gains
- **TIM/IMM** (Tang, Shi, Xiao 2014–2015): reverse-influence sampling; near-linear scaling

Library: `Greedy`, `ndlib`, or implement IMM yourself for serious work.

### When influence maximization is the wrong question

The standard formulation assumes:
- A specific dynamics (IC, LT, SIR) that may not match reality
- Static network (no rewiring during spreading)
- Identical activation probabilities (uniform edge weights)
- No competing diffusions

For real applications, the chosen seeds depend strongly on these assumptions; sensitivity matters. Also: the "best seeds" under IC are often not the "best seeds" under LT or threshold — they're optimizing different objectives.

## Random walks on networks

A discrete-time random walker visits nodes according to A and the chosen walk rule. Stationary distribution:
- **Simple random walk**: π_i ∝ k_i (degree). Higher-degree nodes are visited more.
- **PageRank walk**: stationary distribution is PageRank (with teleport).
- **Personalized PageRank**: teleport to a specific subset; gives proximity to that subset.
- **Lazy walks**: with probability 1/2 stay; ensures convergence on bipartite graphs.

### Spectral gap and mixing time

Mixing time τ_mix ~ 1/(1 - λ_2), where λ_2 is the second-largest eigenvalue of the transition matrix. Communities (modularity) correspond to slow mixing — the walker takes a long time to "forget" its starting community. This is the formal connection between community structure and random-walk dynamics that underlies Infomap.

### Applications

- **Personalized PageRank for recommendation**: nodes with high PPR from a query are similar
- **Random walks for community detection**: Infomap, walktrap (Pons & Latapy 2005)
- **DeepWalk / node2vec**: random walks as "sentences" for embedding
- **Diffusion maps**: walks define a multiscale geometric structure

## Cascades on social media (empirical)

Empirical studies of information cascades (Goel, Anderson, Hofman & Watts 2016; Vosoughi, Roy & Aral 2018) found:

- **Almost all cascades are small and shallow**: vast majority don't go viral
- **"Viral" cascades are typically broadcast**, not peer-to-peer: a few high-degree nodes account for the spread
- **Surprise rather than novelty** predicts viral cascades for misinformation
- **Heterogeneity in spreaders matters more than network structure** at the broadcasting end

This suggests that targeting strategies based purely on network position (centrality) may underperform strategies that also consider node-level content quality, susceptibility, or recency.

## Synchronization

For coupled oscillators on a network (Kuramoto model), the **master stability function** approach (Pecora & Carroll 1998) shows that synchronization depends on the eigenvalue ratio λ_N / λ_2 of the Laplacian — the **synchronizability**. Lower ratio = more synchronizable.

Topologies optimized for synchronizability are NOT scale-free; **homogeneous random graphs synchronize better than scale-free** in many regimes (Nishikawa et al. 2003). This was counterintuitive when discovered.

## Vaccination / immunization

The optimization problem: which nodes to immunize to prevent / minimize an outbreak?

### Strategies (in order of typical effectiveness on real networks)

1. **Random**: baseline; usually poor on heterogeneous networks
2. **Highest-degree**: targets hubs; effective for SIS on scale-free
3. **Highest-betweenness**: targets brokers; effective when the bottleneck is between subgroups
4. **Acquaintance immunization** (Cohen, Havlin & ben-Avraham 2003): vaccinate a random friend of a random person. Exploits the **friendship paradox** (your friends have more friends than you on average); doesn't require knowing the global degree distribution. Often nearly as good as targeted as global degree-based, with vastly less information.
5. **Community-bridge nodes**: nodes whose removal disconnects communities
6. **Eigenvalue-driven**: nodes whose removal maximally reduces λ_max(A) (and hence the SIS threshold). NP-hard but greedy works.

For diseases with high transmissibility, vaccination of any small subset is unlikely to prevent an epidemic; the question becomes minimizing peak / total cases.

## Common dynamics mistakes

- **Picking a dynamics that doesn't match reality**: SIR for an opinion (which often doesn't "recover"); IC for a behavior requiring multiple exposures
- **Reporting results from a single simulation run**: stochastic processes need many runs; report distribution
- **Ignoring the cascade window**: cascades may be impossible for the given parameters, or guaranteed, regardless of seed choice
- **Targeting strategies that ignore the dynamics**: degree-based targeting fails for complex contagion
- **Inferring causation from cascade observation**: just because A's adoption preceded B's, with A→B in the network, doesn't mean A *caused* B's adoption (homophily/selection alternative)
- **Mean-field on heterogeneous networks**: a single "average degree" hides distributional structure that drives the dynamics
- **Confusing "spread" with "adoption"**: information can spread without anyone "adopting" the underlying behavior

## Default recipe for a diffusion question

1. **What is the substantive process?** Information sharing, opinion change, disease, technology adoption?
2. **Pick the dynamics that matches** (simple contagion: IC/SIR; complex contagion: threshold model; sustained: SIS; opinion: voter / DeGroot)
3. **Choose seeds and run many simulations** (Monte Carlo, ≥ 100 runs for any reasonable estimate)
4. **Compare to a randomized baseline** (random seeds, randomized network preserving degree sequence)
5. **Report distribution of outcomes**, not just the mean
6. **Sensitivity-check the dynamics parameters**: if conclusions are very sensitive to β or threshold, qualify them

## Canonical references

- Newman, M. E. J. (2018). *Networks* (2nd ed.). Oxford. Chapters 16–17.
- Kiss, I. Z., Miller, J. C., & Simon, P. L. (2017). *Mathematics of Epidemics on Networks*. Springer.
- Pastor-Satorras, R., Castellano, C., Van Mieghem, P., & Vespignani, A. (2015). "Epidemic processes in complex networks." *Reviews of Modern Physics* 87: 925.
- Watts, D. J. (2002). "A simple model of global cascades on random networks." *PNAS* 99: 5766–5771.
- Centola, D. & Macy, M. (2007). "Complex contagions and the weakness of long ties." *AJS* 113: 702–734.
- Kempe, D., Kleinberg, J., & Tardos, É. (2003). "Maximizing the spread of influence through a social network." *KDD*.
- Tang, Y., Xiao, X., & Shi, Y. (2014). "Influence maximization: Near-optimal time complexity meets practical efficiency." *SIGMOD*.
- Cohen, R., Havlin, S., & ben-Avraham, D. (2003). "Efficient immunization strategies for computer networks and populations." *PRL* 91: 247901.
- Goel, S., Anderson, A., Hofman, J., & Watts, D. J. (2016). "The structural virality of online diffusion." *Management Science* 62: 180–196.
