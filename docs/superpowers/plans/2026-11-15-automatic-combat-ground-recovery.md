# Automatic combat ground recovery implementation

Status: offline implementation and focused verification complete; native unbuilt/unqualified. Use executing-plans and TDD; Root independent review/integration,
no delegation. Spec: `../specs/2026-11-15-automatic-combat-ground-recovery.md`.

1. Add opt-in Bridge behavior fixtures via a SFINAE compatibility call; current
   production fallback remains default false. Execute only the relevant normal
   Bridge suite for a real failure showing missing combat recovery. Cover actual
   Driver-trigger helper separately when present, without weakening old contracts.
2. Add smallest same-tick combat metadata pin and production request helper;
   extend SafeMotion with default-false flag and wire actual Driver call. Existing
   ground geometry/support/cast predicates and cecil_motion remain unchanged.
   New observation authority does not mean Nav ownership, goal/hint mutation,
   FlightAccepted or a blanket speed cap on ordinary combat.
3. Add all adversarial controls and interface compatibility for actual Driver-call
   contract. Run one relevant full normal Bridge GREEN plus focused action-call
   regression. Stop on unexpected failures; no predicate loosening, no repeated
   parent loops. ASan only for a new memory defect.
4. Save real RED/GREEN output0600, source/call/Core-of-motion hashes and exact
   resulting denominators. Update spec/status/report, commit only the claim and
   hand off disabled/unbuilt source. Native026 episode cause remains unresolved.

Before production: Root has been told that time-only existing stamps do not bind
reference/world changes; the proposed combat-only metadata pin addresses that gap
without adding casts. All CPU jobs stop on Root STATICONLY.

Root rulings: combat-only metadata pin accepted, including map serial and prior
validated reference ID; never dereference an unvalidated retained pointer. The
single productive Capturecall is explicitly inversed separately from passive
diagnostic additions in the historical source proof. ActionNative10-argument
stub/actual helper extraction is in scope. Its existing mandatory ASan/UBSan is
an explicit Root exception for exactly one targeted Caller regression; no new
CLI/default change and no sanitizer Bridge repeat.

Review correction: negative map serial was reproducibly accepted before Capture
and by Fresh when both negative serials matched. Four focused checks produced
three real failures before the combat-only fix, then zero failures. Both new
combat boundaries now deny map<0; Fresh additionally checks the resolved current
reference ID. Legacy Nav predicates are unchanged. Final relevant normal Bridge:
3663 checks/0 failures. Preserve the earlier3659/0 checkpoint and the single
existing ActionNative ASan/UBSan PASS as pre-review-fix evidence; no repeat series.
