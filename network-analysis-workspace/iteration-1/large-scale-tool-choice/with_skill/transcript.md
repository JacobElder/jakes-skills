# Transcript: large-scale-tool-choice (with_skill)

## Task

User prompt: "We're building a recommendation system and want to model our user-item interaction graph. It has about 5 million users, 2 million items, and 800 million interactions. I want to compute betweenness centrality and run community detection on this thing. Was planning to use NetworkX. Will that work?"

## Steps

### Step 1: Read SKILL.md

Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` in full.

Key guidance applied:
- Scale classification: 7M nodes and 800M edges → "massive" (>10⁶). Skill states: "Scale changes which library is viable (NetworkX → igraph → graph-tool → NetworKit/cuGraph)."
- Skill explicitly says NetworkX is inappropriate above ~50k nodes.
- Bipartite structure flagged as requiring special handling before community detection.
- Betweenness flagged as requiring approximation at scale.
- Resolution limit of modularity flagged as a pitfall.
- Backbone extraction required before projection-based analysis.

### Step 2: Read references/tools.md

Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/tools.md` in full.

Key guidance applied:
- Decision matrix: 500k–10M nodes → graph-tool, NetworKit. >10M → graph-tool, NetworKit, cuGraph or distributed.
- NetworkX explicitly called out as a wrong-tool mistake: "Using NetworkX for a million-node graph and concluding 'this is too slow for our problem': it's not the problem, it's the tool."
- NetworKit `ApproxBetweenness` identified as correct tool for approximate betweenness at scale.
- cuGraph identified for GPU acceleration.
- leidenalg identified as the correct Leiden implementation.
- graph-tool identified as the best SBM tool.

### Step 3: Compose response

Structured around:
1. Direct answer to the NetworkX question (no)
2. Network classification (bipartite, massive scale)
3. Betweenness centrality: tractability analysis + approximation options
4. Community detection: bipartite handling + backbone extraction requirement + tool recommendations
5. Tool summary table
6. Infrastructure considerations
7. Concrete next steps

### Step 4: Write outputs

- Wrote response.md (8,678 chars)
- Wrote metrics.json
- Wrote transcript.md (this file)

## Tool calls

| Tool | Count |
|---|---|
| Read | 2 |
| Write | 3 |
| Bash | 3 |
| **Total** | **8** |

## Key decisions made by skill

1. **NetworkX rejection**: Explicit, with reference to the tools.md decision matrix
2. **Bipartite flag**: Identified that the user-item graph is bipartite and that standard community detection would produce meaningless mixed-type communities
3. **Backbone extraction requirement**: Surfaced before the user ran projection + community detection without it (a common mistake the skill explicitly lists)
4. **Betweenness tractability analysis**: Computed O(nm) complexity to show exact betweenness is infeasible at this scale
5. **CPM over modularity**: Recommended to avoid resolution limit on a graph of this size
6. **Leiden over Louvain**: Recommended because Louvain can produce disconnected communities
