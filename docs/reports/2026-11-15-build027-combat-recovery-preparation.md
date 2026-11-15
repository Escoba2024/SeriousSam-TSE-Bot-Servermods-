# Build027: Combat-Recovery, gebaut und noch nicht nativ abgenommen

Build027 enthält gegenüber026 ausschließlich die neue produktive Combat-Recovery
in `BotDriver.cpp` und `BotSupplyNative.h`. Die
[Quelländerung](2026-11-15-automatic-combat-ground-recovery.md) wurde von Root
vollständig geprüft;3663 relevante portable Checks/0FAIL, die sechs tatsächlichen
Authorlogs und fünf Sourcepins wurden geprüft. NegativeMap war ein echter zusätzlicher
Reviewfund:4Checks/3FAIL vor Combat-only-Korrektur, danach4/0. Das ist kein Nachweis,
dass die Änderung den beobachteten026-Stillstand tatsächlich beseitigt.

## Build und Herkunft

- Quelle13896f5fac700ba98dbd2312123880693597f25a,
  Treeeadd2e1e28f03bc65acdf563f95ebd1eec4c762b.
- MSVC Retail107:15 Übersetzungseinheiten und Linker Exit0;47Source-/28Overlay-
  Dateien vollständig gehasht; zusammen mit Manifest+DLL77Buildpins geprüft.
- DLLf5bf76801cade78803c6f4bcf97837390329fc30d2a016d202a9f4b96bbfc17e,
  446464Bytes. Manifestca235d88b0e20ed98fed83d9adf16e731feaec286f4da8f9dde0defe96d3c551.
- Build027 ist ein BotClient-Kandidat, kein Ersatz der Original-Dedicated-DLL.
  Keine Liveänderung und keine automatische Retailqualifikation.

Der erste Root-Wrapperentwurf ersetzte versehentlich auch das Jahr2026→2027;
der Pfadpreflight stoppte vor jeder Build-/Runtimeänderung. Die gezielte
Ersetzung wurde korrigiert. Der anschließend einzige Build lief erfolgreich.
Keine Fehlermeldung wurde als Erfolg umetikettiert.

Source075 wurde tatsächlich von GitHub abgeholt: Remote
ff32dc1c0fbeb4cd7991cf407e39eeb271099355 hat exakt den oben genannten lokalen
Quellbaum, Diff0. Das inkrementelle Sourcebundle benötigt e54282c aus065.

## Vor dem Test festgelegte Auswertung

Ein isoliertes027-Skulls600diag1-Fenster soll026 unter denselben Einstellungen
gegenüberstellen: Skulls'n'Bones, Hard2,8DEMON, OriginalDedicated,20FPS unveränderter
Originalbeobachter,600s, passiveDiagnose1. Kein Live-Rollout aus dem Runnerstatus.

Die vollständigen Rohdaten sollen Leben/Respawns, tatsächliche Inventargewinne,
Kills/Schüsse, Positionsverläufe und alle Lese-/Zuordnungsfehler ausweisen.
Insbesondere sind bewaffnete Stillstandsphasen, Zeitraum und Anzahl der gültigen
Messungen, lange Leben ohne Zusatzwaffe sowie tatsächliche Source-/Native-
Zuordnung zu prüfen. Die026-Werte52,303sNoUseful und16,546s exakteStillstandsphase
bleiben Vergleichsbelege. Akzeptierte Vorschläge sind kein ausgeführter Escape;
fehlende Call-ID/Arbitration/Guardbindung bleibt UNKNOWN. Eine abweichende einzelne
Spielsequenz beweist weder Kausalität noch allgemeine Verbesserung.

Vor Promotion erforderlich: keine neue Sync-/Disconnect-/Crash-/Restartregression,
normaler Rollenabschluss und unabhängiger Restore, eingehaltene Ressourcen,
sowie tatsächlicher nachvollziehbarer Bewegungs-/Versorgungsfortschritt. Weitere
Karten, A1, A3 und die formalen A5-Gates bleiben separat offen.

## Private Sicherung

Delta066:27382263B,
SHA72049d8accca6105d417350a757dea4f5bb1554809117bb2bebf0ff9b5290836,
Drive1mnNPd_Y2zsB5PAYLrqzGbWN5qdq_U9Fq. Vollständiger Drive-Rücklesehash und
zweifache SHA/UID/GID/Mode/mtime_ns-Prüfung aller239Dateien/32631557entpackten
Bytes bestanden04:31:15UTC. Enthält Build027, MethodAPI, portableBelege,
Rootreviews, verlustfrei komprimierte geschlossene024Skulls/022023Belege und
Sourcebundle13896f5→e54282c. Kein gestarteter Vollrestore der Retail-Runtime
behauptet. Originalarchive und Mischrollback051 bleiben erhalten.
