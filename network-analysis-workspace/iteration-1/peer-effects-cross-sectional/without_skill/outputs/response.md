# Interpreting Cross-Sectional Peer Effects on Adolescent Smoking

## Your Result and What It Actually Shows

Your coefficient of 0.43 (p < 0.001) on `mean_friends_smoking` says: students whose friends smoke at higher rates are themselves more likely to smoke, even after adjusting for gender, grade, and SES. That's a real association, and it's worth taking seriously. But your advisor's claim — that this *shows peer influence* — is almost certainly too strong. The core problem is that a cross-sectional regression cannot disentangle three fundamentally different processes that all produce the same coefficient:

1. **Peer influence (social contagion):** Adolescents adopt the smoking behavior of their friends. This is what your advisor wants to claim.
2. **Homophily (selection):** Adolescents who already smoke (or are inclined to) preferentially befriend other smokers. The association exists even if nobody ever influenced anyone.
3. **Shared contextual factors (confounding):** Friends who share the same neighborhood, school corridor, extracurricular activity, or family background are exposed to the same environmental pressures — adult smoking in the household, tobacco availability, local norms — that independently drive both their friendship ties and their smoking.

Your regression controls for grade and SES, which partially addresses confounding, but these are crude proxies. Shared micro-environments (the specific friend group's social context) are not captured by individual-level controls.

This identification problem is sometimes called the **reflection problem** (Manski, 1993): in a cross-section, the individual's outcome, their peers' outcomes, and shared background are all simultaneously determined, and you cannot tell which caused which.

---

## Why the Coefficient Is Likely Biased

**Toward overestimation:**
- Smokers select into friendships with other smokers (homophily inflates the coefficient).
- Unmeasured shared contexts (e.g., both friends hang out near a convenience store that sells to minors) create spurious correlation.

**Toward underestimation:**
- Friendship nominations are asymmetric and noisy. Your `mean_friends_smoking` averages over all nominated friends, but influence may flow from specific close ties, not all nominees equally.
- Reverse causation (your own smoking affecting who nominates you) is folded into the estimate.

The net direction of bias is empirically uncertain, but the simulation literature (e.g., Shalizi & Thomas, 2011) shows that even under pure homophily with zero true influence, OLS on cross-sectional network data will recover a substantial positive coefficient. You cannot rule that out here.

---

## What to Do Next

### 1. Reframe the claim (immediately, no new data needed)

Change "this shows peer influence" to "this shows that smoking is socially clustered among friends, consistent with peer influence, homophily, or shared contexts." This is defensible; the stronger causal claim is not.

### 2. Examine the network structure descriptively

Before any causal modeling, characterize the friendship network:
- Calculate network-level statistics: density, clustering coefficient, average degree.
- Plot the network with nodes colored by smoking status. Visual clustering tells you whether homophily is concentrated in specific cliques or diffuse.
- Compute observed assortativity (e.g., Moran's I or a simple correlation of smoking with mean neighbor smoking) and compare to a permutation null that randomizes smoking labels while holding network structure fixed. This tells you whether the clustering is stronger than chance.

These descriptives belong in your paper regardless of what modeling approach you take.

### 3. Test the selection vs. influence question with stochastic actor-based models (if you can get longitudinal data)

The gold standard for peer influence vs. selection is a **stochastic actor-based model (SABM)**, implemented in the R package `RSiena`. SABMs model the co-evolution of the friendship network and behavior simultaneously, with separate parameters for:
- **Selection:** Do smokers preferentially form ties with smokers?
- **Influence:** Do individuals shift their behavior toward their friends' behavior, net of selection?

This requires at least two waves of data (network + behavior at T1 and T2). If you can go back to the school and collect a second wave, or access archival data from a second time point, this is the most credible path. Mercken et al. (2010) apply exactly this framework to adolescent smoking and are a direct model for your study.

### 4. If you're stuck with one wave: partial remedies

Cross-sectional data limits you severely, but these steps add rigor:

**Contextual/structural controls:** Add node-level network controls (degree, betweenness centrality) to your regression. If the `mean_friends_smoking` coefficient drops substantially, this suggests network position itself is confounding the estimate.

**Alter characteristics beyond smoking:** If you have data on friends' other attributes (parental smoking, risk-taking attitudes, sports participation), ask whether the effect of `mean_friends_smoking` survives controlling for these. Persistence is at least consistent with influence, though not proof.

**Sensitivity analysis for homophily:** Use the approach from Shalizi & Thomas (2011) or VanderWeele et al. (2012) to bound the peer influence estimate under varying assumptions about unmeasured homophily.

**Instrumental variables:** Find a variable that affects peer smoking but is unrelated to your own smoking propensity except through peers. One instrument used in the literature: smoking rates of friends-of-friends (alters not in your direct network). Whether a valid instrument exists in your specific data is an empirical question, and this approach requires strong theoretical justification.

### 5. Strengthen the regression you already have

Even within the cross-sectional framing:
- Use **robust standard errors**, since binary outcomes with linear probability models produce heteroskedastic residuals.
- If smoking is binary, consider **logistic regression** and report both odds ratios and average marginal effects.
- Report whether the coefficient on `mean_friends_smoking` changes when you add network structural controls (degree, clustering coefficient of ego's neighborhood). Changes signal confounding by network position.
- Test for heterogeneity by grade and gender — peer influence mechanisms in the smoking literature often show developmental and gender-specific patterns.

---

## How to Frame This in Your Paper

A defensible framing for a cross-sectional study:
- Lead with the descriptive finding: smoking is significantly clustered among friends, even after adjusting for individual demographic and socioeconomic factors.
- Acknowledge the three competing mechanisms and state explicitly that cross-sectional data cannot adjudicate among them.
- Position your study as establishing that the association exists and motivating longitudinal follow-up.
- Cite the methodological literature on peer effects identification (Manski 1993; Shalizi & Thomas 2011) to demonstrate you understand the limits.

This framing is honest, methodologically sound, and will survive peer review. The strong causal claim will not.

---

## Summary Table

| Claim | Supported by your data? |
|---|---|
| Smoking is socially clustered among friends in this school | Yes |
| Students with more smoking friends are more likely to smoke | Yes |
| Peer influence *causes* students to take up smoking | No — requires longitudinal data + selection controls |
| The 0.43 coefficient is an unbiased estimate of peer influence | Almost certainly not |

---

## Key References

- Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. *Review of Economic Studies, 60*(3), 531–542.
- Shalizi, C. R., & Thomas, A. C. (2011). Homophily and contagion are generically confounded in observational social network studies. *Sociological Methods & Research, 40*(2), 211–239.
- Snijders, T. A. B., van de Bunt, G. G., & Steglich, C. E. G. (2010). Introduction to stochastic actor-based models for network dynamics. *Social Networks, 32*(1), 44–60.
- Mercken, L., Snijders, T. A. B., Steglich, C., Vartiainen, E., & de Vries, H. (2010). Dynamics of adolescent friendship networks and smoking behavior. *Social Networks, 32*(1), 72–81.
- VanderWeele, T. J., Ogburn, E. L., & Tchetgen Tchetgen, E. J. (2012). Why and when "flawed" social network analyses still yield valid tests of no contagion. *Statistics, Politics and Policy, 3*(1).
- Christakis, N. A., & Fowler, J. H. (2008). The collective dynamics of smoking in a large social network over 32 years. *New England Journal of Medicine, 358*(21), 2249–2258. (Influential but methodologically contested — read alongside Lyons 2011 for the debate.)
