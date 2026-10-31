"""
Composite index of AI adoption speed against governance readiness.

Country level: three adoption indicators and three governance indicators are
min max normalised, weighted and combined. The lag gap is adoption minus
governance, so a positive gap means adoption is running ahead of the rules.

Sector level: the gap is the growth in adoption against the share of firms
that have an AI policy and whether the sector has specific guidance.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "outputs")

ADOPTION_COLS = ["firm_adoption_rate", "ai_investment_per_capita_usd", "ai_talent_concentration"]
GOVERNANCE_COLS = ["ai_policies_count", "binding_regulation", "regulator_capacity"]

DEFAULT_WEIGHTS = {
    "firm_adoption_rate": 0.5,
    "ai_investment_per_capita_usd": 0.25,
    "ai_talent_concentration": 0.25,
    "ai_policies_count": 0.25,
    "binding_regulation": 0.4,
    "regulator_capacity": 0.35,
}


def normalise(df, cols, log_cols=()):
    out = pd.DataFrame(index=df.index)
    for c in cols:
        x = df[c].astype(float)
        if c in log_cols:
            x = np.log1p(x)
        lo, hi = x.min(), x.max()
        out[c] = (x - lo) / (hi - lo) if hi > lo else 0.5
    return out


def score(df, weights=None, log_cols=("ai_investment_per_capita_usd",)):
    w = dict(DEFAULT_WEIGHTS)
    if weights:
        w.update(weights)
    norm = normalise(df, ADOPTION_COLS + GOVERNANCE_COLS, log_cols)
    res = df[["country", "iso3"]].copy()
    a_w = np.array([w[c] for c in ADOPTION_COLS])
    g_w = np.array([w[c] for c in GOVERNANCE_COLS])
    res["adoption_score"] = norm[ADOPTION_COLS].values @ a_w / a_w.sum()
    res["governance_score"] = norm[GOVERNANCE_COLS].values @ g_w / g_w.sum()
    res["lag_gap"] = res["adoption_score"] - res["governance_score"]
    return res.sort_values("lag_gap", ascending=False).reset_index(drop=True)


def sector_scores(df):
    res = df[["sector"]].copy()
    growth = df["adoption_rate_2025"] - df["adoption_rate_2023"]
    res["adoption_growth_pts"] = growth
    res["adoption_score"] = (growth - growth.min()) / (growth.max() - growth.min())
    pol = df["share_firms_with_ai_policy"] / 100.0
    gov = 0.6 * pol + 0.4 * df["sector_specific_guidance"]
    res["governance_score"] = (gov - gov.min()) / (gov.max() - gov.min())
    res["lag_gap"] = res["adoption_score"] - res["governance_score"]
    res["regulated_sector"] = df["regulated_sector"]
    return res.sort_values("lag_gap", ascending=False).reset_index(drop=True)


def sensitivity(df, n=200, seed=0):
    """Perturb the weights and record how often each country lands in the top three gap."""
    rng = np.random.default_rng(seed)
    ranks = {c: [] for c in df["country"]}
    for _ in range(n):
        w = {k: max(0.05, v + rng.normal(0, 0.1)) for k, v in DEFAULT_WEIGHTS.items()}
        s = score(df, w)
        for i, c in enumerate(s["country"]):
            ranks[c].append(i + 1)
    rows = [dict(country=c, mean_rank=np.mean(r), rank_sd=np.std(r),
                 share_top3=np.mean(np.array(r) <= 3)) for c, r in ranks.items()]
    return pd.DataFrame(rows).sort_values("mean_rank").reset_index(drop=True)


def plot_countries(res, path):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(res["governance_score"], res["adoption_score"])
    for _, r in res.iterrows():
        ax.annotate(r["iso3"], (r["governance_score"], r["adoption_score"]),
                    textcoords="offset points", xytext=(4, 4), fontsize=9)
    lim = [0, 1]
    ax.plot(lim, lim, linestyle=":", color="grey")
    ax.set_xlabel("governance readiness score")
    ax.set_ylabel("adoption speed score")
    ax.set_title("AI adoption against governance readiness by country")
    ax.text(0.02, 0.95, "above the line: adoption ahead of governance", transform=ax.transAxes, fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def plot_sectors(res, path):
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["tab:red" if g > 0 else "tab:blue" for g in res["lag_gap"]]
    ax.barh(res["sector"], res["lag_gap"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("lag gap (adoption growth score minus governance score)")
    ax.set_title("Sector level adoption lag, Canada")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    countries = pd.read_csv(os.path.join(DATA, "adoption_indicators.csv"))
    sectors = pd.read_csv(os.path.join(DATA, "sector_adoption.csv"))

    res = score(countries)
    sens = sensitivity(countries)
    res = res.merge(sens, on="country")
    res.round(3).to_csv(os.path.join(OUT, "index_table.csv"), index=False)
    plot_countries(res, os.path.join(OUT, "adoption_vs_governance.png"))

    sec = sector_scores(sectors)
    sec.round(3).to_csv(os.path.join(OUT, "sector_table.csv"), index=False)
    plot_sectors(sec, os.path.join(OUT, "sector_gap.png"))

    print(res.round(3).to_string(index=False))
    print()
    print(sec.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
