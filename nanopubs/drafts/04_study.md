# 04 — FORRT Replication Study

**Documented field list** (verbatim from `docs/forrt-form-fields.md` § FORRT Replication Study):

| Field label | Field type | Notes |
|---|---|---|
| Short URI suffix for study ID | text input, **required** | Short slug, becomes part of the nanopub URI. |
| Label/name of replication study | text input, **required** | The human-readable title. |
| Study type | dropdown, **required** | (1) Reproduction Study; (2) Replication Study; (3) Reproduction/Replication Study. |
| Search for a FORRT claim | search/select, **required** | Pick the published Claim URI. |
| Describe what part of the claim is reproduced/replicated | textarea, **required** | The **scope**. NOT methodology. NOT results. |
| Describe how the claim is reproduced/replicated | textarea, **required** | The **method** in plain prose. NOT numerical results. |
| Describe any deviations from original methodology | textarea, **optional** | Verify against the actual code first. |
| Search keywords (Wikidata) | multi-select Wikidata search, **optional** | Provide search labels rather than QIDs. |
| Search discipline (Wikidata) | search Wikidata, **optional** | Academic discipline. |

---

## Field-by-field draft

<!-- field: study -->
### Short URI suffix for study ID (text input, required)

```
oliver-2018-mhw-days-replication-study
```

<!-- field: label -->
### Label/name of replication study (text input, required)

```
Replication of the satellite-era marine heatwave day trend using ESA SST CCI and XMHW
```

<!-- field: type -->
### Choose the study type (dropdown, required)

```
Replication Study
```

*Replication with different methodology or conditions* — not Reproduction, and
not both. **Both** inputs to the analysis are independent of the original:

- **Data:** ESA SST CCI Analysis v3.0, an optimal-estimation retrieval produced
  by ESA CCI / the UK Met Office. Oliver et al. used NOAA OI SST.
- **Software:** XMHW (Petrelli, CLEX/coecms), author-disjoint from Oliver et al.
  Oliver et al. used their own `marineHeatWaves` implementation.

What is held **fixed** is the *definition* — Hobday et al. (2016), with the
paper's stated parameters. That is what makes this a replication rather than a
different study: same question, same definition, independent instruments.

- [x] Replication Study - replication with different methodology or conditions
- [ ] Reproduction/Replication Study - study that is both, reproduction and replication
- [ ] Reproduction Study - direct reproduction: same methodology, same tools

<!-- field: claim -->
### Choose FORRT claim (search/select, required)

```
«URI of step 03 (FORRT Claim)»
```

Pre-filled by the chain wizard; otherwise search for the claim label
"Increase in globally averaged marine heatwave days over the 1982-2016 satellite record".

<!-- field: scope -->
### Describe what part of the claim is reproduced/replicated. (textarea, required)

```
This study tests the claim's satellite-era component: the change in globally
averaged annual marine heatwave days between 1982 and 2016, and the 1980s
baseline level against which that change is expressed. The two supporting
metrics the original reports alongside it — trends in marine heatwave frequency
and duration — are also evaluated, since the claim states that the day-count
increase follows from them.

Out of scope: every pre-satellite element of the original paper. Its
century-scale results (1925-1954 versus 1987-2016), the proxy reconstruction
from monthly gridded SST, and the six century-long in situ station records are
not tested here, because no independent daily global SST record exists before
1981 that could test them. The abstract's most-quoted figure — a 54 percent
increase in marine heatwave days - belongs to that pre-satellite proxy analysis
and is therefore not the claim under test.

Also out of scope: the excess-trend attribution of Figure 3a-c, which asks
whether marine heatwave trends exceed what mean sea surface temperature warming
alone would produce. That test requires a Monte Carlo ensemble of synthetic
detections and was not performed.
```

**Scope, not method and not results** — per `docs/pico-study-outcome-levels.md`.
No numbers appear here; they belong in the Outcome.

<!-- field: methodology -->
### Describe how the claim is reproduced/replicated. (textarea, required)

```
Daily sea surface temperature from ESA SST CCI Analysis v3.0 was streamed from
the Copernicus Marine Service ARCO store and area-averaged from its native 0.05
degree grid to a 1 degree analysis grid while streaming, covering 1 January 1982
to 31 December 2016. Cells with continuous sea ice were excluded, following the
original's ice-exclusion rule.

Marine heatwaves were detected with XMHW, an xarray implementation of the
Hobday et al. (2016) definition, using the parameters the original states: 90th
percentile threshold, minimum duration of five days, gaps shorter than three
days merged, an 11-day window for the percentile, 31-day smoothing of the
percentile, and a 1983-2012 baseline climatology.

Marine heatwave days were attributed to the calendar year in which they fall;
event duration and intensity were attributed to the year each event started, as
the original specifies. Per-cell annual statistics were aggregated to a global
mean weighted by the cosine of latitude, and trends were estimated with the
Theil-Sen estimator with 95 percent confidence intervals, as in the original.

To separate the secular trend from interannual variability, the analysis was
repeated on a sea surface temperature series with the ENSO signature removed:
daily anomalies at each cell were regressed onto the multivariate ENSO index
with monthly leads and lags to plus and minus one year, and the fitted ENSO
component subtracted. Detection on that series used the climatology and
threshold derived from the original, unmodified series, so that events remain
defined relative to real-world conditions.
```

**Method, not results** — no numbers from this study appear here. Every
parameter above was read from `notebooks/03_analysis.py` and
`notebooks/05_enso_removal.py`, not recalled (`docs/verify-before-drafting.md`).

<!-- field: deviation -->
### Describe any deviations from original methodology. (textarea, optional)

```
1. Sea surface temperature source. ESA SST CCI Analysis v3.0 rather than NOAA
   OI SST, and a 1 degree analysis grid rather than the original's 0.25 degree
   grid. This is the intended independence of the replication, not an
   incidental difference.

2. Detection software. XMHW rather than the original authors' own
   implementation of the same published definition.

3. Longitude sampling. The ARCO reader takes bands 60 native cells wide starting
   every 64, so 0.2 degrees of longitude is skipped every 3.2 degrees and the
   analysis grid holds 336 of a possible 360 one-degree columns - 93.3 percent
   coverage. Measured effect on the headline statistic: plus or minus 0.64 days.

4. ENSO removal is fitted to deseasonalised anomalies. The original describes
   regressing daily sea surface temperatures onto the multivariate ENSO index.
   Applied literally to raw temperatures, 25 predictors spanning plus and minus
   twelve months can combine into an annual harmonic and absorb the seasonal
   cycle; in this implementation that accounted for 66 percent of the signal
   removed and more than doubled detected marine heatwave days, when removing
   ENSO should reduce them. Regressing the anomaly confines the fit to
   interannual variability. This is believed to be what the original intends
   rather than a departure from it.

5. ENSO index version. The original multivariate ENSO index of Wolter and
   Timlin, which the original paper cites and which NOAA last updated in
   December 2018, rather than the maintained MEI.v2 successor, which uses a
   different variable set and base period.

6. Annual sea surface temperature variance and skewness are computed on
   deseasonalised anomalies. At mid-latitudes the seasonal cycle is roughly 95
   percent of daily variance, so computing these on raw temperatures measures
   seasonal amplitude rather than the variability that governs threshold
   exceedance.

7. The excess-trend significance test against a stochastic climate model was not
   performed, so the corresponding maps carry no significance hatching.
```

Every item verified against the code, not recalled. Items 4 and 6 were found by
checking that intermediate outputs were physically plausible, not by reading the
paper more carefully — both are recorded because a reader reproducing this from
the paper's wording alone would hit the same problem.

<!-- field: keyword -->
### Search keywords (Wikidata) (search/select, optional)

Search labels to enter in the form (select the matching Wikidata item; do not
paste QIDs, and confirm each item's type before selecting):

- `marine heatwave`
- `sea surface temperature`
- `climate change`
- `time series analysis`

<!-- field: discipline -->
### Search discipline (Wikidata) (search/select, optional)

```
oceanography
```

Alternative if the form's vocabulary prefers it: `climatology`.

---

## Pre-flight checklist

- [x] Section for this template found in `docs/forrt-form-fields.md`
- [x] Section is documented (not "needs screenshot")
- [x] Every field enumerated in form order; optional fields explicitly resolved
- [x] No invented field names
- [x] Scope field contains scope only — no method, no results
- [x] Method field contains method only — no results
- [x] Deviations verified against `notebooks/`, not recalled
