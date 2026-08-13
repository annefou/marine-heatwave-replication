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
# # 01 — Data download
#
# Fetches the independent SST record for the replication: **ESA SST CCI Analysis
# v3.0** (Good & Embury 2024), DOI
# [10.5285/4a9654136a7148e39b7feb56f8bb02d2](https://doi.org/10.5285/4a9654136a7148e39b7feb56f8bb02d2).
#
# This is the *independent data* half of the replication. Oliver et al. (2018)
# ran their satellite-era analysis on NOAA OI SST V2; SST_cci is produced by
# ESA CCI / UK Met Office with an independent optimal-estimation retrieval over
# (A)ATSR, AVHRR and SLSTR — a separate estimate of the same field, not a
# re-version of the same pipeline.
#
# ## Why Copernicus Marine and not the CEDA archive
#
# The dataset of record lives at CEDA, and its files are openly downloadable at
# `dap.ceda.ac.uk/neodc/eocis/...` (~16.6 MB/day, so ~212 GB for 1982–2016).
# The Copernicus Marine Service redistributes the same ESA SST CCI Analysis v3.0
# as an **ARCO/Zarr** store (`ESACCI-GLO-SST-L4-REP-OBS-SST`), which supports
# lazy chunked reads. That lets us average to the target grid *while streaming*
# instead of mirroring 212 GB of daily files. Same product, better access path.
#
# > CMEMS also carries a `C3S-GLO-SST-L4-REP-OBS-SST` dataset in the same
# > product. That is the Copernicus Climate Change Service variant — **not** the
# > ESA CCI one this replication cites. Do not swap them.
#
# **Credentials.** Copernicus Marine account (free) at
# <https://data.marine.copernicus.eu/register>. `copernicusmarine login` writes
# `~/.copernicusmarine/.copernicusmarine-credentials`.
# In CI, set COPERNICUSMARINE_SERVICE_USERNAME / _PASSWORD instead — the library
# checks those before any config file, and `login` prompts and would hang —
# see `DOMAIN.md` § Copernicus credentials in CI.

# %%
import json
import os
import time
from pathlib import Path

import copernicusmarine as cm
import numpy as np
import xarray as xr

# %% [markdown]
# ## Configuration
#
# `TARGET_RES_DEG` sets the analysis grid. Oliver et al. worked on the 0.25°
# NOAA OISST grid; we **area-average** native 0.05° cells up to the target
# rather than point-sampling them, so each analysis cell is an areal mean like
# an OISST cell rather than a single sub-pixel value.
#
# `LON_BAND_STRIDE` controls how much of the globe is read. The Zarr store is
# chunked 64 cells wide in longitude, so bands are taken on those boundaries to
# avoid reading a chunk to keep a sliver of it.
#
# * `1` → every band → true global coverage, ~2.65 TB decoded (~10 h transfer).
# * `8` → every 8th band → 14 bands, 12.5% of longitudes (**default**).
#
# A longitude-band sample is an unbiased estimator of an area-weighted global
# mean, but it is a **declared deviation** from the paper's full-field analysis
# and must be reported as such in the Outcome. Set `MHW_LON_BAND_STRIDE=1` for
# the full-coverage run.

# %%
# Matches Oliver et al.'s satellite record. MHW_PERIOD_END exists only to smoke-test
# the pipeline cheaply; a real run must leave it unset so the full record is used.
PERIOD = ("1982-01-01", os.environ.get("MHW_PERIOD_END", "2016-12-31"))
TARGET_RES_DEG = float(os.environ.get("MHW_TARGET_RES_DEG", 1.0))
LON_BAND_STRIDE = int(os.environ.get("MHW_LON_BAND_STRIDE", 8))

DATASET_ID = "ESACCI-GLO-SST-L4-REP-OBS-SST"
NATIVE_RES_DEG = 0.05
COARSEN = int(round(TARGET_RES_DEG / NATIVE_RES_DEG))  # 20 for 1.0 deg
LON_CHUNK = 64  # longitude chunk width of the ARCO store
BAND_WIDTH = (LON_CHUNK // COARSEN) * COARSEN  # largest multiple of COARSEN that fits

RAW_DIR = Path("../data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = RAW_DIR / f"sst_cci_{TARGET_RES_DEG:g}deg_stride{LON_BAND_STRIDE}.nc"

print(f"target grid   : {TARGET_RES_DEG}° (coarsen {COARSEN}x{COARSEN} native cells)")
print(f"band stride   : {LON_BAND_STRIDE} chunk(s); band width {BAND_WIDTH}/{LON_CHUNK} cells")
print(f"period        : {PERIOD[0]} .. {PERIOD[1]}")
print(f"output        : {OUT_PATH}")

# %% [markdown]
# ## Open the ARCO store (lazy)

# %%
ds = cm.open_dataset(
    dataset_id=DATASET_ID,
    variables=["analysed_sst"],
    service="arco-time-series",
)
sst_all = ds["analysed_sst"].sel(time=slice(*PERIOD))
n_time, n_lat, n_lon = sst_all.shape
print(f"native cube: time={n_time}, lat={n_lat}, lon={n_lon}")

band_starts = list(range(0, n_lon - BAND_WIDTH + 1, LON_CHUNK * LON_BAND_STRIDE))
print(f"{len(band_starts)} longitude band(s) -> "
      f"{len(band_starts) * BAND_WIDTH // COARSEN} analysis columns")

# %% [markdown]
# ## Stream each band and average to the target grid
#
# A single band at native resolution is ~23 GB, so it is never materialised.
# We rechunk to bounded blocks, let dask stream them, and keep only the
# coarsened result (a few tens of MB per band).

# %%
def fetch_band(start: int) -> xr.DataArray:
    """Read one longitude band lazily and area-average it to the target grid."""
    band = sst_all.isel(longitude=slice(start, start + BAND_WIDTH))
    # Bounded blocks: 1056 x 400 x BAND_WIDTH x 8 B ~= 216 MB per task.
    band = band.chunk({"time": 1056, "latitude": 400, "longitude": BAND_WIDTH})
    coarse = band.coarsen(
        latitude=COARSEN, longitude=COARSEN, boundary="trim"
    ).mean()
    return coarse.astype("float32")


# Each band is written to its own file as soon as it lands. At full global
# coverage the in-memory alternative would hold ~3 GB of bands and then double
# that during concat; this keeps peak memory flat and makes the download
# resumable — a band whose file already exists is skipped on re-run.
BAND_DIR = RAW_DIR / f"bands_{TARGET_RES_DEG:g}deg"
BAND_DIR.mkdir(parents=True, exist_ok=True)

t_start = time.time()
band_paths = []
n_fetched = 0  # bands actually downloaded in this run, excluding resumed ones
for i, start in enumerate(band_starts, 1):
    band_path = BAND_DIR / f"band_{start:05d}.nc"
    band_paths.append(band_path)
    if band_path.exists():
        print(f"[{i}/{len(band_starts)}] {band_path.name} exists — skipping", flush=True)
        continue
    t0 = time.time()
    band = fetch_band(start).compute(scheduler="threads", num_workers=4)
    band.name = "analysed_sst"
    # Write to a temp name and rename atomically. If the process is killed
    # mid-write, resume must not mistake a truncated file for a finished band.
    tmp_path = band_path.with_suffix(".nc.tmp")
    band.to_netcdf(tmp_path, encoding={"analysed_sst": {"zlib": True, "complevel": 4}})
    os.replace(tmp_path, band_path)
    lon0, lon1 = float(band.longitude[0]), float(band.longitude[-1])
    n_fetched += 1
    total = len(band_starts)
    # Rate is per *fetched* band; bands skipped on resume cost ~0 s and would
    # otherwise make the ETA far too optimistic.
    remaining = sum(
        1 for s in band_starts[i:] if not (BAND_DIR / f"band_{s:05d}.nc").exists()
    )
    eta = (time.time() - t_start) / n_fetched * remaining / 60
    print(
        f"[{i}/{total}] lon {lon0:8.2f}..{lon1:8.2f}  "
        f"shape={tuple(band.shape)}  {time.time() - t0:5.0f}s  "
        f"(elapsed {(time.time() - t_start) / 60:5.1f} min, "
        f"{remaining} left, ETA {eta:5.1f} min)",
        flush=True,
    )
    del band

sst = xr.open_mfdataset(
    [str(p) for p in band_paths], combine="by_coords", engine="netcdf4"
)["analysed_sst"].sortby("longitude")
print("assembled:", dict(sst.sizes))

# %% [markdown]
# ## Save
#
# NetCDF with CF-style attributes — self-describing, language-agnostic, and the
# format `DOMAIN.md` mandates over `.npz` for intermediate arrays.

# %%
sst.name = "analysed_sst"
sst.attrs.update(
    units="kelvin",
    long_name="Analysed sea surface temperature, area-averaged to target grid",
    source_dataset=DATASET_ID,
    source_doi="10.5285/4a9654136a7148e39b7feb56f8bb02d2",
    source_product="SST_GLO_SST_L4_REP_OBSERVATIONS_010_024",
    native_resolution_deg=NATIVE_RES_DEG,
    target_resolution_deg=TARGET_RES_DEG,
    aggregation="area mean over %dx%d native cells" % (COARSEN, COARSEN),
    lon_band_stride=LON_BAND_STRIDE,
    period_start=PERIOD[0],
    period_end=PERIOD[1],
)
encoding = {"analysed_sst": {"zlib": True, "complevel": 4, "dtype": "float32"}}
sst.to_netcdf(OUT_PATH, encoding=encoding)
print(f"wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1e6:.0f} MB)")

# %% [markdown]
# ## Source log

# %%
SOURCES = [
    {
        "name": "ESA SST CCI Analysis v3.0 (Level 4, global, daily)",
        "doi": "10.5285/4a9654136a7148e39b7feb56f8bb02d2",
        "url": "https://data.marine.copernicus.eu/product/SST_GLO_SST_L4_REP_OBSERVATIONS_010_024",
        "dataset_id": DATASET_ID,
        "access_route": "Copernicus Marine ARCO (arco-time-series); "
                        "dataset of record archived at CEDA",
        "license": "Copernicus Marine Service / ESA CCI open licence",
        "accessed_on": time.strftime("%Y-%m-%d"),
        "period": list(PERIOD),
        "target_resolution_deg": TARGET_RES_DEG,
        "lon_band_stride": LON_BAND_STRIDE,
        "n_bands": len(band_starts),
    },
]
with open(RAW_DIR / "sources.json", "w") as f:
    json.dump({"sources": SOURCES}, f, indent=2)
print(f"Logged {len(SOURCES)} source(s) to {RAW_DIR / 'sources.json'}")
