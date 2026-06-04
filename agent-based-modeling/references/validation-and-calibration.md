# Verification, Calibration, and Validation

People constantly conflate these three. Keeping them distinct is the single
biggest improvement most ABM projects can make to their credibility.

**Contents**
1. The three definitions (and why the order matters)
2. Verification — is the model built right?
3. Calibration — tuning to data
4. Validation — is it the right model?
5. Pattern-Oriented Modeling as calibration + validation
6. Calibration machinery: ABC, Bayesian, history matching, emulators
7. A hierarchical (agent / model / output) validation framework
8. Reproducibility of the validation itself

---

## 1. The three definitions

- **Verification** — *Did I build the model right?* Does the implementation
  faithfully realize the intended conceptual model, free of programming errors
  and accidental artefacts? Internal correctness; no reference to the real world
  yet.
- **Calibration** — *What parameter values make the model match observations?*
  The process of adjusting uncertain parameters so model output aligns with data.
- **Validation** — *Did I build the right model?* Does the model adequately
  represent the real system for its stated purpose, judged against data or
  patterns **not** used in calibration?

The order matters. Validating before verifying means you may be "validating"
behavior that is actually a bug or artefact. Calibrating before verifying means
you may be tuning parameters to compensate for an implementation error, which can
hide the error and produce confidently wrong results. **Verify first, then
calibrate, then validate** — and never treat calibration fit as validation
(reproducing the data you tuned to is circular).

---

## 2. Verification

Verification asks whether the code does what you think it does. Techniques:

- **Independent reimplementation / replication** — the gold standard; if a second
  implementation (ideally a different person and framework) reproduces the
  results, the original is much more trustworthy. ABM results have failed
  replication often enough that this matters.
- **Docking (model alignment).** A structured form of the above: deliberately
  reimplement the model (or align it against an existing, trusted model) and test
  whether the two produce equivalent results — "equivalent" ranging from identical
  numbers, to the same distributions, to the same qualitative relationships (Axtell
  et al. 1996, "Aligning Simulation Models"). Docking against a known model is a
  strong way to validate a new implementation and to expose hidden assumptions in
  either model.
- **Unit-test the submodels.** Each submodel from ODD element 7 should be testable
  in isolation against hand-computed cases.
- **Extreme-value / corner-case tests.** Run with parameters at limits where you
  know the answer (zero agents, no interaction, deterministic settings) and check
  the model behaves as analysis predicts.
- **Sweep the whole parameter space before fitting to data.** A model whose
  behavior over its full parameter space has *not* been studied will hide both
  bugs and incoherent results. Approaching empirical data too early can lead you
  to defend a model that doesn't yet deserve the effort (Edmonds; ten Broeke et
  al.). Theoretical exploration first is legitimate and protective.
- **Code review and visual/animation checks** — watching the model run catches a
  surprising share of logic errors.

Distinguish **errors** (the model isn't what the developer believes it is — bugs)
from **artefacts** (real phenomena in the model caused by incidental assumptions
mistakenly thought irrelevant — grid topology, update order, boundary handling).
Both produce results that look like findings but aren't. See
`limitations-and-pitfalls.md` for the full treatment.

---

## 3. Calibration

Calibration tunes uncertain parameters to reproduce observations. Guidance:

- **Calibrate as few parameters as possible.** Each free parameter is a degree of
  freedom that makes fitting easier and the result less meaningful. Fix what you
  can from independent data or theory; calibrate only the genuinely unknown.
- **Calibrate to multiple, independent targets**, not one aggregate curve (this
  is POM, §5). Fitting one time series with several free parameters is easy and
  unconvincing.
- **Expect identifiability problems.** Different parameter sets (and even
  different model structures) can fit the same data equally well — equifinality.
  Report the *set* of acceptable parameters, not a single "best" point, unless you
  can show the optimum is well-identified.
- **Verify the calibration method itself.** Especially for stochastic models,
  separate "is my calibration procedure working?" from "is my model valid?"
  Simulation-based calibration (fit the model to data it generated under known
  parameters; check you recover them) catches calibration bugs that overall
  validation would otherwise absorb.

---

## 4. Validation

Validation judges fitness for purpose against evidence held out from calibration.
Forms of validation evidence, roughly increasing in strength:

- **Face validity / plausibility** — do experts agree the structure and behavior
  are reasonable? Necessary but weak alone.
- **Qualitative pattern match** — does the model reproduce the right *kinds* of
  behavior (tipping points, oscillations, distributions' shape)?
- **Quantitative match to independent data** — out-of-sample or different-variable
  comparison. Compare *distributions* (model is stochastic) rather than single
  values; a credible/confidence band from repeated runs vs. observed data.
- **Prediction of new patterns** — the model predicts a pattern not used in its
  construction and that pattern is then confirmed. Strongest, rarest.

Always state the **domain of validity**: the parameter ranges, scales, and
conditions under which the validation holds. A validated model is validated
*there*, not everywhere.

---

## 5. Pattern-Oriented Modeling (POM)

POM (Grimm et al. 2005; Grimm & Railsback) is both a design principle and a
calibration/validation strategy, and it's the recommended default for any model
meant to represent a real system.

- Identify **multiple patterns** observed in the real system at different
  hierarchical levels, spatial scales, and temporal scales. Individually weak
  patterns are fine — their power is collective.
- **Design** the model so it can, in principle, reproduce all of them; strip out
  structure not needed to do so.
- **Filter** candidate model structures and parameter sets by how many patterns
  they reproduce simultaneously, discarding the implausible ones (also called
  inverse modeling).

The payoff: a model that hits several independent patterns at once is far less
likely to be right by coincidence, and validation happens *throughout* model
development rather than as a single end-stage test on one output. This directly
attacks the equifinality and over-fitting problems.

---

## 6. Calibration machinery

For models where you need formal parameter estimation and uncertainty
quantification:

- **Approximate Bayesian Computation (ABC).** When the likelihood is intractable
  (typical for ABMs), accept parameter draws whose simulated summary statistics
  fall close enough to observed ones. Yields an approximate posterior over
  parameters. Workhorse method for ABM calibration.
- **Full Bayesian inference** where a likelihood can be constructed; gives joint
  posteriors and honest uncertainty, but is hard for complex stochastic ABMs
  (the likelihood problem is exactly why ABC exists).
- **History matching / emulation.** Build a fast statistical surrogate (emulator,
  e.g. a Gaussian process) of the expensive ABM, then use it to rule out regions
  of parameter space that *cannot* reproduce the data (implausibility), iterating
  to a non-implausible region. Scales POM-style filtering to expensive models and
  pairs naturally with it.
- **Quantile-based / distribution-matching emulation** for stochastic ABMs, where
  the output is a distribution, not a point.

Whatever the method: account for **both** stochastic variability in the model and
parameter uncertainty when comparing to data. A band built only from repeated
runs at a fixed best-fit parameter understates uncertainty.

---

## 7. A hierarchical validation framework

A useful way to organize validation activity (e.g. the Hierarchical ABM
Validation framework; ACM TOMACS 2026, and Manson's earlier verification/
validation work) is by **level**:

- **Agent level (micro).** Validate the agents' rules and inputs in isolation —
  are the behavioral assumptions and parameters defensible *before* worrying
  about interactions?
- **Model level (meso).** Validate the calibrated interactions among agents —
  compare output distributions and aggregate variables produced by interaction.
- **Output / system level (macro).** Validate the whole system's emergent output,
  its stability, and its scaling, including how it relates to other
  systems/subsystems.

Match the validation method to the data you have and the simulation type; reviews
catalog ~17 distinct validation approaches with different data requirements.
There is no single test — assemble evidence across levels.

---

## 8. Reproducibility of the validation itself

The credibility of a validation depends on others being able to rerun it. Publish
the model code, parameter files, random seeds, the calibration/validation data
(or its provenance), and the analysis scripts. CoMSES Net / OpenABM provides a
peer-reviewed model repository and reproducibility standards for exactly this.
Treat the validation pipeline as part of the model, not an afterthought.
