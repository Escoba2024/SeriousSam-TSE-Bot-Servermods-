#!/usr/bin/env bash
# Measure one already-running, isolated TSE variant without touching it.
#
# The harness never starts or stops a game process. It samples the PIDs you
# name, optionally polls the server population, then runs the three analyses
# that the 2026-10-21 test was missing:
#
#   1. tse_cpu_profile.py analyze  -> was the measurement free of throttling?
#   2. bot_telemetry.py            -> were the bots actually ticking at 20 Hz?
#   3. gamespy_query.py            -> were the players still on the server?
#
# A window that fails 1 or 2 is reported as NOT_QUALIFIED; the CPU number is
# still stored, but it must not be used for a saving claim.
#
# Exit codes: 0 QUALIFIED_WINDOW, 6 invalid CPU window, 3 bots inactive,
#             4 bot timer stalled, 8 server population mismatch, 2 usage.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY=python3

LABEL=""
OUT=""
DURATION=""
WARMUP="300"
INTERVAL="0.5"
SERVER=""
EXPECT_PLAYERS=""
EXPECT_PREFIX=""
TELEMETRY=""
EXPECT_BOTS=""
EXPECT_NULLRENDER=""
ALLOW_BUSY_HOST=0
ALLOW_NO_TELEMETRY=0
REQUIRE_CWD=""
PIDS=()
CHILDREN=()

usage() {
  cat <<'EOF'
usage: measure_window.sh --label NAME --out DIR --duration SECONDS
                         --pid PID[:ROLE] [--pid ...]
                         [--warmup 300] [--interval 0.5]
                         [--server HOST:PORT] [--expect-players N] [--expect-prefix P]
                         [--telemetry PATH] [--expect-bots N] [--expect-nullrender 0|1]
                         [--require-cwd PREFIX]
                         [--allow-busy-host] [--allow-no-telemetry]

--pid       repeat for every process: client/server role drives the comparison
--telemetry BotTelemetry.csv written by the P0 candidate build
--require-cwd  refuse to sample a PID whose working directory is outside PREFIX
               (use it to keep production processes out of the measurement)
--warmup    seconds excluded from the analyses (default 300 = 5 min)
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --label) LABEL="${2:-}"; shift 2 ;;
    --out) OUT="${2:-}"; shift 2 ;;
    --duration) DURATION="${2:-}"; shift 2 ;;
    --warmup) WARMUP="${2:-}"; shift 2 ;;
    --interval) INTERVAL="${2:-}"; shift 2 ;;
    --pid) PIDS+=("${2:-}"); shift 2 ;;
    --server) SERVER="${2:-}"; shift 2 ;;
    --expect-players) EXPECT_PLAYERS="${2:-}"; shift 2 ;;
    --expect-prefix) EXPECT_PREFIX="${2:-}"; shift 2 ;;
    --telemetry) TELEMETRY="${2:-}"; shift 2 ;;
    --expect-bots) EXPECT_BOTS="${2:-}"; shift 2 ;;
    --expect-nullrender) EXPECT_NULLRENDER="${2:-}"; shift 2 ;;
    --allow-busy-host) ALLOW_BUSY_HOST=1; shift ;;
    --allow-no-telemetry) ALLOW_NO_TELEMETRY=1; shift ;;
    --require-cwd) REQUIRE_CWD="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$LABEL" ] || [ -z "$OUT" ] || [ -z "$DURATION" ] || [ "${#PIDS[@]}" -eq 0 ]; then
  usage; exit 2
fi
if [ -e "$OUT/evidence.json" ]; then
  echo "refusing to overwrite existing evidence in $OUT" >&2
  exit 2
fi

# Isolation guard: never sample a process that was not started from the
# experiment directory. A production fleet must never enter a measurement.
if [ -n "$REQUIRE_CWD" ]; then
  for spec in "${PIDS[@]}"; do
    pid="${spec%%:*}"
    if [ ! -d "/proc/$pid" ]; then
      echo "pid $pid does not exist" >&2
      exit 2
    fi
    cwd="$(readlink -f "/proc/$pid/cwd" 2>/dev/null || true)"
    case "$cwd" in
      "$REQUIRE_CWD"*) ;;
      *) echo "refusing pid $pid: cwd '$cwd' is outside '$REQUIRE_CWD'" >&2; exit 2 ;;
    esac
  done
fi
mkdir -p "$OUT"
START_EPOCH="$(date +%s)"
START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

cleanup() {
  for child in "${CHILDREN[@]:-}"; do
    [ -n "$child" ] && kill "$child" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

# ---- 1. sample the named processes for warmup + measurement ----------------
total="$(awk -v d="$DURATION" -v w="$WARMUP" 'BEGIN{printf "%.0f", d+w}')"
sampler_cmd=("$PY" "$HERE/tse_cpu_profile.py" sample
             --duration "$total" --interval "$INTERVAL"
             --out "$OUT/cpu.jsonl" --label "$LABEL")
for spec in "${PIDS[@]}"; do sampler_cmd+=(--pid "$spec"); done
"${sampler_cmd[@]}" &
CHILDREN+=($!)

if [ -n "$SERVER" ]; then
  count="$(awk -v d="$DURATION" -v w="$WARMUP" -v i="$INTERVAL" \
    'BEGIN{c=int((d+w)/10); if(c<1)c=1; print c}')"
  query_cmd=("$PY" "$HERE/../gamespy_query.py" "$SERVER" '\status\'
             --count "$count" --interval 10 --timeout 3
             --jsonl "$OUT/server-query.jsonl")
  [ -n "$EXPECT_PLAYERS" ] && query_cmd+=(--expect-players "$EXPECT_PLAYERS")
  [ -n "$EXPECT_PREFIX" ] && query_cmd+=(--expect-prefix "$EXPECT_PREFIX")
  "${query_cmd[@]}" >/dev/null 2>"$OUT/server-query.err" &
  CHILDREN+=($!)
fi

echo "measuring $LABEL for ${total}s (warmup ${WARMUP}s) into $OUT" >&2
set +e
wait "${CHILDREN[0]}"
sampler_rc=$?
set -e
set +e
for child in "${CHILDREN[@]:1}"; do wait "$child"; done
set -e
CHILDREN=()
if [ "$sampler_rc" -ne 0 ]; then
  echo "sampler failed (rc=$sampler_rc)" >&2
  exit 2
fi

# ---- 2. CPU validity -------------------------------------------------------
set +e
analyze_cmd=("$PY" "$HERE/tse_cpu_profile.py" analyze --input "$OUT/cpu.jsonl"
             --warmup "$WARMUP" --json "$OUT/cpu-analysis.json")
[ "$ALLOW_BUSY_HOST" -eq 1 ] && analyze_cmd+=(--allow-busy-host)
"${analyze_cmd[@]}"
cpu_rc=$?
set -e

# ---- 3. Bot activity -------------------------------------------------------
bot_rc=0
telemetry_used=""
if [ -n "$TELEMETRY" ] && [ -f "$TELEMETRY" ]; then
  # Stale evidence is worse than none: the file must have been written during
  # this window, otherwise the candidate DLL was not the one that ran.
  mtime="$(stat -c %Y "$TELEMETRY" 2>/dev/null || echo 0)"
  if [ "$mtime" -lt "$START_EPOCH" ]; then
    bot_rc=3
    echo "telemetry file is older than this window; the candidate DLL did not run" >&2
  else
    telemetry_used="$TELEMETRY"
    bot_cmd=("$PY" "$HERE/../bot_telemetry.py" "$TELEMETRY"
             --warmup "$WARMUP" --duration "$DURATION"
             --json "$OUT/bot-telemetry.json")
    [ -n "$EXPECT_BOTS" ] && bot_cmd+=(--expect-bots "$EXPECT_BOTS")
    [ -n "$EXPECT_NULLRENDER" ] && bot_cmd+=(--expect-nullrender "$EXPECT_NULLRENDER")
    set +e
    "${bot_cmd[@]}"
    bot_rc=$?
    set -e
  fi
else
  if [ "$ALLOW_NO_TELEMETRY" -eq 1 ]; then
    echo "WARNING: no telemetry given; bot activity is unproven" >&2
  else
    echo "no telemetry file: bot activity cannot be proven, window is NOT_QUALIFIED" >&2
    bot_rc=3
  fi
fi

# ---- 4. Server population continuity --------------------------------------
server_rc=0
if [ -n "$SERVER" ] && [ -f "$OUT/server-query.jsonl" ]; then
  if [ -s "$OUT/server-query.err" ]; then
    server_rc=8
  fi
  failures="$($PY - "$OUT/server-query.jsonl" <<'PY'
import json, sys
rows = [json.loads(line) for line in open(sys.argv[1]) if line.strip()]
bad = [r for r in rows if r.get("error") or r.get("problems")]
print(len(bad))
PY
)"
  if [ "$failures" -gt 0 ]; then
    server_rc=8
    echo "server population check failed in $failures sample(s)" >&2
  fi
fi

# ---- 5. Summary ------------------------------------------------------------
final="NOT_QUALIFIED"
if [ "$cpu_rc" -eq 0 ] && [ "$bot_rc" -eq 0 ] && [ "$server_rc" -eq 0 ]; then
  final="QUALIFIED_WINDOW"
fi

cat > "$OUT/evidence.json" <<EOF
{
  "label": "$LABEL",
  "start_utc": "$START_UTC",
  "end_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_s": $DURATION,
  "warmup_s": $WARMUP,
  "interval_s": $INTERVAL,
  "pids": $(printf '%s\n' "${PIDS[@]}" | $PY -c 'import json,sys;print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))'),
  "files": {
    "cpu_samples": "cpu.jsonl",
    "cpu_analysis": "cpu-analysis.json",
    "bot_telemetry_source": "${telemetry_used}",
    "bot_telemetry_analysis": "bot-telemetry.json",
    "server_query": "server-query.jsonl"
  },
  "exit_codes": {"cpu": $cpu_rc, "bot": $bot_rc, "server": $server_rc},
  "result": "$final",
  "note": "QUALIFIED_WINDOW covers measurement validity and active bots only. Vanilla join, CRC, 60-minute sync, combat and crash gates remain separate."
}
EOF

cat > "$OUT/summary.md" <<EOF
# Measurement window: $LABEL

- UTC: $START_UTC .. $(date -u +%Y-%m-%dT%H:%M:%SZ)
- Duration: ${DURATION}s measured, ${WARMUP}s warmup excluded, ${INTERVAL}s sampling
- PIDs: ${PIDS[*]}
- Result: **$final**
- Exit codes: CPU=$cpu_rc bot=$bot_rc server=$server_rc

See \`cpu-analysis.json\` (throttling/validity), \`bot-telemetry.json\`
(tick/action rates, stalls, ga_csNetwork waits) and \`server-query.jsonl\`
(population continuity). A CPU percentage from this window may only be used in
a saving claim together with two further non-overlapping repetitions per
variant (\`tse_cpu_profile.py compare\`).
EOF

echo "window result: $final" >&2
if [ "$cpu_rc" -ne 0 ]; then exit "$cpu_rc"; fi
if [ "$bot_rc" -ne 0 ]; then exit "$bot_rc"; fi
if [ "$server_rc" -ne 0 ]; then exit "$server_rc"; fi
exit 0
