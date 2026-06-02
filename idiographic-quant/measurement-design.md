# Measurement and protocol design (read this BEFORE collecting data)

The hardest-to-fix mistakes in idiographic work happen before any model is fit. A bad
ESM protocol produces data that no method can rescue, and you only find out weeks later.
If the user is still planning data collection, this is the highest-leverage thing to get
right. If the data already exist, read this to diagnose what you're stuck with.

## Contents
1. Sampling scheme
2. How many beeps, how long
3. Item selection: common vs personalized
4. Compliance and missingness
5. Reactivity
6. The design ↔ analysis contract

---

## 1. Sampling scheme

Match the scheme to the process, not to convenience.

- **Interval-contingent** (fixed times, e.g., every 3 h): simplest, gives near-regular
  spacing that discrete-time models like, but misses fast events and invites anticipation.
- **Signal-contingent** (semi-random prompts within blocks): the ESM default; captures
  momentary states without anticipation, but produces **unequally spaced** data — plan to
  handle that (continuous-time models or DSEM `TINTERVAL`; see the time-series reference).
- **Event-contingent** (log when X happens): essential for rare/punctuated events
  (panic, conflict, smoking), but timing is endogenous to the process, which complicates
  lagged modeling.

You can combine them (e.g., signal-contingent mood + event-contingent lapses). Decide and
document, because the scheme determines what lag structure is even estimable.

## 2. How many beeps, how long

Two separate quantities, both binding:

- **Beeps per day × days = total T**, which must support the model (see data-density floors
  in the main skill). Person-specific dynamics need *occasions*, not participants.
- **Beeps per day** must out-resolve the process. A dynamic that turns over in an hour is
  invisible at 4 beeps/day; an effect that unfolds over weeks won't show in lag-1 at
  hourly spacing. The sampling rate *defines* which lagged effects exist.

Don't fix T from a rule of thumb when planning — **simulate**: generate data from a
plausible model at candidate (beeps/day, days) combinations and check parameter recovery.
Then budget for attrition (below), because effective T is always less than scheduled T.

## 3. Item selection: common vs personalized — a genuinely idiographic decision

This is where idiographic measurement diverges from nomothetic and people don't realize
they're making a choice:

- **Common (nomothetic) items** — everyone answers the same validated items. Pro:
  comparable across people, supports pooled methods (mlVAR/GIMME/DSEM) and between-person
  questions. Con: the items may not be the *right* variables for a given person; a
  standardized scale can have near-zero within-person variance for someone (a floor/ceiling
  problem that kills their correlations).
- **Personalized (idiographic) items** — items tailored to the individual's own
  complaints/goals (often co-constructed clinically). Pro: maximal personal relevance and
  within-person variance, which is exactly what you need. Con: not comparable across people,
  so you lose pooling and group inference; validity rests on the elicitation, not a
  validated scale.
- **Hybrid** — a common core plus a few personalized items. Often the sane compromise:
  keeps some comparability while capturing what matters to the person.

There is no free lunch. If the deliverable is "understand and treat *this* person,"
personalized items win. If you need to pool across people or compare, you need a common
core. Decide based on the question, and state the tradeoff you accepted.

Practical item cautions: keep the battery short (respondent burden compounds over dozens of
prompts and tanks compliance); check that each item has enough *within-person* variance to
correlate (a symptom that's always "1" carries no idiographic information); and pilot the
wording for momentary phrasing ("right now," not "in general").

## 4. Compliance and missingness

Compliance erodes T and is rarely missing-completely-at-random — people skip beeps when
busy, distressed, or asleep, so missingness correlates with the states you care about.

- Plan for it: schedule more beeps than your minimum T requires; use reminders; keep the
  battery short; consider modest incentives tied to completion.
- Report it honestly: overall compliance %, *and* its pattern over time and across people,
  and whether it relates to the outcomes. A 60%-compliant series with distress-linked gaps
  is a different object than a 95%-compliant one.
- Don't naively impute across long gaps or overnight; respect day boundaries so you don't
  manufacture "bedtime predicts morning" lagged artifacts.

## 5. Reactivity

Repeatedly measuring a process can change it (self-monitoring is itself a mild
intervention — e.g., tracking mood or craving can shift them). Evidence suggests reactivity
is often small but it is not zero and it can matter for the very clinical processes
idiographic studies target. Mitigations: avoid leading items, don't over-prompt, and where
feasible check for drift early in the series that looks like adaptation to monitoring rather
than the substantive process. At minimum, acknowledge it as a limitation.

## 6. The design ↔ analysis contract

Design choices silently commit you to analysis choices. Make the links explicit up front:

- Signal-contingent sampling → unequal spacing → continuous-time or `TINTERVAL` later.
- Personalized items → no pooling → per-person or replication-across-persons, not mlVAR/DSEM.
- Few beeps/day → only slow dynamics estimable → don't promise momentary mechanism.
- Short battery to protect compliance → few nodes → keep the network small (which you wanted
  anyway for power).

Decide the analysis when you decide the design. Choosing the model after seeing the data is
how researcher degrees of freedom creep in — pre-register the sampling scheme, T target,
item set, and intended model.
