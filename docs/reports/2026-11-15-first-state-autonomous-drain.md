# FirstState: autonomer Drain, ausschließlich Offlinevorbereitung

Der neue Methodenadapter ist implementiert; nach der unten dokumentierten
Deadline-Reviewkorrektur bestehen **57 fokussierte Tests in4,154s**. Er ist kein
nativer Methoden-, ABI-, A1- oder Schadensnachweis.
Ein frischer matched Control/Trace-Vergleich bleibt erforderlich. Alte native
FAILs und der bisherige Monitor-Checkpoint bleiben unverändert.

Der deaktivierte Builder wurde nur in temporären Testverzeichnissen ausgeführt.
Das feste Reviewpaket wird nach Root-Quellreview erzeugt; es ist noch nicht
eingefroren oder gestartet. Alle Runtimegates bleiben False.

## Implementierung

- Ein FreshExec-Worker mit einem `select`-Loop statt blockierendem `readline`.
  Fragmentierte Kommandos und langsame Parentabnahme halten den Capturepump
  nicht an. Es gibt keine neuen Threads, Forks, Inputs, Hooks oder Gamewrites.
- Zielperiode20ms; tatsächliche Capturedauer/Serviceintervalle über100ms,
  falsche Ownership, Journal-/fsyncfehler und abgelaufene Budgets bleiben FAIL.
  Es besteht keine Echtzeit- oder harte90s-Killgarantie. Frida-RPC kann intern
  hängen; unabhängiges normales Rollen-Cleanup bleibt im Parent.
- Erste Journal-JSON-Kodierung der Frida-Pythonwerte vor semantischer Prüfung.
  NaN bleibt als ungültiges NaN erhalten und scheitert danach. Das sind keine
  behaupteten ursprünglichen Frida-Wirebytes. Parent archiviert empfangene
  Wirebytes vor Parse; ganze Pakete werden weder quotiert noch Base64-kodiert,
  zusammengeführt, ausgewählt oder normalisiert.
- Höchstens1024 Indexeinträge,512MiB Journal,2MiB Payload plus16KiB Envelope.
  Der Produktionsbatch liest Journalbereiche mit `preadv` direkt in einen
  Wire-bytearray. Ein2MiB-Paket passt vollständig. Der gemessene Encoderpeak
  liegt unter2MiB+16KiB+512KiB; Python-Rückgabewerte, Kodierung und semantisches
  JSON-Parsen benötigen zusätzliche transiente Objekte. Kein Whole-Heap-Beleg.
- Unveränderliche StopserialS und FinalserialF; jeder Versuch bleibt im Nenner,
  auch bei Indexüberlauf. Alle indexierten Originalpakete werden in Reihenfolge
  durch den unveränderten strikten Validator versucht, einschließlich ungültiger
  und Cleanup-Tail-Pakete. Fehlende1..F-Abdeckung verhindert Erfolg.
- STOP geht über den frisch PID/start-geprüften Proxy und den billigen
  Workerownershipguard vor der teuren Parentprüfung. Normale Batches behalten
  volle Parentprüfungen davor/danach. Worker-NativeContextprüfungen vor/nach
  Capture und die bestehenden JS-Guards pro Event sind weitere, getrennte Ebenen.
- Admission-only Stop, authentisches Idle/finishstop außerhalb von Callbacks,
  Unload/Detach und38 externe Originalregionen bleiben Pflicht. Worker-Reaping
  erfolgt erst nach den drei belegten normalen Rollen-/Unitcloses.

## Scope und Quellidentität

Die bisherigen JS-/Body-/I1-/I2-/18Hook-/38Region-/11Importbindungen, StrictTrace,
LegacySession und Inputdateien werden nicht geändert. Der Builder validiert
alle erwarteten Parent- und verschachtelten **Hashwerte**, nicht nur die Keysets.
Selbst repinnte Body-, Policy-, Worker- und Transactionänderungen werden abgewiesen.

Der neue Helper verwendet nur lazy Traceimports. Control bleibt ohne Frida-/
Worker-/Nativeimporte; auch `tools.`-Aliasnamen werden abgewiesen. Main ändert
nur zwei Namespaces. Der komplette Helperdelta und Mainnamespacewechsel lassen
sich byteexakt auf den gepinnten Monitorparent zurückführen. In den Testpaketen:
**154 Runtimepins /75 verschachtelte APIpins /90 bytegleiche Parentdateien**.

64Queue/8192Calls/16384Events/1024Damage/256Bindingcalls/2000msBinding/15000msTTL,
10s Beobachtung, parent-start+85s und90s Admissionalbudget bleiben unverändert.
Keine aktive Inventory-/Geometrie-/FixedLife-Abnahme wird daraus abgeleitet.
Der neue Abschlussbericht hat ein eigenes typisiertes AUTODRAIN-Schema; eine
alte `packets`-Passstruktur kann ihn nicht ersetzen. Positiver Tickpaarbeleg muss
vor S liegen; Cleanup-Tail kann keine fehlende Beobachtung ergänzen.

## Tatsächliche Prüfschritte und Grenzen

Fehlende Komponenten lieferten zunächst echte REDs; für die konkreten Review-
Fehler wurden zusätzlich reproduzierbare Assertion-REDs erhalten:

- Payloadkopien/fehlender Journalencoder und auf1024 verkürzter Überlaufnenner;
- wiederholte Expiryjournale und mögliche0s-Selectschleife;
- teure Parentprüfung vor Admissionclose;
- veralteter Workerstart-Snapshot und gestrandetes bereits gepuffertes STOP;
- tatsächlicher JournalCollector schluckte Raw-/fsyncfehler bei stop/status/
  finishstop, ohne Pumpfehlersignal: alle drei Fälle waren RED. Authentische
  ACKs bleiben jetzt für sicheres Cleanup nutzbar, der Fehler bleibt sticky.

Der letzte fokussierte Lauf umfasst Protokoll, Journal/Pump/Loop, Proxy,
passiven Nativeadapter, Batchsession, Windowtransform und Builder. Der echte
unveränderte private TraceValidator wurde mit erhaltenen Callback-Fixtures und
allen38 Restorebereichen genutzt. Keine Frida-, Display-, Spiel- oder DLL-
Ausführung. Es gab einen korrigierten Patch-IndentationError und eine korrigierte
synthetische Ereignisform; diese Zwischenfehler sind in der privaten Ledger-
Dokumentation benannt, nicht als bestandene Läufe gezählt.

Der historische FileTransaction bleibt bytegleich; daraus folgt kein bisher
nicht belegter atime-/mtime-Restore. Root behandelt dessen Metadatenkorrektur
separat. Keine Liveänderung, Promotion, A-Abnahme oder B-Implementierung.

Reproduzierbarer fokussierter Befehl:

```sh
python3 -m unittest tools.test_first_state_autodrain_protocol tools.test_first_state_autodrain_worker tools.test_first_state_autodrain_proxy tools.test_first_state_autodrain_native_adapter tools.test_first_state_autodrain_session tools.test_first_state_autodrain_window_patch tools.test_prepare_first_state_autodrain
```

Private Original-/Retailbindings, Rawpakete und Laufzeitidentitäten gehören
ausschließlich in die vorhandenen privaten Evidencepakete.

## Nachtrag: letzte Batchvalidierung bleibt innerhalb ihrer Budgets

Der unabhängige Sourcepeerreview zu `ff205d7` fand einen wichtigen Abschluss-
fehler: nach der letzten Validierung beziehungsweise Batchmetadatenarchivierung
konnte die vollständige Serialdeckung die nächste Deadlineprüfung überspringen.
Vier echte Owner-RED-Subfälle bestätigten fälschliches COMPLETE: absolute
Observerdeadline und2s-Backlogbudget, jeweils durch letzte Validierung oder
Archivierung überschritten. Das ursprüngliche55-Test-Ergebnis bleibt separat.

Die enge Korrektur prüft die absolute Deadline nach Verarbeitung/Archivierung
und beide Budgets vor dem erfolgreichen `_collect`-Return. Die Limits werden
nicht verändert. Bei Verspätung bleibt FAIL sticky; bereits verarbeitete Pakete,
vollständiger Nenner und weitere Unload-/Detach-/38Restoreversuche bleiben
erhalten. Die Kontrolle innerhalb beider Grenzen (1,999s Backlog) bleibt COMPLETE.
Letzter Gesamtlauf57/57 PASS4,154s; kein festes Paket oder Nativefall angelegt.
