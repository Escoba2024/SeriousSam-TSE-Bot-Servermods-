# A1: XRes-Attribution – statischer Fähigkeiten- und Semantikbefund

Nur Plan-/Quellenarbeit im eigenen Worktree ab Root100bda4. Kein neuer
Native-, Display-, Input-, Test-, Compiler- oder Installationsaufruf.

## Tatsächlich vorhandene Ausgangspunkte

Der eigene XResV2-Fall ist begrenzt bestanden: Rootresult
`own-xres-pid-v2-method-root-20261114/method-result.json`, SHA aus Rootquittung
`18d16f195c64d2d5f6564b0166422d63aa72011c4dcd71284f05d1d9a1afc953`.
Die gelesene Antwort enthält zwei Snapshots, zwölf richtige PIDqueries,2/2
QueryClientsarrays und12/12IDarraysfreigaben sowie vier normale Exit0-Closings.
Das qualifiziert die öffentlichen XRes-Aufrufe im eigenen Linuxmethodenfall;
Wine-Clientzuordnung und durchgehende Clientbase-Lebensdauer folgen daraus nicht.
Der ältere Base0-FAIL47e103… bleibt unverändert.

Aktueller A1-Parent ist tatsächlich
`/srv/tse-a1-xtest-preparation-root-frozen-20261114`, Manifest aus vorherigem
Pinreview `71b9c896e068e473d0fd8317871b0fa3ccc5f4a43828c87e8b1b09619c60170a`.
Öffentlicher Builder `tools/prepare_a1_xtest_preparation.py:26` erklärt die
Derivation aus ReleaseSafeAttempt; neuer Adapter muss vom tatsächlichen
Rootparent ableiten und dessen vollständige Pins später frisch prüfen.
Die vier Dateien unter `passive-core/` bleiben unveränderte Referenz.

## Konkrete vorhandene Grenzen

- `a1_passive_xrecord.py:131`: XTestQueryExtension+XSync läuft vor RECORDarm;
  erst danach wird der Proxyobserver gesetzt. Keine neue Eingabe nötig.
- `a1_passive_xrecord_worker.py:125`: GetContext bindet Controller-GC und
  Originalfenster über echte serverseitige Resourceowner-Basen. Das ist keine
  PIDzuordnung weiterer Wine-Verbindungen. Der Datenclient wird ausgeschlossen;
  FutureClients2 muss erhalten bleiben, aktuelle Contextclients sind auf32begrenzt.
- `passive-core/xrecord_core_native.py:33–42`: alle vier ausgewählten Ranges
  bleiben bei client_started=0/client_died=0. AllClients/FutureClients registriert
  Verbindungen, fordert diese Kategorien aber nicht an.
- `passive-core/xrecord_core_method.py:75–77` könnte Start-/Diedkategorien als
  Rohrecords übernehmen; Parserfähigkeit bedeutet keine aktivierte Erfassung.
- `passive-core/xrecord_core_worker.py:58–113`: StartOfData vor Armantwort,
  später Disable+Sync und Drain bis EndOfData. Die vorhandene Pump-/FreeData-
  Strecke und fehlender Drop sind wichtige Voraussetzungen, noch kein
  Lebenszyklusnachweis mit den heutigen deaktivierten Flags.
- `a1_passive_xrecord_evidence.py:39` weist fremde bzw. weitere Bases ausdrücklich
  als unattributed aus. Snapshot-PIDs dürfen diese historischen Zähler nicht
  rückwirkend umetikettieren.

## Protokollbefund

[RECORD-Spezifikation](https://www.x.org/releases/X11R7.7/doc/recordproto/record.html),
Abschnitte Types/RecordEnableContext: Lifecycleflags selektieren Clientstart/-tod;
AllClients umfasst aktuelle und zukünftige Verbindungen. StartOfData beginnt den
Stream, EndOfData beendet ihn; id-base benennt die Clientverbindung. GetContext
ist eine Zustandsabfrage, kein Verbindungsverlauf.

[RECORD-Bibliotheksspezifikation](https://www.x.org/releases/X11R7.7/doc/libXtst/recordlib.html),
Datum Flags/Protocol Ranges, und lokale Primärquelle libXtst1.2.3
`XRecord.c:741–745,809–826`: Callbackmetadaten enthalten Base/Sequenz; ClientStarted
trägt die Setupantwort, ClientDied erhält bei Flag4 die Clientsequenz und keinen
Payload. Deshalb reichen vorhandene Decoderzweige allein nicht als Beleg.

**Folgerung:** Mit den heutigen Ranges liefern zwei Snapshots nur zwei
Punktzuordnungen. Für eine eng begrenzte Intervallzuordnung braucht der Plan
aktivierte, vollständig geprüfte Lifecycleaufnahme und Snapshots INNERHALB des
enabled RECORDintervalls. Vorarm-Snapshot und Nachstop-Snapshot lassen sonst
unbeobachtete Randlücken. Weder Hostzeiten noch ähnliche Xserverzeiten dürfen
diese Lücken überbrücken.

## Wine-/PIDgrenze

XRes liefert serverseitige lokale Client-PIDmetadaten, keine Windowsprozess- oder
Threadzuordnung. Die gelesene Xorg-Implementierung
[DetermineClientPid](https://raw.githubusercontent.com/mirror/xserver/master/os/client.c)
nutzt lokale Verbindungcredentials und cached sie für die Verbindung. Der
Originalprozess kann mehrere X-Verbindungen haben; ein Helper oder anders
berichteter Linux-Identifier darf nicht ungeprüft dem Original zugerechnet werden.

Der nächste Adapter darf ausschließlich eine exakt zur bekannten eigenen
Original-HostPID passende Antwort mit aktueller Startgeneration und gleichem
PIDnamespace als solche ausweisen. PIDnamespace von Parent, Xvfb, Recorder und
Original vor/nach beiden Metadatenphasen prüfen. Eine abweichende PID bleibt
UNKNOWN/OTHER_KNOWN_OWN_ROLE; kein Name-/Zeit-/PIDnähefallback. Falls tatsächlich
eine TID statt der gepinnten HostPID erscheint, nur separat dokumentieren. Eine
optionale TID→TGID-Regel benötigt vorher belegten eigenen `/proc`-Datenfluss und
Rootentscheidung; sie ist nicht Bestandteil dieses Plans.

Die alte Verbindung U ist beendet und bleibt UNKNOWN. Selbst eine neue
Original-PIDzuordnung erklärt weder Winecache noch doppelte GetInput-Werte oder
die Wirkung eines Warprequests. Original-Get/SetCursorPos-Hooks beobachten echte
Returns; es werden keine neuen User32-/Pointerprobeaufrufe hinzugefügt.
