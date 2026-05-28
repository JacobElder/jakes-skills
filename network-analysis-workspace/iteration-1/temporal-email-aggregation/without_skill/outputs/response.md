# Response: Aggregated Email Network Analysis

## Question

I have a dataset of timestamped email exchanges between 450 employees at a tech company — about 2.3M emails over 3 years, each row is (sender, recipient, timestamp). I want to do social network analysis to understand communication patterns and find key communicators. My plan is to aggregate all emails into a weighted adjacency matrix (weight = number of emails sent) and then compute standard SNA metrics. Does that approach work?

## Answer

The approach of aggregating all emails into a weighted adjacency matrix and computing standard SNA metrics is reasonable as a starting point, but has several important limitations worth addressing.

### What works well

- A weighted directed graph (sender → recipient, weight = email count) correctly captures volume of communication
- Standard centrality metrics (degree, betweenness, closeness, eigenvector/PageRank) will identify key communicators in different senses — high in-degree nodes receive many emails, high betweenness nodes broker communication across groups
- Community detection on this graph will surface team/department structure

### Where the approach falls short

**1. Temporal flattening loses critical signal.** Three years of data collapsed into one matrix hides whether relationships are stable, seasonal, project-driven, or evolving. An employee who was central 3 years ago but left 2 years ago looks identical to one who is currently central. For communication pattern analysis, temporal dynamics often ARE the finding.

**2. Directed vs. undirected.** Email is directed. A→B 100 times and B→A 0 times is a very different relationship than mutual 50/50 exchange. Many SNA metrics assume undirected graphs; make sure you use directed versions or explicitly symmetrize with justification.

**3. Raw email count is a crude weight.** Reply chains inflate volume between certain pairs. One broadcast email to 100 recipients counts as 100 edges. Consider normalizing by reply-chain membership, or filtering to distinguish broadcast vs. conversational messages.

**4. Bursty communication vs. sustained relationships.** A project team that emails intensely for 6 weeks and then never again looks similar to a pair who email weekly for 3 years. Burstiness matters for understanding "key communicators."

**5. Self-loops and group emails.** Mailing lists, calendar invites, and automated system emails will pollute the graph unless filtered.

### Recommended additions

- **Temporal slicing:** Compute metrics in rolling windows (e.g., monthly or quarterly) and look at how centrality rankings change over time. This reveals emerging leaders, departing hubs, and structural shifts.
- **Reciprocity analysis:** Compute reciprocity ratios (B replies / A initiates) to distinguish one-way broadcasts from genuine dialogue.
- **Community detection:** Louvain or InfoMap on the weighted directed graph will often recover org-chart structure, and deviations from it (cross-team brokers) are often the most interesting finding.
- **Ego network analysis:** For the "key communicators" question, look at the ego networks of high-betweenness nodes — are they bridges between otherwise disconnected groups?
- **Filter noise first:** Remove automated senders, mailing lists, and self-emails before analysis.

### Bottom line

Yes, the aggregated weighted adjacency matrix + standard metrics approach works and will produce meaningful results. But treating the temporal dimension as a first-class feature rather than collapsing it will significantly strengthen the analysis — this is where the most interesting patterns often live in longitudinal organizational communication data.
