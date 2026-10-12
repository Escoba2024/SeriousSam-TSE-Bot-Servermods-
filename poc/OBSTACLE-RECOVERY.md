# Optionale reaktive Hinderniserholung – 10.10.2026

Die Erweiterung setzt auf der optionalen automatischen Kampfsteuerung auf.
Sie nutzt den vorhandenen `StuckDetector` und native Engine107-Sichtstrahlen,
um einen Bot an einer nahen Blockade anzuhalten, zur freieren Seite zu drehen
und anschließend für eine begrenzte Zeit vorwärtszugehen. Alle Eingaben
laufen weiterhin durch `ctl_ComposeActionPacket` und `CPlayerSource::SetAction`.
Dedicated Server, Engine, EntitiesMP und menschliche Clients bleiben original.

## Verhalten und Grenzen

`bot_bObstacleAvoidance` ist standardmäßig aus. Die Erweiterung benötigt
`bot_bEnabled = 1`, `bot_bAutoCombat = 1` und `bot_iTestTarget = -1` und gilt
für Scorematch/Fragmatch. Drei horizontale physische Kollisionsstrahlen reichen
3 m nach vorn und jeweils 60 Grad seitlich. Eine Blockade unter 1,2 m oder
40 angeforderte Bewegungsticks ohne ausreichenden Positionsfortschritt lösen
die Erholung aus. Links/rechts werden anhand der gemessenen freien Strecke
gewählt; Gleichstand verwendet eine Richtung pro lokalem Spielerslot.
Sind beide Seiten eng, versucht der Bot eine halbe Drehung.

Während des Drehens bleibt die Vorwärtsbewegung null. Erst eine ausgerichtete
und freie Richtung erlaubt bis zu 40 Vorwärtsticks. Eine erneute Blockade
veranlasst eine neue Richtungswahl, auch genau beim Übergang vom Drehen zum
Laufen. Die Drehphase ist auf 160 Ticks begrenzt, der gesamte Versuch inklusive
neuer Richtungswahlen auf 240 Ticks; nach Abbruch folgen 40 Ticks Wiederholpause.
Bei der nativen 20-Hz-Tickrate sind das 8, 12 und 2 Sekunden. Die Wiederholpause
gibt die Steuerung an die bestehende Kampf-/Suchbewegung zurück. Ein beendeter
Versuch garantiert deshalb noch keine dauerhaft freie Route.

Die konfigurierte Bewegungsgeschwindigkeit bleibt erhalten. Nullgeschwindigkeit,
Tod, bewusste Nahkampf-/Nahdistanzpausen, Botabschaltung, Spielende, fehlende
Spielerquellen, neue Spieleridentität und große Positionssprünge verwerfen
den alten Ausweichkurs. Eine vorübergehende Zielausrichtung mit null Bewegung
startet keinen neuen Stuck-Versuch. Während einer übernommenen Ausweichaktion
unterbleibt der lebende Kampfschuss; der native Respawn-Impuls bleibt separat.

Dies ist eine reaktive Bewegungserholung. Globale Routen, Item-Wege,
Navmesh, Treppenplanung und Boden-/Abgrundsicherheit sind noch offen.
Die horizontalen Strahlen prüfen keinen begehbaren Boden. Coop und andere
Spielmodi sind für diese Erweiterung nicht abgenommen. Die älteren Netzwerk-
und Kampf-Abnahmen bleiben ihren jeweiligen DLLs zugeordnet.

## Aktivieren und separat bauen

Für reguläre Bots die Symbole nur im separaten BotClient setzen:

```text
bot_bEnabled = 1;
bot_bAutoCombat = 1;
bot_bObstacleAvoidance = 1;
bot_bCombatSkipLocals = 1;
bot_iTestTarget = -1;
```

`poc/scripts/Phase1ObstacleAvoidance.ini` ist eine QA-Konfiguration mit
zugelassenen lokalen Gegnern und Telemetrie in jedem Tick.
Für reguläre Verwendung lokale Gegner ausschließen und Diagnostik reduzieren.

Der Bau benötigt den erhaltenen Auto-Combat-SDK-Build mit Ausgangs-DLL
`28A32C6401928717FE8AA5619E490DE8A8CEB8713116368914D5CBBCEC646615`:

```powershell
./poc/scripts/Build-ObstacleGameMP.ps1 `
  -BaseBuild .codex/shadow-20261010-ai-combat `
  -BuildDir .codex/my-obstacle-build
```

Der Helfer erstellt ein neues Verzeichnis, übernimmt die vorhandenen Quellen,
kopiert `bot_navigation.h`, prüft und verwendet Patch 0005 und baut x86
`Release_TSE107` mit MSVC v143. SDK-Includes und Entities-Header bleiben
Referenzen auf den vorhandenen SDK-Bestand. Der separate nachgebaute Stand
wurde anhand von zehn Quellenhashes mit dem Testbuild verglichen. DLL-Hashes
können wegen Buildmetadaten zwischen Bauverzeichnissen abweichen.

Der nativ geprüfte Build ist:

```text
.codex/shadow-20261010-obstacle/Sources/Bin/vs2022.Release_TSE107/GameMP.dll
SHA256 1A38F0A41583A11A0790CE91EEA2A86162B2B3B8E575204AB1360854BA6AF1E7
```

## Nachweis und Wiederholung

Der finale Zwei-Bot-Lauf dauerte 180,0964517 s mit CRC 2
und 3390 / 3390 Datensätzen. Bot0/1 zeigten 27 / 28
Wand-Auslöser und 2 / 8 abgeschlossene Ausweichversuche
mit 24,017–25,052 m planarem Fortschritt.
Der Vanilla-Observer protokollierte 4 Kills; insgesamt
3 Tod-/Respawn-Zyklen traten auf.
Der Vier-Bot-Legacy-Lauf mit ausgeschalteter Erweiterung dauerte
60,0803289 s und bestand mit 926/926/926/926 Snapshots.
Sechs Core-Programme, neun Auditor-Fixtures, Re-Review, Patch-Neuaufbau und
abschließende Restaurierung bestanden. Die native Vier-Bot-Abnahme der
eingeschalteten neuen Steuerung bleibt offen.

Die Core-Suite ergänzt die fünf vorhandenen Programme um
`poc/botcore/test_bot_navigation.cpp`. Die neun Auditor-Fixtures laufen mit:

```powershell
python -B poc/scripts/test_obstacle_evidence.py
```

Auf Shadow den gebündelten Python-Pfad verwenden, falls `python` nur den
Windows-Store-Alias aufruft. Native Tests in den vorhandenen Retail-Kopien
nacheinander ausführen, damit Sicherung und Restaurierung sich nicht überlagern:

```powershell
./tools/run-shadow-validation.ps1 -Mode Combat -Counts 2 -Seconds 180 `
  -Dll .codex/shadow-20261010-obstacle/Sources/Bin/vs2022.Release_TSE107/GameMP.dll `
  -StartupSource poc/scripts/Phase1ObstacleAvoidance.ini `
  -Evidence .codex/evidence/my-obstacle-run

python -B poc/scripts/Test-ObstacleEvidence.py .codex/evidence/my-obstacle-run `
  --dll .codex/shadow-20261010-obstacle/Sources/Bin/vs2022.Release_TSE107/GameMP.dll `
  --output .codex/evidence/my-obstacle-run/acceptance-audit.json
```

Der Auditor verlangt zwei echte verschiedene Profile/GUIDs, nativen Join/CRC,
lückenlose Navigationsdaten mit passenden Kampf-/Action-Daten, begrenzte
Eingaben, tatsächliche Brush-Kollisionen und mindestens einen abgeschlossenen
Ausweichversuch mit mindestens 2 m Positionsfortschritt je Bot. Wandkontakt
und abgeschlossener Fortschritt müssen zum selben Versuch gehören.
Er prüft außerdem lebende Kampfschüsse außerhalb der Erholung, einen
unabhängigen Vanilla-Observer-Killbeleg, Wiederherstellung und Crash-/Cleanup-Gates.
Ein Netzwerkbeitritt allein reicht nicht.

Der vollständige lokale Abschlussbericht und Rohbelege liegen unter
`.codex/evidence/shadow-20261010/obstacle-avoidance/`.
Die Stunden- und Acht-Bot-Abnahme wurde für diese neue DLL nicht wiederholt.
