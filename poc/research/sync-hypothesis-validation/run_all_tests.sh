#!/usr/bin/env bash
# Full offline test suite for the sync-hypothesis-validation toolchain.
# No game files, no processes, no network. Deterministic.
set -u
cd "$(dirname "$0")"

echo "== registry self-check =="
python3 tools/hypothesis_registry.py --check > /dev/null || {
  echo "registry invalid"; exit 1; }

echo "== unit + integration tests =="
python3 -m unittest discover -s tests -v
status=$?

echo
echo "== quick manual smoke (documented commands) =="
tmp="$(mktemp -d)"
python3 tools/make_synthetic_cases.py --out "$tmp/fixtures" > /dev/null
python3 tools/fp_determinism_probe.py --ticks 200 > "$tmp/fp.json"; echo "fp probe exit=$?"
python3 tools/cadence_model.py --telemetry "$tmp/fixtures/telemetry_starved.csv" > "$tmp/cad.json"; echo "cadence exit=$?"
python3 tools/checksum_coverage_probe.py \
  --client-trace "$tmp/fixtures/actions_client.csv" \
  --server-trace "$tmp/fixtures/actions_server_visible_diff.csv" \
  --layout "$tmp/fixtures/layout_verified.json" --first-bad-tick 83.4 > /dev/null
echo "coverage probe exit=$?"
python3 tools/evidence_bundle_audit.py --bundle "$tmp/fixtures/bundle_simulated" > /dev/null
echo "bundle audit exit=$? (5 = simulated, expected)"
rm -rf "$tmp"
exit $status
