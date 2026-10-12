> Historische manuelle Prüfcheckliste. Aktuelle bestandene Gates und automatisierter Release-Ablauf: `../docs/reports/2026-10-12-shadow-development-status.md` und `LOCAL-RELEASE.md`. BAT-Vorlagen benötigen manuell passende Installationspfade; Start allein ist kein Join-/CRC-Nachweis.

# Anleitung – Phase 2 (2–4 Bots pro Client) und Phase 3 (mehrere Bot-Client-Prozesse)

> Voraussetzung: Phase-1-Gate bestanden (`TESTPROTOKOLL-PHASE-1.md`). Der BotDriver bedient bereits alle 4 lokalen Spieler-Slots (Schleife über `gm_lpLocalPlayers[0..3]`) – es ist **keine Code-Änderung** nötig.

## Phase 2 – 2 bis 4 lokale Bot-Spieler in einem Prozess

### 1. Split-Screen-Konfiguration (einmalig im Bot-Client)

1. `TSE-BotClient\Bin\SeriousSam.exe` starten (normal, ohne `+connect`)
2. Menü → **Players/Split Screen**: gewünschte Anzahl Spieler wählen (**2P/3P/4P**; entspricht `SSC_PLAY2..4`)
3. Für **jeden** Spieler-Slot ein eigenes Spielerprofil/Character anlegen (eigener Name, ggf. eigenes Aussehen) – das ist die Grundlage für eindeutige GUIDs
4. Menü verlassen; die Einstellungen werden mit den Game-Settings gespeichert. **Achtung:** nach Neustart prüfen, ob die Auswahl persistsiert; falls nicht, vor jedem Join erneut setzen (dann erfolgt der Join-Schritt über das Menü statt `+quickjoin`)

### 2. Joinen

```
SeriousSam.exe +connect <server-ip>:25600 +quickjoin +script Scripts\BotStartup.ini
```

Alle konfigurierten lokalen Spieler joinen gemeinsam (1 Client-Verbindung, N Player-Slots; Server bucht jeden Slot – Beleg `VERIFIKATION.md` Abschnitt 2, Zeile 8).

### 3. Prüfungen (Gate Phase 2)

- [ ] Server-Log: „Adding player …" für **jeden** lokalen Spieler, je eigener Index
- [ ] Alle 2–4 Bots im Scoreboard mit **unterschiedlichen Namen**
- [ ] Alle bewegen sich (BotDriver nutzt Phasen-Offset pro Feuerpuls, damit es nicht synchron wirkt)
- [ ] GUID-Einzigartigkeit: bei Reconnect werden die Characters wiedererkannt (Server-Log prüfen)
- [ ] Sync/Performance mit 4 Spielern in einem Prozess (20 Hz Action-Loop × 4)

**Grenze:** 4 lokale Spieler pro Client sind hardcodiert (`NET_MAXLOCALPLAYERS = 4`, `gm_lpLocalPlayers[4]`) – **nicht** versuchen zu erweitern (Vorgabe der Design-Spec).

## Phase 3 – Skalierung über mehrere Bot-Client-Prozesse

### 1. Installationen vorbereiten

Pro weiterem Bot-Client eine **eigene vollständige Installation** (nicht nur ein Kopie-Vorgang im laufenden Betrieb):
- `C:\Games\TSE-BotClient-2\`, `-3\`, `-4\` …
- je: unmodifizierte 1.07-Basis + getauschte GameMP.dll (identischer Build wie BotClient 1) + `Scripts\BotStartup.ini`
- je: eigenes Spielerprofil/Name im Menü setzen (einmalig), damit die Bots unterscheidbar sind
- Hash-Inventur je Installation (identische EntitiesMP/Daten!)

### 2. Starten

`scripts\start-all-bots.bat` anpassen (`BASE`, `SERVER_IP`, `SERVER_PORT`, Anzahl) und ausführen – startet alle gefundenen Bot-Clients gestaffelt (5 s Abstand, damit Joins die Server-Session nicht gleichzeitig belasten).

### 3. Prüfungen (Gate Phase 3)

- [ ] 8 Bots (2 Prozesse) → dann 12/16 nach Bedarf: alle als normale Spieler sichtbar
- [ ] Gesamtlimit: **16 Spieler** (`NET_MAXGAMEPLAYERS`) – Bots + echte Spieler zusammen
- [ ] Serverbrowser-Count stimmt mit echter Slot-Belegung überein
- [ ] Ressourcenlast beobachten: jeder Bot-Client ist ein voller Game-Client (RAM/CPU/GPU); Fenster minimiert starten; Notfall: Anzahl reduzieren oder später headless (Engine-Eingriff, **nicht** in Phase 3)
- [ ] `ded_bRestartWhenEmpty = 0` auf dem Server bleibt gesetzt
- [ ] 60 min Stabilität mit voller Bot-Zahl

### 4. Betriebshinweise

- **Slot-Freigabe für echte Spieler** ist erst Phase 5 (Population Manager). Bis dahin: `gam_ctMaxPlayers` so wählen, dass immer freie Slots bleiben (z. B. 16 Slots, 10 Bots → Beispielverhalten aus dem Projektprotokoll).
- Server-Restart/Mapwechsel: alle Bot-Clients reconnecten automatisch (`gam_strJoinAddress`) – gestaffelte Starts vermeiden Lastspitzen.
- Ein Absturz eines Bot-Clients betrifft nur dessen eigene Bots (die anderen Prozesse bleiben verbunden).
