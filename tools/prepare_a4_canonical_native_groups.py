"""Offline-only derivation of a disabled, prospective fixed-group controller."""
import argparse
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil

PARENT = Path('/srv/tse-a4-build020-hard-map-startup-final-20261114')
PARENT_SHA = '593e29ac10f68654e01e17f566a4aaa409a4843087d52560624aed2acca18f8f'
CORE_SHA = '201ca2d0f3098637ffb129162d84e126062df24790cfa865693781683732e5fc'
AUDIT_SHA = '3ac187c8775b2bd1ed7021dc7b4037b0eeda6aec2a0292f9d87e47c9d8f4b466'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def once(source, old, new):
    if source.count(old) != 1:
        raise ValueError('nonunique inherited anchor '+old)
    return source.replace(old, new, 1)


def transform(source):
    s = once(source, 'import a4_fire_observer_v2 as native_fire',
             'import a4_fire_observer_v2 as native_fire\nimport a4_canonical_native_groups as canonical_groups')
    s = once(s, "PREFIX=f'ssam-a4-020-hard-{map_key}-20261114'",
             "PREFIX=f'ssam-a4-020-hard-groups-{map_key}-20261114'")
    s = once(s, "E=BASE/f'a4-020-hard-{map_key}-", "E=BASE/f'a4-020-hard-groups-{map_key}-")
    anchor = "   groups=[('botA_actual',tuple(mapping['botA'])),('botB_actual',tuple(mapping['botB'])),('vanilla_plus_overlap',tuple(mapping['vanilla']+mapping['botA'][:3]))]"
    s = once(s, anchor, anchor+"\n   native_group_contract=canonical_groups.declare(mapping,server,log_offsets)\n   (E/'native-group-contract.json').write_text(json.dumps(native_group_contract,indent=2))\n   report['native_group_contract']=native_group_contract")
    s = once(s, "snap=inventory.sample(slots);assert snap['all_selected_present'];inventory_stream.write",
             "snap=inventory.sample(slots);assert snap['all_selected_present'];snap=canonical_groups.bind_sample(snap,group,native_group_contract);inventory_stream.write")
    s = once(s, 'sampled=native_fire.bind_sample(sampled,0,server,log_offsets);',
             'sampled=canonical_groups.bind_sample(sampled,group,native_group_contract);')
    anchor = '      native_registry=hardmap.registry(rotation.registry,list(current_rows.values()),mapping,server)'
    s = once(s, anchor, anchor+"\n      native_registry['native_group_contract']=native_group_contract")
    s = once(s, 'native_fire.apply(report[\'active_evidence\'],logs,mapping,active_snapshots,native_registry,server)',
             "canonical_groups.apply(report['active_evidence'],logs,mapping,active_snapshots,native_registry,server,native_group_contract)")
    s = once(s, "'reset_policy.py'):", "'reset_policy.py','a4_canonical_native_groups.py'):")
    ast.parse(s)
    return s


def prepare(destination):
    dest = Path(destination).resolve()
    if dest.exists():
        raise ValueError('new destination required; inherited packages remain immutable')
    assert sha(PARENT/'source-manifest.json') == PARENT_SHA
    parent = json.loads((PARENT/'source-manifest.json').read_text())
    for path, expected in parent['runtime_dependencies'].items():
        assert sha(path) == expected, ('parent runtime pin', path)
    for name, expected in parent['sources'].items():
        assert sha(PARENT/name) == expected, ('parent source pin', name)
    assert parent['runtime_reviewed'] is False
    assert sha(PARENT/'a4_fire_observer_v2.py') == CORE_SHA
    assert sha(PARENT/'audit_a4_native_fire_observer_v2.py') == AUDIT_SHA
    old = (PARENT/'run-a4.py').read_text()
    assert 'RUNTIME_REVIEWED=False' in old
    transformed = transform(old)
    shutil.copytree(PARENT, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    tools = Path(__file__).resolve().parent
    additions = ('a4_canonical_native_groups.py', 'test_a4_canonical_native_groups.py',
                 'test_prepare_a4_canonical_native_groups.py', 'prepare_a4_canonical_native_groups.py',
                 'check_a4_canonical_archive_design.py')
    for name in additions:
        shutil.copy2(tools/name, dest/name)
    (dest/'run-a4.py').write_text(transformed)
    # Adapt only the inherited test's two authoritative observer assertions.
    # Its startup, host, rate, session and normal-close cases remain identical.
    fixture = (PARENT/'test_a4_hard_maps.py').read_text()
    fixture = once(fixture, "'native_fire.apply('", "'canonical_groups.apply('")
    fixture = once(fixture, "'native_fire.bind_sample(sampled,0,server,log_offsets)'",
                   "'canonical_groups.bind_sample(sampled,group,native_group_contract)'")
    (dest/'test_a4_hard_maps.py').write_text(fixture)
    (dest/'canonical-runtime.diff').write_text(''.join(difflib.unified_diff(
        old.splitlines(True), transformed.splitlines(True),
        fromfile='hard-startup-final/run-a4.py', tofile='canonical-disabled/run-a4.py')))
    deps = {}
    for path, expected in parent['runtime_dependencies'].items():
        p = Path(path)
        if p.is_relative_to(PARENT):
            p = dest/p.relative_to(PARENT)
            expected = sha(p)
        deps[str(p)] = expected
    deps[str(dest/'a4_canonical_native_groups.py')] = sha(dest/'a4_canonical_native_groups.py')
    m = json.loads(json.dumps(parent))
    m['inherited_canonical_parent_metadata'] = dict(scope=m['scope'], derivation=m['derivation'],
        sources=m['sources'], draft_source_sha256=m['draft_source_sha256'], root_review=m['root_review'])
    m.update(scope='DISABLED_BUILD020_HARD_SINGLE_MAP600S_CANONICAL_NATIVE_GROUPS',
             runtime_reviewed=False, runtime_performed=False, qualified=False, functional_pass=False,
             runtime_dependencies=dict(sorted(deps.items())))
    m['derivation'] = dict(parent=str(PARENT), parent_manifest_sha256=PARENT_SHA,
        independent_review='PENDING', native_started=False, frida_used=False,
        duration_seconds=600, diagnostics=0, hard_difficulty=2,
        fixed_sources=dict(botA='botA_actual', botB='botB_actual'),
        original_v2_core_sha256=CORE_SHA, original_v2_audit_sha256=AUDIT_SHA,
        historical_results='unchanged FAIL; offline replay is design-only')
    m['root_review'] = dict(approved_for_private_a4=False, reference='PENDING independent review and Root freeze/preflight')
    excluded = {'source-manifest.json', 'HANDOFF-disabled.json'}
    m['sources'] = {p.name:sha(p) for p in dest.iterdir() if p.is_file() and p.name not in excluded}
    m['draft_source_sha256'] = {p.name:sha(p) for p in dest.glob('*.py')}
    (dest/'source-manifest.json').write_text(json.dumps(m, indent=2)+'\n')
    handoff = dict(runtime_authorized=False, native_started=False, qualified=False, functional_pass=False,
        source_manifest_sha256=sha(dest/'source-manifest.json'),
        next='independent review, Root freeze and preflight, one prospective600s window; no automatic retry')
    (dest/'HANDOFF-disabled.json').write_text(json.dumps(handoff, indent=2)+'\n')
    return dict(package=str(dest), manifest_sha256=sha(dest/'source-manifest.json'),
                runtime_pins=len(deps), native_started=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    print(json.dumps(prepare(parser.parse_args().destination), indent=2))
