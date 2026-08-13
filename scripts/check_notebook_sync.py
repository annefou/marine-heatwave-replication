#!/usr/bin/env python
"""Check each committed .ipynb matches its .py source and carries outputs.

The Jupyter Book renders the committed notebooks/*.ipynb rather than executing
them (the pipeline is ~8 core-hours and needs Copernicus credentials -- see
docs/cicd-conventions.md). That buys a book with real results, at the cost of
two failure modes this script exists to close:

  1. Someone edits the .py and does not re-execute, so the book shows results
     produced by code that no longer exists.
  2. Someone commits a converted-but-never-executed .ipynb, which renders as a
     book with empty figure cells.

Comparing the files as *text* does not work: round-tripping an .ipynb back to
py:percent drops the `formats:` key and rewrites `jupytext_version`, so a plain
diff reports every notebook as stale. This compares CELL CONTENT, which is what
"in sync" actually means.

    pixi run python scripts/check_notebook_sync.py [notebooks/]

Exit 0 if every notebook is in sync and executed, 1 otherwise.
"""

import sys
from pathlib import Path

import jupytext


def cells_of(path: Path) -> list[tuple[str, str]]:
    """(cell_type, source) per cell, whitespace-normalised."""
    nb = jupytext.read(path)
    return [
        (c["cell_type"], c["source"].strip())
        for c in nb.cells
        if c["source"].strip()
    ]


def has_outputs(path: Path) -> bool:
    nb = jupytext.read(path)
    return any(
        c["cell_type"] == "code" and c.get("outputs") for c in nb.cells
    )


def check(nb_dir: Path) -> int:
    sources = sorted(nb_dir.glob("*.py"))
    if not sources:
        print(f"no .py notebooks in {nb_dir}", file=sys.stderr)
        return 1

    failures = 0
    for py in sources:
        ipynb = py.with_suffix(".ipynb")
        if not ipynb.exists():
            print(
                f"::error::{ipynb} is missing. The book renders committed "
                f"executed notebooks. Generate it with:\n"
                f"    pixi run jupytext --to notebook --execute {py}"
            )
            failures += 1
            continue

        if cells_of(py) != cells_of(ipynb):
            print(
                f"::error::{ipynb} is out of sync with {py}. The book would "
                f"show results from code that no longer exists. Re-execute:\n"
                f"    pixi run jupytext --to notebook --execute {py}"
            )
            failures += 1
        elif not has_outputs(ipynb):
            print(
                f"::error::{ipynb} has no cell outputs -- it was converted but "
                f"never executed, so the book would render empty. Re-execute:\n"
                f"    pixi run jupytext --to notebook --execute {py}"
            )
            failures += 1
        else:
            print(f"  ok   {ipynb.name} matches {py.name} and carries outputs")

    if failures:
        print(f"\n{failures} notebook(s) need re-executing.")
        return 1
    print(f"\nAll {len(sources)} notebooks are in sync and executed.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "notebooks")
    raise SystemExit(check(target))
