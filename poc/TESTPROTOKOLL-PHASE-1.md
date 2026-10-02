# Testprotokoll – Phase 1: Pfad-D-PoC mit genau 1 Bot

**Datum:** ____________  **Tester:** ____________
**Bot-Client:** GameMP.dll ersetzt ☐ (Hash dokumentieren: ____________)  **Bot-Aktivierung:** `Scripts\BotStartup.ini` mit `bot_bEnabled = 1;` ☐
**Bot-Start:** `SeriousSam.exe +connect <ip>:25600 +quickjoin +script Scripts\BotStartup.ini` ☐
**Beobachter:** unveränderter Vanilla-Client ☐ (Hash identisch zu Phase 0 ☐)

> Gate der Design-Spec: **alle** Pflichttests PASS + 60 Minuten ohne `MSG_SYNCCHECK`-Kick, Desync oder Crash. Erst danach Phase 2 (2–4 Bots).

## Pflichttests

| # | Prüfung | Erwartung | Ergebnis (PASS/FAIL) | Notiz / Beweis (Log) |
|---|---|---|---|---|
| 1 | Join ohne Mod-Download/Fehler | Bot-Client verbunden; Server-Log: „Adding player …", CRC check OK | | |
| 2 | Bot als normaler Spieler sichtbar | Scoreboard/Playerliste zeigt Bot-Name | | |
| 3 | Bewegung sichtbar | läuft dauerhaft vorwärts, dreht langsam (ca. 45°/s per Default) | | |
| 4 | Schießen sichtbar | Feuerpulse (~1 s Periode), Sounds/Projektile beim Beobachter | | |
| 5 | Schaden/Frag | Beobachter kann Bot treffen/töten; Frags zählen korrekt | | |
| 6 | Tod/Respawn | nach Tod → Fire-Puls löst Respawn aus (Beleg: `VERIFIKATION.md` Abschnitt 3.6) | | |
| 7 | Mapwechsel | Server wechselt Map → Bot-Client reconnectet automatisch (`gam_strJoinAddress`) | | |
| 8 | Disconnect/Reconnect sauber | Bot-Client-Prozess neu starten → Bot erscheint wieder | | |
| 9 | Eindeutige Character-/GUID-Zuordnung | Server-Log zeigt Player-Index + Name; Reconnect erkennt Character wieder | | |
| 10 | Serverbrowser/Player-Query (333networks oder Direkt-IP-Abfrage) | Spielerzahl zählt Bot als belegten Slot | | |
| 11 | Bot-Client-Log | `[BotDriver] bot0 tick=… pos=(…) heading=… fire=…` alle 2 s; Position ändert sich mit Laufgeschwindigkeit | | |

## 60-Minuten-Stabilitätstest

Start: ____________  Ende: ____________

| Zeitpunkt | Beobachtung (Sync? Kick? Latenz? Framedrops?) |
|---|---|
| 0 min | |
| 10 min | |
| 20 min | |
| 30 min | |
| 40 min | |
| 50 min | |
| 60 min | |

**Ergebnis:** ☐ GATE BESTANDEN → Phase 2 (`PHASE-2-3-ANLEITUNG.md`)  ☐ FAIL

**Bei FAIL (Abbruchkriterium der Spec):** Ursachenbericht schreiben (Server-Log, Bot-Log, Wireshark), Fehlerklasse zuordnen (CRC / Version / Mod-Kennung / Desync / Timing) und Entscheidung dokumentieren: Nachbesserung Pfad D oder Wechsel auf Fallback B2.

________________________________________________________________

## Troubleshooting-Schnellreferenz (Disconnect-Meldungen)

| Meldung | Ursache | Fix |
|---|---|---|
| „Wrong CRC check." | EntitiesMP.dll/Daten weichen ab | Bot-Client-Installation auf Hash-Gleichheit mit Server prüfen (Phase 0.3) |
| „This server runs version X.Y, your version is A.B" | Engine-Versionen gemischt | Bot-Client = 1.07-Installation; nur GameMP.dll getauscht |
| „MOD:<name>\<url>" | Bot-Client hat Mod aktiv | kein `+game`, kein Mods-Ordner, DLL direkt ins Hauptverzeichnis |
| „Server full!" | Slots belegt | `gam_ctMaxPlayers` erhöhen (max. 16) |

## Laufzeitnachtrag 01.10.2026 – Gates A/B

**Phase 1: NOCH OFFEN.** Nachweise unter `.codex/evidence/phase1-20261001/`.

| Pflichtpunkt | Status | Evidenz / Grenze |
|---|---|---|
| Join/CRC + Vanilla Observer | BESTÄTIGT | visual-first 180.17 s; diagnostics 120.21 s; combat-fixed-target 180.07 s; combat-warmup 180.29 s, jeweils 2 CRC OK und Observer sieht Bot-Join im Log |
| Echter Spielername/Slot | BESTÄTIGT | Native UDP-25601-Statusantwort: gamever 1.07, activemod leer, numplayers 2, player_1 TSE_Bot_PoC |
| Scoreboard/Player-Menü sichtbar | OFFEN | Kein verlässlicher GUI-Capture |
| Lokale Entity-Bewegung/Rotation | BESTÄTIGT | diagnostics/telemetry.json: 1005 verschiedene Positionen, 161 Yaw-Werte |
| Angewendete Fire-Buttons | BESTÄTIGT | 329 Fire-on- und 1821 Fire-off-Samples; keine Aussage über sichtbare Schusswirkung |
| Observer sieht Bewegung/Rotation/Fire, passende Richtung, keine Teleports/Resets/Jitter/Desync | OFFEN | Capture-Timeout auch mit sichtbaren Fenstern; keine Bilder gewonnen |
| Schaden, Frag, Schaden erhalten, Death/Respawn mehrfach und Aktionen danach | OFFEN / TEST NICHT BESTANDEN | Beide Kampfversuche: beide Spieler health 100, frags 0; keine erfolgreiche Kampfinteraktion |
| Disconnect/Reconnect + Slotfreigabe/Aktionen | OFFEN | Neustarts zwischen isolierten Sessions beweisen kein Reconnect innerhalb einer Session |
| Mindestens zwei Mapwechsel + Aktionen | OFFEN | Nach Gate-B-Reihenfolge nicht gestartet |
| Regulärer Shutdown aller drei Prozesse / ABI-Freigabe | OFFEN | Alt+F4 kein nachgewiesenes Beenden; Cleanup hart |
| 10/30/60 min Sync, Reproduktion 60 min | OFFEN | Nicht gestartet, weil Kampfzyklus nicht bestanden; kurze Läufe sind kein Soak-Gate |

Die genaue Ursache der fehlenden Treffer ist nicht bewiesen. Stagnierende
Positionen trotz Zieltest legen geometrische Blockierung nahe, ersetzen aber
keine Sicht-/Schusslinienprüfung. Keine Navigation hinzugefügt. Kleinster nächster
Test: Bot und unveränderten Observer nachweislich auf freie Schusslinie bringen,
dann realen Schaden/Frag und mehrere Death-/Respawn-Zyklen prüfen.

## Neuer Kampfnachweis 01.10.2026
Native Capture und Action-Composer korrigiert; alter Shell-Speedread ergab -666.
`native-composer-combat`: health des Observers 100/80/60/40/20/0 und Bot-Frag1.
`observer-fire-key-combat`: finale DLL AA0D07C... wiederholt den Kill. Vanilla-
Observerlog und native HUD-TGAs bestaetigen Treffer/Kill/Frag. Native Bilder unter
`.codex/evidence/phase1-continue-20261001/`; siehe Bericht fuer genaue Laeufe.
Spielernamen/Frag-HUD/Schadenswirkung/Tod des Observers jetzt visuell bestaetigt.
Bot-Schaden/Tod/mehrfache Bot-Respawns bleiben offen; auch vollstaendige visuelle
Bewegungs-/Rotations-/Jitterabnahme und anschliessend C/D/E. Phase 1 NOCH OFFEN.

## Fortsetzung 02.10.2026: vier native Bot-Respawns
Cleanup-Race-Test korrigiert: gemeinsam mutierbares Hashtable statt script-scope Flag. Echter Lauf cleanup-race-regression30.19s PASS, simulierte Stop-Process-Ausnahme nach Terminierung tatsaechlich injiziert; alle Prozesse/Ports entfernt, beide Konfigurationen byte-identisch restauriert,300TGAs+3Logs archiviert. Fuenf PS-Syntaxchecks und Telemetriechecks PASS. Standalone Botcorecheck PASS; Testkommentar klaert, dass er keinen nativen Composer ausfuehrt.
Neue Evidenz: .codex/evidence/phase1-20261002. Hole-straight90.13s und Hole-native-combat90.23s CRC/Join PASS, health100; keine Death-/Respawnabnahme daraus.
Fortress-slow-turn180.09s PASS mit finaler AA0D07C-DLL, Vanilla-Observer/Server/Entities. Normale Fragmatch-Stockmap Fortress, TestTarget-1, YawSpeed5. Bothealth Minimum-15.5; vier Todesuebergaenge bei Ticks629/1712/2060/2420, vier Respawns health100 bei664/1744/2104/2464. Observer meldet viermal passed away. Nach jedem Respawn161-388 Positionen und45-153 Fire-on-Samples, jeweils Fire-off vorhanden. Native Frags0->-4 bei Umwelttoden. cycles.json und telemetry.json enthalten Details. Keine direkte Health-/Entity-/World-Manipulation. Reproduzierbares Profil poc/scripts/Phase1Respawn.ini.
Konsolenrootcause geklaert: SDK Console.cpp verlangt im laufenden Spiel / vor Befehlen, sonst Chat. Native Tasten mit Shift+7 erreichen jetzt nachweislich Shellparser; zwei Variablenabfragen scheitern wegen deutscher Zeichentasten (Unterstrich als - bzw. '). Kein erfolgreicher Variablenwechsel behauptet; die -666 Parserausgabe ist kein neuer Speedread im BotDriver.
Little-trouble-wide-fov60.07s PASS,602TGAs: kein Bot im Sichtfeld und kein Schaden. FOV150 wird in normalem Fragmatch durch natives Player.es auf90 gesetzt; Einstellung byte-identisch restauriert. Kein FOV-/Modellgate daraus ableiten. Skulls-native-visual90 laeuft fuer sichtbare Spielerrepraesentation.
Phase1 weiterhin OFFEN: gesamte visuelle Bewegung/Rotation/Jitter-Abnahme und vollstaendige serverseitige Schadenskonsistenz noch nicht belegt; danach C/D/E. Kein Phase2, kein Commit/Push bisher. Manual-combat-ready vom Vortag ist abgeschlossen, nicht mehr aktiv.

Neuester Stand: Fortress-Zyklen durch unabhaengigen Reviewer gegen Rohlog bestaetigt, keine neuen relevanten Codebefunde. Skulls-native-visual90.26s PASS,902TGAs, Beobachterblick aus einem anderen Raum; contact.png zeigt noch kein Botmodell, keine Gate-A-Freigabe. Kunta-native-combat120 prueft erstmals den korrigierten nativen Composer auf dieser Stockmap; laeuft. Kurze manuelle Observer-Kameraausrichtung angefragt, weil automatisierte Eingaben keine Gameplay-Actions liefern. C/D/E weiterhin nach den offenen vorherigen Abnahmen.

## Gesicherter Zwischenstand 02.10.2026
Kunta-native-combat120.07s: CRC/Join/Prozessleben PASS,1200TGAs; health100 bei beiden Spielern, geometrisch getrennte Ebenen. contact.png zeigt kein Botmodell. Damit keine weitere visuelle Freigabe.
Alle eigenen Testprozesse und UDP25600/25601 beendet; Bot-/Observer-Displayconfigs und Servermap aus Backups byte-identisch restauriert. Finale DLL weiterhin AA0D07C11D00CF92C4908AA7C0C547AC8E96B32685737469701ACF7F87A37984. Reviewer ohne neue relevante Befunde.
Phase1 NOCH OFFEN. Neu belegt: vier normale Umwelt-Deaths/Respawns mit Actions danach. Noch offen: sichtbare Botbewegung/-rotation und Jitterpruefung, volle Schadenskonsistenz; danach Reconnect, zwei Mapwechsel, regulaerer Shutdown,10/30/60min-Sync. Phase2 nicht begonnen. Benoetigter naechster Schritt: Vanilla-Observer manuell zum Bot ausrichten; automatisierte Tastendruecke erzeugen keine beobachteten Gameplay-Actions. Die Anfrage dazu bleibt ohne Antwort.
Der Quell-/Test-/Dokustand wird als wertvoller Zwischencheckpoint gesichert; Retailkopien, DLLs und TGAs bleiben lokal ausgeschlossen.
