# Bot-KI 2.0: CecilBotMod-P1-Transfer (RDC/Hetzner, 25.10.2026)

**Stand:** Experimenteller opt-in Kandidat. Keine Produktions- oder main-Freigabe.

## Quellen und Isolierung

Remote main: 107d28a276c4fe4428cc3c8bf5bbd876e1a85351 (verifiziert).
PR54-Analyse: 2241cc591d58be8048ebb1630f4490869244bc5a.
AI2-Ausgangscommit: 18d47cdac9c12d2013efe09fd9b866b9f296ffea, auf PR51 01d847d. Der andere AI2-Worktree mit fünf uncommitteten Dokumentdateien wurde nicht berührt.
Keine Cecil-Quelldatei/Navmesh-Daten kopiert, keine Änderungen an Retail-Originalen, öffentlicher Build04, Server oder poc/release/gamemp.

## Umsetzung, Default OFF

Neues Shell-Flag bot_bCecilP1=0. Voraussetzung bot_bHumanAI=1, nur experimentelle Clients.

1. Gegnerwahl: frische visuell bestätigte replizierte Gegner-Yaw- und HP-Daten; geschätzte Blickrichtung, Entfernung, niedrige gegnerische HP, eigene HP und Persönlichkeit. Bestehende Reaktionszeit, Stickiness und Zielwechsel-Hysterese bleiben. Blickrichtung ist keine direkt gemessene Schussabsicht.
2. Waffen-Kadenz: Tommygun/Minigun weiterhin kontinuierlich, Rocket 0,75 s, Granate 1,0 s, Sniper 1,3 s, Cannon 1,8 s. Feuerfreigabe bleibt an Aim, LOS und Explosions-Sicherheitsgate gebunden. Native Cannon-Ladung und tatsächlicher Projektilnachweis sind OFFEN.
3. Respawn-Verzögerungen in 20-Hz-Ticks: Skill 1→2,00 s; Skill 2→1,50 s; Skill 3→1,00 s; Skill 4→0,60 s; Skill 5→0,25 s. Lebensübergänge setzen den Zustand deterministisch zurück. Default-OFF reproduziert den bisherigen 4-Tick-Fire-Puls.
4. Privater Native-Test-Schalter --cecil-p1 nur für netns-isolierte, marker-geschützte Sessionqualifikation. Keine neue öffentl. Portfreigabe.

## Tests, Methoden und Grenzen

RED: ursprünglicher C++-Test kompiliert vor Implementierung nicht (Beleg RED-compile.log privat).
GREEN: test_bot_cecil_p1.cpp 255 Checks, 0 Fehler; permanentes Makefile-Testziel.
Bestehende C++-Tests vollständig PASS, Human AI 555 Checks/0 Fehler, Combat, Intercept, Route, Reconnect, Weapon. Driver-Integrationsblock-Smoke PASS.
make bench PASS: 4 simulierte Rays/Tick. Zwei A/B-Läufe mit Flag standardmäßig OFF auf gemeinsamem Host: Baseline im Mittel 1,3806 µs/Tick; Kandidat 1,4750 µs/Tick; +0,0944 µs (6,8 %). Nicht ausreichend für belastbare CPU-Schlüsse, opt-in Kosten noch nicht isoliert.
Reproduzierbarer MSVC-x86/Wine-Build: 15 Quelldateien, Link PASS; GameMP.dll SHA256 7dc961c880e0ed68ead13ed4e8299a025be71e05619de36c437c756e964334bf. Compilerwarnung C4474 in unveränderter Controls.cpp, keine neue Warnung geänderter Quelle.
Python-Test-/Native-Sync-Ergebnisse folgen als eigene Abschnitte im Handoff.

## Native Evidenz, aktualisiert

- Private Ein-Bot-Messung bei aktiviertem Opt-in: /srv/tse-session-qualification-cecil-p1-one-20261025-r2/result.json -> **PASS_LIMITED_SESSION_LIFECYCLE**, 131,87 s, peak_playing=1, unveränderter Retail-Kontrollclient beigetreten, Kandidat-SHA wie oben, kein Cleanup-Fehler; 0 SYNCBAD (im Serverlog), SYNCOK bestätigt.
- Erster Lauf fehlgeschlagen **vor** Eintritt des Kontrollclients (also keinerlei KI-Fehlernachweis), weil der Runtime-Root durch umask 077 statt beabsichtigter 0755 nur 0700 für UID65534 zugänglich war. Originalprozessmeldungen: Wine WINEPREFIX Permission denied. Eigene Testhülle korrigiert: private Root explizit 0711 (execute-only, keine fremde Dateiliste), zugehörige zwei Regressionstests bestanden. Die sechs Overlay-Mounts des ersten Fehlschlags wurden erfolgreich entfernt; Wine-Server-Cleanup-Fehlermeldung ist unter eigener Evidenz abgelegt. Zweiter Lauf bestätigt vollständiges Cleanup.
- Python-Regressionen im Testbaum: **170 Tests PASS** (vor dem anschließend verbesserten 2-Fall-Root-Permissions-Test). Die Root-Berechtigungs-Tests danach zusätzlich 2/2 PASS.
- Vier-Bot-Evidenz: in Arbeit (separater privater Runtime-Root und Marker-Wächter); ausführlicher Abschluss wird in dieser Datei ergänzt.

**Wichtige Abgrenzung:** Der native Ein-Bot-Nachweis ist eine isolierte Session-/Join-/Sync-Lifecycle-Abnahme, keine Endabnahme der Wirksamkeit von Zielwahl/Kadenz oder Cannon-Mechanik. Kein Deploy.

## Produktions- und Risikoschutz

Öffentlicher Server zuvor auf ausdrücklichen Nutzerauftrag deaktiviert, Marker /srv/tse-public-disabled.json unverändert. Keine Gameserver/Wine/Xvfb-Prozesse beim Start oder öffentlichen Listener. Keine öffentliche DLL ersetzt. Host 3,7 GiB RAM und 9,5 GiB freier Disk; native Testhülle fordert unveränderten Shutdown-Marker, private netns/cgroup, 768 MiB RAM-Rest, 8 GiB Disk, bewachte Prozessgenerationen, korrektes Cleanup. Privatlogs und alle Retail-Assets ausschließlich /srv, niemals GitHub.

Weiter offen: reale Gameplayqualität/Schüsse, mehrfache A/B mit getroffenen Zielen, längere native Sync- und Vier-Bot-Gates, produktive Freigabe. P4/P5 (Messer/Lauf, Strafe-Gesundheitsdynamik, Live-Profilwechsel) nur nach separater sicherer isolierter Abnahme. Kein Abgrund-/Ground-Lookahead-Rollout wegen historischer SYNCBAD-Probleme.
