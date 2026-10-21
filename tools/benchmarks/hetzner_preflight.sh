#!/usr/bin/env bash
# Read-only preflight before an isolated TSE CPU experiment on Hetzner.
#
# It never starts, stops or signals a game process and never writes into the
# runtime. It only answers: is this runtime isolated, is the expected binary
# present, does the current shell (and therefore every child process) run
# under a CPU quota, is the network port free, and does the host have any
# measurable headroom left?
#
# Exit codes: 0 GO, 9 NO-GO, 2 usage error.
set -euo pipefail

RUNTIME=""
DLL=""
PORT=""
SERVER=""
MAX_LOAD=""
ALLOW_NONISOLATED=0
PRODUCTION_HASH="61dc27e0e7b80badcf9ae705c30fca88edd3935737715dffff59e90c26f1fef9"
NULLRENDER_HASH="4f74146eb4e8b640e1d5a080d61d311c6965f1bfb071160f0753c370929c54fb"

usage() {
  cat <<'EOF'
usage: hetzner_preflight.sh --runtime DIR [--dll PATH] [--port N] [--server HOST:PORT]
                            [--max-load X] [--allow-nonisolation]

--runtime   isolated bot-client installation (contains Bin/SeriousSam.exe)
--dll       GameMP.dll that will be used (hash is classified)
--port      local UDP game port that the test will bind
--server    public/loopback server to query read-only (host:port)
--max-load  fail when the 1-minute load average is above this value
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --runtime) RUNTIME="${2:-}"; shift 2 ;;
    --dll) DLL="${2:-}"; shift 2 ;;
    --port) PORT="${2:-}"; shift 2 ;;
    --server) SERVER="${2:-}"; shift 2 ;;
    --max-load) MAX_LOAD="${2:-}"; shift 2 ;;
    --allow-nonisolation) ALLOW_NONISOLATED=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$RUNTIME" ]; then usage; exit 2; fi

failed=0
warned=0
say()  { printf '%-6s %s\n' "$1" "$2"; }
ok()   { say "[ OK ]" "$1"; }
warn() { say "[WARN]" "$1"; warned=$((warned+1)); }
bad()  { say "[FAIL]" "$1"; failed=$((failed+1)); }

echo "== runtime =="
if [ ! -d "$RUNTIME" ]; then
  bad "runtime directory does not exist: $RUNTIME"
else
  ok "runtime exists: $(readlink -f "$RUNTIME")"
  case "$(readlink -f "$RUNTIME")" in
    /srv/tse|/srv/tse/) bad "runtime is the human/production checkout (/srv/tse)" ;;
    *cand*|*Cand*|*CAND*|*test*|*Test*|*ab-*|*botclient*|*BotClient*) ok "path looks like an isolated copy" ;;
    *)
      if [ "$ALLOW_NONISOLATED" -eq 1 ]; then
        warn "path has no isolation marker; continuing because --allow-nonisolation was given"
      else
        bad "path has no isolation marker (candidate/test/ab-/BotClient); refusing to treat it as isolated"
      fi ;;
  esac
  if [ -f "$RUNTIME/Data/Var/Sam_Version.var" ]; then
    version="$(tr -d '[:space:]' < "$RUNTIME/Data/Var/Sam_Version.var")"
    [ "$version" = "v1.07" ] && ok "native version marker: v1.07" || bad "version marker is '$version', expected v1.07"
  else
    bad "missing Data/Var/Sam_Version.var"
  fi
  for name in SeriousSam.exe Engine.dll EntitiesMP.dll GameMP.dll; do
    [ -f "$RUNTIME/Bin/$name" ] && ok "Bin/$name present" || bad "missing Bin/$name"
  done
  if [ -f "$RUNTIME/Bin/BotTelemetry.csv" ]; then
    warn "Bin/BotTelemetry.csv already exists ($(stat -c '%y' "$RUNTIME/Bin/BotTelemetry.csv" 2>/dev/null || echo '?')); it must be rewritten by the candidate or the evidence is stale"
  else
    ok "no stale BotTelemetry.csv"
  fi
fi

echo "== binary identity =="
if [ -n "$DLL" ]; then
  if [ -f "$DLL" ]; then
    hash="$(sha256sum "$DLL" | cut -d' ' -f1)"
    ok "GameMP.dll sha256 $hash"
    case "$hash" in
      "$PRODUCTION_HASH") warn "this is the qualified production hash 61DC...; it has no P0 telemetry and no null-render switch" ;;
      "$NULLRENDER_HASH") warn "this is the older PR #40 candidate (4F74...), which lacks P0 telemetry" ;;
      *) warn "unknown hash: treat as a new, unqualified candidate and build it from the reviewed patch" ;;
    esac
  else
    bad "--dll does not exist: $DLL"
  fi
else
  warn "no --dll given; binary identity cannot be checked"
fi

echo "== CPU limits of this shell (inherited by every child) =="
if [ -r "/proc/self/cgroup" ]; then
  cg_path="$(awk -F: '$1==0 {print $3}' /proc/self/cgroup | head -1)"
  if [ -n "${cg_path:-}" ] && [ -r "/sys/fs/cgroup${cg_path}/cpu.max" ]; then
    read -r quota period < "/sys/fs/cgroup${cg_path}/cpu.max"
    ok "cgroup v2 ${cg_path} cpu.max='${quota} ${period}'"
    if [ "$quota" != "max" ]; then
      pct=$(( quota * 100 / period ))
      if [ "$pct" -lt 100 ]; then
        bad "this shell is capped at ${pct}% of one CPU; every measurement would be saturated (the 2026-10-21 failure mode)"
      else
        warn "cpu.max caps at ${pct}% of one CPU; verify it is above the expected client demand"
      fi
    fi
  else
    ok "no cgroup v2 CPU cap visible for this shell"
  fi
  if [ -r "/sys/fs/cgroup${cg_path}/cpu.stat" ]; then
    nr_periods="$(awk '$1=="nr_periods"{print $2}' "/sys/fs/cgroup${cg_path}/cpu.stat")"
    nr_throttled="$(awk '$1=="nr_throttled"{print $2}' "/sys/fs/cgroup${cg_path}/cpu.stat")"
    ok "cgroup cpu.stat before start: nr_periods=${nr_periods:-?} nr_throttled=${nr_throttled:-?} (sample it again after the run)"
  fi
fi

echo "== host headroom =="
read -r load1 load5 _ < /proc/loadavg
nproc="$(nproc)"
ok "load1=$load1 load5=$load5 nproc=$nproc"
if [ -n "$MAX_LOAD" ]; then
  if awk -v a="$load1" -v b="$MAX_LOAD" 'BEGIN{exit !(a>b)}'; then
    bad "load1 $load1 exceeds --max-load $MAX_LOAD"
  else
    ok "load1 within --max-load $MAX_LOAD"
  fi
else
  warn "no --max-load given; record load1/load5 with every repetition anyway"
fi
if [ -r /proc/meminfo ]; then
  avail="$(awk '$1=="MemAvailable:"{print $2}' /proc/meminfo)"
  ok "MemAvailable $(( avail / 1024 )) MiB"
  [ "$avail" -lt 524288 ] && warn "less than 512 MiB available; a Wine client plus llvmpipe may swap or fail"
fi

echo "== port and server =="
if [ -n "$PORT" ]; then
  if python3 - "$PORT" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.bind(("0.0.0.0", port))
except OSError:
    sys.exit(1)
finally:
    s.close()
PY
  then ok "UDP port $PORT is free"; else bad "UDP port $PORT is already bound"; fi
fi
if [ -n "$SERVER" ]; then
  if python3 "$(dirname "$0")/../gamespy_query.py" "$SERVER" '\status\' --count 1 --timeout 2 >/dev/null 2>&1; then
    ok "server $SERVER answers a read-only GameSpy status query"
  else
    warn "server $SERVER did not answer (it may be the isolated test server and not started yet)"
  fi
fi

echo
if [ "$failed" -gt 0 ]; then
  echo "RESULT: NO-GO ($failed blocking, $warned warnings)"
  exit 9
fi
echo "RESULT: GO ($warned warnings; warnings must be recorded in the report)"
