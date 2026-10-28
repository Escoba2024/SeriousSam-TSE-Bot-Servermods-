"""Source-only integration tests: never import or execute a native qualifier."""
import ast
from pathlib import Path
import re
from types import SimpleNamespace
import unittest

from log_error_prefilter import RUNTIME_ERROR_PATTERN, make_runtime_error_matcher

BASE = Path(__file__).resolve().parent.parent
ORIGINAL = (BASE/'native-tools/qualify_bot_sessions.py' if
            (BASE/'native-tools/qualify_bot_sessions.py').is_file() else
            Path('/srv/tse-cecil-guard-20261026/tools/qualify_bot_sessions.py'))
CANDIDATE = (BASE/'native-prefilter-candidate/tools/qualify_bot_sessions.py' if
             (BASE/'native-prefilter-candidate/tools/qualify_bot_sessions.py').is_file() else
             BASE/'performance/native/tools/qualify_bot_sessions.py')


def load_function(path):
    tree = ast.parse(path.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'runtime_error')
    scope = {'q': SimpleNamespace(BAD=re.compile(RUNTIME_ERROR_PATTERN.removesuffix('|FatalError:'))),
             're': re, 'make_runtime_error_matcher': make_runtime_error_matcher,
             '_runtime_error_matcher': None}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), scope)
    return scope


def result_signature(match):
    return None if match is None else (match.span(), match.group(), match.groups(), match.groupdict())


class IntegrationTests(unittest.TestCase):
    def test_entire_other_ast_is_unchanged(self):
        def stripped(path):
            tree = ast.parse(path.read_text())
            # The 28 October join predicate has its own behavioral/equivalence
            # tests. Normalize only that exact documented transformation;
            # resource/error gates and all other native code must still match.
            if path == ORIGINAL:
                transport = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                                 and n.name == 'WineTransport')
                observe = next(n for n in transport.body if isinstance(n, ast.FunctionDef)
                               and n.name == 'observe')
                observe.body = [n for n in observe.body if not (
                    isinstance(n, ast.Assign) and len(n.targets) == 1
                    and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'logs')]
                for n in observe.body:
                    if (isinstance(n, ast.Assign) and len(n.targets) == 1
                            and isinstance(n.targets[0], ast.Name)
                            and n.targets[0].id == 'native_join'):
                        n.value = ast.parse("native_join_present(self.roles[state['id']]/'SeriousSam.log')",
                                            mode='eval').body
            tree.body = [n for n in tree.body if not (
                isinstance(n, ast.FunctionDef) and n.name in ('runtime_error', 'native_join_present') or
                isinstance(n, ast.Import) and [a.name for a in n.names] == ['locale'] or
                isinstance(n, ast.ImportFrom) and n.module == 'log_error_prefilter' or
                isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and
                    t.id == '_runtime_error_matcher' for t in n.targets))]
            return ast.dump(tree, include_attributes=False)
        self.assertEqual(stripped(ORIGINAL), stripped(CANDIDATE))

    def test_real_entrypoint_returns_reference_matches(self):
        old, new = load_function(ORIGINAL), load_function(CANDIDATE)
        texts = [
            'normal state', "Identifier 'sam_strTechTestLevel' is not declared",
            "Identifier 'sam_strTechTestLevel_extended' is not declared",
            "Identifier 'sam_strTechTestLevel\nnext' is not declared",
            "Identifier 'other' is not declared", 'FatalError:', 'CRC check failed',
            'fatal Error first SYNCBAD second', 'Unknown symbol', 'Cannot load script',
            "Identifier 'sam_strTechTestLevel' is not declared; Fatal Error",
        ]
        for text in texts:
            with self.subTest(text=text):
                self.assertEqual(result_signature(old['runtime_error'](text)),
                                 result_signature(new['runtime_error'](text)))

    def test_pattern_changes_refresh_cache_and_fallback(self):
        old, new = load_function(ORIGINAL), load_function(CANDIDATE)
        self.assertIsNone(new['runtime_error']('ordinary'))
        for scope in (old, new):
            scope['q'].BAD = re.compile('NEW_FATAL')
        self.assertEqual(result_signature(old['runtime_error']('NEW_FATAL diagnostic')),
                         result_signature(new['runtime_error']('NEW_FATAL diagnostic')))
        self.assertFalse(new['_runtime_error_matcher'].fast_path_enabled)

    def test_original_runtime_ignores_bad_compilation_flags_so_candidate_must_too(self):
        old, new = load_function(ORIGINAL), load_function(CANDIDATE)
        for scope in (old, new):
            scope['q'].BAD = re.compile('SYNCBAD', re.IGNORECASE)
        self.assertIsNone(old['runtime_error']('syncbad'))
        self.assertIsNone(new['runtime_error']('syncbad'))

    def test_same_size_changed_full_text_is_not_cached(self):
        new = load_function(CANDIDATE)
        self.assertIsNone(new['runtime_error']('ordinary line'))
        self.assertIsNotNone(new['runtime_error']('SYNCBAD line!'))


if __name__ == '__main__':
    unittest.main()
