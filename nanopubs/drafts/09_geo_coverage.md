# 09 — Geographical coverage (optional)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting. Read `docs/geo-coverage.md` first.

**Applicability.** The paper is spatial and its study area is the **global ocean** — a
single pooled extent, not a set of distinct sites. One coverage nanopub, one block.

The six century-long in situ stations (Table 1: Pacific Grove, Scripps Pier, Newport
Beach, Arendal, Port Erin, Race Rocks) are *not* drafted as separate coverage nanopubs
here: they ground the paper's monthly-proxy strand, which this replication does not test
(see `00_paper_summary.md`). Add them later only if the replication is ever extended to
the station analysis.

## Shared field

<!-- field: paper -->
### Cited DOI (text input, required — same for every location)

The **original paper's** DOI (bare, starting `10.` — the form prepends `https://doi.org/`). Same DOI as the Quote (step 01) / CiTO (step 06). Read it from `CITATION.cff` `references:`; do not recall it.

```
10.1038/s41467-018-03732-9
```

---

## Per-location block

### Location A

<!-- field: quoteType -->
**Quote type** (radio: whole | ends, required)

```
whole
```

<!-- field: quotation -->
**Quoted Text** (textarea, required) — the **verbatim** sentence from the paper naming *this* area.

```
The data have been interpolated daily onto a 0.25° × 0.25° spatial grid with global coverage from 1982 to 2016.
```

Character count: 111 / 500. Verified verbatim against `paper/oliver-2018.pdf`, Methods
§ "Daily, global, remotely sensed SSTs covering 1982–2016", via the `pdftotext` text layer.

<!-- field: quotation-end -->
**Quoted Text End** (textarea, optional — only if quote type = ends). Leave blank for `whole`.

*(skip — optional; quote type is `whole`)*

```

```

<!-- field: location -->
**Short ID for location** (text input, required) — slug for the URI suffix.

```
global-ocean
```

<!-- field: location-label -->
**Area name** (text input, required) — human-readable name as the paper frames it.

```
Global ocean
```

<!-- field: geometry -->
**Short ID for geometry** (text input, optional) — URI suffix for the geometry node.

```
coverage
```

<!-- field: wkt -->
**Geometry as Well-known Text (WKT)** (map / text, resolved in the form) — **Do NOT hand-write coordinates.**

*Leave blank — resolve in the form.* The paper states a grid resolution (0.25°) and a
period, but no bounding coordinates for the study area, so there is nothing verbatim to
copy. Let the form's location search / map resolve "Global ocean"; a hand-written global
bounding box would be a fabricated datum. Note the analysis is not literally every ocean
cell: grid cells with continuous ice cover longer than 5 days were excluded, which trims
the highest latitudes.

```

```

<!-- field: comment -->
**Comment** (textarea, required) — one or two sentences on **how the quoted text supports** this being the coverage. Grounded in the paper, no new claims.

```
The quoted sentence states the spatial extent of the paper's primary dataset directly: a 0.25° daily SST grid with global coverage over 1982-2016. The marine heatwave frequency, intensity and duration fields are computed at every one of those grid points and then area-weighted into the globally averaged series, so the coverage of the finding is the global ocean, excluding cells under continuous ice cover for more than five days.
```

Character count: 432 / 500.

## Publication note

Each location block is a **standalone** nanopub, not one of the six FORRT chain steps.
Publish via the platform's **"Document geographical coverage"** template. After publishing,
paste the resulting URI into `nanopubs/PUBLISHED.md` under a "Geographical coverage" row.
