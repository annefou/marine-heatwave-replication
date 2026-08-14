#!/usr/bin/env python
"""Compare the headline statistics of two complete pipeline runs.

This exists because XMHW fails non-deterministically on a few percent of
latitude blocks (measured 2-8% across runs, with no pattern in latitude or data
coverage) and the same block succeeds when retried. That raised a fair question
for a REPLICATION study: if the failures are not reproducible, are the numbers?

Running the pipeline twice and diffing the headline JSONs answers it directly.
On 2026-08-14 two independent complete runs -- which failed on different blocks,
3 and 11 respectively -- produced IDENTICAL values to all reported digits. That
converts an open worry into a bounded, disclosable statement: the failures are
an operational property requiring retry logic, not a source of scientific
uncertainty.

Re-run this whenever the detection code, XMHW version, or input data changes.

Usage:
    pixi run python scripts/compare_runs.py RUN_A.json RUN_B.json
    pixi run python scripts/compare_runs.py            # backup vs current

Exits 0 if every compared metric is identical, 1 otherwise.
"""

import json
import sys
from pathlib import Path

DEFAULT_A = "results/run1_backup/headline_comparison.json"
DEFAULT_B = "results/headline_comparison.json"

# (section, key) pairs that constitute the reported result.
METRICS = [
    ("mhw_days", "replication_change_over_record"),
    ("mhw_days", "replication_baseline_1980s"),
    ("mhw_days", "replication_trend_per_decade"),
    ("mhw_frequency", "replication_trend_per_decade"),
    ("mhw_duration", "replication_trend_per_decade"),
]
# Provenance that must also agree, or the runs are not comparable at all.
PROVENANCE = ["resolution_deg", "lon_band_stride", "n_cells",
              "software_version", "is_full_replication"]


def main(path_a: str, path_b: str) -> int:
    for p in (path_a, path_b):
        if not Path(p).exists():
            print(f"error: {p} does not exist", file=sys.stderr)
            return 2
    a = json.loads(Path(path_a).read_text())
    b = json.loads(Path(path_b).read_text())

    print(f"A: {path_a}")
    print(f"B: {path_b}\n")

    # A difference in configuration makes any metric comparison meaningless,
    # so check it first and refuse rather than reporting a misleading delta.
    mismatched = [
        k for k in PROVENANCE
        if a["replication"].get(k) != b["replication"].get(k)
    ]
    if mismatched:
        print("CONFIGURATION DIFFERS — these runs are not comparable:")
        for k in mismatched:
            print(f"  {k}: {a['replication'].get(k)!r} vs {b['replication'].get(k)!r}")
        return 1

    print(f"{'metric':52s} {'A':>10s} {'B':>10s} {'delta':>10s}")
    print("-" * 86)
    worst = 0.0
    for section, key in METRICS:
        x, y = a[section][key], b[section][key]
        d = y - x
        worst = max(worst, abs(d))
        print(f"{section + '.' + key:52s} {x:10.4f} {y:10.4f} {d:+10.4f}")

    print(f"\nlargest absolute change: {worst:.6f}")
    if worst == 0:
        print("IDENTICAL — the pipeline reproduces its own numbers exactly.")
        return 0
    print("DIFFERS — the pipeline is not bit-reproducible across runs. "
          "This belongs in the Outcome's limitations.")
    return 1


if __name__ == "__main__":
    args = sys.argv[1:]
    a, b = (args + [DEFAULT_A, DEFAULT_B][len(args):])[:2] if args else (DEFAULT_A, DEFAULT_B)
    raise SystemExit(main(a, b))
