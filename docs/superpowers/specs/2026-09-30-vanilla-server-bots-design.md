# Serious Sam TSE 1.07 Vanilla Bots – Design Specification

## Status / Architektur-Update 30.09.2026

Diese Fassung ersetzt die ursprüngliche Präferenz für einen rein serverseitigen `ServerBotController`.

Nach Abgleich der bisherigen Projektquellen (Gemini Deep Research, Claude-Gegenprüfung, Kroc Deep Research und Claude Deep Research II) sowie zusätzlicher direkter Prüfung des öffentlichen SE1-ModSDK gilt jetzt:

- **Primärpfad: Pfad D – echter Bot-Client mit regulären lokalen Spielern.**
- **Fallback: Pfad B2 – virtueller PlayerBuffer/PlayerTarget direkt im Server.**
- **Verworfen als Primärpfad: CecilBot-/eigene Bot-Entity in der synchronisierten Welt.**
- **Nur Ergänzung, nicht Endlösung: Serverbrowser-/Query-Fake-Count.**

Vanilla-Kompatibilität bleibt ein hartes Gate. Pfad D ist technisch gut belegt, aber erst nach einem echten TSE-1.07-PoC experimentell bestätigt.

## Ziel

Mehrere Serious Sam: The Second Encounter 1.07 Dedicated Server sollen autonome Bots betreiben, während unveränderte Vanilla-TSE-1.07-Clients ohne Modinstallation beitreten können.

Bots sollen:

- als reguläre Netzwerkspieler erscheinen;
- echte Slots belegen;
- im Scoreboard und möglichst automatisch im Serverbrowser/Playerstatus erscheinen;
- eigenständig bewegen, zielen, schießen, Schaden verursachen, sterben und respawnen;
- später kontrolliert joinen/leaven, chatten und durch eine Populationslogik verwaltet werden.

CecilBotMod dient nur als KI-/Navigationsreferenz und nicht als Netzwerkarchitektur.

## Harte Anforderungen

- Menschliche Clients bleiben **Vanilla TSE 1.07**; kein CecilBotMod, eigener Mod-Ordner oder zusätzliche Client-DLLs.
- Der Dedicated Server bleibt im Primärpfad möglichst unverändert.
- Bot-Logik darf in **separaten Bot-Client-Prozessen** laufen. Die frühere Vorgabe „ausschließlich serverseitig“ ist aufgehoben.
- Bots müssen über den normalen Netzwerkspieler-/Action-Pfad teilnehmen.
- Keine neuen synchronisierten Entity-Klassen oder Bot-Entities, die Vanilla-Clients nicht kennen.
- Keine Änderung an Session-RNG/`IRnd()` durch Bot-KI.
- Kein global künstlich erhöhter `GetPlayersCount()`.
- 1.10-Engine-Quellen sind Referenz/Landkarte, nicht Beweis für 1.07-Binary-Kompatibilität.
- Jede Entwicklungsstufe benötigt einen reproduzierbaren Test mit einem **unveränderten TSE-1.07-Beobachter-Client**.
- Von CecilBotMod übernommener oder abgeleiteter GPLv2-Code muss Lizenz- und Attribution-Pflichten beibehalten.

## Bestätigte technische Basis

### Lockstep / Action-Netcode

Die Serious Engine verteilt pro Spieltick Spieleraktionen und simuliert die Welt bei allen Teilnehmern deterministisch. `MSG_SEQ_ALLACTIONS` enthält pro aktivem Spieler eine `CPlayerAction`. Sync-Checks erkennen abweichende Simulationen.

Konsequenz: Ein Bot darf für Vanilla-Kompatibilität keine zusätzliche nur serverseitig bekannte Simulations-Entity benötigen. Er soll stattdessen ein regulärer Spieler sein, dessen Aktionen programmgesteuert erzeugt werden.

### `CPlayerAction`

Relevante Felder:

- `pa_vTranslation`
- `pa_aRotation`
- `pa_aViewRotation`
- `pa_ulButtons`
- `pa_llCreated`

### Action-Erzeugung im öffentlichen TSE-SDK/SE1-ModSDK

Direkt im SE1-ModSDK bestätigt:

- `ctl_ComposeActionPacket(const CPlayerCharacter&, CPlayerAction&, BOOL)` ist als `DECL_DLL` deklariert/implementiert.
- `ctl_pvPlayerControls` und `ctl_slPlayerControlsSize` sind als DLL-Schnittstellen vorhanden.
- `CControls::CreateAction(...)` ruft `ctl_ComposeActionPacket(...)` auf.
- `CGame` besitzt `gm_lpLocalPlayers[4]`; das öffentliche Quellmodell sieht damit bis zu vier lokale Spieler pro Prozess vor.

Noch **nicht bestätigt** ist, ob die tatsächlich eingesetzte TSE-1.07-Retail-/Steam-`EntitiesMP.dll` diese Symbole in einer für den geplanten Hook geeigneten Form exportiert. Das muss an der echten Binary geprüft werden.

## Warum CecilBotMod nicht die Netzwerkarchitektur ist

CecilBotMod verwaltet Bots separat (`_aPlayerBots`) und ersetzt an vielen Stellen Vanilla-Zugriffe durch Bot-spezifische Varianten wie `CECIL_GetMaxPlayers`, `CECIL_GetPlayerEntity`, `CECIL_PlayerIndex` und `IS_PLAYER`.

Zusätzlich werden `PlayerBot.es`, `BotModGlobal.es`, `NavMeshGenerator.es` und weitere Game-/HUD-Pfade integriert. Der Autor warnt selbst vor Integration mit Serious Sam Classics Patch wegen kollidierender Netzwerkfunktionalität und möglichem undefiniertem Verhalten.

Daher:

- `CPlayerBot`/Bot-Entities nicht als Produktions-Netzwerkspieler verwenden;
- keine NavMesh-Entity in der synchronisierten Welt für den Vanilla-PoC;
- CecilBotMod nur als Quelle für KI, Zielwahl, Waffenlogik, Wegfindung, Namen und Verhalten nutzen.

## Architekturentscheidung

### Primärer Ansatz: Pfad D – Bot-Client mit regulären lokalen Spielern

Ein separater TSE-1.07-Client-Prozess joint einen normalen Dedicated Server. Der Client meldet einen oder mehrere lokale Spieler an. Diese Spieler sind normale Netzwerkspieler; lediglich die Erzeugung ihrer `CPlayerAction` wird programmgesteuert.

Vorteile:

- normaler Connect-/Handshake-/State-Delta-Pfad;
- normale Player-Slots;
- normale `ADDPLAYER`-/Action-Verarbeitung;
- Kartenwechsel/Reconnect laufen über echten Client-Code;
- der Dedicated Server benötigt für den ersten PoC keinen Bot-Patch;
- Vanilla-Beobachter sehen normale Spieler, sofern der PoC die Kompatibilität bestätigt;
- echte Slots sollten Serverbrowser-/Playerstatus natürlicher abbilden als synthetische Fake-Counts.

Erster bevorzugter Eingriffspunkt:

1. echte 1.07-Exporttabelle prüfen;
2. falls geeignet, `ctl_ComposeActionPacket` im **Bot-Client** hooken;
3. Originalfunktion aufrufen, um normales Bookkeeping zu behalten;
4. anschließend nur die Action-Felder für den Bot überschreiben;
5. `bPreScan`-Semantik vor finaler Implementierung im echten 1.07-Pfad prüfen.

Alternative Eingriffspunkte:

- `PlayerControls`/Control-Symbole manipulieren;
- falls pro lokalem Spieler notwendig, Game-/Controls-Schicht vor `ctl_ComposeActionPacket` hooken.

### Lokale Spieler / Skalierung

Das öffentliche SE1-ModSDK definiert `gm_lpLocalPlayers[4]`.

Arbeitsannahme:

- bis zu 4 Bot-Spieler pro Bot-Client-Prozess;
- mehr Bots über mehrere Bot-Client-Prozesse;
- tatsächliches Runtime-Verhalten mit TSE 1.07 muss getestet werden.

Nicht versuchen, das 4er-Limit im ersten PoC zu erweitern.

### GUID / Profile

Jeder Bot-Spieler muss als eigenständiger Charakter/Netzwerkspieler erscheinen.

Zu prüfen:

- Entstehung der GUID im echten 1.07-Profil-/Character-Pfad;
- ob mehrere lokale Spieler automatisch unterschiedliche GUIDs besitzen;
- Verhalten bei Reconnect/Mapwechsel.

Keine GUID-Annahmen ungeprüft hardcoden.

### Navigation / KI

Navigation und KI sollen im Bot-Client außerhalb der synchronisierten Welt laufen.

Regeln:

- Weltzustand nur lesen;
- keine synchronisierten Entities erzeugen oder verändern;
- kein Session-RNG verwenden;
- eigener Bot-PRNG;
- externe Waypoints/Nav-Daten pro Map sind erlaubt, sofern sie nur den Bot-Client betreffen;
- zuerst einfache Action-Injektion ohne NavMesh/KI beweisen.

### Headless / Ressourcen

Erste Version darf ein normaler minimierter Client mit niedriger Grafiklast sein.

Headless/Custom-Client ist eine spätere Optimierung und kein PoC-Gate.

Zu messen:

- CPU/RAM pro Bot-Client-Prozess;
- Netzlast;
- Stabilität bei mehreren Prozessen;
- Mapwechsel/Reconnect;
- Langzeit-Sync.

## Fallback: Pfad B2 – virtueller PlayerBuffer im Server

Falls mehrere Bot-Client-Prozesse langfristig zu teuer oder unpraktisch sind, kann ein zweiter Architekturpfad untersucht werden:

- Server erzeugt intern reguläre PlayerBuffer-/PlayerTarget-Strukturen;
- pro Tick werden normale `CPlayerAction`s eingespeist;
- Vanilla-Clients sehen weiterhin normale Player-Slots.

Risiken:

- tiefes Reverse Engineering der echten 1.07-Engine-Binary;
- `CServer` / `CSessionSocket` / Timeouts;
- Sync-Check-Verhalten ohne echten Remote-Client;
- Ping-/Status-/Disconnect-Semantik;
- höhere Crash-/Kompatibilitätsgefahr.

B2 wird **nicht** vor Pfad-D-PoC umgesetzt.

## Nicht-Ziel: Pfad C – reine Browser-/Query-Fälschung

Eine nur künstlich erhöhte Spielerzahl löst nicht das Ziel spielender Bots.

Bei Pfad D wird zuerst erwartet, dass echte Bot-Spieler-Slots vom Status-Query normal erfasst werden. Nur falls reale Browserdaten trotz echter Player-Slots unvollständig sind, wird die Query-Schicht gezielt ergänzt.

## Serverbrowser / 333networks

333networks beschreibt den klassischen Ablauf so:

1. Masterserver liefert Serveradressen/Query-Ports.
2. Der Client fragt anschließend die Gameserver direkt nach Detailstatus.
3. Der Status enthält u. a. Map/Regeln/aktive Spieler und Scores.

Daher soll beim Pfad-D-PoC mit einer echten Live-Query geprüft werden, ob Bot-Spieler automatisch erscheinen.

Keine Browser-Fälschung implementieren, bevor diese Messung vorliegt.

## Versionsregel 1.07 vs. 1.10

- Croteams vollständiger Open-Source-Stand ist 1.10.
- TSE 1.07 besitzt nur SDK-Teilquellen + Binaries.
- Das SE1-ModSDK warnt, dass bereits kleine Logikabweichungen Desync verursachen können.
- 1.10-Code dient daher nur zur Orientierung.
- Protokoll-/Struct-/Message-Annahmen müssen gegen echte TSE-1.07-Binaries oder einen realen Packet-Capture geprüft werden.

Hinweis zur Switch-Port-Quelle: Deren Release-Notes belegen, dass Stock-Demos desyncen können und Network-Multiplayer in diesem Port nicht funktioniert. Sie belegen **nicht** hinreichend die spezifische Aussage, ein 1.10-Client könne grundsätzlich keine 1.07-PC-Server joinen. Diese Aussage bleibt offen.

## Entwicklungsphasen und Gates

### Phase 0 – Testbasis / Binary-Inventur

Ziel:

- Vanilla TSE 1.07 Dedicated Server reproduzierbar starten;
- unveränderten Beobachter-Client festlegen;
- Bot-Client-Installation separat anlegen;
- Versionen/Hashes/Binaries dokumentieren;
- Exporttabelle der echten `EntitiesMP.dll` prüfen;
- Logging und optional Wireshark-Basis herstellen.

Gate: Keine Hook-Implementierung, bevor echte 1.07-Binary und Symbol-/Hook-Pfad inventarisiert sind.

### Phase 0A – Vanilla-Netzwerk-Baseline

Ein zweiter normaler Vanilla-Client joint den Server und führt reproduzierbar Bewegung/Schießen aus.

Prüfen:

- Join;
- Playerliste/Scoreboard;
- Schaden/Frag/Respawn;
- Mapwechsel;
- Disconnect/Reconnect;
- Logging.

Dies beweist noch keinen Bot, aber die Testumgebung.

### Phase 1 – Pfad-D-PoC mit genau einem Bot-Spieler

Bot-Client joint als normaler Client mit einem lokalen Spieler.

Minimaler Action-Generator:

- konstant vorwärts;
- langsame reproduzierbare Rotation;
- periodisches `PLACT_FIRE`;
- kein NavMesh;
- keine CecilBot-Entity;
- kein Chat;
- kein Population Manager.

Pflichttests:

- Vanilla-Beobachter kann ohne Mod joinen;
- Bot erscheint als normaler Spieler;
- Bewegung/Blickrichtung sichtbar;
- Schießen sichtbar;
- Schaden/Frag funktionieren;
- Tod/Respawn funktioniert;
- Mapwechsel funktioniert;
- Disconnect/Reconnect sauber;
- eindeutige Character-/GUID-Zuordnung;
- mindestens 60 Minuten ohne `MSG_SYNCCHECK`-Kick, Desync oder Crash.

Gate: Erst danach mehrere lokale Bot-Spieler.

### Phase 2 – 2 bis 4 lokale Bot-Spieler

- mehrere lokale Spieler im selben Bot-Client aktivieren;
- pro Spieler unabhängige Actions;
- GUID/Profile prüfen;
- Scoreboard/Playerstatus prüfen;
- Mapwechsel/Reconnect testen.

Gate: 4-Spieler-Prozess stabil, bevor Multiprocess skaliert wird.

### Phase 3 – Multiprocess / Skalierung

- 2 Bot-Client-Prozesse × bis zu 4 Spieler;
- danach schrittweise erhöhen;
- parallel echte menschliche Clients joinen/leaven lassen;
- CPU/RAM/Netz messen;
- Serverbrowser-Live-Query prüfen.

### Phase 4 – einfache KI / externe Navigation

Erst nach stabiler Action-Injektion:

- Targeting;
- Waffenwahl;
- einfache Waypoints/Sichtlinien;
- später CecilBot-KI selektiv portieren.

Keine CecilBot-spezifischen Simulations-Entities übernehmen.

### Phase 5 – Population Manager

Zielpopulation verwalten:

- Human-Slots priorisieren;
- Bots kontrolliert disconnecten, wenn Menschen Platz benötigen;
- Bots später wieder verbinden;
- keine künstliche `GetPlayersCount()`-Semantik.

### Phase 6 – Presence / Chat

Erst nach stabiler Population:

- Join-/Leave-Verzögerungen;
- Namensprofile;
- niedrige Chat-Frequenz;
- keine permanent identischen Muster.

### Phase 7 – mehrere Dedicated Server

- getrennte Ports;
- getrennte Bot-Client-Gruppen/Profile;
- getrennte Zielpopulationen;
- gemeinsamer Code, instanzspezifische Config;
- reproduzierbarer Start/Stop.

## Abbruchkriterium pro Teststufe

Jeder der folgenden Punkte stoppt die aktuelle Stufe:

- `MSG_SYNCCHECK`-Kick;
- sichtbarer Desync;
- Crash;
- Doppel-Entity/GUID-Kollision;
- Bot wird nicht als regulärer Spieler behandelt.

Erst Ursache dokumentieren und beheben, dann skalieren.

## Aktuell zuerst zu untersuchende Dateien/Funktionen

### TSE/SE1-ModSDK

- `Sources/EntitiesMP/Player.es`
  - `ctl_ComposeActionPacket`
  - `PlayerControls`
  - `ctl_pvPlayerControls`
  - `ctl_slPlayerControlsSize`
- Game-/Controls-Code
  - `CControls::CreateAction`
  - lokale Spieler-Konfiguration
  - `gm_lpLocalPlayers`
  - Join-/Split-Screen-Pfad
- echte TSE-1.07-`EntitiesMP.dll`
  - Exporttabelle
  - Symbolnamen
  - Hookbarkeit

### Netzwerk als Referenz

- `CPlayerSource`
- `CPlayerBuffer`
- `CPlayerTarget`
- `CSessionState`
- `CServer`
- `CSessionSocket`

1.10-Netzcode nur als Landkarte; 1.07-Binary hat Vorrang.

### Classics Patch

- `Core/` – vorhandene dynamische Engine-Hooks
- `Extensions/Sample` – Plugin-API
- prüfen, ob vorhandene Hook-Infrastruktur für den Bot-Client nutzbar ist

### CecilBotMod

Nur KI-/Verhaltensreferenz:

- `PlayerBot.es`
- `BotModGlobal.es`
- `NavMeshGenerator.es`
- `Bots/*`

## Geplante Repository-Struktur

Die Struktur wird erst nach bestandenem PoC konkretisiert.

```text
SeriousSam-TSE-Bot-Servermods-/
  docs/
    PROJECT_STATE.md
    ARCHITECTURE.md
    COPY_INSTRUCTIONS.md
    superpowers/
      specs/
      plans/
  src/
    BotClientHook/
    BotActionGenerator/
    BotAI/
    PopulationManager/
  tests/
  tools/
```

## Copy-/Reproduzierbarkeitsprinzip

Jede relevante Änderung erhält:

- eindeutige Quelldatei bzw. Hook-/Patchdatei;
- Zielprozess (Bot-Client oder Server);
- genaue Integrationsanweisung;
- Test, der die Funktion beweist;
- Commit/PR mit nur einer logisch abgegrenzten Änderung.

`COPY_INSTRUCTIONS.md` soll später so präzise sein, dass eine andere KI oder ein Entwickler den funktionierenden Stand ohne Chat-Historie reproduzieren kann.

## Nicht-Ziele der ersten Implementierungsrunde

- kein CecilBotMod-`+game` als Produktionslösung;
- keine eigene Bot-Entity im Vanilla-PoC;
- keine Serverbrowser-Fake-Spielerzahl vor realem Player-Slot-Test;
- kein Chat im ersten PoC;
- keine KI/NavMesh vor funktionierender Action-Injektion;
- kein >4-Local-Player-Patch;
- kein Headless-Umbau als Voraussetzung;
- kein B2-Engine-Reverse-Engineering, solange Pfad D nicht getestet wurde.

## Definition of Done für das Gesamtprojekt

Das Projekt gilt als technisch erreicht, wenn:

1. mehrere TSE-1.07-Dedicated-Server unabhängig laufen;
2. unveränderte Vanilla-Clients direkt joinen können;
3. Bots als reguläre Netzwerkspieler eigenständig spielen;
4. Bots in Serverbrowser, Playerliste und Scoreboard konsistent erscheinen;
5. Menschen Bot-Slots automatisch verdrängen können;
6. Bots zeitversetzt zurückkehren;
7. Join/Leave/Chat konfigurierbar funktionieren;
8. der komplette Build-/Hook-/Integrationsprozess aus GitHub + Dokumentation reproduzierbar ist;
9. alle wesentlichen Änderungen über Tests und Commits nachvollziehbar sind.

## Offene Forschungsfragen vor PoC-1

- Exportiert die tatsächlich eingesetzte 1.07-`EntitiesMP.dll` `ctl_ComposeActionPacket`, `ctl_pvPlayerControls` und `ctl_slPlayerControlsSize` in hookbarer Form?
- Welche genaue Bedeutung hat `bPreScan` im realen 1.07-Aufrufpfad?
- Wie wird pro lokalem Spieler die Action-/Controls-Instanz getrennt?
- Wie entstehen GUIDs für mehrere lokale Spieler/Profile?
- Bleiben lokale Spieler nach Mapwechsel/Reconnect sauber registriert?
- Welche Classics-Patch-Hooks können ohne unnötige Netzwerkänderungen im Bot-Client wiederverwendet werden?
- Welche Ressourcenlast entsteht bei mehreren vollständigen Bot-Client-Prozessen?
- Meldet der eingesetzte 1.07-Status-/333networks-Pfad alle Bot-Spieler automatisch korrekt?
- Welche Teile der CecilBotMod-KI lassen sich ohne Entity-Kopplung extrahieren?

## Empfohlener nächster Schritt

**Keine vollständige Bot-KI implementieren.**

1. Echte TSE-1.07-Binaries und Exporttabellen inventarisieren.
2. Vanilla Dedicated Server + unveränderten Beobachter-Client als reproduzierbare Baseline testen.
3. Hook-Punkt im Bot-Client verifizieren.
4. PoC-1 mit genau einem Action-gesteuerten regulären Spieler implementieren.
5. 60-Minuten-Sync-/Mapwechsel-/Reconnect-Test bestehen.
6. Erst danach 2–4 lokale Bots und Multiprocess.
