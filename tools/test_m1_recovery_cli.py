import json
import importlib.util
from unittest.mock import patch
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

class RecoveryCLITests(unittest.TestCase):
    def test_module_import_has_no_native_or_cli_side_effects(self):
        script=Path(__file__).with_name('qualify_m1_recovery.py')
        spec=importlib.util.spec_from_file_location('m1_recovery_import_test',script)
        module=importlib.util.module_from_spec(spec)
        with patch.object(sys,'argv',[str(script)]):
            try:spec.loader.exec_module(module)
            except SystemExit as exc:self.fail('import executed CLI admission: '+str(exc))
        self.assertTrue(callable(module.main))
    def test_default_mode_never_creates_or_overwrites_native_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);(base/'duration-matrix.json').write_text('{"status":"DURATION_MATRIX_ACCEPTED"}')
            marker=base/'recovery-qualification.json';marker.write_text('{"existing":"preserve"}')
            script=Path(__file__).with_name('qualify_m1_recovery.py')
            p=subprocess.run([sys.executable,str(script),'--evidence-root',str(base)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertFalse(json.loads(p.stdout)['native_actions'])
            self.assertEqual(marker.read_text(),'{"existing":"preserve"}')
            self.assertEqual({x.name for x in base.iterdir()},{'duration-matrix.json','recovery-qualification.json'})
    def test_missing_matrix_default_fails_closed_without_side_effects(self):
        with tempfile.TemporaryDirectory() as d:
            p=subprocess.run([sys.executable,str(Path(__file__).with_name('qualify_m1_recovery.py')),'--evidence-root',d],capture_output=True,text=True)
            self.assertEqual(p.returncode,3,p.stderr)
            self.assertFalse(json.loads(p.stdout)['native_actions'])
            self.assertEqual(list(Path(d).iterdir()),[])

if __name__=='__main__':unittest.main()
