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
# continuous ice cover duration for longer than 5 days"*. That test names a sea-ice
# field, which we did not download. We apply the **same rule shape** to a proxy
# indicator: SST_cci is a gap-filled L4 analysis that reports SST *under* ice
# pinned to the freezing point of seawater, so "SST ≤ −1.7 °C" stands in for
# "ice present", and a cell is excluded when that persists for **more than 5
# consecutive days** — the paper's own threshold.
#
# The substitution is justified empirically rather than assumed: in the
# downloaded record, cells that ever reach −1.7 °C sit below it ~246 days per
# year at a median latitude of 72.5°, i.e. they are persistently ice-covered
# rather than marginal. Matching the ">5 consecutive days" form (instead of
# "ever freezes") is what keeps genuinely marginal cells in the analysis.
#
# This remains a **declared deviation** — a proxy indicator, not the paper's ice
# field — and the sensitivity of the exclusion is quantified below so the
# Outcome can report its size rather than merely note its existence.

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
MAX_ICE_RUN_DAYS = 5  # the paper's threshold: >5 days continuous ice cover

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
# 3. **Ice-affected** — SST stays at/below freezing for more than 5 consecutive
#    days at any point in the record.


# %%
def max_run_length(da: xr.DataArray, threshold: float,
                   lat_block: int = 20) -> xr.DataArray:
    """Longest run of consecutive days with `da <= threshold`, per cell.

    Materialising the whole cube would cost ~3.3 GB of float plus ~0.8 GB of
    bool at 1° global, so latitude blocks are loaded one at a time and reduced
    to a 2-D run-length map before the next block is read.
    """
    out = []
    n_lat = da.sizes["latitude"]
    for i in range(0, n_lat, lat_block):
        block = (da.isel(latitude=slice(i, i + lat_block)) <= threshold)
        arr = block.fillna(False).values  # (time, lat, lon)
        cur = np.zeros(arr.shape[1:], dtype=np.int32)
        best = np.zeros(arr.shape[1:], dtype=np.int32)
        for t in range(arr.shape[0]):
            cur = np.where(arr[t], cur + 1, 0)
            np.maximum(best, cur, out=best)
        out.append(
            xr.DataArray(
                best,
                dims=("latitude", "longitude"),
                coords={
                    "latitude": block.latitude,
                    "longitude": block.longitude,
                },
            )
        )
    return xr.concat(out, dim="latitude")


# %%
n_time = sst_c.sizes["time"]
n_valid = sst_c.notnull().sum("time")

is_land = n_valid == 0
is_incomplete = (n_valid > 0) & (n_valid < n_time)

ice_run = max_run_length(sst_c, FREEZING_C)
is_ice = ice_run > MAX_ICE_RUN_DAYS

valid = (~is_land) & (~is_incomplete) & (~is_ice)

# Sensitivity: how many cells does the paper's ">5 consecutive days" form keep
# that a naive "ever freezes" rule would have thrown away?
ever_freezes = ice_run > 0
rescued = int(((ever_freezes & ~is_ice) & ~is_land).sum())

total_cells = int(np.prod([sst_c.sizes[d] for d in ("latitude", "longitude")]))
print(f"total cells      : {total_cells}")
print(f"  land           : {int(is_land.sum())}")
print(f"  incomplete     : {int(is_incomplete.sum())}")
print(f"  ice-affected   : {int((is_ice & ~is_land).sum())}")
print(f"    (marginal cells kept by the >5-day rule that "
      f"'ever freezes' would drop: {rescued})")
print(f"  -> analysed    : {int(valid.sum())} "
      f"({100 * float(valid.sum()) / total_cells:.1f}% of grid)")

# Area actually excluded matters more than the cell count, because the excluded
# cells are polar and cos(lat)-weighted down.
w = np.cos(np.deg2rad(sst_c.latitude)).broadcast_like(is_land)
area_ocean = float(w.where(~is_land).sum())
area_excluded = float(w.where((~is_land) & is_ice).sum())
print(f"  ice exclusion  : {100 * area_excluded / area_ocean:.2f}% of ocean AREA")

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
               f"(SST <= {FREEZING_C} degC for > {MAX_ICE_RUN_DAYS} "
               "consecutive days)",
    ice_criterion_note="SST at the seawater freezing point is used as a proxy "
                       "for ice presence; the >5-consecutive-day threshold is "
                       "Oliver et al. (2018)'s own ice-exclusion rule",
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
