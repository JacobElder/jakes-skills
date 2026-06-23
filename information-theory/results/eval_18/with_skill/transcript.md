# Entropy Rate vs. Marginal Entropy of a Navigation Stream

## The objects being computed

Two different quantities are in play here, and conflating them is the standard mistake:

1. **Entropy rate** `H(𝒳)` — the per-step uncertainty *given the state you are currently in*. Because the next state depends on the current one (the chain has memory), this is the conditional entropy averaged over the stationary distribution.

2. **Marginal entropy** `H(μ)` — the entropy of *which state is visited*, treating each visit as independent. This ignores the transition structure entirely.

The reference puts it directly: "Reporting marginal symbol entropy for a clearly dependent sequence (anything with autocorrelation) **overstates** its true per-symbol information — the conditional form is the honest one."

---

## Step 1: Stationary distribution

The transition matrix is

```
P = [[0.9, 0.1],
     [0.2, 0.8]]
```

Row 1 = "currently in state A", row 2 = "currently in state B".

Solve `μ P = μ` with `μ_A + μ_B = 1`:

```
μ_A = 0.9 μ_A + 0.2 μ_B
μ_A − 0.9 μ_A = 0.2 μ_B
0.1 μ_A = 0.2 μ_B
μ_A = 2 μ_B
```

With `μ_A + μ_B = 1`:

```
2 μ_B + μ_B = 1  →  μ_B = 1/3,  μ_A = 2/3
```

**Stationary distribution: μ = (2/3, 1/3)**

Interpretation: in the long run the user spends 2/3 of their time in state A and 1/3 in state B.

---

## Step 2: Per-row transition entropies

The entropy of each row is the binary entropy `H_b(p) = −p log₂ p − (1−p) log₂(1−p)`.

**Row A** (transitions 0.9 → A, 0.1 → B):

```
H(row A) = −0.9 log₂(0.9) − 0.1 log₂(0.1)
         = −0.9 × (−0.15200) − 0.1 × (−3.32193)
         = 0.13680 + 0.33219
         = 0.46900 bits
```

Detailed arithmetic:
- `log₂(0.9) = ln(0.9)/ln(2) = −0.10536/0.69315 = −0.15200`
- `log₂(0.1) = ln(0.1)/ln(2) = −2.30259/0.69315 = −3.32193`

**Row B** (transitions 0.2 → A, 0.8 → B):

```
H(row B) = −0.2 log₂(0.2) − 0.8 log₂(0.8)
         = −0.2 × (−2.32193) − 0.8 × (−0.32193)
         = 0.46439 + 0.25754
         = 0.72193 bits
```

Detailed arithmetic:
- `log₂(0.2) = ln(0.2)/ln(2) = −1.60944/0.69315 = −2.32193`
- `log₂(0.8) = ln(0.8)/ln(2) = −0.22314/0.69315 = −0.32193`

---

## Step 3: Entropy rate (Markov closed form)

For a stationary first-order Markov chain:

```
H(𝒳) = Σᵢ μᵢ H(row i)
       = μ_A · H(row A) + μ_B · H(row B)
```

```
H(𝒳) = (2/3) × 0.46900 + (1/3) × 0.72193
       = 0.31267 + 0.24064
       = 0.55331 bits/step
```

**Entropy rate ≈ 0.5533 bits per step.**

This is the right "how compressible is this navigation stream" number. It answers: given that I know which state the user is in right now, how much information (in bits) does the next transition carry on average?

---

## Step 4: Marginal entropy of visited states

Treat each visit as an independent draw from the stationary distribution μ = (2/3, 1/3):

```
H(μ) = −(2/3) log₂(2/3) − (1/3) log₂(1/3)
```

Computing each term:
- `log₂(2/3) = log₂(2) − log₂(3) = 1 − 1.58496 = −0.58496`
- `log₂(1/3) = −log₂(3) = −1.58496`

```
H(μ) = −(2/3)(−0.58496) − (1/3)(−1.58496)
       = 0.38997 + 0.52832
       = 0.91830 bits
```

**Marginal entropy H(μ) ≈ 0.9183 bits.**

---

## Step 5: Comparison and interpretation

| Quantity | Value | What it measures |
|---|---|---|
| Entropy rate `H(𝒳)` | **0.5533 bits/step** | Per-step uncertainty *given current state* |
| Marginal entropy `H(μ)` | **0.9183 bits** | Per-visit uncertainty ignoring transitions |
| **Difference** | **0.3650 bits** | Information "used up" by the Markov structure |

The marginal entropy is larger by 0.3650 bits — **about 66% larger than the entropy rate.** That gap is the information already explained by knowing where the user currently is. The chain has strong self-loops (0.9 and 0.8), so the next state is highly predictable from the current one, and the marginal entropy substantially overstates how surprising the stream actually is.

This is the same relationship as Shannon's famous claim that English is ~1 bit/character (entropy rate) versus ~4 bits/character (marginal letter entropy): the marginal ignores context and overstates unpredictability. The entropy rate is the honest number for compression and predictive modeling.

---

## When to use which

- **Entropy rate** is the right number for: lossless compression of the event log, assessing how predictable the UX flow is, building a next-state predictor, or characterizing the "true" information content of the stream.
- **Marginal entropy** is appropriate only if you genuinely believe successive visits are independent — which the transition matrix directly contradicts. Using it here would overstate how hard the stream is to predict by 66%.

---

## Quick sanity check

The inequality `H(𝒳) ≤ H(μ)` must hold for any stationary ergodic chain, because conditioning on the current state cannot increase entropy on average. ✓ (0.5533 < 0.9183).

Equality would hold only if the rows of P were all identical (transitions independent of current state), which would mean the chain has no memory. Here the rows differ substantially (0.46 vs 0.72 bits), so the gap is real and meaningful.
