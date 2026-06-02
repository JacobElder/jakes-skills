# Designing the 3-layout navigation study with ~30 participants

With 30 people and three conditions, a between-subjects design (10 per layout)
would be hopeless — individual differences in speed and error-proneness are huge
relative to any layout effect, and 10 per cell can't see past that noise.

**Use a within-subjects (repeated-measures) design: every participant tries all
three layouts.** This is what makes n=30 workable. Each person serves as their
own control, so the large person-to-person variability (some users are just
faster) is removed from the comparison instead of swamping it — you're measuring
*within-person* differences between layouts, which is a far more sensitive test
for the same number of people.

**Counterbalance the order.** The catch with within-subjects is order and
carryover effects: whichever layout comes first benefits (or suffers) from
unfamiliarity, and practice accumulates across tasks. Rotate the order so it's
balanced across participants — a Latin square for three conditions (e.g. ABC,
BCA, CAB assigned in rotation) ensures each layout appears in each position
equally, so order can't masquerade as a layout effect. Use fresh, comparable
tasks per layout so people aren't just repeating the identical task.

**Analyze respecting the repeated measures.** Each participant contributes three
observations that are correlated, so don't treat them as independent. Use a
repeated-measures approach — repeated-measures ANOVA, or better a mixed-effects
model with a random intercept per participant (and a random effect for task if
tasks vary). Treating the trials as independent would fake your effective sample
size and produce false positives.

**Both outcomes:**
- *Task-completion time* — continuous; mixed model on (log-)time works well and
  log helps with the right-skew typical of timing data.
- *Error rate* — counts/proportions per participant×layout; a logistic or
  Poisson mixed model rather than a plain t-test.

**Be honest about power.** Within-subjects buys a lot, but 30 participants still
only reliably detects *sizable* within-person differences. If two layouts differ
only slightly, this study likely won't distinguish them — treat a null as
"didn't detect a large difference," not "the layouts are equivalent." Pair the
quant with observation/think-aloud notes to catch usability problems that a
30-person test won't certify statistically.
