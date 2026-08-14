#!/usr/bin/env python
"""How much does the headline statistic depend on WHICH ocean was sampled?

This backs a specific claim in the Replication Outcome's limitations. The ARCO
read in 01_data_download samples 336 of 360 one-degree longitude columns: bands
are 60 native cells wide but start every 64, so 0.2 deg is skipped every 3.2
deg, leaving 93.3% longitude coverage. This script measures whether that
matters, rather than asserting that it does not.

It answers two questions that are easy to conflate:

  1. SPARSE GLOBAL SAMPLING -- dropping a regular comb of longitude columns.
     This is what our real coverage gap is. It should be near-harmless: a
     regular subsample is an unbiased estimator of a global mean.

  2. A SMALL CONTIGUOUS AREA -- can one region stand in for the global claim?
     It cannot, and the numbers show why: MHW trends are strongly
     heterogeneous in space, which is the subject of the paper's own Fig. 3.
     This panel exists because "just run a small box, it's faster" is a
     natural suggestion, and the answer needs to be evidence, not assertion.

Usage:
    pixi run python scripts/check_coverage_sensitivity.py [results/mhw_annual_1deg.nc]

Exits 0 always; this is a measurement, not a pass/fail gate.
"""

import sys
from itertools import product

import numpy as np
import xarray as xr
from scipy import stats

# 40x40 degree boxes spanning distinct MHW regimes.
REGIONS = {
    "North Atlantic": (30, 70, -60, -20),
    "Tropical Pacific": (-20, 20, -180, -140),
    "Southern Ocean": (-60, -20, 0, 40),
    "Indian Ocean": (-30, 10, 60, 100),
    "NE Pacific 'blob'": (30, 60, -160, -120),
}
N_DRAWS = 60
FULL_GRID_COLUMNS = 360  # a complete 1 degree global grid


def headline(da: xr.DataArray, years: np.ndarray) -> float:
    """Change in area-weighted global-mean MHW days over the record.

    Theil-Sen, matching 03_analysis.py and the paper's stated estimator.
    """
    w = np.cos(np.deg2rad(da.latitude))
    g = da.weighted(w).mean(dim=["latitude", "longitude"]).values
    ok = np.isfinite(g)
    if ok.sum() < 10:
        return float("nan")
    slope, *_ = stats.theilslopes(g[ok], years[ok], alpha=0.95)
    return float(slope * (years[-1] - years[0]))


def main(path: str) -> int:
    ds = xr.open_dataset(path)
    days = ds["mhw_days"]
    years = ds.year.values.astype(float)
    nlon = days.sizes["longitude"]

    full = headline(days, years)
    print(f"full sample: {nlon} longitude columns "
          f"({100 * nlon / FULL_GRID_COLUMNS:.1f}% of a complete 1 deg grid)")
    print(f"headline: {full:.2f} days added over the record\n")

    print("1. SPARSE GLOBAL SUBSAMPLING (comb pattern, as our real gaps are)")
    for keep in (300, 250, 200, 150, 100):
        if keep >= nlon:
            continue
        idx = np.linspace(0, nlon - 1, keep).astype(int)
        h = headline(days.isel(longitude=idx), years)
        print(f"   {keep:4d} cols ({100 * keep / FULL_GRID_COLUMNS:5.1f}% of full): "
              f"{h:6.2f}   delta {h - full:+6.2f}")

    # Apply the SAME fractional loss again (336/360) many times, at random, to
    # estimate the sampling noise our actual gap introduces.
    keep = int(round(nlon * nlon / FULL_GRID_COLUMNS))
    rng = np.random.default_rng(0)
    hs = np.array([
        headline(days.isel(longitude=np.sort(rng.choice(nlon, keep, replace=False))), years)
        for _ in range(N_DRAWS)
    ])
    print(f"\n   random draws dropping a further "
          f"{100 * (1 - nlon / FULL_GRID_COLUMNS):.1f}% ({N_DRAWS} draws of {keep} cols):")
    print(f"   mean {hs.mean():6.2f}   sd {hs.std():.3f}   "
          f"range [{hs.min():.2f}, {hs.max():.2f}]")
    print(f"   => sampling noise attributable to the coverage gap: "
          f"+/- {hs.std():.3f} days")

    print("\n2. SMALL CONTIGUOUS AREAS (40x40 deg boxes)")
    print("   A region is a DIFFERENT quantity, not a cheaper estimate of the")
    print("   global mean. The spread below is why the claim must stay global.")
    for name, (la0, la1, lo0, lo1) in REGIONS.items():
        sub = days.sel(latitude=slice(la0, la1), longitude=slice(lo0, lo1))
        if 0 in (sub.sizes["latitude"], sub.sizes["longitude"]):
            print(f"   {name:18s}: no cells in this grid")
            continue
        h = headline(sub, years)
        print(f"   {name:18s}: {h:6.2f}   delta {h - full:+6.2f}   "
              f"({100 * (h - full) / full:+6.1f}% vs global)")
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "results/mhw_annual_1deg.nc"
    raise SystemExit(main(target))
