# 05 — FORRT Replication Outcome

**Documented field list** (verbatim from `docs/forrt-form-fields.md` § FORRT Replication Outcome):

| Field label | Field type | Notes |
|---|---|---|
| Short URI suffix for outcome ID | text input, **required** | |
| Plain-text label for the outcome | text input, **required** | Descriptive title. |
| Search for a FORRT replication study | search/select, **required** | Pick the published Replication Study URI. |
| Repository URL | text input, **required** | |
| Completion date | date picker, **required** | ISO format. |
| Validation status | dropdown, **required** | `Validated` / `PartiallySupported` / `Contradicted` / `Inconclusive` / `NotTested`. |
| Confidence level | dropdown, **required** | `VeryHighConfidence` / `HighConfidence` / `Moderate` / `LowConfidence` / `VeryLowConfidence`. |
| Describe the overall conclusion about the original claim | textarea, **required** | Substantive interpretation, with the headline numerical comparison. |
| Describe the evidence that supports your conclusion | textarea, **required** | Numerical results, test statistics. |
| Describe what limits the conclusions of the study | textarea, **optional** | Caveats / limitations. |

> **All numbers below were read from `results/headline_comparison.json` and
> `results/headline_comparison_enso_removed.json`, not recalled.**

---

## Field-by-field draft

<!-- field: outcome -->
### Short URI suffix for outcome ID (text input, required)

```
oliver-2018-mhw-days-outcome
```

<!-- field: label -->
### Plain-text label for the outcome (text input, required)

```
Satellite-era marine heatwave day trend validated with independent data and independent software
```

<!-- field: study -->
### Search for a FORRT replication study (search/select, required)

```
«URI of step 04 (FORRT Replication Study)»
```

<!-- field: repository -->
### Repository URL (text input, required)

```
https://github.com/annefou/marine-heatwave-replication
```

Matches the `repository-code` in `CITATION.cff` and the repository's git remote.
`/verify-chain` cross-checks these against each other.

<!-- field: date -->
### Completion date (date picker, required)

```
2026-08-15
```

<!-- field: status -->
### Validation status (dropdown, required)

```
Validated
```

All three metrics the claim rests on agree in sign, magnitude and significance,
using an independent sea surface temperature record and independent detection
software. The headline figure differs from the original by 6 percent.

**Why not `PartiallySupported`:** that status signals a mixed direction of
agreement — some elements supported, others not. Nothing here contradicts or
fails to support the claim. The unresolved item (marine heatwave intensity
trends, see limitations) is not part of the claim under test; it is a
supplementary map in the original's Figure 3b.

<!-- field: confidence -->
### Confidence level (dropdown, required)

```
HighConfidence
```

*Strong evidence, mostly agrees with the original.* Not `VeryHighConfidence`,
which the vocabulary reserves for extensive evidence with high agreement: this
replication covers 93.3 percent of longitudes, leaves the intensity discrepancy
unexplained, and did not attempt the excess-trend attribution. The evidence for
the claim itself is strong; the coverage of the original paper is partial.

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

```
The claim is validated. Using ESA SST CCI Analysis v3.0 in place of NOAA OI SST
and XMHW in place of the original authors' own implementation, globally averaged
marine heatwave days increased by 31.77 days over 1982-2016, against the 30 days
reported originally - a difference of 6 percent. The two supporting metrics also
agree: marine heatwave frequency increased by 0.433 events per decade against
0.45 reported, and mean duration by 1.482 days per decade against 1.3 reported.
All three trends are significant at the 5 percent level, as in the original.

The trend is not an artefact of El Nino Southern Oscillation variability. After
removing the ENSO signature from the temperature record, the increase is 29.82
days over the record - 6 percent smaller - and remains significant. This
reproduces the original's own argument for the same conclusion, independently.

The agreement is notable because both the observational basis and the software
were replaced. A shared dataset or a shared codebase can carry a common error
into a reproduction; here neither is shared with the original, so the agreement
is evidence about the finding rather than about the pipeline.
```

<!-- field: evidence -->
### Describe the evidence that supports your conclusion (textarea, required)

```
Data: ESA SST CCI Analysis v3.0 (DOI 10.5285/4a9654136a7148e39b7feb56f8bb02d2),
1 January 1982 to 31 December 2016, 1 degree analysis grid, 30,774 ocean cells,
climatology 1983-2012.
Software: XMHW 1.0.0, archived at
swh:1:rev:1006312ae693e8aef8bd3706b9afb431eca564a5.

Marine heatwave days, globally averaged, Theil-Sen trend:
  change over the record   31.77 days   (original: 30)
  trend                    9.344 days per decade, 95% CI [6.354, 12.938]
  significant at 5%        yes
  1980s baseline           21.70 days   (original: about 25)

Marine heatwave frequency: 0.433 events per decade (original: 0.45), significant.
Marine heatwave duration:  1.482 days per decade (original: 1.3), significant.

With the ENSO signature removed: 29.82 days over the record, 8.770 days per
decade, significant. The globally averaged series falls below the unadjusted
series in 34 of 35 years, with the largest reductions in 1998, 2010 and 2016 -
the major El Nino years.

The 1980s baseline of 21.70 days is not distinguishable from the original's
approximately 25: the 1982-1989 mean has a 95% confidence interval of
[14.60, 28.79] (n=8, s.d. 8.49), which contains 25, and a one-sample t-test
gives t = -1.10, p = 0.31. Interannual variability over that window is large,
ranging from 12.49 days in 1985 to 34.47 days in 1983.

Reproducibility of these numbers was tested directly rather than assumed. Two
complete independent runs of the pipeline, which failed on different latitude
blocks and were retried differently, produced identical headline statistics to
all reported digits (scripts/compare_runs.py).
```

<!-- field: limitations -->
### Describe what limits the conclusions of the study (textarea, optional)

```
1. Longitude coverage is 93.3 percent, not complete. The reader takes bands 60
   native cells wide starting every 64, skipping 0.2 degrees every 3.2 degrees,
   so the analysis grid holds 336 of a possible 360 one-degree columns. The
   effect was measured rather than assumed: repeating the analysis on random
   subsamples that drop a further 6.7 percent of columns moves the headline by
   plus or minus 0.64 days, about 2 percent of a statistic whose trend
   confidence interval spans 6.35 to 12.94 days per decade. Even a 28 percent
   sample of longitudes holds the headline to within 0.66 days.

2. Marine heatwave intensity trends are weaker here than in the original. The
   per-cell intensity trend map is close to featureless, with a median of
   +0.0012 degrees Celsius per decade, whereas the original's equivalent map
   shows structure across a range ten times larger. This is unresolved: it may
   reflect a genuine difference between the two temperature records, or a
   difference between XMHW's mean-intensity metric and the original's. Marine
   heatwave intensity is not part of the claim under test, so this does not bear
   on the validation, but it is not explained.

3. The detection software fails non-deterministically. XMHW raised
   InvalidIndexError on 2 to 8 percent of latitude blocks across runs, with no
   pattern in latitude or data coverage, and the same block succeeded when
   retried. Separately, it cannot assemble a block in which any cell has zero
   detected events, which appears across the equatorial Pacific once ENSO is
   removed; that path uses XMHW's single-cell mode instead. Neither affects the
   results - two complete runs produced identical numbers - but both mean this
   pipeline cannot be run without retry logic.

4. The 1980s baseline is 21.70 days against the original's approximately 25.
   The difference is not statistically distinguishable given interannual
   variability, but the point estimate is lower and is reported as such.

5. The excess-trend attribution of the original's Figure 3a-c was not attempted.
   That test asks whether marine heatwave trends exceed what mean sea surface
   temperature warming alone would produce, and requires a Monte Carlo ensemble
   of synthetic detections at roughly 6.7 core-hours per realisation. The
   corresponding maps here carry no significance hatching.

6. The pre-satellite portion of the original paper is untested and untestable by
   this design. Its century-scale results, including the widely quoted 54
   percent increase in marine heatwave days, rest on a proxy reconstruction from
   monthly gridded sea surface temperature. No independent daily global record
   exists before 1981 against which to test them.
```

---

## Pre-flight checklist

- [x] Section for this template found in `docs/forrt-form-fields.md`
- [x] Section is documented (not "needs screenshot")
- [x] Every field enumerated in form order; optional fields explicitly resolved
- [x] No invented field names
- [x] Every number read from `results/`, none recalled
- [x] Validation status and Confidence level chosen from the controlled vocabularies
- [x] Limitations state the unresolved intensity discrepancy rather than omitting it
- [x] "percentage points" / percentages spelled out per `DOMAIN.md` § Style
