# Reasoning Transcript

## Step 1: Read SKILL.md

Read the full skill file at `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/SKILL.md`.

Key observations:
- The skill contains a mapping table: "Are similar people connected, or do connections make people similar?" maps to `references/peer_effects.md`
- Core principle #4 explicitly states: "Homophily and contagion are confounded. This is Shalizi and Thomas (2011)'s central result..."
- The common mistakes section explicitly flags: `"Peer effects" from cross-sectional data with friendship. Manski reflection + Shalizi-Thomas confound. SAOM, randomized experiments, or negative-control methods are needed.`

The user's scenario maps cleanly to the peer effects reference. Read that next.

## Step 2: Read references/peer_effects.md

Read the full reference at `/Users/jacobelder/Documents/GitHub/jakes-skills/network-analysis/references/peer_effects.md`.

Key findings relevant to this user:
- The four mechanisms (endogenous peer effects, contextual effects, correlated/homophily, common shocks) — Manski (1993)
- The reflection problem: linear-in-means OLS is unidentified
- Bramoullé et al. (2009): intransitive triads can provide instruments
- Shalizi & Thomas (2011): stronger result — cross-sectional observational data generally cannot separate influence from homophily
- The reference table shows: "Regress y_i on mean(y_friends) in cross-section | claimed: peer influence | actually identifies: almost nothing"
- Recommended methods: SAOM (≥3 waves), Bramoullé IV, latent space, RCT
- The protocol: establish data structure → discuss four confounds → recommend strongest method → report what can/cannot be said

## Step 3: Identify the task type

The user's question is "Are similar people connected, or do connections make people similar?" — this is selection vs. influence. The specific setup:
- Cross-sectional (one wave) — the weakest possible design for this question
- OLS regression of smoking on mean_friends_smoking — hits the reflection problem
- Coefficient β = 0.43, p < 0.001 — highly significant, but the significance doesn't solve identification
- Advisor claims "this shows peer influence" — overclaim

The skill explicitly marks this as a "common mistake to watch for and call out."

## Step 4: Structure the response

The response needs to:
1. Validate the finding (clustering is real)
2. Explain the Manski reflection problem clearly
3. Explain the Shalizi-Thomas confound clearly
4. Precisely characterize what β = 0.43 means and doesn't mean
5. Offer a ranked set of next steps (SAOM > Bramoullé IV > descriptive only)
6. Provide code for both approaches
7. Give the user language to bring back to their advisor
8. Include Moran's I and other descriptive analyses they can run now
9. Summarize with a table

The tone should be: rigorous and honest but constructive — not dismissive of their work. The finding has real value as a descriptive result; the limitation is about causal interpretation.

## Step 5: Write the response

Wrote comprehensive response covering:
- Framing of what the result actually shows
- The two identification problems (reflection problem and Shalizi-Thomas confound)
- Precision about what β = 0.43 means and doesn't mean
- What can legitimately be reported
- Three tiered next steps (SAOM, Bramoullé IV, descriptive minimum)
- Supplementary analyses (Moran's I, assortativity, baseline stats)
- Language for the advisor
- Summary table
- Key references

## Step 6: Save outputs

- response.md → with_skill/outputs/response.md
- metrics.json → with_skill/outputs/metrics.json
- transcript.md → with_skill/transcript.md
