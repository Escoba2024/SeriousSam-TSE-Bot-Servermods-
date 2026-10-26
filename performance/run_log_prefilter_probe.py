#!/usr/bin/env python3
"""Offline-only 25-minute log-prefilter diagnostic supervisor.

This controller is deliberately separate from M1 duration acceptance.  It starts
exactly one pinned *outer* native qualifier, retains only private diagnostic
receipts, and can at most emit ``DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE`` with
``m1_complete=false``.  It never invokes the protected qualifier's ``--inner``
mode, the hardened driver's ``run_locked()``, an M1 matrix routine, or an M1
acceptance evaluator.

The only intended native source change is policy-documented and source-pinned:
``runtime_error()`` uses the reviewed safe matcher cache from
``log_error_prefilter.py`` and refreshes it when the source regex changes.
This controller neither imports nor rewrites that native source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
from types import ModuleType
from typing import Any, Callable, Iterable


# Production values deliberately have no command-line override.  Portable tests
# patch module constants to temporary files and never write /srv or /root.
BASE = Path('/root/ssam-ai-backups/m1-completion-20261026-0155')
CANDIDATE_ROOT = Path('/srv/tse-manus-m1-m4-20261026')
NATIVE = CANDIDATE_ROOT / 'performance/native/tools'
TOOLS = CANDIDATE_ROOT / 'tools'
BASE_SUPPORT = TOOLS / 'run_eight_duration_hardened.py'
DIAGNOSTIC_EVIDENCE = CANDIDATE_ROOT / 'performance/diagnostic_native_evidence.py'
PROTECTED_ORIGINAL_QUALIFIER = Path('/srv/tse-cecil-guard-20261026/tools/qualify_bot_sessions.py')
ROOT = Path('/srv/tse-session-qualification-master-m1-eight-logprefilter-probe-20261026')
MANIFEST = Path('/srv/tse-cecil-p1-build-20261025-01/manifest.json')
CONFIG = BASE / '8-duration-config.json'
BASELINE_POLICY = BASE / 'duration-policy.json'
POLICY_PATH = BASE / 'manus-log-prefilter-probe-policy-v2.json'
OFFLINE_MARKER = Path('/root/ssam-ai-backups/shutdown-20261026-0033/public-disabled.json')

CONTROLLER_LOCK = BASE / 'manus-log-prefilter-probe-controller.lock'
MATRIX_LOCK = BASE / 'matrix.lock'
STATE = BASE / 'manus-log-prefilter-probe-progress.json'
COMMAND_RECEIPT = BASE / 'manus-log-prefilter-probe-command.json'
INPUT_SIDECAR = BASE / 'manus-log-prefilter-probe-inputs.json'
CPU_EVIDENCE = BASE / 'manus-log-prefilter-probe-cpu-attribution.jsonl'
FINAL_RECEIPT = BASE / 'manus-log-prefilter-probe-final.json'
HOLD = BASE / 'manus-log-prefilter-probe-HOLD.json'
LOG = BASE / 'manus-log-prefilter-probe-controller.log'

PROC_ROOT = Path('/proc')
CGROUP_ROOT = Path('/sys/fs/cgroup')

DURATION_S = 1500
BOTS = 8
POLL_S = 0.20
CPU_SAMPLE_S = 1.0
PIN_RECHECK_S = 15.0
FINAL_FULL_POPULATION_S = 1200.0
HEX64 = re.compile(r'^[0-9a-f]{64}$')
CGROUP_NAME = re.compile(r'^tse-sessions-([1-9][0-9]*)$')
NATIVE_SCOPE = 'ISOLATED_NETNS_RETAIL_WINE'

# The copied diagnostic candidate writes its ordinary producer receipt for these
# exact five paths.  It is new provenance, never the protected eight-duration
# source inventory and never an M1 acceptance input.
PRODUCER_SOURCE_NAMES = (
    'qualify_bot_sessions.py',
    'bot_session_executor.py',
    'bot_session_runtime.py',
    'bot_sessions.py',
    'qualify_integrated_wine.py',
)

# All imports/direct data inputs used by the candidate, plus the reviewed
# prefilter.  ``native_owned_process.py`` remains in the candidate tools root;
# Phase1HumanAI.ini remains one level above the native tools directory.
DIAGNOSTIC_INPUT_NAMES = (
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
    'log_error_prefilter.py',
)

# The controller documents the sole diagnostic override in its pinned source
# and persists this exact object in its private input sidecar.  The separately
# generated policy pins the complete candidate source containing this behavior.
DIAGNOSTIC_OVERRIDES = {
    'runtime_error_mode': 'CACHED_SAFE_MATCHER',
    'matcher_source': 'performance/native/tools/log_error_prefilter.py',
    'runtime_pattern': "q.BAD.pattern + r'|FatalError:'",
    'refresh_when_pattern_changes': True,
    'default_flags_only_fast_path': True,
    'complete_log_read_each_tick': True,
    'native_guard_limits_unchanged': True,
}
POLICY_STATUS = 'PRIVATE_LOG_PREFILTER_DIAGNOSTIC_NOT_M1_ACCEPTANCE_NOT_RELEASE_AUTHORIZATION'
BASELINE_ANCHOR_FIELDS = (
    'candidate_sha256',
    'acceptance_sha256',
    'receipt_reader_sha256',
    'baseline_policy_sha256',
    'stage8_config_sha256',
    'build_manifest_sha256',
)


class PinError(RuntimeError):
    """A policy, source, configuration, or candidate pin is not trustworthy."""


class SafetyAbort(RuntimeError):
    """A launched native diagnostic lost a required lifecycle safety property."""


class CleanupHold(RuntimeError):
    """Cleanup cannot be proven; a fresh root must not be started automatically."""


@dataclass(frozen=True)
class PinContext:
    """Immutable pins verified before any pinned support module is imported."""

    policy: dict[str, Any]
    policy_sha256: str
    config: dict[str, Any]
    config_sha256: str
    manifest_sha256: str
    candidate_sha256: str
    base_sha256: str
    protected_original_sha256: str
    producer_sha256: dict[str, str]
    input_sha256: dict[str, str]


@dataclass(frozen=True)
class ProcessGeneration:
    """Non-sensitive generation identity for an owned /proc process."""

    pid: int
    start_ticks: int


@dataclass(frozen=True)
class CgroupBinding:
    """Cgroup binding proven while the direct outer and direct inner are live."""

    cgroup: Path
    outer: ProcessGeneration
    inner: ProcessGeneration


@dataclass
class CpuAttributionCollector:
    """Read-only roughly-one-second attribution evidence for this known cgroup.

    The collector never scans or signals arbitrary processes.  Before the native
    receipt proves a *new* inner cgroup directly parented by the owned outer
    process, it records only an unavailable reason.  It does not collect
    cmdlines, user identities, nicknames, logs, profiles, or query payloads.
    """

    output: Any
    outer: ProcessGeneration
    preexisting_cgroups: set[str]
    binding: CgroupBinding | None = None
    last_host: list[int] | None = None
    last_cgroup_usage_usec: int | None = None
    last_members: dict[tuple[int, int], float] = field(default_factory=dict)
    next_due_mono: float = 0.0
    records: int = 0
    unavailable: int = 0

    def maybe_sample(self, *, now_mono: float | None = None, now_epoch: float | None = None) -> None:
        now_mono = time.monotonic() if now_mono is None else now_mono
        if now_mono + 1e-9 < self.next_due_mono:
            return
        self.next_due_mono = now_mono + CPU_SAMPLE_S
        now_epoch = time.time() if now_epoch is None else now_epoch
        record: dict[str, Any] = {
            'schema': 'LOG_PREFILTER_PROBE_CPU_ATTRIBUTION_V1',
            'monotonic_s': round(now_mono, 6),
            'epoch_s': round(now_epoch, 6),
            'outer_pid': self.outer.pid,
            'outer_start_ticks': self.outer.start_ticks,
        }
        try:
            host = _host_cpu_ticks()
            record['host_procstat_delta'] = _host_delta(self.last_host, host)
            self.last_host = host
        except (OSError, ValueError, IndexError):
            record['host_procstat_delta'] = None
            record['host_procstat_unavailable'] = True
        if self.binding is None:
            record.update(availability='UNAVAILABLE_CGROUP_UNBOUND', members=[])
            self.unavailable += 1
        else:
            try:
                record.update(availability='BOUND', **self._bound_sample())
            except (OSError, ValueError, IndexError) as exc:
                # No fallback to an arbitrary process list.  The next sample can
                # recover if the process/cgroup race was transient.
                record.update(availability='UNAVAILABLE_BOUND_CGROUP_READ',
                              unavailable_reason=type(exc).__name__, members=[])
                self.unavailable += 1
        self.output.write(json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n')
        self.output.flush()
        self.records += 1

    def bind_from_result(self, result: dict[str, Any], outer_process: Any) -> None:
        """Bind only a fresh cgroup whose initial process is the direct inner child."""
        if self.binding is not None:
            return
        cgroup_text = result.get('cgroup')
        if not isinstance(cgroup_text, str):
            return
        candidate = Path(cgroup_text)
        match = CGROUP_NAME.fullmatch(candidate.name)
        if candidate.parent != CGROUP_ROOT or match is None:
            raise SafetyAbort('CPU_CGROUP_UNBOUND_PATH')
        if candidate.name in self.preexisting_cgroups:
            raise SafetyAbort('CPU_CGROUP_REUSED_BEFORE_SPAWN')
        inner_pid = int(match.group(1))
        if outer_process.poll() is not None:
            raise SafetyAbort('CPU_CGROUP_OUTER_EXITED_BEFORE_BIND')
        members = _read_cgroup_pids(candidate)
        if inner_pid not in members:
            raise SafetyAbort('CPU_CGROUP_INNER_PID_NOT_A_MEMBER')
        # Generation and PPID deliberately come from one stat snapshot.  A
        # separate /proc read here permits PID reuse between those fields.
        inner, inner_ppid = _read_generation_and_ppid(inner_pid)
        if inner_ppid != self.outer.pid:
            raise SafetyAbort('CPU_CGROUP_INNER_NOT_DIRECT_CHILD_OF_OWNED_OUTER')
        # The outer generation was captured by the pidfd helper at binding time;
        # require it to remain that direct child until this relation is observed.
        outer, _outer_ppid = _read_generation_and_ppid(self.outer.pid)
        if outer != self.outer:
            raise SafetyAbort('CPU_CGROUP_OUTER_GENERATION_CHANGED')
        # Commit only after re-reading cgroup membership and both generations.
        # This rejects exit/PID-reuse and cgroup-migration races instead of
        # attributing a transient process to the diagnostic cgroup.
        if outer_process.poll() is not None:
            raise SafetyAbort('CPU_CGROUP_OUTER_EXITED_DURING_BIND')
        if inner_pid not in _read_cgroup_pids(candidate):
            raise SafetyAbort('CPU_CGROUP_INNER_PID_NOT_MEMBER_AT_COMMIT')
        committed_inner, committed_ppid = _read_generation_and_ppid(inner_pid)
        if committed_inner != inner:
            raise SafetyAbort('CPU_CGROUP_INNER_GENERATION_CHANGED_DURING_BIND')
        if committed_ppid != self.outer.pid:
            raise SafetyAbort('CPU_CGROUP_INNER_PPID_CHANGED_DURING_BIND')
        committed_outer, _committed_outer_ppid = _read_generation_and_ppid(self.outer.pid)
        if committed_outer != self.outer:
            raise SafetyAbort('CPU_CGROUP_OUTER_GENERATION_CHANGED_DURING_BIND')
        self.binding = CgroupBinding(candidate, self.outer, inner)

    def _bound_sample(self) -> dict[str, Any]:
        assert self.binding is not None
        cgroup = self.binding.cgroup
        usage_usec = _read_cgroup_usage_usec(cgroup)
        members: list[dict[str, Any]] = []
        current_keys: set[tuple[int, int]] = set()
        for pid in _read_cgroup_pids(cgroup):
            member = _read_member_cpu(pid)
            if member is None:
                continue
            # Recheck membership and generation *after* reading CPU fields so
            # an exiting/reused PID is never emitted as a cgroup attribution.
            try:
                if pid not in _read_cgroup_pids(cgroup):
                    continue
                generation, _member_ppid = _read_generation_and_ppid(pid)
            except (OSError, ValueError, IndexError):
                continue
            if (member.get('pid') != pid or member.get('start_ticks') != generation.start_ticks):
                continue
            key = (member['pid'], member['start_ticks'])
            previous = self.last_members.get(key)
            member['cpu_delta_s'] = None if previous is None else round(max(0.0, member['cpu_s'] - previous), 6)
            members.append(member)
            current_keys.add(key)
        self.last_members = {key: next(m['cpu_s'] for m in members
                                        if (m['pid'], m['start_ticks']) == key)
                             for key in current_keys}
        delta = None if self.last_cgroup_usage_usec is None else usage_usec - self.last_cgroup_usage_usec
        self.last_cgroup_usage_usec = usage_usec
        return {
            'cgroup': str(cgroup),
            'inner_pid': self.binding.inner.pid,
            'inner_start_ticks': self.binding.inner.start_ticks,
            'cgroup_cpu_usage_usec': usage_usec,
            'cgroup_cpu_delta_usec': delta,
            'members': members,
        }

    def summary(self) -> dict[str, Any]:
        return {
            'records': self.records,
            'unavailable_records': self.unavailable,
            'cgroup_binding': None if self.binding is None else {
                'cgroup': str(self.binding.cgroup),
                'outer_pid': self.binding.outer.pid,
                'outer_start_ticks': self.binding.outer.start_ticks,
                'inner_pid': self.binding.inner.pid,
                'inner_start_ticks': self.binding.inner.start_ticks,
            },
            'contains_no_cmdlines_or_identities': True,
        }


def sha(path: Path | str) -> str:
    """Hash one required file; a missing file is always an error to the caller."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc_now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def atomic_json(path: Path, value: Any, *, overwrite: bool = True) -> None:
    """Atomically write a private 0600 receipt, never silently adopting an old one."""
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


def _read_bootstrap_object(path: Path) -> dict[str, Any]:
    """Bounded JSON read used before dynamically importing any pinned source."""
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


def _read_json(path: Path, code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PinError(code) from exc
    if not isinstance(value, dict):
        raise PinError(code)
    return value


def _require_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or HEX64.fullmatch(value) is None:
        raise PinError('PIN_POLICY_INVALID_' + label)
    return value


def _producer_paths() -> dict[str, Path]:
    return {name: NATIVE / name for name in PRODUCER_SOURCE_NAMES}


def _diagnostic_input_paths() -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for name in DIAGNOSTIC_INPUT_NAMES:
        if name == 'native_owned_process.py':
            paths[name] = TOOLS / name
        elif name == 'poc/scripts/Phase1HumanAI.ini':
            paths[name] = NATIVE.parent / name
        else:
            paths[name] = NATIVE / name
    return paths


def _check_exact_map(policy: dict[str, Any], field: str, paths: dict[str, Path]) -> dict[str, str]:
    expected = policy.get(field)
    if not isinstance(expected, dict) or set(expected) != set(paths):
        raise PinError('PIN_POLICY_' + field.upper() + '_EXACT_KEYS_REQUIRED')
    checked: dict[str, str] = {}
    for name, path in paths.items():
        expected_digest = _require_digest(expected.get(name), field.upper() + '_' + name.replace('/', '_'))
        try:
            actual = sha(path)
        except OSError as exc:
            raise PinError('PIN_INPUT_UNREADABLE_' + name.replace('/', '_')) from exc
        if actual != expected_digest:
            raise PinError('PIN_INPUT_DRIFT_' + name.replace('/', '_'))
        checked[name] = actual
    return checked


def _require_config_shape(config: dict[str, Any]) -> int:
    """The unchanged eight-bot configuration may only set the known fixed shape."""
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


def _require_policy_metadata(policy: dict[str, Any]) -> None:
    """Require the generated policy's immutable baseline anchors and bounds."""
    if policy.get('status') != POLICY_STATUS:
        raise PinError('PIN_POLICY_STATUS_INVALID')
    if policy.get('m1_complete') is not False:
        raise PinError('PIN_POLICY_M1_COMPLETE_MUST_BE_FALSE')
    if policy.get('diagnostic_duration_s') != DURATION_S:
        raise PinError('PIN_POLICY_DIAGNOSTIC_DURATION_INVALID')
    if policy.get('diagnostic_min_full_population_s') != int(FINAL_FULL_POPULATION_S):
        raise PinError('PIN_POLICY_DIAGNOSTIC_FULL_POPULATION_INVALID')
    for field in BASELINE_ANCHOR_FIELDS:
        _require_digest(policy.get(field), field.upper())
    _require_digest(policy.get('hardened_support_sha256'), 'HARDENED_SUPPORT')
    _require_digest(policy.get('protected_original_qualifier_sha256'), 'PROTECTED_ORIGINAL_QUALIFIER')


def _check_base_pin(policy: dict[str, Any]) -> str:
    expected = _require_digest(policy.get('hardened_support_sha256'), 'HARDENED_SUPPORT')
    try:
        actual = sha(BASE_SUPPORT)
    except OSError as exc:
        raise PinError('PIN_BASE_CONTROLLER_UNREADABLE') from exc
    if actual != expected:
        raise PinError('PIN_BASE_CONTROLLER_DRIFT')
    return actual


def _check_receipt_reader_pin(policy: dict[str, Any]) -> None:
    expected = _require_digest(policy.get('receipt_reader_sha256'), 'RECEIPT_READER')
    try:
        actual = sha(TOOLS / 'native_receipt_io.py')
    except OSError as exc:
        raise PinError('PIN_RECEIPT_READER_UNREADABLE') from exc
    if actual != expected:
        raise PinError('PIN_RECEIPT_READER_DRIFT')


def _check_diagnostic_evidence_pin(policy: dict[str, Any]) -> None:
    expected = _require_digest(policy.get('diagnostic_evidence_sha256'), 'DIAGNOSTIC_EVIDENCE')
    try:
        actual = sha(DIAGNOSTIC_EVIDENCE)
    except OSError as exc:
        raise PinError('PIN_DIAGNOSTIC_EVIDENCE_UNREADABLE') from exc
    if actual != expected:
        raise PinError('PIN_DIAGNOSTIC_EVIDENCE_DRIFT')


def _check_baseline_policy_pin(policy: dict[str, Any]) -> None:
    expected = _require_digest(policy.get('baseline_policy_sha256'), 'BASELINE_POLICY')
    try:
        actual = sha(BASELINE_POLICY)
    except OSError as exc:
        raise PinError('PIN_BASELINE_POLICY_UNREADABLE') from exc
    if actual != expected:
        raise PinError('PIN_BASELINE_POLICY_DRIFT')


def _check_protected_original_pin(policy: dict[str, Any]) -> str:
    expected = _require_digest(policy.get('protected_original_qualifier_sha256'),
                               'PROTECTED_ORIGINAL_QUALIFIER')
    try:
        actual = sha(PROTECTED_ORIGINAL_QUALIFIER)
    except OSError as exc:
        raise PinError('PIN_PROTECTED_ORIGINAL_QUALIFIER_UNREADABLE') from exc
    if actual != expected:
        raise PinError('PIN_PROTECTED_ORIGINAL_QUALIFIER_DRIFT')
    return actual


def _check_config_manifest_candidate(policy: dict[str, Any]) -> tuple[dict[str, Any], str, str, str]:
    config_expected = _require_digest(policy.get('stage8_config_sha256'), 'STAGE8_CONFIG')
    manifest_expected = _require_digest(policy.get('build_manifest_sha256'), 'BUILD_MANIFEST')
    candidate_expected = _require_digest(policy.get('candidate_sha256'), 'CANDIDATE')
    try:
        config_digest = sha(CONFIG)
    except OSError as exc:
        raise PinError('PIN_STAGE8_CONFIG_UNREADABLE') from exc
    if config_digest != config_expected:
        raise PinError('PIN_STAGE8_CONFIG_DRIFT')
    config = _read_json(CONFIG, 'PIN_STAGE8_CONFIG_READ_FAILED')
    _require_config_shape(config)
    try:
        manifest_digest = sha(MANIFEST)
    except OSError as exc:
        raise PinError('PIN_BUILD_MANIFEST_UNREADABLE') from exc
    if manifest_digest != manifest_expected:
        raise PinError('PIN_BUILD_MANIFEST_DRIFT')
    manifest = _read_json(MANIFEST, 'PIN_BUILD_MANIFEST_READ_FAILED')
    if manifest.get('build_ok') is not True or manifest.get('dll_sha256') != candidate_expected:
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_MISMATCH')
    candidate = manifest.get('candidate')
    if not isinstance(candidate, str) or not candidate:
        raise PinError('PIN_BUILD_MANIFEST_CANDIDATE_PATH_INVALID')
    try:
        if sha(Path(candidate)) != candidate_expected:
            raise PinError('PIN_CANDIDATE_DRIFT')
    except OSError as exc:
        raise PinError('PIN_CANDIDATE_UNREADABLE') from exc
    return config, config_digest, manifest_digest, candidate_expected


def bootstrap_pins() -> PinContext:
    """Verify policy, base, candidate, and all eleven inputs before any import.

    The dynamic hardened support module and the candidate's OwnedProcess helper
    are loaded only later, after this complete source/configuration bootstrap.
    The native qualifier itself is never imported by this supervisor.
    """
    policy = _read_bootstrap_object(POLICY_PATH)
    _require_policy_metadata(policy)
    base_digest = _check_base_pin(policy)
    _check_receipt_reader_pin(policy)
    _check_diagnostic_evidence_pin(policy)
    _check_baseline_policy_pin(policy)
    protected_original_digest = _check_protected_original_pin(policy)
    producer = _check_exact_map(policy, 'harness_sha256', _producer_paths())
    inputs = _check_exact_map(policy, 'stage8_additional_input_sha256', _diagnostic_input_paths())
    config, config_digest, manifest_digest, candidate_digest = _check_config_manifest_candidate(policy)
    return PinContext(policy=policy, policy_sha256=sha(POLICY_PATH), config=config,
                      config_sha256=config_digest, manifest_sha256=manifest_digest,
                      candidate_sha256=candidate_digest, base_sha256=base_digest,
                      protected_original_sha256=protected_original_digest,
                      producer_sha256=producer, input_sha256=inputs)


def verify_pins(context: PinContext) -> None:
    """Repeat every static check without importing candidate application code."""
    try:
        if sha(POLICY_PATH) != context.policy_sha256:
            raise PinError('PIN_POLICY_DRIFT')
    except OSError as exc:
        raise PinError('PIN_POLICY_UNREADABLE') from exc
    _require_policy_metadata(context.policy)
    if _check_base_pin(context.policy) != context.base_sha256:
        raise PinError('PIN_BASE_CONTROLLER_DRIFT')
    _check_receipt_reader_pin(context.policy)
    _check_diagnostic_evidence_pin(context.policy)
    _check_baseline_policy_pin(context.policy)
    if _check_protected_original_pin(context.policy) != context.protected_original_sha256:
        raise PinError('PIN_PROTECTED_ORIGINAL_QUALIFIER_DRIFT')
    if _check_exact_map(context.policy, 'harness_sha256', _producer_paths()) != context.producer_sha256:
        raise PinError('PIN_PRODUCER_MAP_DRIFT')
    if (_check_exact_map(context.policy, 'stage8_additional_input_sha256', _diagnostic_input_paths()) !=
            context.input_sha256):
        raise PinError('PIN_INPUT_MAP_DRIFT')
    config, config_digest, manifest_digest, candidate_digest = _check_config_manifest_candidate(context.policy)
    if (config_digest != context.config_sha256 or manifest_digest != context.manifest_sha256 or
            candidate_digest != context.candidate_sha256 or config != context.config):
        raise PinError('PIN_STATIC_CONTEXT_DRIFT')


def _load_pinned_module(module_name: str, path: Path) -> ModuleType:
    """Import only a source already verified by bootstrap_pins()."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError('module spec unavailable')
        module = importlib.util.module_from_spec(spec)
        previous = sys.modules.get(module_name)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            if previous is None:
                sys.modules.pop(module_name, None)
            else:
                sys.modules[module_name] = previous
            raise
        return module
    except BaseException as exc:
        raise PinError('PINNED_MODULE_LOAD_FAILED_' + path.name) from exc


def load_pinned_receipt_reader(context: PinContext) -> Callable:
    """Use the existing bounded retry reader for native truncate+write receipts."""
    _check_receipt_reader_pin(context.policy)
    module = _load_pinned_module('_log_prefilter_probe_native_receipt_io',
                                 TOOLS / 'native_receipt_io.py')
    reader = getattr(module, 'read_receipt', None)
    if not callable(reader):
        raise PinError('PINNED_RECEIPT_READER_MISSING')
    return reader


def load_pinned_support(context: PinContext) -> tuple[ModuleType, type]:
    """Load hardened support primitives and the exact candidate pidfd helper.

    This deliberately does not call the base runner, its main entry point, any
    prior-stage routine, or its duration/matrix acceptance routine.
    """
    support = _load_pinned_module('_log_prefilter_probe_hardened_support', BASE_SUPPORT)
    required = ('derive_budget', 'check_live_heartbeat', 'census_native_residue',
                'wait_for_clean_census', 'request_orderly_abort')
    if any(not callable(getattr(support, name, None)) for name in required):
        raise PinError('PINNED_BASE_SUPPORT_PRIMITIVE_MISSING')
    # Supply only the diagnostic runtime constants to the reused support
    # primitives.  The source was hash-pinned before this import.
    support.ROOT = ROOT
    support.DURATION_S = DURATION_S
    support.BOTS = BOTS
    support.CGROUP_ROOT = CGROUP_ROOT
    support.PROC_ROOT = PROC_ROOT
    support.MOUNTINFO = PROC_ROOT / 'self/mountinfo'
    try:
        loader = getattr(support, '_load_module_from_path')
        owned_module = loader('_log_prefilter_probe_owned_process', TOOLS / 'native_owned_process.py')
        owned = getattr(owned_module, 'OwnedProcess')
    except BaseException as exc:
        raise PinError('PINNED_OWNED_PROCESS_HELPER_MISSING') from exc
    if owned is None:
        raise PinError('PINNED_OWNED_PROCESS_HELPER_MISSING')
    return support, owned


def _assert_native_outer_guard_contract() -> None:
    """Pin plus a narrow source-shape check preserves the native global lock."""
    try:
        source = (NATIVE / 'qualify_bot_sessions.py').read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as exc:
        raise PinError('PIN_NATIVE_OUTER_SOURCE_UNREADABLE') from exc
    required = ('/srv/tse-session-qualification.lock', 'fcntl.LOCK_EX', "['--inner']")
    if any(token not in source for token in required):
        raise PinError('PIN_NATIVE_GLOBAL_GUARD_CONTRACT_MISSING')


def build_fixed_outer_argv() -> list[str]:
    """The single authorized outer command; direct inner/default routes are absent."""
    return [
        '/usr/bin/python3', '-u', str(NATIVE / 'qualify_bot_sessions.py'),
        '--config', str(CONFIG), '--runtime', str(ROOT), '--duration', str(DURATION_S),
        '--execute', '--cecil-p1', '--preset', 'redstation', '--port', '27160', '--display', ':157',
        '--build-manifest', str(MANIFEST), '--offline-public-marker', str(OFFLINE_MARKER),
    ]


def validate_fixed_outer_argv(argv: list[str]) -> None:
    if argv != build_fixed_outer_argv() or '--inner' in argv:
        raise RuntimeError('FIXED_OUTER_ARGV_REQUIRED; direct inner/default invocation is forbidden')


def write_input_sidecar(context: PinContext, phase: str, *, overwrite: bool) -> None:
    actual_producer = _check_exact_map(context.policy, 'harness_sha256', _producer_paths())
    actual_inputs = _check_exact_map(context.policy, 'stage8_additional_input_sha256', _diagnostic_input_paths())
    atomic_json(INPUT_SIDECAR, {
        'schema': 'LOG_PREFILTER_PROBE_INPUT_INVENTORY_V1',
        'phase': phase,
        'utc': utc_now(),
        'policy_sha256': context.policy_sha256,
        'hardened_support_sha256': context.base_sha256,
        'protected_original_qualifier_sha256': context.protected_original_sha256,
        'config_sha256': context.config_sha256,
        'harness_sha256': actual_producer,
        'stage8_additional_input_sha256': actual_inputs,
        'diagnostic_overrides': DIAGNOSTIC_OVERRIDES,
        'formal_m1_source_inventory_untouched': True,
        'm1_complete': False,
    }, overwrite=overwrite)


def _fresh_start_guard() -> None:
    if ROOT.exists():
        raise RuntimeError('fresh diagnostic root required; never adopt a prior result/runtime')
    if HOLD.exists():
        raise CleanupHold('PERSISTENT_CLEANUP_HOLD_PRESENT; manual inspection required; no retry')
    for path in (STATE, COMMAND_RECEIPT, INPUT_SIDECAR, CPU_EVIDENCE, FINAL_RECEIPT, LOG):
        if path.exists():
            raise RuntimeError('fresh private diagnostic receipt required; never adopt or overwrite: ' + str(path))


def _open_private_lock(path: Path):
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    stream = os.fdopen(fd, 'r+')
    try:
        mode = os.fstat(stream.fileno()).st_mode
        if not stat.S_ISREG(mode):
            raise RuntimeError('private controller lock must be a regular file')
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return stream
    except BaseException:
        stream.close()
        raise


def _open_existing_matrix_lock(path: Path):
    """Lock the base driver's existing matrix lock without creating or writing it."""
    flags = os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise RuntimeError('SHARED_MATRIX_LOCK_OPEN_FAILED') from exc
    stream = os.fdopen(fd, 'r+')
    try:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise RuntimeError('shared matrix lock must be a regular file')
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('SHARED_MATRIX_LOCK_BUSY_BEFORE_SPAWN') from exc
        return stream
    except BaseException:
        stream.close()
        raise


def _open_cpu_evidence() -> Any:
    stream = CPU_EVIDENCE.open('x', encoding='utf-8')
    CPU_EVIDENCE.chmod(0o600)
    return stream


def _new_cgroup_names() -> set[str]:
    try:
        return {path.name for path in CGROUP_ROOT.iterdir() if path.is_dir() and CGROUP_NAME.fullmatch(path.name)}
    except OSError as exc:
        raise SafetyAbort('CPU_CGROUP_PRESPAWN_CENSUS_UNAVAILABLE') from exc


def _host_cpu_ticks() -> list[int]:
    fields = (PROC_ROOT / 'stat').read_text(encoding='utf-8').splitlines()[0].split()[1:9]
    values = [int(value) for value in fields]
    if len(values) < 5:
        raise ValueError('procstat fields missing')
    return values


def _host_delta(previous: list[int] | None, current: list[int]) -> dict[str, Any] | None:
    if previous is None or len(previous) != len(current):
        return None
    deltas = [new - old for old, new in zip(previous, current)]
    if any(delta < 0 for delta in deltas):
        return {'reset': True}
    total = sum(deltas)
    idle = deltas[3] + deltas[4]
    return {
        'total_ticks': total,
        'busy_ticks': total - idle,
        'idle_ticks': idle,
        'busy_percent': None if total <= 0 else round(100.0 * (total - idle) / total, 4),
    }


def _read_cgroup_pids(cgroup: Path) -> list[int]:
    values = (cgroup / 'cgroup.procs').read_text(encoding='utf-8').split()
    return sorted({int(value) for value in values})


def _read_cgroup_usage_usec(cgroup: Path) -> int:
    fields = dict(line.split(None, 1) for line in (cgroup / 'cpu.stat').read_text(encoding='utf-8').splitlines())
    return int(fields['usage_usec'])


def _stat_tail(pid: int) -> list[str]:
    return (PROC_ROOT / str(pid) / 'stat').read_text(encoding='utf-8').rsplit(') ', 1)[1].split()


def _read_generation(pid: int) -> ProcessGeneration:
    generation, _ppid = _read_generation_and_ppid(pid)
    return generation


def _read_ppid(pid: int) -> int:
    _generation, ppid = _read_generation_and_ppid(pid)
    return ppid


def _read_generation_and_ppid(pid: int) -> tuple[ProcessGeneration, int]:
    """Return process generation and parent from one /proc/<pid>/stat read."""
    fields = _stat_tail(pid)
    return ProcessGeneration(pid=pid, start_ticks=int(fields[19])), int(fields[1])


def _read_member_cpu(pid: int) -> dict[str, Any] | None:
    try:
        fields = _stat_tail(pid)
        start_ticks = int(fields[19])
        cpu_s = (int(fields[11]) + int(fields[12])) / os.sysconf('SC_CLK_TCK')
        rss_mib = int(fields[21]) * os.sysconf('SC_PAGE_SIZE') / 1024 ** 2
        comm = (PROC_ROOT / str(pid) / 'comm').read_text(encoding='utf-8').strip()
    except (OSError, ValueError, IndexError):
        return None
    return {'pid': pid, 'start_ticks': start_ticks, 'cpu_s': round(cpu_s, 6),
            'comm': comm, 'rss_mib': round(rss_mib, 6)}


def _close_owned_if_stopped(owned: Any | None) -> None:
    if owned is not None and owned.process.poll() is not None:
        owned.close()


def _post_stop_census(support: ModuleType, *, timeout: float) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        result = _read_json(ROOT / 'result.json', 'CENSUS_RESULT_UNAVAILABLE')
    except PinError as exc:
        raise CleanupHold(str(exc)) from exc
    census = support.wait_for_clean_census(ROOT, result, timeout=timeout)
    if not census.get('clean'):
        raise CleanupHold('NATIVE_RESOURCE_CENSUS_UNRESOLVED: ' + json.dumps(census, sort_keys=True))
    return result, census


def _best_effort_post_stop_census(support: ModuleType, *, timeout: float) -> tuple[dict[str, Any] | None, dict[str, Any], BaseException | None]:
    """Always obtain an independent census, even if the final receipt is absent."""
    try:
        result, census = _post_stop_census(support, timeout=timeout)
        return result, census, None
    except BaseException as exc:
        try:
            census = dict(support.census_native_residue(ROOT, {}))
        except BaseException as census_exc:
            census = {'clean': False, 'errors': ['CENSUS_EXCEPTION'], 'detail': str(census_exc)}
        errors = list(census.get('errors', []))
        errors.append('POST_STOP_CENSUS_RECEIPT_UNAVAILABLE')
        census.update(clean=False, errors=sorted(set(errors)), post_stop_error=str(exc))
        return None, census, exc


def _live_receipt_matches_owned_context(result: dict[str, Any], context: PinContext,
                                        collector: CpuAttributionCollector | None) -> bool:
    """Accept only a current native receipt consistent with known ownership facts."""
    if result.get('scope') != NATIVE_SCOPE:
        return False
    dll_sha256 = result.get('dll_sha256')
    if dll_sha256 is not None and dll_sha256 != context.candidate_sha256:
        return False
    cgroup_text = result.get('cgroup')
    if cgroup_text is not None:
        if not isinstance(cgroup_text, str):
            return False
        candidate = Path(cgroup_text)
        if candidate.parent != CGROUP_ROOT or CGROUP_NAME.fullmatch(candidate.name) is None:
            return False
        if collector is not None and collector.binding is not None and candidate != collector.binding.cgroup:
            return False
    return True


def _classify_current_signal_state(read_live_receipt: Callable, context: PinContext,
                                   collector: CpuAttributionCollector | None) -> tuple[str, str]:
    """Make the only signal decision from a fresh pinned-reader receipt pair."""
    try:
        guard = read_live_receipt(ROOT / 'host-guard.json')
        result = read_live_receipt(ROOT / 'result.json')
    except BaseException as exc:
        return 'AMBIGUOUS', 'LIVE_RECEIPT_UNREADABLE_' + type(exc).__name__
    if not isinstance(guard, dict) or not isinstance(result, dict):
        return 'AMBIGUOUS', 'LIVE_RECEIPT_OBJECT_REQUIRED'
    if not _live_receipt_matches_owned_context(result, context, collector):
        return 'AMBIGUOUS', 'LIVE_RECEIPT_OWNERSHIP_MISMATCH'
    if (result.get('status') == 'FAIL' and
            guard.get('status') in ('MONITORING', 'STOPPED_GUARD', 'FINISHED')):
        return 'NATIVE_FAILURE_CLEANUP', 'CURRENT_NATIVE_FAIL_CLEANUP'
    if result.get('status') == 'MEASURING' and guard.get('status') == 'MONITORING':
        return 'OWNED_MEASURING', 'CURRENT_MEASURING_MONITORING'
    return 'AMBIGUOUS', 'LIVE_RECEIPT_STATUS_OR_GUARD_AMBIGUOUS'


def _wait_without_signal(child: Any, *, timeout: float) -> None:
    """Bounded wait for the directly launched child; never signal an unbound PID."""
    if child.poll() is not None:
        return
    try:
        child.wait(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise CleanupHold('OWNED_OUTER_WAIT_TIMEOUT_WITHOUT_ADDITIONAL_SIGNAL') from exc


def _persistence_failure(persistence_errors: list[dict[str, str]], label: str,
                         exc: BaseException, state: dict[str, Any] | None) -> None:
    entry = {'label': label, 'error': type(exc).__name__, 'detail': str(exc)}
    persistence_errors.append(entry)
    if state is not None:
        state['persistence_errors'] = list(persistence_errors)
    try:
        print('PERSISTENCE_FAILURE ' + json.dumps(entry, sort_keys=True), file=sys.stderr, flush=True)
    except BaseException:
        pass


def robust_best_effort_persist(persistence_errors: list[dict[str, str]], label: str,
                               action: Callable[[], None], *, state: dict[str, Any] | None = None) -> bool:
    """Persist diagnostics without allowing a write failure to interrupt cleanup."""
    if state is not None:
        state['persistence_errors'] = list(persistence_errors)
    try:
        action()
        return True
    except BaseException as exc:
        _persistence_failure(persistence_errors, label, exc, state)
        return False


def _persist_or_abort(persistence_errors: list[dict[str, str]], label: str,
                      action: Callable[[], None], state: dict[str, Any]) -> None:
    if not robust_best_effort_persist(persistence_errors, label, action, state=state):
        raise SafetyAbort('PERSISTENCE_FAILED_' + label)


def _persist_hold(state: dict[str, Any], reason: BaseException | str,
                  census: dict[str, Any] | None, collector: CpuAttributionCollector | None,
                  persistence_errors: list[dict[str, str]]) -> None:
    text = str(reason) or type(reason).__name__
    state.update(status='CLEANUP_HOLD', error=text, no_retry=True, cleanup_census=census,
                 cpu_attribution=None if collector is None else collector.summary(), utc=utc_now(),
                 m1_complete=False)
    robust_best_effort_persist(persistence_errors, 'STATE_CLEANUP_HOLD',
                               lambda: atomic_json(STATE, state), state=state)

    def write_hold() -> None:
        if HOLD.exists():
            return
        atomic_json(HOLD, {
            'status': 'HOLD', 'reason': text, 'utc': utc_now(), 'no_retry': True,
            'runtime': str(ROOT), 'cleanup_census': census,
            'cpu_attribution': None if collector is None else collector.summary(),
            'm1_complete': False,
            'persistence_errors': list(persistence_errors),
            'instruction': 'Do not restart. Inspect retained root manually; no foreign process is signalled.',
        }, overwrite=False)
    robust_best_effort_persist(persistence_errors, 'HOLD_RECEIPT', write_hold, state=state)


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise RuntimeError(label + '_UNREADABLE') from exc
    rows: list[dict[str, Any]] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(label + '_INVALID_JSONL') from exc
        if not isinstance(row, dict):
            raise RuntimeError(label + '_ROW_INVALID')
        rows.append(row)
    if not rows:
        raise RuntimeError(label + '_EMPTY')
    return rows


def _expected_ids(config: dict[str, Any]) -> list[str]:
    identities = config['identities']
    values = [item.get('id') for item in identities if isinstance(item, dict)]
    if len(values) != BOTS or any(not isinstance(value, str) or not value for value in values) or len(set(values)) != BOTS:
        raise RuntimeError('DIAGNOSTIC_IDENTITY_IDS_INVALID')
    return values


def _log_and_raw_telemetry_inventory(config: dict[str, Any]) -> dict[str, Any]:
    """Check post-unmount overlay upper files by metadata only; never read raw data."""
    roles = ['server', 'vanilla'] + _expected_ids(config)
    logs: list[dict[str, Any]] = []
    raw_telemetry: list[dict[str, Any]] = []
    for role in roles:
        filename = 'Dedicated_BotTest.log' if role == 'server' else 'SeriousSam.log'
        path = ROOT / 'layers' / role / 'upper' / filename
        try:
            info = path.stat()
        except OSError as exc:
            raise RuntimeError('DIAGNOSTIC_COMPLETE_LOG_MISSING_' + role) from exc
        if not stat.S_ISREG(info.st_mode) or info.st_size <= 0:
            raise RuntimeError('DIAGNOSTIC_COMPLETE_LOG_INVALID_' + role)
        logs.append({'role': role, 'bytes': info.st_size})
    for role in _expected_ids(config):
        path = ROOT / 'layers' / role / 'upper/Bin/BotTelemetry.csv'
        try:
            info = path.stat()
        except OSError as exc:
            raise RuntimeError('DIAGNOSTIC_RAW_TELEMETRY_MISSING_' + role) from exc
        if not stat.S_ISREG(info.st_mode) or info.st_size <= 0:
            raise RuntimeError('DIAGNOSTIC_RAW_TELEMETRY_INVALID_' + role)
        raw_telemetry.append({'role': role, 'bytes': info.st_size})
    return {'complete_log_count': len(logs), 'logs': logs,
            'raw_telemetry_count': len(raw_telemetry), 'raw_telemetry': raw_telemetry}


def _full_population_summary() -> dict[str, Any]:
    rows = _read_jsonl(ROOT / 'samples.jsonl', 'DIAGNOSTIC_SAMPLES')
    last_elapsed = -1.0
    segment_start: float | None = None
    last_full: float | None = None
    longest = 0.0
    for row in rows:
        elapsed = row.get('elapsed_s')
        active = row.get('active')
        if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0:
            raise RuntimeError('DIAGNOSTIC_SAMPLES_ELAPSED_INVALID')
        elapsed = float(elapsed)
        if elapsed + 0.001 < last_elapsed:
            raise RuntimeError('DIAGNOSTIC_SAMPLES_ELAPSED_REGRESSED')
        full = active == BOTS
        if full:
            if segment_start is None or (last_full is not None and elapsed - last_full > 3.0):
                segment_start = elapsed
            last_full = elapsed
            longest = max(longest, elapsed - segment_start)
        else:
            segment_start = None
            last_full = None
        last_elapsed = elapsed
    if longest < FINAL_FULL_POPULATION_S:
        raise RuntimeError('DIAGNOSTIC_FULL_POPULATION_BELOW_1200S')
    return {'longest_contiguous_full_population_s': round(longest, 3), 'sample_rows': len(rows)}


def _telemetry_summary(result: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    telemetry = result.get('telemetry')
    if not isinstance(telemetry, dict):
        raise RuntimeError('DIAGNOSTIC_TELEMETRY_MISSING')
    accepted: list[str] = []
    for identity in _expected_ids(config):
        windows = telemetry.get(identity)
        if not isinstance(windows, list) or not windows:
            raise RuntimeError('DIAGNOSTIC_TELEMETRY_IDENTITY_MISSING_' + identity)
        active_ok = False
        for window in windows:
            if not isinstance(window, dict):
                continue
            reports = window.get('reports')
            if not isinstance(reports, list):
                continue
            for report in reports:
                if not isinstance(report, dict):
                    continue
                hz = report.get('tick_hz_median')
                if (report.get('verdict') == 'ACTIVE_OK' and report.get('lp_median') == 1 and
                        type(hz) in (int, float) and 18 <= hz <= 22 and
                        report.get('render_skip_total', 0) > 0 and report.get('render_draw_total') == 0 and
                        isinstance(report.get('config'), dict) and report['config'].get('nullrender') == '1'):
                    active_ok = True
        if not active_ok:
            raise RuntimeError('DIAGNOSTIC_ACTIVE_OK_20HZ_MISSING_' + identity)
        accepted.append(identity)
    return {'active_ok_20hz_identities': accepted, 'count': len(accepted)}


def _cleanup_summary(result: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    cleanup = result.get('cleanup')
    if not isinstance(cleanup, list):
        raise RuntimeError('DIAGNOSTIC_CLEANUP_MISSING')
    expected = {'server', 'vanilla', *_expected_ids(config)}
    observed: set[str] = set()
    for row in cleanup:
        if not isinstance(row, dict):
            raise RuntimeError('DIAGNOSTIC_CLEANUP_ROW_INVALID')
        role = row.get('role')
        if isinstance(role, str) and role in expected:
            observed.add(role)
        if row.get('errors'):
            raise RuntimeError('DIAGNOSTIC_CLEANUP_ERRORS')
    if observed != expected or result.get('all_bots_drained') is not True:
        raise RuntimeError('DIAGNOSTIC_CLEANUP_INCOMPLETE')
    unmounts = result.get('unmounts')
    if not isinstance(unmounts, list) or len(unmounts) != 2 * (BOTS + 2):
        raise RuntimeError('DIAGNOSTIC_UNMOUNT_COUNT_INVALID')
    if any(not isinstance(row, dict) or row.get('exitcode') != 0 for row in unmounts):
        raise RuntimeError('DIAGNOSTIC_UNMOUNT_FAILED')
    return {'cleanup_roles': sorted(observed), 'unmount_count': len(unmounts), 'all_bots_drained': True}


def evaluate_diagnostic_final(*, result: dict[str, Any], guard: dict[str, Any], exitcode: int,
                              config: dict[str, Any], census: dict[str, Any],
                              collector: CpuAttributionCollector, context: PinContext) -> dict[str, Any]:
    """Source-pinned independent diagnostic validation; never a relaxed M1 gate."""
    if exitcode != 0:
        raise RuntimeError('DIAGNOSTIC_OUTER_EXIT_NONZERO')
    if collector.binding is None:
        raise RuntimeError('DIAGNOSTIC_CPU_CGROUP_NEVER_OWNED_BOUND')
    _check_diagnostic_evidence_pin(context.policy)
    evidence = _load_pinned_module('_log_prefilter_probe_independent_evidence', DIAGNOSTIC_EVIDENCE)
    verdict = evidence.validate_probe_evidence(root=ROOT, result=result, guard=guard, config=config,
        census=census, candidate_sha256=context.candidate_sha256,
        bound_cgroup=str(collector.binding.cgroup), harness_sha256=context.producer_sha256)
    verdict.update(outer_exitcode=exitcode, cpu_attribution=collector.summary())
    return verdict


def _record_pre_spawn_block(reason: BaseException) -> None:
    """Persist a no-spawn block once; it also prevents implicit automatic retry."""
    if not STATE.exists():
        atomic_json(STATE, {'status': 'BLOCKED', 'phase': 'PRE_SPAWN',
                            'error': str(reason) or type(reason).__name__, 'utc': utc_now(),
                            'm1_complete': False, 'no_retry': True}, overwrite=False)


def run_probe_locked(_controller_lock: Any, _matrix_lock: Any | None = None) -> None:
    """Run one pinned diagnostic while both controller serialisation locks are held."""
    context = bootstrap_pins()
    verify_pins(context)
    _assert_native_outer_guard_contract()
    support, OwnedProcess = load_pinned_support(context)
    read_live_receipt = load_pinned_receipt_reader(context)
    budget = support.derive_budget(context.config)
    argv = build_fixed_outer_argv()
    validate_fixed_outer_argv(argv)

    # These receipts precede Popen.  If any one fails, there is no native child
    # whose cleanup could be bypassed.
    atomic_json(COMMAND_RECEIPT, {
        'schema': 'LOG_PREFILTER_PROBE_FIXED_OUTER_ARGV_V1', 'argv': argv,
        'duration_s': DURATION_S, 'bots': BOTS, 'direct_inner_forbidden': True,
        'native_global_guard_preserved_by_pinned_outer_source': True,
        'diagnostic_only': True, 'm1_complete': False,
    }, overwrite=False)
    write_input_sidecar(context, 'BEFORE_START', overwrite=False)
    state: dict[str, Any] = {
        'status': 'STARTING_LOG_PREFILTER_PROBE', 'utc': utc_now(), 'm1_complete': False,
        'no_retry': True, 'duration_s': DURATION_S, 'bots': BOTS, 'budget': budget,
        'fixed_outer_argv': argv, 'candidate_sha256': context.candidate_sha256,
        'diagnostic_overrides': DIAGNOSTIC_OVERRIDES,
    }
    atomic_json(STATE, state, overwrite=False)

    child = None
    owned = None
    collector: CpuAttributionCollector | None = None
    evidence = None
    heartbeat: dict[str, Any] = {}
    launched_mono = time.monotonic()
    last_pin_check = float('-inf')
    normal_complete = False
    cleanup_in_progress = False
    prior_handlers: dict[int, Any] = {}
    persistence_errors: list[dict[str, str]] = []

    def interrupted(signum: int, _frame: Any) -> None:
        # Never let a second controller signal release either serialization lock
        # while this controller is still waiting or censusing its own child.
        if cleanup_in_progress:
            return
        raise SafetyAbort('DRIVER_SIGNAL_' + str(signum) + '_ORDERLY_ABORT_REQUIRED')

    for signum in (signal.SIGINT, signal.SIGTERM):
        prior_handlers[signum] = signal.signal(signum, interrupted)

    try:
        preexisting_cgroups = _new_cgroup_names()
        evidence = _open_cpu_evidence()
        with LOG.open('xb') as log:
            LOG.chmod(0o600)
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                     env=dict(os.environ, PYTHONOPTIMIZE='0'))
        try:
            owned = OwnedProcess(child)
        except BaseException as exc:
            # A Popen child exists, but identity binding did not.  The exception
            # path below holds, waits only for that direct child, and censes; it
            # never sends a signal to an unbound PID.
            raise CleanupHold('DIRECT_CHILD_PIDFD_OWNERSHIP_BIND_FAILED') from exc
        outer_generation = ProcessGeneration(child.pid, int(owned.start_ticks))
        collector = CpuAttributionCollector(evidence, outer_generation, preexisting_cgroups)
        state.update(status='LOG_PREFILTER_PROBE_RUNNING', controller_pid=child.pid, utc=utc_now())
        _persist_or_abort(persistence_errors, 'STATE_RUNNING', lambda: atomic_json(STATE, state), state)
        print('LOG_PREFILTER_PROBE_STARTED pid=' + str(child.pid), flush=True)

        deadline = launched_mono + budget['total_s']
        while child.poll() is None:
            now_mono = time.monotonic()
            collector.maybe_sample(now_mono=now_mono, now_epoch=time.time())
            if now_mono > deadline:
                raise SafetyAbort('FULL_LIFECYCLE_DEADLINE_EXCEEDED_NO_RETRY')
            if now_mono - last_pin_check >= PIN_RECHECK_S:
                verify_pins(context)
                _assert_native_outer_guard_contract()
                _persist_or_abort(persistence_errors, 'INPUT_SIDECAR_DURING',
                                  lambda: write_input_sidecar(context, 'DURING_RUN', overwrite=True), state)
                # The pinned bounded reader is passed unchanged to both the
                # heartbeat helper and live cgroup binding paths.
                heartbeat = support.check_live_heartbeat(
                    read_live_receipt,
                    launched_mono=launched_mono, now_mono=now_mono,
                    now_epoch=time.time(), budget=budget, previous=heartbeat)
                try:
                    running_result = read_live_receipt(ROOT / 'result.json')
                except BaseException:
                    # A transient truncate/write race has no ownership value;
                    # the reader is retried by the next tick and does not signal.
                    running_result = {}
                collector.bind_from_result(running_result, child)
                state.update(status='LOG_PREFILTER_PROBE_RUNNING', heartbeat=heartbeat,
                             cpu_attribution=collector.summary(), utc=utc_now())
                _persist_or_abort(persistence_errors, 'STATE_MONITORING',
                                  lambda: atomic_json(STATE, state), state)
                print('PROGRESS ' + json.dumps({'utc': state['utc'], 'heartbeat': heartbeat}, sort_keys=True),
                      flush=True)
                last_pin_check = now_mono
            time.sleep(POLL_S)

        collector.maybe_sample(now_mono=time.monotonic(), now_epoch=time.time())
        _close_owned_if_stopped(owned)
        verify_pins(context)
        _assert_native_outer_guard_contract()
        result, census = _post_stop_census(support, timeout=budget['cleanup_s'])
        state['cleanup_census'] = census
        guard = _read_json(ROOT / 'host-guard.json', 'DIAGNOSTIC_GUARD_UNAVAILABLE')
        verdict = evaluate_diagnostic_final(result=result, guard=guard, exitcode=child.returncode,
                                            config=context.config, census=census, collector=collector,
                                            context=context)
        verify_pins(context)
        _persist_or_abort(persistence_errors, 'INPUT_SIDECAR_AFTER_SUCCESS',
                          lambda: write_input_sidecar(context, 'AFTER_DIAGNOSTIC_SUCCESS', overwrite=True), state)
        verdict['utc'] = utc_now()
        verdict['policy_sha256'] = context.policy_sha256
        _persist_or_abort(persistence_errors, 'FINAL_RECEIPT',
                          lambda: atomic_json(FINAL_RECEIPT, verdict, overwrite=False), state)
        state.update(status='DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE', diagnostic_verdict=verdict,
                     cleanup_census=census, cpu_attribution=collector.summary(), utc=utc_now(),
                     m1_complete=False)
        _persist_or_abort(persistence_errors, 'STATE_SUCCESS', lambda: atomic_json(STATE, state), state)
        normal_complete = True
        print('DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE; M1 REMAINS INCOMPLETE', flush=True)
    except BaseException as exc:
        # No receipt write occurs until after the fresh-reader signal decision,
        # bounded direct-child wait, and independent census have all run.
        cleanup_in_progress = True
        census: dict[str, Any] | None = None
        stop_error: BaseException | None = None
        cleanup_decision = 'NO_CHILD'
        cleanup_detail = 'NO_CHILD'

        if child is not None:
            if child.poll() is None:
                if owned is None:
                    cleanup_decision = 'UNBOUND_DIRECT_CHILD'
                    cleanup_detail = 'PIDFD_BIND_FAILED_NO_SIGNAL'
                    stop_error = CleanupHold('DIRECT_CHILD_PIDFD_OWNERSHIP_BIND_FAILED_NO_SIGNAL')
                else:
                    # This is deliberately reread immediately before the only
                    # possible SIGINT; it never relies on a 15-second heartbeat
                    # cache.  Ambiguity is a no-signal HOLD, not optimism.
                    cleanup_decision, cleanup_detail = _classify_current_signal_state(
                        read_live_receipt, context, collector)
                    if cleanup_decision == 'OWNED_MEASURING':
                        try:
                            # The sole signal path is identity-bound pidfd SIGINT
                            # to the directly spawned Outer child.
                            support.request_orderly_abort(owned, timeout=budget['abort_wait_s'])
                        except BaseException as abort_exc:
                            stop_error = abort_exc
                    elif cleanup_decision == 'AMBIGUOUS':
                        stop_error = CleanupHold('LIVE_RECEIPT_AMBIGUOUS_NO_SIGNAL: ' + cleanup_detail)
                    # NATIVE_FAILURE_CLEANUP intentionally sends no second signal.

                # Request-orderly-abort has its own bounded wait.  If it timed
                # out, or if no signal was allowed, keep both controller locks
                # through the independent cleanup budget before any census.
                if child.poll() is None:
                    try:
                        _wait_without_signal(child, timeout=budget['cleanup_s'])
                    except BaseException as wait_exc:
                        if stop_error is None:
                            stop_error = wait_exc

            _close_owned_if_stopped(owned)
            if child.poll() is not None:
                _result, census, census_error = _best_effort_post_stop_census(
                    support, timeout=budget['cleanup_s'])
                if census_error is not None and stop_error is None:
                    stop_error = census_error
            else:
                try:
                    census = dict(support.census_native_residue(ROOT, {}))
                except BaseException as census_exc:
                    census = {'clean': False, 'errors': ['CENSUS_EXCEPTION'], 'detail': str(census_exc)}
                    if stop_error is None:
                        stop_error = census_exc
                errors = list(census.get('errors', []))
                errors.append('DIRECT_OUTER_STILL_LIVE')
                census.update(clean=False, errors=sorted(set(errors)), direct_outer_still_live=True)
                if stop_error is None:
                    stop_error = CleanupHold('DIRECT_OUTER_STILL_LIVE_AFTER_BOUNDED_WAIT')

        state.update(cleanup_census=census, cleanup_decision=cleanup_decision,
                     cleanup_detail=cleanup_detail,
                     cpu_attribution=None if collector is None else collector.summary(),
                     persistence_errors=list(persistence_errors))
        if stop_error is not None or census is None or not census.get('clean'):
            _persist_hold(state, stop_error or exc, census, collector, persistence_errors)
        else:
            # A native FAIL that completed cleanly still reports BLOCKED because
            # this controller did not produce a diagnostic PASS.
            state.update(status='BLOCKED', error=str(exc) or type(exc).__name__, utc=utc_now(),
                         m1_complete=False)
            robust_best_effort_persist(persistence_errors, 'STATE_BLOCKED',
                                       lambda: atomic_json(STATE, state), state=state)
        raise
    finally:
        try:
            if evidence is not None:
                evidence.close()
        except BaseException as close_exc:
            _persistence_failure(persistence_errors, 'CPU_EVIDENCE_CLOSE', close_exc, state)
        for signum, previous in prior_handlers.items():
            try:
                signal.signal(signum, previous)
            except BaseException as handler_exc:
                _persistence_failure(persistence_errors, 'RESTORE_SIGNAL_HANDLER', handler_exc, state)
        # No terminate(), kill(), bare PID signal, retry, or matrix write exists
        # in this supervisor.  Retained roots are deliberate diagnostic evidence.
        _ = normal_complete

def main() -> None:
    if os.geteuid() != 0 or os.uname().nodename != 'ubuntu-4gb-nbg1-2':
        raise RuntimeError('authorized host/root required')
    _fresh_start_guard()
    with _open_private_lock(CONTROLLER_LOCK) as controller_lock:
        # The base runner serializes itself with this pre-existing file.  Keep
        # the same flock from before Popen through this controller's own wait
        # and post-stop census; this controller never writes any matrix file.
        try:
            with _open_existing_matrix_lock(MATRIX_LOCK) as matrix_lock:
                run_probe_locked(controller_lock, matrix_lock)
        except (PinError, RuntimeError, SafetyAbort, CleanupHold) as exc:
            # A pre-spawn policy/source/config drift has no native root to hold,
            # but its durable private BLOCKED receipt still prevents auto-retry.
            _record_pre_spawn_block(exc)
            raise


if __name__ == '__main__':
    main()
