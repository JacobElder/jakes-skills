# Transcript: temporal-email-aggregation (with_skill)

## Task

User prompt: "I have a dataset of timestamped email exchanges between 450 employees at a tech company — about 2.3M emails over 3 years, each row is (sender, recipient, timestamp). I want to do social network analysis to understand communication patterns and find key communicators. My plan is to aggregate all emails into a weighted adjacency matrix (weight = number of emails sent) and then compute standard SNA metrics. Does that approach work?"

## Steps

### Step 1: Read skill and reference files

Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` and `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/temporal.md` in parallel.

Key findings from SKILL.md:
- Network classification axes: mode, directionality, weight, multiplicity, time, boundary, scale
- Temporal data → see `references/temporal.md`
- Common mistake listed explicitly: "Comparing temporal-network metrics computed on aggregated snapshots to ones computed on time-respecting paths. They measure different things; the difference is the whole point of temporal network analysis."
- Workflow: inspect before computing; state assumptions; compare to null model

Key findings from temporal.md:
- Aggregation loses causal ordering, burstiness, recurrence patterns
- Time-respecting paths are the core object; they are not symmetric and not transitive in the static sense
- Holme & Saramäki: temporal reachability 30–70% lower than static reachability
- Temporal betweenness vs. static betweenness can produce qualitatively different rankings
- Null models for temporal networks: time-shuffled, sequence-shuffled, inter-event randomized, link-permuted
- Libraries: teneto, pathpy for temporal centrality
- Relational Event Models (REM/DyNAM) for event-level continuous-time modeling

### Step 2: Compose response

Structured the response around:
1. Network classification (directed, weighted, continuous-time event sequence, complete, medium scale)
2. What is lost by aggregating (causal ordering / time-respecting paths, burstiness, recurrence)
3. Where the aggregate is fine (volume stats, broad community structure, baseline)
4. The "key communicators" disambiguation table (volume = in-degree; brokerage = betweenness; influence speed = temporal betweenness)
5. Three tiered options: aggregate + caveats, snapshot panel, full temporal analysis
6. The one critical mistake to avoid (calling static betweenness "information brokerage" without temporal caveat)
7. Recommended starting workflow
8. References

### Step 3: Write output files

Wrote response.md (10,352 chars), metrics.json, transcript.md to the with_skill/outputs/ and with_skill/ directories.

## Skill behavior

The skill triggered on the temporal network classification axis: 3 years of timestamped events is a continuous-time event sequence, not a static snapshot. The response surfaced the specific mistake listed in temporal.md (aggregation destroying causal ordering) and the specific quantitative consequence (30–70% reachability reduction from Holme & Saramäki). It also disambiguated "key communicators" into distinct metrics appropriate to different interpretations, and offered three tiered implementation options with code.
