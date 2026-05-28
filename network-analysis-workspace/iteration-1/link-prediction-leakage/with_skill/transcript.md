# Transcript: Link Prediction Leakage (with skill)

## Task

User prompt: "I'm working on a link prediction model for a social network — trying to predict which friendships will form in the next 6 months. My dataset has ~50k nodes and ~300k existing edges. I split the edges randomly 80/20, trained a GNN on the 80%, and got AUROC = 0.94 on the 20% holdout. My advisor says this is too good to be true. Is she right? How do I know if my evaluation is valid?"

## Steps taken

### Step 1: Read SKILL.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md` in full to understand the methodology, decision points, and which reference files to load.

Identified task archetype: "Predict missing/future links" → link prediction → `references/prediction.md`.

### Step 2: Read references/prediction.md
Read `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/prediction.md` in full.

Key findings relevant to this user's situation:
- Three framings: temporal forecasting, missing-link recovery, spurious link detection. User's stated goal (forecasting) mismatches their protocol (missing-link recovery via random split).
- Critical evaluation issue: test edge leakage into message-passing graph. PyG's RandomLinkSplit handles it correctly if used correctly; many ad-hoc implementations do not.
- Negative sampling: random negatives inflate AUROC substantially; hard negatives (common-neighbor, within-component) are needed for realistic evaluation.
- Heuristic baselines (Adamic-Adar, resource allocation) are often competitive with or better than GNNs; Ghasemian et al. (2020) showed many published GNN gains disappear under proper evaluation.
- Multiple splits needed: single split variance is large.

### Step 3: Checked output directory structure
Verified that `with_skill/outputs/` exists and is empty, ready for output files.

### Step 4: Wrote response
Composed a complete response covering:
1. Framing mismatch (temporal forecasting vs. missing-link recovery)
2. Test edge leakage explanation with diagnostic code
3. Negative sampling inflation problem
4. Heuristic baselines requirement
5. Summary checklist table with canonical references

Saved to: `with_skill/outputs/response.md`

### Step 5: Wrote metrics and transcript
Saved `with_skill/outputs/metrics.json` and this file.

## Key skill contributions

The skill directed attention to:
- The three-framing taxonomy (temporal / missing / spurious), which immediately identified the framing mismatch
- The specific leakage mechanism for GNNs: message-passing graph must exclude val/test edges
- The negative sampling problem as a distinct inflation source
- The Ghasemian et al. (2020) result that proper baselines eliminate many GNN gains
- The requirement to report variance across multiple splits
- Appropriate citations and concrete diagnostic code

Without the skill, a response would likely have addressed the general "sounds too good" concern vaguely and possibly suggested just rerunning the experiment, without diagnosing the specific leakage mechanism or the framing mismatch.
