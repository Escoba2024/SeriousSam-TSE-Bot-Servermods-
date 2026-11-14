# A4: begrenzte Healthconnector-Kontinuität (portabel)

Status: lokaler Produktionsvorschlag mit SDK107-Regressionen; keine DLL und
keine neue native Retail-Abnahme. Root allein integriert und startet Runtime.
Der historische native Ausfall und offene A-Ziele bleiben unverändert offen.

## Ursache und Reichweite

Der vorangehende Bericht `2026-11-14-a4-item-connector-sdk107-repro.md`
belegt mit tatsächlichem BotSupplyTick und CecilNavigator einen reproduzierbaren
Übergangsfehler: nach echter Navankunft am gewöhnlichen Healthterminal führt
das Verlassen seiner 2m-Sphäre wieder zum Navpunkt statt zum noch gebundenen,
5–6m entfernten Item. Beide Richtungen ergaben im unveränderten Code sechs
Fehler bei 2942 Checks. Dies ist keine vollständige Ursachenattribution des
beobachteten langen unbewaffneten nativen Lebens: Gründe für nicht verfügbare
Waffen und Healthfreigaben bei Diagnostics0 sind weiterhin unbekannt. Im
nativen Leben stieg HP teilweise; „keine Healthpickups“ wäre unbelegt.

## Produktionsänderung

`BotSupplyNative.h` merkt ausschließlich eine gewöhnliche Health-Endphase,
die erst nach echter `move.arrived`-Ankunft und frischem Erfolg des bestehenden
Connectorcasts entsteht. Die Fortsetzung bleibt an World/Map, Spieler und
Generation, Item, Ziel und aktuellen Hop, Zielstart, rohe und effektive feste
Deadline, Gravity, Zielgeometrie sowie Navigatorresetserial gebunden.
Bisherige Itemreads/Needprüfung, 8m/3m-Grenzen, LOS, 12s-Deadline und
30s-Backoff werden weiter verwendet. Budget <=2 wartet ohne neue Rays,
Ablehnung oder verlängerte Deadline. Keine globalen Claims oder Itemwrites.

Reset, Tod, Goalverlust, Zeitrücklauf, NAV-Replan auf einen anderen Hop,
Relocation, Special/Chain/Lock/Important, Liquid/Flight, Follow, Use und andere
Movementownership beenden die Phase. Kontextwiederkehr reaktiviert sie nicht.
Außerhalb der echten Navsphäre werden Navzeit/-ziel/-travel gelöscht; dies
verleiht keine Floorfreigabe. Die bisherige physische Safety bleibt maßgeblich.
Weaponziele erhalten keine solche Phase; ihre bisherigen Entscheidungen und
Watchdogs bleiben erhalten.

`cecil_motion.h` ergänzt nur einen beobachtenden Resetserial: jede vorhandene
Resetquelle erhöht ihn. Konstruktion/Prepare, direkte und interne Resets sowie
Zeitfehler sind getestet. Überlauf wird dauerhaft ungültig (0), statt eine alte
Kennung erneut zu verwenden. Vollständiger Supplyreset verwirft die Phase.
`BotDriver.cpp` ergänzt nur `health_connector_proposal` in der bestehenden
periodischen Zustandszeile. Das Flag bedeutet frischen Planungsvorschlag,
keinen akzeptierten Input, Pickup oder erfolgreichen Weg.

## TDD-Nachweis

Die bestehende SDK107-Brücke führt tatsächliche Produktionskörper mit
SDK-gepinntem Action-/Rayvertrag aus; Geometrie und Welt sind deterministische
Stubs. Kein portabler Test qualifiziert Retail-ABI oder physische Runtime.

| Schritt | Checks | Fehler | Ergebnis |
| --- | ---: | ---: | --- |
| Unveränderter Parent | 2920 | 0 | Ausgangsstand |
| Erste sequenzielle Radiusreproduktion | 2942 | 6 | RED, Commit6b38b8 |
| Adversariale Phasen-/Safetytests vor Produktion | 3084 | 20 | RED, Commit0e10f9e |
| Erster begrenzter Produktionspatch | 3084 | 0 | GREEN |
| Zusätzliche finale Ownership-/Invalidframefälle | 3098 | 4 | RED vor Clear-Ergänzung |
| Nach Clear im bestehenden Safetyweg | 3098 | 0 | GREEN |
| Zusätzlicher tatsächlicher NAV-Replan ohne Reset | 3104 | 2 | RED vor Hopbindung |
| Finale Hopbindung, normale Brücke | 3104 | 0 | GREEN |

Finale ASan/UBSan-Brücke: 3104 Checks, 0 Fehler, Exit0. Der Compiler meldete
nur einen Debug-Variable-Tracking-Fallback am großen generierten main; keine
Sanitizerdiagnose. Alle zwölf C++-Header-/Policytests und vier gezielten
Python-Parentprüfungen liefen am finalen Produktionsstand mit Exit0.
Die zusätzliche 3098/4-RED-Ausgabe ist im Sitzungsverlauf beobachtet, aber
nicht als eigene private stdout-Datei erhalten; die 3084/20- und 3104/2-REDs
sind als private Dateien erhalten.

Weitere Gegenfälle decken Coldstart außerhalb Radius, Specialapproach,
35 Kontextänderungen mit anschließender Rückkehr, Budget0/1/2 und Erholung,
Deadline/Backoff, Connectorhöhe/-distanz/-wand, reale Relocation,
fehlende opt-in-Floorunterstützung, Tod, vollständigen Reset, andere finale
Movementowner, erfolglose erste Ankunft und unveränderten Weaponconnector ab.
19 warme Folgeticks verursachten keine Allokation.

## Reproduzierbare Kommandos und Grenzen

Aus Repositoryroot, SDK lokal `/srv/tse-sdk-20261021`:

```sh
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es
python3 poc/candidates/redstation-supply-20261107/test_cecil_native_bridge.py --sdk-player /srv/tse-sdk-20261021/Sources/EntitiesMP/Player.es --sanitize
```

Die Brücke wird als portables C++14-Programm gebaut; `--sanitize` aktiviert
ASan/UBSan. Ergänzend alle zwölf vorhandenen `test_*.cpp` im Kandidatenordner
jeweils mit `g++ -std=c++14 -O2` bauen und ausführen sowie die vier gezielten
Parentprüfungen `test_cecil_action_native.py --sdk-player …`,
`test_cecil_items_native.py`, `test_cecil_rules_exports.py fixtures/cecil-953b477`
und `test_supply_observer_native.py --sdk-player …` ausführen. Vollständige
Kommandos/Exitcodes/Outputhashes und finale Sourcepins stehen in der privaten
Quittung `.codex/evidence/health-connector-fix/final-receipt.json` dieses
Worktrees. Keine privaten Native-Rohlogs oder Retaildateien werden publiziert.

Rootreview, neuer DLL-Build und Devprüfung sind ausstehend. Erst diese können
zeigen, ob die begrenzte Healthfortsetzung im wirklichen Karten-/Kampfbetrieb
hilft; der Vorschlag beweist weder Waffenbeschaffung noch Cecil-Parität oder
A4-/A-Abschluss und erlaubt keinen automatischen Rollout.

## Finale Produktionspins

Sourcecommit: `b8854df01479a3aa0cd0673de86bc5d170561e1e`.

| Datei | SHA256 |
| --- | --- |
| BotSupplyNative.h | `d149936716b4233844d8b74a16df72ae2606a16282dd35c3b940bc0d59b64915` |
| cecil_motion.h | `f9f5acdb88dcf51c64bdc4523290877a1376e66c1795daa3a2897d3c7460f69d` |
| BotDriver.cpp | `9e8a1ed5c058c4bd0a45c99b07ddedf29580bca38940c4dbb27403c05816b153` |
| test_cecil_native_bridge.py | `26da2049b6a4338855eb8124a6f1f080712b9d841903efcae001ae348c57242a` |

## Rootintegration und Gegenprüfung20:28UTC

Produktionsauthorb8854df→Root3ba189d, Berichtauthorf71653e→Rootfe55f10. Root hat den vollständigen Produktionsdiff und die echten Bridge-Gegenfälle unabhängig geprüft, Source-/SDKpins sowie alle gespeicherten Authoroutputs frisch gehasht. Eigene normale SDK107-Brücke3104/0/Exit0 in6,282s; eigene ASan/UBSan-Brücke3104/0/Exit0 in34,926s. Nur der dokumentierte Debug-Vartracking-Fallback, keine Sanitizerdiagnose. RootEV/health-connector-root-review.json und beide Rootlogs sind privateBelege. DLL-Build und native Verbesserung bleiben ausstehend.

## Erster Windowsbuild: Build021 FAIL

Build021 aus Source05112fcb6caa2abf29d634ac61aa386e76c3d43c scheiterte20:31:25UTC am echten MSVC-Compiler: cecil_motion.h-Zeile54, Windows-Funktionsmakro max kollidiert mit numeric_limits<uint64_t>::max(). C4003/C2589/C2059, kein DLL-Link und kein nativer Kandidat. PrivateBuild-/Compilerlogs und Manifest bleiben unverändert. Folgefix klammert den Funktionsnamen: (std::numeric_limits<uint64_t>::max)(). Zählerwert, Sättigung und Verhalten bleiben gleich; erneuter vollständiger Windowsbuild in neuem Verzeichnis steht aus.
