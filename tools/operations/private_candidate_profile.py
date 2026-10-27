"""Opt-in, private M1 profile. Loading verifies receipts; it starts nothing.

No deployment or M1-completion authority is conferred by this module. The legacy
operations profile is unchanged. A caller must retain outer host/exclusivity
monitoring during every native supervisor qualification.
"""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import sys

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
CANDIDATE = '7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf'
EVIDENCE = Path('/root/ssam-ai-backups/m1-prefilter-matrix-20261026-idle-r3')
QUALIFIER = Path('/srv/tse-m1-diagnostic-fix-20261026')
BUILD = Path('/srv/tse-cecil-p1-build-20261025-01/manifest.json')
CONFIG = Path('/root/ssam-ai-backups/m1-completion-20261026-0155/8-duration-config.json')
MARKER = Path('/root/ssam-ai-backups/shutdown-20261026-0033/public-disabled.json')
TEMPLATE = Path('/srv/tse-wine-runtime-20261020/public-eight-20261020-2140')
VANILLA = Path('/srv/tse-wine-runtime-20261020/install/vanilla')
BASE = Path('/srv/tse-ops-m1-20261027')
OPERATIONS_SOURCES = ('tools/operations/private_candidate_profile.py',
    'tools/operations/fleet_supervisor.py','tools/operations/fleet_health.py',
    'tools/qualify_integrated_wine.py','tools/bot_telemetry.py',
    'tools/m1_duration_acceptance.py','tools/native_receipt_io.py',
    'tools/m1_prefilter_recovery_profile.py','tools/run_prefilter_duration_matrix.py')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_object(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(16 * 1024**2 + 1)
    if len(raw) > 16 * 1024**2:
        raise ValueError('bounded profile metadata required')
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError('JSON object required')
    return obj


def validate_location(root, port, display):
    root = Path(root)
    if (not root.is_absolute() or root.parent != BASE or root != root.resolve() or
            not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', root.name) or
            type(port) is not int or not 26800 <= port <= 26998 or port % 2 or
            not isinstance(display, str) or not re.fullmatch(r':12[0-9]', display)):
        raise ValueError('exact private supervisor location required')
    return root


@dataclass(frozen=True)
class Role:
    name: str
    kind: str
    nickname: str
    local_players: int


def role_contract(identities):
    if (not isinstance(identities, dict) or len(identities) != 8 or
            set(identities) != {f'gamer-{i:03}' for i in range(8)} or
            any(not isinstance(n, str) or not re.fullmatch(r'[A-Za-z0-9 ._\[\]-]{1,22}', n)
                or n != n.strip() for n in identities.values()) or
            any(not any(c.isalnum() for c in n) for n in identities.values()) or
            len({n.casefold() for n in identities.values()} | {'retail_control'}) != 9):
        raise ValueError('exact eight unique single-local-player identities required')
    return (Role('server', 'server', '', 0), Role('vanilla', 'observer', 'Retail_Control', 1),
            *(Role(k, 'bot', identities[k], 1) for k in sorted(identities)))


def matrix_stages(matrix):
    from m1_prefilter_recovery_profile import validated_stages
    return validated_stages(matrix, CANDIDATE)


def validate_policy_inventory(policy):
    from run_prefilter_duration_matrix import expected_source_paths, validate_stage_contract, PRODUCER_NAMES
    validate_stage_contract(policy)
    expected_sources={str(QUALIFIER/Path(x).relative_to(TOOLS.parent)) for x in expected_source_paths()}
    expected_artifacts={str(BUILD),str(BUILD.parent/'Sources/Game/GameMP.dll'),str(MARKER),
        *(str(CONFIG.parent/name) for name in ('one-hour-config.json','4-duration-config.json','8-duration-config.json'))}
    sources=policy.get('source_sha256',{})
    artifacts=policy.get('artifact_sha256',{})
    if (policy.get('candidate_sha256')!=CANDIDATE or not isinstance(sources,dict) or
            set(sources)!=expected_sources or not isinstance(artifacts,dict) or
            set(artifacts)!=expected_artifacts):
        raise ValueError('exact qualified producer/source/artifact inventory required')
    if any(not re.fullmatch('[0-9a-f]{64}',str(v)) for v in [*sources.values(),*artifacts.values()]):
        raise ValueError('full SHA256 pins required')
    expected_harness={name:sources[str(QUALIFIER/'performance/native/tools'/name)] for name in PRODUCER_NAMES}
    if policy.get('harness_sha256')!=expected_harness:
        raise ValueError('native producer inventory mismatch')


def validate_native_profile_result(result):
    if (result.get('scope')!='ISOLATED_NETNS_RETAIL_WINE' or
            result.get('dll_sha256')!=CANDIDATE or result.get('max_bots')!=8 or
            result.get('cecil_p1') is not True or result.get('original_client') is not True or
            result.get('accelerated') is not False or result.get('low_memory_rendering') is not True or
            result.get('observer_fps_cap')!=5 or result.get('preset')!='redstation' or
            result.get('colors_enabled') is not False):
        raise ValueError('exact P1 single-local-player Red Station/observer/render profile required')
    peak=result.get('cgroup_peak_mib')
    if type(peak) not in (int,float) or not 0<peak<3072:
        raise ValueError('measured startup memory budget absent')
    return int((peak+64)*1024**2)


def isolated_namespace():
    try:
        return (os.readlink('/proc/self/ns/net') != os.readlink('/proc/1/ns/net') and
                {name for _, name in socket.if_nameindex()} == {'lo'})
    except OSError:
        return False


@dataclass(frozen=True)
class PrivateProfile:
    root: Path
    port: int
    display: str
    roles: tuple
    profile_path: Path
    profile_sha256: str
    matrix_sha256: str
    policy_sha256: str
    marker_sha256: str
    reference_root: Path
    # (role, relative path, expected hash): qualified settings, never live logs.
    prepared_pins: tuple
    evidence_pins: tuple
    startup_budget_bytes: int
    candidate_sha256: str = CANDIDATE

    @property
    def role_names(self):
        return tuple(r.name for r in self.roles)

    @property
    def expected_names(self):
        return tuple(r.nickname for r in self.roles if r.nickname)

    def role(self, name):
        return next(r for r in self.roles if r.name == name)

    def is_bot(self, name):
        return self.role(name).kind == 'bot'

    def local_players(self, name):
        return self.role(name).local_players

    def source(self, role):
        prefix = role.startswith('prefix-')
        name = role.removeprefix('prefix-')
        item = self.role(name)
        if prefix:
            return TEMPLATE / ('prefix-server' if item.kind == 'server' else 'prefix-botA')
        return VANILLA if item.kind == 'observer' else TEMPLATE / ('server' if item.kind == 'server' else 'botA')

    def reference_bytes(self, role, relative):
        if not any(r == role and f == relative for r, f, _ in self.prepared_pins):
            raise ValueError('unregistered qualified setting')
        data = (self.reference_root/'layers'/role/'upper'/relative).read_bytes()
        if role == 'server' and relative == 'Scripts/Dedicated_startup.ini':
            data += (f'\nnet_strLocalHost="127.0.0.1";\nnet_iPort={self.port};\n'
                     'ser_bHeartbeatGameSpy=0;\nser_bEnumeration=1;\n').encode()
        return data

    def verify_pins(self):
        for path, digest in self.evidence_pins:
            if sha(path) != digest:
                raise ValueError('private profile evidence/source drift: ' + path)
        if sha(self.profile_path) != self.profile_sha256:
            raise ValueError('private candidate profile drift')

    def verify_settings(self):
        self.verify_pins()
        for role, relative, digest in self.prepared_pins:
            if sha(self.root/role/relative) != digest:
                raise ValueError('qualified runtime setting drift: ' + role + '/' + relative)

    def require_namespace(self):
        if not isolated_namespace():
            raise ValueError('private loopback-only network namespace required')

    def master_isolation_ok(self):
        # Private policy substitutes no DNS fact: no non-loopback interface and
        # exact prepared server settings with advertising disabled are required.
        self.require_namespace()
        self.verify_settings()
        return True

    def recovery_action(self, role, names, missing_seconds):
        if any(n not in self.expected_names for n in names):
            return 'HOLD_HUMANS'
        owned = self.role(role).nickname
        if not owned or owned not in names:
            return 'RESTART_ROLE'
        # A nickname still present is not proof of a harmless ghost. Never
        # evict an unproven occupant by escalating to a private fleet restart.
        return 'WAIT_GHOSTS'


def load(config):
    """Load only after a real accepted matrix; no synthetic admission fallback."""
    reference = config.get('private_profile')
    if not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}:
        raise ValueError('explicit immutable private profile reference required')
    path = Path(reference['path'])
    if not path.is_absolute() or path!=path.resolve():
        raise ValueError('absolute nonsymlink profile file required')
    if not re.fullmatch('[0-9a-f]{64}', str(reference['sha256'])) or sha(path) != reference['sha256']:
        raise ValueError('caller-pinned private profile required')
    doc = read_object(path)
    if set(doc) != {'schema', 'root', 'port', 'display', 'matrix_sha256', 'policy_sha256', 'operations_source_sha256'} or doc['schema'] != 'M1_PRIVATE_SUPERVISOR_V1':
        raise ValueError('exact private profile schema required')
    root = validate_location(doc['root'], doc['port'], doc['display'])
    if (config.get('root') != str(root) or config.get('port') != doc['port'] or
            config.get('display') != doc['display'] or config.get('bots') != 8):
        raise ValueError('instance/profile mismatch')
    for filename, digest in [('matrix.json', doc['matrix_sha256']), ('policy.json', doc['policy_sha256'])]:
        if not re.fullmatch('[0-9a-f]{64}', str(digest)) or sha(EVIDENCE/filename) != digest:
            raise ValueError('pinned duration evidence drift')
    policy = read_object(EVIDENCE/'policy.json')
    matrix = read_object(EVIDENCE/'matrix.json')
    stages = matrix_stages(matrix)
    if matrix.get('policy_sha256') != doc['policy_sha256']:
        raise ValueError('matrix belongs to another policy')
    validate_policy_inventory(policy)
    if policy.get('candidate_sha256') != CANDIDATE:
        raise ValueError('wrong matrix candidate')
    operations=doc['operations_source_sha256']
    if not isinstance(operations,dict) or set(operations)!=set(OPERATIONS_SOURCES):
        raise ValueError('complete reviewed operations-source inventory required')
    for name,digest in operations.items():
        if not re.fullmatch('[0-9a-f]{64}',str(digest)) or sha(TOOLS.parent/name)!=digest:
            raise ValueError('operations source drift: '+name)
    pins = dict(policy.get('source_sha256', {}))
    pins.update(policy.get('artifact_sha256', {}))
    pins.update({str(TOOLS.parent/name):digest for name,digest in operations.items()})
    if not pins or str(BUILD) not in pins or str(CONFIG) not in pins or str(MARKER) not in pins:
        raise ValueError('missing source/build/config/shutdown pins')
    # Reuse the direct native receipt validator; never trust only a status field.
    from m1_duration_acceptance import evaluate_runtime
    acceptance = TOOLS/'m1_duration_acceptance.py'
    expected_acceptance = policy.get('source_sha256', {}).get(str(QUALIFIER/'tools/m1_duration_acceptance.py'))
    if expected_acceptance is None or sha(acceptance) != expected_acceptance:
        raise ValueError('reviewed acceptance source required')
    for name, digest in pins.items():
        if sha(name) != digest:
            raise ValueError('duration source/artifact drift: ' + name)
    for stage_root, bots, seconds in stages:
        verdict = evaluate_runtime(stage_root, bots=bots, required_s=seconds,
            dll_sha256=CANDIDATE, harness_sha256=policy['harness_sha256'])
        if verdict.get('status') != 'DURATION_RECEIPTS_ACCEPTED':
            raise ValueError('direct native duration receipts not accepted')
    build = read_object(BUILD)
    if build.get('build_ok') is not True or build.get('dll_sha256') != CANDIDATE or sha(build['candidate']) != CANDIDATE:
        raise ValueError('candidate manifest mismatch')
    sources=build.get('source_sha256')
    if not isinstance(sources,dict) or len(sources)!=39 or build.get('source_count')!=15:
        raise ValueError('complete candidate build-source provenance required')
    for name,digest in sources.items():
        source=BUILD.parent/'Sources/Game'/name
        if source.parent!=BUILD.parent/'Sources/Game' or sha(source)!=digest:
            raise ValueError('candidate build-source drift: '+name)
        pins[str(source)]=digest
    session = read_object(CONFIG)
    roles = role_contract({who['id']: who['nickname'] for who in session['identities']})
    reference_root = Path(stages[-1][0])
    prepared = []
    for role in roles:
        upper = reference_root/'layers'/role.name/'upper'
        found = []
        for file in upper.rglob('*'):
            relative = file.relative_to(upper).as_posix()
            if (not file.is_file() or file.is_symlink() or
                    not (relative.startswith(('Scripts/', 'Players/', 'Data/')) or relative == 'Bin/GameMP.dll')):
                continue
            data = file.read_bytes()
            if role.kind == 'server' and relative == 'Scripts/Dedicated_startup.ini':
                data += (f'\nnet_strLocalHost="127.0.0.1";\nnet_iPort={doc["port"]};\n'
                         'ser_bHeartbeatGameSpy=0;\nser_bEnumeration=1;\n').encode()
            prepared.append((role.name, relative, hashlib.sha256(data).hexdigest()))
            found.append(relative)
        if role.kind != 'server' and not {'Scripts/Session.ini','Data/SeriousSam.gms','Players/Player0.plr','Players/Player0.plr.guid'} <= set(found):
            raise ValueError('qualified client settings absent')
        if role.kind == 'bot' and (b'bot_bCecilP1=1;' not in (upper/'Scripts/Session.ini').read_bytes() or 'Bin/GameMP.dll' not in found):
            raise ValueError('qualified P1 candidate settings absent')
        if role.kind == 'server' and not {'Scripts/Dedicated_startup.ini','Scripts/Dedicated/BotTest/1_begin.ini'} <= set(found):
            raise ValueError('qualified Red Station server settings absent')
    startup_budget=validate_native_profile_result(read_object(reference_root/'result.json'))
    pins.update({str(EVIDENCE/'matrix.json'):doc['matrix_sha256'],str(EVIDENCE/'policy.json'):doc['policy_sha256']})
    return PrivateProfile(root,doc['port'],doc['display'],roles,path,reference['sha256'],
        doc['matrix_sha256'],doc['policy_sha256'],pins[str(MARKER)],reference_root,
        tuple(prepared),tuple(sorted(pins.items())),startup_budget)


def prepare(config):
    """Prepare fresh private upper files only; no mount, process or network action.

    Revalidates admission internally. Never overwrites/adopts an existing root.
    The parent must subsequently start the existing supervisor in a fresh private
    network namespace, under its host reserve/exclusivity monitor.
    """
    profile = load(config)
    profile.verify_pins()
    if BASE.exists() and (BASE.is_symlink() or BASE.stat().st_uid != 0):
        raise ValueError('private preparation base ownership mismatch')
    BASE.mkdir(mode=0o755, exist_ok=True)
    profile.root.mkdir(mode=0o755)  # exclusive freshness; no exist_ok
    for path in [profile.root/'home', profile.root/'home/cache', profile.root/'archives']:
        path.mkdir(mode=0o755)
        if path.name != 'archives':os.chown(path,65534,65534)
    for role in profile.role_names:
        for name in (role, 'prefix-'+role):
            (profile.root/name).mkdir(mode=0o755)
            layer=profile.root/'layers'/name
            layer.mkdir(parents=True,mode=0o755)
            (layer/'upper').mkdir(mode=0o755);os.chown(layer/'upper',65534,65534)
            (layer/'work').mkdir(mode=0o700)
    for role,relative,digest in profile.prepared_pins:
        data=profile.reference_bytes(role,relative)
        if hashlib.sha256(data).hexdigest()!=digest:
            raise ValueError('qualified preparation reference drift')
        path=profile.root/'layers'/role/'upper'/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(data)
        path.chmod(0o644);os.chown(path,65534,65534)
    for role in profile.role_names:
        for path in (profile.root/'layers'/role/'upper').rglob('*'):
            if path.is_dir():os.chown(path,65534,65534)
    state=dict(status='PRIVATE_PREPARED_NOT_QUALIFIED',processes={},mounts=[],
        template=str(TEMPLATE),bots=8,game_port=profile.port,query_port=profile.port+1,
        display=profile.display,dll_sha256=CANDIDATE,private_profile_sha256=profile.profile_sha256,
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        scope='PRIVATE_SUPERVISOR_QUALIFICATION_NOT_RELEASE',m1_complete=False)
    for name,value in [('result.json',state),('instance.json',config)]:
        path=profile.root/name
        with path.open('x') as stream:json.dump(value,stream,indent=2)
        path.chmod(0o600)
    return profile.root/'instance.json'
