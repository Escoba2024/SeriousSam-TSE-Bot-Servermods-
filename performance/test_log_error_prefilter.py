"""TDD regression tests for log_error_prefilter.

All strings in this file are synthetic source-only fixtures.  They are not
copied from, sampled from, or a benchmark of native/Hetzner logs.
"""

from __future__ import annotations

import random
import re
import unittest

from log_error_prefilter import RUNTIME_ERROR_PATTERN, make_runtime_error_matcher


class LogErrorPrefilterTests(unittest.TestCase):
    def assert_same_search(self, pattern: re.Pattern[str], text: str) -> None:
        """Require the helper's result to retain all observable match details."""

        expected = pattern.search(text)
        matcher = make_runtime_error_matcher(pattern)
        actual = matcher.search(text)
        if expected is None:
            self.assertIsNone(actual)
            return
        self.assertIsNotNone(actual)
        assert actual is not None  # narrows for static readers
        self.assertIs(actual.re, pattern)
        self.assertEqual(actual.span(), expected.span())
        self.assertEqual(actual.group(), expected.group())
        self.assertEqual(actual.groups(), expected.groups())
        self.assertEqual(actual.groupdict(), expected.groupdict())

    def test_every_current_error_alternative(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        alternatives = (
            "Identifier 'unregistered_symbol' is not declared",
            "SYNCBAD",
            "Too many bad syncs",
            "CRC check failed",
            "Cannot load script",
            "Unknown symbol",
            "unknown symbol",
            "Unrecognized symbol",
            "unrecognized symbol",
            "Permission denied",
            "Fatal Error",
            "Fatal error",
            "fatal Error",
            "fatal error",
            "FatalError:",
        )
        for alternative in alternatives:
            with self.subTest(alternative=alternative):
                text = "synthetic prefix :: " + alternative + " :: suffix"
                self.assert_same_search(pattern, text)

    def test_allowed_identifier_and_near_miss_behavior(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        allowed = "Identifier 'sam_strTechTestLevel' is not declared"
        allowed_extension = "Identifier 'sam_strTechTestLevel_more' is not declared"
        near_misses = (
            "Identifier 'sam_strTechTestLeve' is not declared",
            "Identifier 'Sam_strTechTestLevel' is not declared",
            "Identifier 'sam_strTechTestLeveL' is not declared",
        )

        matcher = make_runtime_error_matcher(pattern)
        self.assertIsNone(matcher.search(allowed))
        self.assertIsNotNone(matcher.search(allowed_extension))
        self.assertEqual(matcher.counters.prefilter_rejections, 1)
        self.assertEqual(matcher.counters.full_searches, 1)
        self.assert_same_search(pattern, allowed_extension)

        for text in near_misses:
            with self.subTest(near_miss=text):
                self.assert_same_search(pattern, text)

    def test_allowed_identifier_does_not_hide_a_later_identifier_match(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        text = (
            "Identifier 'sam_strTechTestLevel' is not declared; then "
            "Identifier 'actual_problem' is not declared"
        )
        self.assert_same_search(pattern, text)

    def test_allowed_name_requires_immediate_closing_quote_for_exemption(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        for text in (
            "Identifier 'sam_strTechTestLevel_more' is not declared",
            "Identifier 'sam_strTechTestLevel\nnext' is not declared",
            "Identifier 'sam_strTechTestLevelλ' is not declared",
        ):
            with self.subTest(text=text):
                self.assert_same_search(pattern, text)

    def test_arbitrary_quotes_newlines_unicode_and_constructed_chunks(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        cases = (
            "Identifier 'snowman=☃\nnext=λ' is not declared",
            "Identifier 'one' trailing quote ' is not declared",
            "ordinary text Identifier 'unterminated only",
            "head-" + "Fatal" + "Error:" + "-tail",
            "head-" + "Too many " + "bad syncs" + "-tail",
        )
        for text in cases:
            with self.subTest(text=text):
                self.assert_same_search(pattern, text)

    def test_explicit_fatalerror_alternative(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        text = "prefix FatalError: intentional synthetic suffix"
        self.assert_same_search(pattern, text)

    def test_earliest_span_and_groups_are_from_original_search(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        text = (
            "start fatal error appears first; later SYNCBAD; later "
            "Identifier 'unknown' is not declared; later FatalError:"
        )
        expected = pattern.search(text)
        self.assertIsNotNone(expected)
        assert expected is not None
        matcher = make_runtime_error_matcher(pattern)
        actual = matcher.search(text)
        self.assertIsNotNone(actual)
        assert actual is not None
        self.assertEqual(actual.span(), expected.span())
        self.assertEqual(actual.group(), "fatal error")
        self.assertEqual(actual.groups(), expected.groups())
        self.assertEqual(actual.groupdict(), expected.groupdict())
        self.assertEqual(matcher.counters.full_searches, 1)

    def test_no_possible_marker_returns_none_without_full_regex_search(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        matcher = make_runtime_error_matcher(pattern)
        text = "synthetic ordinary status: player joined and retained unicode λ"
        self.assertIsNone(matcher(text))
        self.assertEqual(matcher.counters.calls, 1)
        self.assertEqual(matcher.counters.prefilter_rejections, 1)
        self.assertEqual(matcher.counters.full_searches, 0)
        self.assertEqual(matcher.counters.fallback_searches, 0)

    def test_incomplete_nonallowed_identifier_still_uses_original_regex(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        matcher = make_runtime_error_matcher(pattern)
        text = "Identifier 'not_closed_or_declared"
        self.assertIsNone(matcher.search(text))
        self.assertEqual(matcher.counters.full_searches, 1)
        self.assertEqual(matcher.counters.prefilter_rejections, 0)

    def test_ignorecase_and_unknown_patterns_always_fallback(self) -> None:
        ignorecase = re.compile(RUNTIME_ERROR_PATTERN, re.IGNORECASE)
        ignorecase_matcher = make_runtime_error_matcher(ignorecase)
        lower_case_only = "diagnostic says syncbad"
        self.assert_same_search(ignorecase, lower_case_only)
        self.assertIsNotNone(ignorecase_matcher.search(lower_case_only))
        self.assertFalse(ignorecase_matcher.fast_path_enabled)
        self.assertEqual(ignorecase_matcher.counters.fallback_searches, 1)

        unknown = re.compile(r"only-an-unknown-pattern-can-find-this")
        unknown_matcher = make_runtime_error_matcher(unknown)
        text = "prefix only-an-unknown-pattern-can-find-this suffix"
        self.assertIsNotNone(unknown_matcher.search(text))
        self.assertFalse(unknown_matcher.fast_path_enabled)
        self.assertEqual(unknown_matcher.counters.fallback_searches, 1)

    def test_other_flags_fallback_even_if_pattern_text_matches(self) -> None:
        flagged = re.compile(RUNTIME_ERROR_PATTERN, re.MULTILINE)
        matcher = make_runtime_error_matcher(flagged)
        self.assert_same_search(flagged, "ordinary text with no known markers")
        self.assertFalse(matcher.fast_path_enabled)
        self.assertIsNone(matcher.search("ordinary text with no known markers"))
        self.assertEqual(matcher.counters.fallback_searches, 1)

    def test_same_size_rewritten_complete_text_is_scanned_every_call(self) -> None:
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        matcher = make_runtime_error_matcher(pattern)
        first = "status=green; tick=001; no native diagnostic"
        replacement = "status=green; tick=001; SYNCBAD diagnostic!!"
        self.assertEqual(len(first), len(replacement))
        self.assertIsNone(matcher.search(first))
        second = matcher.search(replacement)
        self.assertIsNotNone(second)
        assert second is not None
        self.assertEqual(second.group(), "SYNCBAD")
        self.assertEqual(matcher.counters.calls, 2)
        self.assertEqual(matcher.counters.prefilter_rejections, 1)
        self.assertEqual(matcher.counters.full_searches, 1)

    def test_fixed_seed_synthetic_fuzz_matches_original_regex(self) -> None:
        # Source-only fixture generation; it is neither native log data nor a
        # benchmark assertion.  Fixed seed makes a semantic regression stable.
        rng = random.Random(20261026)
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        inserts = (
            "",
            "SYNCBAD",
            "unknown symbol",
            "FatalError:",
            "Identifier 'sam_strTechTestLevel' is not declared",
            "Identifier 'fuzz_name' is not declared",
            "Identifier 'α\nβ' is not declared",
        )
        alphabet = "abcXYZ 0123_'\nλ☃:-"
        for _ in range(250):
            base = "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, 160)))
            point = rng.randrange(len(base) + 1)
            text = base[:point] + rng.choice(inserts) + base[point:]
            self.assert_same_search(pattern, text)

    def test_large_synthetic_benign_corpus_is_source_only(self) -> None:
        # This deliberately contains no native/Hetzner log material and makes
        # no performance claim.  It checks only that a whole supplied string is
        # safely rejected when none of the necessary markers occurs.
        pattern = re.compile(RUNTIME_ERROR_PATTERN)
        matcher = make_runtime_error_matcher(pattern)
        corpus = ("source-only benign progress λ line 000000\n" * 20_000)
        self.assertGreater(len(corpus), 500_000)
        self.assertIsNone(matcher.search(corpus))
        self.assertEqual(matcher.counters.prefilter_rejections, 1)
        self.assertEqual(matcher.counters.full_searches, 0)


if __name__ == "__main__":
    unittest.main()
