"""Independent private 1,500-second diagnostic evidence; never an M1 evaluator.

No game/process/signal operation, no matrix I/O, no raw-log retention. Caller must
pin this source, verify all producer sources, stop the owned outer, and prove a
clean independent census before calling this pure read-only final validation.
"""
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import stat

MEASURE_S = 1500
FULL_S = 1200
BOTS = 8
SCOPE = 'ISOLATED_NETNS_RETAIL_WINE'
MARKERS = ('SYNCBAD', 'Too many bad syncs', 'CRC check failed')
SOURCE_NAMES = ('qualify_bot_sessions.py', 'bot_session_executor.py', 'bot_session_runtime.py',
                'bot_sessions.py', 'qualify_integrated_wine.py')


def require(ok, reason):
    if not ok:
        raise RuntimeError('DIAGNOSTIC_' + reason)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def read_object(path):
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise RuntimeError('DIAGNOSTIC_JSON_UNREADABLE') from exc
    require(isinstance(value, dict), 'JSON_OBJECT_REQUIRED')
    return value


def identities(config):
    entries = config.get('identities')
    require(isinstance(entries, list) and len(entries) == BOTS, 'CONFIG_IDENTITIES_INVALID')
    ids = [entry.get('id') if isinstance(entry, dict) else None for entry in entries]
    require(all(isinstance(i, str) and re.fullmatch(r'[A-Za-z0-9_-]+', i) for i in ids)
            and len(set(ids)) == BOTS and not set(ids) & {'server', 'vanilla'}, 'CONFIG_IDS_INVALID')
    return set(ids)


def result_schema(result, *, candidate_sha256, bound_cgroup):
    require(result.get('status') == 'PASS_LIMITED_SESSION_LIFECYCLE' and
            result.get('scope') == SCOPE, 'RESULT_STATUS_OR_SCOPE_INVALID')
    require(isinstance(candidate_sha256, str) and re.fullmatch(r'[0-9a-f]{64}', candidate_sha256)
            and result.get('dll_sha256') == candidate_sha256, 'CANDIDATE_MISMATCH')
    require(type(result.get('max_bots')) is int and result['max_bots'] == BOTS and
            type(result.get('peak_playing')) is int and result['peak_playing'] == BOTS and
            result.get('original_client') is True, 'POPULATION_OR_ORIGINAL_MISSING')
    require(type(result.get('measured_s')) is int and result['measured_s'] == MEASURE_S and
            number(result.get('elapsed_s')) and result['elapsed_s'] >= MEASURE_S,
            'MEASUREMENT_SCHEMA_INVALID')
    require(result.get('all_bots_drained') is True and
            type(result.get('new_throttled_periods')) is int and result['new_throttled_periods'] == 0,
            'DRAIN_OR_THROTTLE_INVALID')
    require(isinstance(bound_cgroup, str) and result.get('cgroup') == bound_cgroup,
            'CGROUP_BINDING_MISMATCH')


def guard_schema(guard, result):
    require(guard.get('status') == 'FINISHED' and type(guard.get('child_exitcode')) is int and
            guard['child_exitcode'] == 0 and 'error' in guard and guard['error'] is None,
            'GUARD_NOT_FINISHED')
    require(guard.get('public_guard_mode') == 'USER_DISABLED' and guard.get('public_disabled') is True,
            'PUBLIC_GUARD_MODE_INVALID')
    rows = guard.get('samples')
    require(isinstance(rows, list) and len(rows) >= 2, 'GUARD_SAMPLES_MISSING')
    times = []
    overload = 0
    for row in rows:
        require(isinstance(row, dict) and number(row.get('at')), 'GUARD_SAMPLE_TIME_INVALID')
        require(number(row.get('available_mib')) and row['available_mib'] >= 768 and
                number(row.get('disk_free_gib')) and row['disk_free_gib'] >= 8,
                'GUARD_RESERVE_NOT_PROVEN')
        require(number(row.get('host_busy_percent')) and 0 <= row['host_busy_percent'] <= 100,
                'GUARD_CPU_INVALID')
        overload = overload + 1 if row['host_busy_percent'] >= 85 else 0
        require(overload < 3, 'GUARD_OVERLOAD_NOT_CLEAN')
        times.append(row['at'])
    require(all(0 < b - a <= 15 for a, b in zip(times, times[1:])), 'GUARD_SAMPLE_GAP')
    try:
        end = datetime.fromisoformat(result['utc'].replace('Z', '+00:00'))
        require(end.tzinfo is not None, 'GUARD_TIME_COVERAGE_TIMESTAMP_UNZONED')
        epoch = end.timestamp()
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise RuntimeError('DIAGNOSTIC_GUARD_TIME_COVERAGE_TIMESTAMP_INVALID') from exc
    require(times[-1] - times[0] >= MEASURE_S and
            times[0] <= epoch - result['elapsed_s'] + 5 and
            epoch - 5 <= times[-1] <= epoch + 15, 'GUARD_TIME_COVERAGE_MISSING')
    return {'samples': len(rows), 'min_available_mib': min(r['available_mib'] for r in rows),
            'min_disk_free_gib': min(r['disk_free_gib'] for r in rows),
            'max_host_busy_percent': max(r['host_busy_percent'] for r in rows)}


def continuous_population(path, *, bot_ids, final_elapsed_s):
    roles = bot_ids | {'server', 'vanilla'}
    longest = 0.0
    start = previous = None
    generations = None
    count = 0
    try:
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                require(isinstance(row, dict), 'SAMPLE_OBJECT_REQUIRED')
                now = row.get('elapsed_s')
                require(number(now) and 0 <= now <= final_elapsed_s and
                        (previous is None or now > previous), 'NONMONOTONIC_SAMPLES')
                processes = row.get('processes')
                decisions = row.get('decisions')
                valid = (type(row.get('active')) is int and row['active'] == BOTS and
                         type(row.get('population')) is int and row['population'] == BOTS + 1 and
                         isinstance(processes, dict) and set(processes) == roles and
                         all(isinstance(v, dict) and type(v.get('start_ticks')) is int and
                             v['start_ticks'] > 0 and number(v.get('pss_mib')) and v['pss_mib'] > 0
                             for v in processes.values()) and
                         isinstance(decisions, list) and len(decisions) == BOTS and
                         all(isinstance(d, dict) for d in decisions) and
                         {d.get('id') for d in decisions} == bot_ids and
                         all(d.get('action') == 'healthy' for d in decisions))
                current = tuple(sorted((role, data['start_ticks']) for role, data in processes.items())) if valid else None
                if not valid:
                    start = generations = None
                elif start is None or current != generations or (previous is not None and now - previous > 3):
                    start, generations = now, current
                else:
                    longest = max(longest, now - start)
                previous = now
                count += 1
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise RuntimeError('DIAGNOSTIC_SAMPLES_UNREADABLE_OR_INVALID') from exc
    require(count > 0 and longest >= FULL_S, 'GENERATION_TRUE_FULL_POPULATION_BELOW_1200S')
    return {'longest_contiguous_full_population_s': round(longest, 3), 'sample_rows': count,
            'requires_population_nine_and_exact_roles_and_healthy_decisions': True}


def telemetry_summary(result, bot_ids):
    telemetry = result.get('telemetry')
    require(isinstance(telemetry, dict) and set(telemetry) == bot_ids, 'TELEMETRY_ROLE_SET_INVALID')
    for role, windows in telemetry.items():
        require(isinstance(windows, list) and bool(windows), 'TELEMETRY_WINDOWS_MISSING')
        total = 0.0
        for window in windows:
            require(isinstance(window, dict) and number(window.get('playing_s')) and
                    window['playing_s'] >= 0, 'TELEMETRY_WINDOW_INVALID')
            total += window['playing_s']
            reports = window.get('reports')
            require(isinstance(reports, list) and bool(reports), 'TELEMETRY_REPORTS_MISSING')
            for report in reports:
                require(isinstance(report, dict) and report.get('verdict') == 'ACTIVE_OK' and
                        report.get('exit_code') == 0 and report.get('lp_median') == 1 and
                        number(report.get('tick_hz_median')) and 18 <= report['tick_hz_median'] <= 22 and
                        number(report.get('render_skip_total')) and report['render_skip_total'] > 0 and
                        report.get('render_draw_total') == 0 and isinstance(report.get('config'), dict) and
                        report['config'].get('nullrender') == '1', 'TELEMETRY_NOT_ALL_ACTIVE_OK_20HZ')
        require(total >= FULL_S, 'TELEMETRY_PLAYING_DURATION_INSUFFICIENT')
    return {'count': len(bot_ids), 'active_ok_20hz_identities': sorted(bot_ids),
            'every_report_valid': True}


def cleanup_summary(root, result, roles):
    rows, unmounts = result.get('cleanup'), result.get('unmounts')
    require(isinstance(rows, list) and len(rows) == len(roles) and
            all(isinstance(r, dict) for r in rows) and {r.get('role') for r in rows} == roles and
            all(r.get('errors') == [] for r in rows), 'CLEANUP_ROLES_OR_ERRORS_INVALID')
    mounts = {str(root / (prefix + role)) for role in roles for prefix in ('', 'prefix-')}
    require(isinstance(unmounts, list) and len(unmounts) == len(mounts) and
            all(isinstance(r, dict) for r in unmounts) and {r.get('path') for r in unmounts} == mounts and
            all(type(r.get('exitcode')) is int and r['exitcode'] == 0 for r in unmounts),
            'UNMOUNT_PROOF_INVALID')
    return {'cleanup_roles': sorted(roles), 'unmount_count': len(mounts), 'all_bots_drained': True}


def scan_complete_logs(root, roles, *, max_log_bytes):
    require(type(max_log_bytes) is int and max_log_bytes > 0, 'LOG_BOUND_INVALID')
    records = []
    for role in sorted(roles):
        path = root / 'layers' / role / 'upper' / ('Dedicated_BotTest.log' if role == 'server' else 'SeriousSam.log')
        try:
            before = path.lstat()
            require(stat.S_ISREG(before.st_mode) and 0 < before.st_size <= max_log_bytes, 'COMPLETE_LOG_INVALID')
            with path.open('rb') as stream:
                data = stream.read(max_log_bytes + 1)
            after = path.lstat()
        except OSError as exc:
            raise RuntimeError('DIAGNOSTIC_COMPLETE_LOG_UNREADABLE') from exc
        require((before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and
                len(data) == before.st_size, 'COMPLETE_LOG_DRIFT')
        counts = {marker: data.count(marker.encode('ascii')) for marker in MARKERS}
        require(sum(counts.values()) == 0, 'INDEPENDENT_SYNC_SCAN_NOT_CLEAN')
        records.append({'role': role, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'marker_counts': counts})
    return {'complete_log_count': len(records), 'logs': records, 'independent_sync_scan_complete': True,
            'sync_marker_total': 0, 'raw_log_retained': False}


def validate_probe_evidence(*, root, result, guard, config, census, candidate_sha256, bound_cgroup,
                            harness_sha256):
    root = Path(root)
    require(census.get('clean') is True, 'INDEPENDENT_CENSUS_NOT_CLEAN')
    require(isinstance(harness_sha256, dict) and set(harness_sha256) == set(SOURCE_NAMES) and
            all(isinstance(d, str) and re.fullmatch(r'[0-9a-f]{64}', d) for d in harness_sha256.values()),
            'PRODUCER_SOURCE_INVENTORY_INVALID')
    require(read_object(root / 'source-sha256.json') == harness_sha256 and bool(harness_sha256),
            'PRODUCER_SOURCE_RECEIPT_MISMATCH')
    bot_ids = identities(config)
    roles = bot_ids | {'server', 'vanilla'}
    result_schema(result, candidate_sha256=candidate_sha256, bound_cgroup=bound_cgroup)
    guard_summary = guard_schema(guard, result)
    population = continuous_population(root / 'samples.jsonl', bot_ids=bot_ids,
                                       final_elapsed_s=result['elapsed_s'])
    telemetry = telemetry_summary(result, bot_ids)
    cleanup = cleanup_summary(root, result, roles)
    # The pinned native producer defaults this optional field before use.
    max_mib = config.get('max_log_mib', 32)
    require(type(max_mib) is int and 1 <= max_mib <= 128, 'MAX_LOG_CONFIG_INVALID')
    logs = scan_complete_logs(root, roles, max_log_bytes=max_mib * 1024 ** 2)
    raw = []
    for role in sorted(bot_ids):
        path = root / 'layers' / role / 'upper/Bin/BotTelemetry.csv'
        try:
            info = path.lstat()
        except OSError as exc:
            raise RuntimeError('DIAGNOSTIC_RAW_TELEMETRY_MISSING') from exc
        require(stat.S_ISREG(info.st_mode) and info.st_size > 0, 'RAW_TELEMETRY_INVALID')
        raw.append({'role': role, 'bytes': info.st_size})
    logs.update(raw_telemetry_count=len(raw), raw_telemetry=raw)
    return {'status': 'DIAGNOSTIC_PASS_NOT_M1_ACCEPTANCE', 'm1_complete': False,
            'diagnostic_only': True, 'native_status': result['status'], 'guard_status': guard['status'],
            'log_inventory': logs, 'telemetry': telemetry, 'full_population': population,
            'cleanup': cleanup, 'guard_resources': guard_summary,
            'no_m1_matrix_or_acceptance_evaluated': True}
