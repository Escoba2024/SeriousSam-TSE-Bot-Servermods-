"""Bounded source preparation on Root's closed own-PE build; no execution."""
from pathlib import Path
import hashlib
import importlib.util
import json
import tempfile
import unittest


class PreparationTests(unittest.TestCase):
    def test_actual_source_package_is_disabled_complete_and_does_not_copy_prefix(self):
        try:import prepare_win32_instruction_method as builder
        except ImportError:self.fail('missing offline source preparer')
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'new';builder.prepare(p)
            m=json.loads((p/'source-manifest.json').read_text())
            self.assertFalse(m['runtime_reviewed']);self.assertFalse(m['retail_qualified'])
            self.assertEqual(m['build']['exe_sha256'],'4305c136f460f6fec4ff8b6ccb9419394514e2cee808b5ab5865b12b59f5acf4')
            self.assertEqual(Path(m['build']['original_manifest']).parent.name,'tse-win32-instruction-method-build-stdin-fixed-20261114')
            self.assertIn(str(p/'test_win32_command_reader.py'),m['runtime_dependencies'])
            self.assertEqual([(s['rva'],len(bytes.fromhex(s['hex'])))for s in m['sites']],[(0x1000,17),(0x1070,14)])
            for n,h in m['runtime_dependencies'].items():
                self.assertEqual(hashlib.sha256(Path(n).read_bytes()).hexdigest(),h,n)
            self.assertFalse((p/'wineprefix').exists())
            with self.assertRaises(ValueError):builder.prepare(p)


if __name__=='__main__':unittest.main()
