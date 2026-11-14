# Build020: direkte Tiervergleiche Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Schritte mit Checkboxen nachführen.

**Goal:** Einen deaktivierten, überprüfbaren Nachfolger für direkte MITTEL↔STARK- und STARK↔DEMON-Vergleiche liefern; kein nativer Stärke-/A3-PASS aus Offlinearbeit.

**Architecture:** Original-A3-Build018-Controller, Originaldamagehook, Hostbindung, strenge Anfangserfassung und FileTransaction übernehmen. Beide Vierergruppen laden dieselbe Build020-DLL und dieselbe kanonische Kandidatenkonfiguration; nur ArenaTier unterscheidet sich. Neue kleine Policy und beidseitige Auswertung erfassen konkrete Tieridentitäten statt aus der DLL auf Legacy/Kandidat zu schließen.

**Tech Stack:** Python3, bestehender privater Retail-1.07/Wine-/Frida-Harness; portable Python-Unittests ohne Compiler.

**Spec:** Benutzerauftrag A3; Root-Bestätigung vom14.11.2026: zwei benachbarte Paare, je zwei vertauschte120s-Starts, gleiche Build020/Kampfkonfiguration, keine neue Killmarge, Unentschieden/Widersprüche offen.

## Global Constraints

- Während des laufenden A4-Fensters keine Tests, Builds oder native Aktionen. Tests zuerst schreiben; RED/GREEN erst nach bestätigtem A4-Ende ausführen. Diese verzögerte Ausführung ist ausdrücklich angeordnet.
- Runtimegate und Runplan deaktiviert; nur Root friert ein und startet einzelne Fenster. Keine automatische Serie/Retry.
- 4+4eigene Bots plus unveränderte Vanilla, Red Station, ursprüngliche120s/125000ms-Hook-TTL/2000ms-Reserve; Initialreferenz und sämtliche Host-/ABI-/Identity-/Restoregrenzen unverändert.
- CPU≤75%, RAM≥1,5GiB, Disk≥8GiB; keine parallele breite Suite und keine stillschweigende Produktionspause.
- Originaldamage-/Host-/Restorecode bytegleich kopieren und pinnen; keine Spielzustandswrites. Historische Legacy-Siege getrennt halten.
- Neues Paarpaket verwendet überall Build020 094ec8edbedd5e63d8e4eb03fcce70518283b22440e5f80ba4c2482ff81fe6c0, Source e5f7a65502fbea683014ef8fcc95ecdd2a927b6a.
- Server Hard2 in allen vier neuen Fenstern, native Session-/Querybelege aus vorhandenen Samples; historische Serious3-/109:33-Belege getrennt. Gepinnte Rootpolicy `stability_hard_rules.py` wiederverwenden, keine neue Samplerate.

## Review Focus

- Gleiche DLL in beiden Gruppen darf Zuordnung nicht kollabieren: tatsächliche Rolle/Slots/Entity plus zugewiesener Tier müssen übereinstimmen.
- Canonical Profile0..3=7/Seed2026110750 beibehalten; beide Configs nach Entfernen genau einer Tierzeile bytegleich. RosterOffset4 bleibt identisch, explizite Profile überschreiben den Offset.
- Beidseitige Cecil-Lebens-/Waffen-/Aimdaten einschließlich Nullereignissen, Toten ohne Zusatzwaffe und zensierten Leben; Fireanforderungen nicht Treffer nennen.
- Unattributed/Self/Corpse/Fremd-/Vanillaschaden bleibt getrennt; Originalserverkills gegen tödliche Calls abgleichen.
- Resultat/Logs/Restorefehler bleiben sticky; gemischte Builds/Hostbedingungen/Swaps nicht gemeinsam qualifizieren. Keine künstliche Siegschwelle oder erfundene Stichprobensicherheit.

## Status und Aufgaben

- [x] Statische Bestandsaufnahme: Build018-Harness und Analyzer sind einseitig Legacy7fc/Kandidat; Tiercode in bot_profile.h und Arena-Ausnahme in HumanBotPolicy::Configure geprüft.
- [x] Tests zuerst schreiben: exakte Configgleichheit außerTier, vier Paar/Swap-Zuordnungen, verbotene Paare/Legacyconfig, richtige Registrylabels, beidseitige Behaviorzuordnung, Gleichstand/Widerspruch ohne Pass.
- [x] Pure Policy/Adapter und eng angepasste beide Analyzer implementieren; keine Originalhook-/Host-/Restoreänderung.
- [x] Deaktivierten privaten Controller plus vollständiges geerbtes Manifest erzeugen; erlaubten Source-Diff und unveränderte Dateien dokumentieren.
- [x] Erst nach bestätigtem A4-Ende fokussierte Checks ausführen: 23/23 grün, ausschließlich portable synthetische Fälle; keine breite Compiler-/Native-Suite.
- [x] Reviewbare Deltas, Pins, Teststatus und konkrete Aufrufe/Handoff vorbereiten. Root allein integriert/native/live.

## Festgelegte spätere Fenster

| Paar | Swap | botA | botB | Dauer |
|---|---:|---|---|---:|
|1↔2|0|MITTEL|STARK|120s|
|1↔2|1|STARK|MITTEL|120s|
|2↔3|0|STARK|DEMON|120s|
|2↔3|1|DEMON|STARK|120s|

Jeweils einzeln auswählen. Dieser enge Nachfolger akzeptiert ausschließlich Instrumentierung1, Diagnostics0 und120s. Der historische Originalcontroller bleibt separat erhalten; keine zusätzliche Kontrollserie wird angelegt.

## Auswertung und Grenzen

Alle direkten lebenden Gegner-Damagecalls, rohen und auf Vorher-HP begrenzten HP-Verluste, Rüstungsverluste, tödlichen Calls und unabhängigen Serverkillpaare je Tier/Swap zeigen. Waffenbeschaffung, alle Leben, Bewegungs-/Stuckbeobachtungen und tatsächlich protokollierte Profile beidseitig auswerten. Ergebnisse pro Swap und zusammen nur bei identischer Build-/Config-/Hostbedingung zeigen. Keine automatische Variable `tier_strength_pass`: unentschiedene, widersprüchliche oder unvollständige Ereignisse bleiben offen. Zwei kurze Starts sind keine allgemeine menschliche Spielstärke, Stundenstabilität oder universelle Dominanz; DEMON↔MITTEL ist kein direkter Bestandteil dieses engen Auftrags.

## Fortsetzung nach Observer-V2

Das ursprüngliche Design0454337 bezog sich auf019. Für den aktuellen Kandidaten
ist die Umsetzung ausdrücklich auf dieselbe020-DLL in beiden Gruppen retargeted;
historische019-/Legacyergebnisse werden nicht vermischt. Datei heißt aus
Historiengründen weiterhin build019.

- [x] Reine Zusatzpolicy `tools/a3_direct_tiers.py` und acht gezielte Tests.
  Erster Aufruf ROT wegen fehlender Implementierung; anschließend8/8grün in
  0,001s im ausdrücklich freigegebenen Offlinefenster. Keine breite Suite.
- [x] Exakte Configgleichheit außerArenaTier, beide realen Entity-/Slotlabels,
  beideSwaprichtungen und offene Gleichstände/Widersprüche modellieren.
- [x] Private deaktivierte020-Hard2-Controllerkopie und beidseitige geschlossene
  Damage-/Behaviorauswertung fertigstellen. Originaldamage/Host/Restore bleiben
  unverändert; aktueller Commit ist allein portable Policy, keine Nativefreigabe.
- [ ] Hauptagent reviewed/friert ein/startet ausschließlich einzelne Fenster.

Die private deaktivierte Hard2-Controllerkopie, der dünne Adapter und beide
Analyzer sind fertig. Nach ausdrücklich freigegebenem Quiet-Ende bestanden
23 fokussierte Fälle in0,062s, einschließlich vollständiger synthetischer
geschlossener Analyzerfixture. 77 Runtime-, 75 Build-/Overlay- und142 Parentpins
sowie zehn unveränderte Damage-/Host-/Restorequellen passen frisch;
18 maßgebliche Dateien wurden offline bytegleich reproduziert. Nächster Schritt:
unabhängiger Rootreview und separater Freeze. Keine Nativeaktion durch diesen
Worker, kein A3-PASS durch portable Tests; Ereignisrichtungen bleiben ohne
zusätzliche Killmarge sichtbar.

Root ergänzte als zwingende Finalbedingung Hard2. Der ursprüngliche A3-Parent
erbt die Lab-Startvorlage und beweist dadurch keinen Hard2-Betrieb. Deshalb wird
ein eigener `direct020-hard`-Sourcecontainer erzeugt: innerhalb des versiegelten
Restores nurDifficulty2 setzen; vorhandene übrige Regeln unverändert prüfen,
Roots reine Hardpolicy bytegleich übernehmen und vorhandene native Barrier-/
Health-/Querysamples prüfen. Diese gezielten Offlinefälle wurden ausdrücklich
erst nach geschlossenem Quiet-Fenster ausgeführt. Finaler Paket-/Manifest-/
Quittungspfad steht im Bericht
`docs/reports/2026-11-14-a3-direct020-disabled-controller.md`.
