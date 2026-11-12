"""Read-only stabilization around an existing STRICT native backend identity check.

Call only after an authorized own launch, under the caller's existing exclusive
lock. This module calls only ``backend.identity(role, unit)`` and ``backend.same``;
it never launches, controls, closes, signals, or changes a process. It does not
replace namespace/module/hash or gameplay qualification gates.

Integration::

    receipt = wait_native_identity(B, role, unit)
    records[role]['identity'] = receipt.identity
    # Archive dataclasses.asdict(receipt), then run existing remaining guards.

A failed wait grants NO cleanup/control authority. Preserve the exception evidence
and use the existing strict partial-launch cleanup policy. Revalidate identity
before later control: these observations are not an everlasting process lease.

The monotonic deadline is checked before/after synchronous backend reads. A backend
call must itself be bounded: this helper cannot interrupt a blocked read and never
accepts a late result. Clock/sleep injection is for offline tests, not runtime policy.
"""
from dataclasses import dataclass
import math
import time


class IdentityWaitTimeout(TimeoutError):
    def __init__(self, evidence):
        self.evidence = evidence
        super().__init__(f"strict native identity did not stabilize: {evidence}")


class IdentityMismatch(RuntimeError):
    """A stale/changed/malformed identity is a terminal failure, never a retry."""


@dataclass(frozen=True)
class IdentityReceipt:
    identity: tuple[int, int]
    attempts: int
    stable_samples: int
    stable_seconds: float
    elapsed_seconds: float
    transient_errors: int


def wait_native_identity(backend, role, unit, *, timeout=15.0, stable_for=.3,
                         interval=.1, min_samples=3,
                         monotonic=time.monotonic, sleep=time.sleep):
    """Return only consecutive identical, same()-valid strict identity samples.

    AssertionError/FileNotFoundError/ProcessLookupError from the two backend reads
    are transient until the deadline. They reset the consecutive stability period,
    never the first successfully read PID/start pin. Other exceptions propagate.
    ``same`` must return the actual boolean True. A changed PID/start, stale same(),
    or malformed identity aborts immediately, even if a replacement later settles.
    """
    for name, value in (('timeout', timeout), ('stable_for', stable_for), ('interval', interval)):
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{name} must be positive and finite')
    if timeout > 60 or stable_for >= timeout or interval > timeout:
        raise ValueError('require stable_for < timeout <= 60 and interval <= timeout')
    if type(min_samples) is not int or min_samples < 2:
        raise ValueError('min_samples must be an integer >= 2')

    started = monotonic()
    deadline = started + timeout
    pinned = None
    stable_since = None
    samples = attempts = transient_errors = 0
    last_transient = None

    def timed_out(now):
        return IdentityWaitTimeout(dict(role=role, unit=unit, identity=pinned,
            attempts=attempts, stable_samples=samples,
            elapsed_seconds=now-started, required_stable_seconds=stable_for,
            timeout_seconds=timeout, transient_errors=transient_errors,
            last_transient=last_transient))

    while True:
        now = monotonic()
        if now >= deadline:
            raise timed_out(now)
        attempts += 1
        valid = False
        try:
            observed = backend.identity(role, unit)
            if not (isinstance(observed, (tuple, list)) and len(observed) == 2
                    and all(type(x) is int for x in observed)
                    and observed[0] > 1 and observed[1] > 0):
                raise IdentityMismatch(f'invalid strict identity for {role}/{unit}: {observed!r}')
            observed = tuple(observed)
            if pinned is None:
                pinned = observed
            elif observed != pinned:
                raise IdentityMismatch(f'identity changed for {role}/{unit}: expected={pinned}, observed={observed}')
            if backend.same(pinned) is not True:
                raise IdentityMismatch(f'identity no longer same for {role}/{unit}: {pinned}')
            valid = True
        except (AssertionError, FileNotFoundError, ProcessLookupError) as error:
            transient_errors += 1
            last_transient = f'{type(error).__name__}: {error}'[:512]
            stable_since = None
            samples = 0

        now = monotonic()
        if now >= deadline:
            raise timed_out(now)
        if valid:
            if stable_since is None:
                stable_since = now
            samples += 1
            stable_seconds = now-stable_since
            if samples >= min_samples and stable_seconds >= stable_for:
                return IdentityReceipt(pinned, attempts, samples, stable_seconds,
                                       now-started, transient_errors)
        sleep(min(interval, deadline-now))
