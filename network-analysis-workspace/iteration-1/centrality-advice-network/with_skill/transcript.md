# Transcript: centrality-advice-network (with_skill)

## Setup

- Read SKILL.md at `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md`
- Read `references/centrality.md` at `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/centrality.md`
- Checked output directory structure under `iteration-1/centrality-advice-network/with_skill/`
- Read `eval_metadata.json` to confirm assertions

## Skill guidance applied

From SKILL.md:
- Identified task archetype: "Who is the most important/influential/central?" → Node-level structural position → `references/centrality.md`
- Classified network along mandatory axes before any analysis: one-mode, directed (advice-seeking is asymmetric), binary weight, single-relation, cross-sectional, complete (200 employees), small scale
- Applied core principle: "Centrality is plural; pick the right one" — the skill explicitly forbids recommending a single centrality without process-based justification
- Applied workflow step 1: recommend inspecting before computing (n, m, density, components, reciprocity, degree distribution)
- Applied workflow step 2: state assumptions explicitly (directionality, harmonic handling for disconnected components)

From references/centrality.md:
- Used Borgatti (2005) flow-type × path-type typology to match centrality to substantive process
- Flagged eigenvector centrality failure on directed graphs without strong components → recommended PageRank and Katz as alternatives
- Included Burt's constraint / effective size for structural hole brokerage (organizational network analysis use case explicitly cited in reference)
- Applied harmonic centrality as the correct fix for closeness on disconnected/directed graphs
- Referenced measurement-error sensitivity (Borgatti, Carley, Krackhardt 2006) per the reference's robustness section

## Key decisions made in the response

1. **Directed network classification**: flagged in-degree vs. out-degree distinction; noted asymmetry of advice-seeking
2. **Eigenvector exclusion**: explicitly stated why eigenvector centrality fails here (no guaranteed SCC); recommended PageRank instead
3. **Harmonic centrality over standard closeness**: handled disconnected/directed graph correctly
4. **Multiple centralities tied to distinct use cases**: PageRank/in-degree for knowledge prestige; betweenness for brokerage/rollout targeting; harmonic for broadcast speed; Burt's constraint for structural hole brokerage
5. **Practical composite ranking**: code skeleton that ranks on all four and produces a composite score
6. **Caveats**: measurement error in survey data; overload risk for high-centrality individuals

## Output

- `outputs/response.md`: 13,631 characters, full practitioner-grade response
- `outputs/metrics.json`: tool call and character tracking
