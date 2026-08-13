# 01 — Quote-with-comment (paper-rooted chains)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.

**Documented field list** (from `docs/forrt-form-fields.md` § Quote-with-comment, form
heading *"Annotate a paper quotation — Annotating a paper quotation with personal
interpretation"*): Cited DOI (text input) · Quote whole text / Quote start-end (radio) ·
Quoted Text (textarea, required, ≤500) · Comment (textarea, required, ≤500 enforced live).

**Form heading:** *"Annotate a paper quotation — Annotating a paper quotation with personal interpretation"*

## Field-by-field draft

<!-- field: paper -->
### Cited DOI (text input, required)

Format: starts with `10.` — bare DOI, **NOT** `https://doi.org/...` form.

```
10.1038/s41467-018-03732-9
```

### Quote mode (radio button)

- [x] **Quote whole text (less than 500 characters)**
- [ ] Quote start/end *(use this if the quote exceeds 500 chars)*

<!-- field: quotation -->
### The exact quotation from the paper (max. 500 characters) (textarea, required)

Verbatim from the paper PDF in `paper/`. Character-for-character. ≤ 500 chars in whole-text mode.

> _Read the PDF first. Don't paraphrase from memory. See `docs/verify-before-drafting.md`._

```
The increases in frequency and duration metrics translate to 30 additional marine heatwave days per year by the end of the 35-year period (p < 0.01; based on a linear trend) from a baseline level of about 25 days in the 1980s (Fig. 2).
```

Character count: 235 / 500.

**Provenance of this quote.** `paper/oliver-2018.pdf`, Results § "Marine heatwaves over the
satellite record", the paragraph describing Fig. 2. Extracted with `pdftotext` (text layer,
not transcribed by eye) and matched programmatically against the PDF. Two normalisations
were applied, both font/extraction artefacts rather than differences in the text: the
`ﬁ`/`ﬂ` ligatures render as `fi`/`fl`, and `pdftotext` drops the hyphen when rejoining the
line-broken `35-\nyear`, which is `35-year` in the PDF.

**Why this sentence and not the abstract's "54%" sentence.** The 34% / 17% / 54% figures
come from a monthly *proxy* reconstruction comparing 1925–1954 with 1987–2016 (Fig. 5),
not from the daily satellite record, and no satellite SST product reaches before ~1981.
The sentence quoted here is the paper's daily-satellite statement of the same quantity —
total annual MHW days — and is the one an independent satellite record can address. See
`00_paper_summary.md` § "Why not the abstract's 54% sentence".

<!-- field: quotation-end -->
### End of quotation (optional - use when quoting beginning and end of a longer passage, max. 500 characters) (textarea, optional)

*(skip — optional; the quote fits whole-text mode at 233 characters)*

```

```

<!-- field: comment -->
### Our interpretation and explanation of why this quotation is relevant (max. 800 characters) (textarea, required)

Why this quote matters and what the replication tests. Don't repeat the quote.

> _Must stand alone: true independently of any replication. Do not describe this study's design. Live form enforces 500 characters._

```
This is where the paper's century-scale narrative reduces to a directly measurable quantity: globally averaged total marine heatwave days per year, from daily satellite SST under a fixed 90th-percentile, five-day detection rule. Unlike the abstract's 34/17/54% figures, which rest on a monthly proxy reconstruction of the pre-satellite era, this number is computed from observed daily fields, so any independent daily SST record can test it.
```

Character count: 441 / 500.

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 01.
