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
# # 02 — Data clean
#
# Turns the raw SST_cci download into the tidy analysis cube consumed by
# `03_analysis.py`: kelvin → °C, land dropped, ice-affected cells excluded, and
# cells with incomplete records removed.
#
# ## Exclusions, and how they map to the original paper
#
# Oliver et al. (2018) *"excluded any grid cells from the analysis which had
# continuous ice cover duration for longer than 5 days"*. That test needs a sea-ice
# field. We downloaded only `analysed_sst`, so we apply a **proxy**: a cell is
# treated as ice-affected if its daily SST ever falls to the freezing point of
# seawater (≈ −1.7 °C), since an L4 analysis pinned to the freezing point is
# reporting ice rather than open water.
#
# This is a **declared deviation** — it is a stricter, coarser criterion than the
# paper's, and it removes some marginal-ice cells the paper would have kept. It
# affects the high-latitude fringe only. Record it in the Outcome's limitations.

# %%
import os
from pathlib import Path

import numpy as np
import xarray as xr

# %%
TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
LON_BAND_STRIDE = int(os.environ.get("MHW_LON_BAND_STRIDE", 1))

RAW_DIR = Path("../data/raw")
PROC_DIR = Path("../data/processed")
PROC_DIR.mkdir(parents=True, exist_ok=True)

IN_PATH = RAW_DIR / f"sst_cci_{TARGET_RES_DEG:g}deg_stride{LON_BAND_STRIDE}.nc"
OUT_PATH = PROC_DIR / f"sst_clean_{TARGET_RES_DEG:g}deg.nc"

FREEZING_C = -1.7  # seawater freezing point; proxy for "ice was present"

# %% [markdown]
# ## Load

# %%
sst = xr.open_dataarray(IN_PATH)
print("input:", dict(sst.sizes))
print("period:", str(sst.time.values[0])[:10], "->", str(sst.time.values[-1])[:10])

# %% [markdown]
# ## Kelvin → °C
#
# XMHW is unit-agnostic (the threshold is a percentile of whatever it is given),
# but °C keeps intensities readable and comparable with the paper, which reports
# intensities in °C.

# %%
sst_c = sst - 273.15
sst_c.attrs.update(sst.attrs)
sst_c.attrs["units"] = "degC"

# %% [markdown]
# ## Build the valid-cell mask
#
# Three exclusions, applied to the cell (all times) rather than to individual days:
#
# 1. **Land** — all-NaN columns.
# 2. **Incomplete records** — any NaN in the time series. MHW detection depends on
#    day-to-day continuity, so a gap makes the 5-consecutive-day rule ambiguous.
# 3. **Ice-affected** — SST reaches the freezing point at any time (see above).

# %%
n_time = sst_c.sizes["time"]
n_valid = sst_c.notnull().sum("time")

is_land = n_valid == 0
is_incomplete = (n_valid > 0) & (n_valid < n_time)
is_ice = (sst_c <= FREEZING_C).any("time")

valid = (~is_land) & (~is_incomplete) & (~is_ice)

total_cells = int(np.prod([sst_c.sizes[d] for d in ("latitude", "longitude")]))
print(f"total cells      : {total_cells}")
print(f"  land           : {int(is_land.sum())}")
print(f"  incomplete     : {int(is_incomplete.sum())}")
print(f"  ice-affected   : {int((is_ice & ~is_land).sum())}")
print(f"  -> analysed    : {int(valid.sum())} "
      f"({100 * float(valid.sum()) / total_cells:.1f}% of grid)")

# %% [markdown]
# ## Apply the mask and save
#
# Masked cells become all-NaN columns; XMHW's `land_check` drops them, and the
# area-weighted global mean in `03_analysis.py` ignores them.

# %%
sst_clean = sst_c.where(valid)
sst_clean.name = "sst"
sst_clean.attrs.update(
    units="degC",
    long_name="Sea surface temperature, cleaned for MHW detection",
    exclusions="land; incomplete time series; ice-affected "
               f"(SST <= {FREEZING_C} degC at any time)",
    ice_criterion_note="proxy for Oliver et al. (2018) '>5 days continuous ice cover'",
    n_cells_analysed=int(valid.sum()),
)

encoding = {"sst": {"zlib": True, "complevel": 4, "dtype": "float32"}}
sst_clean.to_netcdf(OUT_PATH, encoding=encoding)
print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1e6:.0f} MB)")

# %% [markdown]
# ## Sanity check
#
# A global-mean SST around 18–21 °C with a visible warming trend is the
# expectation; anything far outside that means the mask or the unit conversion
# is wrong.

# %%
weights = np.cos(np.deg2rad(sst_clean.latitude))
gm = sst_clean.weighted(weights).mean(dim=["latitude", "longitude"])
annual_gm = gm.groupby("time.year").mean()
print("global mean SST (degC), first 3 years:",
      [round(float(v), 2) for v in annual_gm.values[:3]])
print("global mean SST (degC), last 3 years :",
      [round(float(v), 2) for v in annual_gm.values[-3:]])
