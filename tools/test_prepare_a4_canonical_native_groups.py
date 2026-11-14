"""Focused offline adapter checks; never import or launch the native runner."""
import ast
import json
import os
from pathlib import Path
import unittest

import prepare_a4_canonical_native_groups as builder


class ProspectiveAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = (builder.PARENT/'run-a4.py').read_text()
        cls.source = builder.transform(cls.parent)

    def test_fixed_contract_is_archived_before_first_read_and_barrier_release(self):
        source = self.source
        self.assertLess(source.index('canonical_groups.declare('), source.index('snap=inventory.sample('))
        self.assertLess(source.index("(E/'native-group-contract.json').write_text"), source.index("control('key','Pause',.1)"))
        self.assertIn("native_registry['native_group_contract']=native_group_contract", source)
        self.assertIn('snap=canonical_groups.bind_sample(snap,group,native_group_contract)', source)
        self.assertIn('sampled=canonical_groups.bind_sample(sampled,group,native_group_contract)', source)

    def test_one_authoritative_wrapper_and_raw_activity_stream_unchanged(self):
        self.assertEqual(self.source.count('canonical_groups.apply('), 1)
        self.assertNotIn('native_fire.apply(', self.source)
        self.assertIn('canonical_groups.apply(report[\'active_evidence\'],logs,mapping,active_snapshots,native_registry,server,native_group_contract)', self.source)
        raw = "policy.active_evidence(logs,mapping,active_snapshots,queries,(R/'server/Dedicated_BotTest.log').read_text(errors='replace'))"
        self.assertIn(raw, self.source)
        self.assertIn('initial.add(sampled,elapsed);active_snapshots.append(sampled)', self.source)

    def test_all_existing_reader_query_sleep_and_control_calls_are_identical(self):
        def calls(source):
            result = []
            for n in ast.walk(ast.parse(source)):
                if not isinstance(n, ast.Call):
                    continue
                named = isinstance(n.func, ast.Name) and n.func.id in {'control', 'sample_host', 'HostBudget'}
                attribute = isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id in {'probe','inventory','B','time','pauseprobe','transaction','host_budget'}
                if named or attribute:
                    result.append(ast.dump(n, include_attributes=False))
            return sorted(result)
        self.assertEqual(calls(self.parent), calls(self.source))

    def test_normal_close_startup_and_final_gates_unchanged(self):
        def function(source, name):
            node = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == name)
            return ast.dump(node, include_attributes=False)
        for name in ('close', 'count', 'checked_query', 'launch', 'archive_preflight_query', 'whole_quiescent'):
            with self.subTest(name=name):
                self.assertEqual(function(self.parent, name), function(self.source, name))
        self.assertIn("roles=tuple(records)", self.source)
        self.assertIn('RUNTIME_REVIEWED=False', self.source)
        self.assertIn('default=600', self.source)
        self.assertIn('gam_iStartDifficulty=2;', self.source)
        self.assertNotIn('frida', self.source.lower())

    def test_parent_and_old_v2_bytes_have_exact_reviewed_pins(self):
        self.assertEqual(builder.sha(builder.PARENT/'source-manifest.json'), builder.PARENT_SHA)
        self.assertEqual(builder.sha(builder.PARENT/'a4_fire_observer_v2.py'), builder.CORE_SHA)
        self.assertEqual(builder.sha(builder.PARENT/'audit_a4_native_fire_observer_v2.py'), builder.AUDIT_SHA)
        for name, expected in [('a4_fire_observer_v2.py', builder.CORE_SHA), ('audit_a4_native_fire_observer_v2.py', builder.AUDIT_SHA)]:
            self.assertEqual(builder.sha(Path(__file__).with_name(name)), expected)

    def test_nonunique_or_missing_inherited_anchor_rejected(self):
        with self.assertRaises(ValueError):
            builder.transform(self.parent.replace('import a4_fire_observer_v2 as native_fire', ''))
        with self.assertRaises(ValueError):
            builder.transform(self.parent+'\nimport a4_fire_observer_v2 as native_fire\n')


@unittest.skipUnless(os.environ.get('TSE_A4_CANONICAL_PACKAGE'), 'explicit disabled package required')
class DisabledPackageTests(unittest.TestCase):
    def test_all_pins_and_unchanged_inherited_files(self):
        root = Path(os.environ['TSE_A4_CANONICAL_PACKAGE'])
        m = json.loads((root/'source-manifest.json').read_text())
        for key in ('runtime_reviewed', 'runtime_performed', 'qualified', 'functional_pass'):
            self.assertIs(m[key], False)
        self.assertIs(m['root_review']['approved_for_private_a4'], False)
        self.assertEqual(m['derivation']['parent_manifest_sha256'], builder.PARENT_SHA)
        for p, h in m['runtime_dependencies'].items():
            self.assertEqual(builder.sha(p), h, p)
        for name, h in m['sources'].items():
            self.assertEqual(builder.sha(root/name), h, name)
        for name, h in m['draft_source_sha256'].items():
            self.assertEqual(builder.sha(root/name), h, name)
        for path in builder.PARENT.iterdir():
            if path.is_file() and path.name not in {'run-a4.py','source-manifest.json','HANDOFF-disabled.json','test_a4_hard_maps.py'}:
                self.assertEqual(builder.sha(root/path.name), builder.sha(path), path.name)
        self.assertEqual((root/'run-a4.py').read_text(), builder.transform((builder.PARENT/'run-a4.py').read_text()))
        expected = (builder.PARENT/'test_a4_hard_maps.py').read_text().replace("'native_fire.apply('", "'canonical_groups.apply('").replace(
            "'native_fire.bind_sample(sampled,0,server,log_offsets)'", "'canonical_groups.bind_sample(sampled,group,native_group_contract)'")
        self.assertEqual((root/'test_a4_hard_maps.py').read_text(), expected)


if __name__ == '__main__':
    unittest.main()
