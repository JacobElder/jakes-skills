# Transcript: Without-Skill Run — Link Prediction Leakage

**Date:** 2026-05-25
**Model:** claude-sonnet-4-6
**Skill used:** None (base model response)

---

## User Prompt

> I'm working on a link prediction model for a social network — trying to predict which friendships will form in the next 6 months. My dataset has ~50k nodes and ~300k existing edges. I split the edges randomly 80/20, trained a GNN on the 80%, and got AUROC = 0.94 on the 20% holdout. My advisor says this is too good to be true. Is she right? How do I know if my evaluation is valid?

---

## Agent Response (summary of steps)

1. Answered the question directly from general knowledge without reading any skill or reference files.
2. Identified the root cause: random edge splitting causes structural data leakage in graph settings because train and test edges share nodes and their neighborhoods.
3. Explained why this inflates AUROC: GNN embeddings already encode neighborhood structure for all nodes, making test edges easy to score.
4. Provided the correct evaluation protocol: temporal splitting based on edge timestamps.
5. Listed additional validity checks: negative sampling strategy (hard vs. easy negatives), degree bias, structural baseline sanity checks, timestamp leakage.
6. Provided a concrete checklist table covering 6 evaluation dimensions.
7. Gave realistic AUROC expectations under rigorous evaluation (0.72–0.85).
8. Recommended precision@K as a more relevant metric for the actual use case.

---

## Tool Calls

| Step | Tool | Purpose |
|------|------|---------|
| 1 | Bash | Create output directory |
| 2 | Bash | Check existing files |
| 3 | Read | Read existing response.md |
| 4 | Read | Read existing metrics.json |
| 5 | Edit | Update response.md with full response |
| 6 | Bash | List transcript directory |
| 7 | Read | Read existing transcript.md |
| 8 | Edit | Update transcript.md |
| 9 | Edit | Update metrics.json |

---

## Key Concepts Covered

- **Random edge splitting leakage**: test edges share node neighborhoods with training edges
- **Structural leakage**: GNN embeddings encode neighborhood proximity for all nodes before test evaluation
- **Common neighbors leakage**: the training graph already reveals structural closeness for test pairs
- **Negative sampling bias**: random negatives are trivially easy; hard negatives (distance-2, structurally proximate pairs) are needed
- **Temporal split**: the correct protocol for future link prediction tasks
- **Degree bias**: high-degree hub nodes inflate aggregate AUROC
- **Structural baseline sanity check**: heuristics like common neighbors or Adamic-Adar expose inflated evaluations without any learning
- **Realistic performance range**: AUROC 0.72–0.85 under rigorous conditions
- **Precision@K**: more relevant metric than AUROC for actionable friendship recommendations
