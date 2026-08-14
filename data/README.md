# `data/` — downloaded artefacts, never committed

This directory holds the raw and cleaned datasets used by the replication pipeline. **Files in this directory are never committed to git** (`.gitignore` excludes everything except this README).

## Why download-on-first-run

Every replication must be self-contained: a user clones the repo and runs `snakemake --cores 1` (or executes notebook 01 directly), and the code fetches its own input data. No "ask the author for the dataset" steps; no folder-of-CSVs that drift out of sync with the analysis.

## What this replication uses

Two inputs, both fetched automatically.

### 1. ESA SST CCI Analysis v3.0 — the independent SST record

| | |
|---|---|
| **DOI** | [10.5285/4a9654136a7148e39b7feb56f8bb02d2](https://doi.org/10.5285/4a9654136a7148e39b7feb56f8bb02d2) |
| **Accessed via** | Copernicus Marine Service ARCO/Zarr store, dataset ID `ESACCI-GLO-SST-L4-REP-OBS-SST` |
| **Fetched by** | `notebooks/01_data_download.py` (`copernicusmarine`) |
| **Credentials** | Free account at <https://data.marine.copernicus.eu/register> |
| **Period / grid** | 1982-01-01 – 2016-12-31, native 0.05°, averaged to 1° in flight |
| **Licence** | Copernicus Marine Service licence (free reuse with attribution) |

This is the *independent* half of the replication: Oliver et al. used NOAA OISST
and HadISST, so a different observational basis is what makes this a Replication
rather than a Reproduction.

**Why CMEMS and not CEDA.** CEDA is the archive of record and openly
downloadable, but as daily files — ~16.6 MB/day, ~212 GB for the full record.
CMEMS redistributes the *same product* as an ARCO/Zarr store supporting lazy
chunked reads, so `01` averages 0.05° → 1° **while streaming** and keeps only
575 MB of coarsened bands. Same data, tractable access.

> **Do not substitute `C3S-GLO-SST-L4-REP-OBS-SST`.** It sits in the same CMEMS
> product family but is the Climate Change Service variant, not the ESA CCI one
> this replication cites. Swapping it would leave the DOI above pointing at data
> that was not used.

### 2. Multivariate ENSO Index (MEI) — for the Fig. 2 ENSO-removed series

| | |
|---|---|
| **Source** | <https://psl.noaa.gov/enso/mei.old/table.html> (Wolter & Timlin) |
| **Fetched by** | `notebooks/05_enso_removal.py`, cached to `data/raw/mei_original.csv` |
| **Coverage** | Bimonthly, 1950 – 2018 |

The **original** MEI is used, not NOAA's maintained MEI.v2 successor: it is the
index the paper cites, and its final update (Dec 2018) postdates the paper, so
it is effectively the data the authors had. MEI.v2 uses a different variable set
and base period. This is recorded as a deviation in `05_enso_removal.py`.

## What lands where

| Path | Produced by | Size | Committed? |
|---|---|---|---|
| `raw/bands_1deg/` | 01 | ~575 MB | no (resume cache) |
| `raw/sst_cci_1deg_stride1.nc` | 01 | ~1 GB | no |
| `raw/mei_original.csv` | 05 | 14 KB | no (re-fetched) |
| `processed/sst_clean_1deg.nc` | 02 | ~956 MB | no |
| `processed/enso_chunks_1deg/` | 05 | ~3 GB | no (resume cache) |
| `processed/sst_enso_removed_1deg.nc` | 05 | ~3 GB | no |

Budget ~5 GB. Everything here is regenerable from the two sources above.

## Required credentials

If your replication uses a credentialled API, document the credential setup at the top of `notebooks/01_data_download.py`, including:

- Where the user gets the credential (URL).
- Where it lives on disk (or which env var Claude expects).
- The corresponding GitHub Actions secret name(s) for CI.

## CI cache

Large downloads (>100 MB) should be cached in GitHub Actions via `actions/cache@v4`. See `.github/workflows/ci.yml` for the pattern.
