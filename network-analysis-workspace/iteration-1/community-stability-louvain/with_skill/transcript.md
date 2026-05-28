# Transcript: community-stability-louvain (with_skill)

## Task

User prompt: "I ran Louvain community detection on my co-authorship network (1200 authors, 4800 edges) and got 8 communities. The modularity is 0.67 which seems great. How do I report these communities in my paper? I want to name them and describe what each one represents."

## Steps

### Step 1: Read SKILL.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` in full. Key takeaways relevant to this task:
- Community detection section explicitly states: "Treating Louvain's single output as 'the' communities" is a listed common mistake — run many times, report stability.
- Louvain can produce disconnected communities; Leiden was invented to fix this.
- Modularity overfits random graphs; compare Q against a configuration-model null.
- Resolution limit: cannot detect communities smaller than sqrt(2m).
- For community partitions, report stability (NMI/ARI across runs), not just the partition.
- Distinguish description from inference: "This network has high modularity" is description; "These communities reflect real social groups" is inference needing justification.

### Step 2: Read references/communities.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/communities.md` in full. Key takeaways:
- Modularity degeneracy (Good et al. 2010): exponentially many near-optimal partitions; single run is unreliable.
- Louvain disconnects communities (Traag et al. 2019): use Leiden instead.
- Null comparison required before claiming communities are real.
- Resolution limit: sqrt(2 * 4800) ≈ 98 internal edges minimum detectable community size.
- Partition comparison metrics: ARI (adjusted Rand index), NMI, Variation of Information.
- SBM as gold-standard alternative: degree-corrected SBM, graph-tool.
- Reporting standard: "mean ARI across 100 Louvain runs = 0.72" or "dominant partition appears in 84/100 runs."

### Step 3: Check directory structure
Verified that `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis-workspace/iteration-1/community-stability-louvain/with_skill/outputs/` exists and is empty.

### Step 4: Compose and write response.md
Composed a comprehensive methodological response covering:
1. The single-Louvain-run problem and how to fix it (100 runs, ARI, switch to Leiden)
2. Why Leiden is preferred over Louvain (connected communities guarantee)
3. Configuration-model null comparison for Q validation
4. Resolution limit check (sqrt(2m) ≈ 98 internal edges for this network)
5. Structural descriptors to compute per community
6. How to use metadata (institution, journal, subfield) to assign substantive names
7. A methods-section reporting template
8. SBM validation as supplementary check
9. Canonical references

### Step 5: Write metrics.json and transcript.md
Recorded tool call counts and output size.

## Key methodological decisions flagged to user

1. **Single Louvain run is insufficient** — must run 100+ times and report mean ARI.
2. **Switch to Leiden** — Louvain can produce disconnected communities; Leiden guarantees connectedness.
3. **Q = 0.67 needs null comparison** — compare against 1,000 configuration-model nulls with same degree sequence.
4. **Resolution limit** — with 4,800 edges, communities must have > sqrt(9,600) ≈ 98 internal edges to be reliably detected.
5. **Names must come from metadata** — substantive labels (institution, subfield, journal) not structural labels.

## Output file
`/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis-workspace/iteration-1/community-stability-louvain/with_skill/outputs/response.md`
Length: 12,824 characters
