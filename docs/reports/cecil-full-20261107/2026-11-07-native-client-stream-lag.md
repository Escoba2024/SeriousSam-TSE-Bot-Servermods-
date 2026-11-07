# Native Retail-1.07: verspätete Weltverarbeitung durch Client-Bandbreitenbudget

Stand: 7. November 2026. **Begrenzte native Diagnose und Konfigurationskontrolle; keine Langzeit- oder Produktionsfreigabe.**

## Ergebnis

Client B steuerte im untersuchten Skulls-Lauf gegen einen verspäteten Weltzustand. Seine eigenen Drehwinkel wurden auf Client A nach ungefähr 0,10 Sekunden verarbeitet, auf B selbst erst nach 2,15 Sekunden. Spätere passive Messungen lokalisierten den verbleibenden Rückstand im serverseitigen Versandpuffer für B.

Die effektiven Client- und Server-Sessionparameter waren `BufferActions=1, MaxBPS=4000, MinBPS=100`. Die vorhandene LAN-Konfigurationsdatei enthielt höhere Werte, diese waren zur Messzeit jedoch nicht wirksam. Originaler Retail-1.07-Code begrenzt mit den tatsächlich aktiven Werten das komprimierte Nachrichtenbudget auf 200 Byte je Tick. Das reicht häufig für einen neuen Tick, bietet bei den beobachteten Nachrichtengrößen aber wenig Spielraum zum Aufholen eines Rückstands.

Nach expliziter Startup-Konfiguration von B auf die vorhandenen LAN-Werte `cli_iMaxBPS=100000` und `cli_iMinBPS=6000` sowie dessen Neustart mit **derselben DLL** waren beide serverseitigen Versandpuffer aktuell. B verarbeitete die eigenen Drehwinkel im vollständigen neuen 60-Sekunden-Trace nach ungefähr 0,05 Sekunden; die zuvor gemessene Weltphasendifferenz zwischen A und B verschwand. A lief unverändert weiter. Ein Aim- oder Navigationscode-Fix war für diese Kontrolle nicht erforderlich.

Die Intervention umfasst Konfigurationsänderung und Neustart gemeinsam. Ein zusätzlicher Neustart mit den alten Bandbreitenwerten wurde in dieser Vergleichsserie nicht ausgeführt. Deshalb ist die Vermeidung jedes zukünftigen Rückstands noch nicht isoliert nachgewiesen. Die Diagnose des vorhandenen serverseitigen Rückstands und seines wirksamen Budgetlimits ist davon unabhängig belegt.

## Kandidaten und Messverfahren

| Bestandteil | Pin |
|---|---|
| Build010 Runtime-Quellstand | `df1ca40d3feb3788b7be1cb098d26a035a4a3b0e` |
| GameMP.dll, vor und nach Intervention | SHA256 `224ee607072982a521bdab36250554039f9e606a4db755fdd42716fb0f031475` |
| Original Engine.dll | SHA256 `b79bf8bb3927fe4f8f252e141d721ae5c738df02218f0ecc12da5c1afbcb534f` |
| Original EntitiesMP.dll für Winkeloffsets | SHA256 `7f595f2a7fc96a978b3467983e8f17c70d827f17a5f4ee887f9c7a1f20b1d350` |
| Winkeltrace vorher | SHA256 `c499f57597b806e49289f565ab8e61462f13d60ff55690c33d03ed452523c774` |
| Winkeltrace nach LAN-Konfiguration von B | SHA256 `77b28d884fe6b5549da563bf8d545557bd4b6f1d2156cefbfd12213aa9c1c678` |
| Abgeschlossener 300-Sekunden-Observerbericht | SHA256 `22fc120386d9ea17f3db613b032cd962341f0b6e502331d3bd6855c57d539762` |
| Vorheriger passiver UDP-Mitschnitt | SHA256 `b5c2cf21fc8c41ce3d44e9f19f1ed5efb150bd5a02f16738f7282dc398e43d8b` |

Die Winkeltraces lesen ausschließlich eigene autorisierte Prozesse über `O_RDONLY`/`pread`: keine Hooks, kein Prozessstopp, keine Speicheränderung. Abtastrate 20 Hz, Dauer jeweils 60 Sekunden. Pointerketten und Winkel-/Placement-Snapshots werden doppelt gelesen; inkonsistente Snapshots werden verworfen. Das neue Messfenster enthält 1.200 Abtastungen je Client, ohne verworfene instabile Snapshots. Externe Messungen sind trotz dieser Prüfung nicht atomar zum Timer-Callback oder Action-Composer.

Die Auswertung sucht jedes neu beobachtete Paar aus lokal akkumuliertem Yaw und Pitch in der späteren `m_aLastRotation` derselben globalen Spieler-Entity. Beide Komponenten müssen auf 0,002 Grad übereinstimmen; Suchfenster maximal 5,25 Sekunden. Wiederholte Quellwerte und bereits angewendete Paare werden übersprungen; die letzten 5,25 Sekunden werden nicht als vollständiges Vorwärtsfenster ausgewertet. Globale Slots 0–3 gehören A, 4–7 B. Identische beziehungsweise wiederkehrende Winkelpaare können besonders bei längeren Suchfenstern mehrdeutige Treffer erzeugen. Deshalb werden bei der Weltphasenmessung vor allem die stark variierenden A-Slots 1 und 3 herangezogen.

## Vorher/Nachher

| Messgröße | Vorher | Nach expliziten LAN-Werten und B-Neustart |
|---|---|---|
| B eigene lokale Winkel → B zuletzt verarbeitete Winkel | Median 2,150 s für alle vier Slots; p10 etwa 2,149 s, p90 etwa 2,200 s | Median 0,050 s für alle vier Slots; p10 0,049 s, p90 0,051 s |
| Zugeordnete Winkelpaare je B-Slot | 1010 / 819 / 897 / 990 | 668 / 1046 / 955 / 1095; kein unzugeordnetes Paar im auswertbaren Fenster |
| A eigene lokale Winkel → A zuletzt verarbeitete Winkel | Median 0,100 s | Median 0,100 s für alle vier Slots |
| B lokale Winkel → Verarbeitung auf A | Median 0,099 s für alle vier B-Slots | Median etwa 0,049 s |
| A bereits verarbeiteter Zustand → derselbe Zustand auf B | Median 2,051 s bei A-Slots 1 und 3 | Median 0,001 s für alle vier A-Slots; innerhalb der sequentiellen Abtastauflösung |
| Server-Session B, separate passive Momentaufnahme | 12 Sequenzen hinter neuestem gepuffertem Zustand | `lastSentSequence == newestBufferedSequence` bei A und B |
| Effektive B-Parameter, Client und Server-Session | `[1,4000,100]` | `[1,100000,6000]` |
| Serverlimit | 8000 B/s | Unverändert 8000 B/s |

Der Rückstand war zeitlich veränderlich. Im vorherigen UDP-Mitschnitt trafen 801 gleiche Tick-/Sequenz-/CRC-Paare von B später als von A ein: Median 3,692 Sekunden; die ersten 50 Paare hatten 4,143 Sekunden Median, die letzten 50 noch 3,442 Sekunden. Der höchste Anfangswert betrug 10,351 Sekunden. Eine spätere Sessionmessung zeigte eine Weltphasendifferenz von ungefähr 0,85 auf 0,75 Sekunden über 60 Sekunden. Das passt zu langsamem Aufholen; es ist kein Nachweis eines festen künstlichen Transportdelays.

Alle vier künstlichen Latenz-/Variationsvariablen waren bei beiden Clients zur passiven Kontrolle null. Client-GameStream-Puffer waren in der weiteren Sessionmessung leer; `MissingSequence` war −1. Der Server hielt dagegen noch nicht versendete Sequenzen für B vor. Das lokalisiert den dort gemessenen Rückstand vor der clientseitigen GameStream-Verarbeitung.

Die ursprüngliche 600-Sekunden-Funktionsbeobachtung hatte bei B nur 1 / 5 / 1 / 1 emittierte Combat-Feueraktionen trotz sichtbarer Gegner, bei A 219 / 289 / 220 / 75. Diese Zähler messen abgegebene Feueraktionen, keine Projektilanzahl oder Treffer. Der separate Observer nach der Konfigurationskontrolle endete nach 300,005 Sekunden mit 298 Stichproben, ohne gemeldete Fehler und Status `DURATION_ACTIVITY_SYNC_PASS_BEHAVIOR_REVIEW_REQUIRED`. B emittierte in diesem Fenster 193 / 236 / 285 / 260 Combat-Feueraktionen, A 167 / 115 / 203 / 228. Damit ist die vorherige nahezu vollständige Feuersperre von B in dieser begrenzten Kontrolle nicht mehr vorhanden. Die Fenster sind unterschiedlich lang; diese Rohzähler sind keine kontrollierte Leistungs- oder Trefferquotenmessung. Der Observer verlangt weiterhin Verhaltensreview und ersetzt keine Langzeitqualifikation.

## Beleg im Originalcode

Alle folgenden Adressen beziehen sich auf die oben gepinnte originale Engine.dll, Preferred Image Base `0x600c0000`. Für passive Speicherlesungen ist die tatsächlich gemappte Basis zu berücksichtigen. Dies sind Befunde aus Retail 1.07, keine Übertragung von Engine 1.10.

- `CServer::SendGameStreamBlocks`, `0x601a11a0`, liest die effektiven Sessionwerte für Min/MaxBPS und dividiert ganzzahlig durch 20. Beide Nachrichtenbudgets werden zunächst auf 0–1000 Byte und anschließend auf `ser_iMaxAllowedBPS / 20 - 11` begrenzt; Laden des Serverlimits bei `0x601a1237`.
- Die Routine fügt neue Sequenzen vorwärts an und komprimiert Kandidaten bei `0x601a1328`. Wenn bereits mindestens ein Block enthalten ist, wird ein weiterer Kandidat mit komprimierter Größe größer oder gleich dem Maximalbudget verworfen (`0x601a1330`–`0x601a133e`, Sprung nach `0x601a1376`). Die vorherige Nachricht bleibt erhalten.
- Mit Clientwerten 4000/100 und Serverlimit 8000 ergeben sich Maximalbudget 200 Byte und Minimalbudget 5 Byte. Mit 100000/6000 ergeben sich 389 beziehungsweise 300 Byte. Das Serverlimit bleibt wirksam; 100000 im Client hebt es nicht auf.
- `SessionStateLoop`, `0x601a8020`, verarbeitet empfangene Nachrichten in einer Schleife (`0x601a8482` zurück nach `0x601a8049`). `ProcessGameStream`, `0x601a64e0`, verarbeitet verfügbare Folgesequenzen ebenfalls wiederholt. Ein einfaches Ein-Tick-pro-Frame-Limit in diesen Funktionen wurde nicht gefunden.
- `SetLerpFactor`, `0x601a7140`, berechnet und begrenzt Interpolation und setzt Zeitanker bei Ausreißern zurück. Es verwirft oder drosselt keine GameStream-Sequenzen. Ein Rendering-Interpolationsfehler erklärt den gemessenen Unterschied in tatsächlich angewendeter `m_aLastRotation` nicht.

Die passiven Routen wurden ebenfalls am Original abgesichert: Netzwerk-Sessionreferenz `network+0x20`, letzter verarbeiteter Tick `session+0x4c` (`GetGameTime`, `0x6019c8d0`), letzte Sequenz `session+0x20`. Effektive Client-Sessionparameter liegen bei `session+0xcc/+0xd0/+0xd4`. Die Serverreferenz liegt bei `network+0x14` (`TimerLoop`, `0x6019c51b`), dessen Sessionarray-Daten bei `server+8`, mit 0x50 Byte je Session. Darin liegen letzte versendete Sequenz bei +0x18, Streamhead bei +0x30 und effektive Parameter bei +0x3c/+0x40/+0x44. Originale Player-Propertyregistrierungen belegen `m_aLastRotation` bei +0xca0 und `m_aLocalRotation` bei +0xcc4.

## Grenzen und nächste Abnahme

Die Kontrolle betrifft Build010 auf dem isolierten Dev-Server und einer Map. Sie qualifiziert weder die fünf Produktionsserver noch alle Maps, Langzeit-Sync, externen menschlichen Gameplay-Input, Ressourcen unter sauberer Messlast oder 24/7-Betrieb. Gleiche Stichproben-CRCs sind kein vollständiger Nachweis aller Simulationsticks.

Für einen freizugebenden Kandidaten müssen die Startup-Werte reproduzierbar gesetzt und nach Join auf Client sowie Server-Session kontrolliert werden. Versandrückstand, Eingabe-Feedbackzeit und tatsächlicher Combat-Fortschritt gehören zusammen in die erneute native Abnahme. Die bestehenden Stillstands-, Sync- und Langzeitkriterien bleiben unverändert. Alle privaten Rohtraces, Konfigurationen, Prozessdaten, Spieldaten und Binaries bleiben außerhalb des öffentlichen Commits.

Private Nachweise: `rotation010`, `rotation010-lanB`, `session010`, `server_session010.json`, `server_session010-lanB.json`, `diagnose010.pcap`, `dev-lan010-B.log`, `dev-lan010-B-functional/report.json`; reproduzierbare private Auswertungen `rotation-action-lag*.py`, `rotation-cross-lag*.py` und `sync010-time-lag.py`.
