# Response Formats and Scale Construction

The response format determines what mapping the respondent must perform and what error that
mapping introduces. Choose deliberately.

## Contents
1. Open vs closed
2. Format taxonomy (which closed format)
3. Bipolar vs unipolar structure, and the branching alternative
4. Number of scale points — the 5 vs 7 vs more question
5. The midpoint (odd vs even)
6. Don't-know / no-opinion
7. Labeling: full vs endpoint vs numeric
8. How numeric scale values themselves bias answers

---

## 1. Open vs closed
Closed questions dominate because they're fast to answer and trivial to analyze. But closed
isn't always better:
- **Quantities** (counts, durations, amounts) are usually better **open and numeric**. Closed
  ranges convey normative information — a scale running "<½ hr … >2½ hr" tells respondents the
  researcher thinks ~1 hr is typical, and answers shift accordingly (Schwarz et al. 1985). Ask
  the number; bin later if needed.
- **Categorical "pick one"** items work closed only if the option list is comprehensive;
  respondents largely confine themselves to the shown options, and an omitted-but-common option
  can change even the rank order of results. If you don't yet know the real categories, pretest
  with an open version first.
- **Open follow-ups** ("Why?") add interpretive richness a closed item can't, at the cost of
  coding effort.

## 2. Format taxonomy — picking the closed format
- **Item-specific rating scale** ("How would you rate X? Very poor → Excellent"). The default
  for measuring intensity of one attitude or evaluation. Preferred over agree/disagree.
- **Agree/disagree (Likert-type) statements.** Popular and easy to mass-produce, but they
  carry acquiescence, impose more cognitive burden (you must decode the statement, then map
  agreement), and yield lower-quality data than item-specific equivalents (Saris et al. 2010;
  Revilla, Saris & Krosnick 2014). Reserve for cases where agreement is the natural response
  dimension; otherwise convert to item-specific.
- **Single-select multiple choice** for one choice among unordered categories. Exhaustive,
  mutually exclusive, order randomized.
- **Forced-choice yes/no grid** instead of **"select all that apply."** Check-all lets people
  satisfice by stopping after a few endorsements; asking yes/no for each option produces more
  endorsements and more comparable data (Smyth et al. 2006), though it costs more effort.
- **Semantic differential** — bipolar adjective pairs (good–bad, weak–strong) on a 7-point
  field; good for connotative/affective meaning.
- **Ranking** for relative priorities, but only up to ~5 objects; beyond that it's cognitively
  punishing and quality collapses. Use **MaxDiff (best–worst scaling)** for longer lists.
- **Slider / visual analog scale (VAS)** for fine-grained magnitude. Finer resolution but more
  respondent effort, more breakoffs, and known mobile/accessibility problems; the starting
  handle position anchors answers. Default to a labeled discrete scale unless you specifically
  need continuous resolution.
- **Constant-sum** when you need proportions that must total 100.

**Grids/matrices**: efficient to present but the leading cause of straightlining. Keep rows
few, keep all items in a grid genuinely parallel in scale, and on mobile prefer item-by-item.

## 3. Bipolar vs unipolar structure, and the branching alternative

Before choosing the number of points, decide whether the construct is **bipolar** or
**unipolar** — this shapes the right format, midpoint treatment, and point count.

- **Bipolar**: the construct has a meaningful opposite at each end (good–bad, favor–oppose,
  agree–disagree). The midpoint is a genuine neutral, not zero. Use **7 points** to give
  both poles room; include a midpoint. Semantic-differential and most agree/disagree items
  are bipolar.
- **Unipolar**: the construct runs from "none" to "a lot" with no meaningful negative end
  (frequency, intensity, confidence, satisfaction). Use **5 points**; the lowest anchor is
  effectively zero, not an opposite.

Misclassifying matters: treating a bipolar construct as unipolar collapses one pole, and
the midpoint's meaning changes. "How much do you support this policy?" is unipolar (no
support → strong support); "Do you favor or oppose this policy?" is bipolar (strong
opposition → strong favor). They are not equivalent re-phrasings — they measure different
distributions.

### Branching (two-step) format

For directional attitude items, a branching sequence often outperforms a single wide scale.
Instead of a 5- or 7-point scale in one step, split into two:

1. **Direction:** "Do you favor, oppose, or neither favor nor oppose [X]?" (3 options)
2. **Intensity** (shown only to those who chose favor or oppose): "Would you say you
   favor/oppose it a lot, or just a little?" (2 options)

This yields an effective 5-level scale (oppose a lot / a little / neither / favor a little /
a lot) while lowering per-question cognitive demand. Each step is simpler than navigating
a 7-point scale, which benefits lower-education and lower-motivation respondents (Krosnick
& Berent 1993). The branching format also makes the neutral group explicit — it isn't
lumped with weak-opinion respondents in a midpoint pile.

Use branching for: directional attitude items where distinguishing true neutrals from
mild leaners matters. Skip it for: evaluative ratings (quality, satisfaction), unipolar
frequency items, or when question count is tightly constrained.

## 4. Number of scale points — the 5 vs 7 vs more question
There is no universal optimum; the answer depends on the format and the population. The
defensible synthesis:

- **Reliability and validity rise as you add points, then plateau.** Below ~4 points you throw
  away real variance (coarse measurement biases estimates). Gains flatten around 5–7. Beyond
  ~7 the marginal information is small and you can no longer label points cleanly, so quality
  often *falls* (Krosnick & Presser 2010; Alwin & Krosnick 1991).
- **Default to 5 or 7** for attitude/evaluation scales. Use **7** when respondents genuinely
  make fine distinctions (bipolar attitudes, expert raters); **5** when they don't or when the
  scale must be fully labeled.
- **For agree/disagree scales specifically, use 5 — not 7 or 11.** In multitrait-multimethod
  experiments, 5-category AD scales produced higher measurement quality than 7 or 11 (Revilla,
  Saris & Krosnick 2014).
- **Moderators.** Children and low-literacy respondents do better with **4–5** points; able,
  practiced respondents tolerate more. Number of points is **confounded with labeling** — you
  can fully label 5 points easily, 7 with effort, and rarely more — so "more points" and "fewer
  labels" arrive together and shouldn't be evaluated in isolation.
- **0–10 (11-point) scales** are common for global single items (NPS, life satisfaction) where
  endpoint-anchored fine gradation is wanted and respondents are familiar with the format; this
  is a reasonable exception to the "≤7" guidance for *single* global ratings, not for multi-item
  attitude batteries.

The trade-off is fundamentally cognitive: more points = more information *if* respondents use
them, but also more mapping effort = more satisficing. Match resolution to how finely people
actually represent the construct.

> Where the choice is being justified by downstream reliability/validity *estimates* or by a
> measurement model, that estimation is a psychometrics task — recommend the design here, hand
> off the modeling.

## 5. The midpoint (odd vs even number of points)
- **Include a midpoint** when a neutral/indifferent position is psychologically real for the
  construct; omitting it forces true neutrals to mismap and adds error.
- **Omit it (even-point, forced choice)** when you deliberately want to push respondents to a
  side and neutrality is not substantively meaningful — accepting that you mislabel genuine
  neutrals.
- The midpoint attracts satisficers and people who lack an opinion but won't say so, so a fat
  midpoint can be a data-quality warning. **A midpoint is not a "don't know" option** — neutral
  ("neither agree nor disagree") and "no opinion" are different states; don't collapse them.

## 6. Don't-know / no-opinion options
Offering an explicit "Don't know" / "No opinion" feels respectful but mostly invites
satisficing: people who *could* answer take the easy exit, and data quality doesn't improve
(Krosnick & Holbrook 2002). Defaults:
- **Attitudes/opinions:** don't display a prominent no-opinion option; let it be available only
  to those who truly need it (e.g., a quietly placed option or a follow-up), not advertised.
- **Factual/knowledge items:** discourage DK and encourage a best guess — discouraging DK
  raises validity because some "don't knows" are really "don't want to work for it."
- Distinguish "no opinion" (no attitude exists) from "not applicable" (the item doesn't apply);
  the latter is legitimate and should be offered when relevant via a filter question.

## 7. Labeling: full vs endpoint vs numeric
- **Label every point with words.** Fully verbal labeling generally produces higher reliability
  and validity than labeling only the endpoints (Krosnick & Berent 1993; Menold et al. 2014;
  Krosnick & Fabrigar 1997), with the largest benefit for lower-education respondents, because
  verbal labels give every point a shared, stable meaning. (A minority of studies, e.g. Andrews
  1984, found the reverse, so this is a strong tendency, not a law — but full labeling is the
  safer default.)
- **Avoid numeric-only scales.** Bare numbers "have no inherent meaning" — respondents must
  invent a verbal equivalent for each before they can map, which adds burden and variance
  (Gummer et al. 2021). If you must use numbers (e.g., 0–10), anchor the ends verbally.
- **Choose labels that divide the continuum into roughly equal intervals** (Klockars &
  Yamagishi 1988); intensity-calibrated label sets exist. Uneven labels distort the spacing
  respondents perceive.
- Endpoint-only labeling tends to evoke more **extreme responding** (Moors et al. 2014).

## 8. How numeric scale values themselves bias answers
The numbers printed on a scale are not neutral:
- **Polarity of the number set matters.** A scale numbered −5 to +5 yields different responses
  than the same verbal scale numbered 0 to 10: the negative numbers signal the presence of an
  opposite, not merely a low amount, shifting the distribution (Schwarz et al. 1991). Numeric
  labels should *reinforce* the verbal polarity, not fight it.
- **Visual layout is interpreted.** Respondents read meaning into spacing and position — the
  visual midpoint reads as "typical," top/left reads as "first/most" (Tourangeau, Couper &
  Conrad 2004). Keep spacing visually equal and order consistent with the intended scale
  direction.
