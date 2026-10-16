# Konservativer Population-Supervisor

`scripts/Manage-BotPopulation.ps1` steuert bereits vorbereitete BotClient-Installationen als ganze Prozessgruppen mit jeweils ein bis vier lokalen Spielern. Vorbereitung, native Profile und qualifizierte GameMP-DLL bleiben Aufgabe der [Release-Anleitung](LOCAL-RELEASE.md). Die Fleet-Konfiguration muss auf getrennte Installationen und den richtigen unveränderten TSE-1.07-Server zeigen.

Der Supervisor zählt die gesamte gemeldete Serverpopulation. Ein Mensch mit einem Botnamen verbraucht genauso Kapazität; Namen dienen ausschließlich als zusätzliche Join-/Wiederstart-Sperre. Es gibt keine Human-Präfixklassifikation. Die Obergrenze ist `min(TargetPopulation, max(0, MaxPlayers - ReservedHumanSlots))`.

Bei Ziel acht und zwei Vierergruppen führt ein zusätzlicher Mensch zu neun Spielern: Eine eigene Vierergruppe wird gestoppt, anschließend verbleiben vier Bots und der Mensch. Nach dessen Austritt kann die zweite Vierergruppe wieder starten. Drei freie Plätze bleiben bewusst unbesetzt, weil eine Vierergruppe nicht hineinpasst. Die Steuerung bietet keine exakte Belegung einzelner Slots und keine Garantie gegen beliebig viele gleichzeitige Beitritte.

## Aufruf

Zuerst eine begrenzte Beobachtung gegen einen laufenden Server durchführen. `-ObserveOnly` liest ausschließlich; `-FleetState` kann dabei die bestehende Fleet-Buchhaltung für die Beobachtung aktiver Gruppen bezeichnen.

```powershell
pwsh -NoProfile -File poc/scripts/Manage-BotPopulation.ps1 `
  -Config C:/TSE/fleet.json -StateDirectory C:/TSE/evidence/observe-001 `
  -TargetPopulation 8 -ReservedHumanSlots 2 -Iterations 30 -ObserveOnly
```

Für die aktive Steuerung müssen alle konfigurierten BotClient-Prozesse zunächst beendet sein. Jeder Aufruf braucht einen neuen State-Ordner. `-Iterations 0` läuft bis zur Stop-Anforderung; ein begrenzter Aufruf beendet seine eigenen Clients beim Abschluss.

```powershell
pwsh -NoProfile -File poc/scripts/Manage-BotPopulation.ps1 `
  -Config C:/TSE/fleet.json -StateDirectory C:/TSE/evidence/live-001 `
  -TargetPopulation 8 -ReservedHumanSlots 2 -Iterations 120

# Einen laufenden Aufruf kontrolliert beenden:
New-Item -ItemType File C:/TSE/evidence/live-001/stop.request
```

`-PollMilliseconds` liegt zwischen 100 und 5000, Standard 1000. UDP-Abfragen und Prozessstarts/-stops können den tatsächlichen Abstand verlängern. Ctrl+C bemüht ebenfalls den `finally`-Cleanup; hartes Beenden des PowerShell-Prozesses oder Rechnerausfall kann diesen verhindern. Für diese Ausfälle gibt es noch keinen externen Watchdog.

## Schutz und Nachweise

- Pro Beobachtung werden vollständige Status-, Spieler- und zweite Statusantwort verglichen. Anzahl, Maximum, Karte, Spielversion und Mod müssen konsistent sein. Fehlende Abschlussfelder, doppelte Indizes oder unvollständige Spielerlisten führen zu keiner neuen Startaktion.
- Starts benötigen zwei stabile Beobachtungen. Weitere Starts warten auf den eigenen nativen Join und alle erwarteten lokalen BotDriver-Slots. Eine nachfolgende Fehler-/Sync-Zeile hebt die Bereitschaft auf.
- Ein nicht bestätigter Start endet nach 45 Sekunden. Verliert eine bereits bestätigte eigene Gruppe später ihre Bereitschaft (beispielsweise nach einem Sync-Disconnect bei weiterlaufendem Prozess), beginnt erneut eine begrenzte 45-Sekunden-Frist. Rechtzeitige Wiederherstellung hebt die Frist auf; andernfalls wird die eigene Gruppe beendet. Nach einem abgeschlossenen Stop folgen zehn Sekunden Wiederstartverzögerung. Noch gemeldete Namen der alten Gruppe sperren einen Neustart zusätzlich; unbekannte oder doppelte eigene Namen werden konservativ behandelt.
- Exklusive Locks in jeder Client-Installation verhindern einen zweiten Supervisor auch bei anderem State-Ordner. Vorhandene Clientprozesse werden nicht übernommen. Ein reiner Beobachter setzt keine Locks.
- Stop und Fehler-Cleanup verwenden die gehaltene Prozessidentität, gepinnten Handle, exakten Executable-Pfad, Startzeit und Elternprozess. Fehlende oder beschädigte State-Dateien verhindern diesen Cleanup nicht. Ein Fenster-Exit wird als unbestätigt protokolliert; ein nötiger harter Stop ist keine reguläre Shutdown-Abnahme.
- Vor jedem Start wird ein vorhandenes `SeriousSam.log` in den State-Ordner kopiert und anschließend am exakten Pfad entfernt. Das neue Log gehört damit zum aktuellen Start. Profile, GUID-Sidecars und DLL werden vom Supervisor nicht verändert. Die Lock-Datei bleibt nach Freigabe als kleine Besitzformat-Datei erhalten.

`events.jsonl` enthält Beobachtungen und Start-/Stop-/Timeout-Ereignisse; pro Generation entstehen Konfiguration und Fleet-State. Ein Stop-Receipt erhält die Endung `.supervisor-stopped.json`. `completed.json` bestätigt ausschließlich den normalen Abschluss des Controllers (`nativeAcceptance=false`), auch wenn kein gültiger UDP-Sample vorlag. State-Dateien und Rohlogs enthalten lokale Pfade, Namen und Runtime-Daten; sie gehören in einen privaten Evidence-Ordner.

## Qualifikationsgrenze

Die [Abnahme vom 14.10.2026](../docs/reports/2026-10-14-population-supervisor.md) beschreibt den tatsächlich geprüften Umfang. Ein kurzer lokaler Prozessgruppen-Lifecycle ersetzt keine KI-Stunde, öffentliche Browserabnahme, exakte Einzelslot-Steuerung oder 24/7-Qualifikation. Die umfassende Population-Manager-Phase bleibt bis zu den weiteren Abnahmen teilweise offen.

Portable Regressionen starten keine Spiele:

```powershell
pwsh -NoProfile -File tools/Test-Publication.ps1 -Evidence C:/TSE/evidence/check-001 -Python python
```
