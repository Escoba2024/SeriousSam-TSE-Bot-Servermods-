# A3: begrenzter Damageworker und zweistufiger passiver Stop

**Ziel:** Die deaktivierte A3-Hard2-Vorbereitung darf den Rollen-/Restorecontroller
bei Frida-Attach, Load, RPC, Unload oder Detach nicht blockieren. Ein Hookstop
darf zugelassene ReceiveDamage-Paare nicht verlieren oder vor Idle entladen.
Keine native Freigabe aus dieser Umsetzung.

**Ausgang:** A3-Commit7391419, privates Hard2-Paket mit Manifest7730510e…;
Reviewbefunde: direkte unbegrenzte Fridaoperationen im Hauptprozess und Stop-
Detach unabhängig von `inFlight`. HardMap-Parent benötigt keinen Fridaworker;
mit dem anderen Worker abgestimmt, keine zweite Architektur.

**Architektur:** Frischer exec-Unterprozess nach dem bereits geprüften A1-
Workerprinzip; nur ein Socket wird vererbt, keine Reader-/Runtime-Lock-FDs.
Alle Fridaoperationen verbleiben dort. Parent-IPC mit festen Fristen und sticky
Fehlern. Parent schließt eigene Spielrollen weiterhin regulär und führt Restore
unabhängig vom Worker aus. Nur der eigene Child darf nach bestätigtem normalem
Rollenende und Quieszenz beendet werden. Keine Signale an Spielrollen.

**Stop:** Admission schließen; bereits zugelassene Damage-OnLeave-Paare laufen
unter unverändertem TTL und denselben Body-/Entity-/Worldgrenzen aus. Danach
explizit `inFlight==0`, keine aktiven Records/Callbacks und Getter-Bindervertrag
prüfen; erst dann Damage-/verbliebenen Getterhook abhängen, originale Bytes
prüfen, Script entladen und Session trennen. Historische Getter-TLS-Bindung und
deren Selbstabnahme unverändert erhalten; Zählerhülle beobachtet nur ihren
Callback. Native Quieszenz bleibt bis neuer Retailprobe unqualifiziert.

## Aufgaben

- [x] Konkrete Original-A3- und A1-Workerpfade lesen; Mapinterface abgleichen.
- [x] Fokussierte Tests zuerst: blockierender IPC-/Attachersatz, sticky Timeout,
  frischer exec/FD-Scope, Fehler vor Arm, rollenabhängiges Childcleanup;
  tatsächliche JS-Stoplogik mit zugelassenem Paar, verspätetem OnLeave, laufendem
  Gettercallback, TTL-/Fault-/Queuegrenzen und Idle vor Unload.
- [x] Reiner Workerproxy und spezifischer Originaldamage-Collector; alle
  Fingerprints/Host-/PID-/Start-/CWD-/Namespace-/Moduleinode-/Populationpins
  bleiben wirksam. Message-/Journalfehler dürfen sicheren Cleanup nicht überspringen.
- [x] Neuer deaktivierter privater Fork, minimaler Main-/JS-Diff; keine Änderung
  geschlossener Pakete und keine Fridaoperation im Parent.
- [x] Fokussierte portable RED/GREEN-Prüfung nach Rootfreigabe, aktuelle Pins,
  bereinigte Reviewdiffs und Handoff committen. Root reviewed/integriert/native.

## Unveränderte Grenzen

Hard2, zwei benachbarte Tierpaare mit je zwei vertauschten Einzelstarts,
120s Fenster, 125000ms Hook-TTL, 2000ms Bindung und Reserve, Queue64,
1024 Damagecalls, maximal256 Getter-Bindungscalls; keine neue Eingabe,
Gameplayaktion, Enginefunktion oder Speicher-/Spielzustandswrite. Samplerraten,
Hostbudget und bisherige physische A3-Kriterien bleiben unverändert.

Worker-IPC übernimmt enge bestehende A1-Budgets: Arm3s, Drain100ms, Close2s.
Ein Timeout bleibt FAIL und beendet normale Parent-Rollenbereinigung nicht.
Das ist eine neue technische Begrenzung, keine Verlängerung eines bestehenden
Gameplay-/ABI-/TTL-/Bindungsfensters. Kein automatischer Retry oder Folgestart.

## Abschluss dieses Offline-Scope

58 gezielte Fälle PASS, 79 Runtimepins und 109 finale Paketquellen geprüft.
Finalfork und genaue SHAs stehen im Bericht; Independent-Review und jede
native Qualifikation bleiben offen. Drei Codegates und Manifest sind false.
