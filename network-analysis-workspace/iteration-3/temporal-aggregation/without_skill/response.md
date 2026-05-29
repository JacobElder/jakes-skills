# Social Network Analysis of Email Data: Does a Static Weighted Adjacency Matrix Work?

Your plan is a reasonable starting point, but it has several important limitations you should understand before committing to it — and some are significant enough that they could lead you to incorrect conclusions about "key communicators."

## What works about your approach

Aggregating into a weighted adjacency matrix and computing standard SNA metrics (degree centrality, betweenness, closeness, PageRank, etc.) is well-established and will produce interpretable results. The directed weighted graph you're describing (sender → recipient, weight = email count) is appropriate for this data structure. NetworkX, igraph, and similar libraries handle this natively.

## What the static aggregation misses

**Temporal dynamics are discarded.** Collapsing 3 years into a single matrix loses all information about when communication happened. A person who was a central hub in year 1 but left the company in year 2 will look nearly as important as someone central throughout all 3 years. More subtly, communication patterns often shift — team restructuring, project cycles, and organizational changes will all be invisible in the aggregate.

**Burstiness and recency are conflated with sustained influence.** Someone who sent 500 emails in one intense two-week project sprint looks identical to someone who sent 500 emails at a steady rate of one per day. These are behaviorally and organizationally very different patterns, but your weight variable treats them the same.

**Directionality asymmetries may matter.** A weight of 100 on edge A→B tells you A sent B 100 emails, but nothing about whether B responded. A "key communicator" who broadcasts to everyone but receives no replies is a very different node than one with high two-way reciprocal communication. You may want to compute reciprocity or consider in-degree vs. out-degree separately.

**Edge weight = email count conflates volume with influence.** High email volume can reflect organizational necessity (e.g., a helpdesk role), automated sends, or CC/BCC behavior rather than genuine social influence. If your data includes CC'd recipients, those edges carry very different meaning than direct sends.

## Specific issues with "key communicators"

If your goal is to find influential connectors, betweenness centrality on the aggregate graph is the standard choice, but be aware:

- **Betweenness centrality is computationally expensive** on a 450-node graph it's fast, but be aware that it assumes information flows along shortest paths, which is not a safe assumption for email.
- **High degree does not equal influence.** The CEO or an email distribution list might have the highest degree centrality but not be the most meaningful connector. Consider filtering automated senders and mailing lists before analysis.
- **Weighted vs. unweighted results can diverge substantially.** Run both and compare — if the top-10 lists are very different, investigate why.

## What you should consider adding

1. **Temporal windowing.** Slice the 3 years into monthly or quarterly windows and compute centrality separately for each window. This lets you track how key communicators change over time and detect events (e.g., when someone becomes a central node after a promotion).

2. **Community detection.** Algorithms like Louvain or Leiden on your weighted graph will identify communication clusters that likely correspond to teams or informal groups. This is often more actionable than raw centrality.

3. **Temporal network analysis.** Libraries like `teneto` (Python) support temporal network metrics — temporal degree, temporal betweenness, and burstiness — that operate directly on timestamped edge lists without collapsing time.

4. **Response-pair analysis.** Before aggregating, identify reply chains (email thread reconstruction) to distinguish broadcast communication from reciprocal dialogue. This requires threading logic but substantially improves validity.

5. **Null model comparison.** Your centrality scores are hard to interpret in isolation. Consider comparing against a configuration model null (random graph with the same degree sequence) to determine which structural features are statistically meaningful.

## Practical recommendation

Your static weighted adjacency matrix approach will work as an initial exploratory analysis and will surface gross structural patterns. But treat it as a first pass rather than a final answer. The most common mistake in organizational network analysis from email data is over-interpreting aggregate metrics without accounting for temporal dynamics — a significant structural change mid-way through your 3-year window could substantially distort your conclusions about who the key communicators are.

Run the aggregate analysis first to get a baseline. Then immediately segment by year to check whether your top-10 centrality nodes are stable or not. If they shift substantially, invest in proper temporal network analysis before drawing conclusions.
