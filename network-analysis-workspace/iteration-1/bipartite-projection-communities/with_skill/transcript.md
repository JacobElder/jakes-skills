# Transcript: Bipartite Projection + Communities (With Skill)

## Task
Respond to user question about projecting a bipartite employee×project network to person-person and running Louvain community detection to find employee communities.

## Steps

### Step 1: Read SKILL.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` in full.

Key guidance identified:
- Bipartite network → projection without backbone extraction is listed as a primary "common mistake to watch for and call out" (line 104–105)
- "The projection inherits a huge clique structure from each event/group node and inflates clustering, modularity, and centrality measures."
- Task maps to "communities" archetype → read `references/communities.md`
- Skill also references `references/data_decisions.md` for projection decisions

### Step 2: Read references/communities.md
Read in full. Key guidance:
- Louvain disconnects communities (Traag, Waltman, van Eck 2019) → use Leiden instead
- Modularity degeneracy: single Louvain run is unreliable; run many times, report ARI stability
- Resolution limit: modularity cannot detect communities smaller than √(2m)
- "Using modularity on a bipartite projection" listed explicitly as a common mistake
- Bipartite-specific options: bipartite modularity (Barber 2007), bipartite SBM (graph-tool)
- Default recommendations table: Leiden for quick/defensible; nested SBM for principled K selection

### Step 3: Read references/data_decisions.md
Read in full. Key guidance:
- Bipartite trap: projection of size-d event creates d(d-1)/2 cliques; large events dominate
- Backbone extraction is required before any SNA on projections
- SDSM (Neal 2014) is the recommended null for bipartite projections: preserves expected row/column sums, gives per-edge p-values
- FDSM is stronger but slower
- Disparity filter does NOT use bipartite structure → inferior for this use case
- R backbone package; Python requires custom implementation or cdlib
- Alternative: analyze bipartite network directly (bipartite centrality, bipartite SBM)

### Step 4: Write response
Composed full response addressing:
1. Problem 1: Projection without backbone extraction (SDSM fix, code example, alternative of bipartite SBM)
2. Problem 2: Louvain → Leiden upgrade + stability reporting via ARI across 100 seeds
3. Principled alternative: nested SBM in graph-tool
4. Concrete recommended workflow for their specific setup (800 nodes, 150 projects)
5. Summary table of changes
6. Key references

Response saved to: `outputs/response.md` (9,539 characters)

## Files read
- `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md`
- `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/communities.md`
- `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/data_decisions.md`

## Files written
- `outputs/response.md`
- `outputs/metrics.json`
- `transcript.md` (this file)
