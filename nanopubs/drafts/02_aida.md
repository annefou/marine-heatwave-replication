# 02 — AIDA Sentence

**Form heading:** *"AIDA Sentence — Make structured scientific claims following the AIDA model"*

**Documented field list** (verbatim from `docs/forrt-form-fields.md` § AIDA sentence):

| Field label | Field type | Notes |
|---|---|---|
| Enter your AIDA sentence here (ending with a full stop) | textarea, **required** | The atomic, independent, declarative, absolute sentence. Must end with a full stop. |
| Select related topics/tags | dropdown, **optional** | Predefined topic vocabulary — open the dropdown and pick available labels. |
| Relates to this nanopublication | text input, **required** | URI of the nanopub the AIDA derives from. For paper-rooted chains this is the Quote-with-comment URI. |
| Supported by datasets | repeatable group ("+ Add Item"), **optional** | DOI/URL of datasets that ground the AIDA claim. |
| Supported by other publications | repeatable group ("+ Add Item"), **optional** | DOI/URL of publications that support the AIDA claim. |

---

## Field-by-field draft

<!-- field: aida -->
### Enter your AIDA sentence here (textarea, required)

```
The globally averaged number of marine heatwave days per year increased by approximately 30 days between 1982 and 2016, from a baseline of about 25 days per year in the 1980s.
```

Character count: 176.

**Atomicity check.** One empirical finding: the magnitude of the increase in
globally averaged annual MHW days over the satellite record. The 1980s baseline
is not a second finding — it is the anchor that makes the increase quantitative,
and removing it would leave the sentence non-absolute ("increased by 30 days"
from what?).

The paper's sentence also reports increases in *frequency* and *duration*. Those
are **separate findings** and deliberately not folded in here: an AIDA containing
"and" linking distinct findings is non-atomic and cannot be cited individually
(`docs/forrt-form-fields.md` § Atomic AIDA rule). They belong on their own AIDA
sentences anchored on their own Claims, should this chain be extended.

**Whose claim is this?** The AIDA restates the **original paper's** finding, not
this replication's result. The replication's numbers belong in the Outcome
(step 05). This distinction is what lets the chain express "claim X was tested
and held" rather than collapsing claim and verdict into one assertion.

**Provenance.** Derived from the verbatim quote in `nanopubs/drafts/01_quote.md`,
itself extracted from `paper/oliver-2018.pdf` with `pdftotext` and matched
programmatically. Period stated as 1982–2016 because that is the satellite
record the quoted "35-year period" refers to (`00_paper_summary.md`).

<!-- field: topics -->
### Select related topics/tags (dropdown, optional)

*Select in the form* — this is a closed vocabulary rendered as a dropdown, and
its option list is not documented in `docs/forrt-form-fields.md`. Per the
pre-flight checklist, values are not invented here.

Open the dropdown and look for terms matching: *marine heatwave*, *sea surface
temperature*, *climate change*, *oceanography*. Pick only labels that actually
appear.

<!-- field: relates -->
### Relates to this nanopublication (text input, required)

```
«URI of step 01 (Quote-with-comment)»
```

Filled automatically by the Science Live chain wizard, which carries each
published URI into the next step's back-reference. If publishing by hand, paste
the Quote URI from `nanopubs/PUBLISHED.md` row 01.

<!-- field: datasets -->
### Supported by datasets (repeatable, optional)

*(skip — optional)*

Deliberately left empty. Two reasons:

1. **Scope.** This AIDA states the *original paper's* finding, which rests on
   NOAA OI SST and HadISST. The ESA SST CCI record this replication used grounds
   the **Outcome**, not the claim under test, and is cited there.
2. **Known platform bug** (`docs/forrt-form-fields.md`, 2026-04-26): publishing
   with both *Supported by datasets* and *Supported by other publications*
   populated has previously failed on Science Live. Only one group is populated
   here, and the publication is the more informative of the two.

<!-- field: publications -->
### Supported by other publications (repeatable, optional)

**Item 1**

```
https://doi.org/10.1038/s41467-018-03732-9
```

Oliver, E. C. J. et al. (2018), *Longer and more frequent marine heatwaves over
the past century*, Nature Communications 9:1324 — the source of the quoted
claim. Verified to resolve (HTTP 200).

---

## Pre-flight checklist

- [x] Section for this template found in `docs/forrt-form-fields.md`
- [x] Section is documented (not "needs screenshot")
- [x] Every field enumerated in form order; optional fields explicitly resolved
- [x] No invented field names
- [x] No "form may have other fields" caveats
- [x] Documented field list pasted at the top
- [x] AIDA is atomic — one empirical finding, ends with a full stop
