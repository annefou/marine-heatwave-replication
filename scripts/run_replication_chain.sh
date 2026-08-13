#!/usr/bin/env bash
# Wait for 01_data_download to finish, then run 02 -> 03 -> 04 in sequence.
#
# 01 is launched separately (it is the long streaming download); this script
# picks up as soon as its output file appears and drives the rest of the
# pipeline unattended. Logs land in results/logs/.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
REPO="$PWD"
PIXI="$HOME/.pixi/bin/pixi"
RES="${MHW_TARGET_RES_DEG:-1}"
RES="$(python3 -c "print(f'{float(\"$RES\"):g}')")"
STRIDE="${MHW_LON_BAND_STRIDE:-1}"
RAW="$REPO/data/raw/sst_cci_${RES}deg_stride${STRIDE}.nc"

mkdir -p "$REPO/results/logs"

echo "[chain] waiting for $RAW"
while [ ! -f "$RAW" ]; do
  # Bail out if the downloader died without producing its output.
  if ! pgrep -f "01_data_download.py" >/dev/null 2>&1; then
    if [ ! -f "$RAW" ]; then
      echo "[chain] ERROR: downloader is gone and $RAW was never written" >&2
      tail -5 "$REPO/data/raw/download.log" >&2 2>/dev/null
      exit 1
    fi
  fi
  sleep 30
done
echo "[chain] raw data present: $(du -h "$RAW" | cut -f1)"

cd "$REPO/notebooks" || exit 1
for nb in 02_data_clean 03_analysis 04_figures; do
  echo "[chain] === $nb === $(date -u +%H:%M:%S)"
  if ! "$PIXI" run python "$nb.py" > "$REPO/results/logs/$nb.log" 2>&1; then
    echo "[chain] FAILED at $nb — see results/logs/$nb.log" >&2
    tail -20 "$REPO/results/logs/$nb.log" >&2
    exit 1
  fi
  echo "[chain] $nb OK"
done
echo "[chain] complete $(date -u +%H:%M:%S)"
