import os
import pathlib
import stat
import tempfile
import unittest
from qualify_bot_sessions import create_private_runtime_root

class RootPermissionsTest(unittest.TestCase):
    def test_umask_no_longer_prevents_unprivileged_prefix_traversal(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/'private-wine-test'
            old=os.umask(0o077)
            try:
                create_private_runtime_root(root)
            finally:
                os.umask(old)
            perms=stat.S_IMODE(root.stat().st_mode)
            self.assertEqual(perms,0o711)
            self.assertTrue(perms & stat.S_IXOTH)
            self.assertFalse(perms & stat.S_IROTH)

    def test_existing_root_never_reused(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td)/'present'
            root.mkdir()
            with self.assertRaises(FileExistsError):
                create_private_runtime_root(root)

if __name__=='__main__':unittest.main()
