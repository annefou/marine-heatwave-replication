# marine-heatwave-replication

[![CI](https://github.com/annefou/marine-heatwave-replication/actions/workflows/ci.yml/badge.svg)](https://github.com/annefou/marine-heatwave-replication/actions/workflows/ci.yml)
[![Jupyter Book](https://github.com/annefou/marine-heatwave-replication/actions/workflows/jupyter-book.yml/badge.svg)](https://annefou.github.io/marine-heatwave-replication/)
[![Docker](https://github.com/annefou/marine-heatwave-replication/actions/workflows/docker.yml/badge.svg)](https://github.com/annefou/marine-heatwave-replication/pkgs/container/marine-heatwave-replication)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DOI](https://zenodo.org/badge/DOI/{{ZENODO_DOI}}.svg)]({{ZENODO_DOI}})
[![FAIR4RS](https://img.shields.io/badge/FAIR4RS-conformant-brightgreen)](docs/fair4rs-checklist.md)
[![FORRT](https://img.shields.io/badge/FORRT-replication-blue)](https://forrt.org/)
[![Science Live](https://img.shields.io/badge/Science%20Live-nanopub%20chain-purple)](nanopubs/PUBLISHED.md)
[![RO-Crate](https://img.shields.io/badge/RO--Crate-1.2-orange)](ro-crate-metadata.json)
[![Software Heritage](https://archive.softwareheritage.org/badge/origin/https://github.com/annefou/marine-heatwave-replication/)](https://archive.softwareheritage.org/browse/origin/?origin_url=https://github.com/annefou/marine-heatwave-replication)

> **Longer and more frequent marine heatwaves over the past century** — replication study.
> Reference paper: [10.1038/s41467-018-03732-9](https://doi.org/10.1038/s41467-018-03732-9)

This is a self-contained replication of the headline claim of the reference paper. It produces a reproducible computational pipeline, a Zenodo-archived release with a citable DOI, and a FORRT-tagged nanopublication chain on the [Science Live platform](https://platform.sciencelive4all.org).

---

## Quick start

```bash
git clone https://github.com/annefou/marine-heatwave-replication.git
cd marine-heatwave-replication
pixi install
pixi run snakemake --cores 1
```

(Pixi resolves `pixi.toml` against the per-platform `pixi.lock`, installs the env under `.pixi/`, and provides `pixi run` for any task without needing an `activate` step.)

Or with Docker:

```bash
docker run --rm ghcr.io/annefou/marine-heatwave-replication:latest
```

The Jupyter Book version is at <https://annefou.github.io/marine-heatwave-replication/>.

---

## Reproducing this replication

**Read this before starting a full run.** The pipeline is not a five-minute job,
and it needs an account.

### What you need

| | |
|---|---|
| **Copernicus Marine account** | Free, at <https://data.marine.copernicus.eu/register>. Then `copernicusmarine login` once, or set `COPERNICUSMARINE_SERVICE_USERNAME` / `_PASSWORD`. Stage 01 cannot run without it. |
| **Disk** | ~5 GB (≈1 GB cleaned SST, ~0.6 GB download bands, ~3 GB ENSO-removed SST, plus checkpoints) |
| **RAM** | **15 GB** at the default `MHW_WORKERS=5`. See "Tuning" below before running on a smaller machine. |
| **Time** | **~8 core-hours**, about 3.5 h wall-clock on 8 cores |

Nothing else is manual: every input is fetched by the notebooks themselves.

### Runtime, measured on 8 cores / 15 GB

| Stage | Wall time | What it does |
|---|---|---|
| `01_data_download` | ~55 min | Streams ESA SST CCI v3.0 from the CMEMS ARCO store, averaging 0.05° → 1° in flight |
| `02_data_clean` | ~1 min | Ice/land masking |
| `03_analysis` | ~1.3 h | MHW detection, ~6.7 core-hours over 30,774 ocean cells |
| `05_enso_removal` | ~10 min | Regresses SST on the MEI, subtracts the ENSO signal |
| `03` again (ENSO mode) | ~1.3 h | Re-detects on the ENSO-less series |
| `04_figures` | <1 min | |

### Every stage resumes

Kill it, lose a session, hit an OOM — nothing is lost. Re-run the same command
and it continues:

- `01` skips longitude bands already in `data/raw/bands_<res>deg/`
- `03` skips latitude blocks already in `results/blocks_<res>deg/`
- `05` skips latitude chunks already in `data/processed/enso_chunks_<res>deg/`

All are written to a temporary name and renamed atomically, so a process killed
mid-write cannot leave a truncated file that resume mistakes for finished work.

For a long run, detach it so it outlives your shell:

```bash
setsid nohup bash scripts/run_replication_chain.sh > results/logs/chain.log 2>&1 < /dev/null &
cat results/logs/STATUS      # stage + heartbeat
```

### Just want to check it works?

A coarse configuration exercises every stage in ~10 minutes. It does **not**
reproduce the result — outputs are named `partial_run_*` and figures are
watermarked, so they cannot be mistaken for it:

```bash
MHW_TARGET_RES_DEG=3 MHW_LON_BAND_STRIDE=8 pixi run snakemake --cores 2
```

Do not go above 3.2°: `01` derives `BAND_WIDTH = (64 // COARSEN) * COARSEN`, so a
coarser target floors it to zero and every band comes back empty *with no error*.

### Tuning

| Variable | Default | Notes |
|---|---|---|
| `MHW_WORKERS` | 5 | × per-block peak RSS must fit in RAM. **Measure first**: `pixi run python scripts/probe_block.py 90 91` (1.88 GB/block here). Guessing this once cost a run to an OOM kill. |
| `MHW_LAT_BLOCK` | 1 | Rows per block. Larger = more memory, no throughput gain (~0.78 s/cell either way). |
| `MHW_BLOCK_ATTEMPTS` | 4 | Retries per block. XMHW fails transiently on 2–8% of blocks and succeeds on retry — see below. |
| `MHW_TARGET_RES_DEG` | 1.0 | Analysis grid. |
| `MHW_LON_BAND_STRIDE` | 1 | 1 = full longitude sampling. |

### Known behaviour that is not a bug

**XMHW fails non-deterministically** on a few percent of latitude blocks with
`InvalidIndexError`, with no pattern in latitude or data coverage. The same block
succeeds when retried, which `03` now does automatically. It does **not** affect
results: two complete independent runs that failed on *different* blocks produced
identical headline numbers to all reported digits
(`pixi run compare-runs`).

### Verifying what you got

```bash
pixi run compare-runs      # two runs produce identical numbers?
pixi run check-coverage    # does the longitude sampling bias the headline?
pixi run check-colors      # are the figures colour-vision safe?
```

See [`docs/verification-checks.md`](docs/verification-checks.md) for what each
one established.

## Built from a template

This repository was created from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template). The template ships an operating manual for AI assistants ([`CLAUDE.md`](CLAUDE.md), [`AGENTS.md`](AGENTS.md)), domain conventions ([`DOMAIN.md`](DOMAIN.md)), and reference docs (`docs/`) so that an AI working only inside this repository can guide a researcher from "paper PDF + GitHub repo" to "published FORRT chain + Zenodo DOI" with no other context.

If you are reading this in a fresh fork, run [`/init-template`](.claude/skills/init-template/SKILL.md) inside Claude Code to substitute the placeholder tokens with your details. (For other AI tools, see [`docs/ai-portability.md`](docs/ai-portability.md).)

After `/init-template`, do these one-time setup steps to enable the full CI/CD path:

- **Enable GitHub Pages** at *Settings → Pages → Source: GitHub Actions*. Until enabled, the Jupyter Book build runs but the deploy step is skipped (CI stays green).
- All three workflows share one **readiness guard** (`.github/actions/check-ready`). Before `/init-template` runs, the `.template-uninitialised` sentinel makes them skip with an informative `::notice::` (badges stay green); `/init-template` deletes the sentinel, which activates them. They also skip while `notebooks/*.py` are still scaffolds (Phase 2). **Once you've published a nanopub chain** (real URIs in `nanopubs/PUBLISHED.md`), a skip is treated as a bug and **fails the run loudly** — so a finished replication can't sit on silently-green-but-empty CI.

## Repository structure

```
.
├── CLAUDE.md / AGENTS.md       # operating manual for AI assistants
├── DOMAIN.md                   # domain flavour (current: biodiversity + earth observation)
├── USER_PREFERENCES.md         # per-user style (edit on first clone)
├── README.md                   # this file
├── LICENSE                     # MIT
├── CITATION.cff                # how to cite
├── codemeta.json               # software metadata (CodeMeta-2.0)
├── ro-crate-metadata.json      # research object packaging (RO-Crate 1.2)
├── pixi.toml + pixi.lock       # pinned dependencies (single source of truth; lockfile is per-platform)
├── Dockerfile                  # container build
├── Snakefile                   # pipeline orchestration
├── myst.yml + index.md         # Jupyter Book scaffold
├── paper/                      # the source paper PDF
├── data/                       # downloaded artefacts (gitignored)
├── notebooks/                  # jupytext .py pipeline (01–04)
├── nanopubs/                   # FORRT chain drafts + published-URI registry
├── docs/                       # reference material
├── figures/                    # curated figures used in the Jupyter Book
├── .github/workflows/          # CI, Jupyter Book, Docker
└── .claude/                    # Claude Code agents, skills, sandbox config
```

## What you get

This template bakes in conventions that took multiple replications to discover. By using it, you inherit:

- **FAIR4RS conformance** — see [`docs/fair4rs-checklist.md`](docs/fair4rs-checklist.md) for the principle-by-principle mapping.
- **Self-contained data downloads** — the first notebook fetches everything; no manual data prep.
- **`pixi.toml` + `pixi.lock` as single source of truth** — local dev, Docker, and CI all install the same per-platform-pinned env.
- **`prefix-dev/setup-pixi`-based CI** — caches the env, runs the pipeline with `pixi run`, executes notebooks via a glob, fails fast on a stale lockfile.
- **Jupyter Book deployment** — auto-deploys to GitHub Pages with `BASE_URL` set correctly. (Don't put `base_url` in `myst.yml` — MyST silently ignores it.)
- **Docker + GHCR + Zenodo image archival** — `release` trigger pushes to GHCR and (optionally) archives to Zenodo for long-term preservation.
- **RO-Crate packaging** — the entire repo is a navigable Research Object via `ro-crate-metadata.json` (Process Run Crate + Workflow RO-Crate profiles).
- **Six-step FORRT chain workspace** — `nanopubs/drafts/` has a field-by-field skeleton for each step. `nanopubs/PUBLISHED.md` is the URI registry.
- **Layered AI guidance** — `CLAUDE.md` (universal) + `DOMAIN.md` (swappable per field) + `USER_PREFERENCES.md` (per-user). See [`docs/ai-portability.md`](docs/ai-portability.md) for non-Claude AI tools.
- **Sandbox by default** — `.claude/settings.json` denies file ops outside the repo, so a fresh AI session can't accidentally read `~/.ssh/` or write to `/etc/`.

## The six FORRT chain steps

A complete FORRT chain has six steps published on [platform.sciencelive4all.org](https://platform.sciencelive4all.org):

```
Quote-with-comment  →  AIDA  →  FORRT Claim  →  Replication Study  →  Replication Outcome  →  CiTO Citation
```

(For question-rooted chains with no upstream paper, replace step 1 with PICO or PCC. See [`docs/chain-decision-tree.md`](docs/chain-decision-tree.md).)

Drafts live in [`nanopubs/drafts/`](nanopubs/drafts/) field-by-field. Published URIs go into [`nanopubs/PUBLISHED.md`](nanopubs/PUBLISHED.md).

Optional further layers:

- **Research Software nanopub** — for reusable upstream tools (not demo repos). See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Software.
- **Research Synthesis nanopub** — when this chain is part of a multi-chain story. See [`docs/forrt-form-fields.md`](docs/forrt-form-fields.md) § Research Synthesis.

## After publishing

When the chain is live and the FAIR4RS checklist is green, drafting an announcement post is the next step. See [`docs/announcement-template.md`](docs/announcement-template.md) for the structural template (vision-piece-first; the worked replication is the payoff, not the lead).

For lower-level nanopub work — retraction, superseding, batch publishing — see [`docs/programmatic-nanopubs.md`](docs/programmatic-nanopubs.md).

## Citation

If you use this work, please cite both:

- This software: [`CITATION.cff`](CITATION.cff) → DOI [{{ZENODO_DOI}}]({{ZENODO_DOI}})
- The original paper: [10.1038/s41467-018-03732-9](https://doi.org/10.1038/s41467-018-03732-9)

## Acknowledgements

This repository was built from [`sciencelivehub/forrt-replication-template`](https://github.com/sciencelivehub/forrt-replication-template), part of the [Science Live platform](https://platform.sciencelive4all.org). The template is licensed MIT and contributions (especially new domain flavours under [`docs/domain-flavours/`](docs/domain-flavours/)) are welcome.
