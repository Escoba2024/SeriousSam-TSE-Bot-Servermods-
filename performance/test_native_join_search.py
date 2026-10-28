"""Fresh join evidence must remain equivalent to the former full-text predicate."""
import ast
import io
import locale
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).parent / 'native/tools/qualify_bot_sessions.py'


class NativeJoinSearchTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(SOURCE.read_text())
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                 and n.name == 'native_join_present']
        self.assertEqual(len(nodes), 1, 'stateless native join search is missing')
        scope = {'locale': locale, 'sys': sys,
                 'q': SimpleNamespace(text=lambda p: p.read_text(errors='replace') if p.exists() else '')}
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), scope)
        self.search = scope['native_join_present']

    def test_equivalent_for_missing_empty_and_complete_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log'
            self.assertFalse(self.search(path))
            for text in ['', 'joining', 'rejoined', 'joined', 'JOINED', 'xjoinedx',
                         'a' * 40000, 'a' * 40000 + 'joined']:
                path.write_text(text)
                self.assertEqual(self.search(path), 'joined' in path.read_text(errors='replace'))

    def test_marker_across_every_chunk_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log'
            for offset in range(16379, 16390):
                path.write_text('x' * offset + 'joined' + 'z' * 17000)
                self.assertTrue(self.search(path), offset)

    def test_encoding_and_universal_newlines_match_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log'
            for data in [b'\xffjoined', b'jo\xffined', b'jo\r\nined',
                         'é' .encode() * 16383 + b'joined',
                         b'x' * 16383 + b'joi\rned', b'joined\r\n']:
                path.write_bytes(data)
                self.assertEqual(self.search(path), 'joined' in path.read_text(errors='replace'))

    def test_same_size_rewrite_truncation_and_append_are_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'log'
            for text, expected in [('joined', True), ('absent', False),
                                   ('', False), ('later joined', True)]:
                path.write_text(text)
                self.assertEqual(self.search(path), expected)

    def test_late_read_error_is_not_hidden_by_early_join_marker(self):
        class LateFailure(io.BytesIO):
            def read(self, size=-1):
                if size < 0 or self.tell() + size > 20000:
                    raise OSError('failure in later part of complete file')
                return super().read(size)
        class LateTextFailure(io.StringIO):
            def read(self, size=-1):
                if size < 0 or self.tell() + size > 20000:
                    raise OSError('failure in later part of complete file')
                return super().read(size)
        with patch.object(Path, 'exists', return_value=True), patch.object(
                Path, 'open', side_effect=lambda *a, **kw: (
                    LateFailure(b'joined' + b'x' * 40000) if (a == ('rb',) or kw.get('mode') == 'rb')
                    else LateTextFailure('joined' + 'x' * 40000))):
            with self.assertRaisesRegex(OSError, 'later part'):
                self.search(Path('/unused'))

    def test_absent_marker_reads_to_eof_and_closes_stream(self):
        readers = []
        def opened(*a, **kw):
            reader = io.BytesIO(b'x' * 40000) if (a == ('rb',) or kw.get('mode') == 'rb') else io.StringIO('x' * 40000)
            readers.append(reader)
            return reader
        with patch.object(Path, 'exists', return_value=True), patch.object(Path, 'open', side_effect=opened):
            self.assertFalse(self.search(Path('/unused')))
        self.assertTrue(all(r.closed for r in readers))

    def test_read_failure_is_never_clean_evidence(self):
        with patch.object(Path, 'exists', return_value=True), patch.object(
                Path, 'open', side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):
                self.search(Path('/unused'))

    def test_non_utf8_default_retains_original_decoder(self):
        # UTF16 shows why unconditional byte substring search is incorrect.
        with patch.object(sys, 'flags', SimpleNamespace(utf8_mode=0)), patch.object(
                locale, 'getencoding', return_value='utf-16'), patch.object(
                Path, 'exists', return_value=True), patch.object(
                Path, 'open', side_effect=lambda **kw: io.StringIO('joined')):
            self.assertTrue(self.search(Path('/unused')))


if __name__ == '__main__':
    unittest.main()
