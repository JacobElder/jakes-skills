# Interpreting Peer Effects on Adolescent Smoking: A Critical Assessment

Your regression result is a useful starting point, but your advisor's interpretation — that this coefficient demonstrates peer *influence* — is almost certainly premature. Here is a careful unpacking of what you found, what it cannot yet tell you, and what you should do next.

---

## What Your Coefficient Actually Tells You

The coefficient of 0.43 on `mean_friends_smoking` means: for a one-unit increase in the proportion of close friends who smoke, a student's own smoking increases by 0.43 units on whatever scale you are using (binary, Likert, frequency?). The association is strong and statistically significant.

But this is an **association**, not a causal effect. The fundamental identification problem in peer effects research is that you cannot distinguish three very different data-generating processes from cross-sectional data alone:

1. **Peer influence (social contagion):** Friends cause a student to start smoking (or continue smoking) through direct social pressure, modeling, or norm transmission. This is what your advisor wants to claim.

2. **Homophily (selection):** Students who already smoke, or who are predisposed to smoke, preferentially befriend other smokers. The network forms *because of* shared behavior, not the other way around.

3. **Correlated unobservables (contextual effects):** Students in the same friendship group share a common environment — a neighborhood, a hangout spot, access to a specific dealer or social context — that independently causes all of them to smoke more, without any direct influence of one student on another.

Your regression cannot separate these three mechanisms. All three produce a positive, significant coefficient on `mean_friends_smoking`.

---

## Additional Statistical Concerns

**Reflection problem (Manski, 1993)**
If you regress individual behavior on group mean behavior, and group membership is endogenous, the coefficient is not identified. Your group mean (mean friends' smoking) is partly a function of the student's own behavior and choices. This creates a mechanical simultaneity that inflates your estimate. Manski's "reflection problem" is the canonical framing here — even with panel data, separating endogenous peer effects from correlated effects is very hard.

**Network endogeneity**
The friendship ties themselves are not random. Students chose their friends. Any model that treats the network as exogenous when the network reflects selection on the very outcome you are studying will produce biased estimates.

**Measurement of the outcome**
If smoking is binary (smoker/non-smoker), OLS is not ideal. A logistic regression or probit model would give you better-calibrated probabilities. The linear probability model can produce fitted values outside [0,1] and has heteroscedastic errors by construction.

**Potential non-independence of observations**
Students in the same school share many features (teachers, rules, culture, local environment). Your 312 students are not independent observations — they are clustered within a school, and within the school, they are embedded in a friendship network where observations are explicitly correlated by design. Standard errors from OLS assume independence and are almost certainly too small, making your p-value anticonservative.

**Directionality of nominations**
Did students nominate friends, or did you use mutual nominations? In directed networks, whether A nominates B but B does not nominate A has substantive meaning. If you are using outgoing nominations (who a student names), you may be measuring perceived norms or aspirational ties, not reciprocal influence relationships.

---

## What Would Actually Help

### Short term (within your existing data)

1. **Reformulate as a network autocorrelation model.** Rather than just using mean friends' smoking as a covariate, use a spatial/network lag model that accounts for the network structure more fully. The `spdep` package in R or `spreg` in Python can handle this, treating the adjacency matrix as the weight matrix.

2. **Check sensitivity to network definition.** Rerun your analysis using only mutual nominations, and separately with all nominations. If results change substantially, the finding is fragile.

3. **Separate contextual from endogenous effects.** Add controls for friends' characteristics other than smoking (e.g., mean friends' SES, mean friends' grade) to at least partially distinguish contextual from endogenous peer effects.

4. **Use robust standard errors.** Use heteroscedasticity-robust standard errors at minimum. Ideally, cluster standard errors at the clique or component level to account for within-cluster correlation.

5. **Network autocorrelation diagnostics.** Compute Moran's I for your residuals using the adjacency matrix as the weight matrix. If residuals are spatially autocorrelated, your model is misspecified.

### Medium term (redesign or supplementary data collection)

6. **Collect longitudinal data if at all possible.** Even one follow-up wave would transform your analysis. With two time points, you can control for lagged own behavior (T1 smoking predicting T2 smoking), which absorbs a large share of selection bias. The canonical design is the Cross-Lagged Panel Model or, better, a dynamic network model.

7. **Consider stochastic actor-based models (SABMs).** The Snijders/Ripple RSiena framework (implemented in the `RSiena` R package) jointly models network evolution and behavior evolution over time. It directly estimates selection effects (do smokers befriend smokers?) and influence effects (do friends' smoking habits change your own?) simultaneously. This is the current gold standard for disentangling homophily from influence in social network data. It requires panel data with at least two waves of both network and behavior measures.

8. **Consider exponential random graph models (ERGMs).** ERGMs model the probability of the observed network structure as a function of local network features (triangles, reciprocity, degree distributions) and actor attributes. They can help you understand whether the network structure itself is consistent with homophily on smoking — if smokers are significantly more likely to be tied to other smokers than chance would predict, that is evidence for selection, not influence.

9. **Natural experiments or instrumental variables.** Rare in school-based studies, but occasionally exploitable — e.g., random assignment to classrooms, school redistricting, or the entry/exit of a high-status peer. IV approaches require a valid instrument: something that affects who a student is friends with but does not independently affect their smoking behavior.

---

## How to Frame This for Your Advisor

Your advisor is right that this is an important finding worth investigating, but the claim that it "shows peer influence" is stronger than the data support at this stage. A more defensible framing:

> "We find a strong positive association between a student's smoking behavior and the average smoking behavior of their nominated friends (b = 0.43, p < 0.001), net of gender, grade, and SES. While consistent with peer influence on smoking, this cross-sectional result cannot rule out selection (smokers befriending smokers) or correlated contextual effects. Longitudinal data and actor-based network models are needed to identify the influence mechanism."

This is not a finding to discard — it is a finding to build on. Cross-sectional peer effects associations in adolescent smoking are actually a well-established literature (the foundational work by Nicholas Christakis and James Fowler on social contagion, though controversial; work by Simons-Morton and others on adolescent smoking networks), and your result fits the expected pattern. The question is whether you can move toward a causal claim.

---

## Key References to Engage

- **Manski, C. F. (1993).** "Identification of Endogenous Social Effects: The Reflection Problem." *Review of Economic Studies*, 60(3), 531–542. — The foundational paper on why peer effects are hard to identify.
- **Snijders, T. A. B., van de Bunt, G. G., & Steglich, C. E. G. (2010).** "Introduction to stochastic actor-based models for network dynamics." *Social Networks*, 32(1), 44–60. — The SABM framework for jointly modeling selection and influence.
- **Shalizi, C. R., & Thomas, A. C. (2011).** "Homophily and Contagion Are Generically Confounded in Observational Social Network Studies." *Sociological Methods & Research*, 40(2), 211–239. — A rigorous proof that homophily and contagion are not separable from cross-sectional data.
- **Christakis, N. A., & Fowler, J. H. (2008).** "The collective dynamics of smoking in a large social network." *New England Journal of Medicine*, 358, 2249–2258. — Influential but debated empirical work on smoking contagion.
- **Lyons, R. (2011).** "The spread of evidence-poor medicine via flawed social-network analysis." *Statistics, Politics, and Policy*, 2(1). — A methodological critique of the Christakis/Fowler approach.

---

## Summary

| Issue | Severity | What to do |
|---|---|---|
| Homophily/selection confound | High | Longitudinal data + SABM (RSiena) |
| Reflection problem | High | Acknowledge; use lagged or IV approaches |
| Network endogeneity | High | ERGM or joint network-behavior model |
| Non-independence of observations | Moderate | Cluster-robust or network-robust SEs |
| Binary outcome in OLS | Moderate | Logistic regression |
| Cross-sectional causal claim | High | Reframe as association; hedge interpretation |

Your 0.43 coefficient is a real and interesting finding. It just does not yet mean what your advisor says it means. The path forward is more data (longitudinal) and better models (SABM/ERGM). If longitudinal data collection is not feasible for your dissertation timeline, a well-reasoned cross-sectional analysis with honest identification limitations and network-autocorrelation-aware inference is still publishable — but the causal claim needs to be hedged clearly.
