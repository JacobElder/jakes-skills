# Transcript: Large-Scale Graph Tool Choice (Without Skill)

## Task

User prompt: "We're building a recommendation system and want to model our user-item interaction graph. It has about 5 million users, 2 million items, and 800 million interactions. I want to compute betweenness centrality and run community detection on this thing. Was planning to use NetworkX. Will that work?"

Condition: No skill loaded. Standard model response.

---

## Agent Response

The agent answered directly from general knowledge without reading any skill or reference files.

**Key claims made:**

1. NetworkX will fail at this scale due to in-memory Python dict overhead (~320–400 GB for edges alone).
2. Exact betweenness centrality via Brandes is O(V*E) and infeasible at 7M nodes × 800M edges even with fast tools; approximate k-pivot sampling should be used instead (k=1,000–10,000).
3. Recommended tools by context:
   - GPU: RAPIDS cuGraph (approximate BC + Louvain)
   - CPU single-machine: graph-tool or igraph + leidenalg
   - Distributed: GraphX / GraphFrames
   - Rec-system end goal: PyG / DGL / GNN embeddings (LightGCN, PinSage)
4. Advised questioning whether global betweenness centrality is the right signal for a rec system at all — community membership and GNN embeddings often better serve the underlying recommendation objective.

**Code snippet provided:** cuGraph example for approximate BC and Louvain.

---

## Tool Calls

| Step | Tool | Purpose |
|---|---|---|
| 1 | Bash | Check if output directory exists |
| 2 | Bash | List outputs directory contents |
| 3 | Read | Read existing response.md |
| 4 | Read | Read existing metrics.json |
| 5 | Write | Overwrite response.md with current response |
| 6 | Bash | Get output character count |
| 7 | Write | Overwrite metrics.json |
| 8 | Bash | Check for transcript file |
| 9 | Write | Write transcript.md |

---

## Notes

- No skill was loaded; response reflects base model knowledge only.
- No skill files, reference files, or domain-specific documentation were read.
- Response length: ~5,680 characters.
