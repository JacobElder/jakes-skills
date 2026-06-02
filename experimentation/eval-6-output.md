# Running the "what your friends are watching" test

Your teammate is right to stop you, and here's the precise reason: **the naive
50/50 user-level test would give you a biased answer, not just a noisy one.**

**The problem is interference (a SUTVA violation).** Standard A/B analysis
assumes one user's treatment doesn't affect another user's outcome. This feature
breaks that assumption by design — it operates *over the social graph*. If I'm
in treatment and the feature gets me watching (and posting/reacting) more, my
friends in the control group now see more activity from me, which changes *their*
watch time too. Your control group is partly "treated" through the network. That
contaminates the comparison and typically **dilutes the measured effect** (the
control is pulled toward treatment), so the user-level estimate understates the
true full-launch impact — and no amount of extra sample fixes a bias.

**Design that actually works: randomize at a level that contains the
spillover.**
- **Cluster-randomize by social community.** Partition users into clusters that
  capture most friend relationships (community detection on the graph,
  or a coarser proxy), and assign whole clusters to treatment or control. Now
  most of a treated user's friends are also treated, so spillover stays inside
  the treatment arm where it belongs.
- **Ego-network / graph-cluster randomization** is the more sophisticated
  version if you have the infrastructure; **geo-based** assignment is a blunter
  fallback if social ties are regionally concentrated.

**The cost is real — budget for it.** Clustered designs are far less powerful
than user-level ones. Outcomes within a cluster are correlated (intracluster
correlation), so your *effective* sample is much smaller than the user count —
the design effect can inflate the required sample several-fold, and **the number
of clusters matters more for power than users-per-cluster**. So: prefer many
smaller clusters, and run a power calculation that applies the design effect
(the `--icc` / `--cluster-size` options in the power script) rather than the raw
user count. Expect to need more users and/or a longer run than the naive plan
implied.

**Net:** don't run the 50/50 user-level test as planned — it answers the wrong
question. Switch to cluster randomization over social clusters, size it with the
design effect, and you'll get an estimate that actually reflects what shipping to
everyone would do.
