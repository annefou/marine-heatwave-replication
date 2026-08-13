# Paper summary

> This is a working scratchpad for the paper-analysis phase. The output of this file feeds the Quote / AIDA / Claim drafts. It is not itself a nanopub.

**Reference paper:** Longer and more frequent marine heatwaves over the past century

**DOI:** 10.1038/s41467-018-03732-9

**Authors:** Eric C. J. Oliver, Markus G. Donat, Michael T. Burrows, Pippa J. Moore, Dan A. Smale, Lisa V. Alexander, Jessica A. Benthuysen, Ming Feng, Alex Sen Gupta, Alistair J. Hobday, Neil J. Holbrook, Sarah E. Perkins-Kirkpatrick, Hillary A. Scannell, Sandra C. Straub, Thomas Wernberg

**Year:** 2018 (Nature Communications 9:1324)

## Headline claim

The sentence this replication tests — the paper's **satellite-era** result for total marine
heatwave days, which is what Figure 2 plots:

> The increases in frequency and duration metrics translate to 30 additional marine heatwave days per year by the end of the 35-year period (p < 0.01; based on a linear trend) from a baseline level of about 25 days in the 1980s (Fig. 2).

Verified verbatim against `paper/oliver-2018.pdf` (Results, "Marine heatwaves over the
satellite record"). 235 characters.

### Why not the abstract's "54%" sentence

The paper's most-quoted sentence is the abstract's:

> We find that from 1925 to 2016, global average marine heatwave frequency and duration increased by 34% and 17%, respectively, resulting in a 54% increase in annual marine heatwave days globally.

**This is not a satellite-era result and cannot be tested on any satellite SST record.**
Tracing the three percentages to their source in the Results:

| Figure | Number | Data | Period |
|---|---|---|---|
| 5b | +0.78 annual events = **34%** | monthly gridded proxy | 1925–1954 vs 1987–2016 |
| 5d | +1.8 days = **17%** | monthly gridded proxy | 1925–1954 vs 1987–2016 |
| 5f | +14 days on a 26-day baseline = **54%** | monthly gridded proxy | 1925–1954 vs 1987–2016 |
| **2** | **+30 days/yr, ~25-day baseline** | **daily NOAA OI SST v2** | **1982–2016** |

The 34/17/54% figures come from a *proxy reconstruction*: monthly SST from five gridded
products (HadISST v1.1, ERSST v5, COBE 2, CERA-20C, SODA si.3), with generalised linear
models trained on the six century-long daily station records to predict annual MHW
frequency and duration from monthly statistics. They are also a **difference between two
30-year periods**, not a trend "from 1925 to 2016" as the abstract's phrasing suggests.
No satellite SST product reaches before ~1981, so ESA SST_cci cannot address them.

Figure 2 is the paper's own daily-satellite statement of the same quantity (total annual
MHW days, globally averaged) and is fully within SST_cci's coverage. Anchoring the chain
there keeps the Quote, the Claim, and the Outcome about the *same* measurement.

## Methodology summary

- **Data sources.** Three independent strands. (i) Daily NOAA OI SST V2 high-resolution,
  AVHRR-derived, 0.25°×0.25° global grid, 1982–2016 — the source for Figs. 1–3 and the
  claim under test. (ii) Daily in situ records from six century-scale coastal stations
  (Pacific Grove, Scripps Pier, Newport Beach, Arendal, Port Erin, Race Rocks; 89–111
  years each). (iii) Five monthly gridded SST products for the 1900–2016 proxy
  reconstruction.
- **MHW definition.** Hobday et al. (2016) standard: SST above a seasonally varying 90th
  percentile threshold for at least 5 consecutive days; events separated by a gap < 3 days
  are merged into one. The threshold is computed per calendar day from an 11-day window
  across all years of the climatology period, then smoothed with a 31-day moving average.
  Baseline climatology period **1983–2012**. Reference implementation:
  `github.com/ecjoliver/marineHeatWaves` (Python) — authored by the paper's first author.
- **Statistics.** No per-gridcell linear trends (MHW metrics are bounded below and
  quantised); instead, differences of means between two time slices (1982–1998 vs
  2000–2016), tested with a two-sample Kolmogorov–Smirnov test. For the globally averaged
  time series, linear trends use **Theil–Sen** estimates with 95% confidence intervals,
  chosen for robustness to skew and heteroskedasticity. Grid cells with continuous ice
  cover longer than 5 days are excluded. Global averages are area-weighted.
- **Sample size / coverage.** Global ocean, 0.25° grid, 35 years of daily fields
  (~12,784 days per cell).
- **Headline numerical result (the comparison target).** Globally averaged total MHW days
  rise by ~30 days/year across the 35-year record from a baseline of about 25 days in the
  1980s. Supporting satellite-era statistics for the same period: MHW frequency
  +0.45 annual events per decade (p < 0.01); mean duration +1.3 days per decade
  (p < 0.01); mean intensity +0.085 °C per decade (p < 0.01), against a global SST trend
  of +0.16 °C per decade.

## Replication design choice

- [ ] **Reproduction Study** — direct reproduction: same methodology, same tools.
- [x] **Replication Study** — replication with different methodology or conditions.
- [ ] **Reproduction/Replication Study** — both.

Both the data and the software are independent of the original. The input is the **ESA
SST_cci Level 4 Analysis CDR v3.0** (DOI `10.5285/4a9654136a7148e39b7feb56f8bb02d2`,
Good & Embury 2024, CEDA) — produced by ESA CCI / UK Met Office via optimal-estimation
retrieval over (A)ATSR, AVHRR and SLSTR, a genuinely separate estimate of the same field
rather than a re-version of the NOAA OISST pipeline. The detection engine is **XMHW**
(DOI `10.5281/zenodo.7662469`, Petrelli, CLEX/coecms), an xarray-based implementation of
the same Hobday et al. definition, author-disjoint from the Oliver et al. list.

Because the MHW *definition* is held fixed while both the SST estimate and the detection
code change, this tests whether the paper's satellite-era result is an artefact of the
NOAA OISST product or of one specific codebase — the question a replication (not a
reproduction) is for.

> **Do not use `ecjoliver/TasmanSeaMHW_201516`** as an "independent" implementation. The
> Radar flags it independent only because that OpenAIRE record has an empty `authors: []`
> field; the GitHub handle `ecjoliver` is the paper's first author.

## Notes for downstream drafts

- **Keep the Quote, Claim and Outcome on the satellite era.** The Outcome must state
  explicitly that the 1925-onward / 54% result is *out of scope*, not *contradicted* — we
  did not test it. Conflating the two would be the overclaim this template exists to
  prevent.
- **The absence of a testable independent century record is itself a finding** worth
  recording in the Outcome's limitations: ERSST v4 and HadISST are part of the original
  paper's own data chain, and ERA-20C inherits HadISST2 as its ocean boundary condition,
  so none are independent. COBE-SST2 would be the natural candidate but has no citable
  DOI in OpenAIRE.
- **Hold the climatology fixed at 1983–2012** to match the paper. SST_cci v3.0 begins in
  1980–81, so this baseline is fully covered; deviating from it would confound a data
  difference with a methods difference.
- **AIDA atomicity.** Total MHW days is one finding — but it is presented in the paper as
  arising from frequency *and* duration. Keep the AIDA to the MHW-days quantity alone; if
  frequency and duration are also reported, they need their own AIDA/Claim pairs.
- **Version sensitivity.** SST_cci v2.1 (`10.5285/62c0f97b1eac4e0197a674870afe1ee6`) is
  available as a robustness check.
- **Second detector (optional, strengthens the verdict).** `xrMHW`
  (`10.5281/zenodo.18343768`) is a second independent implementation; agreement between
  two detectors is a materially stronger result than one.
