# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 04 — Figures
#
# Produces `figures/main_result.png`: the replication of **Figure 2** of Oliver
# et al. (2018) — globally averaged total marine heatwave days per year — beside
# a direct comparison of the headline statistics.
#
# The original Figure 2 also plots an ENSO-removed series (red line). We do not
# reproduce that line: it requires regressing daily SST on the multivariate ENSO
# index at every pixel, which is a separate analysis from the claim under test.
# Its absence is a scope limitation, not a disagreement.

# %%
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy import stats

plt.style.use("seaborn-v0_8-whitegrid")

# %%
TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
LON_BAND_STRIDE = int(os.environ.get("MHW_LON_BAND_STRIDE", 8))
PERIOD_END = os.environ.get("MHW_PERIOD_END", "2016-12-31")
RESULTS_DIR = Path("../results")
FIG_DIR = Path("../figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# The configuration the replication's reported result was produced with: full
# global coverage at 1°, over Oliver et al.'s complete satellite record.
# CI runs the same code over a coarse grid to prove it still works, and any
# other configuration is a partial run whose numbers are NOT the result. Such a
# run must never overwrite figures/main_result.png or be mistakable for it, so
# it is written under a self-describing name and stamped on the face.
FULL_CONFIG = (1.0, 1, "2016-12-31")
IS_FULL_REPLICATION = (TARGET_RES_DEG, LON_BAND_STRIDE, PERIOD_END) == FULL_CONFIG
FIG_PATH = FIG_DIR / (
    "main_result.png" if IS_FULL_REPLICATION
    else f"partial_run_{TARGET_RES_DEG:g}deg_stride{LON_BAND_STRIDE}.png"
)
if not IS_FULL_REPLICATION:
    print(
        f"NOT the full replication configuration "
        f"({TARGET_RES_DEG:g}° grid, stride {LON_BAND_STRIDE}, to {PERIOD_END}; "
        f"full = 1° / stride 1 / to 2016-12-31).\n"
        f"These numbers do not reproduce the paper's statistic. "
        f"Writing {FIG_PATH.name} instead of main_result.png."
    )

_tag = f"partial_run_{TARGET_RES_DEG:g}deg_stride{LON_BAND_STRIDE}"
ANNUAL_PATH = RESULTS_DIR / (
    f"mhw_annual_{TARGET_RES_DEG:g}deg.nc" if IS_FULL_REPLICATION
    else f"{_tag}_annual.nc"
)
CMP_PATH = RESULTS_DIR / (
    "headline_comparison.json" if IS_FULL_REPLICATION
    else f"{_tag}_comparison.json"
)

res = xr.open_dataset(ANNUAL_PATH)
with open(CMP_PATH) as f:
    cmp = json.load(f)

years = res.year.values
days = res["global_mhw_days"].values

# %% [markdown]
# ## Figure 2 replication + headline comparison

# %%
fig, (ax, ax2) = plt.subplots(
    1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.7, 1]}
)

# --- Panel A: the Figure 2 analogue -----------------------------------------
ax.plot(years, days, color="black", lw=1.8, label="ESA SST_cci + XMHW (this work)")

ok = np.isfinite(days)
slope, intercept, lo, hi = stats.theilslopes(days[ok], years[ok].astype(float), 0.95)
ax.plot(years, intercept + slope * years, color="crimson", lw=1.6, ls="--",
        label=f"Theil–Sen trend ({slope * 10:+.1f} days/decade)")

# Oliver et al.'s stated satellite-era endpoints, for reference.
o_base = cmp["mhw_days"]["original_baseline_1980s"]
o_end = o_base + cmp["mhw_days"]["original_change_over_record"]
ax.plot([years[0], years[-1]], [o_base, o_end], color="tab:blue", lw=1.6, ls=":",
        label=f"Oliver et al. 2018 (~{o_base:.0f} → ~{o_end:.0f} days)")

ax.set_xlabel("Year")
ax.set_ylabel("Annual MHW days (global mean)")
ax.set_title("Total marine heatwave days globally\n"
             "replication of Oliver et al. (2018) Fig. 2", fontsize=11)
ax.legend(fontsize=8, loc="upper left")

# --- Panel B: headline statistics, original vs replication -------------------
metrics = [
    ("MHW days\nover record", cmp["mhw_days"]["original_change_over_record"],
     cmp["mhw_days"]["replication_change_over_record"], "days"),
    ("Frequency\ntrend", cmp["mhw_frequency"]["original_trend_per_decade"],
     cmp["mhw_frequency"]["replication_trend_per_decade"], "events/decade"),
    ("Duration\ntrend", cmp["mhw_duration"]["original_trend_per_decade"],
     cmp["mhw_duration"]["replication_trend_per_decade"], "days/decade"),
]
y = np.arange(len(metrics))
h = 0.36
ax2.barh(y - h / 2, [m[1] for m in metrics], height=h,
         color="tab:blue", alpha=0.85, label="Oliver et al. 2018")
ax2.barh(y + h / 2, [m[2] for m in metrics], height=h,
         color="black", alpha=0.85, label="This replication")
for i, (_, orig, repl, unit) in enumerate(metrics):
    ax2.text(max(orig, repl) * 1.03, i - h / 2, f"{orig:g}", va="center", fontsize=8)
    ax2.text(max(orig, repl) * 1.03, i + h / 2, f"{repl:g}", va="center", fontsize=8)
ax2.set_yticks(y)
ax2.set_yticklabels([m[0] for m in metrics], fontsize=9)
ax2.invert_yaxis()
ax2.set_xlabel("Value (units differ per row — see labels)")
ax2.set_title("Headline statistics", fontsize=11)
ax2.legend(fontsize=8, loc="lower right")

n_cells = cmp["replication"]["n_cells"]
fig.suptitle("", y=0.99)
fig.text(0.01, 0.01,
         f"ESA SST CCI Analysis v3.0 (DOI 10.5285/4a9654136a7148e39b7feb56f8bb02d2) · "
         f"XMHW (DOI 10.5281/zenodo.7662469) · {TARGET_RES_DEG:g}° grid, "
         f"{n_cells} ocean cells · climatology "
         f"{cmp['replication']['climatology_period'][0]}–"
         f"{cmp['replication']['climatology_period'][1]}",
         fontsize=7, color="0.35")

# A partial run's figure is visually indistinguishable from the real one, and
# a figure outlives the shell that made it. Stamp it so it cannot be quoted by
# mistake.
if not IS_FULL_REPLICATION:
    fig.text(
        0.5, 0.5,
        f"SMOKE RUN — NOT THE REPLICATION RESULT\n"
        f"{TARGET_RES_DEG:g}° grid, every {LON_BAND_STRIDE}th longitude band",
        ha="center", va="center", fontsize=20, color="crimson",
        alpha=0.28, rotation=24, weight="bold", zorder=10,
    )

fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig(FIG_PATH, dpi=150, bbox_inches="tight")
plt.show()

# %% [markdown]
# ## Spatial diagnostic
#
# Not in the original Figure 2, but it shows *where* the global trend comes from
# and makes a hemispheric artefact immediately visible if one exists.

# %%
try:
    import cartopy.crs as ccrs

    trend = xr.apply_ufunc(
        lambda v: stats.theilslopes(v, years.astype(float))[0] * 10
        if np.isfinite(v).sum() > 10 else np.nan,
        res["mhw_days"],
        input_core_dims=[["year"]],
        vectorize=True,
        output_dtypes=[float],
    )

    fig2 = plt.figure(figsize=(11, 5))
    axm = plt.axes(projection=ccrs.Robinson())
    p = trend.plot(
        ax=axm, transform=ccrs.PlateCarree(), cmap="RdBu_r",
        vmin=-30, vmax=30, add_colorbar=False,
    )
    axm.coastlines(linewidth=0.4)
    axm.set_global()
    cb = fig2.colorbar(p, ax=axm, orientation="horizontal", pad=0.05, shrink=0.7)
    cb.set_label("Trend in annual MHW days (days per decade)")
    axm.set_title("Where the global MHW-day trend comes from, 1982–2016", fontsize=11)
    fig2.savefig(FIG_DIR / "mhw_days_trend_map.png", dpi=150, bbox_inches="tight")
    plt.show()
except Exception as exc:  # cartopy is optional for the headline result
    print(f"skipped map: {exc}")
