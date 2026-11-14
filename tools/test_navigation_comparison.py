"""Matched candidate contracts; never import or execute a native controller."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import navigation_comparison_policy as policy
import prepare_navigation_comparison as builder


def logs(build):
    tail = 'BOT-Expert-Rifle tier=5 persona=marksman' if build == '048' else 'DEMON tier=3 persona=duelist'
    suffix = '' if build == '048' else ' model=arena-v1'
    text = ''.join(f'[BotHuman] local={i} profile={tail} seed={100+i}{suffix}\n' for i in range(4))
    return dict(botA=text, botB=text)


class ProfileContract(unittest.TestCase):
    def test_each_actual_schema_requires_all_four_locals_and_both_groups(self):
        for build in ('048', '018', '020'):
            rows = policy.check_tiers(logs(build), build)
            self.assertEqual(set(rows), {'botA', 'botB'})
            self.assertEqual({r['local'] for r in rows['botA']}, set(range(4)))

    def test_wrong_model_persona_tier_missing_malformed_or_fallback_fails(self):
        for build in ('048', '018', '020'):
            text = logs(build)['botA']
            bad = [text.replace('local=3', 'local=2'), text.replace('tier=', 'tier=9'),
                   text + '[BotHuman] local=0 roster index 7 rejected, average fallback\n',
                   text.replace('seed=100', 'seed=broken'), text + '[BotHuman] local=0 profile=unknown tier=3 persona=duelist seed=1\n',
                   logs('018' if build == '048' else '048')['botA']]
            for candidate in bad:
                with self.subTest(build=build, candidate=candidate[:80]), self.assertRaises(ValueError):
                    policy.check_tiers(dict(botA=candidate, botB=text), build)
            with self.assertRaises(ValueError):
                policy.check_tiers(dict(botA=text), build)

    def test_only_red600_diag0_and_whitelisted_versions(self):
        policy.options('redstation', 600, 0, '048')
        for args in [('hole',600,0,'048'), ('redstation',599,0,'018'),
                     ('redstation',600,1,'020'), ('redstation',600,0,'019'),
                     ('redstation',True,0,'048')]:
            with self.assertRaises(ValueError): policy.options(*args)


class DerivationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = (builder.PARENT/'run-a4.py').read_text()
        cls.adapter = (builder.PARENT/'adapter_policy.py').read_text()

    def test_controller_changes_only_candidate_paths_and_unique_names(self):
        for build in ('048','018','020'):
            result = builder.transform_controller(self.parent, build)
            record = policy.CANDIDATES[build]
            restored = result.replace(record['directory']+'/Sources/Game/GameMP.dll', policy.CANDIDATES['020']['directory']+'/Sources/Game/GameMP.dll')
            restored = restored.replace(f'ssam-nav-{build}-hard-ordered-', 'ssam-a4-020-hard-ordered-')
            restored = restored.replace(f'nav-{build}-hard-ordered-', 'a4-020-hard-ordered-')
            self.assertEqual(restored, self.parent)
            self.assertIn('RUNTIME_REVIEWED=False', result)

    def test_adapter_preserves_all_other_functions_and_the_old_v3_readers(self):
        def normalized(source):
            tree=ast.parse(source)
            tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name in ('options','check_tiers'))]
            for n in tree.body:
                if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CANDIDATE_SHA' for t in n.targets): n.value=ast.Constant('CANDIDATE')
            return ast.dump(tree)
        for build in ('048','018','020'):
            output = builder.transform_adapter(self.adapter, build)
            self.assertEqual(normalized(output), normalized(self.adapter))
            namespace={}
            for n in ast.parse(output).body:
                if isinstance(n,ast.FunctionDef) and n.name in ('options','check_tiers'):
                    exec(compile(ast.Module(body=[n],type_ignores=[]),'<isolated contract>','exec'),namespace)
            self.assertEqual(len(namespace['check_tiers'](logs(build))['botA']),4)
            with self.assertRaises(ValueError): namespace['options']('hole',600,0)

    def test_parent_manifest_and_required_observers_are_pinned(self):
        self.assertEqual(builder.sha(builder.PARENT/'source-manifest.json'), builder.PARENT_SHA)
        for filename, expected in builder.UNCHANGED.items():
            self.assertEqual(builder.sha(builder.PARENT/filename), expected)

    def test_nonunique_controller_anchor_fails(self):
        with self.assertRaises(ValueError): builder.transform_controller(self.parent + '\n' + "CANDIDATE_DLL=Path('/srv/tse-milestone-a-build-020-20261114/Sources/Game/GameMP.dll')",'048')

    def test_wrong_source_or_dll_cannot_create_a_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/'package'
            with patch.object(builder,'validate_build',side_effect=ValueError('source hash')):
                with self.assertRaisesRegex(ValueError,'source hash'):builder.prepare(dest,'048')
            self.assertFalse(dest.exists())

    def test_complete_build_closure_rejects_real_file_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp); source=base/'Sources/Game'; source.mkdir(parents=True)
            overlay=base/'overlay'; overlay.mkdir()
            source_hashes={}; overlay_hashes={}
            for directory,count,pins in [(source,47,source_hashes),(overlay,28,overlay_hashes)]:
                for i in range(count):
                    name=f'source-{i}.h'; file=directory/name; file.write_text(str(i)); pins[name]=builder.sha(file)
            dll=source/'GameMP.dll'; dll.write_bytes(b'candidate fixture')
            original=policy.CANDIDATES['048']
            manifest=dict(build_ok=True,repo_commit=original['source_commit'],dll_sha256=builder.sha(dll),candidate=str(dll),source_overlay=str(overlay),source_sha256=source_hashes,overlay_sha256=overlay_hashes)
            path=base/'manifest.json';path.write_text(json.dumps(manifest))
            spec=dict(original,directory=str(base),dll_sha256=builder.sha(dll),manifest_sha256=builder.sha(path))
            with patch.dict(policy.CANDIDATES,{'048':spec}):
                _,pins=builder.validate_build('048');self.assertEqual(len(pins),77)
                (source/'source-1.h').write_text('corrupted')
                with self.assertRaisesRegex(ValueError,'source hash'):builder.validate_build('048')
                (source/'source-1.h').write_text('1');dll.write_bytes(b'wrong DLL')
                with self.assertRaisesRegex(ValueError,'source hash'):builder.validate_build('048')


if __name__ == '__main__': unittest.main()
