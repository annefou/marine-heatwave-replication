# 06 — CiTO Citation

**Description:** *"Declare citations between papers or other works, using Citation Typing Ontology"*

**Documented field list** (verbatim from `docs/forrt-form-fields.md` § Citation with CiTO):

| Field label | Field type | Notes |
|---|---|---|
| Identifier for the citing creative work | text input, **required** | For FORRT chains this is the Outcome's nanopub URI. |
| List citations | repeatable group, **required** ≥1 | One or more entries, each with type + URL. |
| ↳ Citation Type | dropdown | From the controlled list. **`replicates` is NOT available.** |
| ↳ DOI or other URL of the cited work | text input | DOI URL form `https://doi.org/10.x/y` or other URL. |

---

## Field-by-field draft

<!-- field: work -->
### Identifier for the citing creative work (text input, required)

```
«URI of step 05 (FORRT Replication Outcome)»
```

The Outcome is the citing work: it is the Outcome that stands in a citation
relation to the original paper, not the repository or the study design. Pulled
from `nanopubs/PUBLISHED.md` row 05, or pre-filled by the chain wizard.

<!-- field: citations -->
### List citations (repeatable group, required ≥ 1)

**Item 1 — the paper under replication**

| Sub-field | Value |
|---|---|
| Citation Type | `confirms` |
| DOI or other URL | `https://doi.org/10.1038/s41467-018-03732-9` |

`confirms` follows directly from the Outcome's `Validated` status, per the
mapping rule in `docs/forrt-form-fields.md`:

| Validation status | CiTO intention |
|---|---|
| Validated | `confirms` |
| PartiallySupported | `qualifies` |
| Contradicted | `disputes` |

**Note on `replicates`.** It would be the natural verb here and it is **not** in
the CiTO list available on this form. `confirms` is the correct available
intention for a validated outcome; the *fact* that this was a replication rather
than a citation of agreement is carried by the Replication Study node (step 04),
which is where it belongs structurally.

---

**Item 2 — the independent data source** *(optional, recommended)*

| Sub-field | Value |
|---|---|
| Citation Type | `citesAsDataSource` |
| DOI or other URL | `https://doi.org/10.5285/4a9654136a7148e39b7feb56f8bb02d2` |

ESA SST CCI Analysis v3.0. Included because the independence of this record from
the original's NOAA OI SST is what makes the outcome evidence about the finding
rather than about the pipeline. A reader following the chain should be able to
reach the data without opening the repository.

---

**Item 3 — the independent detection software** *(optional, recommended)*

| Sub-field | Value |
|---|---|
| Citation Type | `usesMethodIn` |
| DOI or other URL | `https://doi.org/10.5281/zenodo.5112732` |

XMHW, the concept DOI for the project. `usesMethodIn` rather than `credits`: the
method — the Hobday et al. (2016) definition as implemented by XMHW — is what
was used, and `credits` is documented for directly reused notebooks or
tutorials.

**Caveat carried from `CITATION.cff`:** this concept DOI resolves to XMHW 0.9.2,
the latest version deposited on Zenodo, whereas this replication ran **1.0.0**,
which was never deposited there. The exact revision is identified in the
Outcome's evidence field by SWHID
(`swh:1:rev:1006312ae693e8aef8bd3706b9afb431eca564a5`), which is the only
persistent identifier for the code that actually produced these results.

---

## Pre-flight checklist

- [x] Section for this template found in `docs/forrt-form-fields.md`
- [x] Section is documented (not "needs screenshot")
- [x] Every field enumerated in form order; optional fields explicitly resolved
- [x] No invented field names
- [x] Citation types taken from the documented available list (`replicates` correctly avoided)
- [x] CiTO intention matches the Outcome's validation status per the mapping rule
- [x] All DOIs verified to resolve
