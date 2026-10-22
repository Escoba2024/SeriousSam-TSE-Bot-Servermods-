> Aktuelle Fortsetzung: [ausführende Bridge und Native-Runner](2026-10-21-session-execution.md), [Tool-/Isolationsentscheidung](../decisions/2026-10-21-isolated-session-execution.md). Der ältere Offline-Vertrag unten bleibt als Architekturhistorie erhalten. Jetzt vorhanden: `SessionExecutor`, eigener Wine-Transport und `qualify_bot_sessions.py`; standardmäßig kein Runtime-Start. `colors_enabled=true` ist nach nativer Prüfung innerhalb des konservativen 32-Byte-Policy-Limits möglich; Standard bleibt false. Neue zentrale Optionen: `min_bots`, `debug_logging`, `log_every_ticks`, `max_log_mib`. Kein produktiver Fixed-Slot-Supervisor darf dieselben Session-Prozesse steuern.

# Identitäten und Sitzungen – Benutzung und Integrationsvertrag

**Status: portabler Kern und offline Runtime-Vertrag Task3a, keine native Runtime-Steuerung oder Aktivierungsfreigabe.**
Dieser Code verändert weder die laufende öffentliche Flotte noch deren Supervisor.
Er erzeugt nur persistierte Absichten; keine Spiele, Eingaben, Prozesse, Ports oder Services.

## Konfiguration und Persistenz
Beispiel: `poc/scripts/BotSessions.example.json`, 24 fiktive Identitäten.
`enabled=false` ist der Standard. `colors_enabled=true` wird bis zum nativen Farb-Gate ausdrücklich verweigert.
Die RGB-Angabe ist bisher nur gespeicherte Metadaten. Namen werden als einfache ASCII-Namen ausgegeben.
24 sichtbare Zeichen sind eine konservative Projektregel, kein nachgewiesenes Retail-Maximum.
`^cRRGGBB`/`^r` wird zur konservativen Kollisionsprüfung entfernt, nicht als bereits nativ bewiesene Ausgabe erzeugt.
Unbekannte Formatierung in menschlichen Namen sperrt neue Joins.

`profile` wählt den vorhandenen Rosterindex:
0 beginner/aggressor, 1 beginner/survivor, 2 casual/flaky, 3 casual/controller,
4 average/duelist, 5 average/marksman, 6 advanced/aggressor, 7 expert/marksman.
Der spätere Adapter muss `bot_iProfile0` und den gespeicherten `gameplay_seed` als `bot_iProfileSeed` setzen.
Er darf GUID/Nickname/Farbe nicht bei jedem Prozessstart erzeugen.

Jede Instanz/Controller verwendet **dieselbe lokale SQLite-Datenbank** auf Hetzner.
Keine getrennte Datenbank pro Server; keine Netzwerk-Dateisysteme. Pro Identität existiert genau eine servergebundene Zeile.
Die anfängliche Serverzuordnung ist deterministisch und bleibt gespeichert. Pool-/Seed-/Identitätsänderungen bei vorhandener DB werden verweigert; keine automatische GUID-Neuerstellung oder stille Migration.
Zeitparameter dürfen verändert werden; bereits geplante Sitzungsenden/Pausen bleiben gespeichert.
Datenbank und Ereignisse sind private Runtime-Daten und gehören außerhalb des öffentlichen Git.
Vor jedem späteren realen Einsatz exklusiven eigenen Runtime-Pfad und Wiederherstellung sicherstellen.

## Reiner Offline-Aufruf
```python
import json
from bot_sessions import Planner

config = json.load(open("poc/scripts/BotSessions.example.json"))
config["enabled"] = True             # Nur für diesen Offline-Speichertest.
planner = Planner(":memory:", config)
server = "alpha-one"
planner.plan(server, {"observed_at": 1000, "maxplayers": 16, "human_names": []}, 1000)
intents = planner.plan(server, {"observed_at": 1200, "maxplayers": 16, "human_names": []}, 1200)
print([(i["action"], i["identity_id"]) for i in intents])
planner.close()
```
Mit `PYTHONPATH=tools` aus dem Repository ausführen. Kein Prozess wird gestartet.

## Runtime-Vertrag – vor Aktivierung noch zu implementieren und zu prüfen
- Ein frischer, vollständiger Query-/Eigentumsabgleich erzeugt `snapshot={observed_at,maxplayers,human_names}`.
  `human_names` muss alle nicht nachweislich eigenen Verbindungen umfassen; fremde Bots sind dabei ebenfalls Fremdbelegung.
  Eine reine Namensliste beweist keine Prozesseigentümerschaft. Bei unvollständiger/unsicherer Zuordnung `snapshot=None` übergeben.
- `plan(server,snapshot,now)` läuft in einer SQLite-`BEGIN IMMEDIATE`-Transaktion.
  Es reserviert `JOINING` oder `LEAVING`, bevor es eine Absicht zurückgibt.
  Global höchstens ein gleichzeitiger Join und Leave; Abstand 1–3 x Joinintervall (Dreiecksverteilung) bzw. mindestens Leaveintervall.
  Menschenreserve verringert die Obergrenze; sie wird nicht durch fremde Belegung verbraucht.
- Absichtsschlüssel ist `(identity_id, epoch)`. Vor jedem realen Start/Stop eigene PID/start/CWD/cgroup/Port/GUID prüfen.
  Eine zweite Instanz darf bei vorhandenem `JOINING` keinen zweiten Spielprozess starten.
- Ein Neustart muss gespeicherte `JOINING`/`LEAVING` mit tatsächlichen Verbindungen abgleichen.
  Unterbrochene Absichten werden aus `states()` und `identities()` rekonstruiert; sie werden von `plan()` nicht erneut emittiert.
  Nicht pauschal zurück nach WAITING setzen. Prozessausfall, Query-Lücke und Ghost-Slot sind unterschiedliche Beobachtungen.
- Erst echte Verbindung bestätigt `record(id,epoch,"joined",now)`; erst bestätigter sauberer Abgang bestätigt `"left"`.
  Unerwartete Ausgänge heißen `"crashed"` oder `"disconnected"`. Bei LEAVING bleiben Abmeldegrund und tatsächliches Ausgangsereignis getrennt gespeichert.
- `set_enabled(server,False,now)` bleibt über Controller-Neustarts erhalten; neue Joins bleiben aus.
  Bereits eigene aktive Verbindungen erhalten kontrollierte Admin-Leave-Absichten.
- Der PR-46-Supervisor benötigt denselben Sollzustand. Keine gleichzeitige Verwendung seines fixen Acht-Bot-Wiederanlaufs
  mit diesem Planer: geplante Pause könnte sonst als Fehler wieder aufgefüllt werden.
- Keine beliebigen externen Befehle aus Nicknames/Konfiguration; keine direkte Änderung gemeinsam simulierter Enginezustände.

## Zeitmodelle
Normal: 10% 5–19:59 min, 80% 20–90 min, 10% 90:01–180 min, Pause 15–120 min.
`regular_weight` bevorzugt wiederkehrende Identitäten innerhalb des verfügbaren Pools; es hebt keine Pause auf.
`accelerated=true` erlaubt kürzere Testwerte. Unit-Tests mit virtueller Uhr und 200 normalen Zeitziehungen
sind **keine** Echtzeit-, Retail- oder Langzeitabnahme.
Unbekannte/veraltete Queries blockieren neue Joins. Bereits geplante eigene/admin Abmeldungen bleiben möglich.
Rückwärts laufende Controllerzeit wird abgelehnt; nach korrekter Uhr weiterarbeiten, keine Pause manuell verkürzen.

## Aktivierung und Rollback
**Derzeit keine produktive Aktivierung:** Runtime-Anbindung, Retail-Farben/Längen, individuelle Abgänge/Rückkehr,
Gameplay-Erweiterungen, 8/2x8-Kapazität und neue 60-Minuten-Abnahme fehlen.
Der kleinste nächste Runtime-Schritt steht im Handoff. Kein Eingriff in die aktuelle Flotte zur Freiräumung.

Nach später bestandenen Gates: DB sichern, eigene isolierte Konfiguration/Ports/Buildhash pinnen,
Scheduler-Sollzustand an genau einen verantwortlichen Supervisor anbinden, erst 1/4/8 und dann 2x8 qualifizieren.
Realer Quit zuerst regulär; Force nur für nachgewiesen eigene PID nach Timeout und im Bericht getrennt.

Rollback dieses Teilstands: keinen Planer aktivieren; Bibliothek entfernen oder `enabled=false` belassen.
Da weder Runtime- noch Servicekonfiguration geändert wird, ist hier kein Spiel-Restore nötig.
Bei später aktiver Anbindung: Admin-Off, eigene Verbindungen kontrolliert schließen, Abwesenheit/Ports nachweisen,
gesicherte Konfiguration zurücksetzen; Identitätsdatenbank/GUIDs erhalten. Nur dann bisherigen Supervisor wieder allein betreiben.

## Ergänzung Task3a – reine Profil- und Prozessentscheidung, nicht aktiviert
- `from bot_session_runtime import profile_bytes, guid_bytes, startup_script, ControllerLock, reconcile` (mit `PYTHONPATH=tools`).
- `profile_bytes(template, identity)` erwartet eine **originalgetreu gelesene PLC4-Vorlage** im verifizierten Format und liefert neue Bytes; `guid_bytes(identity)` liefert genau die 16 Bytes für die `.plr.guid`-Sidecar. Der künftige native Adapter muss die beiden Outputs **ausschließlich in ein eigenes Overlay** schreiben und dann beide verifizieren.
- `startup_script(identity)` liefert nur sichere Human-BotDriver-Overrides für den vorhandenen qualifizierten `Integrated.ini`-Basisinhalt. Erst in einem getrennten **Ein-Spieler-pro-Prozess**-Wine-Overlay und mit entsprechend konfiguriertem Local-Player-Count verwendbar. Die CPU-/RAM-Kapazität dieses Modus ist noch unbewiesen.
- `ControllerLock(database)` schützt den exklusiven Live-Executor; nur `claim_launch(identity_id,epoch)` darf eine frische JOINING-Epoch einmalig beanspruchen. Nach Absturz/unklarer Ausführung nicht automatisch ein zweites Mal starten. SQLite-DB und Lock müssen auf lokalem, eigenem Runtime-Speicher liegen; keine Hardlinks oder geteilten Volume-Aliase.
- `reconcile(state,observation)` verlangt gleiche Identität/Epoch und vom späteren eigentumsbewussten nativen Prozessprüfer frisch bestätigte Beobachtungen. Der Rückgabewert `claim_launch` ist **keine Startfreigabe für sich allein**: nur nach erfolgreichem atomaren Claim unter dem exklusiven Lock darf ein späterer qualifizierter Adapter den eigenen Prozess starten. `quarantine` bedeutet: weder Auto-Start noch blindes Stop/Reset.
- Es existiert **noch kein** Prozessprobe-Konsument dieser Bibliothek. Insbesondere NICHT die laufende öffentliche Acht-Bot-Flotte oder den separaten PR46-Supervisor an die neue Sollzustandslogik binden. Farben bleiben trotz vorhandener RGB-Metadaten bewusst ohne `^c`-Ausgabe.
- Portabler Nachweis auf Hetzner: 17 neue Adapter-Tests, gesamte Tools-Python-Suite 89/89 PASS; keine native Anwendungs- oder Multiplayer-Qualifikation.

**Zusätzlicher Beleg 18:00 UTC:** 19 reine Adapter-Tests inklusive echter multiprozessübergreifender Lock-Sperre und simulierter End-to-End-Join/Leave/Cooldown-Kette; gesamte Python-Suite **91/91 PASS**. Keine echte Spielausführung daraus abgeleitet.

### Privat-Testharness (noch keine Runtime-Freigabe)
`tools/qualify_integrated_wine.py --identity-record <privater JSON-Export aus Planner.identities()>` ist nur mit `--stage one` und ohne `--public-address`/Reference gültig. Er nutzt die bisherige private Overlay-/Originalhash-Absicherung, ein Local-Player-Profil, die feste GUID-Sidecar und den bereits qualifizierten Build04-Quellhash. Der Flag-Pfad wurde bislang **ausschließlich statisch mit einem temporären Testfixture** geprüft; vor nativer Nutzung alle aktuellen fremden Qualifikationen beenden lassen, isolierte Ports/Xvfb/cgroup/Pfade wählen, private Belege außerhalb Git bewahren und die reale Rückkehr mit gleicher GUID separat verifizieren.

## Native Tests 18:29 UTC, nur private Umgebung
- Native Same-Server-Sessionprüfung mit `tools/qualify_integrated_wine.py --identity-record <eigene persistierte Identität> --identity-rejoin-smoke --stage one`, zwingend ohne Public-/Reference-/Color-Flags; echte Profile/GUID nur im eigenen Overlay, reguläres WM_DELETE_WINDOW auf **nachweislich eigene** Bot-PID, 3 Query-Abwesenheiten, erneuter Join auf gleicher Server-PID, Hash-Gleichheit, CGroup/CPU/0 Throttles. Private Rohdaten nie in Git.
- Option `--color-probe` ist ausschließlich eine **isolierte Syntaxprobe**, keine dauerhafte Freigabe: native Query entfernt `^cRRGGBB` und `^r` aus sichtbarem Namen, HUD/Scoreboard nicht geprüft; `bot_sessions.validate_config` verweigert weiterhin `colors_enabled=true`.
- Das Testharness ist nicht der fehlende produktionsfähige Zeitplaner: native Einzel-Session war nur eine Probe; für echte zufällige Beitritts-/Abgangsintervalle ist die ControllerLock/Planner-Integration mit verifiziertem Prozess-/GameSpy-Eigentum noch offen.
- Native Resultate und Grenzen in `docs/reports/2026-10-21-identities-native-smokes.json`.
