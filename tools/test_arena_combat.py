"""Run the actual engine-free arena policy; no native Retail acceptance claim."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class ArenaPolicyTests(unittest.TestCase):
    def test_migration_combat_reaction_and_isolation(self):
        source = (Path(__file__).resolve().parents[1] / 'poc/candidates/'
                  'redstation-supply-20261107/test_arena_combat.cpp')
        with tempfile.TemporaryDirectory(prefix='tse-arena-policy-') as tmp:
            executable = str(Path(tmp) / 'arena')
            subprocess.run(['g++', '-std=c++17', '-O1', '-Wall', '-Wextra',
                            '-pedantic', str(source), '-o', executable], check=True)
            subprocess.run([executable], check=True)


if __name__ == '__main__':
    unittest.main()
