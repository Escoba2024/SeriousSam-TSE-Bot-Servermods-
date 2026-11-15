# Existing Dedicated powerup flag: isolated OFF/ON contrast

Status: approved narrow Root ruling, offline preparation only. No native test,
new DLL, live change, automatic sequence or retry.

The two independent cases use the existing Dedicated `fe4a77bd1eae15a25cfeb67cf5dfdd6643cba59661f2ca3e99467a9fb15b06e0`,
the existing 048 bot DLL `ec820d0461313c41fec2b477f57109310d3c71a77b4423955ac69f3807566530`,
and the unchanged original observer. Dedicated and bot roles remain separate.
Only `dev_bRemoveDamageAndInvisibility=0` versus `=1`, assigned in the sealed
private startup template before NewGame, differs in gameplay configuration.
Both cases retain Red Station, Hard2, eight own bots, one Original at slot1,
20FPS observer, diagnostics0, 600 seconds and all inherited inputs, sampling,
V3 memory/attempt predicates, host limits, locks, normal closes and complete
transaction restoration. No original dedicated control is repeated.

Erratum to the earlier private static memo: its `eightDemon` wording is wrong.
The actual frozen 048 canonical config selects profile7 for all four locals;
048 `bot_profile.h:399–429` maps it to tier5/persona4/BOT-Expert-Rifle and
BuildRosterProfile passes those values unchanged. The frozen version-bound
check_tiers requires tier5/marksman. Settings preset2 is retained. Neither arm
changes these profiles to Arena DEMON.

Source feasibility is limited: DevPowerupFilter performs its census and only
server/non-demo startup removal of types0/2 after StartPeerToPeer and before
local player setup. This does not establish its network/CRC effects, later
spawn treatment or the cause of live Dev bad syncs. Both arms require one
ordered before/removed/after census with the effective invocation flag,
nonzero initial affected items, exact OFF no-op or ON removal, and preservation
of all unaffected counts. Missing, ambiguous or unexercised evidence fails
the contrast; it never becomes a negative causal result.

The reviewed 048/Red600 parent manifest is
`91a3f9c02891b39512ca25484fb4fd82d41f650ef9b953c1d941e93b8c3e04f6`.
Only the new fixed option check, own namespaces/disabled gate, server loaded
hash, server DLL staging, server InventoryReader GameMP hash, startup flag and
bounded census recording/checks may alter its controller. Exact whole-source
inversion must recover the parent. Engine/Entities readers, vanilla originals,
configuration/Nav, finalizer and all other source files remain byte identical.
The existing dedicated manifest `b3bbd208089a41271a518142de707429732c860761e8a2c4188efdc107b0bb7f`
supplies all49 source +30 overlay +manifest +DLL pins, freshly checked.

Two passing windows only bound this scenario. An ON-only failure can support
flag association in this local case, not a Destroy/CRC cause without first
divergent-state evidence. OFF failure weakens a filter-only hypothesis.
The inherited limited status, functional_pass=False and qualified=False stay
unchanged. No result triggers live promotion.
