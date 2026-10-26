#!/usr/bin/env python3
"""Owned, isolated Retail M1 fault qualification after completed duration matrix."""
from pathlib import Path
import argparse, fcntl, hashlib, json, os, signal, subprocess, sys, time, traceback

def main():
    DEFAULT_BASE = Path('/root/ssam-ai-backups/m1-completion-20261026-0155')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', type=Path, default=DEFAULT_BASE)
    parser.add_argument('--execute', action='store_true', help='explicit private fault qualification after duration matrix')
    args = parser.parse_args()
    BASE = args.evidence_root.resolve()
    TOOLS = Path(__file__).resolve().parent
    sys.path.insert(0, str(TOOLS))
    import native_sync_handler_probe as binding
    import m1_recovery_gate as gate
    import m1_duration_acceptance as duration
    from native_receipt_io import read_receipt
    from native_owned_process import OwnedProcess
    if not args.execute:
        try:
            accepted = read_receipt(BASE / 'duration-matrix.json').get('status') == 'DURATION_MATRIX_ACCEPTED'
        except (RuntimeError, ValueError, OSError):
            accepted = False
        print(json.dumps(dict(status='ADMISSION_ONLY_NO_NATIVE_ACTIONS', matrix_marked_accepted=accepted, native_actions=False, m1_complete=False)))
        raise SystemExit(0 if accepted else 3)
    if BASE != DEFAULT_BASE or os.geteuid() != 0 or os.uname().nodename != 'ubuntu-4gb-nbg1-2':
        raise SystemExit('refuse non-private authorized recovery host/evidence root')
    POLICY = read_receipt(BASE / 'duration-policy.json')
    state = dict(status='WAITING_DURATION_MATRIX', m1_complete=False)
    active_child = [None]
    lock = (BASE / 'recovery.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def read(path):
        return read_receipt(path)

    def save():
        state['utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        tmp = BASE / 'recovery-qualification.tmp'
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(BASE / 'recovery-qualification.json')

    def sources_intact():
        manifest = read('/srv/tse-cecil-p1-build-20261025-01/manifest.json')
        if not (manifest.get('build_ok') is True and manifest.get('dll_sha256') == POLICY['candidate_sha256'] == '7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf' and (sha(manifest['candidate']) == POLICY['candidate_sha256'])):
            return False
        return sha(TOOLS / 'native_receipt_io.py') == POLICY['receipt_reader_sha256'] and sha(duration.__file__) == POLICY['acceptance_sha256'] and all((sha(Path('/srv/tse-cecil-guard-20261026/tools') / name) == digest for name, digest in POLICY['harness_sha256'].items()))

    def original_pins():
        sys.path.insert(0, '/srv/tse-cecil-guard-20261026/tools')
        import qualify_integrated_wine as q
        root = Path('/srv/tse-wine-runtime-20261020/install/vanilla/Bin')
        return all((sha(root / name) == digest for name, digest in q.PINS.items() if name != 'DedicatedServer.exe')) and sha(Path('/srv/tse-wine-runtime-20261020/public-eight-20261020-2140/server/Bin/DedicatedServer.exe')) == q.PINS['DedicatedServer.exe']

    def cpu():
        return list(map(int, Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))

    def resources():
        a = cpu()
        time.sleep(2)
        b = cpu()
        d = [y - x for x, y in zip(a, b)]
        busy = 100 * (sum(d) - d[3] - d[4]) / max(1, sum(d))
        mem = int(next((s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))) / 1024
        fs = os.statvfs('/srv')
        return (mem, fs.f_bavail * fs.f_frsize / 1024 ** 3, busy)

    def command(root, config, seconds, port, display, crash=False):
        return gate.native_command(root, config, seconds, port, display, crash=crash)

    def start(root, config, seconds, port, display, crash=False):
        if root.exists() or not sources_intact() or (not original_pins()):
            raise RuntimeError('fresh/source/original admission failed')
        roles = ['server', 'vanilla'] + [i['id'] for i in read(config)['identities']]
        args = command(root, config, seconds, port, display, crash)
        with (BASE / (root.name + '-controller.log')).open('w') as out:
            p = subprocess.Popen(args, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            child_guard = OwnedProcess(p)
        except BaseException:
            if p.poll() is None:
                p.terminate()
            p.wait(timeout=15)
            raise
        active_child[0] = (p, child_guard, root, roles)
        state['active'] = dict(root=str(root), controller_pid=p.pid, start_ticks=child_guard.start_ticks)
        save()
        return p

    def wait_native(root, p, seconds, expect_failure=False):
        deadline = time.monotonic() + seconds + 600
        while p.poll() is None:
            if time.monotonic() > deadline:
                raise RuntimeError('owned fault qualification timeout; inspect own process, do not retry')
            time.sleep(2)
        r = read(root / 'result.json')
        g = read(root / 'host-guard.json')
        if g.get('status') != 'FINISHED' or g.get('error') is not None or (not expect_failure and (p.returncode != 0 or r.get('status') != 'PASS_LIMITED_SESSION_LIFECYCLE')):
            raise RuntimeError('native fault stage failed: ' + str(root))
        item = active_child[0]
        if not item or item[0] is not p or (not cleanup_observed(root, r, item[3])):
            raise RuntimeError('native final cleanup census failed')
        item[1].close()
        active_child[0] = None
        return (r, g)

    def cleanup_observed(root, r, roles):
        cg = Path(r['cgroup'])
        if not cg.is_dir() or (cg / 'cgroup.procs').read_text().strip():
            return False
        expected = {str(root / (prefix + role)) for role in roles for prefix in ('', 'prefix-')}
        mounted = {s.split()[4] for s in Path('/proc/self/mountinfo').read_text().splitlines()}
        if mounted & expected:
            return False
        for p in Path('/proc').glob('[0-9]*'):
            try:
                live = (p / 'stat').read_text().rsplit(') ', 1)[1].split()[0] != 'Z'
                if live and (Path(os.readlink(p / 'cwd')).is_relative_to(root) or str(root).encode() in (p / 'cmdline').read_bytes().split(b'\x00')):
                    return False
            except (OSError, ValueError):
                pass
        return True
    try:
        save()
        deadline = time.monotonic() + 6 * 3600
        while True:
            matrix = read(BASE / 'duration-matrix.json')
            if matrix.get('status') == 'DURATION_MATRIX_ACCEPTED':
                break
            if matrix.get('status') == 'BLOCKED' or time.monotonic() > deadline:
                raise RuntimeError('duration matrix blocked; recovery not started')
            time.sleep(10)
        if not sources_intact():
            raise RuntimeError('source drift')
        for stage_root, bots, seconds in gate.validated_matrix_stages(matrix, POLICY['candidate_sha256']):
            again = duration.evaluate_runtime(stage_root, bots=bots, required_s=seconds, dll_sha256=POLICY['candidate_sha256'], harness_sha256=POLICY['harness_sha256'])
            if again['status'] != 'DURATION_RECEIPTS_ACCEPTED':
                raise RuntimeError('duration receipts changed')
        root = Path('/srv/tse-session-qualification-master-m1-client-fault-20261026')
        cfg = BASE / 'one-hour-config.json'
        state['status'] = 'CLIENT_FAULT_QUALIFICATION'
        save()
        p = start(root, cfg, 1500, 27144, ':156', crash=True)
        r, g = wait_native(root, p, 1500)
        fault = r.get('fault_probe')
        events = r.get('events', [])
        if not fault or not any((e['id'] == fault['id'] and e['epoch'] > fault['epoch'] and (e['event'] == 'joined') for e in events)):
            raise RuntimeError('no native owned client rejoin')
        rows = [json.loads(s) for s in (root / 'samples.jsonl').read_text().splitlines()]
        for role in ('server', 'vanilla'):
            epochs = {s['processes'][role]['start_ticks'] for s in rows if s.get('processes', {}).get(role)}
            if len(epochs) != 1:
                raise RuntimeError('original observer/server generation changed during bot recovery')
        state['client_recovery'] = dict(status='PASS_NATIVE_OWNED_CLIENT_RECOVERY', elapsed_s=r['elapsed_s'], original_observer_preserved=True)
        save()
        root = Path('/srv/tse-session-qualification-master-m1-server-fault-a-20261026')
        cfg = BASE / '8-duration-config.json'
        cfg_sha = sha(cfg)
        state['status'] = 'SERVER_FAULT_QUALIFICATION'
        save()
        p = start(root, cfg, 600, 27148, ':157')
        deadline = time.monotonic() + 300
        record = None
        known = False
        while p.poll() is None and time.monotonic() < deadline:
            if (root / 'result.json').exists():
                rr = read(root / 'result.json')
                if rr.get('status') == 'MEASURING' and rr.get('peak_playing') == 8:
                    qrows = (root / 'combat-queries.jsonl').read_text().splitlines()
                    query = json.loads(qrows[-1])['query']
                    allowed = {i['nickname'] for i in read(cfg)['identities']} | {'Retail_Control'}
                    names = {v for k, v in query.items() if k.startswith('player_')}
                    known = names == allowed and int(query['numplayers']) == 9
                    if not known:
                        raise RuntimeError('unknown/incorrect private roster; do not signal')
                    for proc in Path('/proc').glob('[0-9]*'):
                        try:
                            if (proc / 'comm').read_text().strip() == 'DedicatedServer' and os.readlink(proc / 'cwd') == str(root / 'server'):
                                record = binding.read_process_record(int(proc.name))
                                break
                        except (OSError, ValueError):
                            pass
                    if record:
                        break
            time.sleep(2)
        if not record:
            raise RuntimeError('private eightbot server not ready for owned fault')
        proc, engine_sha, entry = binding.inspect_runtime(root, record['pid'])
        fd = os.pidfd_open(record['pid'])
        try:
            if binding.read_process_record(record['pid']) != record:
                raise RuntimeError('PID changed; no signal')
            fault_at = time.time()
            signal.pidfd_send_signal(fd, signal.SIGTERM)
        finally:
            os.close(fd)
        state['fault_at'] = fault_at
        state['fault_target_epoch'] = record['start_ticks']
        save()
        r, g = wait_native(root, p, 600, expect_failure=True)
        finished = time.time()
        roles = ['server', 'vanilla'] + [i['id'] for i in read(cfg)['identities']]
        paths = [root / 'layers' / role / 'upper' / ('Dedicated_BotTest.log' if role == 'server' else 'SeriousSam.log') for role in roles]
        scan = all((path.is_file() and path.stat().st_size for path in paths))
        import re
        sync_bad = sum((len(re.findall('SYNCBAD|Too many bad syncs|CRC check failed', path.read_text(errors='replace'))) for path in paths if path.is_file()))
        time.sleep(30)
        mem, disk, busy = resources()
        observed = dict(runtime=str(root), scope=r['scope'], candidate_sha256=r['dll_sha256'], expected_candidate_sha256=POLICY['candidate_sha256'], duration_matrix_accepted=True, source_intact=sources_intact(), originals_intact=original_pins(), config_intact=sha(cfg) == cfg_sha, public_disabled=g.get('public_disabled') is True, known_players_only=known, owned_fault=True, server_identity_verified=proc == record, server_absent=not Path('/proc', str(record['pid'])).exists(), cleanup_complete=cleanup_observed(root, r, roles), sync_scan_complete=bool(scan), sync_bad=sync_bad, guard_finished=g['status'] == 'FINISHED', guard_error=g.get('error'), child_exitcode=g['child_exitcode'], failure=r.get('error'), available_mib=mem, disk_free_gib=disk, host_busy_percent=busy, attempts=[], fault_at=fault_at, finished_at=finished, now=time.time())
        decision = gate.decide_recovery(observed)
        state['server_recovery_admission'] = decision
        save()
        if decision['action'] != 'RESTART_ONE_PRIVATE_GENERATION':
            raise RuntimeError('private restart admission HOLD: ' + json.dumps(decision))
        root2 = Path('/srv/tse-session-qualification-master-m1-server-fault-b-20261026')
        p = start(root2, cfg, 420, 27152, ':158')
        r2, g2 = wait_native(root2, p, 420)
        if r2.get('peak_playing') != 8 or not r2.get('all_bots_drained'):
            raise RuntimeError('restarted generation did not restore eight bots')
        state['server_recovery'] = dict(status='PASS_NATIVE_PRIVATE_GENERATION_RECOVERY', restored_bots=8, elapsed_s=r2['elapsed_s'])
        state['status'] = 'FAULT_QUALIFICATION_ACCEPTED'
        state.pop('active', None)
        save()
        print(json.dumps(state))
    except BaseException as exc:
        if isinstance(exc, SystemExit) and exc.code == 0:
            raise
        state['status'] = 'BLOCKED'
        state['error'] = str(exc)
        save()
        traceback.print_exc()
        sys.exit(1)
    finally:
        item = active_child[0]
        if item:
            cleanup_errors = []
            try:
                item[1].stop(timeout=10, kill_timeout=5)
            except BaseException as exc:
                cleanup_errors.append('controller cleanup: ' + str(exc))
            end = time.monotonic() + 180
            clean = False
            while time.monotonic() < end:
                try:
                    clean = cleanup_observed(item[2], read(item[2] / 'result.json'), item[3])
                except (OSError, ValueError, RuntimeError, KeyError):
                    clean = False
                if clean:
                    break
                time.sleep(1)
            state['exception_cleanup_confirmed'] = clean
            if cleanup_errors:
                state['exception_cleanup_errors'] = cleanup_errors
            if not clean:
                state['status'] = 'BLOCKED'
                state['cleanup_hold'] = 'owned native cleanup not verified; no further restart'
            save()
if __name__ == '__main__':
    main()
