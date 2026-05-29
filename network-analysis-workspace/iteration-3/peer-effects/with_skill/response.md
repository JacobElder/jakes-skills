# Interpreting Your Peer Effects Result

Your advisor's framing — "this shows peer influence" — is the most common misinterpretation in observational social network research. The coefficient is real and worth reporting, but it does not show what your advisor says it shows. Let me explain exactly why, and then lay out a concrete path forward.

---

## What your regression actually estimates

Your model is:

```
smoking_i = α + 0.43 · mean_friends_smoking_i + β₁·gender + β₂·grade + β₃·SES + ε_i
```

This is a **linear-in-means model** with a network-based peer measure. Three fundamental problems apply simultaneously, and they compound rather than cancel.

### Problem 1: The reflection problem (Manski 1993)

The coefficient on `mean_friends_smoking` does not cleanly identify influence because of **simultaneous determination**: if peers influence you, then you also influence your peers, and everyone's smoking status is jointly determined. Regressing your outcome on the mean of your friends' outcomes conflates your influence on them with their influence on you. In a strict group-based setting this causes perfect collinearity; in a network setting it produces severe bias unless you use the right identification strategy (more on this below).

### Problem 2: Selection / homophily (Shalizi & Thomas 2011)

The deeper problem: students who smoke likely chose to become friends with other students who smoke, or vice versa — before any influence occurred. This is **homophily** (birds of a feather flock together), and it generates exactly the same cross-sectional correlation as peer influence. Shalizi and Thomas (2011) proved formally that in observational cross-sectional data, **influence and homophily are generically confounded** — the statistical signature of "my friends smoke so I smoke" and "I became friends with smokers because I was already inclined to smoke" are indistinguishable without time ordering or exogenous variation.

Your 0.43 coefficient reflects some weighted sum of at least four distinct mechanisms:

1. **Endogenous peer influence**: friends' smoking causes my smoking
2. **Exogenous/contextual effects**: friends' characteristics (not just smoking) affect my behavior
3. **Correlated effects / homophily**: smokers select into friendships with other smokers
4. **Shared environment**: students who smoke may cluster in shared contexts (same neighborhood, same after-school hangout, same social event) that make them both smoke and become friends

You cannot separate these with a cross-sectional OLS regression.

### Problem 3: Friendship endogeneity

You are using self-reported friendship nominations to construct the network. Friendship ties are themselves outcomes of prior behavior, shared identity, and opportunity. A network whose structure is endogenous to the very behavior being studied — smoking — cannot serve as an exogenous conditioning variable in a causal regression without strong assumptions you cannot verify from this dataset.

---

## What you *can* say

The coefficient is informative as a **descriptive** finding: smoking is positively autocorrelated on the friendship network. You can report this. The honest framing:

> "Students whose nominated friends smoke are more likely to smoke themselves (b = 0.43, p < 0.001), net of gender, grade, and SES. This is consistent with peer influence, but also with homophily — students who smoke selecting into friendships with other smokers — and with shared environments. The cross-sectional design does not permit identification of the causal mechanism."

This is a stronger and more defensible contribution than a causal claim that won't survive peer review.

You should also compute a **network autocorrelation statistic** (Moran's I) to formalize the clustering observation. Moran's I gives you:

```
I = (n / Σ_ij w_ij) · Σ_ij w_ij (y_i - ȳ)(y_j - ȳ) / Σ_i (y_i - ȳ)²
```

where W is your row-normalized adjacency matrix. Test it against a permutation null (shuffle smoking labels across nodes, recompute I, repeat 10,000 times). A significant positive I is evidence of network autocorrelation — which you then interpret carefully, not as proof of influence.

---

## What to do next: a decision tree

The right path depends on what data you can access. Here is the hierarchy from strongest to weakest identification.

### Option A: Collect longitudinal panel data (strongest observational path)

If you can run a second wave — ideally a third — surveying the same students again, you can use **SAOM (Stochastic Actor-Oriented Model, RSiena)**. SAOM jointly models:
- How friendships change (selection): do students become friends with others who are similar in smoking status?
- How behavior changes (influence): do students' smoking patterns shift to match their existing friends?

SAOM identifies both effects through **time precedence**: selection is observed when students form new ties to similar others *before* behavior converges; influence is observed when behavior changes *after* tie formation. The key requirements:
- Minimum 2 waves, ideally 3+
- Meaningful network change between waves (RSiena checks this)
- Meaningful behavior change between waves

This is the standard approach for adolescent health behavior in networks — Steglich, Snijders, & Pearson (2010) use it explicitly for smoking and alcohol. SAOM is implemented in the `RSiena` R package.

### Option B: Use network structure as instruments (Bramoullé et al. 2009)

If you are stuck with cross-sectional data, there is still an identification strategy — but it requires restructuring your estimator from OLS to GMM/IV.

Bramoullé, Djebbari & Fortin (2009) show that if your friendship network contains **intransitive triads** (student A nominates B, B nominates C, but A does not nominate C), then the smoking behavior of **friends-of-friends** provides a valid instrument for friends' smoking. The intuition: C's smoking affects A only through B, so if you instrument B's smoking with C's smoking and C's characteristics, you partial out the homophily confound.

This requires:
1. The matrices I, G, G² (where G is the row-normalized adjacency) are linearly independent — check this for your specific network
2. Network exogeneity: friendship ties must be uncorrelated with unobserved determinants of smoking, conditional on your covariates — a strong assumption, but testable by robustness checks

Implementation: construct the instruments manually in R or Python, then estimate via GMM. The `peerInteractions` package in R implements this for standard cases.

**Caveat**: this approach does not solve the homophily problem if there is *unmeasured* homophily on unobservables — students who are similar in ways you do not observe (e.g., risk tolerance, parental smoking, access to cigarettes) may both befriend each other and smoke, and the instrument will not absorb this.

### Option C: Latent space model (defensible with cross-sectional data)

If you believe that unmeasured individual-level factors simultaneously drive both tie formation and smoking, a **latent space model** (Hoff, Raftery & Handcock 2002) can absorb part of this unobserved homophily. Each student gets a position in latent Euclidean space; both tie probability and smoking propensity depend on latent position. The influence effect is then estimated after partialing out latent position.

R packages: `latentnet`, `eigenmodel`.

This is principled but identification of the influence coefficient depends on the parametric form of the latent space. Misspecification reintroduces the bias you are trying to eliminate. Use as a sensitivity check, not a primary strategy.

### Option D: Descriptive analysis + honest framing (minimum viable)

If data collection is not feasible and you cannot implement IV, describe what you have rigorously:

1. Report network autocorrelation (Moran's I with permutation test)
2. Report the regression coefficient and CIs as a *descriptive association*, explicitly flagging the identification limits
3. Characterize the network structure: directedness of nominations, reciprocity rate, density, clustering coefficient — these affect how social influence would operate if it exists
4. Use the E-I index or Newman's assortativity coefficient to quantify smoking homophily directly
5. Frame the paper as establishing the empirical groundwork and motivating longitudinal follow-up

This is a contribution. Many published papers in sociology do exactly this; the key is framing it correctly so you are not overclaiming.

---

## Immediate next steps for your current dataset

Before going further, characterize the network structure. This is both good practice and informs which methods are feasible.

```python
import networkx as nx
import numpy as np
import pandas as pd
from scipy import stats

# Load your data — assumes edge_list and node_attributes DataFrames
G = nx.DiGraph()  # Directed: A nominates B is not same as B nominates A
G.add_edges_from(zip(edge_list['nominator'], edge_list['nominee']))

# Attach attributes
for col in ['smoking', 'gender', 'grade', 'ses']:
    nx.set_node_attributes(G, dict(zip(node_attrs['student_id'], node_attrs[col])), col)

# Network summary
print(f"n={G.number_of_nodes()}, m={G.number_of_edges()}")
print(f"density={nx.density(G):.4f}")
print(f"reciprocity={nx.reciprocity(G):.3f}")
print(f"transitivity={nx.transitivity(G):.3f}")
print(f"components (weak)={nx.number_weakly_connected_components(G)}")

# Smoking assortativity
r = nx.numeric_assortativity_coefficient(G, 'smoking')
print(f"smoking assortativity (Newman's r) = {r:.3f}")

# Moran's I (manual implementation)
nodes = list(G.nodes())
n = len(nodes)
smoking = np.array([G.nodes[v]['smoking'] for v in nodes])
y_bar = smoking.mean()

# Row-normalized adjacency
A = nx.to_numpy_array(G, nodelist=nodes)
row_sums = A.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1  # avoid divide by zero for isolates
W = A / row_sums

# Moran's I
W_sum = W.sum()
numerator = n * np.sum(W * np.outer(smoking - y_bar, smoking - y_bar))
denominator = W_sum * np.sum((smoking - y_bar)**2)
I = numerator / denominator
print(f"Moran's I = {I:.4f}")

# Permutation test (10,000 shuffles)
np.random.seed(42)
permuted_I = []
for _ in range(10000):
    perm = np.random.permutation(smoking)
    num_p = n * np.sum(W * np.outer(perm - perm.mean(), perm - perm.mean()))
    den_p = W_sum * np.sum((perm - perm.mean())**2)
    permuted_I.append(num_p / den_p)
p_value = np.mean(np.array(permuted_I) >= I)
print(f"Permutation p-value: {p_value:.4f}")
```

### Things to check from this output

- **Reciprocity rate**: if it is low (< 0.3), many nominations are one-sided. This is common in adolescent friendship networks. Whether you symmetrize or keep the network directed has substantive meaning — a directed network where A nominates B but B does not nominate A represents a different type of relationship than mutual nomination. For peer effects, you probably want to condition on **mutual nominations** (reciprocated ties), as those are more likely to represent the close friendships through which influence operates.
- **Isolates**: students who nominated no one or were nominated by no one have undefined peer means. How you handle them in the regression matters. Report how many there are and what you did.
- **Smoking assortativity (r)**: a positive assortativity coefficient in the range 0.2–0.5 is typical for adolescent smoking networks. This is the baseline fact your regression is trying to explain.
- **Moran's I p-value**: if significant, you have network autocorrelation in smoking. This is consistent with (but does not prove) influence or homophily.

---

## A note on your advisor's claim

Your advisor saying "this shows peer influence" is a common shorthand in applied sociology, but it would not survive a methods review in *Social Networks*, *American Journal of Sociology*, or *Sociological Methods & Research*. The field has had this debate since Manski (1993) and it was sharpened considerably by Shalizi & Thomas (2011). If your dissertation committee includes a social network specialist or a quantitative sociologist, this exact question about identification will come up in your defense.

The good news: cross-sectional observational studies documenting smoking autocorrelation in adolescent friendship networks *are* publishable — there is a substantial literature doing exactly that. The contribution is in (a) the descriptive rigor, (b) the network characterization, and (c) the honest discussion of what the design can and cannot rule out, paired with a concrete recommendation for how future work should address identification.

---

## Summary

| Your current situation | What to report | What to do next |
|---|---|---|
| Cross-sectional, single wave, observational | Descriptive network autocorrelation; regression as descriptive association | Collect a second wave; pursue Bramoullé IV if stuck with cross-section |
| 0.43 coefficient | Positive association, not identified peer influence | Frame as "consistent with influence but not identified" |
| p < 0.001 | Strong autocorrelation signal | Supports that something is going on; does not tell you what |

The most important methodological move you can make right now is to collect a second wave of data. Even a 6-month follow-up that re-surveys network ties and smoking status would let you apply SAOM and produce a meaningfully stronger claim. If that is not feasible, the Bramoullé IV approach using friends-of-friends' smoking as instruments is the best cross-sectional alternative, paired with an honest discussion of the residual identification limitations.

---

## Key references

- Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. *Review of Economic Studies* 60: 531–542.
- Shalizi, C. R. & Thomas, A. C. (2011). Homophily and contagion are generically confounded in observational social network studies. *Sociological Methods & Research* 40: 211–239.
- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. *Journal of Econometrics* 150: 41–55.
- Snijders, T. A. B., Steglich, C. E. G., & Schweinberger, M. (2010). Dynamic networks and behavior: Separating selection from influence. *Sociological Methodology* 40: 329–393.
- McPherson, M., Smith-Lovin, L., & Cook, J. M. (2001). Birds of a feather: Homophily in social networks. *Annual Review of Sociology* 27: 415–444.
