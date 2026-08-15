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
# # 06 — Annual SST statistics
#
# Produces panels **d, e and f** of Oliver et al. (2018) Fig. 3: linear trends in
# annual **mean SST**, annual **SST variance** and annual **SST skewness**.
#
# These three panels exist in the paper to separate cause from effect. Panels
# a–c show trends in marine heatwave frequency, intensity and duration; d–f show
# trends in the underlying temperature distribution. If MHW trends were driven
# purely by the mean warming in panel d, they would carry no extra information —
# so the paper tests each MHW trend against what mean warming alone predicts.
# Variance and skewness matter because a distribution can shift (mean), widen
# (variance) or become more asymmetric (skewness), and each changes how often
# the 90th-percentile threshold is exceeded.
#
# Unlike a–c this is cheap: no MHW detection, just three moments per cell-year.
#
# Hatching in d–f marks trends significantly different from zero at 5%, which is
# computed here from the Theil–Sen confidence interval. (The hatching in a–c
# needs a Monte Carlo ensemble of synthetic MHW detections and is deliberately
# not attempted — see `docs/verification-checks.md`.)

# %%
import os
from pathlib import Path

import numpy as np
import xarray as xr

TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
LAT_CHUNK = int(os.environ.get("MHW_STATS_LAT_CHUNK", 30))

PROC_DIR = Path("../data/processed")
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

IN_PATH = PROC_DIR / f"sst_clean_{TARGET_RES_DEG:g}deg.nc"
OUT_PATH = RESULTS_DIR / f"sst_annual_stats_{TARGET_RES_DEG:g}deg.nc"

# %% [markdown]
# ## Compute the three moments per cell-year
#
# Chunked by latitude for the same reason as everywhere else here: the full cube
# is ~3 GB and holding it while deriving from it is what gets a process
# OOM-killed on this machine.

# %%
sst = xr.open_dataarray(IN_PATH)
years = np.unique(sst["time"].dt.year.values)
year_of = sst["time"].dt.year.values
n_lat = sst.sizes["latitude"]
print(f"input {dict(sst.sizes)}; {len(years)} years")

pieces = []
for lat0 in range(0, n_lat, LAT_CHUNK):
    block = sst.isel(latitude=slice(lat0, lat0 + LAT_CHUNK)).load()
    vals = block.values.astype("float64")  # (time, lat, lon)
    shape = (len(years),) + vals.shape[1:]
    mean_a = np.full(shape, np.nan)
    var_a = np.full(shape, np.nan)
    skew_a = np.full(shape, np.nan)

    # Variance and skewness are computed on the DESEASONALISED anomaly, the
    # mean on the raw SST. At mid-latitudes the seasonal cycle is ~95% of the
    # daily variance, so variance computed on raw SST measures the seasonal
    # amplitude and its trend measures how that amplitude is changing — not the
    # variability that governs threshold exceedance, which is what Fig. 3e is
    # about. The paper's own stochastic climate model removes the seasonal
    # climatology for the same reason.
    doy_all = block["time"].dt.dayofyear.values
    seasonal = np.full((366,) + vals.shape[1:], np.nan)
    for d in range(1, 367):
        sel = doy_all == d
        if sel.any():
            seasonal[d - 1] = np.nanmean(vals[sel], axis=0)
    anom_all = vals - seasonal[doy_all - 1]

    for i, y in enumerate(years):
        sel = year_of == y
        x = vals[sel]
        a = anom_all[sel]
        mu = np.nanmean(x, axis=0)
        dev = a - np.nanmean(a, axis=0)
        var = np.nanmean(dev ** 2, axis=0)
        # Fisher-Pearson skewness: m3 / sd**3. Guard the zero-variance case
        # (constant series) rather than emitting a divide warning and a NaN.
        sd = np.sqrt(var)
        with np.errstate(invalid="ignore", divide="ignore"):
            skew = np.where(sd > 0, np.nanmean(dev ** 3, axis=0) / sd ** 3, np.nan)
        mean_a[i], var_a[i], skew_a[i] = mu, var, skew

    coords = {"year": years, "latitude": block.latitude, "longitude": block.longitude}
    dims = ("year", "latitude", "longitude")
    pieces.append(xr.Dataset(
        {"sst_mean": (dims, mean_a),
         "sst_variance": (dims, var_a),
         "sst_skewness": (dims, skew_a)},
        coords=coords,
    ))
    print(f"  lat {lat0:3d}..{min(lat0 + LAT_CHUNK, n_lat):3d}", flush=True)

stats = xr.concat(pieces, dim="latitude").sortby("latitude")

# Restore the ocean mask: land cells are NaN in the input and must stay NaN.
valid = sst.isel(time=0).notnull()
stats = stats.where(valid)

stats["sst_mean"].attrs.update(units="degC", long_name="Annual mean SST")
stats["sst_variance"].attrs.update(
    units="degC2", long_name="Annual variance of deseasonalised SST")
stats["sst_skewness"].attrs.update(
    units="1", long_name="Annual skewness of deseasonalised SST")
stats.attrs.update(
    title="Annual SST moments from ESA SST CCI Analysis v3.0",
    replicates="10.1038/s41467-018-03732-9 Fig. 3d-f",
)

# %% [markdown]
# ## Sanity check
#
# Skewness is dimensionless and should sit within a few units of zero; variance
# is in degC^2 and strictly non-negative. Values far outside that mean the
# moments were computed over the wrong axis.

# %%
for name in ("sst_mean", "sst_variance", "sst_skewness"):
    a = stats[name].values
    print(f"  {name:14s} min {np.nanmin(a):8.3f}  median {np.nanmedian(a):8.3f}  "
          f"max {np.nanmax(a):8.3f}")
assert np.nanmin(stats["sst_variance"].values) >= 0, "negative variance"
assert np.nanmax(np.abs(stats["sst_skewness"].values)) < 20, "implausible skewness"

# %%
tmp = OUT_PATH.with_suffix(".nc.tmp")
stats.to_netcdf(tmp)
os.replace(tmp, OUT_PATH)
print(f"wrote {OUT_PATH}")
