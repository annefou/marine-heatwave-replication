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
# # 03 — Analysis
#
# Reproduces the headline satellite-era statistic of Oliver et al. (2018) on an
# independent SST record with an independent detection engine.
#
# **Claim under test** (Results, "Marine heatwaves over the satellite record"):
#
# > The increases in frequency and duration metrics translate to 30 additional
# > marine heatwave days per year by the end of the 35-year period (p < 0.01;
# > based on a linear trend) from a baseline level of about 25 days in the 1980s
# > (Fig. 2).
#
# ## Method alignment
#
# XMHW implements Hobday et al. (2016) — the same definition Oliver et al. used —
# and its defaults coincide exactly with the paper's stated parameters:
#
# | Paper | XMHW argument |
# |---|---|
# | 90th percentile threshold | `pctile=90` |
# | ≥ 5 consecutive days | `minDuration=5` |
# | breaks < 3 days merged | `joinGaps=True, maxGap=2` |
# | 11-day window for the percentile | `windowHalfWidth=5` |
# | 31-day moving average smoothing | `smoothPercentileWidth=31` |
# | 1983–2012 baseline climatology | `climatologyPeriod=[1983, 2012]` |
#
# So the *definition* is held fixed while the SST estimate and the codebase both
# change — which is what makes this a Replication rather than a Reproduction.
#
# ## Annual aggregation
#
# Following the paper, MHW **days** are attributed to the calendar year in which
# they fall, while **events** are attributed to the year the event started
# ("the duration and intensity are assigned to the start year of that event").

# %%
import json
import os
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from pathlib import Path

import numpy as np
import xarray as xr
from scipy import stats

warnings.filterwarnings("ignore", category=FutureWarning)

# %%
TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
# Memory per block is measured, not estimated. An earlier comment here guessed
# ~1.1 GB for a 2-row block; the real figure is ~4x that, and 6 workers on that
# assumption got OOM-killed on a 15 GB machine part-way through the stage.
#
# Measured on a full-ocean tropical block (scripts/probe_block.py 90 92 / 90 91):
#   LAT_BLOCK=2 -> 4.22 GB peak RSS, 436 s
#   LAT_BLOCK=1 -> 1.88 GB peak RSS, 210 s
# Peak scales with the block's valid-cell count, because XMHW's intermediate
# dataset holds ~15 time-length arrays over the stacked cells. Time is ~0.78 s
# per ocean cell either way, so narrow blocks cost throughput nothing and buy
# the headroom: at 1° there are ~30.8k ocean cells, i.e. ~6.7 core-hours.
#
# N_WORKERS x per-block peak must fit in RAM: 5 x 1.88 GB = 9.4 GB, which leaves
# room on a 15 GB machine. Re-probe before raising it on different hardware.
LAT_BLOCK = int(os.environ.get("MHW_LAT_BLOCK", 1))
N_WORKERS = int(os.environ.get("MHW_WORKERS", 5))
CLIM_PERIOD = [1983, 2012]

PROC_DIR = Path("../data/processed")
RESULTS_DIR = Path("../results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

IN_PATH = PROC_DIR / f"sst_clean_{TARGET_RES_DEG:g}deg.nc"
OUT_PATH = RESULTS_DIR / f"mhw_annual_{TARGET_RES_DEG:g}deg.nc"
SUMMARY_PATH = RESULTS_DIR / "headline_comparison.json"
# Per-block checkpoints. This stage is many core-hours; without them an OOM kill
# or a lost session throws away every finished block. Same atomic-rename pattern
# as the download bands in 01.
BLOCK_DIR = RESULTS_DIR / f"blocks_{TARGET_RES_DEG:g}deg"
BLOCK_DIR.mkdir(parents=True, exist_ok=True)
# A block with no ocean cells has no output to cache, so record it as an empty
# marker file rather than recomputing the (fast) land test on every resume.
EMPTY = ".empty"


# %% [markdown]
# ## Per-block MHW detection
#
# Each worker re-opens the file and takes its own latitude slice, so only small
# arrays cross the process boundary. Blocks are kept narrow because XMHW's
# intermediate dataset holds ~15 time-length arrays, and that — not the input —
# sets peak memory.

# %%
def block_path(lat0: int) -> Path:
    return BLOCK_DIR / f"block_{lat0:05d}.nc"


def run_block(args):
    """Detect MHWs for one latitude block; return annual per-cell statistics.

    Writes its result to a per-block checkpoint and reuses it on resume, so a
    killed run only loses the blocks that were in flight.
    """
    path, lat0, lat1 = args
    out_path = block_path(lat0)
    if out_path.exists():
        with xr.open_dataset(out_path) as ds:
            return ds.load()
    if out_path.with_suffix(EMPTY).exists():
        return None

    from xmhw.xmhw import detect, threshold  # imported in the worker

    sst = xr.open_dataarray(path).isel(latitude=slice(lat0, lat1)).load()

    # Skip blocks that are entirely land/masked.
    if not bool(sst.notnull().any()):
        out_path.with_suffix(EMPTY).touch()
        return None

    clim = threshold(sst, climatologyPeriod=CLIM_PERIOD).compute()
    _, inter = detect(sst, clim.thresh, clim.seas, intermediate=True)
    inter = inter.compute()

    is_day = inter["events"].notnull()
    # An event starts on a day that is in an event and follows a day that is not.
    prev = is_day.shift(time=1)
    prev = prev.where(prev.notnull(), False).astype(bool)
    is_start = is_day & (~prev)

    days = is_day.groupby("time.year").sum("time")
    events = is_start.groupby("time.year").sum("time")

    out = xr.Dataset({"mhw_days": days, "mhw_events": events})
    # Restore the mask: cells XMHW dropped as land come back as NaN, not 0.
    valid = sst.notnull().any("time")
    out = out.where(valid)

    # Write then rename, so a kill mid-write cannot leave a truncated file that
    # resume would mistake for a finished block.
    tmp = out_path.with_suffix(".nc.tmp")
    out.to_netcdf(tmp)
    os.replace(tmp, out_path)
    return out


# %% [markdown]
# ## Run

# %%
if __name__ == "__main__":
    sst_meta = xr.open_dataarray(IN_PATH)
    n_lat = sst_meta.sizes["latitude"]
    print(f"input: {dict(sst_meta.sizes)}")
    blocks = [
        (str(IN_PATH), i, min(i + LAT_BLOCK, n_lat))
        for i in range(0, n_lat, LAT_BLOCK)
    ]
    cached = sum(
        1 for _, lat0, _ in blocks
        if block_path(lat0).exists() or block_path(lat0).with_suffix(EMPTY).exists()
    )
    print(f"{len(blocks)} latitude block(s) x {LAT_BLOCK} rows, {N_WORKERS} workers"
          f"{f' ({cached} cached)' if cached else ''}")

    t0 = time.time()
    results = []
    n_computed = 0  # blocks actually detected in this run, excluding resumed ones
    failed = []
    # submit/as_completed rather than map: one block that dies (an OOM kill takes
    # the whole pool down with BrokenProcessPool) must not discard the blocks that
    # finished. Their checkpoints are already on disk either way, but this also
    # lets the run report exactly which blocks still need doing.
    with ProcessPoolExecutor(max_workers=N_WORKERS) as pool:
        futures = {pool.submit(run_block, b): b for b in blocks}
        try:
            for i, fut in enumerate(as_completed(futures), 1):
                _, lat0, _ = futures[fut]
                try:
                    res = fut.result()
                except Exception as exc:  # noqa: BLE001 — report, don't abort
                    failed.append((lat0, repr(exc)))
                    print(f"  block {lat0}: FAILED {exc!r}", flush=True)
                    continue
                if res is not None:
                    results.append(res)
                if not block_path(lat0).with_suffix(EMPTY).exists():
                    n_computed += 1
                if i % 5 == 0 or i == len(blocks):
                    el = (time.time() - t0) / 60
                    # Rate is per *computed* block; resumed ones cost ~0 s and
                    # would otherwise make the ETA far too optimistic.
                    rate = el / max(n_computed, 1)
                    eta = rate * (len(blocks) - i)
                    print(f"  [{i}/{len(blocks)}] elapsed {el:5.1f} min, "
                          f"ETA {eta:5.1f} min", flush=True)
        except BrokenProcessPool:
            print("pool died (likely an OOM kill). Finished blocks are "
                  "checkpointed in "
                  f"{BLOCK_DIR}; re-run to resume, with a lower MHW_WORKERS.",
                  flush=True)
            raise

    if failed:
        raise RuntimeError(
            f"{len(failed)} block(s) failed: {failed[:5]}"
            + (" ..." if len(failed) > 5 else "")
        )

    annual = xr.concat(results, dim="latitude").sortby("latitude")
    print("annual stats:", dict(annual.sizes))

    # %% [markdown]
    # ## Globally averaged series
    #
    # Area-weighted by cos(latitude), as in the paper.

    # %%
    weights = np.cos(np.deg2rad(annual.latitude))
    gmean = annual.weighted(weights).mean(dim=["latitude", "longitude"])
    years = gmean.year.values.astype(float)
    days = gmean["mhw_days"].values
    events = gmean["mhw_events"].values
    duration = np.divide(days, events, out=np.full_like(days, np.nan),
                         where=events > 0)

    # %% [markdown]
    # ## Trends
    #
    # Theil–Sen with a 95% confidence interval, as the paper specifies for the
    # globally averaged series ("more robust for time series data that are
    # heteroskedastic or have a skewed distribution").

    # %%
    def theil_sen(y, x=years):
        ok = np.isfinite(y)
        slope, intercept, lo, hi = stats.theilslopes(y[ok], x[ok], alpha=0.95)
        # Significant at the 5% level when the CI excludes zero.
        return {
            "slope_per_year": float(slope),
            "slope_per_decade": float(slope * 10),
            "ci_low_per_decade": float(lo * 10),
            "ci_high_per_decade": float(hi * 10),
            "significant_5pct": bool(lo > 0 or hi < 0),
            "intercept": float(intercept),
        }

    tr_days = theil_sen(days)
    tr_events = theil_sen(events)
    tr_duration = theil_sen(duration)

    n_years = years[-1] - years[0]
    change_over_record = tr_days["slope_per_year"] * n_years
    baseline_1980s = float(np.nanmean(days[years <= 1989]))

    # %% [markdown]
    # ## Headline comparison

    # %%
    comparison = {
        "replication": {
            "dataset": "ESA SST CCI Analysis v3.0",
            "dataset_doi": "10.5285/4a9654136a7148e39b7feb56f8bb02d2",
            "software": "XMHW",
            "software_doi": "10.5281/zenodo.7662469",
            "resolution_deg": TARGET_RES_DEG,
            "period": [int(years[0]), int(years[-1])],
            "climatology_period": CLIM_PERIOD,
            "n_cells": int(annual["mhw_days"].isel(year=0).notnull().sum()),
        },
        "mhw_days": {
            "original_change_over_record": 30.0,
            "original_baseline_1980s": 25.0,
            "replication_change_over_record": round(change_over_record, 2),
            "replication_baseline_1980s": round(baseline_1980s, 2),
            "replication_trend_per_decade": round(tr_days["slope_per_decade"], 3),
            "replication_significant_5pct": tr_days["significant_5pct"],
            "replication_ci_per_decade": [
                round(tr_days["ci_low_per_decade"], 3),
                round(tr_days["ci_high_per_decade"], 3),
            ],
        },
        "mhw_frequency": {
            "original_trend_per_decade": 0.45,
            "replication_trend_per_decade": round(tr_events["slope_per_decade"], 3),
            "replication_significant_5pct": tr_events["significant_5pct"],
        },
        "mhw_duration": {
            "original_trend_per_decade": 1.3,
            "replication_trend_per_decade": round(tr_duration["slope_per_decade"], 3),
            "replication_significant_5pct": tr_duration["significant_5pct"],
        },
    }

    print(json.dumps(comparison, indent=2))
    with open(SUMMARY_PATH, "w") as f:
        json.dump(comparison, f, indent=2)

    # %% [markdown]
    # ## Save

    # %%
    gseries = xr.Dataset(
        {
            "mhw_days": ("year", days),
            "mhw_events": ("year", events),
            "mhw_duration": ("year", duration),
        },
        coords={"year": gmean.year.values},
    )
    out = annual.merge(gseries.rename({v: f"global_{v}" for v in gseries.data_vars}))
    out.attrs.update(
        title="Annual marine heatwave statistics from ESA SST CCI Analysis v3.0",
        detection_software="XMHW (Hobday et al. 2016 definition)",
        climatology_period=f"{CLIM_PERIOD[0]}-{CLIM_PERIOD[1]}",
        replicates="10.1038/s41467-018-03732-9 Fig. 2",
    )
    out.to_netcdf(OUT_PATH)
    print(f"wrote {OUT_PATH} and {SUMMARY_PATH}")
