# Entropy Rate vs. Stationary Entropy for a Markov Chain

## Setup

Transition matrix (rows = from-state, columns = to-state):

```
P = [[0.9, 0.1],
     [0.2, 0.8]]
```

States: A (index 0), B (index 1).

So:
- From A: P(A→A) = 0.9, P(A→B) = 0.1
- From B: P(B→A) = 0.2, P(B→B) = 0.8

---

## Step 1: Find the Stationary Distribution

The stationary distribution π satisfies πP = π with π_A + π_B = 1.

From πP = π:

```
π_A · 0.9 + π_B · 0.2 = π_A
π_A · 0.1 + π_B · 0.8 = π_B
```

From the first equation:
```
0.9·π_A + 0.2·π_B = π_A
0.2·π_B = 0.1·π_A
π_A = 2·π_B
```

With π_A + π_B = 1:
```
2·π_B + π_B = 1
π_B = 1/3 ≈ 0.3333
π_A = 2/3 ≈ 0.6667
```

Verification: πP
- π_A' = (2/3)(0.9) + (1/3)(0.2) = 0.600 + 0.0667 = 0.6667 ✓
- π_B' = (2/3)(0.1) + (1/3)(0.8) = 0.0667 + 0.2667 = 0.3333 ✓

---

## Step 2: Entropy Rate

For an ergodic Markov chain, the **entropy rate** is:

```
H(X) = -∑_i π_i · ∑_j P(i→j) · log₂ P(i→j)
```

This is the stationary-distribution-weighted average of each row's entropy.

### Row entropy for state A

```
H_A = -[0.9·log₂(0.9) + 0.1·log₂(0.1)]
```

Computing each term:
- log₂(0.9) = ln(0.9)/ln(2) = −0.10536/0.69315 = −0.15200
- log₂(0.1) = ln(0.1)/ln(2) = −2.30259/0.69315 = −3.32193

So:
```
H_A = -[0.9·(−0.15200) + 0.1·(−3.32193)]
     = -[−0.13680 + (−0.33219)]
     = -[−0.46899]
     = 0.46900 bits
```

### Row entropy for state B

```
H_B = -[0.2·log₂(0.2) + 0.8·log₂(0.8)]
```

Computing each term:
- log₂(0.2) = ln(0.2)/ln(2) = −1.60944/0.69315 = −2.32193
- log₂(0.8) = ln(0.8)/ln(2) = −0.22314/0.69315 = −0.32193

So:
```
H_B = -[0.2·(−2.32193) + 0.8·(−0.32193)]
     = -[−0.46439 + (−0.25754)]
     = -[−0.72193]
     = 0.72193 bits
```

### Weighted average

```
H(X) = π_A · H_A + π_B · H_B
      = (2/3)·0.46900 + (1/3)·0.72193
      = 0.31267 + 0.24064
      = 0.55331 bits per step
```

**Entropy rate ≈ 0.5533 bits per step.**

---

## Step 3: Entropy of the Stationary Distribution

The stationary entropy treats the marginal visit frequency as an i.i.d. source:

```
H(π) = -[π_A·log₂(π_A) + π_B·log₂(π_B)]
      = -[(2/3)·log₂(2/3) + (1/3)·log₂(1/3)]
```

Computing each term:
- log₂(2/3) = log₂(2) − log₂(3) = 1 − 1.58496 = −0.58496
- log₂(1/3) = −log₂(3) = −1.58496

So:
```
H(π) = -[(2/3)·(−0.58496) + (1/3)·(−1.58496)]
      = -[−0.38997 + (−0.52832)]
      = -[−0.91829]
      = 0.91830 bits
```

**Stationary entropy H(π) ≈ 0.9183 bits.**

---

## Step 4: Comparison and Interpretation

| Quantity | Value |
|---|---|
| Entropy rate H(X) | **0.5533 bits/step** |
| Stationary entropy H(π) | **0.9183 bits/step** |
| Difference | **0.3650 bits/step** |

**The entropy rate is substantially lower than the stationary entropy** — about 60% of it.

### Why they differ

The **stationary entropy H(π) = 0.9183 bits** answers: "If I told you which state the system is in at a random timestep, how surprised would you be?" It treats each observation as drawn i.i.d. from the marginal distribution and ignores all temporal structure.

The **entropy rate H(X) = 0.5533 bits/step** answers: "Given that I already know the current state, how surprised am I by the next state?" It accounts for the serial dependence encoded in P. Because the chain is sticky — high self-loop probabilities (0.9 and 0.8) — knowing the current state tells you a lot about the next one. That predictability compresses each step to well below what the marginal frequencies alone would suggest.

The gap between the two equals the **mutual information between consecutive states**:

```
I(Xₜ; Xₜ₊₁) = H(π) − H(X) ≈ 0.9183 − 0.5533 = 0.3650 bits
```

This is the information that the current state carries about the next one — the information the i.i.d. approximation throws away.

### Intuition

If the transition matrix were the identity (P = I, perfectly sticky), the entropy rate would collapse to 0 bits/step — the next state is completely determined by the current one — while H(π) would remain nonzero as long as both states are visited. Conversely, if rows of P were uniform [0.5, 0.5], the next state would be independent of the current one, entropy rate would equal H(π) = 1 bit, and the gap would vanish. This chain sits between those extremes: moderately sticky transitions produce an entropy rate that is real but meaningfully below the marginal entropy.
