# Discovery decisions

_Carried over from the replication-radar discovery session. `gh repo create --template` copies a
BLANK template and does not record these — this file bridges the gap so the fresh in-repo session
(and `/init-template`) has what you settled on._

- **Paper to replicate:** Longer and more frequent marine heatwaves over the past century — DOI `10.1038/s41467-018-03732-9`
- **Independent dataset:** ESA SST_cci Level 4 Analysis Climate Data Record v3.0, DOI 10.5285/4a9654136a7148e39b7feb56f8bb02d2 (Good & Embury 2024, CEDA) - independent of Oliver et al.'s NOAA OISST v2
- **Reusable software:** XMHW - xarray-based Marine HeatWave detection, DOI 10.5281/zenodo.7662469, https://github.com/coecms/xmhw (Petrelli, CLEX/coecms) - author-disjoint from Oliver et al.
- **Repo:** marine-heatwave-replication

## Next (in this repo, in a fresh agent session)
1. `/init-template` — bootstrap (author identity + the paper DOI above).
2. Put the paper PDF in `paper/`.
3. Phase 1: record the dataset DOI + methodology in `nanopubs/drafts/`; use the software above as the independent engine.

## Discovery context worth carrying forward

**Replication status at time of discovery (2026-08-13):** `replication_status("10.1038/s41467-018-03732-9")`
returned `replicated: false` — zero Science Live verdicts from any signer, no CiTO relations,
no registered claims. Status `open`, despite 1,738 citations. Radar readiness score 1.0 (highest
in the marine-heatwave field).

**The claim under test.** Oliver et al. (2018) report that from 1925 to 2016, global average marine
heatwave frequency increased 34% and duration 17%, producing a **54% increase in annual marine
heatwave days globally** — and that these trends are largely explained by increases in mean ocean
temperature.

**Independence rationale.**
- *Data:* Oliver et al. ran primarily on NOAA OISST v2 (`10.7289/v5sq8xb5`), plus HadISST/HadSST3
  and ERSST for the century-scale reconstruction. ESA SST_cci is produced by ESA CCI / UK Met
  Office with an independent optimal-estimation retrieval over (A)ATSR, AVHRR and SLSTR — a
  genuinely separate estimate of the same field, not a re-version of the same pipeline.
  SST_cci v2.1 (`10.5285/62c0f97b1eac4e0197a674870afe1ee6`) is available as a version-sensitivity
  check.
- *Software:* XMHW is authored by Petrelli (CLEX/coecms), disjoint from the Oliver et al. author
  list. It implements the same Hobday et al. MHW definition as an independent codebase.
  Cross-check candidate: `xrMHW` (`10.5281/zenodo.18343768`,
  https://github.com/Gabo2000s/xarray_MHW-xrMHW-) — a second independent detector; agreement
  between two implementations is a materially stronger verdict than one.

**Known scope limitation — state this explicitly in the Outcome nanopub.** No satellite SST product
reaches back before ~1981, so SST_cci supports replication of the **satellite-era portion only**
(~1982–2016, the same window as Oliver et al.'s own OISST analysis). The full 1925-onward trend
cannot be tested with this dataset. An independent century-scale record was searched for and not
found with a citable DOI in OpenAIRE: ERSST v4 (`10.7289/v5kd1vvf`) and HadISST are both part of
the original paper's own data chain, and ERA-20C (`10.5065/d6vq30qg`) uses HadISST2 as its ocean
boundary condition, so it inherits the same lineage. JMA's COBE-SST2 would be the natural
independent long record but has no citable DOI in OpenAIRE — it would need sourcing from
JMA/NOAA PSL and citing via its documentation paper. The absence of a testable independent
century record is itself a finding worth recording.

**Do not use `ecjoliver/TasmanSeaMHW_201516`.** The Radar's `find_independent_software` flags it
`independent: true`, but this is a false positive: the GitHub handle `ecjoliver` is Eric C. J.
Oliver, first author of the target paper. The author-disjointness check passed only because that
OpenAIRE record has an empty `authors: []` field. Using it would defeat the independence of the
replication.

**Field context.** All 10 top-ranked marine-heatwave targets on the Radar are OPEN. The single
verified paper in the field is "Climate-driven regime shift of a temperate marine ecosystem"
(`10.1126/science.aad8745`, Validated, 1 independent replication) — a useful model for how to
reduce a paper to one atomic AIDA-form claim and test it on an independent substrate.
