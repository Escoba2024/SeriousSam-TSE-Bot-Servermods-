#!/usr/bin/env bash
# bench_harness.sh - reproducible RAM/CPU benchmark harness for the Wine bot
# fleet (architectures A/B/C). SAFE BY DEFAULT:
#
#   * `simulate` mode runs entirely offline with dummy processes and only
#     validates the measurement plumbing (memsample.py, output layout).
#     This is the only mode that was executed in the LMArena sandbox.
#   * `real` mode is REFUSED unless BOTH of the following hold:
#       - TSE_RAM_BENCH_AUTHORIZED=1 is exported by the operator, and
#       - a launch-command file is supplied (the harness itself contains no
#         Wine/retail launch logic and never touches the public fleet).
#     Additionally it aborts if SeriousSam.exe/DedicatedServer.exe processes
#     are visible and TSE_RAM_BENCH_COEXIST_ACK=1 is not set, so it cannot be
#     pointed at the production fleet by accident.
#
# A real benchmark run must follow the protocol in
# docs/research/ram-efficiency/2026-10-25-measurement-protocol.md
# (phases, warm-up, sample counts, PSS capture, provenance file).
#
# Usage:
#   ./bench_harness.sh simulate --clients 4 --duration 10 --out /tmp/ram-bench
#   TSE_RAM_BENCH_AUTHORIZED=1 ./bench_harness.sh real \
#       --launch-file my_launch_commands.txt --duration 600 --out ./results
#
# launch-file format (real mode): one shell command per line; line N starts
# client N and must print the PID of the game process as its last stdout line.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-}"
shift || true

CLIENTS=4
DURATION=10
INTERVAL=2
OUT="./ram-bench-$(date -u +%Y%m%dT%H%M%SZ)"
LAUNCH_FILE=""
CGROUP=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --clients)      CLIENTS="$2"; shift 2 ;;
    --duration)     DURATION="$2"; shift 2 ;;
    --interval)     INTERVAL="$2"; shift 2 ;;
    --out)          OUT="$2"; shift 2 ;;
    --launch-file)  LAUNCH_FILE="$2"; shift 2 ;;
    --cgroup)       CGROUP="$2"; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

fail() { echo "REFUSED: $*" >&2; exit 3; }

provenance() {
  local mode="$1"
  mkdir -p "$OUT"
  {
    echo "{"
    echo "  \"mode\": \"$mode\","
    echo "  \"utc\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"host\": \"$(hostname)\","
    echo "  \"kernel\": \"$(uname -r)\","
    echo "  \"clients\": $CLIENTS,"
    echo "  \"duration_s\": $DURATION,"
    echo "  \"interval_s\": $INTERVAL,"
    echo "  \"note\": \"simulate mode proves plumbing only; it is NOT a Wine/retail measurement\""
    echo "}"
  } > "$OUT/provenance.json"
}

preflight_report() {
  python3 "$HERE/ksm_probe.py" > "$OUT/ksm.json" 2>/dev/null || true
  { grep -E 'MemTotal|MemAvailable|SwapTotal' /proc/meminfo || true; } > "$OUT/meminfo.txt"
  { swapon --show 2>/dev/null || true; } > "$OUT/swap.txt"
}

case "$MODE" in
  simulate)
    provenance simulate
    preflight_report
    echo "[simulate] starting $CLIENTS dummy clients (python sleep+alloc)"
    PIDS=()
    for i in $(seq 1 "$CLIENTS"); do
      python3 -c '
import sys, time
# hold ~8 MiB anonymous memory per dummy client so the sampler sees signal
blob = bytearray(8 * 1024 * 1024)
time.sleep(float(sys.argv[1]) + 5)
' "$DURATION" &
      PIDS+=("$!")
    done
    PID_ARGS=()
    for p in "${PIDS[@]}"; do PID_ARGS+=(--pid "$p"); done
    COUNT=$(( DURATION / INTERVAL ))
    [[ "$COUNT" -lt 1 ]] && COUNT=1
    python3 "$HERE/memsample.py" "${PID_ARGS[@]}" \
      --interval "$INTERVAL" --count "$COUNT" --out "$OUT/samples.jsonl"
    kill "${PIDS[@]}" 2>/dev/null || true
    wait 2>/dev/null || true
    echo "[simulate] wrote $OUT/samples.jsonl ($(wc -l < "$OUT/samples.jsonl") samples)"
    echo "[simulate] PLUMBING TEST ONLY - no Wine measurement performed"
    ;;

  real)
    [[ "${TSE_RAM_BENCH_AUTHORIZED:-0}" == "1" ]] \
      || fail "real mode needs TSE_RAM_BENCH_AUTHORIZED=1 (operator decision; see GRENZEN)"
    [[ -n "$LAUNCH_FILE" && -f "$LAUNCH_FILE" ]] \
      || fail "real mode needs --launch-file with operator-provided launch commands"
    if pgrep -f 'SeriousSam\.exe|DedicatedServer\.exe' >/dev/null 2>&1; then
      [[ "${TSE_RAM_BENCH_COEXIST_ACK:-0}" == "1" ]] \
        || fail "game processes already running (public fleet?); set TSE_RAM_BENCH_COEXIST_ACK=1 only after verifying isolation per the measurement protocol"
    fi
    provenance real
    preflight_report
    echo "[real] launching clients from $LAUNCH_FILE"
    PIDS=()
    n=0
    while IFS= read -r cmd; do
      [[ -z "$cmd" || "$cmd" == \#* ]] && continue
      n=$((n+1))
      [[ "$n" -gt "$CLIENTS" ]] && break
      pid="$(bash -c "$cmd" | tail -n1)"
      [[ "$pid" =~ ^[0-9]+$ ]] || fail "launch command $n did not print a PID"
      PIDS+=("$pid")
      echo "[real] client $n pid=$pid"
    done < "$LAUNCH_FILE"
    PID_ARGS=()
    for p in "${PIDS[@]}"; do PID_ARGS+=(--pid "$p"); done
    CG_ARGS=()
    [[ -n "$CGROUP" ]] && CG_ARGS=(--cgroup "$CGROUP")
    COUNT=$(( DURATION / INTERVAL ))
    python3 "$HERE/memsample.py" "${PID_ARGS[@]}" "${CG_ARGS[@]}" \
      --interval "$INTERVAL" --count "$COUNT" --out "$OUT/samples.jsonl"
    echo "[real] sampling finished; the harness does NOT stop the clients -"
    echo "[real] teardown stays with the operator's qualified runner/cleanup."
    ;;

  *)
    echo "usage: $0 {simulate|real} [--clients N] [--duration S] [--interval S] [--out DIR] [--launch-file F] [--cgroup DIR]" >&2
    exit 2
    ;;
esac
