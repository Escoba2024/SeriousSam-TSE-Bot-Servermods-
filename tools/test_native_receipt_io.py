import tempfile
from pathlib import Path
import unittest
import native_receipt_io as n

class ReceiptIOTests(unittest.TestCase):
    def test_truncated_write_retried_using_completed_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'guard.json';p.write_text('{"status":')
            def finish_write(_):p.write_text('{"status":"FINISHED"}')
            self.assertEqual(n.read_receipt(p,pause=finish_write),{'status':'FINISHED'})
    def test_persistent_truncation_never_returns_empty_or_old_success(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'guard.json';p.write_text('{')
            with self.assertRaises(RuntimeError):n.read_receipt(p,attempts=2,pause=lambda _:None)
    def test_missing_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):n.read_receipt(Path(d)/'missing',attempts=1)
    def test_array_is_not_a_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'guard.json';p.write_text('[]')
            with self.assertRaises(ValueError):n.read_receipt(p)
    def test_size_limit_rejects_oversized_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'guard.json';p.write_text('{"long":"'+'a'*100+'"}')
            with self.assertRaises(ValueError):n.read_receipt(p,max_bytes=32)

if __name__=='__main__':unittest.main()
