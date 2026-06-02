# Estimating the effect of the California fee cap

Yes — you can't randomize which states got the law, but this is a textbook
quasi-experiment, and the panel structure (all 50 states, monthly, 3 years) is
exactly what the main method needs.

**Primary method: difference-in-differences (DiD).** California is the treated
unit; other states are the comparison. Compare California's before→after-Jan-1
change to the same change in the comparison states. Differencing nets out two
things at once: stable level differences between California and elsewhere, and
any nationwide time trend that hit everyone. What's left is attributed to the
cap.

**The assumption it rests on — parallel trends.** DiD is only valid if, absent
the law, California's outcome would have moved parallel to the comparison
states'. You can't prove this, but you support it by plotting the pre-period
(pre-Jan-1) trajectories and showing California and the comparison group tracked
together for the prior months/years. Divergent pre-trends would invalidate the
estimate. State this assumption as the headline caveat — it's the thing
randomization would have guaranteed and now you're buying on credit.

**Alternative worth running: synthetic control.** With a single treated unit
(one state), synthetic control is purpose-built: it constructs a weighted blend
of other states that reproduces California's *pre-Jan-1* trajectory, then reads
the gap after January. It often fits the pre-period better than an unweighted
comparison group, and inference comes from placebo permutations across the donor
states. Strong complement to DiD — if both agree, you're on firmer ground.

**Threats to name:**
- A **concurrent California-only shock** around Jan 1 (another state policy, a
  large CA-specific market event) would be confounded with the cap.
- **Anticipation** — if firms or consumers reacted before Jan 1, the "pre"
  period is contaminated; check for pre-trends right at the boundary.
- **Other states changing too** — make sure comparison states didn't pass
  similar caps in the window.

**Falsification check:** run the same DiD on a placebo date (a year before the
law) or a placebo outcome that the cap shouldn't affect — it should show no
effect. If it shows an "effect," your design is picking up something other than
the law.

Bottom line: a defensible causal estimate is reachable, but the conclusion rests
on the parallel-trends (or good-synthetic-match) assumption rather than on
randomization, so report it with that assumption stated plainly.
