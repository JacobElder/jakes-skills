# Sanity-check: "we shipped to 100% and active minutes are up 8%"

Your instinct is right. The claim has one load-bearing flaw, and it's fatal:

**There's no control group, so there's no counterfactual.** Shipping to 100%
means every user is in "treatment." The 8% is a *before-after* comparison, which
silently assumes that without the redesign last week would have looked exactly
like the week before. That assumption is almost never true.

A week-over-week change absorbs everything else that differs between those two
weeks: day-of-week and seasonal patterns, a marketing push or press hit, a
pricing or algorithm change that shipped around the same time, even weather or a
holiday. Any of those could produce an 8% swing on its own. The redesign might
be responsible for all of it, none of it, or it might be *masking* a decline —
the data as described can't distinguish these.

So "we did X and the metric went up" is evidence the metric went up, not
evidence X caused it. I wouldn't green-light "more like this" on this basis.

**What would actually support the claim**, given it's already fully shipped:
- **Holdback / holdout** — carve out a small randomized group kept on the old
  feed for a few weeks. This is the cleanest fix and also reads the durable
  effect after any novelty fades. Easiest to set up going forward.
- **Difference-in-differences** — if a comparable segment or market didn't get
  the redesign at the same time, compare each group's before→after change
  (rests on the two having parallel trends pre-launch).
- **Interrupted time series** — model the active-minutes trend for many weeks
  before the launch and test for a real break at the launch date, ideally
  against a control series that didn't change.

If none of those is available, the honest statement to leadership is "active
minutes rose 8% after launch; we can't yet attribute that to the redesign," plus
a proposal to run a holdback so the *next* one has a real read.
