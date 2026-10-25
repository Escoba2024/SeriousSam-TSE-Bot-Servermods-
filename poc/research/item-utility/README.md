# Item-Utility-AI (Prototyp, enginefrei)

**Stand:** 25.10.2026 · **Agent 5** · Basis `main` @ `107d28a`
**Lizenz:** GPL-2.0-only (SPDX-Header in jeder Datei)
**Dokumentation:** `docs/research/item-utility/`

Beantwortet genau eine Frage: **Welches Item soll der Bot suchen, und warum?**
Navigation (WaypointGraph, A*, Pathfinding) ist **nicht** Teil dieses Prototyps — sie kommt später
über `include/navigation_interface.h` vom Navigation-Agenten.

---

## Bauen und prüfen

```bash
cd poc/research/item-utility
make test     # drei Testbinaries
make bench    # CPU-Benchmark (Entscheidungsschicht)
make clean
```

Voraussetzungen: C++17, `g++`/`clang++`, sonst nichts. Kein Retail, kein Windows, kein SDK, kein
Netzwerk. Der Adapter-Test liest `poc/botcore/bot_loadout.h` und `bot_profile.h` (nur lesend).

## Ergebnis (Linux-Sandbox, g++ 13, `-O2`, 25.10.2026)

| Binary | Inhalt | Ergebnis |
|---|---|---|
| `test_item_utility` | Entscheidungssemantik, Abbrüche, Hysterese, Kooldowns, Skill, Persönlichkeit, Determinismus, Nav-Seam, CPU | **378 Checks, 0 Fehler** |
| `test_scoring_terms` | jede Utility-Term-Formel, Bänder, Property-Sweep über 4 000 Zufallswelten | **91 711 Checks, 0 Fehler** |
| `test_botcore_adapter` | Waffen-Score bitgleich zu `botcore::ScoreWeapon` (40 446 Vergleiche, max. Diff 0), Masken-/Profil-Mapping | **401 Checks, 0 Fehler** |
| `bench_item_utility` | 0/6/12/24/64 Items, mit/ohne Nav-Sink | **BENCH PASS** |

```
idle (0 Items)    0,160 µs/Tick
sparse (6)        0,545 µs/Tick
typical (12)      0,722 µs/Tick
dense (24)        1,177 µs/Tick   (0,002 % des 20-Hz-Ticks)
worst case (64)   3,305 µs/Tick   ≈ 0,052 µs pro Item-Bewertung
+ Nav-Sink        1,190 µs/Tick   (+0,013 µs)
```

> Diese Zahlen messen **nur** die enginefreie Entscheidung. Sie sagen **nichts** über GameMP.dll,
> einen Bot-Client-Prozess, Retail 1.07 oder die Hetzner-Flotte aus.

## Dateien

```
include/item_types.h             Grundtypen, Item-Kategorien, Aktions-/Begründungs-Vokabular
include/item_snapshot.h          synthetischer Weltzustand + fail-closed-Validierung
include/item_weapons.h           Waffentabelle (Form identisch zu botcore::ScoreWeapon)
include/item_profile.h           Skill-, Persönlichkeits- und Tuning-Modell
include/item_scoring.h           Utility-Funktion (Bedarf × Seltenheit × Nutzen × …)
include/item_planner.h           Ziel-Zustandsmaschine, Hysterese, Kooldowns, Abbrüche
include/navigation_interface.h   Vertrag zum Navigation-Agenten + skriptbares Testdouble
include/botcore_adapter.h        Mapping zur bestehenden Human-KI (Integration, ungenutzt)
tests/                           drei Testbinaries
benches/                         CPU-Benchmark
```

## Designregeln

1. **Enginefrei**: keine Engine-Typen, keine Rays, kein I/O, keine Allokation in `Step`.
2. **Fail closed**: ungültiger Snapshot ⇒ `kInvalidWorld`, kein Ziel.
3. **Deterministisch**: Seed nur für Gleichstände und die „flaky"-Stimmung; identische Eingaben ⇒
   bitgleiche Entscheidungsfolge (getestet).
4. **Keine Navigation**: kein Pfad, kein Wegpunkt, keine Richtung; nur ein Ziel + Zeitfenster.
5. **Skill ≠ Persönlichkeit**: Skill beschreibt Entscheidungsqualität, Persönlichkeit Präferenzen;
   blockweise orthogonal und getestet.

## Was hier bewusst **nicht** passiert

- keine Änderung an `poc/botcore/`, `poc/patch/`, `poc/release/`, `poc/scripts/`, `poc/navigation-lab/`;
- kein Retail-/Serverbetrieb, keine DLL, keine Netzwerkänderung;
- keine Cecil-Codeübernahme (nur Ideen, siehe `docs/research/item-utility/…cecilbotmod-item-logik-analyse.md`).

## Abnahme-Status

| Prüfung | Status |
|---|---|
| Offline-Unit-/Akzeptanztests | **bestanden** (in dieser Sitzung ausgeführt) |
| CPU-Benchmark (Entscheidungsschicht) | **bestanden** |
| Adapter-Gleichheit mit `botcore` | **bestanden** (nur lesend geprüft) |
| MSVC-Build | **NOT_TESTED** |
| Retail-1.07-Runtime, Sync-Gate | **NOT_TESTED** (folgt in Phase II/III des Integrationsplans) |
