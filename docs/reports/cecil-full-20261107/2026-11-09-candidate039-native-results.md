# Normal039: Skulls und Einzelbot-Versorgung fehlgeschlagen

Normal039 ist **nicht für den Rollout qualifiziert**. Die unveränderten Verhaltens- und Versorgungsgates scheitern. Kein formales Stundenfenster wurde begonnen; die sechs öffentlichen Instanzen behalten ihren bisherigen Stand.

Quelle `c11bc16d6892068f65bf3946fd60b31ff9d554b5`, Tree `62148f3c357739f5e681eab1b73aa1e2b3593486`, normale PE32-x86-DLL `42d2a536263d599edf47c3387b4056eb5e099ee836ab2337fb7dab6f7fbc267f`. [Buildmanifest](build039.json). Alle 15 nativen Übersetzungseinheiten und der Link bestanden; die zusammengeführte SDK-Bridge bestand 556 ASan/UBSan-Prüfungen. Diese Belege ersetzen keine Runtime-Abnahme.

## Vollständiger Skulls-Lauf

Acht Bots wurden 600,008 Sekunden vollständig beobachtet. Alle acht erhöhen ihren Score; 35 Todesereignisse und keine neuen Monitor-/Sync-/CRC-/Fatalfehler wurden erkannt. Trotzdem überschreiten drei Slots die unveränderte Grenze von zehn Sekunden unbegründetem Stillstand:

| Slot | Stillstand |
| --- | ---: |
| BotA:1 | 552,588 s |
| BotA:3 | 19,164 s |
| BotB:0 | 14,113 s |

Im längsten Fall bleiben Entity, Generation, positive Gesundheit, Position, Standzustand und physische Referenz konstant. Die finale Eingabe enthält über weite Teile eine freigegebene langsame Seitwärtsbewegung; eine Positionsänderung oder NAV-Wiederaufnahme findet nicht statt. Für diese Entity/Generation erzeugt der neue Ground-Watchdog kein Stallereignis. An anderen Stellen des vollständigen Laufs sind zwölf Ground-Recovery-Meldungen vorhanden; seine generelle native Aktivierung ist damit belegt, jedoch keine wirksame Behandlung dieser Blockade. Die konkrete ausbleibende Voraussetzung ist damit noch nicht bewiesen. Freie Prüfstrahlen sind weiterhin kein Nachweis einer erfolgreichen körperlichen Bewegung.

Der Lauf wurde vollständig normal geschlossen und die Rohlogs gesichert. Weitere Karten des geplanten Durchlaufs wurden nach diesem Fehler nicht gestartet.

## Neue vollständige Versorgungskohorte v12

Alle zehn aufeinanderfolgenden frischen Einzelbot-Beitritte sind normal beendet: zehn unterschiedliche PID-/Startepochen, 594 gültige Abfragen mit genau einem eigenen Bot, ursprüngliche Red-Station-CRC und keine administrativ zensierte First-10-Kohorte. Es gelten weiterhin mindestens 60 Sekunden pro Fall, Beobachtung eines noch offenen First-10-Versuchs bis zum nativen Ende und einer späteren vollständigen State-Barriere, sowie eine administrative Grenze von 520 Sekunden. Die neue Ledgerfassung begrenzt ausschließlich die Fallwechsel-Zensierung korrekt auf die ersten zehn Versuche; spätere Rohereignisse werden weiterhin erhalten.

Sieben der ersten zehn tatsächlich gewählten aufnehmbaren Waffenziele haben korroborierte Besitzänderungen. Zwei Cannon-Versuche enden mit `unreachable_hold`, ein Grenade-Versuch mit `timeout`; keiner wird entfernt oder ersetzt. Die zehn initialen Leben liefern 9,65/3,35/33,05/12,85/5,60/3,15/9,90/20,10/4,85/10,00 Sekunden bis zum ersten sinnvollen Pickup. Median 9,775 Sekunden erfüllt die 15-Sekunden-Grenze; P95 33,05 Sekunden überschreitet die unveränderte 30-Sekunden-Grenze. Sieben Erwerbe unterschreiten die geforderten neun. **Versorgung fehlgeschlagen.** Frühere038-Ergebnisse werden nicht übertragen.

## Abgetrennte passive Diagnose

Eine eigene diagnostische DLL aus lokalem Commit `4a80615c1ac2e0d43510db370ab753c5d8ce606b` ergänzt ausschließlich begrenzte Guard-/Zeit-/Supportprotokolle. Ihr Hash lautet `ec014c89a6bc0c1ff8984048ce82f142fc409ef54b1b1f5ba6a239ac345fb973`. Ein separater privater Acht-Bot-Lauf auf Skulls dauert 300 Sekunden und endet normal. Er erhält ausdrücklich keine normale039-, Stunden- oder Produktionsfreigabe.

Dort sind unter anderem stabile lebende Standzustände mit NULL-Referenz und ohne Treffer des vorhandenen kurzen Near-Foot-Strahls belegt. Ein fehlender Treffer beweist weder den exakten Bodenabstand noch eine sichere alternative Richtung. Die längste normale039-Blockade mit einer nichtleeren Referenz ist dadurch noch nicht erklärt; weitere gezielte Diagnose bleibt notwendig.

Eine vermutete Zeitabweichung wurde geprüft: Das tatsächliche SDK107 definiert `TIME` und `FLOAT` als float. Portable Gegenprobe und die tatsächlichen MSVC-Objektsequenzen zeigen für beide Produktionsausdrücke eine Float32-Multiplikation mit anschließender Double-Konvertierung. Es gibt keinen belegten x87-/Double-TIME-Fehler. Der bisherige Bridge-Timerstub verwendet dagegen double; dies ist eine ausdrücklich dokumentierte Prüfgrenze und kein nativer Fehlernachweis.

Die sechs öffentlichen Instanzen wurden um 18:18 UTC erneut lesend geprüft: erreichbar, jeweils acht eigene Bots und keine zusätzlichen Spieler, fünf Produktions-DLLs unverändert und die Entwicklung weiterhin mit ihrem früheren013-Stand auf Hole. Die finalen Karten-, Waffen-/Sonderaktions-, Retail-, 3600-/3600-/7200-Sekunden-, Ressourcen-, Wiederanlauf- und Flottengates bleiben offen. Keine Messgrenze wurde nachträglich gelockert.

Private Rohlogs, Profile, Retail-Dateien und vollständige NAV-Daten werden nicht veröffentlicht.
