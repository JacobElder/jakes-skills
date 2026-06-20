# Handoff Notes

This file is referenced by several documents in `reference/` and `evals/` as a placeholder
for known gaps and future tasks. Items flagged here are not blocking for the current release
but should be addressed before a subsequent milestone.

## Known gaps

- **Ordinal / polytomous IRT:** The joint model currently binarizes polytomous scores.
  Graded-response or partial-credit extensions are scoped for a future iteration.
- **Cross-backend agreement check:** A formal test comparing Stan (CmdStanPy / cmdstanr)
  and PyMC posteriors to within acceptable Monte Carlo error is planned but not yet
  implemented. This is the "protect-the-claims" gate referenced in `evals/run_evals.md`.
- **Item drift / temporal DIF:** Detecting drift across time windows in the joint model
  is a future extension noted in `reference/13_item_drift.md`.
- **Validation before ship decision:** The Stan backend (`stan/`) should pass a held-out
  benchmark comparison before its numbers are used for a release decision
  (`reference/09_joint_glmm.md`).
