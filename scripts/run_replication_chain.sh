#!/usr/bin/env bash
# Run the whole replication pipeline (01 -> 02 -> 03 -> 04) unattended.
#
# Designed to outlive the shell that started it. Launch it detached:
#
#   setsid nohup bash scripts/run_replication_chain.sh > results/logs/chain.log 2>&1 < /dev/null &
#
# setsid puts it in its own session so it survives the terminal, the SSH
# connection, or the agent session going away. Progress is in results/logs/,
# and a heartbeat plus the current stage are in results/logs/STATUS.
#
# Resumable. 01 skips longitude bands already on disk (written atomically, so a
# truncated band cannot be mistaken for a finished one), and any stage whose
# output already exists is skipped. Re-running after a kill picks up where it
# stopped; delete the relevant output to force a stage to re-run.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
REPO="$PWD"
PIXI="$HOME/.pixi/bin/pixi"

RES="${MHW_TARGET_RES_DEG:-1}"
RES="$(python3 -c "print(f'{float(\"$RES\"):g}')")"
STRIDE="${MHW_LON_BAND_STRIDE:-1}"
export MHW_TARGET_RES_DEG="$RES" MHW_LON_BAND_STRIDE="$STRIDE"

LOGS="$REPO/results/logs"
STATUS="$LOGS/STATUS"
mkdir -p "$LOGS"

RAW="$REPO/data/raw/sst_cci_${RES}deg_stride${STRIDE}.nc"
CLEAN="$REPO/data/processed/sst_clean_${RES}deg.nc"
ANNUAL="$REPO/results/mhw_annual_${RES}deg.nc"
MAINFIG="$REPO/figures/main_result.png"

say() { echo "[chain $(date -u +%H:%M:%S)] $*"; }

status() {
  { echo "stage=$1"
    echo "updated=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "pid=$$"
    echo "bands=$(ls "$REPO/data/raw/bands_${RES}deg"/band_*.nc 2>/dev/null | wc -l)"
  } > "$STATUS"
}

# stage <name> <notebook> <output-path>
stage() {
  local name="$1" nb="$2" out="$3"
  if [ -e "$out" ]; then
    say "$name: output exists, skipping ($out)"
    return 0
  fi
  say "$name: starting"
  status "$name"
  if ( cd "$REPO/notebooks" && "$PIXI" run python "$nb.py" ) \
        > "$LOGS/$nb.log" 2>&1; then
    say "$name: OK"
    return 0
  fi
  say "$name: FAILED — tail of $LOGS/$nb.log:"
  tail -25 "$LOGS/$nb.log"
  status "FAILED:$name"
  return 1
}

say "starting; repo=$REPO res=${RES}deg stride=$STRIDE"
say "python: $("$PIXI" run python -c 'import sys; print(sys.version.split()[0])' 2>/dev/null)"

stage "01_download" 01_data_download "$RAW"    || exit 1
stage "02_clean"    02_data_clean    "$CLEAN"  || exit 1
stage "03_analysis" 03_analysis      "$ANNUAL" || exit 1
stage "04_figures"  04_figures       "$MAINFIG" || exit 1

status "complete"
say "complete — results/headline_comparison.json and figures/main_result.png are ready"
if [ -f "$REPO/results/headline_comparison.json" ]; then
  say "headline comparison:"
  cat "$REPO/results/headline_comparison.json"
fi
