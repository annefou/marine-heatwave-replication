# Snakefile — orchestrates the replication pipeline end-to-end.
#
# One rule per pipeline stage; each rule wraps a notebook executed via jupytext,
# so the notebook stays the source of truth and the Snakefile just sequences them.
#
# Usage:
#   snakemake --cores 1                  # run everything
#   snakemake --cores 1 -n               # dry run
#
# Runtime is dominated by two stages and both are long:
#   01_data_download  ~1 h   (streams ~2.65 TB decoded from the CMEMS ARCO store)
#   03_analysis       ~3 h   (~16 core-hours of MHW detection, 6 workers)
# Configure with environment variables — see the notebook headers:
#   MHW_TARGET_RES_DEG (default 1.0)   analysis grid
#   MHW_LON_BAND_STRIDE (default 1)    1 = full global coverage
#   MHW_WORKERS / MHW_LAT_BLOCK        parallelism vs memory in 03

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
ANNUAL = f"{RESULTS}/mhw_annual_{RES}deg.nc"
COMPARISON = f"{RESULTS}/headline_comparison.json"
MAIN_FIG = f"{FIGURES}/main_result.png"


rule all:
    input:
        MAIN_FIG,
        COMPARISON,


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
