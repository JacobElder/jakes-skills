# Response: Social Network Analysis of Email Communication Data

Your approach — aggregate all emails into a weighted adjacency matrix and compute standard SNA metrics — is a reasonable starting point, and it will produce meaningful results. But for a 3-year dataset of 2.3M emails, that aggregation step throws away a lot of signal that probably matters for your actual questions about communication patterns and key communicators. Here's what works, what doesn't, and what you should add.

---

## What works fine

**Weighted adjacency matrix + standard metrics** is well-established for organizational network analysis. Once you have the matrix, computing degree centrality (total email volume per person), betweenness centrality (who sits on the shortest paths between others), eigenvector or PageRank centrality (who is connected to other well-connected people), and clustering coefficients is all standard and interpretable. For 450 nodes this is computationally trivial — even betweenness, which is O(VE) on unweighted graphs, will run in seconds.

You should treat this as a directed graph, not undirected. Sending and receiving emails are different behaviors. An employee who sends many emails to everyone versus one who receives many but replies rarely are playing different organizational roles. Use separate in-degree and out-degree weighted centrality measures.

**Community detection** on the aggregated graph is also likely to be informative. Algorithms like Louvain or Leiden will find clusters of employees who email each other more than they email outside the cluster — these often map onto teams, projects, or informal coalitions. This is valuable organizational insight.

---

## The main problem: temporal aggregation loses critical information

Collapsing 3 years into a single matrix treats an email sent on day 1 the same as one sent on day 1095. For communication patterns and key communicators, this matters a lot:

**Temporal dynamics of influence.** Someone who was central in year 1 but left or changed roles may look like a top communicator in the aggregated view even if they're irrelevant now. Conversely, someone who rose to prominence in year 3 will appear less central than their current actual influence. If you care about who the key communicators *are* (present tense), you need to weight recent activity more heavily or analyze time windows separately.

**Bursty vs. sustained communication.** Email volume is bursty. A project team might exchange 500 emails in a week during a crunch, then very few for two months. The aggregated weight of 500 looks impressive but doesn't distinguish "this pair has a strong ongoing relationship" from "this pair had one intense but temporary collaboration." These have very different interpretations for organizational network analysis.

**Relationship formation and dissolution.** Organizations change over 3 years. New employees join, others leave, teams restructure. A static aggregated graph cannot show you how the network evolved — who became more or less central, whether the organization became more siloed or integrated over time, which communities formed or disbanded.

**Practical fixes:**
- Analyze multiple time windows (e.g., quarterly snapshots, or a rolling 90-day window) and compare centrality rankings across windows. This lets you identify consistently central people versus temporarily prominent ones.
- Consider decay-weighted aggregation: weight each email by a recency factor (e.g., exponential decay) so recent emails count more toward the current graph.
- Use temporal network analysis methods if you want to study dynamic reachability and temporal paths — though this adds complexity.

---

## Other issues with the aggregation approach

**Directionality of weight.** You're defining weight as number of emails sent from sender to recipient. This is fine, but consider whether reply chains matter. If Alice sends 50 emails to Bob and Bob replies to all of them, that's a reciprocal relationship with weight 50 in each direction. If Alice sends 50 emails to Bob and Bob never replies, that's a different relationship but might have the same weight in your matrix. You may want to compute a reciprocity ratio alongside raw weight.

**Email volume as a proxy for relationship strength.** High email volume between two people can mean strong collaboration, but it can also mean one person is flooding another with requests, or that they're on the same mailing list threads. You may want to filter out emails with more than ~10 recipients, which are likely announcements rather than direct communication. Mass emails inflate edge weights without reflecting genuine dyadic relationships.

**Self-loops and distribution lists.** Make sure you handle cases where sender == recipient (automated systems), and think about how to treat emails sent to distribution lists if those appear as single recipients in your data.

---

## Recommended approach

1. Build the full aggregated weighted directed graph as planned — this gives you a useful baseline.
2. Also build quarterly or 6-month snapshot graphs and compute centrality for each. Compare rankings.
3. Filter out high-fan-out emails (e.g., emails sent to >10 recipients) for the relationship-strength analysis; keep them if you want to study broadcast patterns.
4. For key communicators, look at several centrality measures together: out-degree (who initiates communication broadly), betweenness (who bridges groups), and PageRank (who is in the core of the network). These identify different types of key communicators — broadcasters, brokers, and cores — which often correspond to different organizational roles.
5. Run community detection on the aggregated graph to get team/cluster structure, then check whether those communities are stable across your time windows.

The aggregated approach will give you solid, defensible results for a first analysis. The temporal extensions are worth adding if you want to make claims about current state or organizational change over time.
