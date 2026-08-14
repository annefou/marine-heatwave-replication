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
# # 05 — Remove the ENSO signature from the SST record
#
# Produces the input for the **red line** in Oliver et al. (2018) Fig. 2, the
# globally averaged MHW days *after removing the signature of ENSO*.
#
# ## The paper's method (Methods, "Removing ENSO")
#
# > We removed the influence of ENSO from the SST time series, before the MHW
# > detection, using a statistical approach. We first estimated the ENSO signal
# > at each pixel by regressing daily SSTs onto the multivariate ENSO index
# > (MEI) and subtracted the linear prediction based on this model. We included
# > monthly leads and lags of the MEI up to ±1 year, into a multiple linear
# > regression model. The MEI is defined monthly as a 2-month average (Dec–Jan,
# > Jan–Feb, etc.) and we assumed the monthly values to be centred on the middle
# > of second month.
#
# Two details from that paragraph drive the implementation:
#
# 1. **±1 year of monthly leads and lags** → 25 MEI predictors (−12 … +12)
#    plus an intercept.
# 2. **Detection afterwards uses the ORIGINAL climatology and threshold**, not
#    one recomputed from the ENSO-less series. The paper is explicit about why:
#    *"what we consider MHWs, and what ecosystems are adapted to, are based on
#    the real-world threshold"*. That happens in `03_analysis.py` under
#    `MHW_ENSO_REMOVED=1`; this notebook only produces the ENSO-less SST.
#
# ## Deviation from the paper
#
# The paper used the original MEI (Wolter & Timlin). NOAA PSL froze that index
# in 2018 and now maintains MEI.v2, computed from a different variable set over
# a different base period. We use the **original** MEI, still published at
# `psl.noaa.gov/enso/mei.old/`, because matching the paper's index matters more
# here than using the current one — its last update (Dec 2018) postdates the
# paper, so it is the same data the authors had.

# %%
import io
import os
import re
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
MEI_URL = "https://psl.noaa.gov/enso/mei.old/table.html"
MAX_LAG_MONTHS = 12  # ±1 year, per the paper

PROC_DIR = Path("../data/processed")
RAW_DIR = Path("../data/raw")
IN_PATH = PROC_DIR / f"sst_clean_{TARGET_RES_DEG:g}deg.nc"
OUT_PATH = PROC_DIR / f"sst_enso_removed_{TARGET_RES_DEG:g}deg.nc"
MEI_PATH = RAW_DIR / "mei_original.csv"

# Latitude rows per chunk. The regression is cheap; holding the full cube is
# not (12784 x 180 x 336 float32 is ~3 GB, doubled while predicting).
LAT_CHUNK = int(os.environ.get("MHW_ENSO_LAT_CHUNK", 20))

# %% [markdown]
# ## Fetch and parse the MEI
#
# Self-contained, like every other input here: no manual download step.

# %%
if MEI_PATH.exists():
    mei_monthly = pd.read_csv(MEI_PATH, index_col=0, parse_dates=True)["mei"]
    print(f"MEI: reusing {MEI_PATH}")
else:
    with urllib.request.urlopen(MEI_URL, timeout=60) as fh:
        html = fh.read().decode("utf-8", errors="replace")
    # Rows are: YEAR then 12 bimonthly values (DECJAN ... NOVDEC).
    rows = []
    for line in html.splitlines():
        m = re.match(r"^\s*(19|20)(\d{2})\s+((?:-?\.?\d[\d.]*\s*){12})$", line)
        if m:
            year = int(m.group(1) + m.group(2))
            vals = [float(v) for v in m.group(3).split()]
            rows.append((year, vals))
    if not rows:
        raise RuntimeError(f"could not parse any MEI rows from {MEI_URL}")

    # "we assumed the monthly values to be centred on the middle of second
    # month": DECJAN -> mid-January, JANFEB -> mid-February, ... NOVDEC -> mid-December.
    index, values = [], []
    for year, vals in rows:
        for month, v in enumerate(vals, start=1):
            index.append(pd.Timestamp(year=year, month=month, day=15))
            values.append(v)
    mei_monthly = pd.Series(values, index=pd.DatetimeIndex(index), name="mei").sort_index()
    MEI_PATH.parent.mkdir(parents=True, exist_ok=True)
    mei_monthly.to_frame().to_csv(MEI_PATH)
    print(f"MEI: parsed {len(mei_monthly)} bimonthly values "
          f"({mei_monthly.index[0].date()} .. {mei_monthly.index[-1].date()})")

# %% [markdown]
# ## Build the design matrix
#
# One column per monthly lead/lag of the MEI, each interpolated to the daily SST
# time axis, plus an intercept.

# %%
sst = xr.open_dataarray(IN_PATH)
time = pd.DatetimeIndex(sst.time.values)
print(f"SST: {dict(sst.sizes)}  {time[0].date()} .. {time[-1].date()}")

lags = range(-MAX_LAG_MONTHS, MAX_LAG_MONTHS + 1)
columns = []
for lag in lags:
    shifted = mei_monthly.copy()
    # A positive lag shifts the index FORWARD, so the MEI value from `lag`
    # months earlier lines up with the SST date being predicted.
    shifted.index = shifted.index + pd.DateOffset(months=lag)
    # Monthly -> daily by linear interpolation onto the SST time axis.
    col = shifted.reindex(shifted.index.union(time)).interpolate("time").reindex(time)
    columns.append(col.to_numpy(dtype="float64"))

X = np.column_stack([np.ones(len(time))] + columns)  # intercept first
n_pred = X.shape[1]
if not np.isfinite(X).all():
    bad = np.where(~np.isfinite(X).all(axis=1))[0]
    raise RuntimeError(
        f"design matrix has {len(bad)} non-finite row(s) — the MEI does not "
        f"cover {time[bad[0]].date()} .. {time[bad[-1]].date()} with ±"
        f"{MAX_LAG_MONTHS} months of padding"
    )
print(f"design matrix: {X.shape[0]} days x {n_pred} predictors "
      f"(intercept + {len(list(lags))} MEI lags {lags.start}..{lags.stop - 1})")

# Solve once: the design matrix is identical for every cell.
XtX_inv_Xt = np.linalg.solve(X.T @ X, X.T)  # (n_pred, n_time)

# %% [markdown]
# ## Remove the ENSO prediction, cell by cell
#
# The **intercept is deliberately retained**. We subtract only the MEI terms, so
# the mean and seasonal cycle survive untouched — detection in `03` then applies
# the *original* threshold to this series, which would detect nothing if the
# series had been recentred on zero.

# Each chunk is written to its own file as soon as it lands, then the files are
# streamed into one at the end — the same pattern 01 uses for the download
# bands, and for the same reason. Accumulating the chunks in memory instead
# holds the whole ~3 GB cube and then doubles it while diffing, which gets the
# process OOM-killed on a 15 GB machine. It also makes this resumable.

# %%
CHUNK_DIR = PROC_DIR / f"enso_chunks_{TARGET_RES_DEG:g}deg"
CHUNK_DIR.mkdir(parents=True, exist_ok=True)

n_lat = sst.sizes["latitude"]
chunk_paths, ss_removed, n_removed, max_removed = [], 0.0, 0, 0.0
for lat0 in range(0, n_lat, LAT_CHUNK):
    cpath = CHUNK_DIR / f"chunk_{lat0:05d}.nc"
    chunk_paths.append(cpath)
    if cpath.exists():
        print(f"  lat {lat0:3d}..{min(lat0 + LAT_CHUNK, n_lat):3d}  cached", flush=True)
        continue

    block = sst.isel(latitude=slice(lat0, lat0 + LAT_CHUNK)).load()
    arr = block.values.reshape(block.sizes["time"], -1).astype("float64")

    ocean = np.isfinite(arr).all(axis=0)
    resid = arr.copy()
    if ocean.any():
        beta = XtX_inv_Xt @ arr[:, ocean]              # (n_pred, n_ocean)
        enso = X[:, 1:] @ beta[1:, :]                  # MEI terms only
        resid[:, ocean] = arr[:, ocean] - enso
        # Accumulate diagnostics here; a whole-cube diff afterwards would need
        # another copy of the cube.
        ss_removed += float(np.sum(enso ** 2))
        n_removed += enso.size
        max_removed = max(max_removed, float(np.abs(enso).max()))

    out = block.copy(data=resid.reshape(block.shape).astype("float32"))
    out.name = "analysed_sst"
    tmp = cpath.with_suffix(".nc.tmp")
    out.to_netcdf(tmp, encoding={"analysed_sst": {"zlib": True, "complevel": 4}})
    os.replace(tmp, cpath)
    print(f"  lat {lat0:3d}..{min(lat0 + LAT_CHUNK, n_lat):3d}  "
          f"{ocean.sum():5d} ocean cells -> {cpath.name}", flush=True)
    del block, arr, resid, out

if n_removed:
    print(f"\nremoved ENSO signal: rms {np.sqrt(ss_removed / n_removed):.4f} degC, "
          f"max |.| {max_removed:.4f} degC")

# %% [markdown]
# ## Combine and save
#
# `open_mfdataset` keeps this lazy and `to_netcdf` streams it, so the full cube
# is never resident.

# %%
combined = xr.open_mfdataset(
    [str(p) for p in chunk_paths], combine="by_coords", engine="netcdf4"
)["analysed_sst"].sortby("latitude")
combined.attrs.update(
    description="SST with the linear MEI prediction removed (Oliver et al. 2018 Methods)",
    mei_source=MEI_URL,
    mei_lags_months=f"-{MAX_LAG_MONTHS}..+{MAX_LAG_MONTHS}",
    note="Intercept retained: only the MEI terms are subtracted, so the "
         "original climatology and threshold remain applicable.",
)
print("combined:", dict(combined.sizes))

tmp = OUT_PATH.with_suffix(".nc.tmp")
combined.to_netcdf(tmp, encoding={"analysed_sst": {"zlib": True, "complevel": 4}})
os.replace(tmp, OUT_PATH)
print(f"wrote {OUT_PATH}")
