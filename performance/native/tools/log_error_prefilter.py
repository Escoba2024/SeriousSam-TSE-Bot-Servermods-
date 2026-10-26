"""Conservative prefilter for the current Retail runtime-error regular expression.

This module is deliberately standalone: it does not import or change the native
qualification sources.  It can only prefilter the exact current expression used
by ``qualify_bot_sessions.runtime_error``.  Every other pattern or flag set is
searched by the caller-supplied compiled pattern without a prefilter.

The helper never reads a file and retains no text, offset, size, or append state.
A caller must continue to read the complete log on every tick and pass that
complete string to :meth:`RuntimeErrorMatcher.search`.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Match, Pattern

# Copied verbatim from native-tools/qualify_integrated_wine.py's q.BAD.pattern,
# followed verbatim by the extra alternative in
# native-tools/qualify_bot_sessions.py's runtime_error().
BAD_PATTERN = (
    r"Identifier '(?!sam_strTechTestLevel')[^']+' is not declared"
    r"|SYNCBAD"
    r"|Too many bad syncs"
    r"|CRC check failed"
    r"|Cannot load script"
    r"|[Uu]nknown symbol"
    r"|[Uu]nrecognized symbol"
    r"|Permission denied"
    r"|[Ff]atal [Ee]rror"
)
RUNTIME_ERROR_PATTERN = BAD_PATTERN + r"|FatalError:"

# re.compile(<str>) and re.search(<str>, <str>) use this default for the
# current source expression.  A pattern with any other flags must not be
# prefiltered because its accepted literals may differ.
_DEFAULT_FLAGS = re.compile(RUNTIME_ERROR_PATTERN).flags

# Each fixed branch has at least one exact, case-sensitive literal below.  The
# [Uu] and [Ff]/[Ee] branches need every permitted spelling rather than a
# case-folded test, so they preserve the source regex's case semantics.
_FIXED_BRANCH_MARKERS = (
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
_IDENTIFIER_PREFIX = "Identifier '"
_ALLOWED_IDENTIFIER_PREFIX = "sam_strTechTestLevel'"


@dataclass
class MatcherCounters:
    """Observable counts for a local benchmark; they have no acceptance role."""

    calls: int = 0
    prefilter_rejections: int = 0
    full_searches: int = 0
    fallback_searches: int = 0


class RuntimeErrorMatcher:
    """Call a supplied compiled regex, using a safe prefilter only when exact.

    ``search`` returns precisely the supplied pattern's ``Match`` object or
    ``None``.  For a supported pattern, the prefilter may reject only when no
    source-regex alternative can match.  Any possible alternative still calls
    ``pattern.search(text)``; this retains the original earliest-match choice,
    positions, groups, and all regex behavior.
    """

    def __init__(self, pattern: Pattern[str]) -> None:
        if not isinstance(pattern, re.Pattern):
            raise TypeError("pattern must be a compiled str regular expression")
        self.pattern = pattern
        self.fast_path_enabled = _is_exact_runtime_error_pattern(pattern)
        self.counters = MatcherCounters()

    def search(self, text: str) -> Match[str] | None:
        """Search one complete current log text, with fail-closed delegation.

        Non-string input is passed straight to the original pattern.  This keeps
        its native TypeError behavior rather than inventing prefilter semantics.
        """

        self.counters.calls += 1
        if not self.fast_path_enabled or not isinstance(text, str):
            self.counters.fallback_searches += 1
            return self.pattern.search(text)

        if not _known_pattern_may_match(text):
            self.counters.prefilter_rejections += 1
            return None

        self.counters.full_searches += 1
        return self.pattern.search(text)

    __call__ = search


def make_runtime_error_matcher(
    pattern: Pattern[str] | None = None,
) -> RuntimeErrorMatcher:
    """Build a matcher for the current runtime-error expression.

    Passing the production expression compiled by its caller makes the helper
    call that same compiled pattern whenever a match remains possible.  Omitting
    ``pattern`` creates an equivalent default-flag compiled expression for
    isolated tests or local benchmarks.
    """

    return RuntimeErrorMatcher(
        re.compile(RUNTIME_ERROR_PATTERN) if pattern is None else pattern
    )


def _is_exact_runtime_error_pattern(pattern: Pattern[str]) -> bool:
    """Allow the fast path only for the exact source expression and flags."""

    return (
        isinstance(pattern.pattern, str)
        and pattern.pattern == RUNTIME_ERROR_PATTERN
        and pattern.flags == _DEFAULT_FLAGS
    )


def _known_pattern_may_match(text: str) -> bool:
    """Return False only after ruling out every current regex alternative.

    ``in`` and ``find`` use CPython's native string-search implementation.  No
    text is normalized, lower-cased, split into lines, or retained between calls.
    """

    if any(marker in text for marker in _FIXED_BRANCH_MARKERS):
        return True
    return _identifier_branch_may_match(text)


def _identifier_branch_may_match(text: str) -> bool:
    """Conservatively screen the negative-lookahead Identifier alternative.

    Only the exact excluded name immediately followed by its closing quote,
    ``sam_strTechTestLevel'``, cannot match that alternative.  Every other
    ``Identifier '`` occurrence delegates to the original regex, including
    malformed, quoted, unicode, or newline-containing text.  That conservatism
    is necessary because ``[^']+`` is unbounded and may cross line boundaries.
    """

    position = text.find(_IDENTIFIER_PREFIX)
    while position != -1:
        after_prefix = position + len(_IDENTIFIER_PREFIX)
        if not text.startswith(_ALLOWED_IDENTIFIER_PREFIX, after_prefix):
            return True
        # Advance one code point to preserve a possible later/overlapping
        # occurrence without parsing the identifier itself.
        position = text.find(_IDENTIFIER_PREFIX, position + 1)
    return False


__all__ = [
    "BAD_PATTERN",
    "RUNTIME_ERROR_PATTERN",
    "MatcherCounters",
    "RuntimeErrorMatcher",
    "make_runtime_error_matcher",
]
