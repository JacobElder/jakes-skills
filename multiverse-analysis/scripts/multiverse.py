"""
multiverse.py — a small, dependency-light engine for multiverse / specification-curve analysis.

A multiverse analysis makes the *arbitrary-but-defensible* choices in a data analysis
explicit, runs the analysis under every reasonable combination of those choices, and
reports the whole distribution of results instead of a single hand-picked number.
See Steegen et al. (2016) and Simonsohn, Simmons & Nelson (2020).

This module deliberately depends only on pandas, numpy and matplotlib (scipy is optional)
so it runs anywhere. It is analysis-agnostic: YOU supply a function that takes the data
plus one resolved combination of choices and returns a dict of results. The engine handles
the boring, error-prone parts: enumerating the grid, dropping nonsensical cells, running
every universe (without one failure killing the rest), tidying results, drawing the
specification curve, and running permutation-based inference on the curve as a whole.

Typical use
-----------
    from multiverse import Multiverse, specification_curve, permutation_test

    def analyze(data, choices):
        # `choices` is a dict {decision_name: resolved_option_value}
        df = data
        if choices["outliers"] is not None:
            z = (df["y"] - df["y"].mean()) / df["y"].std()
            df = df[z.abs() <= choices["outliers"]]
        # ... fit a model using choices["dv"], choices["covariate"], etc.
        return {"estimate": beta, "p_value": p, "ci_low": lo, "ci_high": hi, "n": len(df)}

    mv = Multiverse(
        decisions={
            "outliers":  {"none": None, "3sd": 3.0, "2sd": 2.0},
            "dv":        {"time": "time_to_top", "falls": "num_falls"},
            "covariate": {"none": [], "time_of_day": ["time_of_day"]},
        },
        # drop combinations that are not meaningful before they ever run:
        constraints=[lambda c: not (c["dv"] == "falls" and c["covariate"] == "none")],
    )
    print(mv.summary())              # how many universes, after constraints
    results = mv.run(analyze, data)  # tidy DataFrame: one row per universe
    specification_curve(results, outfile="curve.png")
    permutation_test(mv, analyze, data, shuffle="group", stat_col="estimate")
"""

from __future__ import annotations

import itertools
import traceback
from typing import Callable, Iterable

import numpy as np
import pandas as pd


class Multiverse:
    """Enumerate and execute the cross-product of analytic decisions.

    Parameters
    ----------
    decisions : dict[str, dict[str, Any]]
        Maps each decision point (parameter) to its reasonable options. Keys of the
        inner dict are human-readable option names that appear in the output; values
        are whatever your analysis function needs (a threshold, a column name, a list
        of covariates, a callable, ...).
    constraints : list of callables, optional
        Each callable receives a dict {decision: option_name} and returns True if the
        combination is VALID (should be kept). Use these to remove nonsensical cells
        (e.g. a linear model with a binary DV) *before* execution rather than letting
        them error out. This mirrors `%when%` in the R `multiverse` package and
        `@constraint` in Boba.
    """

    def __init__(self, decisions: dict[str, dict], constraints: Iterable[Callable] | None = None):
        if not decisions:
            raise ValueError("Provide at least one decision.")
        self.decisions = {k: dict(v) for k, v in decisions.items()}
        self.constraints = list(constraints or [])

    # -- enumeration ---------------------------------------------------------
    def grid(self) -> list[dict]:
        """Return the list of valid universes as dicts of {decision: option_name}."""
        names = list(self.decisions)
        option_names = [list(self.decisions[n]) for n in names]
        universes = []
        for combo in itertools.product(*option_names):
            choice = dict(zip(names, combo))
            if all(c(choice) for c in self.constraints):
                universes.append(choice)
        return universes

    def n_total(self) -> int:
        n = 1
        for opts in self.decisions.values():
            n *= len(opts)
        return n

    def summary(self) -> str:
        valid = len(self.grid())
        total = self.n_total()
        lines = [f"{len(self.decisions)} decisions, {total} combinations, "
                 f"{valid} valid universes after constraints ({total - valid} dropped)."]
        for name, opts in self.decisions.items():
            lines.append(f"  - {name}: {len(opts)} options ({', '.join(opts)})")
        return "\n".join(lines)

    # -- execution -----------------------------------------------------------
    def _run_one(self, analyze: Callable, data, i: int, choice: dict) -> dict:
        resolved = {d: self.decisions[d][opt] for d, opt in choice.items()}
        row = {".universe": i, **choice, ".error": None}
        try:
            out = analyze(data, resolved)
            if not isinstance(out, dict):
                raise TypeError("analyze() must return a dict of results.")
            row.update(out)
        except Exception as e:  # keep going; record what broke
            row[".error"] = f"{type(e).__name__}: {e}"
            row["_traceback"] = traceback.format_exc()
        return row

    def run(self, analyze: Callable, data, max_universes: int | None = None,
            seed: int = 0, progress: bool = True, n_jobs: int = 1) -> pd.DataFrame:
        """Run `analyze(data, resolved_choices)` for every valid universe.

        Returns a tidy DataFrame: one row per universe, with the option-name columns
        for each decision, a `.universe` index, an `.error` column (None if the run
        succeeded), plus whatever keys your analyze() dict returned.

        A failure in one universe is recorded in `.error` and does not stop the others
        (same philosophy as `execute_multiverse()` in the R package). If `max_universes`
        is set and the grid is larger, a random sample of that many universes is run --
        useful when the full cross-product is too big to estimate exhaustively (Simonsohn
        et al. note you can randomly draw from the set of reasonable specifications).

        `n_jobs` > 1 (or -1 for all cores) parallelizes across universes via joblib if it
        is installed, falling back to serial otherwise. Because joblib uses cloudpickle,
        a closure `analyze` works fine. Each universe must not mutate shared state -- copy
        `data` inside `analyze` (the engine does not copy it for you, to avoid the cost on
        large frames). Parallelism mainly pays off for the permutation test.
        """
        universes = self.grid()
        if max_universes is not None and len(universes) > max_universes:
            rng = np.random.default_rng(seed)
            idx = rng.choice(len(universes), size=max_universes, replace=False)
            universes = [universes[i] for i in sorted(idx)]

        if n_jobs != 1:
            try:
                from joblib import Parallel, delayed
                rows = Parallel(n_jobs=n_jobs)(
                    delayed(self._run_one)(analyze, data, i, c)
                    for i, c in enumerate(universes))
            except ImportError:
                n_jobs = 1
        if n_jobs == 1:
            rows = []
            for i, choice in enumerate(universes):
                rows.append(self._run_one(analyze, data, i, choice))
                if progress and (i + 1) % max(1, len(universes) // 10) == 0:
                    print(f"  ...{i + 1}/{len(universes)} universes")
        df = pd.DataFrame(rows)
        n_err = df[".error"].notna().sum()
        if n_err:
            print(f"Note: {n_err}/{len(df)} universes errored (see the .error column).")
        return df


# -- visualization -----------------------------------------------------------
def specification_curve(results: pd.DataFrame, estimate: str = "estimate",
                        p_value: str | None = "p_value", alpha: float = 0.05,
                        ci: tuple[str, str] | None = ("ci_low", "ci_high"),
                        decisions: list[str] | None = None, outfile: str | None = None,
                        title: str = "Specification curve", figsize=(11, 9),
                        highlight: dict | int | None = None,
                        max_display: int | None = None, seed: int = 0):
    """Draw the standard two-panel specification curve (Simonsohn et al., 2020).

    Top panel: every universe's point estimate, sorted ascending, with optional CIs,
    colored by statistical significance. Bottom panel: a tick grid showing which option
    was active in each decision for the universe directly above it, so the reader can
    see *which choices* move the estimate.

    `highlight` marks the analyst's original/preferred specification on the curve (the
    reporting guidance asks you to locate it): pass a `.universe` index, or a dict of
    {decision: option_name} identifying it. It is drawn as a labelled vertical marker.

    `max_display` downsamples the plot for very large multiverses (Simonsohn et al.
    suggest ~150 specs is readable). When set, the N/4 lowest and N/4 highest estimates
    are always shown, and the remaining display budget is filled with a random sample from
    the middle — following the recommendation to anchor on the tails. All statistics
    (median, share significant) are computed on the full results, not the display subset.
    """
    import matplotlib.pyplot as plt

    df = results[results[".error"].isna()].copy() if ".error" in results else results.copy()
    df = df.dropna(subset=[estimate]).sort_values(estimate).reset_index(drop=True)
    if df.empty:
        raise ValueError("No successful universes with a non-null estimate to plot.")

    # compute stats on the FULL frame before any downsampling
    sig_full = (df[p_value] < alpha) if (p_value and p_value in df) else None
    med = df[estimate].median()
    share_sig = float(sig_full.mean()) if sig_full is not None else float("nan")
    n_total = len(df)

    # downsample for display only
    if max_display is not None and len(df) > max_display:
        n_tail = max(1, max_display // 4)
        n_mid  = max_display - 2 * n_tail
        tail_idx  = list(range(n_tail)) + list(range(len(df) - n_tail, len(df)))
        mid_pool  = [i for i in range(n_tail, len(df) - n_tail) if i not in tail_idx]
        rng       = np.random.default_rng(seed)
        mid_idx   = sorted(rng.choice(mid_pool, size=min(n_mid, len(mid_pool)), replace=False))
        keep      = sorted(set(tail_idx) | set(mid_idx))
        df        = df.iloc[keep].reset_index(drop=True)

    x = np.arange(len(df))

    if decisions is None:
        reserved = {estimate, p_value, ".universe", ".error", "_traceback"}
        if ci:
            reserved |= set(ci)
        decisions = [c for c in df.columns
                     if c not in reserved and not pd.api.types.is_numeric_dtype(df[c])
                     and df[c].nunique() > 1]

    sig = None
    if p_value and p_value in df:
        sig = df[p_value] < alpha
    rows = sum(df[d].nunique() for d in decisions)
    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=figsize, sharex=True,
        gridspec_kw={"height_ratios": [3, max(1.2, rows / 4)], "hspace": 0.05})

    # top: estimates
    if ci and ci[0] in df and ci[1] in df:
        ax_top.vlines(x, df[ci[0]], df[ci[1]], color="0.8", lw=0.8, zorder=1)
    colors = np.where(sig, "#c0392b", "#7f8c8d") if sig is not None else "#34495e"
    ax_top.scatter(x, df[estimate], c=colors, s=10, zorder=2)
    ax_top.axhline(0, color="black", lw=0.8, ls="--")
    med = df[estimate].median()
    ax_top.axhline(med, color="#2980b9", lw=1.0, ls=":")  # pre-computed on full frame

    # mark the analyst's original/preferred specification, if given
    if highlight is not None:
        pos = None
        if isinstance(highlight, int) and ".universe" in df:
            hits = df.index[df[".universe"] == highlight].tolist()
            pos = hits[0] if hits else None
        elif isinstance(highlight, dict):
            mask = np.ones(len(df), dtype=bool)
            for k, v in highlight.items():
                if k in df:
                    mask &= (df[k] == v).values
            hits = np.where(mask)[0]
            pos = int(hits[0]) if len(hits) else None
        if pos is not None:
            ax_top.axvline(pos, color="#16a085", lw=1.2, zorder=0)
            ax_top.annotate("original", xy=(pos, df[estimate].iloc[pos]),
                            xytext=(0, 12), textcoords="offset points",
                            ha="center", fontsize=8, color="#16a085",
                            fontweight="bold")
    ax_top.set_ylabel(estimate)
    ax_top.set_title(title, loc="left", fontweight="bold")
    ax_top.text(0.99, 0.02,
                f"median={med:.3g}   {n_total} specs"
                + (f"   {share_sig:.0%} p<{alpha}" if not np.isnan(share_sig) else ""),
                transform=ax_top.transAxes, ha="right", va="bottom", fontsize=9, color="0.3")

    # bottom: which option was active
    ylabels, y = [], 0
    for d in decisions:
        for opt in sorted(df[d].dropna().unique(), key=str):
            mask = (df[d] == opt).values
            ax_bot.scatter(x[mask], np.full(mask.sum(), y),
                           marker="|", s=30,
                           c=(colors[mask] if sig is not None else "#34495e"))
            ylabels.append(f"{d}: {opt}")
            y += 1
        y += 0.4  # gap between decisions
    ax_bot.set_yticks(range(len(ylabels)))
    ax_bot.set_yticklabels(ylabels, fontsize=8)
    ax_bot.set_ylim(-1, y)
    ax_bot.invert_yaxis()
    ax_bot.set_xlabel("specification (sorted by estimate)")
    ax_bot.grid(axis="y", color="0.92")
    for s in ("top", "right"):
        ax_top.spines[s].set_visible(False)
        ax_bot.spines[s].set_visible(False)
    fig.tight_layout()
    if outfile:
        fig.savefig(outfile, dpi=150, bbox_inches="tight")
        print(f"Saved {outfile}")
    return fig


def decision_importance(results: pd.DataFrame, estimate: str = "estimate",
                        decisions: list[str] | None = None) -> pd.DataFrame:
    """How much does each decision move the estimate?

    For each decision, reports the spread (max-min of the per-option median estimate)
    and a **marginal** eta-squared: the share of total variance explained by that
    decision in a one-way ANOVA, ignoring all other decisions. Because this is marginal
    (not a full variance decomposition), the values can sum to more than 1.0 when
    decisions share variance — treat the ranking, not the absolute numbers, as the
    meaningful output. In a balanced orthogonal design the values will sum to ≤ 1.

    Bigger = more consequential. Schweinsberg et al. (2021) found operationalization
    decisions dominated statistical ones; this quantifies that for your own multiverse.
    """
    df = results[results[".error"].isna()].copy() if ".error" in results else results.copy()
    df = df.dropna(subset=[estimate])
    if decisions is None:
        reserved = {estimate, "p_value", ".universe", ".error", "_traceback",
                    "ci_low", "ci_high", "n"}
        decisions = [c for c in df.columns
                     if c not in reserved and not pd.api.types.is_numeric_dtype(df[c])
                     and df[c].nunique() > 1]
    grand_var = df[estimate].var(ddof=0)
    out = []
    for d in decisions:
        grp = df.groupby(d)[estimate]
        between = ((grp.transform("mean") - df[estimate].mean()) ** 2).mean()
        eta2 = between / grand_var if grand_var > 0 else float("nan")
        spread = grp.median().max() - grp.median().min()
        out.append({"decision": d, "n_options": df[d].nunique(),
                    "median_spread": spread, "eta_squared": eta2})
    return pd.DataFrame(out).sort_values("eta_squared", ascending=False).reset_index(drop=True)


# -- inference ---------------------------------------------------------------
def permutation_test(mv: "Multiverse", analyze: Callable, data, shuffle,
                     stat_col: str = "estimate", p_col: str = "p_value",
                     alpha: float = 0.05, n_perm: int = 500, seed: int = 0,
                     direction: str = "auto", max_universes: int | None = None,
                     n_jobs: int = 1) -> dict:
    """Joint inference on the specification curve (Simonsohn, Simmons & Nelson, 2020).

    The question is not "is any single specification significant" (with hundreds of specs,
    some will be by chance) but "is the curve as a whole inconsistent with the null?".
    We break the link between the focal predictor and the outcome by shuffling it, re-run
    the entire multiverse on each shuffled dataset, and build a null distribution for three
    test statistics:
      - median estimate across specifications,
      - share of specifications significant in the predicted direction,
      - share significant in the opposite direction.
    The p-value is the proportion of shuffled multiverses whose statistic is at least as
    extreme as the observed one.

    Parameters
    ----------
    shuffle : str or list[str]
        Column(s) representing the focal predictor. If several columns encode the same
        predictor (e.g. two operationalizations of the IV, or dummy codes of one factor),
        pass them as a list -- they are permuted with the SAME row order so their mutual
        relationship is preserved and only their link to the outcome is broken. Permuting
        such columns independently would be wrong.
    direction : {"auto", "positive", "negative"}
        The predicted sign of the effect, used for the one-sided p-values. "auto" infers it
        from the observed statistic relative to the null center; set it explicitly (to your
        pre-registered hypothesis) to avoid the mild optimism of choosing the direction post
        hoc.
    n_jobs : int
        Passed to `mv.run`; >1 parallelizes universes within each permutation. Permutation
        inference is the expensive part (n_perm x n_universes fits), so this is where
        parallelism pays off. Keep `n_perm` modest while iterating; raise it (>=500) to report.
    """
    rng = np.random.default_rng(seed)
    cols = [shuffle] if isinstance(shuffle, str) else list(shuffle)
    for c in cols:
        if c not in data:
            raise KeyError(f"shuffle column {c!r} not in data.")

    def stats(res: pd.DataFrame) -> dict:
        ok = res[res[".error"].isna()].dropna(subset=[stat_col])
        d = {"median": ok[stat_col].median()}
        if p_col in ok:
            d["share_pos_sig"] = float(((ok[p_col] < alpha) & (ok[stat_col] > 0)).mean())
            d["share_neg_sig"] = float(((ok[p_col] < alpha) & (ok[stat_col] < 0)).mean())
        return d

    observed = stats(mv.run(analyze, data, max_universes=max_universes,
                            progress=False, n_jobs=n_jobs))
    null = {k: [] for k in observed}
    for i in range(n_perm):
        shuffled = data.copy()
        perm = rng.permutation(len(shuffled))      # one shared permutation for all cols
        for c in cols:
            shuffled[c] = shuffled[c].values[perm]
        s = stats(mv.run(analyze, shuffled, progress=False, n_jobs=n_jobs))
        for k in null:
            null[k].append(s[k])
        if (i + 1) % max(1, n_perm // 5) == 0:
            print(f"  ...{i + 1}/{n_perm} permutations")

    result = {}
    for k, obs in observed.items():
        nd = np.array(null[k], dtype=float)
        center = float(np.nanmedian(nd))
        if k == "median":
            # the median's extreme tail depends on the predicted sign of the effect
            if direction == "positive" or (direction == "auto" and obs >= center):
                p = (np.sum(nd >= obs) + 1) / (len(nd) + 1)
            else:
                p = (np.sum(nd <= obs) + 1) / (len(nd) + 1)
        else:
            # share_pos_sig / share_neg_sig already encode a direction; the extreme is
            # always "more significant-in-that-direction than the null" -> upper tail
            p = (np.sum(nd >= obs) + 1) / (len(nd) + 1)
        result[k] = {"observed": obs, "null_median": center, "p_value": float(p)}
    print("\nJoint inference on the specification curve:")
    for k, v in result.items():
        print(f"  {k:14s} observed={v['observed']:.4g}  "
              f"null≈{v['null_median']:.4g}  p={v['p_value']:.4f}")
    return result
