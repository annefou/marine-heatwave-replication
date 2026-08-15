# Published nanopub chain — URI registry

This file is the canonical registry of published nanopub URIs for this replication. Update it as you publish each step.

## Chain

| Step | Template | URI | Published |
|---|---|---|---|
| 01 | Quote-with-comment (or PICO / PCC) | https://w3id.org/sciencelive/np/RA1m-2tHCFBVjypflopbfGnuEpxrzPE_khGhss1FJMtbA | 2026-08-15 |
| 02 | AIDA Sentence | https://w3id.org/sciencelive/np/RAmbschSgs8k_AoM34DgIWT0EMkrwKYKEWQFIXkslMtfM | 2026-08-15 |
| 03 | FORRT Claim | https://w3id.org/sciencelive/np/RAGw-EZjva3ybpqWtY3loRFToZrm6GSMQqamvoe-e-JjE | 2026-08-15 |
| 04 | FORRT Replication Study | https://w3id.org/sciencelive/np/RAdIP7v2kJyOD-hRDIKdZkjMfFHkOIKdWoSnvAeGasU_s | 2026-08-15 |
| 05 | FORRT Replication Outcome | https://w3id.org/sciencelive/np/RAGjvtR-Pq6576AIEsj5CTiLW3yK0cPEbfgk7OjhxyVVM | 2026-08-15 |
| 06 | CiTO Citation | https://w3id.org/sciencelive/np/RAnns3mUVRk1WNb6SAuAunHiGGZL4eD9c_Axx-8eCj0x4 | 2026-08-15 |

Published on **platform-dev** (`api-dev.sciencelive4all.org`). Verified GREEN by
`/verify-chain` on 2026-08-15: all six URIs appear in the constellation, the
Outcome's repository DOI and `CITATION.cff`'s DOI resolve to the same Zenodo
record, and the CiTO's cited DOI resolves.

## Optional layers

| Step | Template | URI | Published |
|---|---|---|---|
| 07 | Research Software (if applicable) | _not applicable_ | |
| 08 | Research Synthesis (if applicable) | _not applicable_ | |

Both were considered and deliberately not published:

- **07 Research Software** — `CLAUDE.md` reserves this for a reusable software
  artefact, "a `pip install`-able tool, not a one-off demo repo". This is a
  replication study; the software is cited from the Outcome instead.
- **08 Research Synthesis** — the template synthesises findings across
  *multiple* replication outcomes. This is one chain with one Outcome, so a
  synthesis would restate it and assert a cross-cutting finding that does not
  exist. It becomes appropriate if this claim is later tested by further
  independent chains. See `nanopubs/drafts/08_synthesis.md`.

## Format

URIs from Science Live are of the form `https://w3id.org/sciencelive/np/RA…`. URIs from Nanodash (used as a fallback when the Science Live UI hits a bug) are of the form `https://w3id.org/np/RA…`. Both are valid and citable.

If a URI is not in the Science Live namespace, view it via the Science Live viewer by wrapping the URI:

```
https://platform.sciencelive4all.org/np/?uri=<full-URI>
```

## Cross-references

- Drafts: `nanopubs/drafts/`
- Form structure: `docs/forrt-form-fields.md`
- Chain shape decision: `docs/chain-decision-tree.md`
