# Interpreting Your Peer Effects Result: A Critical Assessment

Your setup — 312 students, friendship nominations, binary smoking outcome, OLS regression with mean_friends_smoking as the key predictor — is one of the most common analyses in social network research, and one of the most commonly misinterpreted. The coefficient of 0.43 (p < 0.001) is real, but it does not identify peer influence. Here is exactly why, what it does show, and what you should do next.

---

## What your result actually tells you

You have found **positive network autocorrelation in smoking**: students whose close friends smoke are themselves more likely to smoke. This is a genuine and substantive finding. But the question of *why* smokers cluster in friendship networks has at least four competing explanations that your cross-sectional OLS cannot distinguish:

1. **Endogenous peer effects (influence/contagion):** your friends' smoking causes you to smoke — the mechanism your advisor has in mind
2. **Correlated effects (homophily/selection):** you become friends with students who already smoke because you are already similar to them, or already smoke yourself
3. **Common environmental shocks:** both you and your friends smoke because you share the same environment — a neighborhood, a hangout spot, a social event where smoking is prevalent — and friendship is also driven by proximity
4. **Exogenous contextual effects:** your friends' background characteristics (e.g., parental smoking, SES) affect your smoking independently of their behavior

These are Manski's (1993) classic four-part decomposition, and your data cannot separate them.

---

## The two identification problems your regression hits

### 1. The reflection problem (Manski 1993)

When you regress `smoking_i` on `mean(smoking_friends_i)`, you are estimating:

```
y_i = α + β · ȳ_{-i} + γ · X_i + ε_i
```

where `ȳ_{-i}` is the mean smoking of i's friends. In a group or cohort setting this is **mechanically unidentified**: the mean of friends' smoking is itself determined by the same model, creating perfect collinearity between the endogenous and contextual effects. You cannot separate "I smoke because my friends smoke" from "we are in the same group and the same background factors drive us all."

*Can this be fixed?* In a network (rather than group) setting, Bramoullé, Djebbari & Fortin (2009) show that **intransitive triads** — i connected to j, j connected to k, but i not connected to k — provide a valid instrument: k's covariates affect i's outcome only through j's behavior. If your network has enough intransitive triads (the matrices I, G, G² must be linearly independent), you can use this GMM/IV approach. But this still requires network exogeneity.

### 2. The Shalizi-Thomas confound

Shalizi & Thomas (2011) prove a stronger result: **even with longitudinal data** (not just cross-sectional), homophily and contagion are generically confounded in observational network data unless you have time-precedence evidence (friendships formed *before* behavior diverged) or exogenous variation in tie formation. With a single cross-sectional wave, you have neither. The same pattern — friends with similar smoking rates — is equally consistent with:

- Students who smoke befriending other smokers (selection/homophily)
- Students who are friends causing each other to take up smoking (influence)
- Both happening simultaneously in some proportion

Your regression cannot distinguish these.

---

## What your coefficient of 0.43 means and doesn't mean

**What it means:** A 10-percentage-point increase in the smoking rate among a student's close friends is associated with a 4.3-percentage-point increase in the probability that the student smokes, after controlling for gender, grade, and SES. This is a descriptive association.

**What it does not mean:**
- It does not mean that if you randomly assigned a new smoking friend to a non-smoker, that student's smoking probability would increase by 4.3 pp
- It does not mean peer influence accounts for 0.43 of the effect; selection may account for all or most of it
- It does not isolate peer effects from correlated exposures

**Your advisor's claim is premature.** The coefficient is consistent with peer influence but is also fully consistent with homophily. Claiming it "shows peer influence" overstates what cross-sectional OLS can identify — this is a known and well-documented limitation, not a minor caveat.

---

## What you *can* legitimately report

You can report:
1. **The network autocorrelation pattern:** smoking clusters within friendship networks in this school. Compute and report Moran's I as a direct measure of this.
2. **The descriptive association** with appropriate hedging: "After controlling for gender, grade, and SES, having friends who smoke is associated with a substantially higher probability of smoking (β = 0.43, p < 0.001). This association is consistent with peer influence, selection of similar peers, or shared environmental factors."
3. **The degree of clustering** relative to a null: compare your observed clustering to a configuration-model null (randomly rewiring the network while preserving degree sequence) to establish that the correlation is not a statistical artifact.

---

## Recommended next steps (in order of defensibility)

### Strongly recommended for your dissertation

**Option A: Collect longitudinal data (SAOM)**

The most defensible observational approach for your exact question is a **Stochastic Actor-Oriented Model (SAOM)** using RSiena. This requires:
- At least 2 more waves of data (3+ total), spaced roughly one semester apart
- Friendship nominations at each wave
- Smoking status at each wave
- Substantial change in both the network and smoking behavior between waves

SAOM jointly models (a) students' decisions to add/drop friendships and (b) students' decisions to start/stop smoking. The selection effect (`simX` term: tendency to befriend similar smokers) and influence effect (`avAlt` or `totSim` term: tendency to adopt friends' smoking behavior) are partially identified through **timing**: if smoking changes after friendship forms, that contributes to the influence estimate; if friendship changes toward similar-smokers, that contributes to selection. This is the standard methodology in adolescent behavior research (e.g., Steglich, Snijders & Pearson 2010).

```r
# RSiena setup sketch (requires panel data)
library(RSiena)

# Create data objects
network <- sienaNet(array_of_adjacency_matrices)  # T x n x n array across waves
smoking  <- sienaDependent(matrix_of_smoking,     type = "behavior")
gender   <- coCovar(gender_vector)
grade    <- coCovar(grade_vector)
SES      <- coCovar(ses_vector)

mydata <- sienaDataCreate(network, smoking, gender, grade, SES)

# Specify model (structural effects + selection + influence)
myeff <- getEffects(mydata)
myeff <- includeEffects(myeff, transTrip, cycle3)            # network structure
myeff <- includeEffects(myeff, simX, interaction1="smoking") # selection
myeff <- includeEffects(myeff, avAlt, interaction1="smoking") # influence
myeff <- includeEffects(myeff, egoX, altX, simX, interaction1="gender")

myAlgorithm <- sienaAlgorithmCreate(projname = 'smoking_saom')
ans <- siena07(myAlgorithm, data=mydata, effects=myeff)
summary(ans)
```

**Option B: Bramoullé IV (cross-sectional, if collecting new data is impossible)**

If you are limited to cross-sectional data, you can attempt identification using the network structure. The instrument is the **mean of friends-of-friends' background characteristics** (SES, parental smoking if you can collect it, grade), under the assumption that these affect a student's smoking only through their direct friends' behavior — not directly.

This requires:
1. The network has enough intransitive triads (i→j→k but not i→k)
2. The instruments (friends-of-friends' characteristics) are genuinely exogenous
3. Strong first-stage relationship (friends-of-friends' characteristics predict friends' smoking)

In R:
```r
# Bramoullé IV approach
library(ivreg)

# W = row-normalized adjacency; W2 = W %*% W (friends of friends)
# Instruments: W2 %*% X (friends-of-friends' characteristics)

iv_model <- ivreg(
  smoking ~ mean_friends_smoking + gender + grade + SES |
            gender + grade + SES + W2_SES + W2_grade,
  data = student_data
)
summary(iv_model, diagnostics = TRUE)  # Check weak instruments (F > 10)
```

**Option C: Describe and contextualize (minimum viable option)**

If neither panel data nor clean instruments are available, the honest approach is:
1. Report the association with appropriate hedging
2. Compute Moran's I and the E-I index for smoking by friendship
3. Conduct a sensitivity analysis: how large would the selection effect need to be to fully explain the observed association? (Cinelli & Hazlett sensitivity framework applied to network settings)
4. Discuss SAOM as the needed next step in your limitations section

---

## Supplementary analyses to run now

These are defensible and add substance without overclaiming:

**1. Compute network autocorrelation directly (Moran's I)**

```python
import numpy as np
import networkx as nx

# G = your friendship network (directed; treat as undirected for Moran's I)
# smoking = {node_id: 0/1}

# Row-normalized adjacency
A = nx.to_numpy_array(G)
W = A / (A.sum(axis=1, keepdims=True) + 1e-9)

y = np.array([smoking[n] for n in G.nodes()])
y_centered = y - y.mean()
n = len(y)

# Moran's I
I = (n / A.sum()) * (y_centered @ W @ y_centered) / (y_centered @ y_centered)
print(f"Moran's I = {I:.3f}")

# Permutation test
null_Is = []
for _ in range(9999):
    y_perm = np.random.permutation(y_centered)
    null_Is.append((n / A.sum()) * (y_perm @ W @ y_perm) / (y_perm @ y_perm))
p_value = np.mean(np.array(null_Is) >= I)
print(f"p (permutation, 9999 draws) = {p_value:.4f}")
```

**2. Check assortativity**

```python
nx.attribute_assortativity_coefficient(G, 'smoking')
# Positive value confirms smokers are disproportionately connected to smokers
```

**3. Descriptive baseline statistics to report**

Always report these alongside any peer-effects claim:
- n = 312, directed friendship nominations
- Network density
- Mean and SD of in-degree and out-degree
- Reciprocity (what fraction of nominations are mutual?)
- Global clustering coefficient
- Smoking prevalence overall and by grade/gender/SES

These ground the analysis and catch data errors before they propagate.

---

## What to tell your advisor

Your advisor's interpretation is substantively reasonable — peer effects on adolescent smoking are real and well-documented in experimental and longitudinal studies. But the cross-sectional OLS you ran cannot identify them. The honest framing is:

> "We find significant positive network autocorrelation in smoking behavior (β = 0.43, p < 0.001), consistent with the peer effects hypothesis. However, cross-sectional data cannot separate peer influence from selection of similar friends or shared environmental exposures (Manski 1993; Shalizi & Thomas 2011). To identify the causal peer effect, we recommend [SAOM with longitudinal data / Bramoullé et al. IV]. The current analysis should be treated as descriptive evidence of clustering."

This is not a fatal critique of your work — it reframes what you can claim and points clearly to the stronger next step.

---

## Summary

| Question | Answer |
|---|---|
| Does β = 0.43 show peer influence? | No; it shows network autocorrelation in smoking, which is consistent with peer influence, homophily, or shared environment |
| Is the result real? | Yes — smokers are disproportionately connected to smokers, and the association survives gender/grade/SES controls |
| What identification problem does your regression hit? | The Manski reflection problem and the Shalizi-Thomas confound |
| What is the strongest observational fix? | SAOM (RSiena) with ≥3 panel waves |
| What can you do right now with cross-sectional data? | Moran's I, E-I index, assortativity, descriptive clustering — plus Bramoullé IV if you have instruments |
| What should you claim in your paper? | Descriptive association, with SAOM as the explicit next step |

---

## Key references

- Manski, C. F. (1993). "Identification of endogenous social effects: The reflection problem." *Review of Economic Studies* 60: 531–542.
- Shalizi, C. R. & Thomas, A. C. (2011). "Homophily and contagion are generically confounded in observational social network studies." *Sociological Methods & Research* 40: 211–239.
- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). "Identification of peer effects through social networks." *Journal of Econometrics* 150: 41–55.
- Snijders, T. A. B., Steglich, C. E. G., & Schweinberger, M. (2010). "Dynamic networks and behavior: Separating selection from influence." *Sociological Methodology* 40: 329–393.
- McPherson, M., Smith-Lovin, L., & Cook, J. M. (2001). "Birds of a feather: Homophily in social networks." *Annual Review of Sociology* 27: 415–444.
