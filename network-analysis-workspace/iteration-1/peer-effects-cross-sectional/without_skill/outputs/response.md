# Interpreting Your Peer Effects Regression: Issues and Next Steps

## What Your Result Says — and Doesn't Say

Your regression coefficient of 0.43 (p < 0.001) on `mean_friends_smoking` means that a one-unit increase in the proportion of friends who smoke is associated with a 0.43-unit increase in smoking (or, if smoking is binary, a 0.43 increase in the probability of smoking). The result is statistically significant and practically sizeable. That part is solid.

**The problem:** Your advisor's interpretation — that this shows *peer influence* — is not warranted from a cross-sectional design. This is one of the most well-known identification problems in social network research, first formalized by Charles Manski (1993) as the "reflection problem." There are three distinct processes that can produce the pattern you observe, and your data cannot distinguish among them:

### The Three Competing Explanations

1. **Peer influence (social contagion):** Students adopt the smoking behavior of their friends. This is what your advisor wants to conclude.

2. **Homophily (selection):** Smokers tend to befriend other smokers, and non-smokers befriend non-smokers. The correlation between ego and alter behavior arises from who chooses to be friends with whom, not from influence after the friendship forms. This is extremely well-documented in adolescent social networks.

3. **Shared contextual exposure (correlated effects):** Students who are friends also share environments — the same neighborhood, the same teachers, the same social spaces. Some third factor (e.g., a neighborhood with high adult smoking norms, a school context where smoking is tolerated) drives both the friendship formation and the smoking behavior simultaneously.

With a single cross-section, you observe everyone at one moment in time. You cannot tell whether Student A smokes *because* their friend B smokes (influence), or whether A and B became friends *because* they both smoke (selection), or whether A and B both smoke because they both live in the same high-risk neighborhood (context). All three mechanisms produce a positive correlation between ego smoking and mean friend smoking.

### Why This Matters for Your Coefficient

The 0.43 you estimated is almost certainly an upward-biased estimate of the true peer influence effect, because it conflates influence, selection, and contextual effects. This has been demonstrated empirically in longitudinal studies that can separate the mechanisms: when selection is accounted for, peer influence effects on adolescent smoking are typically substantially smaller than cross-sectional estimates suggest.

---

## What to Do Next

### 1. Reframe Your Claim (Immediately)

At minimum, revise your interpretation. A defensible claim is: "Students whose friends smoke at higher rates are significantly more likely to smoke themselves (b = 0.43, p < 0.001), consistent with peer socialization or homophilic selection processes." Do not claim directional influence without longitudinal data.

### 2. Collect or Obtain Longitudinal Data

This is the most important methodological step. If you can obtain data at two or more time points — even just a second wave — you can begin to separate influence from selection. The key design:
- Wave 1: friendship nominations + smoking status
- Wave 2 (e.g., 6 months later): same measures

This allows you to model whether Wave 2 smoking is predicted by Wave 1 friends' smoking, controlling for Wave 1 ego smoking (lagged dependent variable approach). This substantially reduces, though does not eliminate, confounding from homophily.

### 3. Use Stochastic Actor-Based Models (SABMs) if Longitudinal Data Exist

If you have two or more waves, the gold-standard approach for simultaneously estimating influence and selection in network data is **Stochastic Actor-Based Modeling**, implemented in the R package `RSiena`. SABMs model the co-evolution of network ties and behavior:
- A **network dynamics** submodel estimates who befriends whom (captures homophily)
- A **behavior dynamics** submodel estimates how behavior changes given network position (captures influence)

This lets you test whether influence effects on smoking remain significant after accounting for the tendency of smokers to select into friendships with other smokers.

### 4. Instrumental Variables (If Longitudinal Data Are Unavailable)

If you're stuck with cross-sectional data, an instrumental variables (IV) approach can in principle identify peer influence by finding an instrument that affects friends' smoking but is unrelated to ego's smoking except through the peer channel. In practice, finding valid instruments in closed school networks is very difficult. One approach used in the literature: use **friends-of-friends** smoking rates as an instrument for friends' smoking (the logic being that your friends' friends influence your friends, but affect you only through your friends). This is not bulletproof but is defensible.

### 5. Consider Propensity Score Matching or Selection Models

If your data include rich pre-treatment covariates (family smoking history, personality measures, prior smoking onset), you can use matching methods or Heckman-style selection corrections to partial out selection bias. These are partial solutions at best but strengthen your identification argument.

### 6. Descriptive Network Analysis (Strengthen the Paper Now)

While pursuing better identification, you can strengthen your current paper with descriptive network analyses that characterize the structure of smoking-related clustering:

- **Assortativity / segregation index:** Quantify how much smokers cluster with other smokers beyond chance. Newman's assortativity coefficient or the E-I index (Krackhardt & Stern) are standard.
- **Visualization:** Network sociograms with smoking status coded by node color show reviewers and readers the clustering pattern directly.
- **Moran's I on the network:** A spatial autocorrelation statistic adapted to network adjacency shows whether smoking is clustered non-randomly in the network.

These don't prove influence, but they document that the social structure of smoking is non-random, which motivates the research question.

### 7. Review Key Literature to Situate Your Findings

You should engage explicitly with the identification problem in your write-up:
- **Manski (1993)** — "Identification of endogenous social effects: The reflection problem" — the foundational statement of why cross-sectional peer effects are hard to identify
- **Snijders et al. (2010)** — "Introduction to stochastic actor-based models for network dynamics" — the SABM framework
- **Mercken et al. (2010)** — "Dynamics of adolescent friendship networks and smoking behavior" — an applied SABM paper on adolescent smoking specifically
- **Christakis & Fowler (2008)** — "The collective dynamics of smoking in a large social network" — influential but methodologically controversial; good to know the debate

---

## Summary of What You Have and What It Supports

| Claim | Supported by your data? |
|---|---|
| Smoking is socially clustered in this school | Yes |
| Students with more smoking friends are more likely to smoke | Yes |
| Friends *cause* students to take up smoking | No — requires longitudinal data + selection controls |
| The coefficient 0.43 is an unbiased estimate of peer influence | Almost certainly not |

Your result is a real finding — social clustering of smoking is substantively important regardless of mechanism. But your next step is either (a) reframe the contribution as documenting social clustering and argue for the need for longitudinal study, or (b) obtain longitudinal data and apply SABMs to actually test the influence vs. selection question.

If you're writing a dissertation chapter, option (b) is strongly preferred. If this is a conference paper or pilot study, option (a) with honest acknowledgment of the limitation is defensible and publishable.
