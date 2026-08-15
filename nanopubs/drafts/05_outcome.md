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
Satellite-era (1982-2016) marine heatwave day trend validated with independent data and software; century-scale claims not tested
```

The label carries the scope boundary deliberately. Nanopub labels travel alone
in search results and constellation views, where "validated" without a period
would read as validating the paper — including the 54 percent century-scale
figure this outcome does not touch.

<!-- field: study -->
### Choose study (search/select, required)

```
«URI of step 04 (FORRT Replication Study)»
```

<!-- field: repo -->
### Repository URL (text input, required)

```
https://github.com/annefou/marine-heatwave-replication
```

Matches the `repository-code` in `CITATION.cff` and the repository's git remote.
`/verify-chain` cross-checks these against each other.

<!-- field: date -->
### Choose completion date (text input, required)

```
2026-08-15
```

<!-- field: validationStatus -->
### Choose validation status (dropdown, required)

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

- [ ] contradicted
- [ ] inconclusive
- [ ] not tested
- [ ] partially supported
- [x] validated

<!-- field: confidenceLevel -->
### Choose confidence level (dropdown, required)

```
HighConfidence
```

*Strong evidence, mostly agrees with the original.* Not `VeryHighConfidence`,
which the vocabulary reserves for extensive evidence with high agreement: this
replication covers 93.3 percent of longitudes, leaves the intensity discrepancy
unexplained, and did not attempt the excess-trend attribution. The evidence for
the claim itself is strong; the coverage of the original paper is partial.

- [x] high - Strong evidence, mostly agrees with original
- [ ] low - Limited evidence, significant disagreement
- [ ] moderate - Adequate evidence, partial agreement
- [ ] very high - Extensive evidence, high agreement with original
- [ ] very low - Minimal evidence, major disagreement

<!-- field: conclusion -->
### Describe the overall conclusion about the original claim (textarea, required)

```
WHAT WAS TESTED. One claim of the original paper: its satellite-era result that
globally averaged marine heatwave days rose by about 30 days per year over
1982-2016, from a baseline of about 25 days in the 1980s. That claim, and only
that claim, is what this outcome validates. The paper's better-known abstract
figure - a 54 percent increase in marine heatwave days - describes a different
analysis over a different period and was NOT tested here. See the limitations.

RESULT. The claim is validated. Using ESA SST CCI Analysis v3.0 in place of
NOAA OI SST and XMHW in place of the original authors' own implementation,
globally averaged marine heatwave days increased by 31.77 days over 1982-2016,
against the 30 days reported originally - a difference of 6 percent. The two
supporting metrics also agree: marine heatwave frequency increased by 0.433
events per decade against 0.45 reported, and mean duration by 1.482 days per
decade against 1.3 reported. All three trends are significant at the 5 percent
level, as in the original.

The trend is not an artefact of El Nino Southern Oscillation variability. After
removing the ENSO signature from the temperature record, the increase is 29.82
days over the record - 6 percent smaller - and remains significant. This
reproduces the original's own argument for the same conclusion, independently.

WHY THE AGREEMENT CARRIES WEIGHT. Both the observational basis and the software
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
A. WHAT THIS OUTCOME DOES NOT COVER

1. Only the satellite-era claim was tested. The original paper is titled
   "Longer and more frequent marine heatwaves over the past century" and its
   central argument spans 1900-2016. This replication tests a 35-year window,
   1982-2016 - about 30 percent of that span. Validation here says nothing
   about the other 70 percent.

2. The paper's most-quoted number was NOT tested. The abstract reports that
   from 1925 to 2016 marine heatwave frequency and duration rose by 34 percent
   and 17 percent, giving a 54 percent increase in annual marine heatwave days.
   Those figures come from a proxy reconstruction built on monthly gridded sea
   surface temperature, comparing 1925-1954 against 1987-2016. Nothing in this
   outcome supports or disputes them.

3. This is a limit of the data, not a choice. Marine heatwaves are defined on
   daily temperatures against a percentile threshold, and no independent daily
   global sea surface temperature record exists before 1981. ESA SST CCI
   Analysis v3.0 begins in 1981; the record used here starts 1 January 1982.
   The century-scale claims cannot be independently replicated with satellite
   data by anyone, and the absence of a testable independent century record is
   itself worth stating.

4. The paper's century-long in situ station records - six stations, 1904-2016 -
   were also not tested. They are point measurements, not a global average, and
   testing them would be a different study with a different claim.

5. The excess-trend attribution of the original's Figure 3a-c was not attempted.
   That test asks whether marine heatwave trends exceed what mean sea surface
   temperature warming alone would produce, and requires a Monte Carlo ensemble
   of synthetic detections at roughly 6.7 core-hours per realisation. The
   corresponding maps here carry no significance hatching.

B. WHAT WORKED

6. The headline statistic replicated to within 6 percent, with independent data
   and independent software, and the two supporting metrics agreed in sign,
   magnitude and significance.

7. The ENSO-removal argument replicated: the trend persists, 6 percent smaller,
   when the ENSO signature is regressed out - reproducing the original's own
   reasoning by an independent route.

8. The numbers are reproducible. Two complete independent runs, which failed on
   different latitude blocks and were retried differently, produced identical
   headline statistics to all reported digits.

9. Figures 2 and 3 were reproduced in the original's layout and can be compared
   with them directly.

C. WHAT DID NOT WORK, OR REMAINS UNEXPLAINED

10. Marine heatwave intensity trends are far weaker here than in the original.
    The per-cell intensity trend map is close to featureless, with a median of
    +0.0012 degrees Celsius per decade, whereas the original's equivalent map
    (its Figure 3b) shows structure across a range roughly ten times larger.
    This is unresolved. It may reflect a genuine difference between the two
    temperature records, or a difference between XMHW's mean-intensity metric
    and the original's definition. Marine heatwave intensity is not part of the
    claim under test, so it does not bear on the validation - but it is a
    disagreement between this replication and the original, and it is not
    explained.

11. The 1980s baseline is 21.70 days against the original's approximately 25.
    The difference is not statistically distinguishable given the interannual
    variability of that window (95 percent confidence interval [14.60, 28.79],
    t = -1.10, p = 0.31), but the point estimate is lower and is reported as
    such rather than rounded toward agreement.

12. The detection software fails non-deterministically. XMHW raised
    InvalidIndexError on 2 to 8 percent of latitude blocks across runs, with no
    pattern in latitude or data coverage, and the same block succeeded when
    retried. Separately, it cannot assemble a block in which any cell has zero
    detected events - which appears across the equatorial Pacific once ENSO is
    removed - and that path had to use XMHW's single-cell mode instead. Neither
    affects the reported numbers, but this pipeline cannot be run without retry
    logic, and that is a property of the independent tooling worth recording.

D. TECHNICAL COVERAGE

13. Longitude coverage is 93.3 percent, not complete. The reader takes bands 60
    native cells wide starting every 64, skipping 0.2 degrees every 3.2 degrees,
    so the analysis grid holds 336 of a possible 360 one-degree columns. The
    effect was measured rather than assumed: repeating the analysis on random
    subsamples that drop a further 6.7 percent of columns moves the headline by
    plus or minus 0.64 days, about 2 percent of a statistic whose trend
    confidence interval spans 6.35 to 12.94 days per decade. Even a 28 percent
    sample of longitudes holds the headline to within 0.66 days.

14. The analysis grid is 1 degree, coarser than the original's 0.25 degree.
    Regional detail is correspondingly coarser; the global average, which is
    what the claim concerns, is not sensitive to this.
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
