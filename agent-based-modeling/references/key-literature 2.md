# Key Literature — Annotated Bibliography

Organized by phase so you can cite the right source for the task at hand. Use
these when the user is writing up a model, defending a method, or wants to go
deeper. Verify exact details (page numbers, DOIs) against the source before
putting them in a manuscript — citation metadata drifts.

---

## Foundational texts and overviews

- **Railsback, S. F. & Grimm, V. (2019). *Agent-Based and Individual-Based
  Modeling: A Practical Introduction* (2nd ed.). Princeton University Press.**
  The standard textbook. Teaches the full cycle — design, programming (in
  NetLogo), documentation, analysis — organized around modeling *concepts*
  (emergence, observation, sensing, adaptation, etc.) and the modeling cycle.
  Start here for almost anyone learning ABM.

- **Epstein, J. M. & Axtell, R. (1996). *Growing Artificial Societies: Social
  Science from the Bottom Up*. MIT Press / Brookings.** The Sugarscape work;
  origin of the **generative** view of social science ("if you didn't grow it, you
  didn't explain it") and the idea of growing whole artificial societies.

- **Schelling, T. C. (1971/1978). Models of segregation / *Micromotives and
  Macrobehavior*.** The canonical demonstration that mild individual preferences
  can produce strong macro segregation — the archetypal KISS model and the
  cleanest illustration of emergence.

- **Bonabeau, E. (2002). Agent-based modeling: methods and techniques for
  simulating human systems. *PNAS* 99(suppl 3):7280–7287.** Compact, widely cited
  argument for *when* ABM adds value (heterogeneity, interaction, emergence).

- **Wilensky, U. & Rand, W. (2015). *An Introduction to Agent-Based Modeling*.
  MIT Press.** NetLogo-based companion text from NetLogo's creator; strong on
  building intuition and on verification/validation basics.

- **Smaldino, P. E. (2023). *Modeling Social Behavior*. Princeton University
  Press.** Modern treatment integrating mathematical and agent-based models of
  social dynamics; good on the epistemics of modeling choices.

---

## Documentation: the ODD protocol and extensions

- **Grimm, V., et al. (2006). A standard protocol for describing individual-based
  and agent-based models. *Ecological Modelling* 198:115–126.** The original ODD.

- **Grimm, V., et al. (2010). The ODD protocol: a review and first update.
  *Ecological Modelling* 221(23):2760–2768.** First revision; clarifies the
  elements based on usage.

- **Grimm, V., et al. (2020). The ODD protocol for describing agent-based and
  other simulation models: a second update to improve clarity, replication, and
  structural realism. *JASSS* 23(2):7. DOI:10.18564/jasss.4259.** Current
  reference: adds model rationale and evaluation, guidance for complex models and
  ODD summaries, and argues ODD generalizes beyond ABM. **Cite this as the current
  ODD standard.**

- **Müller, B., et al. (2013). Describing human decisions in agent-based models —
  ODD+D. *Environmental Modelling & Software* 48:37–48.** The ODD+D extension for
  documenting human decision-making; use for social/economic/land-use models.

- **Grimm, V., et al. (2014). Towards better modelling and decision support:
  documenting model development, testing, and analysis using TRACE.
  *Ecological Modelling* 280:129–139.** (with Schmolke et al. 2010 as the
  precursor.) Documents the *evidence* that a model is fit for purpose; pair with
  ODD for decision-support models.

- **CoMSES Net / OpenABM (comses.net).** Community repository and reproducibility
  standards; the place to deposit and find peer-reviewed ABMs.

---

## Design and pattern-oriented modeling

- **Grimm, V., et al. (2005). Pattern-oriented modeling of agent-based complex
  systems: lessons from ecology. *Science* 310:987–991.** The POM manifesto —
  using multiple observed patterns at different scales to design, filter, and
  validate models simultaneously. Central methodological citation.

- **Grimm, V. & Railsback, S. F. (2012). Pattern-oriented modelling: a
  "multi-scope" for predictive systems ecology. *Phil. Trans. R. Soc. B*
  367:298–310.** Extends POM toward prediction.

- **Edmonds, B. & Moss, S. (2005). From KISS to KIDS — an "anti-simplistic"
  modelling approach.** Articulates the KIDS alternative to KISS and when to prefer
  descriptive starting points.

---

## Verification, calibration, validation

- **Galán, J. M., et al. (2009). Errors and artefacts in agent-based modelling.
  *JASSS* 12(1):1.** The reference on the error-vs-artefact distinction and where
  accidental assumptions (topology, scheduling) masquerade as findings.

- **Manson, S. M. (2002). Validation and verification of multi-agent systems.** In
  Janssen (ed.), *Complexity and Ecosystem Management*. Early, clear V&V framing
  for ABMs.

- **ten Broeke, G., van Voorn, G. & Ligtenberg, A. (2016). Which sensitivity
  analysis method should I use for my agent-based model? *JASSS* 19(1):5.** Also
  covers replication/CV-convergence reasoning; practical and ABM-specific.

- **Thiele, J. C., Kurth, W. & Grimm, V. (2014). Facilitating parameter estimation
  and sensitivity analysis of agent-based models. *JASSS* 17(3):11.** Hands-on
  calibration + SA workflow (with NetLogo/R), including the CV-convergence approach
  to choosing replications (building on Lorscheid et al. 2012).

- **Lee, J.-S., et al. (2015). The complexities of agent-based modeling output
  analysis. *JASSS* 18(4):4.** On sampling, statistics, and the significance-from-
  sheer-run-count trap.

- **Srikrishnan, V. & Keller, K. (2021). Small increases in model complexity can
  result in large increases in required calibration data. *Environmental Modelling
  & Software* 138:104978 (preprint: arXiv:1811.08524).** Key result on
  over-parameterization, identifiability, and data hunger.

- **Hierarchical ABM Validation (HAV) framework.** *Towards Standardizing
  Validation Practices in Agent-Based Modeling*, **ACM TOMACS (2026).** Defines
  calibration/verification/validation, reviews ~17 validation approaches, and
  organizes them across agent/model/output levels.

- **On calibration machinery:** Grazzini, Richiardi & Tsionas (2017) on Bayesian
  estimation of ABMs; **Approximate Bayesian Computation** for intractable
  likelihoods; **history matching / emulation** (Gaussian-process surrogates) for
  expensive models; simulation-based calibration for verifying the calibration
  procedure itself.

---

## Analysis, sensitivity, and experiments

- **Borgonovo, E., et al. (2022). Sensitivity analysis of agent-based models: a
  new protocol. *Computational & Mathematical Organization Theory*.** Adapts
  global SA (and ICE-style plots) to stochastic ABM responses, with significance
  testing for small mean differences.

- **Lorscheid, I., Heine, B.-O. & Meyer, M. (2012). Opening the "black box" of
  simulations: increased transparency and effective communication through the
  systematic design of experiments. *CMOT* 18:22–62.** DoE discipline for
  simulations; source for CV-based replication choice.

- **Lee et al. (2015)** (above) and **ten Broeke et al. (2016)** (above) double as
  the practical analysis references.

---

## ABM vs. equation-based, and limitations

- **Rahmandad, H. & Sterman, J. (2008). Heterogeneity and network structure in the
  dynamics of diffusion: comparing agent-based and differential equation models.
  *Management Science* 54(5):998–1014.** Shows calibrated DE models can closely
  reproduce ABM output under well-mixed conditions — the empirical basis for "don't
  use ABM when a simpler model suffices."

- **Squazzoni, F. (2010); Bruch, E. & Atwell (2015), *Agent-based models in
  empirical social research* (*Sociological Methods & Research*).** Balanced
  reviews of promise and limitations in social science, including data and
  validation challenges.

- **Critiques to engage with honestly:** the "too many ad-hoc assumptions / free
  parameters" critique (note it applies to hidden assumptions in equation-based
  models too), the black-box/interpretability critique, and computational-cost
  constraints. See `limitations-and-pitfalls.md` for how to address each.

---

## Domain entry points

- **Epidemiology:** compartmental (SIR) vs. ABM trade-offs; ABMs shine when
  contact networks and heterogeneity drive transmission. (Marshall & Galea 2015;
  Hunter et al. 2017.)
- **Economics / finance:** agent-based computational economics (Tesfatsion & Judd,
  *Handbook of Computational Economics* vol. 2, 2006); ABM responses to DSGE
  limitations after 2008 (Dosi & Roventini).
- **Ecology:** Railsback & Grimm (above); DeAngelis & Grimm on individual-based
  ecology.
- **Geographical / urban systems:** Heppenstall, Crooks, See & Batty (eds.),
  *Agent-Based Models of Geographical Systems* (2012); Crooks, Castle & Batty on
  key challenges in geospatial ABM.
- **Land use:** Parker et al. (2003) review of multi-agent land-use/land-cover
  models.
