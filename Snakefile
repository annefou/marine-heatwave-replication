# Snakefile — orchestrates the replication pipeline end-to-end.
#
# One rule per pipeline stage; each rule wraps a notebook executed via jupytext,
# so the notebook stays the source of truth and the Snakefile just sequences them.
#
# Usage:
#   snakemake --cores 1                  # run everything
#   snakemake --cores 1 -n               # dry run
#
# Runtime is dominated by two stages and both are long (measured on 8 cores /
# 15 GB, 1° global):
#   01_data_download  ~55 min  (streams ~2.65 TB decoded from the CMEMS ARCO store)
#   03_analysis       ~1.3 h   (~6.7 core-hours of MHW detection, 5 workers)
# Both resume: 01 skips bands already in data/raw/bands_<res>deg/, 03 skips
# latitude blocks already in results/blocks_<res>deg/.
# Configure with environment variables — see the notebook headers:
#   MHW_TARGET_RES_DEG (default 1.0)   analysis grid
#   MHW_LON_BAND_STRIDE (default 1)    1 = full global coverage
#   MHW_WORKERS / MHW_LAT_BLOCK        parallelism vs memory in 03
# MHW_WORKERS x per-block peak RSS must fit in RAM, or the pool is OOM-killed:
# measure with `pixi run python scripts/probe_block.py 90 91` before raising it.

import os

NOTEBOOKS = "notebooks"
DATA = "data"
RESULTS = "results"
FIGURES = "figures"

RES = os.environ.get("MHW_TARGET_RES_DEG", "1")
RES = f"{float(RES):g}"
STRIDE = os.environ.get("MHW_LON_BAND_STRIDE", "1")

RAW_SST = f"{DATA}/raw/sst_cci_{RES}deg_stride{STRIDE}.nc"
CLEAN_SST = f"{DATA}/processed/sst_clean_{RES}deg.nc"
# Only the full configuration produces the reported result, so only it claims
# the canonical artefact names. Any partial/smoke run writes self-describing
# files instead (and a watermarked figure), so it can never overwrite the
# numbers the FORRT Outcome quotes. Keep in step with 03_analysis.py and
# 04_figures.py: if these names change, change them there too.
PERIOD_END = os.environ.get("MHW_PERIOD_END", "2016-12-31")
IS_FULL_REPLICATION = (RES, STRIDE, PERIOD_END) == ("1", "1", "2016-12-31")
_TAG = f"partial_run_{RES}deg_stride{STRIDE}"

ANNUAL = (
    f"{RESULTS}/mhw_annual_{RES}deg.nc" if IS_FULL_REPLICATION
    else f"{RESULTS}/{_TAG}_annual.nc"
)
COMPARISON = (
    f"{RESULTS}/headline_comparison.json" if IS_FULL_REPLICATION
    else f"{RESULTS}/{_TAG}_comparison.json"
)
MAIN_FIG = (
    f"{FIGURES}/main_result.png" if IS_FULL_REPLICATION
    else f"{FIGURES}/{_TAG}.png"
)


# ENSO-removed branch: reproduces the red line of the paper's Fig. 2. Only
# meaningful for the full configuration — a coarse smoke run has no business
# regressing on the MEI — so it is requested only when IS_FULL_REPLICATION.
ENSO_SST = f"{DATA}/processed/sst_enso_removed_{RES}deg.nc"
ENSO_ANNUAL = f"{RESULTS}/mhw_annual_{RES}deg_enso_removed.nc"
ENSO_COMPARISON = f"{RESULTS}/headline_comparison_enso_removed.json"


rule all:
    input:
        [MAIN_FIG, COMPARISON]
        + ([ENSO_ANNUAL, ENSO_COMPARISON] if IS_FULL_REPLICATION else []),


# ---------- 01: Data download ----------
# Self-contained: the notebook fetches ESA SST CCI Analysis v3.0 from the
# Copernicus Marine ARCO store. Needs a Copernicus Marine account — see the
# notebook header and DOMAIN.md § Copernicus credentials in CI.
# Resumable: bands already present in data/raw/bands_<res>deg/ are skipped.
rule data_download:
    output:
        RAW_SST,
    log:
        f"{RESULTS}/logs/01_data_download.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 01_data_download.py 2>&1 | tee ../{log}"


# ---------- 02: Data clean ----------
rule data_clean:
    input:
        RAW_SST,
    output:
        CLEAN_SST,
    log:
        f"{RESULTS}/logs/02_data_clean.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 02_data_clean.py 2>&1 | tee ../{log}"


# ---------- 03: Analysis ----------
rule analysis:
    input:
        CLEAN_SST,
    output:
        ANNUAL,
        COMPARISON,
    log:
        f"{RESULTS}/logs/03_analysis.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 03_analysis.py 2>&1 | tee ../{log}"


# ---------- 05: ENSO removal ----------
# Regresses daily SST onto the MEI (monthly leads/lags to ±1 year) and subtracts
# the MEI terms, leaving the mean and seasonal cycle intact. Resumable: latitude
# chunks already in data/processed/enso_chunks_<res>deg/ are skipped.
rule enso_removal:
    input:
        CLEAN_SST,
    output:
        ENSO_SST,
    log:
        f"{RESULTS}/logs/05_enso_removal.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 05_enso_removal.py 2>&1 | tee ../{log}"


# ---------- 03b: Analysis on the ENSO-removed series ----------
# Same notebook as `analysis`, with MHW_ENSO_REMOVED=1: it detects on the
# ENSO-less series while taking the climatology and threshold from the ORIGINAL
# SST, so it needs both files as input. Outputs are suffixed, so this rule and
# `analysis` never contend for the same paths.
rule analysis_enso:
    input:
        ENSO_SST,
        CLEAN_SST,
    output:
        ENSO_ANNUAL,
        ENSO_COMPARISON,
    log:
        f"{RESULTS}/logs/03_analysis_enso.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "MHW_ENSO_REMOVED=1 jupytext --to notebook --execute "
        "--output ../{RESULTS}/logs/03_analysis_enso.ipynb 03_analysis.py "
        "2>&1 | tee ../{log}"


# ---------- 04: Figures ----------
rule figures:
    input:
        ANNUAL,
        COMPARISON,
    output:
        MAIN_FIG,
    log:
        f"{RESULTS}/logs/04_figures.log",
    shell:
        "mkdir -p {RESULTS}/logs && cd {NOTEBOOKS} && "
        "jupytext --to notebook --execute 04_figures.py 2>&1 | tee ../{log}"
