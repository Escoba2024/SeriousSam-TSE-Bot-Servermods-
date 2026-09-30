# Perplexity Deep Research – TSE 1.07 Vanilla-Bots

Stand: 30.09.2026  
Ursprünglicher Dateiname laut Nutzer: `Bots_TSE107_Deep_Research.md`  
Herkunft: Perplexity Deep Research, vom Nutzer als unabhängige Originalcode-Verifikation bereitgestellt.

## Einordnung

Diese Datei nimmt den vom Nutzer bereitgestellten Perplexity-Bericht als zusätzliche Recherchequelle in das Projekt auf. Der vollständige externe Markdown-Dateiinhalt lag beim Einpflegen nicht als separate Repository-Datei vor; dokumentiert sind daher die bereitgestellten Kernaussagen plus projektseitige Gegenprüfung an Originalquellen.

Evidenz im Projekt:

- **BESTÄTIGT** – direkt an öffentlich zugänglichem Originalcode/SDK geprüft.
- **TECHNISCHE SCHLUSSFOLGERUNG** – aus bestätigten Mechanismen abgeleitet, End-to-End noch nicht experimentell bewiesen.
- **OFFEN** – erst mit echter TSE-1.07-Binary/Testumgebung zu klären.

## Kernergebnis

Der Bericht bestätigt den bereits gewählten **Pfad D** als Primärarchitektur: Ein modifizierter TSE-1.07-Bot-Client verbindet sich als normaler Client mit einem unveränderten Vanilla-Dedicated-Server. Seine lokalen Spieler sind reguläre Netzwerkspieler; lediglich deren `CPlayerAction`-Erzeugung wird programmgesteuert.

Der End-to-End-PoC gegen echte TSE-1.07-Binaries bleibt erforderlich.

## Projektseitig bestätigte neue Punkte

### 1. Vier lokale Spieler sind eine echte Netzwerkgrenze

Im öffentlichen Croteam-Engine-Code steht:

```cpp
#define NET_MAXGAMEPLAYERS   16
#define NET_MAXLOCALPLAYERS   4
```

`CServer::Handle()` verarbeitet bei `MSG_ACTION` pro Client genau `NET_MAXLOCALPLAYERS` mögliche Action-Slots:

```cpp
for(INDEX ipls=0; ipls<NET_MAXLOCALPLAYERS; ipls++) {
  ...
}
```

Zusätzlich begrenzt der `MSG_REQ_CONNECTPLAYER`-Pfad die Zahl der für einen Client angelegten Spieler anhand von `sso_ctLocalPlayers`:

```cpp
if (iClient>0 && GetPlayersCountForClient(iClient)>=sso.sso_ctLocalPlayers) {
  ... Protocol violation ...
}
```

**Konsequenz:** Für einen unveränderten Server wird das Projekt auf maximal vier Bot-Spieler pro Bot-Client-Prozess ausgelegt. Skalierung auf 8/12/16 erfolgt zunächst ausschließlich über mehrere Bot-Client-Prozesse.

### Präzisierung zum Perplexity-Bericht

Der Bericht ordnet den `GetPlayersCountForClient(iClient) >= sso.sso_ctLocalPlayers`-Check teilweise dem `MSG_ACTION`-Handling zu. Im Originalcode liegt dieser konkrete Check im `MSG_REQ_CONNECTPLAYER`-Block. Die feste Vierer-Schleife liegt im `MSG_ACTION`-Block.

Die Architekturfolge bleibt dieselbe: **maximal vier lokale Spieler pro normalem Client-Pfad**.

## 2. Konkreter PoC-Patchpunkt: `GameHandleTimer -> SetAction`

Im öffentlichen `Sources/GameMP/Game.cpp` wird in `CGame::GameHandleTimer()` für jeden aktiven lokalen Spieler eine Action erzeugt und anschließend in den normalen PlayerSource-Pfad gegeben:

```cpp
CControls &ctrls = gm_actrlControls[iCurrentPlayer];
ctrls.CreateAction(gm_apcPlayers[iCurrentPlayer], paAction, FALSE);
gm_lpLocalPlayers[iPlayer].lp_pplsPlayerSource->SetAction(paAction);
```

Damit existiert ein sehr konkreter Bot-Client-only PoC-Punkt:

1. normales Game-/Control-Bookkeeping laufen lassen;
2. unmittelbar vor `SetAction()` die Test-`CPlayerAction` ersetzen/überschreiben;
3. `CPlayerSource` und den restlichen Netzwerkpfad unverändert lassen.

`ctl_ComposeActionPacket` bleibt als alternative Hook-Stelle relevant. Für den ersten PoC werden beide Wege gegeneinander bewertet:

- minimaler 1.07-GameMP-Patch in `GameHandleTimer()`;
- Hook auf die originale `ctl_ComposeActionPacket`-Schnittstelle.

## 3. 1.07 und 1.10 haben eine harte Build-Sperre

SE1-ModSDK `Engine107/Engine/CurrentVersion.h`:

```cpp
#define _SE_BUILD_MAJOR 10000
#define _SE_BUILD_MINOR 7
#define _SE_VER_STRING "1.07"
```

Croteam Serious Engine 1.10:

```cpp
#define _SE_BUILD_MAJOR 10000
#define _SE_BUILD_MINOR 10
#define _SE_VER_STRING "1.10"
```

Im Server-Connect-Pfad wird die Version exakt geprüft:

```cpp
if (iMajor!=_SE_BUILD_MAJOR || iMinor!=_SE_BUILD_MINOR) {
  // disconnect the client
}
```

**BESTÄTIGT:** Ein unverändert aus dem 1.10-Source gebauter Server ist kein direkter Drop-in für Vanilla-1.07-Clients.

**OFFEN:** Ob ein vollständiger 1.10-Rebuild allein durch Build-Konstanten-Änderung netzkompatibel würde. Das Projekt verfolgt diesen Weg für den PoC nicht; echte 1.07-Binaries/SDK-Libs bleiben maßgeblich.

## 4. Netzwerkheader 1.07 vs. 1.10

Der Perplexity-Bericht beschreibt einen Diff von `Engine107` gegen `Engine110` und bewertet mehrere zentrale Netzwerkheader als inhaltlich identisch.

Projektseitige Stichprobe an `Network.h`:

- `NET_MAXGAMEPLAYERS = 16` identisch;
- `NET_MAXLOCALPLAYERS = 4` identisch;
- zentrale `CNetworkLibrary`-Schnittstellen stimmen inhaltlich überein;
- die 1.10-Datei besitzt zusätzlich den GPL-Lizenzkopf und kleine Text-/Whitespace-Unterschiede.

Daher übernimmt das Projekt **nicht** die wörtliche Formulierung „byte-identisch“. Korrekte Arbeitsformulierung:

> Ausgewählte 1.07-/1.10-Netzwerkheader sind strukturell bzw. semantisch sehr ähnlich; dies erleichtert die Nutzung von 1.10 als Landkarte, beweist aber keine vollständige Binary-/Netcode-Kompatibilität.

## 5. Pfad B besitzt keinen fertigen virtuellen Client-Hook

Der Bericht findet im öffentlichen `CServer`-/`CNetworkLibrary`-Pfad keinen dokumentierten nativen Loopback-/Virtual-Client-Einspeisepunkt, der ohne Engine-Patch einen internen Bot als echten Remote-Spieler erzeugt.

**TECHNISCHE SCHLUSSFOLGERUNG:** Pfad B2 bleibt möglich, erfordert aber tiefes 1.07-Engine-Reverse-Engineering/Binary-Patching und ist kein sinnvoller erster PoC.

## 6. CecilBotMod bleibt KI-Spender, nicht Netzwerkarchitektur

Direkt im CecilBotMod-Code bestätigt:

- `CPlayerBotController` existiert als separate Controller-Klasse;
- `_aPlayerBots` ist ein Container von `CPlayerBotController`;
- `CPlayerBot` besitzt einen Controller;
- `BotApplyAction(CPlayerAction&)` wird in der modifizierten Bot-/Player-Logik verwendet;
- Pathfinding-/Movement-/Weapon-Logik ist in eigenen Bot-Modulen organisiert.

Daraus folgt: KI-Teile können später als Ausgangspunkt dienen, müssen aber von CecilBot-spezifischer Entity-/Simulationslogik entkoppelt werden. Zielinterface bleibt: Weltzustand lesen -> `CPlayerAction` für einen regulären Bot-Client-Spieler erzeugen.

## 7. Serverbrowser

Der Bericht bestätigt die bestehende Projektstrategie: Erst echte Player-Slots verwenden und per Live-Status-/Player-Query messen. Keine GameAgent-/Query-Fälschung vor diesem Test.

Wenn die Bot-Client-Spieler als aktive normale `CPlayerBuffer`-Slots geführt werden, ist zu erwarten, dass sie vom normalen Spielerzähler erfasst werden. Das tatsächliche 1.07-/333networks-Verhalten wird experimentell geprüft.

## Aktualisierter PoC

### Phase 0

- Vanilla TSE 1.07 Dedicated Server reproduzierbar starten.
- Unveränderten Vanilla-Beobachter-Client festlegen.
- Versionen/Hashes/Binaries dokumentieren.
- Separaten Bot-Client auf 1.07-Basis anlegen.

### PoC-1

- genau ein lokaler Bot-Spieler;
- primär `GameMP/Game.cpp::GameHandleTimer()` / `CreateAction -> SetAction` als minimalen Patchpfad untersuchen;
- alternativ `ctl_ComposeActionPacket` hooken;
- deterministische Action: vorwärts, langsame Rotation, periodisches Fire;
- keine CecilBot-Entity, kein NavMesh, kein Chat, kein Population Manager.

### Abnahme

- Join ohne Modpflicht;
- Playerliste/Scoreboard;
- Bewegung/Blick;
- Schießen/Schaden;
- Frag/Respawn;
- Mapwechsel;
- Disconnect/Reconnect;
- GUID-Eindeutigkeit;
- mindestens 60 Minuten ohne Sync-Kick/Desync/Crash;
- Live-Serverstatus/Player-Query.

### Danach

- 2 -> 4 lokale Bots in einem Prozess;
- anschließend Multiprocess: 2x4, danach Richtung Zielpopulation;
- erst danach KI/Navigation/Population/Chat.

## Offene Punkte

- Welcher Bot-Client-Eingriff ist mit echten 1.07-Binaries stabiler: GameMP-Rebuild oder Hook?
- GUID-/Profilverhalten mehrerer lokaler Spieler.
- Mapwechsel/Reconnect über lange Laufzeit.
- Live-Query mit mehreren lokalen Spielern und mehreren Prozessen.
- CPU/RAM/Netzlast bei vier Bot-Client-Prozessen für 16 Spieler.
- Vollständige semantische Prüfung aller vom Perplexity-Bericht verglichenen Engine107-/Engine110-Netzwerkheader.

## Originalquellen für die Gegenprüfung

- `Croteam-official/Serious-Engine`
  - `Sources/Engine/Network/Network.h`
  - `Sources/Engine/Network/Server.cpp`
  - `Sources/Engine/CurrentVersion.h`
  - `Sources/GameMP/Game.cpp`
- `DreamyCecil/SE1-ModSDK`, Branch `includes`
  - `Engine107/Engine/CurrentVersion.h`
  - `Engine107/Engine/Network/Network.h`
  - `Engine110/Engine/Network/Network.h`
- `DreamyCecil/CecilBotMod`
  - `Sources/Bots/Classes/PlayerBot.es`
  - `Sources/EntitiesMP/Player.es`
  - `Sources/Bots/BotStructure.*`
  - `Sources/Bots/Logic/*`
  - `Sources/Bots/PathFinding/*`
- `SamClassicPatch/SuperProject` – Hook-/Patch-Infrastruktur als spätere Referenz.

## Status

Perplexity Deep Research ist ab diesem Commit eine offizielle zusätzliche Projektquelle. Direkt gegengeprüfte Erkenntnisse wurden in den kanonischen Google-Drive-Wissensstand übernommen. Der Architekturentscheid **Pfad D zuerst, B2 nur als Fallback** bleibt unverändert, ist aber stärker belegt.
