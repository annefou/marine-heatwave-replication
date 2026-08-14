# Verification checks

Every number the Replication Outcome states should be re-derivable. These
scripts exist because each one produced a claim that ended up in the write-up,
and a claim whose supporting check cannot be re-run is an assertion, not
evidence.

Run them all with `pixi run <task>`; each is standalone and offline.

| Claim in the Outcome | Check | Task |
|---|---|---|
| The longitude coverage gap does not bias the headline | `check_coverage_sensitivity.py` | `pixi run check-coverage` |
| Two complete runs give identical numbers | `compare_runs.py` | `pixi run compare-runs` |
| The figures are legible under colour-vision deficiency | `check_colorblind_safe.py` | `pixi run check-colors` |
| Stage 03's memory fits the machine | `probe_block.py` | `pixi run python scripts/probe_block.py 90 91` |
| The book renders code that still exists | `check_notebook_sync.py` | `pixi run -e tests check-notebooks` |

---

## `check-coverage` — is 93.3% longitude coverage enough?

`01_data_download.py` reads longitude in bands 60 native cells wide, starting
every 64 (the ARCO store's chunk width), so **0.2° is skipped every 3.2°** and
the analysis grid holds 336 of a possible 360 one-degree columns.

The check answers two questions that are easy to conflate.

**Sparse global sampling** — thinning the columns further, in the same comb
pattern, barely moves the result:

```
336 cols (full)   31.77 days
300 cols          31.49   (-0.28)
200 cols          31.76   (-0.01)
100 cols          31.12   (-0.66)

random draws dropping a further 6.7%:  sd 0.638 days
```

Even at 28% of the globe the headline holds to within 0.66 days. The noise
attributable to our actual gap is **±0.64 days** — about 2% of a statistic whose
trend CI is [6.35, 12.94] days/decade. The gap is immaterial, and that is
measured rather than argued.

**A small contiguous area** is a different matter entirely:

```
North Atlantic     48.22   (+51.8% vs global)
Tropical Pacific    8.84   (-72.2%)
Southern Ocean     15.44   (-51.4%)
Indian Ocean       51.42   (+61.8%)
NE Pacific 'blob'  49.41   (+55.5%)
```

Any single 40°×40° box lands 50–70% away from the global answer, in either
direction — pick one region and you could "confirm" or "contradict" the paper at
will. This panel exists because *"just run a small box, it's faster"* is a
natural suggestion, and the refusal needs to be evidence.

The distinction: a regular global subsample is an **unbiased estimator of the
global mean**; a region is a **different quantity**. MHW trends are strongly
heterogeneous in space — the subject of the paper's own Fig. 3. The claim under
test is explicitly global, so the scope must stay global. Shrink the grid for
the *code* (as `ci.yml`'s smoke run does), never for the *claim*.

---

## `compare-runs` — are the numbers reproducible?

XMHW fails non-deterministically on a few percent of latitude blocks with
`InvalidIndexError`, and the same block succeeds when retried — measured at
**3/145 on one pass and 11/145 on the next**, with no pattern in latitude or in
data coverage. For a replication study that raises a fair question: if the
failures are not reproducible, are the results?

Two complete independent runs, which failed on **different** blocks, were
compared:

```
change over record    31.770 -> 31.770   +0.0000
baseline 1980s        21.700 -> 21.700   +0.0000
trend per decade       9.344 ->  9.344   +0.0000
frequency trend        0.433 ->  0.433   +0.0000
duration trend         1.482 ->  1.482   +0.0000
IDENTICAL
```

So the failures are an **operational** property requiring retry logic (now built
into `03_analysis.py` via `MAX_BLOCK_ATTEMPTS`), not a source of scientific
uncertainty. That is the disclosable statement; without this check the honest
version would have been the much weaker "results may not be reproducible".

The script refuses to compare runs whose configuration differs (resolution,
stride, cell count, XMHW version), rather than reporting a misleading delta.

Re-run it whenever the detection code, the XMHW revision, or the input data
changes.

---

## `check-colors` — is the palette legible to everyone?

The figures match Oliver et al. colour-for-colour so a reader can lay them side
by side and judge the replication by eye. That only works if the palette is
legible to everyone, so the borrowed colours are verified rather than assumed.

Colours are **sampled from the paper's own figure** at 200 dpi
(`pdftoppm -r 200`), not eyeballed:

```
black line #000000   red line #ed3c3c
El Nino    #f3b9b9   La Nina  #b3b3f3
```

Simulation uses the Machado, Oliveira & Fernandes (2009) severity-1.0 matrices
in **linear** RGB (where they are defined — applying them to gamma-encoded sRGB
is a common error), compared as CIE Lab ΔE76.

Result: worst separation **ΔE 36.9** under any deficiency, against a threshold
of 20. The paper's palette is already safe — not by luck, but because it uses a
**blue/red** opposition rather than red/green. So we match it exactly and change
nothing.

Verified against a negative control: `#d62728` vs `#2ca02c` (a red/green pair)
correctly fails at ΔE 7.3.

Pass any hex colours as arguments to check a different palette. Exits 1 on
failure, so it can gate a figure change.
