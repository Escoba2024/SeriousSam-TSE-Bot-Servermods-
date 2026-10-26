#!/usr/bin/env python3
"""Private fixed-argv M1 eight-bot duration wrapper; never a release authorization.

This wrapper intentionally invokes only the protected qualifier's *outer* CLI.
It never appends ``--inner`` and it does not modify or replace the protected
qualifier.  It keeps the protected five-file source inventory intact for the
formal evaluator and writes a separate, caller-pinned sidecar for the Red
Station inputs and their execution helpers.

A successful receipt remains only a private duration-stage artifact.  M1 is
still incomplete pending the separately owned recovery/review gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Any, Callable


# Production constants are deliberately not command-line options.  Tests patch
# these module constants to temporary paths; no test writes /srv or /root.
BASE = Path('/root/ssam-ai-backups/m1-completion-20261026-0155')
TOOLS = Path('/srv/tse-manus-m1-m4-20261026/tools')
NATIVE = Path('/srv/tse-cecil-guard-20261026/tools')
ROOT = Path('/srv/tse-session-qualification-master-m1-eight-two-hours-20261026')
MANIFEST = Path('/srv/tse-cecil-p1-build-20261025-01/manifest.json')
CONFIG = BASE / '8-duration-config.json'
POLICY_PATH = BASE / 'manus-stage8-policy.json'
OFFLINE_MARKER = Path('/root/ssam-ai-backups/shutdown-20261026-0033/public-disabled.json')

MATRIX_LOCK = BASE / 'matrix.lock'
STATE = BASE / 'manus-eight-duration-hardened-progress.json'
NEW_MATRIX = BASE / 'manus-eight-duration-hardened-matrix.json'
COMMAND_RECEIPT = BASE / 'manus-eight-duration-hardened-command.json'
INPUT_SIDECAR = BASE / 'manus-eight-duration-hardened-inputs.json'
HOLD = BASE / 'manus-eight-duration-hardened-HOLD.json'
LOG = BASE / 'manus-eight-duration-hardened-controller.log'
# This canonical receipt is intentionally never opened for writing here.
CANONICAL_BLOCKED_MATRIX = BASE / 'duration-matrix.json'

PROC_ROOT = Path('/proc')
MOUNTINFO = PROC_ROOT / 'self/mountinfo'
CGROUP_ROOT = Path('/sys/fs/cgroup')
PRIOR_RUNTIME_PARENT = Path('/srv')

DURATION_S = 7680
REQUIRED_S = 7200
BOTS = 8
POLL_S = 2.0
PIN_RECHECK_S = 15.0
STARTUP_GRACE_S = 180.0
GUARD_STALE_S = 30.0
RESULT_STALE_S = 45.0
CENSUS_POLL_S = 2.0

# The protected outer producer writes exactly this inventory.  Do not add the
# Red Station inputs here: m1_duration_acceptance requires this original map.
ORIGINAL_SOURCE_NAMES = (
    'qualify_bot_sessions.py',
    'bot_session_executor.py',
    'bot_session_runtime.py',
    'bot_sessions.py',
    'qualify_integrated_wine.py',
)

# This is deliberately a second policy map.  It covers dynamic Red Station
# inputs plus every directly/nestedly imported execution helper used by the
# fixed stage, including the pidfd helper imported by this wrapper.
ADDITIONAL_INPUT_NAMES = (
    'qualify_bot_sessions.py',
    'bot_session_executor.py',
    'bot_session_runtime.py',
    'bot_sessions.py',
    'qualify_integrated_wine.py',
    'bot_telemetry.py',
    'redstation_preset.py',
    'gaming_names.py',
    'native_owned_process.py',
    'poc/scripts/Phase1HumanAI.ini',
)
PRIOR_RECEIPT_NAMES = ('source-sha256.json', 'result.json', 'host-guard.json', 'samples.jsonl')
PRIOR_STAGES = ((1, 'one-hour'), (4, 'four-hour-r2'))
HEX64 = re.compile(r'^[0-9a-f]{64}$')
CGROUP_NAME = re.compile(r'^tse-sessions-[1-9][0-9]*$')


class PinError(RuntimeError):
    """A caller-provided source/configuration pin is absent, malformed, or drifted."""


class SafetyAbort(RuntimeError):
    """A running stage lost a required liveness/safety property."""


class CleanupHold(RuntimeError):
    """Native residue cannot be proven absent; no future start may proceed."""


@dataclass(frozen=True)
class PinContext:
    policy: dict[str, Any]
    policy_sha256: str
    config: dict[str, Any]
    config_sha256: str
    manifest_sha256: str
    candidate_sha256: str


def sha(path: Path | str) -> str:
    """Return a SHA-256 digest without silently treating a missing input as empty."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def atomic_json(path: Path, value: Any, *, overwrite: bool = True) -> None:
    """Atomically write a private JSON receipt, refusing accidental first-write adoption."""
    path = Path(path)
    if not overwrite and path.exists():
        raise RuntimeError('fresh private receipt required; never adopt or overwrite: ' + str(path))
    temporary = path.with_name(path.name + '.tmp.' + str(os.getpid()))
    try:
        with temporary.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(0o600)
        temporary.replace(path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _is_hex_digest(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.fullmatch(value))


def _require_digest(value: Any, label: str) -> str:
    if not _is_hex_digest(value):
        raise PinError('PIN_POLICY_INVALID_' + label)
    return value


def _read_bootstrap_object(path: Path) -> dict[str, Any]:
    """Bounded bootstrap read used only to pin the receipt reader itself."""
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PinError('PIN_POLICY_UNREADABLE') from exc
    if not 1 <= len(raw) <= 16 * 1024 ** 2:
        raise PinError('PIN_POLICY_SIZE_INVALID')
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PinError('PIN_POLICY_JSON_INVALID') from exc
    if not isinstance(value, dict):
        raise PinError('PIN_POLICY_OBJECT_REQUIRED')
    return value


def _load_module_from_path(module_name: str, path: Path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError('module spec unavailable')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except BaseException as exc:
        raise PinError('PINNED_MODULE_LOAD_FAILED_' + path.name) from exc


def load_pinned_modules() -> tuple[Callable[[Path], dict[str, Any]], Any]:
    """Load the policy-pinned receipt and acceptance helpers from exact files."""
    receipt_module = _load_module_from_path('_hardened_native_receipt_io', TOOLS / 'native_receipt_io.py')
    read_receipt = getattr(receipt_module, 'read_receipt', None)
    if not callable(read_receipt):
        raise PinError('PINNED_RECEIPT_READER_MISSING')

    # m1_duration_acceptance imports native_receipt_io by this canonical name.
    old = sys.modules.get('native_receipt_io')
    sys.modules['native_receipt_io'] = receipt_module
    try:
        acceptance = _load_module_from_path('_hardened_m1_duration_acceptance',
                                            TOOLS / 'm1_duration_acceptance.py')
    finally:
        if old is None:
            sys.modules.pop('native_receipt_io', None)
        else:
            sys.modules['native_receipt_io'] = old
    if not callable(getattr(acceptance, 'evaluate_runtime', None)):
        raise PinError('PINNED_ACCEPTANCE_HELPER_MISSING')
    return read_receipt, acceptance


def load_owned_process_class():
    """Load the policy-pinned direct-child pidfd helper from the protected source tree."""
    module = _load_module_from_path('_hardened_native_owned_process', TOOLS / 'native_owned_process.py')
    owned = getattr(module, 'OwnedProcess', None)
    if owned is None:
        raise PinError('PINNED_OWNED_PROCESS_HELPER_MISSING')
    return owned


def _additional_input_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name in ADDITIONAL_INPUT_NAMES:
        if name == 'native_owned_process.py':
            paths[name] = TOOLS / name
        else:
            paths[name] = NATIVE.parent / name if name.startswith('poc/') else NATIVE / name
    return paths


def _source_paths(names: tuple[str, ...]) -> dict[str, Path]:
    return {name: NATIVE / name for name in names}


def _check_exact_map(policy: dict[str, Any], field: str, paths: dict[str, Path]) -> dict[str, str]:
    expected = policy.get(field)
    if not isinstance(expected, dict) or set(expected) != set(paths):
        raise PinError('PIN_POLICY_' + field.upper() + '_EXACT_KEYS_REQUIRED')
    checked: dict[str, str] = {}
    for name, path in paths.items():
        digest = _require_digest(expected.get(name), field.upper() + '_' + name.replace('/', '_'))
        try:
            actual = sha(path)
        except OSError as exc:
            raise PinError('PIN_INPUT_UNREADABLE_' + name.replace('/', '_')) from exc
        if actual != digest:
            raise PinError('PIN_INPUT_DRIFT_' + name.replace('/', '_'))
        checked[name] = actual
    return checked


def _require_config_shape(config: dict[str, Any]) -> int:
    """Read the fixed config only to derive a conservative bounded deadline."""
    if config.get('enabled') is not True or config.get('max_bots') != BOTS:
        raise PinError('PINNED_CONFIG_NOT_EIGHT_BOT_ENABLED')
    identities = config.get('identities')
    servers = config.get('servers')
    if not isinstance(identities, list) or len(identities) != BOTS:
        raise PinError('PINNED_CONFIG_IDENTITY_COUNT_INVALID')
    if not isinstance(servers, list) or len(servers) != 1:
        raise PinError('PINNED_CONFIG_SERVER_COUNT_INVALID')
    leave = config.get('leave_interval_s')
    if type(leave) is not int or not 0 <= leave <= 3600:
        raise PinError('PINNED_CONFIG_LEAVE_INTERVAL_INVALID')
    return leave


def bootstrap_pins() -> tuple[PinContext, Callable[[Path], dict[str, Any]], Any, type]:
    """Establish all explicit trust anchors before any prior receipt or child is read."""
    bootstrap = _read_bootstrap_object(POLICY_PATH)
    expected_reader = _require_digest(bootstrap.get('receipt_reader_sha256'), 'RECEIPT_READER')
    try:
        if sha(TOOLS / 'native_receipt_io.py') != expected_reader:
            raise PinError('PIN_RECEIPT_READER_DRIFT')
    except OSError as exc:
        raise PinError('PIN_RECEIPT_READER_UNREADABLE') from exc

    # Reject modified acceptance source before importing any of its code.
    expected_acceptance_bootstrap = _require_digest(bootstrap.get('acceptance_sha256'), 'ACCEPTANCE')
    if sha(TOOLS / 'm1_duration_acceptance.py') != expected_acceptance_bootstrap:
        raise PinError('PIN_ACCEPTANCE_DRIFT')
    read_receipt, acceptance = load_pinned_modules()
    try:
        policy = read_receipt(POLICY_PATH)
    except BaseException as exc:
        raise PinError('PIN_POLICY_READ_FAILED') from exc
    if policy != bootstrap:
        raise PinError('PIN_POLICY_CHANGED_DURING_BOOTSTRAP')

    expected_acceptance = _require_digest(policy.get('acceptance_sha256'), 'ACCEPTANCE')
    try:
        if sha(TOOLS / 'm1_duration_acceptance.py') != expected_acceptance:
            raise PinError('PIN_ACCEPTANCE_DRIFT')
    except OSError as exc:
        raise PinError('PIN_ACCEPTANCE_UNREADABLE') from exc

    # The formal evaluator consumes this map verbatim from source-sha256.json.
    _check_exact_map(policy, 'harness_sha256', _source_paths(ORIGINAL_SOURCE_NAMES))
    # New, separate map: no attempt is made to spoof or extend source-sha256.json.
    _check_exact_map(policy, 'stage8_additional_input_sha256', _additional_input_paths())

    config_expected = _require_digest(policy.get('stage8_config_sha256'), 'STAGE8_CONFIG')
    manifest_expected = _require_digest(policy.get('build_manifest_sha256'), 'BUILD_MANIFEST')
    try:
        config_digest = sha(CONFIG)
    except OSError as exc:
        raise PinError('PIN_STAGE8_CONFIG_UNREADABLE') from exc
    if config_digest != config_expected:
        raise PinError('PIN_STAGE8_CONFIG_DRIFT')
    try:
        config = read_receipt(CONFIG)
    except BaseException as exc:
        raise PinError('PIN_STAGE8_CONFIG_READ_FAILED') from exc
    _require_config_shape(config)

    try:
        manifest_digest = sha(MANIFEST)
    except OSError as exc:
        raise PinError('PIN_BUILD_MANIFEST_UNREADABLE') from exc
    if manifest_digest != manifest_expected:
        raise PinError('PIN_BUILD_MANIFEST_DRIFT')
    try:
        manifest = read_receipt(MANIFEST)
    except BaseException as exc:
        raise PinError('PIN_BUILD_MANIFEST_READ_FAILED') from exc
    candidate_digest = _require_digest(policy.get('candidate_sha256'), 'CANDIDATE')
    if manifest.get('build_ok') is not True:
        raise PinError('PIN_BUILD_MANIFEST_NOT_SUCCESSFUL')
    if manifest.get('dll_sha256') != candidate_digest:
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_MISMATCH')
    candidate = manifest.get('candidate')
    if not isinstance(candidate, str) or not candidate:
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_PATH_INVALID')
    try:
        if sha(Path(candidate)) != candidate_digest:
            raise PinError('PIN_CANDIDATE_DRIFT')
    except OSError as exc:
        raise PinError('PIN_CANDIDATE_UNREADABLE') from exc

    context = PinContext(policy=policy, policy_sha256=sha(POLICY_PATH), config=config,
                         config_sha256=config_digest, manifest_sha256=manifest_digest,
                         candidate_sha256=candidate_digest)
    owned_class = load_owned_process_class()
    return context, read_receipt, acceptance, owned_class


def verify_pins(context: PinContext, read_receipt: Callable[[Path], dict[str, Any]]) -> None:
    """Recheck every static input; all errors are explicit even under ``python -O``."""
    try:
        if sha(POLICY_PATH) != context.policy_sha256:
            raise PinError('PIN_POLICY_DRIFT')
        if sha(CONFIG) != context.config_sha256:
            raise PinError('PIN_STAGE8_CONFIG_DRIFT')
        if sha(MANIFEST) != context.manifest_sha256:
            raise PinError('PIN_BUILD_MANIFEST_DRIFT')
    except OSError as exc:
        raise PinError('PIN_STATIC_INPUT_UNREADABLE') from exc
    _check_exact_map(context.policy, 'harness_sha256', _source_paths(ORIGINAL_SOURCE_NAMES))
    _check_exact_map(context.policy, 'stage8_additional_input_sha256', _additional_input_paths())
    _require_config_shape(context.config)
    try:
        manifest = read_receipt(MANIFEST)
    except BaseException as exc:
        raise PinError('PIN_BUILD_MANIFEST_READ_FAILED') from exc
    if manifest.get('build_ok') is not True or manifest.get('dll_sha256') != context.candidate_sha256:
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_MISMATCH')
    candidate = manifest.get('candidate')
    if not isinstance(candidate, str):
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_PATH_INVALID')
    try:
        if sha(Path(candidate)) != context.candidate_sha256:
            raise PinError('PIN_CANDIDATE_DRIFT')
    except OSError as exc:
        raise PinError('PIN_CANDIDATE_UNREADABLE') from exc


def write_input_sidecar(context: PinContext, phase: str, *, overwrite: bool) -> None:
    """Persist the independently pinned dynamic-input inventory without touching producer inventory."""
    inputs = _check_exact_map(context.policy, 'stage8_additional_input_sha256', _additional_input_paths())
    atomic_json(INPUT_SIDECAR, dict(schema='M1_STAGE8_CALLER_INPUT_INVENTORY_V1', phase=phase,
                                    utc=utc_now(), policy_sha256=context.policy_sha256,
                                    stage8_config_sha256=context.config_sha256,
                                    original_harness_sha256=context.policy['harness_sha256'],
                                    additional_input_sha256=inputs,
                                    formal_source_inventory_unchanged=True,
                                    m1_complete=False), overwrite=overwrite)


def build_fixed_outer_argv() -> list[str]:
    """The only authorized invocation: protected outer controller, fixed values, no --inner."""
    return [
        '/usr/bin/python3', '-u', str(NATIVE / 'qualify_bot_sessions.py'),
        '--config', str(CONFIG), '--runtime', str(ROOT), '--duration', str(DURATION_S),
        '--execute', '--cecil-p1', '--preset', 'redstation', '--port', '27140', '--display', ':155',
        '--build-manifest', str(MANIFEST), '--offline-public-marker', str(OFFLINE_MARKER),
    ]


def validate_fixed_outer_argv(argv: list[str]) -> None:
    if argv != build_fixed_outer_argv() or '--inner' in argv:
        raise RuntimeError('FIXED_OUTER_ARGV_REQUIRED; direct inner execution is forbidden')


def derive_budget(config: dict[str, Any]) -> dict[str, int]:
    """Bound the entire controller lifecycle, not only its 7,680-second measurement."""
    leave = _require_config_shape(config)
    # Protected source: Xvfb(2), initial server wait(8), observer join(120).
    startup = 2 + 8 + 120 + 30
    drain = 120 + leave * BOTS
    # Protected source cleanup: 9 non-server roles * (20 window + 20 pidfd),
    # server * 20, ten prefixes * two wineserver calls * 15, twenty unmounts *
    # 15, and display teardown 10.  This is intentionally conservative.
    cleanup = 9 * 40 + 20 + 10 * 2 * 15 + 20 * 15 + 10
    finalize = 30
    margin = 120
    total = startup + DURATION_S + drain + cleanup + finalize + margin
    return dict(startup_s=startup, measure_s=DURATION_S, drain_s=drain, cleanup_s=cleanup,
                finalize_s=finalize, margin_s=margin, total_s=total,
                abort_wait_s=cleanup + 120)


def _hash_prior_receipts() -> dict[str, dict[str, str]]:
    snapshots: dict[str, dict[str, str]] = {}
    for bots, label in PRIOR_STAGES:
        root = PRIOR_RUNTIME_PARENT / ('tse-session-qualification-master-m1-' + label + '-20261026')
        entries: dict[str, str] = {}
        for name in PRIOR_RECEIPT_NAMES:
            try:
                entries[name] = sha(root / name)
            except OSError as exc:
                raise PinError('PRIOR_RECEIPT_UNREADABLE_' + str(bots) + '_' + name) from exc
        snapshots[str(root)] = entries
    return snapshots


def verify_prior_receipts(snapshots: dict[str, dict[str, str]]) -> None:
    for root_text, entries in snapshots.items():
        for name, expected in entries.items():
            try:
                actual = sha(Path(root_text) / name)
            except OSError as exc:
                raise PinError('PRIOR_RECEIPT_UNREADABLE_' + name) from exc
            if actual != expected:
                raise PinError('PRIOR_RECEIPT_DRIFT_' + name)


def validate_prior_stages(acceptance: Any, context: PinContext,
                          snapshots: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for bots, label in PRIOR_STAGES:
        root = PRIOR_RUNTIME_PARENT / ('tse-session-qualification-master-m1-' + label + '-20261026')
        verdict = acceptance.evaluate_runtime(root, bots=bots, required_s=3600,
                                              dll_sha256=context.candidate_sha256,
                                              harness_sha256=context.policy['harness_sha256'])
        if verdict.get('status') != 'DURATION_RECEIPTS_ACCEPTED':
            raise RuntimeError('prior duration gate rejected: ' + json.dumps(verdict, sort_keys=True))
        stages.append(dict(root=str(root), verdict=verdict, receipt_sha256=snapshots[str(root)]))
    return stages


def _parse_utc(value: Any) -> float:
    if not isinstance(value, str):
        raise ValueError('timestamp missing')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp has no timezone')
    return parsed.timestamp()


def check_live_heartbeat(read_receipt: Callable[[Path], dict[str, Any]], *, launched_mono: float,
                         now_mono: float, now_epoch: float, budget: dict[str, int],
                         previous: dict[str, Any]) -> dict[str, Any]:
    """Require fresh outer guard and result progress, with narrow startup/drain grace."""
    if now_mono - launched_mono <= STARTUP_GRACE_S:
        return dict(previous, phase='STARTUP_GRACE', startup_remaining_s=round(
            STARTUP_GRACE_S - (now_mono - launched_mono), 3))
    try:
        guard = read_receipt(ROOT / 'host-guard.json')
        result = read_receipt(ROOT / 'result.json')
    except BaseException as exc:
        raise SafetyAbort('HEARTBEAT_RECEIPT_UNAVAILABLE') from exc
    samples = guard.get('samples')
    status = result.get('status')
    state = dict(previous)
    if status == 'FAIL':
        # The inner producer has already entered its finally cleanup. Sending
        # SIGINT to an outer controller already waiting for that cleanup can
        # generate a second parent-death signal and interrupt the cleanup.
        if (result.get('scope') != 'ISOLATED_NETNS_RETAIL_WINE' or
                guard.get('status') not in ('MONITORING','STOPPED_GUARD','FINISHED')):
            raise SafetyAbort('NATIVE_FAILURE_CLEANUP_UNBOUND')
        state.setdefault('native_failure_cleanup_until', now_mono + budget['cleanup_s'])
        if now_mono > state['native_failure_cleanup_until']:
            raise SafetyAbort('NATIVE_FAILURE_CLEANUP_DEADLINE_EXCEEDED')
        state.update(phase='NATIVE_FAILURE_CLEANUP', result_status='FAIL',
                     guard_status=guard.get('status'), native_error=result.get('error'))
        return state
    if (guard.get('status') == 'FINISHED' and guard.get('child_exitcode') == 0 and
            guard.get('error') is None and status == 'PASS_LIMITED_SESSION_LIFECYCLE'):
        # The final file may be visible just before the directly owned outer
        # process exits. Its exit code and full receipts are still checked below.
        state.setdefault('finalizing_until', now_mono + 15)
        if now_mono > state['finalizing_until']:
            raise SafetyAbort('FINAL_RECEIPT_WITHOUT_OUTER_EXIT')
        state.update(phase='FINALIZING', result_status=status, guard_status='FINISHED')
        return state
    if guard.get('status') != 'MONITORING' or not isinstance(samples, list) or not samples:
        raise SafetyAbort('HOST_GUARD_NOT_MONITORING')
    last = samples[-1]
    if not isinstance(last, dict) or type(last.get('at')) not in (int, float):
        raise SafetyAbort('HOST_GUARD_SAMPLE_INVALID')
    age = now_epoch - last['at']
    if not -5 <= age <= GUARD_STALE_S:
        raise SafetyAbort('HOST_GUARD_HEARTBEAT_STALE')
    if status == 'FAIL' or not isinstance(status, str):
        raise SafetyAbort('NATIVE_RESULT_FAILURE_OR_INVALID')
    try:
        result_age = now_epoch - _parse_utc(result.get('utc'))
    except (TypeError, ValueError) as exc:
        raise SafetyAbort('RESULT_HEARTBEAT_TIMESTAMP_INVALID') from exc
    elapsed = result.get('elapsed_s')
    numeric_elapsed = type(elapsed) in (int, float) and math.isfinite(elapsed) and elapsed >= 0
    if numeric_elapsed:
        old_elapsed = state.get('elapsed_s')
        if old_elapsed is not None and elapsed + 0.001 < old_elapsed:
            raise SafetyAbort('RESULT_PROGRESS_REGRESSED')
        if old_elapsed is None or elapsed > old_elapsed + 0.1:
            state['last_progress_mono'] = now_mono
        state['elapsed_s'] = elapsed
        if elapsed >= DURATION_S - 30:
            state.setdefault('drain_grace_until', now_mono + budget['drain_s'] + budget['cleanup_s'] + 60)
    elif now_mono - state.get('first_result_mono', now_mono) > RESULT_STALE_S:
        raise SafetyAbort('RESULT_PROGRESS_MISSING')
    state.setdefault('first_result_mono', now_mono)
    draining = now_mono <= state.get('drain_grace_until', -1)
    if not draining:
        if status != 'MEASURING':
            raise SafetyAbort('RESULT_NOT_MEASURING')
        if not -5 <= result_age <= RESULT_STALE_S:
            raise SafetyAbort('RESULT_HEARTBEAT_STALE')
        if numeric_elapsed and now_mono - state.get('last_progress_mono', now_mono) > RESULT_STALE_S:
            raise SafetyAbort('RESULT_PROGRESS_STALE')
    state.update(phase='DRAIN_GRACE' if draining else 'MONITORING', guard_status=guard.get('status'),
                 guard_sample_at=last['at'], guard_age_s=round(age, 3), result_status=status,
                 result_age_s=round(result_age, 3))
    return state


def _unescape_mount_path(value: str) -> str:
    return re.sub(r'\\([0-7]{3})', lambda match: chr(int(match.group(1), 8)), value)


def _process_in_cgroup(proc: Path, cgroup: Path) -> bool:
    try:
        expected = '/' + str(cgroup.relative_to(CGROUP_ROOT))
        for line in (proc / 'cgroup').read_text().splitlines():
            fields = line.split(':', 2)
            if len(fields) == 3 and fields[2] == expected:
                return True
    except (OSError, ValueError):
        return False
    return False


def census_native_residue(root: Path, result: dict[str, Any]) -> dict[str, Any]:
    """Read-only, independent cgroup/process/mount census; never signal a discovered PID."""
    errors: list[str] = []
    live_processes: list[dict[str, Any]] = []
    mounts: list[str] = []
    cgroup_text = result.get('cgroup')
    cgroup: Path | None = None
    if not isinstance(cgroup_text, str):
        errors.append('CENSUS_CGROUP_MISSING')
    else:
        candidate = Path(cgroup_text)
        if candidate.parent != CGROUP_ROOT or not CGROUP_NAME.fullmatch(candidate.name):
            errors.append('CENSUS_CGROUP_UNBOUND')
        else:
            cgroup = candidate
            try:
                pids = (cgroup / 'cgroup.procs').read_text().split()
            except OSError:
                errors.append('CENSUS_CGROUP_UNREADABLE')
            else:
                if pids:
                    errors.append('CENSUS_CGROUP_NOT_EMPTY')
    try:
        root_resolved = root.resolve()
    except OSError:
        root_resolved = root
    try:
        for proc in PROC_ROOT.glob('[0-9]*'):
            try:
                fields = (proc / 'stat').read_text().rsplit(') ', 1)[1].split()
                state = fields[0]
                if state == 'Z':
                    continue
                cwd = Path(os.readlink(proc / 'cwd'))
                causes: list[str] = []
                try:
                    if cwd.is_relative_to(root_resolved):
                        causes.append('cwd')
                except ValueError:
                    pass
                if cgroup is not None and _process_in_cgroup(proc, cgroup):
                    causes.append('cgroup')
                if causes:
                    live_processes.append(dict(pid=int(proc.name), state=state, cwd=str(cwd), causes=causes))
            except (OSError, ValueError, IndexError):
                continue
    except OSError:
        errors.append('CENSUS_PROC_UNREADABLE')
    if live_processes:
        errors.append('CENSUS_LIVE_NATIVE_PROCESS')
    try:
        for line in MOUNTINFO.read_text().splitlines():
            fields = line.split(' - ', 1)[0].split()
            if len(fields) < 5:
                continue
            mount = Path(_unescape_mount_path(fields[4]))
            try:
                if mount.is_relative_to(root_resolved):
                    mounts.append(str(mount))
            except ValueError:
                continue
    except OSError:
        errors.append('CENSUS_MOUNTINFO_UNREADABLE')
    if mounts:
        errors.append('CENSUS_NATIVE_MOUNT_REMAINS')
    return dict(clean=not errors, errors=sorted(set(errors)), cgroup=str(cgroup) if cgroup else None,
                live_processes=live_processes, mounts=sorted(set(mounts)))


def wait_for_clean_census(root: Path, result: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    """Hold the driver serialization lock while a known cleanup finishes; no extra signaling."""
    deadline = time.monotonic() + timeout
    while True:
        census = census_native_residue(root, result)
        if census['clean'] or time.monotonic() >= deadline:
            return census
        time.sleep(CENSUS_POLL_S)


def request_orderly_abort(owned: Any, *, timeout: float) -> None:
    """Ask only the identity-bound direct outer child to enter its KeyboardInterrupt path."""
    process = owned.process
    if process.poll() is not None:
        return
    try:
        signal.pidfd_send_signal(owned.pidfd, signal.SIGINT)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise CleanupHold('ORDERLY_ABORT_TIMEOUT_DIRECT_OUTER_STILL_LIVE') from exc


def _fresh_start_guard() -> None:
    if ROOT.exists():
        raise RuntimeError('fresh stage required; never adopt or overwrite runtime root')
    if HOLD.exists():
        raise CleanupHold('PERSISTENT_CLEANUP_HOLD_PRESENT; manual inspection required; no retry')
    for path in (STATE, NEW_MATRIX, COMMAND_RECEIPT, INPUT_SIDECAR, LOG):
        if path.exists():
            raise RuntimeError('fresh hardened receipt required; never adopt or overwrite: ' + str(path))


def _persist_hold(state: dict[str, Any], reason: BaseException | str,
                  census: dict[str, Any] | None) -> None:
    text = str(reason) or type(reason).__name__
    state.update(status='CLEANUP_HOLD', error=text, no_retry=True, cleanup_census=census, utc=utc_now(),
                 m1_complete=False)
    atomic_json(STATE, state)
    hold = dict(status='HOLD', reason=text, utc=utc_now(), no_retry=True, m1_complete=False,
                runtime=str(ROOT), cleanup_census=census,
                instruction='Do not restart. Inspect residue manually; this driver never signals unknown processes.')
    if not HOLD.exists():
        atomic_json(HOLD, hold, overwrite=False)


def _close_owned_if_stopped(owned: Any | None) -> None:
    if owned is not None and owned.process.poll() is not None:
        owned.close()


def _post_stop_census(read_receipt: Callable[[Path], dict[str, Any]], budget: dict[str, int]) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        result = read_receipt(ROOT / 'result.json')
    except BaseException as exc:
        raise CleanupHold('CENSUS_RESULT_UNAVAILABLE') from exc
    census = wait_for_clean_census(ROOT, result, timeout=budget['cleanup_s'])
    if not census['clean']:
        raise CleanupHold('NATIVE_RESOURCE_CENSUS_UNRESOLVED: ' + json.dumps(census, sort_keys=True))
    return result, census


def run_locked(_matrix_lock: Any) -> None:
    context, read_receipt, acceptance, OwnedProcess = bootstrap_pins()
    verify_pins(context, read_receipt)
    budget = derive_budget(context.config)
    snapshots = _hash_prior_receipts()
    stages = validate_prior_stages(acceptance, context, snapshots)
    verify_prior_receipts(snapshots)
    argv = build_fixed_outer_argv()
    validate_fixed_outer_argv(argv)

    atomic_json(COMMAND_RECEIPT, dict(schema='M1_STAGE8_FIXED_OUTER_ARGV_V1', argv=argv,
                                      direct_inner_forbidden=True, duration_s=DURATION_S,
                                      required_s=REQUIRED_S, m1_complete=False), overwrite=False)
    write_input_sidecar(context, 'BEFORE_START', overwrite=False)
    state: dict[str, Any] = dict(status='STARTING_EIGHT_DURATION_HARDENED', m1_complete=False,
                                 stages=stages, candidate_sha256=context.candidate_sha256,
                                 duration_s=DURATION_S, required_s=REQUIRED_S,
                                 budget=budget, fixed_outer_argv=argv,
                                 prior_receipt_sha256=snapshots, utc=utc_now())
    atomic_json(STATE, state, overwrite=False)

    child = None
    owned = None
    launched_mono = time.monotonic()
    heartbeat: dict[str, Any] = {}
    last_pin_check = float('-inf')
    normal_complete = False
    cleanup_in_progress = False
    prior_handlers: dict[int, Any] = {}

    def interrupted(signum: int, _frame: Any) -> None:
        # Do not let a second signal release this wrapper's serialization lock
        # while it is waiting for the post-stop read-only resource census.
        if cleanup_in_progress:
            return
        raise SafetyAbort('DRIVER_SIGNAL_' + str(signum) + '_ORDERLY_ABORT_REQUIRED')

    for signum in (signal.SIGINT, signal.SIGTERM):
        prior_handlers[signum] = signal.signal(signum, interrupted)
    try:
        with LOG.open('xb') as log:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                     env=dict(os.environ, PYTHONOPTIMIZE='0'))
        try:
            owned = OwnedProcess(child)
        except BaseException as exc:
            # A failed pidfd/direct-child binding is not a license to signal an
            # unbound PID.  Freeze subsequent starts and require inspection.
            raise CleanupHold('DIRECT_CHILD_PIDFD_OWNERSHIP_BIND_FAILED') from exc
        state['controller_pid'] = child.pid
        state['status'] = 'EIGHT_DURATION_RUNNING_HARDENED'
        state['utc'] = utc_now()
        atomic_json(STATE, state)
        print('EIGHT_DURATION_HARDENED_STARTED pid=' + str(child.pid), flush=True)

        deadline = launched_mono + budget['total_s']
        while child.poll() is None:
            now_mono = time.monotonic()
            if now_mono > deadline:
                raise SafetyAbort('FULL_LIFECYCLE_DEADLINE_EXCEEDED_NO_RETRY')
            if now_mono - last_pin_check >= PIN_RECHECK_S:
                verify_pins(context, read_receipt)
                verify_prior_receipts(snapshots)
                write_input_sidecar(context, 'DURING_RUN', overwrite=True)
                heartbeat = check_live_heartbeat(read_receipt, launched_mono=launched_mono,
                                                  now_mono=now_mono, now_epoch=time.time(), budget=budget,
                                                  previous=heartbeat)
                state.update(status='EIGHT_DURATION_RUNNING_HARDENED', heartbeat=heartbeat, utc=utc_now())
                atomic_json(STATE, state)
                print('PROGRESS ' + json.dumps(dict(utc=state['utc'], heartbeat=heartbeat), sort_keys=True), flush=True)
                last_pin_check = now_mono
            time.sleep(POLL_S)

        _close_owned_if_stopped(owned)
        verify_pins(context, read_receipt)
        verify_prior_receipts(snapshots)
        result, census = _post_stop_census(read_receipt, budget)
        state['cleanup_census'] = census
        guard = read_receipt(ROOT / 'host-guard.json')
        if child.returncode != 0 or guard.get('status') != 'FINISHED':
            raise RuntimeError('native outer/guard failed: ' + json.dumps(dict(
                exitcode=child.returncode, result=result.get('status'), error=result.get('error'),
                guard=guard.get('status')), sort_keys=True))
        verdict = acceptance.evaluate_runtime(ROOT, bots=BOTS, required_s=REQUIRED_S,
                                              dll_sha256=context.candidate_sha256,
                                              harness_sha256=context.policy['harness_sha256'])
        state['eight_verdict'] = verdict
        if verdict.get('status') != 'DURATION_RECEIPTS_ACCEPTED':
            raise RuntimeError('eight duration gate rejected: ' + json.dumps(verdict, sort_keys=True))
        stages.append(dict(root=str(ROOT), verdict=verdict, cleanup_census=census))
        for stage in stages:
            verdict_again = acceptance.evaluate_runtime(Path(stage['root']), bots=stage['verdict']['bots'],
                                                        required_s=stage['verdict']['required_s'],
                                                        dll_sha256=context.candidate_sha256,
                                                        harness_sha256=context.policy['harness_sha256'])
            if verdict_again.get('status') != 'DURATION_RECEIPTS_ACCEPTED':
                raise RuntimeError('final duration matrix revalidation failed')
        verify_pins(context, read_receipt)
        verify_prior_receipts(snapshots)
        write_input_sidecar(context, 'AFTER_SUCCESS', overwrite=True)
        state.update(status='DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY', stages=stages, utc=utc_now(),
                     m1_complete=False)
        atomic_json(STATE, state)
        atomic_json(NEW_MATRIX, state, overwrite=False)
        normal_complete = True
        print('DURATION_MATRIX_ACCEPTED_PRIVATE_ONLY; M1 STILL REQUIRES RECOVERY AND REVIEW', flush=True)
    except BaseException as exc:
        cleanup_in_progress = True
        census: dict[str, Any] | None = None
        stop_error: BaseException | None = None
        if owned is not None and owned.process.poll() is None:
            state.update(status='ORDERLY_ABORT_REQUESTED', error=str(exc) or type(exc).__name__, utc=utc_now(),
                         m1_complete=False)
            atomic_json(STATE, state)
            try:
                # SIGINT is intentional: protected outer code catches
                # KeyboardInterrupt and asks its inner child to clean up.
                request_orderly_abort(owned, timeout=budget['abort_wait_s'])
            except BaseException as abort_exc:
                stop_error = abort_exc
        try:
            _close_owned_if_stopped(owned)
            if child is not None and child.poll() is not None:
                _result, census = _post_stop_census(read_receipt, budget)
            elif child is not None:
                # Direct outer child is still live.  We do not send a second,
                # broader, or PID-based signal; a HOLD prevents future starts.
                census = census_native_residue(ROOT, {})
                census['direct_outer_still_live'] = True
        except BaseException as census_exc:
            if census is None:
                census = dict(clean=False, errors=['CENSUS_EXCEPTION'], detail=str(census_exc))
            if stop_error is None:
                stop_error = census_exc
        state['cleanup_census'] = census
        if stop_error is not None or (census is not None and not census.get('clean')):
            _persist_hold(state, stop_error or exc, census)
        else:
            state.update(status='BLOCKED', error=str(exc) or type(exc).__name__, utc=utc_now(),
                         m1_complete=False)
            atomic_json(STATE, state)
        raise
    finally:
        # No terminate()/kill(), no retry, and no signal to a census-discovered
        # process.  The only signal path is request_orderly_abort() above.
        if not normal_complete and child is not None and owned is None and child.poll() is None:
            # Binding failure has already persisted HOLD via the exception path.
            pass
        for signum, previous in prior_handlers.items():
            signal.signal(signum, previous)


def main() -> None:
    if os.geteuid() != 0 or os.uname().nodename != 'ubuntu-4gb-nbg1-2':
        raise RuntimeError('authorized host/root required')
    _fresh_start_guard()
    with MATRIX_LOCK.open('r+') as matrix_lock:
        fcntl.flock(matrix_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run_locked(matrix_lock)


if __name__ == '__main__':
    main()
