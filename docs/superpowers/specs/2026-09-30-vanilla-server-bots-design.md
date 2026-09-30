# Serious Sam TSE 1.07 Vanilla Server Bots – Design Specification

## Ziel

Mehrere Serious Sam: The Second Encounter 1.07 Dedicated Server sollen serverseitig autonome Bots betreiben, während unveränderte Vanilla-TSE-1.07-Clients ohne Modinstallation beitreten können. Bots sollen später wie normale Spieler in Serverbrowser und Playerliste erscheinen, eigenständig spielen, joinen/leaven, chatten und durch eine Populationslogik verwaltet werden.

## Harte Anforderungen

- Client-Seite bleibt Vanilla TSE 1.07; keine CecilBotMod-Installation beim Spieler.
- Server soll möglichst als normaler TSE-1.07-Server erscheinen und nicht als eigener +game-Mod voraussetzen.
- Bot-Logik läuft ausschließlich serverseitig.
- Serverinterne reale Netzwerkspielerzahl darf nicht mit einer künstlich gemeldeten Browser-Spielerzahl vermischt werden.
- Mehrere Dedicated-Server-Instanzen müssen später mit getrennten Konfigurationen betrieben werden können.
- Echte Spieler dürfen nie durch die Bot-Zielpopulation ausgesperrt werden.
- Jede Entwicklungsstufe benötigt einen reproduzierbaren Test, bevor die nächste Stufe beginnt.
- Von CecilBotMod übernommener oder abgeleiteter GPLv2-Code muss Lizenz- und Attribution-Pflichten beibehalten.

## Architekturentscheidung

### Primärer Ansatz: ServerBotController auf Vanilla-Spielerpfad

Die bevorzugte Architektur übernimmt nur die benötigten Bot-Ideen bzw. zulässigen Bot-Logik-Bausteine aus CecilBotMod und bindet sie serverseitig an möglichst normale Vanilla-Spielerobjekte an. Der Bot erzeugt intern CPlayerAction-kompatible Eingaben; Netzwerk-, Entity- und Replikationspfade sollen so nah wie möglich an Vanilla bleiben.

Ziel ist, dass ein unveränderter Client lediglich einen normalen Spieler wahrnimmt, dessen Eingaben vom Server statt von einem menschlichen Netzwerkclient stammen.

### Sekundärer Ansatz: CecilBot-Entity kompatibel machen

Nur falls der primäre Ansatz nicht praktikabel ist, wird geprüft, ob die existierende CPlayerBot-Entity aus CecilBotMod serverseitig so eingesetzt werden kann, dass Vanilla-Clients synchron bleiben. Hinweis aus dem CecilBotMod-Code: CPlayerBot verwendet absichtlich dieselbe Entity-ID wie der Vanilla-Player. Das ist ein positives Signal, aber kein Kompatibilitätsbeweis.

### Fallback: synthetische Netzwerkspieler

Falls weder der normale Vanilla-Spielerpfad noch die kompatible CecilBot-Entity ausreichen, werden Bots tiefer als synthetische Netzwerkspieler in die PlayerBuffer-/PlayerTarget-Pipeline eingebunden. Dieser Weg ist technisch invasiver und wird nur als Fallback verfolgt.

## Komponenten

### 1. VanillaBotController

Verantwortung:
- erzeugt serverseitige Spieleraktionen für einen Bot;
- verwaltet Bot-Zustand und KI-Tick;
- nutzt möglichst Vanilla-kompatible CPlayer-/CPlayerAction-Pfade;
- enthält keine Serverbrowser-Fälschungslogik.

### 2. BotSlotManager

Verantwortung:
- kennt aktive Bots getrennt von echten Netzwerkspielern;
- reserviert reale Slots für Menschen;
- liefert BotCount und verwaltete Bot-Identitäten;
- verhindert, dass Browser-Zählung in Netzwerkspieler-Schleifen gelangt.

### 3. ServerBrowserAdapter

Verantwortung:
- berechnet ausschließlich den nach außen gemeldeten Spielerstand;
- AdvertisedPlayerCount = RealHumanCount + ActiveBotCount, gedeckelt auf maxplayers;
- erweitert später Player-Detailantworten um Botnamen, Frags und Pingwerte;
- verändert niemals globale GetPlayersCount()-Semantik.

### 4. PopulationManager

Verantwortung:
- hält eine konfigurierbare Zielpopulation;
- entfernt Bots zeitversetzt, wenn Menschen joinen;
- fügt Bots zeitversetzt wieder hinzu, wenn Menschen leaven;
- behält einen konfigurierbaren Human-Slot-Puffer.

### 5. BotChat / Presence

Spätere Stufe:
- Join/Leave-Zeitpunkte variieren;
- Botnamen rotieren kontrolliert;
- gelegentliche serverseitig erzeugte Chat-Nachrichten;
- keine unrealistisch statischen Verhaltensmuster.

## Zentrale Sicherheitsregel zur Spielerzahl

Es ist ausdrücklich verboten, global GetPlayersCount() durch eine künstlich erhöhte Zahl zu ersetzen.

Begründung: Engine-Code kann die Rückgabe als Indexgrenze für reale PlayerBuffer/PlayerTarget-Strukturen verwenden. Eine gemeldete 10 bei tatsächlich 2 Netzwerkspielern könnte zu ungültigen Indizes, fehlerhaften Playerdaten oder Crashes führen.

Daher müssen mindestens drei getrennte Größen existieren:

- RealHumanCount
- ActiveBotCount
- AdvertisedPlayerCount

Nur Serverbrowser-/Statusantworten dürfen AdvertisedPlayerCount verwenden.

## Entwicklungsphasen und Gates

### Phase 0 – reproduzierbare Build-Basis

Ziel:
- TSE-1.07-Quellbasis und Build-Toolchain reproduzierbar aufsetzen;
- unveränderte relevante DLLs/Serverkomponenten bauen;
- bestehenden Dedicated Server mit selbstgebauten Binärdateien starten;
- vor jedem Bot-Patch einen bekannten funktionierenden Baseline-Build besitzen.

Gate: Kein Feature-Patch beginnt, solange Baseline-Build und Vanilla-Join nicht reproduzierbar funktionieren.

### Phase 1 – Vanilla-Bot-PoC

Genau ein Bot, ein Dedicated Server, ein unveränderter Vanilla-TSE-1.07-Client.

Pflichttests:
- Client kann ohne Mod joinen;
- Bot ist sichtbar;
- Bot bewegt sich;
- Bot schießt;
- Treffer/Schaden funktionieren;
- Bot kann sterben und respawnen;
- mindestens ein längerer Testlauf ohne offensichtlichen Desync oder Crash;
- keine clientseitige CecilBotMod-Datei erforderlich.

Gate: Erst nach Bestehen dieser Tests darf Serverbrowser-/Playerlistenarbeit beginnen.

### Phase 2 – Serverbrowser-Spielerzahl

Pflichttests:
- 0 Humans + 8 Bots => 8/16;
- 1 Human + 8 Bots => 9/16;
- AdvertisedPlayerCount niemals > maxplayers;
- Human join/leave ohne Crash;
- interne Netzwerkspieler-Schleifen verwenden weiterhin reale Spielerzahl.

### Phase 3 – Player-Detailantwort

Pflichttests:
- Botnamen erscheinen in Browsern, die Player-Detailqueries unterstützen;
- echte Menschen bleiben unverändert gelistet;
- Bot-Frags/Ping sind konsistent und verursachen keine Indexzugriffe auf nicht existierende Netzwerkspieler.

### Phase 4 – dynamische Population

Beispiel:
- maxplayers = 16;
- targetPopulation = 10;
- humanReserve = 4.

Verhalten:
- 0 Humans => bis zu 10 Bots;
- 1 Human => Population Richtung 10 nachregeln;
- steigende Human-Zahl verdrängt Bots;
- Bots kehren nach konfigurierbarer Zufallsverzögerung zurück;
- HumanReserve wird nie von Bots blockiert.

### Phase 5 – Presence/Chat

Erst nach stabiler Population:
- zufällige Join-/Leave-Verzögerungen;
- Namensprofile;
- Chat mit niedriger Frequenz;
- keine permanent identischen Muster.

### Phase 6 – mehrere Dedicated Server

- getrennte Ports;
- getrennte Bot-Profile;
- getrennte Zielpopulationen;
- gemeinsamer Code, instanzspezifische Config;
- reproduzierbare Start-/Stop-Konfiguration.

## Geplante Repository-Struktur

Die Struktur wird erst nach Freigabe des Implementierungsplans angelegt.

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
    VanillaBotController/
    BotSlotManager/
    ServerBrowserAdapter/
    PopulationManager/
  patches/
  tests/
```

## Copy-Overlay-Prinzip

Das Repository soll nicht zu einem undurchsichtigen Komplett-Fork werden. Jede relevante Änderung erhält:

- eindeutige Quelldatei bzw. Patchdatei;
- Zielpfad im TSE-Projekt;
- kurze Integrationsanweisung;
- Test, der beweist, dass die Änderung funktioniert;
- Commit/PR, der nur eine logisch abgegrenzte Änderung enthält.

COPY_INSTRUCTIONS.md soll später so präzise sein, dass eine andere KI oder ein Mensch den funktionierenden Stand reproduzieren kann, ohne die gesamte Chat-Historie zu kennen.

## Nicht-Ziele der ersten Implementierungsrunde

- kein Chat-System im ersten PoC;
- keine künstliche Browser-Spielerzahl vor bewiesenem Vanilla-Bot-PoC;
- kein Multi-Server-Orchestrator vor stabilem Einzelserver;
- keine globale Veränderung von GetPlayersCount();
- keine clientseitige Mod-Pflicht;
- kein Hex-Editing, solange ein nachvollziehbarer Quellcode-Patch möglich ist.

## Definition of Done für das Gesamtprojekt

Das Projekt gilt als technisch erreicht, wenn:

1. mehrere TSE-1.07-Dedicated-Server unabhängig laufen;
2. unveränderte Vanilla-Clients direkt joinen können;
3. Bots serverseitig eigenständig spielen;
4. Bots in Serverbrowser und Playerliste konsistent erscheinen;
5. Menschen Bot-Slots automatisch verdrängen können;
6. Bots zeitversetzt zurückkehren;
7. Join/Leave/Chat konfigurierbar funktionieren;
8. der komplette Build- und Integrationsprozess aus GitHub + Dokumentation reproduzierbar ist;
9. alle wesentlichen Änderungen über Tests und Commits nachvollziehbar sind.

## Offene Forschungsfragen vor Implementierung

- Welcher konkrete Vanilla-Spieler-/Input-Pfad eignet sich am besten, um serverseitige CPlayerAction-Eingaben ohne echten Netzwerkclient einzuspeisen?
- Welche Engine-/GameDLL-Teile müssen dafür minimal verändert werden?
- Bleibt eine serverseitig erweiterte CPlayer-Implementierung für Vanilla-Clients vollständig synchron?
- Welche Serverbrowser-Protokollvariante nutzt das tatsächlich eingesetzte TSE-1.07-Setup?
- Welche Teile der CecilBotMod-KI lassen sich mit minimaler Kopplung wiederverwenden?
- Welche GPLv2-Dateien werden tatsächlich übernommen oder abgeleitet und müssen entsprechend gekennzeichnet werden?

## Empfohlener nächster Schritt

Nach Freigabe dieser Spezifikation wird ein Implementierungsplan erstellt. Der Plan beginnt mit Phase 0 und Phase 1, enthält exakte Dateien, Integrationspunkte, Tests und Commit-Grenzen. Produktivcode wird erst danach geschrieben.
