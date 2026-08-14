#!/usr/bin/env python
"""Check a figure palette is distinguishable under colour-vision deficiency.

The replication figures deliberately match Oliver et al. (2018) colour-for-
colour, so a reader can lay them side by side and judge the replication by eye.
That only works if the palette is legible to everyone, so the match is verified
rather than assumed -- and if a borrowed palette turned out to be unsafe, we
would depart from it and say so.

Method: Machado, Oliveira & Fernandes (2009) severity-1.0 simulation matrices,
applied in LINEAR RGB (they are defined there, not in gamma-encoded sRGB), then
compared as CIE Lab dE76.

    dE < 10   effectively indistinguishable at a glance
    dE < 20   uncomfortable for adjacent categorical elements  -> FAIL
    dE > 20   usable

Usage:
    pixi run python scripts/check_colorblind_safe.py                # figure palette
    pixi run python scripts/check_colorblind_safe.py '#ed3c3c' '#000000' ...

Exits 1 if any pair falls below the threshold under any deficiency type, so it
can gate a figure change.
"""

import sys
from itertools import combinations

import numpy as np

THRESHOLD = 20.0

# Sampled from the paper's own Fig. 2 legend swatches at 200 dpi
# (pdftoppm -r 200), not eyeballed.
PAPER_FIG2 = {
    "black line (global avg)": "#000000",
    "red line (excluding ENSO)": "#ed3c3c",
    "El Nino shading": "#f3b9b9",
    "La Nina shading": "#b3b3f3",
}

MATRICES = {
    "deuteranopia": [[0.367322, 0.860646, -0.227968],
                     [0.280085, 0.672501, 0.047413],
                     [-0.011820, 0.042940, 0.968881]],
    "protanopia": [[0.152286, 1.052583, -0.204868],
                   [0.114503, 0.786281, 0.099216],
                   [-0.003882, -0.048116, 1.051998]],
    "tritanopia": [[1.255528, -0.076749, -0.178779],
                   [-0.078411, 0.930809, 0.147602],
                   [0.004733, 0.691367, 0.303900]],
}


def hex_to_rgb(h: str) -> np.ndarray:
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255


def to_lab(rgb: np.ndarray) -> np.ndarray:
    r, g, b = srgb_to_linear(np.asarray(rgb, dtype=float))
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 1.0
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883

    def f(t):
        return np.cbrt(t) if t > 0.008856 else (7.787 * t + 16 / 116)

    fx, fy, fz = f(x), f(y), f(z)
    return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])


def simulate(rgb: np.ndarray, kind: str) -> np.ndarray:
    return linear_to_srgb(np.array(MATRICES[kind]) @ srgb_to_linear(np.asarray(rgb, float)))


def delta_e(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(to_lab(a) - to_lab(b)))


def main(palette: dict[str, str]) -> int:
    rgb = {k: hex_to_rgb(v) for k, v in palette.items()}
    kinds = list(MATRICES)
    header = f"{'pair':44s} {'normal':>8s}" + "".join(f"{k[:6]:>9s}" for k in kinds)
    print(header)
    print("-" * len(header))

    worst, failures = float("inf"), []
    for a, b in combinations(rgb, 2):
        row = [delta_e(rgb[a], rgb[b])]
        row += [delta_e(simulate(rgb[a], k), simulate(rgb[b], k)) for k in kinds]
        lo = min(row[1:])
        worst = min(worst, lo)
        flag = ""
        if lo < THRESHOLD:
            failures.append((a, b, lo))
            flag = "  <-- FAIL"
        print(f"{a + ' vs ' + b:44s} " + " ".join(f"{v:8.1f}" for v in row) + flag)

    print(f"\nworst separation under any deficiency: dE {worst:.1f} "
          f"(threshold {THRESHOLD:.0f})")
    if failures:
        print(f"{len(failures)} pair(s) too close — adjust the palette:")
        for a, b, lo in failures:
            print(f"  {a} vs {b}: dE {lo:.1f}")
        return 1
    print("PASS — every pair stays distinguishable under deuteranopia, "
          "protanopia and tritanopia.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pal = {f"colour {i + 1}": c for i, c in enumerate(sys.argv[1:])}
    else:
        pal = PAPER_FIG2
    raise SystemExit(main(pal))
