import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import notion_dispatch as dispatch


class ReviewCheckoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ['TMPDIR'])
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.remote = self.root / 'remote'
        self.remote.mkdir()
        self.git(self.remote, 'init', '-q')
        self.git(self.remote, 'config', 'user.name', 'Fixture')
        self.git(self.remote, 'config', 'user.email', 'fixture@example.invalid')
        self.file = self.remote / 'source.txt'
        self.file.write_text('common\n')
        self.commit('common')
        self.base = self.commit('base', 'base\n')
        self.git(self.remote, 'checkout', '-q', 'HEAD~1')
        self.head = self.commit('head', 'head\n')
        self.git(self.remote, 'update-ref', 'refs/pull/7/head', self.head)
        self.work = self.root / 'checkout'

    def git(self, cwd, *args):
        p = subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.strip()

    def commit(self, message, content=None):
        if content is not None:
            self.file.write_text(content)
        self.git(self.remote, 'add', '.')
        self.git(self.remote, 'commit', '-qm', message)
        return self.git(self.remote, 'rev-parse', 'HEAD')

    def checkout(self, remote=None, head=None, base=None):
        return dispatch.prepare_review_checkout(
            self.work, str(remote or self.remote), 7, head or self.head, base or self.base)

    def test_empty_directory_and_repeated_attempt(self):
        self.work.mkdir()
        self.assertIsNone(self.checkout())
        self.assertIsNone(self.checkout())
        self.assertEqual(self.git(self.work, 'rev-parse', 'HEAD'), self.head)

    def test_failed_remote_then_valid_retry(self):
        self.assertEqual(self.checkout(self.root / 'missing')['status'], 'BLOCKED_GIT_FETCH')
        self.assertTrue((self.work / '.git').is_dir())
        self.assertIsNone(self.checkout())

    def test_base_head_three_dot_diff_available(self):
        self.assertIsNone(self.checkout())
        self.assertEqual(self.git(self.work, 'diff', '--name-only', f'{self.base}...{self.head}'), 'source.txt')
        self.assertEqual(self.git(self.work, 'rev-parse', '--is-shallow-repository'), 'false')

    def test_foreign_files_preserved(self):
        self.work.mkdir()
        foreign = self.work / 'keep'
        foreign.write_text('untouched')
        self.assertIsNotNone(self.checkout())
        self.assertEqual(foreign.read_text(), 'untouched')
        self.assertFalse((self.work / '.git').exists())

    def test_mismatched_head_refused(self):
        self.assertIsNone(self.checkout())
        self.git(self.work, 'checkout', '-q', '--detach', self.base)
        self.assertEqual(self.checkout()['status'], 'BLOCKED_SHA_MISMATCH')
        self.assertEqual(self.git(self.work, 'rev-parse', 'HEAD'), self.base)

    def test_dirty_and_untracked_files_refused(self):
        self.assertIsNone(self.checkout())
        for name in ('source.txt', 'untracked'):
            with self.subTest(name=name):
                path = self.work / name
                path.write_text('preserve')
                self.assertIsNotNone(self.checkout())
                self.assertEqual(path.read_text(), 'preserve')
                if name == 'source.txt':
                    path.write_text('head\n')

    def test_remote_pr_branch_must_match_pin(self):
        self.git(self.remote, 'update-ref', 'refs/pull/7/head', self.base)
        self.assertEqual(self.checkout()['status'], 'BLOCKED_SHA_MISMATCH')

    def test_missing_base_refused(self):
        self.assertEqual(self.checkout(base='f' * 40)['status'], 'BLOCKED_GIT_FETCH')

    def test_review_rejects_invalid_base_before_checkout(self):
        for base in ({'sha': self.base, 'repo': {'full_name': 'foreign/repo'}},
                     {'sha': 'invalid', 'repo': {'full_name': dispatch.REPO}}, {}):
            with self.subTest(base=base), patch.object(dispatch, 'ROOT', self.root), patch.object(dispatch, 'github_json', return_value=({
                'state': 'open', 'head': {'sha': self.head, 'repo': {'full_name': dispatch.REPO}},
                'base': base}, '')):
                self.assertEqual(dispatch.review({'pr_number': 7})['status'], 'BLOCKED_PR_ORIGIN_OR_SHA')

    def test_legacy_shallow_checkout_gets_comparison_history(self):
        self.work.mkdir()
        self.git(self.work, 'init', '-q')
        self.git(self.work, 'fetch', '-q', '--depth=1', str(self.remote),
                 'refs/pull/7/head')
        self.git(self.work, 'checkout', '-q', '--detach', 'FETCH_HEAD')
        self.assertEqual(self.git(self.work, 'rev-parse', '--is-shallow-repository'), 'true')
        self.assertIsNone(self.checkout())
        self.assertEqual(self.git(self.work, 'diff', '--name-only',
                                  f'{self.base}...{self.head}'), 'source.txt')

    def test_review_calls_helper_on_every_attempt_with_approved_origin(self):
        (self.root / 'state' / 'codex').mkdir(parents=True)
        pr = {'state': 'open',
              'head': {'sha': self.head, 'repo': {'full_name': dispatch.REPO}},
              'base': {'sha': self.base, 'repo': {'full_name': dispatch.REPO}}}
        error = {'status': 'BLOCKED_GIT_FETCH', 'detail': 'fixture'}
        with patch.object(dispatch, 'ROOT', self.root), \
                patch.object(dispatch, 'github_json', return_value=(pr, '')), \
                patch.object(dispatch, 'prepare_review_checkout', return_value=error) as prepare:
            for _ in range(2):
                self.assertEqual(dispatch.review({'pr_number': 7}), error)
            self.assertEqual(prepare.call_count, 2)
            self.assertEqual(prepare.call_args.args[1:],
                             ('https://github.com/' + dispatch.REPO + '.git',
                              7, self.head, self.base))
