# 08 — Research Synthesis

> **NOT APPLICABLE to this replication — deliberately not published.**
>
> The template's own description is *"Synthesise findings across **multiple**
> replication outcomes"*, and `docs/forrt-form-fields.md` is explicit that it
> exists to *"bind multiple parallel FORRT chains together under one
> cross-cutting conclusion"* — the typical case being three Outcomes from three
> independent chains testing different facets of a shared property.
>
> This repository publishes **one** chain with **one** Outcome. A synthesis over
> a single outcome is not a synthesis: its four required fields (Conclusion,
> Recommendations, Conditions, Limitations) would restate the Outcome's, and it
> would assert a cross-cutting finding on a public network that does not exist.
>
> It becomes appropriate if this claim is later tested by further independent
> chains — then the synthesis names what they jointly establish.
>
> This file is kept as a skeleton, unfilled, so the option stays visible. It is
> excluded from `chain-draft.json` because no field carries a value; it was
> previously included only because the shipped skeleton had a date in a fence,
> which `build_chain_draft.py` read as drafted content. (optional)

> Run the pre-flight checklist in `docs/forrt-form-fields.md` § Pre-flight checklist before drafting.
>
> Use this template only when this chain is **one of several** testing facets of a shared underlying property. The Synthesis names the cross-cutting conclusion and lists the multiple Outcomes as supporting sources.

**Form heading:** *"Science Live Research Synthesis — Synthesise findings across multiple replication outcomes with conclusions, recommendations, conditions, and limitations."*

## Field-by-field draft

<!-- field: synthesis -->
### Short URI suffix for synthesis ID (text input, required)

Slug. Use kebab-case.

```

```

<!-- field: label -->
### Label (text input, required)

A one-line summary.

```

```

<!-- field: conclusion -->
### Conclusion of the synthesis (textarea, required)

The aggregate finding across the underlying outcomes.

```

```

<!-- field: recommendation -->
### Recommendations (textarea, required)

Actionable guidance for practitioners.

```

```

<!-- field: conditions -->
### Conditions under which the synthesis applies (textarea, required)

Scope: data types, methods, domains, regions, time periods.

```

```

<!-- field: limitations -->
### Limitations of the synthesis (textarea, required)

What was not tested? What might not generalise?

```

```

<!-- field: date -->
### Completion date (text input, required)

```
```

*(empty — this step is not applicable; see the note at the top)*

<!-- field: source -->
### Supporting sources (text input, required)

Each entry is a URL — typically the FORRT Outcome URIs being synthesised. Pull from `nanopubs/PUBLISHED.md` (and/or registries from sibling repos).

- _Source URL 1 (Outcome from this chain): ___
- _Source URL 2 (Outcome from a sibling chain): ___
- _Source URL 3 (Research Software nanopub if applicable): ___

<!-- field: topic -->
### Topic (search/select, required)

Provide labels (not QIDs).

- _Label 1: ___

## Publication note

After publishing, paste the resulting URI into `nanopubs/PUBLISHED.md` step 08.
