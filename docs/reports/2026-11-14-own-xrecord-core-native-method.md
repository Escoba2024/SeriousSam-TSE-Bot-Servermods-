# Eigene Core-Eingabemessung: erster nativer Methodenbeleg

Am 14.11.2026 um 17:51:44 UTC endete genau ein Methodenlauf mit
`PASS_METHOD_PARTIAL_CORE_REQUESTS_ONLY`. Kein TSE-Prozess wurde gestartet;
die Liveflotte blieb auf Cecil048 beziehungsweise Gen2.

Die neue eigene Xvfb-Anzeige167 war vorher frei. Der eingefrorene Controller
prüfte seine14 Dateipins und die Systembibliotheken, hielt seine exklusive
Sperre und band Anzeige, Treiber und Recorder an tatsächliche PID/Startzeiten,
Argumente, DISPLAY und Socket. RECORD1.13 und XTEST2.2 waren nativ verfügbar.

Ein einziger relativer XTEST-Request +12/0 bewegte den Zeiger von400/300
nach412/300. Ein einziger Warp-Request setzte ihn auf400/300 zurück.
Die beiden aufgezeichneten QueryPointer-Antworten, Gerätebewegungen und
zugestellten Core-Bewegungen passten jeweils genau. Request-/Reply-Sequenzen
und das eigene Fenster banden die Requestquelle; für Geräteereignisse
wird ausdrücklich kein auslösender Client behauptet.

StartOfData und EndOfData, Freigabe aller Recorddaten/des Kontexts,
geschlossene Verbindungen und normale Beendigung aller drei eigenen
Kindprozesse wurden nachgewiesen. Keine unbekannten, fehlerhaften oder
verworfenen Records, kein Overflow oder Timeout, kein erzwungener Cleanup.
Wandzeit0,183327s; Eltern-CPU0,023761s; Kind-CPU0,171137s;
maximales Kind-RSS63360KiB; anschließend10345500672Byte Datenträger frei.

| Beleg | SHA256 |
|---|---|
| Root-Freeze-Manifest | `43d38e727666d171bc9c6d021d4af018c60fe0279583c6636949d246e0f549ec` |
| Methodenresultat | `f0c3acc94c3c75a7ae0b648e24aa64d098cbf5a2ac4b81cff5be9aa8775ab470` |
| Private Rawrecords,3483Byte | `42ff01014dbd772e5e4e2713788b69a20fd6d55af31e518830a4c09d8925052b` |

Private Dateien liegen unter
`/srv/tse-cecil-rollout-evidence-20261114/own-xrecord-core-root-20261114-175200`.
Der Name enthält eine vorab gewählte Zeitmarke; maßgeblich ist die tatsächliche
Endzeit oben. Owner-, Log- und Endequittung liegen daneben.

Die zuvor unabhängigen62 Offlinefälle und dieser echte Methodenlauf sind
verschiedene Nachweisstufen. Der Lauf qualifiziert weder XI2-Vollständigkeit
noch einen Retail-Eingabepfad, die XTEST→ACK-Kalibrierung, Respawnschaden oder
A1. Nächster Schritt ist eine gesondert geprüfte passive Kopplung an den
bereits eigenen Originalclient-Test, ohne zusätzliche Gameplayeingaben oder
Änderung der bisherigen Gain-/ACK-/Zeitgrenzen.

Die vor diesem Lauf erstellte Delta042-Sicherung wurde vollständig aus Drive
zurückgeladen:8938294Byte,
SHA256`1b37b52a3a0b2be810c4518f35794b7c698c7e5927200842f314f39e23bbbc44`.
760 rekonstruierte Dateien wurden erneut auf Inhalt, UID/GID, Modus und
Nanosekunden-mtime geprüft. Ein vollständiger nativer Archiv-Restorestart
wurde damit nicht getestet. Die neuen Methoden-Rawdaten benötigen die
nächste Deltasicherung.
