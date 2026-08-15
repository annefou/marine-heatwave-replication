# 03 — FORRT Claim

**Form heading:** *"FORRT Claim — Declare an original claim according to FORRT, linking it to an AIDA sentence with a specific FORRT type."*

**Documented field list** (verbatim from `docs/forrt-form-fields.md` § FORRT Claim):

| Field label | Field type | Notes |
|---|---|---|
| Short URI suffix as claim ID | text input, **required** | Slug becomes part of nanopub URI. Use kebab-case. |
| Label of the claim (to find it later) | text input, **required** | Used for searches/discovery. A descriptive title, not a sentence. |
| Search for an AIDA sentence | search/select dropdown, **required** | Search by AIDA text → pick the published AIDA URI. |
| Type of FORRT claim | dropdown, **required** | Single-select from 7 options. See `docs/claim-type-vocabulary.md`. |
| Source URI (optional) | text input, **optional** | **Expects full URL form** (`https://doi.org/10.x/y`). |

There are no other substantive fields below "Source URI" — only a "publish as example" toggle.

---

## Field-by-field draft

<!-- field: claim -->
### Short URI suffix as claim ID (text input, required)

```
mhw-days-satellite-era-increase
```

Kebab-case. Names the claim's subject, not the replication — the Claim node is
the assertion under test, and the same slug should make sense to anyone else who
tests it.

<!-- field: label -->
### Label of the claim, to find it later (text input, required)

```
Increase in globally averaged marine heatwave days over the 1982-2016 satellite record
```

A descriptive title rather than a sentence, per the field's stated purpose
(search and discovery). Includes the period, since a claim about MHW-day
increases is meaningless without one and the century-scale claims in the same
paper would otherwise collide with it in search results.

<!-- field: aida -->
### Search for an AIDA sentence (search/select, required)

```
«URI of step 02 (AIDA sentence)»
```

Search the form for the AIDA text ("The globally averaged number of marine
heatwave days per year increased by approximately 30 days…") and select the
published URI. The chain wizard pre-fills this.

**Caveat from the docs:** it is not confirmed whether this search finds AIDAs
published via Nanodash (`w3id.org/np/…`) as opposed to Science Live
(`w3id.org/sciencelive/np/…`). If step 02 had to be published through Nanodash —
the documented workaround for the datasets+publications bug — paste the URI
manually instead of relying on search.

<!-- field: forrtType -->
### Type of FORRT claim (dropdown, required)

```
descriptive pattern
```

**Why this and not `statistical significance`.** The claim asserts an observed
empirical trend — that globally averaged MHW days rose over the satellite
record. The p < 0.01 in the source sentence is the *evidence* for that trend,
not the claim itself. `docs/claim-type-vocabulary.md` is explicit: pick
`statistical significance` only when the claim is literally "the test was
significant", with no underlying empirical relationship asserted. It also lists
the directly analogous Soroye 2020 case (thermal exposure correlates with
bumble bee extirpation) as `descriptive pattern`.

**Why not `model performance`.** Theil–Sen is the instrument used to quantify
the trend, not the object of the claim. Per the same vocabulary: "empirical
relationships discovered by fitting a model are `descriptive pattern` (the model
is the instrument; the pattern is the claim)."

- [ ] computational performance (Computational & Performance)
- [ ] data governance (access control, licensing, FAIR compliance)
- [ ] data quality (preprocessing, validation, normalization)
- [ ] descriptive pattern (distribution, trend, proportion)
- [ ] model performance (accuracy, F1 score, evaluation metrics)
- [ ] scalability (Computational & Performance)
- [ ] statistical significance (significant difference, relationship, or effect)

<!-- field: source -->
### Source URI (text input, optional)

```
https://doi.org/10.1038/s41467-018-03732-9
```

**Full URL form**, as this field requires — unlike the Quote-with-comment "Cited
DOI" field, which takes the bare `10.x/y`. Getting these two the wrong way round
is a documented trap. Verified to resolve (HTTP 200).

---

## Pre-flight checklist

- [x] Section for this template found in `docs/forrt-form-fields.md`
- [x] Section is documented (not "needs screenshot")
- [x] Every field enumerated in form order; optional fields explicitly resolved
- [x] No invented field names
- [x] No "form may have other fields" caveats
- [x] Documented field list pasted at the top
- [x] Claim type chosen from the controlled vocabulary, with reasoning recorded
