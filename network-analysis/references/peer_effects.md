# Peer Effects, Homophily, and Selection vs. Influence

This file addresses one of the most common — and most often botched — questions in network analysis: *do my peers influence my behavior?* The honest answer is "probably, but proving it from observational data is much harder than you think." This file enumerates the well-known identification problems and the methods that address them.

## The four mechanisms that confound

When you observe that connected people are similar (e.g., friends have similar drinking behavior), at least four mechanisms could be responsible. Without design or strong assumptions, you cannot separate them:

1. **Endogenous peer effects** (influence/contagion): my friends' behavior causes mine ("if my friends drink, I drink")
2. **Exogenous / contextual effects**: my friends' *characteristics* cause my behavior ("my friends are older, so I act older")
3. **Correlated effects** (homophily / selection): we are friends *because* we are similar ("drinkers befriend drinkers")
4. **Common environmental shocks**: we share an environment that affects us all ("we're at a bar")

Manski (1993) called these the "endogenous", "exogenous (or contextual)", and "correlated" effects. Whether they can be identified from observational data depends on the data design and assumptions.

## The reflection problem (Manski 1993)

In the **linear-in-means model** — the default specification when someone runs "outcome regressed on mean of peers' outcome and mean of peers' covariates" — the endogenous and exogenous effects are **perfectly collinear** under the assumption of group interactions. You literally cannot tell them apart.

`y_i = α + β · mean(y_{-i in group}) + γ · mean(X_{-i in group}) + δ · X_i + ε_i`

When the network is "group-based" (everyone in a group is connected to everyone else), the mean of peers' y is a deterministic function of the mean of peers' X (by averaging the equation itself). Result: β and γ are not separately identified.

### When the reflection problem CAN be overcome

Bramoullé, Djebbari & Fortin (2009) — the key paper — show that with **network interactions** (rather than groups), if there exist **intransitive triads** (i with friend j, j with friend k, but i not with k), then peers' peers' X provides a valid instrument for peers' y, and the model is identified. The condition: the matrices I, G, G² (where G is the row-normalized adjacency) must be linearly independent.

**Bottom line**: linear-in-means in groups is hopeless; linear-in-means on a real network *can* be identified, but you need to use Bramoullé et al.'s GMM / IV approach, not OLS on peer means. Implementations: `peerInteractions` (R), custom GMM in Python/Stata.

## The Shalizi-Thomas confound

Shalizi & Thomas (2011), "Homophily and contagion are generically confounded in observational social network studies." The result extends Manski's into the observational network setting and is stronger:

**Even outside the reflection problem**, if you observe that y_i and y_j are correlated and i and j are connected, you cannot separate "my friends influence me" from "I befriend people like me" without either:

1. **Time precedence** — i and j became friends *before* their behaviors became similar (and you observe the trajectory)
2. **Exogenous variation in tie formation** (randomized peer assignment, instrument, natural experiment)
3. **Strong assumptions about which covariates make friendship "as if randomly assigned"** (no unmeasured homophily) — which is rarely defensible
4. **Latent variable models** that explicitly model the unobserved homophily

This is why most "peer effects from observational social media data" studies are not credible: the identification assumption (no unmeasured homophily) is almost never plausible. Three degrees of influence (Christakis & Fowler) was famously challenged on these grounds.

## Methods that work (in various degrees)

### 1. Random assignment of peers

The gold standard. If peer assignment is random (e.g., random roommate assignment at college, random platoon assignment, random teacher assignment), then any correlation between peer characteristics and outcomes is causal. Examples: Sacerdote (2001) on roommate effects on grades, Carrell, Sacerdote & West (2013) on military peer effects.

Practical: even random assignment doesn't solve everything (peers may also self-select within the assigned group), but it's the cleanest identification strategy.

### 2. SAOM (Snijders, Steglich & Schweinberger 2010)

Continuous-time model that jointly models network change and behavior change. The selection effect (`simX`) and the influence effect (`avAlt` or `totSim`) are identified through the **timing**: actors who choose to befriend similar others contribute to selection; actors whose behavior changes to match existing friends contribute to influence.

This is the most defensible observational method but requires:
- At least 3 panel waves (more is much better)
- Substantial network change between waves (if the network is static, selection isn't observed)
- Substantial behavior change (if behavior is stable, influence isn't observed)
- Careful specification of which structural effects to control for

See `references/ergm_saom.md` for setup.

### 3. Instrumental variables

Bramoullé et al. (2009) use the structure of the network to construct instruments: the characteristics of friends-of-friends-of-friends affect i's outcome only through friends' outcomes, under the assumption of bounded interaction depth. De Giorgi, Pellizzari & Redaelli (2010) on student peer effects.

This requires network exogeneity (no homophily on unobservables), which is the same assumption as the linear-in-means literature.

### 4. Double negative controls (Egami & Tchetgen Tchetgen 2021)

A more recent method: identify *one* outcome that should not be affected by treatment (negative-control outcome) and *one* exposure that should not affect the outcome (negative-control exposure). Their differential bias identifies the unobserved network confounder.

### 5. Latent space / latent variable models

Hoff (2005), Hoff, Raftery & Handcock (2002): assume each node has a position in a latent Euclidean / Riemannian space, and tie probability and behavior similarity both depend on latent position. The latent variable absorbs unobserved homophily. R packages: `latentnet`, `eigenmodel`.

This is principled but identification of the influence effect now depends on the parametric form of the latent space model. Misspecification reintroduces bias.

### 6. Field experiments with structured rollout

Aral & Walker (2012), Bond et al. (2012, Facebook): randomize treatment at the *network* level — randomly assign some nodes to be exposed and study spillover. This identifies the *peer-influence-from-treatment-status* effect even without identifying the influence-from-outcome effect.

### 7. Difference-in-differences with network exposure

When peers' behaviors change exogenously (e.g., due to a policy applied to some), DID on network exposure gives a valid causal estimate of peer effects on the response. Requires the "parallel trends" assumption applied to the network setting (Manski 2013).

## Detecting homophily / autocorrelation

Before claiming influence, demonstrate that there is anything to explain. Measures of network autocorrelation:

### Moran's I (network version)

`I = (n / Σ_ij w_ij) · Σ_ij w_ij (y_i - ȳ)(y_j - ȳ) / Σ_i (y_i - ȳ)²`

where W is the (typically row-normalized) network adjacency matrix. Positive I means similar values cluster among connected nodes; can test against permutation null. `spdep` in R or custom.

### Geary's C

Local autocorrelation; similar idea, different functional form. More sensitive to local differences.

### E-I index (Krackhardt & Stern 1988)

For categorical attributes: `E - I) / (E + I)` where E = ties between groups, I = ties within. Negative = within-group bias (homophily); positive = between-group bias.

### Newman's assortativity coefficient

For categorical: `r = (Σ_i e_ii - Σ_i a_i b_i) / (1 - Σ_i a_i b_i)` where e_ij is fraction of edges between category i and j. For continuous: Pearson correlation of attribute values of edge endpoints.

NetworkX: `nx.attribute_assortativity_coefficient(G, 'attr')`, `nx.numeric_assortativity_coefficient`, `nx.degree_assortativity_coefficient`.

### ERGM-based test

Fit an ERGM with `nodematch` (categorical) or `absdiff` (continuous) and an appropriate set of structural controls. A significant nodematch coefficient says "there is homophily *after controlling for other network mechanisms*". This is stronger than raw assortativity, which conflates true homophily with degree-based artifacts (a popular node has more same-group ties just because it has more ties).

## Common analysis patterns and what they actually identify

| What user is doing | What they claim it identifies | What it actually identifies |
|---|---|---|
| Regress y_i on mean(y_friends) in cross-section | "Peer influence" | Almost nothing (reflection problem + homophily + common shocks) |
| ANOVA / regression with friend-attribute as covariate | "Contextual peer effects" | Possibly contextual effect, but not separated from common shocks or homophily |
| Friend-mean as IV for own friend behavior | "Causal peer effect" | If network is exogenous and Bramoullé conditions hold, yes; otherwise no |
| Network autocorrelation (Moran's I) on y | "Peer influence" | Just clustering of y on the network; doesn't say why |
| ERGM with nodematch coefficient | "Homophily" | Selection on observables; doesn't separate from latent homophily |
| SAOM with influence + selection effects | "Peer influence separated from selection" | Both, with caveats about the model's parametric assumptions |
| Diff-in-diff on policy + network exposure | "Causal peer effect" | Yes, the local average treatment effect, under parallel trends |
| RCT randomly assigning treatment, studying spillover | "Causal spillover effect" | Yes, the ITT spillover from randomization |

## When the user asks "do peers influence X?"

This is the protocol to follow:

1. **Establish the data structure.** Cross-sectional? Panel? RCT? Without panel data or experimental variation, peer-effect identification claims should be very modest.
2. **Discuss the four confounding mechanisms.** Make sure the user knows what they're up against; many users do not.
3. **Recommend the strongest available method.**
   - With RCT or quasi-experimental variation: standard causal inference with network-cluster SEs
   - With panel data (≥3 waves): SAOM with co-evolution
   - With cross-sectional but network exogeneity plausible: Bramoullé et al. IV
   - With cross-sectional and homophily plausible: latent space model
   - With only cross-sectional observational data and unmodeled homophily: descriptive analysis only; do NOT claim causation
4. **Report what you can and cannot say.** "We observe positive network autocorrelation in drinking (Moran's I = 0.34, p < 0.001). This is consistent with peer influence, but is also consistent with friends being similar before they became friends. To distinguish these, [next-step recommendation]."

## A note on Christakis & Fowler

The Christakis-Fowler studies on the "three degrees of influence" (obesity, smoking, loneliness, happiness spreading through social networks) are widely cited and have become canonical examples in the popular press. The methodological critiques (Cohen-Cole & Fletcher 2008; Lyons 2011; Noel & Nyhan 2011; Shalizi & Thomas 2011) are devastating but less widely known. If a user references these studies as evidence for contagion, the principled response is: the *observations* are real (clustering of behaviors in networks), but the *causal interpretation* (influence vs. homophily) is not identified.

## Canonical references

- Manski, C. F. (1993). "Identification of endogenous social effects: The reflection problem." *Review of Economic Studies* 60: 531–542.
- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). "Identification of peer effects through social networks." *Journal of Econometrics* 150: 41–55.
- Shalizi, C. R. & Thomas, A. C. (2011). "Homophily and contagion are generically confounded in observational social network studies." *Sociological Methods & Research* 40: 211–239.
- Snijders, T. A. B., Steglich, C. E. G., & Schweinberger, M. (2010). "Dynamic networks and behavior: Separating selection from influence." *Sociological Methodology* 40: 329–393.
- McPherson, M., Smith-Lovin, L., & Cook, J. M. (2001). "Birds of a feather: Homophily in social networks." *Annual Review of Sociology* 27: 415–444.
- Aral, S., Muchnik, L., & Sundararajan, A. (2009). "Distinguishing influence-based contagion from homophily-driven diffusion in dynamic networks." *PNAS* 106: 21544–21549.
- Egami, N. & Tchetgen Tchetgen, E. J. (2024). "Identification and estimation of causal peer effects using double negative controls for unmeasured network confounding." *JRSS-B* 86(2).
- Ogburn, E. L. (2018). "Challenges to estimating contagion effects from observational data." In *Complex Spreading Phenomena in Social Systems*. Springer.
