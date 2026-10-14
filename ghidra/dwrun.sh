#!/bin/bash
# headless Ghidra on the DucatiWorld project. usage: dwrun.sh <log> [headless args after project name]
# Set GHIDRA_HEADLESS (path to analyzeHeadless) and DW_GHIDRA (folder holding DucatiWorld.gpr); scripts in ./scripts.
log="$1"; shift
"$GHIDRA_HEADLESS" "$DW_GHIDRA" DucatiWorld "$@" -scriptPath "$(dirname "$0")/scripts" > "$log" 2>&1
tail -3 "$log"
