#!/usr/bin/env bash
# 05 (ENSO removal) then 03 in ENSO mode -> the red line of Fig 2.
set -uo pipefail
cd /home/ubuntu/openaire/marine-heatwave-replication || exit 1
LOG=results/logs/enso.log
say() { echo "[enso $(date -u +%H:%M:%S)] $*" >> "$LOG"; }
: > "$LOG"
PIXI="$HOME/.pixi/bin/pixi"

say "stage 1: 05_enso_removal (MEI regression, +/-12 month lags)"
if ( cd notebooks && MHW_TARGET_RES_DEG=1 "$PIXI" run python 05_enso_removal.py ) \
     >> results/logs/05_enso_removal.log 2>&1; then
  say "stage 1: OK"
else
  say "stage 1: FAILED — see results/logs/05_enso_removal.log"
  tail -15 results/logs/05_enso_removal.log >> "$LOG"
  exit 1
fi

say "stage 2: 03 in ENSO mode (original threshold, ENSO-less series)"
if ( cd notebooks && MHW_TARGET_RES_DEG=1 MHW_LON_BAND_STRIDE=1 MHW_ENSO_REMOVED=1 \
       "$PIXI" run python 03_analysis.py ) \
     >> results/logs/03_analysis_enso.log 2>&1; then
  say "stage 2: OK"
else
  say "stage 2: FAILED — see results/logs/03_analysis_enso.log"
  tail -15 results/logs/03_analysis_enso.log >> "$LOG"
  exit 1
fi
say "COMPLETE — results/mhw_annual_1deg_enso_removed.nc ready for Fig 2"
