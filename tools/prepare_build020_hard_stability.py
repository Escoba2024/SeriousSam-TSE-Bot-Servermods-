"""Prepare a disabled private adapter from pinned existing local evidence only."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import shutil

PARENT = Path('/srv/tse-milestone-a-evidence-20261111/stability013-root-frozen-20261112')
DEST = Path('/srv/tse-stability-build020-hard-controller-20261114')
BUILD = Path('/srv/tse-milestone-a-build-020-20261114')
OLD_DLL = '3a8d84c9c04e4839ee08d5d8ec879c37f25265df267c03e966ec869754a81f93'
NEW_DLL = '094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0'
SOURCE = 'e5f7a65502fbea683014ef8fcc95ecdd2a927b6a'
PARENT_MANIFEST = '3c781143906c1adf94bdd9aa8774da3984111ef5548423fa84d81ae356c19fad'
BUILD_MANIFEST = '3099a0be953be1ff8047289de056b6cddf931cac9a4791f2520d3898357950c6'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('expected exactly one inherited anchor: '+old)
    return text.replace(old, new, 1)


def main():
    assert sha(PARENT/'source-manifest.json') == PARENT_MANIFEST
    manifest = json.loads((PARENT/'source-manifest.json').read_text())
    for path, expected in manifest['runtime_dependencies'].items():
        assert sha(path) == expected, path
    assert sha(BUILD/'manifest.json') == BUILD_MANIFEST
    build = json.loads((BUILD/'manifest.json').read_text())
    assert build['build_ok'] is True and build['qualified'] is False
    assert build['repo_commit'] == SOURCE and build['dll_sha256'] == NEW_DLL
    assert sha(BUILD/'Sources/Game/GameMP.dll') == NEW_DLL
    for group, base in [('source_sha256', BUILD/'Sources/Game'), ('overlay_sha256', BUILD/'overlay')]:
        for path, expected in build[group].items():
            assert sha(base/path) == expected, path
    shutil.copytree(PARENT, DEST, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    replacements = [
        (OLD_DLL, NEW_DLL),
        ('/srv/tse-milestone-a-build-013-20261111', str(BUILD)),
        ('ssam-stability013-{bots}bot-red-20261112', 'ssam-stability020-hard-{bots}bot-red-20261114'),
        ("E=BASE/f'stability013-", "E=BASE/f'stability020-hard-"),
        ('PRIVATE STABILITY 013', 'PRIVATE STABILITY 020 HARD'),
        ('candidate013 normal gameplay', 'candidate020 Hard normal gameplay'),
    ]
    for name in ('run-a4.py', 'adapter_policy.py'):
        text = (PARENT/name).read_text()
        for old, new in replacements:
            text = text.replace(old, new)
        if name == 'run-a4.py':
            text = replace_once(text, 'RUNTIME_REVIEWED=True', 'RUNTIME_REVIEWED=False')
            text = replace_once(text, 'gam_iStartDifficulty=3;', 'gam_iStartDifficulty=2;')
            text = replace_once(text, 'import stability_policy as stability',
                                'import stability_policy as stability\nimport stability_hard_rules as hard_rules')
            text = replace_once(text, "barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}",
                                "barrier={role:probe.read(rec['identity'][0],R/role) for role,rec in records.items()}\n   for snapshot in barrier.values():hard_rules.validate_session(snapshot)")
            text = replace_once(text, "snapshots={role:probe.read(rec['identity'][0],R/role)for role,rec in records.items()}",
                                "snapshots={role:probe.read(rec['identity'][0],R/role)for role,rec in records.items()}\n     for snapshot in snapshots.values():hard_rules.validate_session(snapshot)")
        ast.parse(text)
        (DEST/name).write_text(text)
    monitor = (PARENT/'stability_monitor.py').read_text()
    monitor = replace_once(monitor, 'import stability_policy as policy',
                           'import stability_policy as policy\nimport stability_hard_rules as hard_rules')
    monitor = replace_once(monitor, 'scores=policy.query_population(q,self.bots,self.vanilla_name)',
                           'scores=policy.query_population(q,self.bots,self.vanilla_name)\n  hard_rules.validate_query(q)')
    ast.parse(monitor)
    (DEST/'stability_monitor.py').write_text(monitor)
    fixture = (PARENT/'test_stability_monitor.py').read_text()
    fixture = replace_once(fixture, "'activemod':''}", "'activemod':'','difficulty':'Hard'}")
    (DEST/'test_stability_monitor.py').write_text(fixture)
    for name in ('stability_hard_rules.py', 'test_stability_hard_rules.py'):
        shutil.copy2(Path(__file__).resolve().parent/name, DEST/name)
    deps = {}
    for old, expected in manifest['runtime_dependencies'].items():
        path = Path(old)
        if path.is_relative_to(PARENT):
            path = DEST/path.relative_to(PARENT)
            expected = sha(path)
        elif path.is_relative_to('/srv/tse-milestone-a-build-013-20261111'):
            path = BUILD/path.relative_to('/srv/tse-milestone-a-build-013-20261111')
            expected = sha(path)
        deps[str(path)] = expected
    deps[str(DEST/'stability_hard_rules.py')] = sha(DEST/'stability_hard_rules.py')
    manifest.update(scope='DISABLED_BUILD020_HARD_RED_FORMAL_STABILITY_PREPARATION',
                    runtime_reviewed=False, runtime_performed=False, qualified=False,
                    functional_pass=False)
    manifest['candidate'] = dict(dll_sha256=NEW_DLL, source_commit=SOURCE,
                                 build_manifest=str(BUILD/'manifest.json'),
                                 build_manifest_sha256=BUILD_MANIFEST)
    manifest['runtime_dependencies'] = dict(sorted(deps.items()))
    manifest.pop('root_changes', None)
    manifest.pop('draft_source_sha256', None)
    manifest['derivation'] = dict(parent=str(PARENT), parent_manifest_sha256=PARENT_MANIFEST,
                                  changes='candidate/namespace/gate pins; Hard2 template and native/query checks only',
                                  native_started=False, independent_review='PENDING')
    manifest['prepared_source_sha256'] = {p.name:sha(p) for p in sorted(DEST.glob('*.py'))}
    for path, expected in deps.items():
        assert sha(path) == expected, path
    (DEST/'source-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    diff = ''.join(''.join(difflib.unified_diff((PARENT/n).read_text().splitlines(True),
                   (DEST/n).read_text().splitlines(True), fromfile=str(PARENT/n), tofile=str(DEST/n)))
                   for n in ('run-a4.py', 'adapter_policy.py', 'stability_monitor.py'))
    (DEST/'build020-hard-controller.diff').write_text(diff)
    (DEST/'README-020.md').write_text('DISABLED; no native run. Earlier013 README/reports are historical parent evidence only.\n'
        'Build020/Hard2 adapter requires independent review, root freeze and fresh exclusive preflight.\n'
        'Formal 1/4/8 durations3600/3600/7200 and all existing gates unchanged. Red-only scope.\n')
    print(json.dumps(dict(package=str(DEST), manifest_sha256=sha(DEST/'source-manifest.json'),
                         dependencies=len(deps), native_started=False)))


if __name__ == '__main__':
    main()
