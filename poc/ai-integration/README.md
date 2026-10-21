# `poc/ai-integration/` — review copy of the profile-driven bot AI

**Status: unqualified candidate source.** Nothing in this directory is built,
tested against Retail 1.07, or part of the qualified `61DC27E0…` DLL.

## Why this directory exists

`poc/release/gamemp/**` is byte-pinned to the qualified candidate
(`tools/Verify-SourceProvenance.py`, `docs/reports/2026-10-12-source-verification.json`).
Changing `BotDriver.cpp` there would destroy that provenance, so the AI change
is delivered the same way as patches `0001`–`0007`:

| Artefakt | Zweck |
|---|---|
| `poc/patch/0008-gamemp-human-bot-ai.patch` | die eigentliche Änderung (+181 / −3 Zeilen) |
| `poc/ai-integration/gamemp/BotDriver.cpp` | dieselbe Änderung als vollständige Datei zum Lesen/Diffen |

Die beiden müssen identisch sein. `poc/botcore/verify_patch.py` beweist das:

```bash
python3 poc/botcore/verify_patch.py
# PATCH VERIFY PASS: 0008 applies cleanly and matches the integration copy
```

## Anwenden

```bash
cd <checkout>
git apply --check poc/patch/0008-gamemp-human-bot-ai.patch
git apply         poc/patch/0008-gamemp-human-bot-ai.patch
for h in bot_profile bot_perception bot_aim bot_loadout bot_human; do
  cp "poc/botcore/$h.h" poc/release/gamemp/
done
```

Danach wie gewohnt mit SE1-ModSDK `aa7869c2c2c4db0562281814d0ac3784e6b9d6f0`,
Includes `94ff8cd0e63941f8601294350b616472f772ed51`, VS2022/v143 und Windows SDK
10.0.19041.0 bauen. `Game.cpp`, `Game.vcxproj` und alle anderen GameMP-Dateien
bleiben unverändert.

Neue Header in `Game.vcxproj` einzutragen ist optional — sie werden über
`#include` gefunden und erscheinen dann nur nicht im Solution Explorer.

## Verhalten

Standardmäßig (ohne INI-Änderung) ist das Verhalten **identisch** zum
qualifizierten Kandidaten: `bot_bHumanAI` ist `0`, der neue Zweig wird nie
betreten. Eingeschaltet wird er über `poc/scripts/Phase1HumanAI.ini`.

Wichtige Schalter:

| Symbol | Standard | Bedeutung |
|---|---|---|
| `bot_bHumanAI` | `0` | Meisterschalter für den profilgesteuerten Pfad |
| `bot_iRosterOffset` | `0` | `0` für Client A, `4` für Client B (Acht-Bot-Roster) |
| `bot_iProfile0..3` | `-1` | optionaler Roster-Index pro Slot; `-1` = `Offset + Slot` |
| `bot_iProfileSeed` | `20261020` | Basis-Seed; Slot/Stufe/Persönlichkeit werden eingemischt |
| `bot_fStrafeScale` | `0` | laterale Bewegung; **0 lassen**, bis nativ geprüft |

## Tests

```bash
cd poc/botcore
make test     # 555 Offline-Checks der Entscheidungslogik
make smoke    # kompiliert den echten Integrationsblock gegen Stubs
make bench    # Entscheidungskosten pro Bot und Tick
```

Details, Grenzen und der exakte nächste Schritt stehen in
`docs/reports/2026-10-20-bot-ai-profiles-and-perception.md`.
