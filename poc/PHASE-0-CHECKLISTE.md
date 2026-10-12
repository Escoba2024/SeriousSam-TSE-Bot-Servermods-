# Phase 0 / 0A – Checkliste: Testbasis & Binary-Inventur

> Bezug: Design-Spec `docs/superpowers/specs/2026-09-30-vanilla-server-bots-design.md` (Phase 0 + 0A) · Ausführung siehe `RUNBOOK.md` · Protokolle: `TESTPROTOKOLL-PHASE-0A.md`, `TESTPROTOKOLL-PHASE-1.md`
> **Ziel von Phase 0:** reproduzierbare, dokumentierte Testumgebung mit **drei sauberen** TSE-1.07-Installationen. **Gate: keine Bot-Implementierung vor abgeschlossener Inventur.**

---

## ⚠️ Wichtigster Punkt vorab

Der bisherige lokale Server lief **mit CecilBotMod** (modifizierte EntitiesMP.dll + Mod-Kennung). Diese Installation kann **keine Vanilla-Clients bedienen** (CRC-/Mod-/Versions-Check → Kick, Belege: `VERIFIKATION.md` Abschnitt 1). Sie wird für Phase 0 **nicht** wiederverwendet. Ebenso: **Auf dem Server bleibt alles vanilla** – insbesondere wird die GameMP.dll auf dem Server **nie** getauscht.

## 0.1 Drei saubere Installationen anlegen

- [ ] `C:\Games\TSE-Server\` – unmodifizierte TSE-1.07-Installation ( Dedicated Server)
- [ ] `C:\Games\TSE-BotClient\` – unmodifizierte Kopie (hier kommt LATER ausschließlich die getauschte GameMP.dll + `Scripts\BotStartup.ini` hinein – erst ab Phase 1, nicht in Phase 0!)
- [ ] `C:\Games\TSE-Observer\` – unmodifizierte Kopie (Beobachter-/Referenz-Client, bleibt für immer unangetastet)
- [ ] Herkunft dokumentieren (Steam/GOG/Retail + Installer-Version)

## 0.2 Version verifizieren (alle drei Installationen)

- [ ] `Data\Var\Sam_Version.var` in einem Texteditor öffnen → muss **1.07** anzeigen
- [ ] Alternativ/zusätzlich: Dateieigenschaften `SeriousSam.exe` (Produktversion)
- [ ] Erwartung: Engine-Build **10000.7** (Beleg für die Bedeutung: `VERIFIKATION.md` Abschnitt 1.2 – der Server vergleicht Major/Minor exakt)

## 0.3 Hash-Inventur

- [ ] `scripts\hash-inventur.bat` für jede der drei Installationen ausführen (Zielordner als Argument)
- [ ] Ergebnisdateien `tse-hash-inventur.txt` im Projektordner (Drive: „Serious Sam TSE Projekt") ablegen
- [ ] Prüfen: `EntitiesMP.dll`, `Engine.dll`, `SeriousSam.exe`, `.gro`-Dateien sind in **allen drei** Installationen identisch (gleiche SHA-256-Werte) – nur so ist der CRC-Check später grün

## 0.4 Server konfigurieren

**Bevorzugter Weg (falls `DedicatedServer.exe` in der Installation enthalten ist):**
- [ ] `scripts\dedicated-config\` (init.ini, 1_begin.ini, 1_end.ini) nach `TSE-Server\Scripts\Dedicated\BotTest\` kopieren und anpassen (Session-Name, Map, `gam_ctMaxPlayers`)
- [ ] Start: `scripts\start-server.bat` bzw. `DedicatedServer.exe BotTest` (Konsolen-Fenster, loggt automatisch nach `Dedicated_BotTest.log`)
- [ ] **`ded_bRestartWhenEmpty = 0`** setzen (Default ist TRUE → Server resettet die Runde, wenn kurzzeitig niemand verbunden ist; für Bot-Betrieb und Phase-0A-Tests störend)
- [ ] Spielmodus: `gam_iStartMode = 2` (Fragmatch/Deathmatch; 0 = Coop, 1 = Scorematch)

**Fallback (ohne DedicatedServer.exe):**
- [ ] `SeriousSam.exe` starten → Multiplayer → New Game → Split-Screen-Auswahl auf **„Dedicated"** → Deathmatch + Map + MaxPlayers setzen → Start (Konsole klappt runter)

**Netzwerk:**
- [ ] Firewall: UDP **25600** (Game) und **25601** (Query) freigeben (Port via `net_iPort` konfigurierbar)
- [ ] Erreichbarkeitstest vom Observer-PC aus

## 0.5 Logging einrichten

- [ ] Server: `DedicatedServer.exe` loggt automatisch (`Dedicated_<config>.log`); beim Menü-Fallback `+logfile <name>` verwenden
- [ ] Observer: normales Spiel-Log reicht; Konsolenbildschirm offen lassen
- [ ] Bot-Client (ab Phase 1): `bot_iLogEvery = 40` in `Scripts\BotStartup.ini` (alle 2 s Position/Heading/Fire im Log)

## 0.6 Wireshark-Baseline (optional, aber empfohlen)

- [ ] Wireshark auf dem Server-PC, Filter `udp port 25600`
- [ ] Capture von Phase 0A (Join, Bewegung, Schießen, Mapwechsel, Disconnect) als Referenz-Pcap archivieren
- [ ] Hinweis aus Claude-II-Quelle: Kompression ggf. per `net_iCompression = 0` deaktivieren, damit Pakete lesbar sind (in der Server-Konsole prüfen, ob das Symbol in 1.07 existiert)

## 0.7 Phase-0-Gate (Abnahme)

- [ ] Drei Installationen vorhanden, Versionen geprüft, Hashes dokumentiert und identisch
- [ ] Server startet reproduzierbar (DedicatedServer.exe oder Menü-Weg), Ports offen
- [ ] Logging läuft
- [ ] **Erst dann:** weiter zu Phase 0A

---

## Phase 0A – Vanilla-Netzwerk-Baseline

Zweck: beweist **die Testumgebung**, nicht den Bot. Ein zweiter normaler Vanilla-Client (Observer) joined und führt reproduzierbar Bewegung/Schießen aus.

Ablauf:
1. Server starten (siehe 0.4)
2. `scripts\start-observer.bat` auf dem Observer-PC anpassen (IP/Port) und starten
3. Reihefolge testen: Join → Playerliste/Scoreboard → Bewegung → Schießen → Schaden/Frag/Respawn → Mapwechsel → Disconnect → Reconnect
4. Alles in `TESTPROTOKOLL-PHASE-0A.md` festhalten; Server-Log sichern

**Gate 0A:** alle Punkte PASS → **Phase 1 (PoC, 1 Bot)** beginnt mit dem GameMP-Build laut `RUNBOOK.md` Schritt 1–3.
