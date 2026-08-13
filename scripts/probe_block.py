#!/usr/bin/env python
"""Measure one 03_analysis latitude block's wall time and peak memory.

Stage 03 is the expensive stage, and its per-worker peak memory sets how many
workers fit in RAM. Guessing that number once cost a multi-hour run to an OOM
kill, so measure it on the target machine instead:

    pixi run python scripts/probe_block.py 90 92     # a full-ocean tropical block

Pick a block with no land for the worst case — peak scales with the number of
valid ocean cells. Then set MHW_WORKERS so workers x peak fits in RAM with
headroom, and MHW_LAT_BLOCK to trade per-worker memory against per-block
overhead.

Runs the real run_block() from the notebook, so it measures what the pipeline
actually does, including the checkpoint write.
"""

import os
import resource
import sys
import time
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parent.parent / "notebooks" / "03_analysis.py"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    lat0, lat1 = int(sys.argv[1]), int(sys.argv[2])

    # The notebook's paths are relative to notebooks/, so run from there.
    os.chdir(NOTEBOOK.parent)

    # Import the notebook's definitions without running its __main__ block.
    src = NOTEBOOK.read_text().split('if __name__ == "__main__":')[0]
    ns: dict = {"__name__": "probe"}
    exec(compile(src, str(NOTEBOOK), "exec"), ns)  # noqa: S102

    t = time.time()
    res = ns["run_block"]((str(ns["IN_PATH"]), lat0, lat1))
    peak_gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    cells = "land/masked" if res is None else f"{res.sizes['longitude']} ocean cells"
    print(
        f"lat[{lat0}:{lat1}]  {time.time() - t:7.1f}s  "
        f"peak_rss={peak_gb:5.2f} GB  {cells}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
