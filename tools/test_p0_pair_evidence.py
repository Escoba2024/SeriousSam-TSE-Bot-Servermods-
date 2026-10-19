"""Synthetic offline fixtures only; no Retail files or native evidence."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import p0_pair_evidence as checker


ENGINE = 'B79BF8BB3927FE4F8F252E141D721AE5C738DF02218F0ECC12DA5C1AFBCB534F'
VANILLA = '1C41DA35B3FC47378C407B770E1BD1DCC2B7E6BF676C140586BC6035461D4208'
BOT = '61DC27E0E7B80BADCF9AE705C30FCA88EDD3935737715DFFFF59E90C26F1FEF9'
SCRIPT = Path(__file__).with_name('p0_pair_evidence.py')


class PairEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='synthetic-private-player-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        modules = {
            'server': {'DedicatedServer.exe': '1' * 64, 'Engine.dll': ENGINE,
                       'EntitiesMP.dll': '2' * 64, 'GameMP.dll': VANILLA},
            'client': {'SeriousSam.exe': '3' * 64, 'Engine.dll': ENGINE,
                       'EntitiesMP.dll': '2' * 64, 'GameMP.dll': VANILLA},
        }
        self.pins = {'schema_version': 1, 'retail_version': '1.07',
                     'client_kind': 'vanilla', 'modules': copy.deepcopy(modules)}
        self.manifest = {
            'schema_version': 1, 'retail_version': '1.07', 'client_kind': 'vanilla',
            'run_id': 'private-run-secret', 'mapepoch': 'private-map-secret',
            'map_sha256': '4' * 64, 'modules': modules, 'snapshots': [],
        }
        for role in ('server', 'client'):
            self.add_snapshot(role)
        self.save()

    def add_snapshot(self, role, tick='83.40', sequence=1689, crc='0x12345678'):
        filename = f'{role}/secret-player-{sequence}.txt'
        raw = (f'CRC: {crc}\nLevel: 1\nSequence: {sequence}\nTick: {tick}\n'
               'Player: PRIVATE_PLAYER_NAME\nRandom seed: 123\n').encode()
        entry = dict(role=role, run_id=self.manifest['run_id'],
                     mapepoch=self.manifest['mapepoch'], path=filename,
                     sha256=hashlib.sha256(raw).hexdigest(), size=len(raw),
                     encoding='utf-8', level=1, sequence=sequence, tick=tick,
                     crc=crc, complete=True, truncated=False, dropped_records=0,
                     writer_closed=True)
        path = self.root / filename
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(raw)
        self.manifest['snapshots'].append(entry)

    def save(self):
        self.manifest_path = self.root / 'manifest.json'
        self.pins_path = self.root / 'pins.json'
        self.manifest_path.write_text(json.dumps(self.manifest), encoding='utf-8')
        self.pins_path.write_text(json.dumps(self.pins), encoding='utf-8')
        self.pin_hash = hashlib.sha256(self.pins_path.read_bytes()).hexdigest()

    def check(self):
        return checker.validate(self.root, 'manifest.json', 'pins.json', self.pin_hash)

    def reject(self):
        report = self.check()
        self.assertEqual(report['status'], 'INVALID_EVIDENCE_MANIFEST', report)
        self.assertEqual(report['native_sync'], 'NOT_ASSESSED')
        self.assertEqual(report['first_divergent_tick'], 'NOT_DETERMINED')
        return report

    def rewrite_dump(self, data, index=0):
        entry = self.manifest['snapshots'][index]
        (self.root / entry['path']).write_bytes(data)
        entry['size'] = len(data)
        entry['sha256'] = hashlib.sha256(data).hexdigest()
        self.save()

    def cli(self, *extra):
        return subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--root', str(self.root),
             '--manifest', 'manifest.json', '--pins', 'pins.json',
             '--pins-sha256', self.pin_hash, *extra],
            capture_output=True, text=True, timeout=10)

    def test_valid_pair_and_redacted_metadata_status(self):
        result = self.check()
        self.assertEqual(result['status'], 'VALIDATED_CAPTURE_METADATA')
        self.assertEqual(result['paired_snapshots'], 1)
        self.assertEqual(result['crc_differing_pairs'], 0)
        self.assertEqual(result['native_sync'], 'NOT_ASSESSED')
        self.assertEqual(result['first_divergent_tick'], 'NOT_DETERMINED')
        serialized = json.dumps(result)
        for secret in ('PRIVATE_PLAYER_NAME', 'private-run-secret',
                       'private-map-secret', 'secret-player', str(self.root), ENGINE):
            self.assertNotIn(secret, serialized)

    def test_crc_difference_is_valid_capture_metadata_not_native_failure(self):
        entry = self.manifest['snapshots'][1]
        raw = (self.root / entry['path']).read_bytes().replace(b'12345678', b'87654321')
        entry['crc'] = '0x87654321'
        self.rewrite_dump(raw, 1)
        result = self.check()
        self.assertEqual(result['status'], 'VALIDATED_CAPTURE_METADATA')
        self.assertEqual(result['crc_differing_pairs'], 1)

    def test_series_decimal_equivalence_and_sparse_coverage(self):
        self.manifest['snapshots'][1]['tick'] = '83.40000000000000000000'
        self.add_snapshot('server', '100.05', 2022)
        self.add_snapshot('client', '100.050', 2022)
        self.save()
        self.assertEqual(self.check()['paired_snapshots'], 2)
        self.assertEqual(self.check()['first_divergent_tick'], 'NOT_DETERMINED')

    def test_bot_pin_mode(self):
        self.pins['client_kind'] = self.manifest['client_kind'] = 'bot61dc'
        self.pins['modules']['client']['GameMP.dll'] = BOT
        self.manifest['modules']['client']['GameMP.dll'] = BOT
        self.save()
        self.assertEqual(self.check()['status'], 'VALIDATED_CAPTURE_METADATA')

    def test_missing_top_fields_and_unknown_fields(self):
        original = copy.deepcopy(self.manifest)
        for key in original:
            with self.subTest(key=key):
                self.manifest = copy.deepcopy(original)
                del self.manifest[key]
                self.save()
                self.reject()
        self.manifest = copy.deepcopy(original)
        self.manifest['unexpected'] = 'PRIVATE_PLAYER_NAME'
        self.save()
        self.reject()

    def test_missing_snapshot_fields(self):
        original = copy.deepcopy(self.manifest)
        for key in original['snapshots'][0]:
            with self.subTest(key=key):
                self.manifest = copy.deepcopy(original)
                del self.manifest['snapshots'][0][key]
                self.save()
                self.reject()

    def test_wrong_role_run_epoch_and_metadata(self):
        original = copy.deepcopy(self.manifest)
        for key, bad in [('role', 'observer'), ('run_id', 'other'),
                         ('mapepoch', 'other'), ('level', 2), ('sequence', 1690),
                         ('tick', '83.40000000000000000001'), ('crc', '0x00000000')]:
            with self.subTest(key=key):
                self.manifest = copy.deepcopy(original)
                self.manifest['snapshots'][0][key] = bad
                self.save()
                self.reject()

    def test_both_raw_and_manifest_different_tick_still_unpaired(self):
        self.manifest['snapshots'][1]['tick'] = '83.45'
        raw = (self.root / self.manifest['snapshots'][1]['path']).read_bytes()
        self.rewrite_dump(raw.replace(b'83.40', b'83.45'), 1)
        self.reject()

    def test_missing_side_empty_series_duplicate_identity_and_file(self):
        original = copy.deepcopy(self.manifest)
        for snapshots in ([], original['snapshots'][:1],
                          original['snapshots'] + [original['snapshots'][0]],
                          [original['snapshots'][0], dict(original['snapshots'][1],
                           path=original['snapshots'][0]['path'])]):
            with self.subTest(snapshots=len(snapshots)):
                self.manifest = copy.deepcopy(original)
                self.manifest['snapshots'] = snapshots
                self.save()
                self.reject()

    def test_hash_and_byte_size_checked_on_original_bytes(self):
        original = copy.deepcopy(self.manifest)
        for key, bad in [('sha256', '0' * 64), ('size', 1)]:
            self.manifest = copy.deepcopy(original)
            self.manifest['snapshots'][0][key] = bad
            self.save()
            self.reject()

    def test_binary_module_pins_version_and_module_omissions(self):
        original = copy.deepcopy(self.manifest)
        for role in ('server', 'client'):
            for name in original['modules'][role]:
                for remove in (False, True):
                    with self.subTest(role=role, module=name, remove=remove):
                        self.manifest = copy.deepcopy(original)
                        if remove:
                            del self.manifest['modules'][role][name]
                        else:
                            self.manifest['modules'][role][name] = '9' * 64
                        self.save()
                        self.reject()
        self.manifest = copy.deepcopy(original)
        self.manifest['retail_version'] = '1.10'
        self.save()
        self.reject()

    def test_trust_anchor_and_known_pins_cannot_be_self_redefined(self):
        self.pin_hash = '0' * 64
        self.reject()
        self.pins['modules']['server']['Engine.dll'] = '9' * 64
        self.manifest['modules']['server']['Engine.dll'] = '9' * 64
        self.save()
        self.reject()

    def test_duplicate_json_keys_at_any_depth(self):
        for path in (self.manifest_path, self.pins_path):
            self.save()
            raw = path.read_text().replace('"Engine.dll":', '"Engine.dll":"' + ENGINE + '","Engine.dll":', 1)
            path.write_text(raw)
            if path == self.pins_path:
                self.pin_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.reject()

    def test_bad_json_types_nonfinite_and_bool_integers(self):
        original = copy.deepcopy(self.manifest)
        for key, bad in [('schema_version', True), ('snapshots', {}), ('modules', []),
                         ('run_id', ''), ('map_sha256', 'not-a-hash')]:
            self.manifest = copy.deepcopy(original)
            self.manifest[key] = bad
            self.save()
            self.reject()
        for value in ('NaN', 'Infinity', '[]', '{', '{"private":NaN}'):
            self.manifest_path.write_text(value)
            self.reject()

    def test_incomplete_truncated_open_writer_and_drop_flags(self):
        original = copy.deepcopy(self.manifest)
        for key, value in [('complete', False), ('truncated', True),
                           ('writer_closed', False), ('dropped_records', 1),
                           ('dropped_records', False), ('size', True)]:
            self.manifest = copy.deepcopy(original)
            self.manifest['snapshots'][0][key] = value
            self.save()
            self.reject()

    def test_invalid_raw_headers_and_truncation_even_when_rehashed(self):
        raw = (self.root / self.manifest['snapshots'][0]['path']).read_bytes()
        mutations = [raw.rstrip(b'\n'), raw + raw, raw.replace(b'83.40', b'NaN'),
                     raw.replace(b'83.40', b'83.40.5'), raw.replace(b'1689', b'bad'),
                     raw.replace(b'CRC:', b'MISSING:'), raw + b'CRC: bad\n',
                     raw.replace(b'Level: 1\n', b''), raw.replace(b'83.40', b'83,40'),
                     b'CRC: 0x12345678\nLevel: 1\nSequence: 1689\nTick: 83.40\n',
                     raw + b'\x00\n', raw + b'\xff\n']
        for data in mutations:
            with self.subTest(data=data):
                self.rewrite_dump(data)
                self.reject()

    def test_strict_encoding_and_crlf_preserve_byte_hash(self):
        raw = (self.root / self.manifest['snapshots'][0]['path']).read_bytes()
        self.manifest['snapshots'][0]['encoding'] = 'cp1252'
        self.rewrite_dump(raw.replace(b'PRIVATE_PLAYER_NAME', b'PRIVATE_\xe4_NAME').replace(b'\n', b'\r\n'))
        self.assertEqual(self.check()['status'], 'VALIDATED_CAPTURE_METADATA')

    def test_path_traversal_absolute_and_windows_escapes(self):
        for path in ('../secret', '/etc/passwd', 'C:/private', 'server/../x',
                     'server//x', './server/x', 'server\\x', 'server/x:stream'):
            with self.subTest(path=path):
                self.manifest['snapshots'][0]['path'] = path
                self.save()
                self.reject()

    def test_symlink_snapshot_directory_manifest_pins_and_root(self):
        original = copy.deepcopy(self.manifest)
        for target in ('file', 'directory', 'manifest', 'pins', 'root'):
            with self.subTest(target=target):
                self.manifest = copy.deepcopy(original)
                self.save()
                alias = self.root / 'alias'
                if target == 'file':
                    alias.symlink_to(self.root / original['snapshots'][0]['path'])
                    self.manifest['snapshots'][0]['path'] = 'alias'
                    self.save()
                    self.reject()
                elif target == 'directory':
                    alias.symlink_to(self.root / 'server', target_is_directory=True)
                    self.manifest['snapshots'][0]['path'] = 'alias/secret-player-1689.txt'
                    self.save()
                    self.reject()
                elif target in ('manifest', 'pins'):
                    source = self.root / (target + '.json')
                    other = self.root / (target + '-copy.json')
                    source.rename(other)
                    source.symlink_to(other)
                    self.reject()
                    source.unlink()
                    other.rename(source)
                else:
                    alias.symlink_to(self.root, target_is_directory=True)
                    report = checker.validate(alias, 'manifest.json', 'pins.json', self.pin_hash)
                    self.assertEqual(report['status'], 'INVALID_EVIDENCE_MANIFEST')
                if alias.is_symlink():
                    alias.unlink()

    def test_missing_directory_and_hardlinked_file(self):
        self.manifest['snapshots'][0]['path'] = 'absent/no-file.txt'
        self.save()
        self.reject()
        self.manifest['snapshots'][0]['path'] = 'hardlink.txt'
        os.link(self.root / 'server/secret-player-1689.txt', self.root / 'hardlink.txt')
        self.save()
        self.reject()

    def test_fifo_rejected_without_blocking(self):
        os.mkfifo(self.root / 'pipe.txt')
        self.manifest['snapshots'][0]['path'] = 'pipe.txt'
        self.save()
        self.assertEqual(self.cli().returncode, 2)

    def test_size_limits_and_snapshot_count(self):
        self.manifest['snapshots'][0]['size'] = 8 * 1024 * 1024 + 1
        self.save()
        self.reject()
        self.manifest['snapshots'] *= 129
        self.save()
        self.reject()
        self.manifest_path.write_bytes(b' ' * (1024 * 1024 + 1))
        self.reject()

    def test_cli_valid_and_invalid_reports_no_private_output(self):
        ok = self.cli()
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)['status'], 'VALIDATED_CAPTURE_METADATA')
        self.manifest_path.write_text('{"PRIVATE_PLAYER_NAME":')
        bad = self.cli()
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(json.loads(bad.stdout)['status'], 'INVALID_EVIDENCE_MANIFEST')
        self.assertEqual(bad.stderr, '')
        for secret in ('PRIVATE_PLAYER_NAME', str(self.root), 'manifest.json'):
            self.assertNotIn(secret, bad.stdout)

    def test_cli_argument_errors_are_redacted(self):
        result = self.cli('--PRIVATE_PLAYER_NAME')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, '')
        self.assertNotIn('PRIVATE_PLAYER_NAME', result.stdout)
        self.assertEqual(json.loads(result.stdout)['status'], 'INVALID_EVIDENCE_MANIFEST')

    def test_no_writes_or_in_place_snapshot_repair(self):
        before = {p.relative_to(self.root): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.check()['status'], 'VALIDATED_CAPTURE_METADATA')
        after = {p.relative_to(self.root): p.read_bytes()
                 for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_multiple_levels_are_not_a_single_map_epoch(self):
        for role in ('server', 'client'):
            self.add_snapshot(role, '84.40', 1709)
            self.manifest['snapshots'][-1]['level'] = 2
            entry = self.manifest['snapshots'][-1]
            raw = (self.root / entry['path']).read_bytes().replace(b'Level: 1', b'Level: 2')
            self.rewrite_dump(raw, len(self.manifest['snapshots']) - 1)
        self.reject()

    def test_snapshot_and_pin_unknown_keys_are_rejected(self):
        self.manifest['snapshots'][0]['native_pass'] = True
        self.save()
        self.reject()
        del self.manifest['snapshots'][0]['native_pass']
        self.pins['native_pass'] = True
        self.save()
        self.reject()

    def test_oversized_actual_snapshot_is_not_read_unbounded(self):
        entry = self.manifest['snapshots'][0]
        with (self.root / entry['path']).open('wb') as target:
            target.truncate(8 * 1024 * 1024 + 1)
        self.reject()

    def test_invalid_utf8_and_deeply_nested_manifest_are_redacted(self):
        for data in (b'\xff', b'[' * 2000 + b']' * 2000):
            self.manifest_path.write_bytes(data)
            result = self.reject()
            self.assertIn(result['reason'], ('INVALID_INPUT_OR_ARCHIVE', 'INVALID_SCHEMA'))

    def test_same_truncation_cannot_be_claimed_native_completeness(self):
        # No native footer is known: even rehashed header+state text can only
        # qualify metadata, never prove native completeness or authenticity.
        for index in (0, 1):
            self.rewrite_dump(b'CRC: 0x12345678\nLevel: 1\nSequence: 1689\n'
                              b'Tick: 83.40\nPlayer: partial\n', index)
        report = self.check()
        self.assertEqual(report['status'], 'VALIDATED_CAPTURE_METADATA')
        self.assertEqual(report['capture_authenticity'], 'NOT_ASSESSED')
        self.assertEqual(report['native_sync'], 'NOT_ASSESSED')


if __name__ == '__main__':
    unittest.main()
